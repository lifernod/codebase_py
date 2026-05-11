import ast
import os
from concurrent.futures.process import ProcessPoolExecutor

from core.parsers.class_parser import parse_class
from core.parsers.function_parser import parse_function
from core.types.file_metadata import FileMetadata


def parse_file(path: str) -> FileMetadata:
    with open(path, "r") as file:
        data = file.read()

    tree = ast.parse(data)

    fm = FileMetadata(
        path=path,
        name=os.path.basename(path)
    )

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            fm.classes.append(parse_class(node))
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            fm.functions.append(parse_function(node))
        else:
            continue

    return fm


def process_dir(path: str) -> list[FileMetadata]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Указанного пути не существует: {path}")

    if not os.path.isdir(path):
        return [parse_file(path)]

    files = [
        os.path.join(path, f)
        for f in os.listdir(path) if f.endswith(".py")
    ]

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = list(executor.map(parse_file, files))

    return results
