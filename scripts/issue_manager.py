"""
This script is used to create and manage GitHub issues for missing test files.
"""

import requests
import os


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


def create_issue(test, package):
    """Create a new GitHub issue for the missing test file."""
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
        "title": f"[Missing Test Coverage]: {test['name']}",
        "body": f"""
### Test Case:
`{test["path"]}`

### Details:
```python
{test["message"]}
```

---

### Suggested Fix (via Agent):
Write test cases to cover the missing test files.

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

    issue_number = response.json().get("number")
    return issue_number


def add_comment_to_issue(issue_number, test, package):
    """Add a comment to an existing GitHub issue."""
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

###  Details:
```python
{test["message"]}
```

---

### Suggested Fix (via Agent):
Write test cases to cover the missing test files.

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


def get_existing_issues():
    """Retrieve all existing issues with the pytest-failure label."""
    url = f"https://api.github.com/repos/{REPO}/issues"
    params = {"labels": "pytest-failure", "state": "open"}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()
