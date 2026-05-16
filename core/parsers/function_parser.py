import ast

from core.parsers.variable_parser import parse_arg
from core.types.function_metadata import FunctionMetadata
from core.types.variable_metadata import VariableMetadata


def _unparse_annotation(node: ast.expr | None) -> str | None:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None


def parse_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionMetadata:
    name = node.name
    line_start = node.lineno
    line_end = line_start if node.end_lineno is None else node.end_lineno
    doc = ast.get_docstring(node)
    is_async = isinstance(node, ast.AsyncFunctionDef)

    args: list[VariableMetadata] = [parse_arg(arg) for arg in node.args.args]

    return_type = _unparse_annotation(node.returns)  # None means "no annotation"

    return FunctionMetadata(
        name=name,
        line_start=line_start,
        line_end=line_end,
        args=args,
        return_type=return_type,
        doc=doc,
        is_async=is_async,
    )
