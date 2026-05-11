import ast

from core.types.variable_metadata import VariableMetadata


def parse_arg(node: ast.arg) -> VariableMetadata:
    line_start = node.lineno
    line_end = line_start if node.end_lineno is None else node.end_lineno
    name = node.arg
    ty = node.annotation.id if isinstance(node.annotation, ast.Name) else None

    return VariableMetadata(
        name=name,
        line_start=line_start,
        line_end=line_end,
        ty=ty,
    )


def parse_assign(node: ast.AnnAssign) -> VariableMetadata | None:
    if not isinstance(node.target, ast.Name):
        return None

    line_start = node.lineno
    line_end = line_start if node.end_lineno is None else node.end_lineno
    name = node.target.id
    ty = node.annotation.id if isinstance(node.annotation, ast.Name) else None

    return VariableMetadata(
        name=name,
        line_start=line_start,
        line_end=line_end,
        ty=ty,
    )