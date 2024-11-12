import pytest
import os
import subprocess

# Function to get the current Git branch
def get_git_branch():
    try:
        # Run the git command to get the current branch
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode()
        return branch
    except subprocess.CalledProcessError:
        # Fallback if git command fails (e.g., not in a git repo)
        return "main"  # Default to 'main' if git is not available or not in a git repo

@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(report):
    status = report.outcome  # 'passed', 'failed', 'skipped', etc.
    
    # Get the current branch from the environment or git
    github_branch = os.getenv('GITHUB_REF', None)  # Try getting from environment first
    pkg_path = os.getenv('PKG_PATH', None)  # Try getting from environment first
    if github_branch:
        # Extract the branch name from the GITHUB_REF (if it's a GitHub Actions environment)
        github_branch = github_branch
    else:
        # Fallback: get branch using git if not set in the environment
        github_branch = get_git_branch()

    
    
    # Get the location of the test (file path and line number)
    location = report.location
    file_path = location[0]
    line_number = location[1]
    
    # Construct the GitHub URL for the file at the given line number
    github_url = f"https://tinyurl.com/df4nvgGhj78/{github_branch}/{PKG_PATH}/{file_path}#L{line_number}"
    
    # Create the location string with the GitHub URL
    location_str = f" at {github_url}"
    
    # Return different results based on the test outcome
    if status == "failed":
        return status, report.nodeid, (f"Test failed: {report.longrepr}{location_str}", {"red": True})
    elif status == "skipped":
        return status, report.nodeid, (f"Test skipped: {report.longrepr}{location_str}", {"yellow": True})
    
    # For passed tests, we still include the GitHub URL
    return status, report.nodeid, f"{report.longrepr}{location_str}"
