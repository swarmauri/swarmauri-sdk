from typing import Dict
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion

from swarmauri_tool_jupyterclearoutput.JupyterClearOutputTool import (
    JupyterClearOutputTool,
)
from swarmauri_tool_jupyterdisplay.JupyterDisplayTool import JupyterDisplayTool
from swarmauri_tool_jupyterdisplayhtml.JupyterDisplayHtmlTool import (
    JupyterDisplayHtmlTool,
)
from swarmauri_tool_jupyterexecuteandconvert.JupyterExecuteAndConvertTool import (
    JupyterExecuteAndConvertTool,
)
from swarmauri_tool_jupyterexecutecell.JupyterExecuteCellTool import (
    JupyterExecuteCellTool,
)
from swarmauri_tool_jupyterexecutenotebook.JupyterExecuteNotebookTool import (
    JupyterExecuteNotebookTool,
)
from swarmauri_tool_jupyterexecutenotebookwithparameters.JupyterExecuteNotebookWithParametersTool import (
    JupyterExecuteNotebookWithParametersTool,
)
from swarmauri_tool_jupyterexporthtml.JupyterExportHtmlTool import JupyterExportHtmlTool
from swarmauri_tool_jupyterexportlatex.JupyterExportLatexTool import (
    JupyterExportLatexTool,
)
from swarmauri_tool_jupyterexportmarkdown.JupyterExportMarkdownTool import (
    JupyterExportMarkdownTool,
)
from swarmauri_tool_jupyterexportpython.JupyterExportPythonTool import (
    JupyterExportPythonTool,
)
from swarmauri_tool_jupyterfromdict.JupyterFromDictTool import JupyterFromDictTool
from swarmauri_tool_jupytergetiopubmessage.JupyterGetIOPubMessageTool import (
    JupyterGetIOPubMessageTool,
)
from swarmauri_tool_jupytergetshellmessage.JupyterGetShellMessageTool import (
    JupyterGetShellMessageTool,
)
from swarmauri_tool_jupyterreadnotebook.JupyterReadNotebookTool import (
    JupyterReadNotebookTool,
)
from swarmauri_tool_jupyterruncell.JupyterRunCellTool import JupyterRunCellTool
from swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool import (
    JupyterShutdownKernelTool,
)
from swarmauri_tool_jupyterstartkernel.JupyterStartKernelTool import (
    JupyterStartKernelTool,
)
from swarmauri_tool_jupytervalidatenotebook.JupyterValidateNotebookTool import (
    JupyterValidateNotebookTool,
)
from swarmauri_tool_jupyterwritenotebook.JupyterWriteNotebookTool import (
    JupyterWriteNotebookTool,
)


@ComponentBase.register_type(ToolkitBase, "JupyterToolkit")
class JupyterToolkit(ToolkitBase):
    tools: Dict[str, SubclassUnion[ToolBase]] = {
        "JupyterClearOutputTool": JupyterClearOutputTool(),
        "JupyterDisplayTool": JupyterDisplayTool(),
        "JupyterDisplayHtmlTool": JupyterDisplayHtmlTool(),
        "JupyterExecuteAndConvertTool": JupyterExecuteAndConvertTool(),
        "JupyterExecuteCellTool": JupyterExecuteCellTool(),
        "JupyterExecuteNotebookTool": JupyterExecuteNotebookTool(),
        "JupyterExecuteNotebookWithParametersTool": JupyterExecuteNotebookWithParametersTool(),
        "JupyterExportHtmlTool": JupyterExportHtmlTool(),
        "JupyterExportLatexTool": JupyterExportLatexTool(),
        "JupyterExportMarkdownTool": JupyterExportMarkdownTool(),
        "JupyterExportPythonTool": JupyterExportPythonTool(),
        "JupyterFromDictTool": JupyterFromDictTool(),
        "JupyterGetIOPubMessageTool": JupyterGetIOPubMessageTool(),
        "JupyterGetShellMessageTool": JupyterGetShellMessageTool(),
        "JupyterReadNotebookTool": JupyterReadNotebookTool(),
        "JupyterRunCellTool": JupyterRunCellTool(),
        "JupyterShutdownKernelTool": JupyterShutdownKernelTool(),
        "JupyterStartKernelTool": JupyterStartKernelTool(),
        "JupyterValidateNotebookTool": JupyterValidateNotebookTool(),
        "JupyterWriteNotebookTool": JupyterWriteNotebookTool(),
    }
