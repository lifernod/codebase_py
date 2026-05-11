from dataclasses import dataclass, field

from core.types.variable_metadata import VariableMetadata


@dataclass
class FunctionMetadata:
    name: str
    line_start: int = field(default=0)
    line_end: int = field(default=0)

    args: list[VariableMetadata] = field(default_factory=list)
    return_type: str = field(default="None")
    doc: str | None = field(default=None)

    is_async: bool = field(default=False)

    is_class_method: bool = field(default=False)
