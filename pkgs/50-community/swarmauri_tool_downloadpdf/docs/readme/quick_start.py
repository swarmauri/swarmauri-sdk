from swarmauri_tool_downloadpdf import DownloadPDFTool

tool = DownloadPDFTool()
result = tool(
    "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
)

print(result.keys())
