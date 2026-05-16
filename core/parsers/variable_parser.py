import ast

from core.types.variable_metadata import VariableMetadata


def _unparse_annotation(node: ast.expr | None) -> str | None:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None


def parse_arg(node: ast.arg) -> VariableMetadata:
    return VariableMetadata(
        name=node.arg,
        ty=_unparse_annotation(node.annotation),
    )


def parse_assign(node: ast.AnnAssign) -> VariableMetadata | None:
    if not isinstance(node.target, ast.Name):
        return None
    return VariableMetadata(
        name=node.target.id,
        ty=_unparse_annotation(node.annotation),
    )
