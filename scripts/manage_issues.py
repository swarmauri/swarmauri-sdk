import os
import json
import requests

# GitHub API settings
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("REPO")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

ISSUE_LABEL = "pytest-failure"


def load_pytest_results(report_file="report.json"):
    """Load pytest results from the JSON report."""
    if not os.path.exists(report_file):
        print("No pytest report file found.")
        return []

    with open(report_file, "r") as f:
        report = json.load(f)

    # Extract failed test cases
    failures = []
    for test in report.get("tests", []):
        if test["outcome"] == "failed":
            failures.append({
                "name": test["name"],
                "path": test["nodeid"],
                "message": test.get("call", {}).get("longrepr", "No details provided")
            })
    return failures


def get_existing_issues():
    """Retrieve all existing issues with the pytest-failure label."""
    url = f"https://api.github.com/repos/{REPO}/issues"
    params = {"labels": ISSUE_LABEL, "state": "open"}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()


def create_issue(test):
    """Create a new GitHub issue for the test failure."""
    url = f"https://api.github.com/repos/{REPO}/issues"
    data = {
        "title": f"Test Failure: {test['name']}",
        "body": f"### Test Case\n```\n{test['path']}\n```\n### Failure Details\n{test['message']}",
        "labels": [ISSUE_LABEL]
    }
    response = requests.post(url, headers=HEADERS, json=data)
    response.raise_for_status()
    print(f"Issue created for {test['name']}")


def add_comment_to_issue(issue_number, test):
    """Add a comment to an existing GitHub issue."""
    url = f"https://api.github.com/repos/{REPO}/issues/{issue_number}/comments"
    data = {"body": f"New failure detected:\n```\n{test['path']}\n```\n### Details\n{test['message']}"}
    response = requests.post(url, headers=HEADERS, json=data)
    response.raise_for_status()
    print(f"Comment added to issue {issue_number} for {test['name']}")


def process_failures():
    """Process pytest failures and manage GitHub issues."""
    failures = load_pytest_results()
    if not failures:
        print("No test failures found.")
        return

    existing_issues = get_existing_issues()

    for test in failures:
        issue_exists = False
        for issue in existing_issues:
            if test["name"] in issue["title"]:
                add_comment_to_issue(issue["number"], test)
                issue_exists = True
                break

        if not issue_exists:
            create_issue(test)


if __name__ == "__main__":
    process_failures()
