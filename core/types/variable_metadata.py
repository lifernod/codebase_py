from dataclasses import dataclass, field


@dataclass
class VariableMetadata:
    name: str
    line_start: int = field(default=0)
    line_end: int = field(default=0)
    ty: str | None = field(default=None)

    def __str__(self):
        if self.ty is None:
            return self.name
        return f"{self.name}:{self.ty}"