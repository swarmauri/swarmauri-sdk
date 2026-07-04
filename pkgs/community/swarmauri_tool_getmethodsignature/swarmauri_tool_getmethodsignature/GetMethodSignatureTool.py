import ast
import inspect
from typing import Any, Dict, List, Literal, Optional

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


def _unparse(node: Optional[ast.expr]) -> Optional[str]:
    """Render an AST expression node back to source text."""
    if node is None:
        return None
    return ast.unparse(node)


def _extract_signature(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> Dict[str, Any]:
    """Build the signature descriptor for a single function node."""
    args = node.args
    params: List[Dict[str, Optional[str]]] = []

    posonly_count = len(args.posonlyargs)
    posargs: List[ast.arg] = list(args.posonlyargs) + list(args.args)
    defaults: List[ast.expr] = list(args.defaults)
    offset = len(posargs) - len(defaults)
    for idx, arg in enumerate(posargs):
        default = None
        if idx >= offset:
            default = _unparse(defaults[idx - offset])
        kind = (
            inspect.Parameter.POSITIONAL_ONLY.name
            if idx < posonly_count
            else inspect.Parameter.POSITIONAL_OR_KEYWORD.name
        )
        params.append(
            {
                "name": arg.arg,
                "annotation": _unparse(arg.annotation),
                "default": default,
                "kind": kind,
            }
        )

    if args.vararg is not None:
        params.append(
            {
                "name": args.vararg.arg,
                "annotation": _unparse(args.vararg.annotation),
                "default": None,
                "kind": inspect.Parameter.VAR_POSITIONAL.name,
            }
        )

    for kw_arg, kw_default in zip(args.kwonlyargs, args.kw_defaults):
        params.append(
            {
                "name": kw_arg.arg,
                "annotation": _unparse(kw_arg.annotation),
                "default": _unparse(kw_default),
                "kind": inspect.Parameter.KEYWORD_ONLY.name,
            }
        )

    if args.kwarg is not None:
        params.append(
            {
                "name": args.kwarg.arg,
                "annotation": _unparse(args.kwarg.annotation),
                "default": None,
                "kind": inspect.Parameter.VAR_KEYWORD.name,
            }
        )

    return_type = _unparse(node.returns)
    is_async = isinstance(node, ast.AsyncFunctionDef)
    args_str = ast.unparse(args)
    ret_str = f" -> {return_type}" if return_type is not None else ""
    prefix = "async def " if is_async else "def "
    type_params = getattr(node, "type_params", None)
    type_params_str = ""
    if type_params:
        type_params_str = "[" + ", ".join(ast.unparse(tp) for tp in type_params) + "]"
    signature = f"{prefix}{node.name}{type_params_str}({args_str}){ret_str}"

    return {
        "name": node.name,
        "parameters": params,
        "return_type": return_type,
        "signature": signature,
        "is_async": is_async,
    }


@ComponentBase.register_type(ToolBase, "GetMethodSignatureTool")
class GetMethodSignatureTool(ToolBase):
    """
    Tool that parses Python source code and returns the signature of a
    specified function or method (name, parameters, return type).
    """

    version: str = "0.1.dev1"
    name: str = "GetMethodSignatureTool"
    description: str = (
        "Parses Python source code and returns the signature of a "
        "specified method or function (name, parameters, return type)."
    )
    type: Literal["GetMethodSignatureTool"] = "GetMethodSignatureTool"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="source",
                input_type="string",
                description="Python source code to parse.",
                required=True,
            ),
            Parameter(
                name="method_name",
                input_type="string",
                description=("Name of the function or method to inspect."),
                required=True,
            ),
        ]
    )

    def __call__(self, source: str, method_name: str) -> Dict[str, Any]:
        """
        Parse ``source`` and return the signature of ``method_name``.

        Returns a single signature dict, an ``overloads`` list when
        multiple definitions share the name, or an ``error`` dict.
        """
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            return {"error": f"Failed to parse source: {exc}"}

        matches: List[ast.FunctionDef | ast.AsyncFunctionDef] = [
            n
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.name == method_name
        ]

        if not matches:
            return {
                "error": (
                    f"No function or method named "
                    f"'{method_name}' found in source."
                )
            }

        signatures = [_extract_signature(n) for n in matches]

        if len(signatures) == 1:
            return signatures[0]
        return {"overloads": signatures}
