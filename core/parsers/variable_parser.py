import ast

from core.types.variable_metadata import VariableMetadata


def parse_arg(node: ast.arg) -> VariableMetadata:
    name = node.arg
    ty = node.annotation.id if isinstance(node.annotation, ast.Name) else None

    return VariableMetadata(
        name=name,
        ty=ty,
    )


def parse_assign(node: ast.AnnAssign) -> VariableMetadata | None:
    if not isinstance(node.target, ast.Name):
        return None

    name = node.target.id
    ty = node.annotation.id if isinstance(node.annotation, ast.Name) else None

    return VariableMetadata(
        name=name,
        ty=ty,
    )