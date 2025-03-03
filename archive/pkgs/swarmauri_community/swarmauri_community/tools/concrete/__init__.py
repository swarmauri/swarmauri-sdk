from swarmauri.utils._lazy_import import _lazy_import

tool_files = [
    ("swarmauri_community.tools.concrete.CaptchaGeneratorTool", "CaptchaGeneratorTool"),
    ("swarmauri_community.tools.concrete.DaleChallReadabilityTool", "DaleChallReadabilityTool"),
    ("swarmauri_community.tools.concrete.DownloadPdfTool", "DownloadPDFTool"),
    ("swarmauri_community.tools.concrete.EntityRecognitionTool", "EntityRecognitionTool"),
    ("swarmauri_community.tools.concrete.FoliumTool", "FoliumTool"),
    ("swarmauri_community.tools.concrete.GithubBranchTool", "GithubBranchTool"),
    ("swarmauri_community.tools.concrete.GithubCommitTool", "GithubCommitTool"),
    ("swarmauri_community.tools.concrete.GithubIssueTool", "GithubIssueTool"),
    ("swarmauri_community.tools.concrete.GithubPRTool", "GithubPRTool"),
    ("swarmauri_community.tools.concrete.GithubRepoTool", "GithubRepoTool"),
    ("swarmauri_community.tools.concrete.GithubTool", "GithubTool"),
    ("swarmauri_community.tools.concrete.GmailReadTool", "GmailReadTool"),
    ("swarmauri_community.tools.concrete.GmailSendTool", "GmailSendTool"),
    ("swarmauri_community.tools.concrete.LexicalDensityTool", "LexicalDensityTool"),
    ("swarmauri_community.tools.concrete.PsutilTool", "PsutilTool"),
    ("swarmauri_community.tools.concrete.QrCodeGeneratorTool", "QrCodeGeneratorTool"),
    ("swarmauri_community.tools.concrete.SentenceComplexityTool", "SentenceComplexityTool"),
    ("swarmauri_community.tools.concrete.SentimentAnalysisTool", "SentimentAnalysisTool"),
    ("swarmauri_community.tools.concrete.SMOGIndexTool", "SMOGIndexTool"),
    ("swarmauri_community.tools.concrete.WebScrapingTool", "WebScrapingTool"),
    ("swarmauri_community.tools.concrete.ZapierHookTool", "ZapierHookTool"),
    # ("swarmauri_community.tools.concrete.PaCMAPTool", "PaCMAPTool"),
]

# Lazy loading of tools, storing them in variables
for module_name, class_name in tool_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded tools to __all__
__all__ = [class_name for _, class_name in tool_files]
