from dataclasses import dataclass, field

from core.types.function_metadata import FunctionMetadata
from core.types.variable_metadata import VariableMetadata


@dataclass
class ClassMetadata:
    name: str
    line_start: int = field(default=0)
    line_end: int = field(default=0)

    doc: str | None = field(default=None)

    fields: list[VariableMetadata] = field(default_factory=list)
    constructors: list[FunctionMetadata] = field(default_factory=list)
    methods: list[FunctionMetadata] = field(default_factory=list)

    def add_field(self, f: VariableMetadata):
        self.fields.append(f)

    def add_method(self, f: FunctionMetadata):
        f.class_name = self.name
        f.is_class_method = True

        if f.name == "__init__":
            f.name = f"{self.name}.__init__/{len(f.args)}"
            self.constructors.append(f)
        else:
            f.name = f"{self.name}.{f.name}"
            self.methods.append(f)