from .GithubBranchTool import GithubBranchTool
from .GithubCommitTool import GithubCommitTool
from .GithubIssueTool import GithubIssueTool
from .GithubPRTool import GithubPRTool
from .GithubRepoTool import GithubRepoTool
from .GithubToolkit import GithubToolkit


__all__ = [
    "GithubBranchTool",
    "GithubCommitTool",
    "GithubIssueTool",
    "GithubPRTool",
    "GithubRepoTool",
    "GithubToolkit",
]

try:
    # For Python 3.8 and newer
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For older Python versions, use the backport
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_toolkit_github")
except PackageNotFoundError:
    # If the package is not installed (for example, during development)
    __version__ = "0.0.0"
