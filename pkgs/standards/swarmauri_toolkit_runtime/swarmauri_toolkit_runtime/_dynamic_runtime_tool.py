import ast
from typing import Any, Dict, Literal

from pydantic import ConfigDict, Field

from swarmauri_base.tools.ToolBase import ToolBase


SAFE_BUILTINS = {
    "abs": abs,
    "bool": bool,
    "dict": dict,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "round": round,
    "set": set,
    "str": str,
    "sum": sum,
    "tuple": tuple,
}

ALLOWED_AST_NODES = (
    ast.Add,
    ast.And,
    ast.BinOp,
    ast.BoolOp,
    ast.Compare,
    ast.Constant,
    ast.Dict,
    ast.Div,
    ast.Eq,
    ast.Expression,
    ast.FloorDiv,
    ast.Gt,
    ast.GtE,
    ast.IfExp,
    ast.List,
    ast.Load,
    ast.Lt,
    ast.LtE,
    ast.Mod,
    ast.Mult,
    ast.Name,
    ast.Not,
    ast.NotEq,
    ast.Or,
    ast.Pow,
    ast.Set,
    ast.Sub,
    ast.Tuple,
    ast.USub,
    ast.UnaryOp,
    ast.Call,
)


class SafeExpressionValidator(ast.NodeVisitor):
    def __init__(self, allowed_names: set[str]):
        self.allowed_names = allowed_names

    def generic_visit(self, node):
        if not isinstance(node, ALLOWED_AST_NODES):
            raise ValueError(
                f"Runtime tool '__call__' contains unsafe syntax: {type(node).__name__}"
            )
        super().generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if node.id not in self.allowed_names:
            raise ValueError(
                f"Runtime tool '__call__' references disallowed name '{node.id}'"
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError(
                "Runtime tool '__call__' only allows direct calls to approved builtins"
            )
        if node.func.id not in SAFE_BUILTINS:
            raise ValueError(
                f"Runtime tool '__call__' cannot call '{node.func.id}' safely"
            )
        self.generic_visit(node)


class DynamicRuntimeTool(ToolBase):
    model_config = ConfigDict(populate_by_name=True)

    version: str = "0.1.0"
    type: str
    runtime_kind: Literal["dynamic"] = Field(default="dynamic", exclude=True)
    call_source: str = Field(alias="__call__", serialization_alias="__call__")

    def validate_call_source(self) -> "DynamicRuntimeTool":
        self._compile_expression(self._normalized_expression())
        return self

    def __call__(self, *args, **kwargs) -> Any:
        try:
            expression = self._normalized_expression()
            compiled = self._compile_expression(expression)
            runtime_inputs = self._bind_inputs(args, kwargs)
            runtime_globals = {"__builtins__": {}}
            runtime_locals = {**SAFE_BUILTINS, **runtime_inputs}
            return eval(compiled, runtime_globals, runtime_locals)
        except BaseException as exc:
            return self._safe_error_result(exc)

    def _normalized_expression(self) -> str:
        expression = self.call_source.strip()
        if expression.startswith("return "):
            expression = expression[7:].strip()
        if not expression:
            raise ValueError("Runtime tool '__call__' must not be empty")
        return expression

    def _compile_expression(self, expression: str):
        try:
            parsed = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise ValueError(
                "Runtime tool '__call__' must be a safe Python expression"
            ) from exc

        allowed_names = {
            parameter.name for parameter in self.parameters
        } | set(SAFE_BUILTINS)
        SafeExpressionValidator(allowed_names).visit(parsed)
        return compile(
            parsed, filename=f"<runtime-tool:{self.name}>", mode="eval"
        )

    def _bind_inputs(
        self, args: tuple[Any, ...], kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        parameter_names = [parameter.name for parameter in self.parameters]
        if len(args) > len(parameter_names):
            raise ValueError(
                f"Runtime tool '{self.name}' received too many positional arguments"
            )

        bound_inputs: Dict[str, Any] = dict(zip(parameter_names, args))
        for key, value in kwargs.items():
            if key not in parameter_names:
                raise ValueError(
                    f"Runtime tool '{self.name}' received unexpected argument '{key}'"
                )
            if key in bound_inputs:
                raise ValueError(
                    f"Runtime tool '{self.name}' received duplicate argument '{key}'"
                )
            bound_inputs[key] = value

        for parameter in self.parameters:
            if parameter.required and parameter.name not in bound_inputs:
                raise ValueError(
                    f"Runtime tool '{self.name}' is missing required argument '{parameter.name}'"
                )
        return bound_inputs

    def _safe_error_result(self, exc: BaseException) -> Dict[str, Any]:
        return {
            "status": "error",
            "tool_name": self.name,
            "tool_type": self.type,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
