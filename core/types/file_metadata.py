from dataclasses import dataclass, field

from core.types.class_metadata import ClassMetadata
from core.types.function_metadata import FunctionMetadata


@dataclass
class FileMetadata:
    path: str
    name: str

    functions: list[FunctionMetadata] = field(default_factory=list)
    classes: list[ClassMetadata] = field(default_factory=list)