import ast

from core.parsers.function_parser import parse_function
from core.parsers.variable_parser import parse_assign
from core.types.class_metadata import ClassMetadata


def parse_class(node: ast.ClassDef) -> ClassMetadata:
    name = node.name
    line_start = node.lineno
    line_end = line_start if node.end_lineno is None else node.end_lineno
    doc = ast.get_docstring(node)

    cls = ClassMetadata(
        name=name,
        line_start=line_start,
        line_end=line_end,
        doc=doc,
    )

    for item in node.body:
        if isinstance(item, ast.AnnAssign):
            field = parse_assign(item)
            if field is not None:
                cls.add_field(field)
        elif isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            method = parse_function(item)
            cls.add_method(method)
        else:
            continue

    return cls