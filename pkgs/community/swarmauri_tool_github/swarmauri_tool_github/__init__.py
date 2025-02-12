from .GithubBranchTool import GithubBranchTool
from .GithubCommitTool import GithubCommitTool
from .GithubIssueTool import GithubIssueTool
from .GithubPRTool import GithubPRTool
from .GithubRepoTool import GithubRepoTool
from .GithubTool import GithubTool


__all__ = [
    "GithubBranchTool",
    "GithubCommitTool",
    "GithubIssueTool",
    "GithubPRTool",
    "GithubRepoTool",
    "GithubTool"
]

try:
    # For Python 3.8 and newer
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For older Python versions, use the backport
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_tool_github")
except PackageNotFoundError:
    # If the package is not installed (for example, during development)
    __version__ = "0.0.0"
