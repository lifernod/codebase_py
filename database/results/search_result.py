from dataclasses import dataclass
from typing import Literal, Any

from core.types.class_metadata import ClassMetadata
from core.types.function_metadata import FunctionMetadata


@dataclass
class FileListResult:
    path: str
    name: str
    function_count: int
    class_count: int

@dataclass
class FileContentResult:
    functions: list[FunctionMetadata]
    classes: list[ClassMetadata]

@dataclass
class SearchResult:
    kind: Literal["function", "class"]
    value: dict[Any, Any]