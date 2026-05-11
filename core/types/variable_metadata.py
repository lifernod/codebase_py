from dataclasses import dataclass, field


@dataclass
class VariableMetadata:
    name: str
    ty: str | None = field(default=None)

    def __str__(self):
        if self.ty is None:
            return self.name
        return f"{self.name}:{self.ty}"