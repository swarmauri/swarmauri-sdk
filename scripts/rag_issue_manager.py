import os
import json
import requests
from swarmauri.utils.load_documents_from_folder import load_documents_from_folder
from swarmauri.llms.concrete.DeepInfraModel import DeepInfraModel
from swarmauri.agents.concrete.RagAgent import RagAgent
from swarmauri.conversations.concrete.MaxSystemContextConversation import (
    MaxSystemContextConversation,
)
from swarmauri.vector_stores.concrete.TfidfVectorStore import TfidfVectorStore
import argparse

# GitHub API settings
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("REPO")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# GitHub Metadata
BASE_BRANCH = os.getenv("GITHUB_BASE_REF", "unknown")
HEAD_BRANCH = (
    os.getenv("GITHUB_HEAD_REF") or os.getenv("GITHUB_REF", "unknown").split("/")[-1]
)
COMMIT_SHA = os.getenv("GITHUB_SHA", "unknown")
WORKFLOW_RUN_URL = (
    os.getenv("GITHUB_SERVER_URL", "https://github.com")
    + f"/{REPO}/actions/runs/{os.getenv('GITHUB_RUN_ID', 'unknown')}"
)

# DeepInfraModel Initialization
DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")
llm = DeepInfraModel(
    api_key=DEEPINFRA_API_KEY, name="meta-llama/Meta-Llama-3.1-8B-Instruct"
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


def ask_agent_for_fix(test_name, failure_message, stack_trace):
    """Ask the LLM Model for suggestions on fixing the test failure."""
    system_context = (
        "Utilizing the following codebase solve the user's problem.\nCodebase:\n\n"
    )
    prompt = f"""
    \n\nUser Problem:
    I have a failing pytest test case named '{test_name}' in a Python project. The error message is:
    `{failure_message}`
    \n\n
    The stack trace is:
    `{stack_trace}`
    \n\n
    Can you help me identify the cause of this failure and suggest a fix?
    """
    try:
        current_directory = os.getcwd()
        documents = load_documents_from_folder(
            folder_path=current_directory,
            include_extensions=["py", "md", "yaml", "toml", "json"],
        )
        print(f"Loaded {len(documents)} documents.")

        # Step 3: Initialize the TFIDF Vector Store and add documents
        vector_store = TfidfVectorStore()
        vector_store.add_documents(documents)
        print("Documents have been added to the TFIDF Vector Store.")

        # Step 5: Initialize the RagAgent with the vector store and language model
        rag_agent = RagAgent(
            system_context=system_context,
            llm=llm,
            vector_store=vector_store,
            conversation=MaxSystemContextConversation(),
        )
        print("RagAgent initialized successfully.")
        response = rag_agent.exec(
            input_data=prompt,
            top_k=20,
            llm_kwargs={"max_tokens": 750, "temperature": 0.7},
        )
        print(
            f"\nPrompt: \n{prompt}\n\n",
            "-" * 10,
            f"Response: {response}\n\n",
            "=" * 10,
            "\n",
        )
        return response
    except Exception as e:
        print(f"Error communicating with LLM: {e}")
        return "Unable to retrieve suggestions from LLM at this time."


def get_existing_issues():
    """Retrieve all existing issues with the pytest-failure label."""
    url = f"https://api.github.com/repos/{REPO}/issues"
    params = {"labels": "pytest-failure", "state": "open"}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()


def create_issue(test, package):
    """Create a new GitHub issue for the test failure."""
    suggestion = ask_agent_for_fix(test["name"], test["message"], test["message"])
    url = f"https://api.github.com/repos/{REPO}/issues"
    if package in {"core", "community", "experimental"}:
        package_name = f"swarmauri_{package}"
    else:
        package_name = "swarmauri"
    resource_kind, type_kind = test["name"].split("/")[2:4]
    comp_file_url = f"pkgs/{package}/{package_name}/{resource_kind}/concrete/{type_kind.split('_')[0]}.py"
    test_file_url = f"pkgs/{package}/{test['name'].split('::')[0]}"

    # Construct the issue body
    data = {
        "title": f"[Test Case Failure]: {test['name']}",
        "body": f"""
### Test Case:
`{test["path"]}`

### Failure Details:
```python
{test["message"]}
```

---

### Suggested Fix (via Agent):
{suggestion}

---

### Context:
- **Commit**: `{COMMIT_SHA}`
- **Matrix Package**: [{package}](https://github.com/{REPO}/tree/{HEAD_BRANCH}/pkgs/{package})
- **Component**: [{comp_file_url}](https://github.com/{REPO}/tree/{HEAD_BRANCH}/{comp_file_url})
- **Test File**: [{test_file_url}](https://github.com/{REPO}/tree/{HEAD_BRANCH}/{test_file_url})                                                                            
- **Branches**: [{HEAD_BRANCH}](https://github.com/{REPO}/tree/{HEAD_BRANCH}) ==> [{BASE_BRANCH}](https://github.com/{REPO}/tree/{BASE_BRANCH})
- **Changes**: [View Changes](https://github.com/{REPO}/commit/{COMMIT_SHA})
- **Files**: [View Files](https://github.com/{REPO}/tree/{COMMIT_SHA})
- **Workflow Run**: [View Run]({WORKFLOW_RUN_URL})

### Labels:
This issue is auto-labeled for the `{package}` package.
""",
        "labels": ["pytest-failure", package],
    }
    response = requests.post(url, headers=HEADERS, json=data)
    response.raise_for_status()
    print(
        f"Issue created for {test['name']} with LLM suggestion in package '{package}'."
    )


def add_comment_to_issue(issue_number, test, package):
    """Add a comment to an existing GitHub issue."""
    suggestion = ask_agent_for_fix(test["name"], test["message"], test["message"])
    url = f"https://api.github.com/repos/{REPO}/issues/{issue_number}/comments"
    if package in {"core", "community", "experimental"}:
        package_name = f"swarmauri_{package}"
    else:
        package_name = "swarmauri"
    resource_kind, type_kind = test["name"].split("/")[2:4]
    comp_file_url = f"pkgs/{package}/{package_name}/{resource_kind}/concrete/{type_kind.split('_')[0]}.py"
    test_file_url = f"pkgs/{package}/{test['name'].split('::')[0]}"
    data = {
        "body": f"""
New failure detected:

### Test Case:
`{test["path"]}`

### Failure Details:
```python
{test["message"]}
```

---

### Suggested Fix (via Agent):
{suggestion}

---

### Context:
- **Commit**: `{COMMIT_SHA}`
- **Matrix Package**: [{package}](https://github.com/{REPO}/tree/{HEAD_BRANCH}/pkgs/{package})
- **Component**: [{comp_file_url}](https://github.com/{REPO}/tree/{HEAD_BRANCH}/{comp_file_url})
- **Test File**: [{test_file_url}](https://github.com/{REPO}/tree/{HEAD_BRANCH}/{test_file_url})                                                                            
- **Branches**: [{HEAD_BRANCH}](https://github.com/{REPO}/tree/{HEAD_BRANCH}) ==> [{BASE_BRANCH}](https://github.com/{REPO}/tree/{BASE_BRANCH})
- **Changes**: [View Changes](https://github.com/{REPO}/commit/{COMMIT_SHA})
- **Files**: [View Files](https://github.com/{REPO}/tree/{COMMIT_SHA})
- **Workflow Run**: [View Run]({WORKFLOW_RUN_URL})

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
