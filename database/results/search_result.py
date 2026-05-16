from dataclasses import dataclass
from typing import Any, Literal

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
    classes: list[ClassMetadata]
    functions: list[FunctionMetadata]


@dataclass
class SearchResult:
    kind: Literal["function", "class"]
    value: dict[str, Any]


@dataclass
class StatsResult:
    file_count: int
    class_count: int
    function_count: int
