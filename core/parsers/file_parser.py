import ast
import os
from concurrent.futures import ProcessPoolExecutor

from core.parsers.class_parser import parse_class
from core.parsers.function_parser import parse_function
from core.types.file_metadata import FileMetadata


def parse_file(path: str) -> FileMetadata:
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    fm = FileMetadata(path=path, name=os.path.basename(path))

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            fm.classes.append(parse_class(node))
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            fm.functions.append(parse_function(node))

    return fm


def _collect_py_files(path: str) -> list[str]:
    found: list[str] = []
    for root, _, filenames in os.walk(path):
        for name in filenames:
            if name.endswith(".py"):
                found.append(os.path.join(root, name))
    return found


def process_dir(path: str) -> list[FileMetadata]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Указанного пути не существует: {path}")

    if not os.path.isdir(path):
        return [parse_file(path)]

    files = _collect_py_files(path)
    if not files:
        return []

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = list(executor.map(parse_file, files))

    return results
