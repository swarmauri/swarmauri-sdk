import os
import json
import requests
from swarmauri.llms.concrete.GroqModel import GroqModel
from swarmauri.agents.concrete.SimpleConversationAgent import SimpleConversationAgent
from swarmauri.conversations.concrete.Conversation import Conversation
import argparse

# GitHub API settings
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("REPO")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# GroqModel Initialization
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = GroqModel(api_key=GROQ_API_KEY)

BASE_BRANCH = (
    os.getenv("GITHUB_HEAD_REF") or os.getenv("GITHUB_REF", "unknown").split("/")[-1]
)
COMMIT_SHA = os.getenv("GITHUB_SHA", "unknown")
WORKFLOW_RUN_URL = (
    os.getenv("GITHUB_SERVER_URL", "https://github.com")
    + f"/{REPO}/actions/runs/{os.getenv('GITHUB_RUN_ID', 'unknown')}"
)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Manage GitHub Issues for Test Failures"
    )
    parser.add_argument(
        "--results-file",
        type=str,
        required=True,
        help="Path to the pytest JSON report file",
    )
    parser.add_argument(
        "--package",
        type=str,
        required=True,
        help="Name of the matrix package where the error occurred.",
    )
    return parser.parse_args()


def load_pytest_results(report_file):
    """Load pytest results from the JSON report."""
    if not os.path.exists(report_file):
        print(f"Report file not found: {report_file}")
        return []

    with open(report_file, "r") as f:
        report = json.load(f)

    failures = []
    for test in report.get("tests", []):
        if test.get("outcome") == "failed":
            test_name = test.get("nodeid", "Unknown test")
            failure_message = test.get("call", {}).get(
                "longrepr", "No failure details available"
            )
            failures.append(
                {
                    "name": test_name,
                    "path": test.get("nodeid", "Unknown path"),
                    "message": failure_message,
                }
            )
    return failures


def ask_groq_for_fix(test_name, failure_message, stack_trace):
    """Ask GroqModel for suggestions on fixing the test failure."""
    prompt = f"""
    I have a failing test case named '{test_name}' in a Python project. The error message is:
    {failure_message}

    The stack trace is:
    {stack_trace}

    Can you help me identify the cause of this failure and suggest a fix?
    """
    try:
        agent = SimpleConversationAgent(llm=llm, conversation=Conversation())
        response = agent.exec(input_str=prompt)
        return response
    except Exception as e:
        print(f"Error communicating with Groq: {e}")
        return "Unable to retrieve suggestions from Groq at this time."


def get_existing_issues():
    """Retrieve all existing issues with the pytest-failure label."""
    url = f"https://api.github.com/repos/{REPO}/issues"
    params = {"labels": "pytest-failure", "state": "open"}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()


def create_issue(test, package):
    """Create a new GitHub issue for the test failure."""
    groq_suggestion = ask_groq_for_fix(test["name"], test["message"], test["message"])
    url = f"https://api.github.com/repos/{REPO}/issues"

    # Construct the issue body
    data = {
        "title": f"[Test Case Failure]: {test['name']}",
        "body": f"""
### Test Case:
{test["path"]}

### Failure Details:
{test["message"]}

---

### Suggested Fix (via Groq):
{groq_suggestion}

---

### Context:
- **Branch**: [{BASE_BRANCH}](https://github.com/{REPO}/tree/{BASE_BRANCH})
- **Commit**: [{COMMIT_SHA}](https://github.com/{REPO}/commit/{COMMIT_SHA})
- **Commit Tree**: [{COMMIT_SHA}](https://github.com/{REPO}/tree/{COMMIT_SHA})
- **Workflow Run**: [View Run]({WORKFLOW_RUN_URL})
- **Matrix Package**: `{package}`

### Labels:
This issue is auto-labeled for the `{package}` package.
""",
        "labels": ["pytest-failure", package],
    }
    response = requests.post(url, headers=HEADERS, json=data)
    response.raise_for_status()
    print(
        f"Issue created for {test['name']} with Groq suggestion in package '{package}'."
    )


def add_comment_to_issue(issue_number, test, package):
    """Add a comment to an existing GitHub issue."""
    url = f"https://api.github.com/repos/{REPO}/issues/{issue_number}/comments"
    data = {
        "body": f"""
New failure detected:

### Test Case:
{test["path"]}

### Details:
{test["message"]}

---

### Context:
- **Branch**: [{BASE_BRANCH}](https://github.com/{REPO}/tree/{BASE_BRANCH})
- **Commit**: [{COMMIT_SHA}](https://github.com/{REPO}/commit/{COMMIT_SHA})
- **Commit Tree**: [{COMMIT_SHA}](https://github.com/{REPO}/tree/{COMMIT_SHA})
- **Workflow Run**: [View Run]({WORKFLOW_RUN_URL})
- **Matrix Package**: `{package}`
"""
    }
    response = requests.post(url, headers=HEADERS, json=data)
    response.raise_for_status()
    print(f"Comment added to issue {issue_number} for {test['name']}.")


def process_failures(report_file, package):
    """Process pytest failures and manage GitHub issues."""
    failures = load_pytest_results(report_file)
    if not failures:
        print("No test failures found.")
        return

    existing_issues = get_existing_issues()

    for test in failures:
        issue_exists = False
        for issue in existing_issues:
            if test["name"] in issue["title"]:
                add_comment_to_issue(issue["number"], test, package)
                issue_exists = True
                break

        if not issue_exists:
            create_issue(test, package)


if __name__ == "__main__":
    args = parse_arguments()
    process_failures(args.results_file, args.package)
