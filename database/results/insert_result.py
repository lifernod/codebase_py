from dataclasses import dataclass

@dataclass(slots=True)
class FunctionInsertResult:
    id: int
    name: str

type FunctionInsertResults = dict[str, FunctionInsertResult]

@dataclass(slots=True)
class ClassInsertResult:
    id: int
    name: str
    constructors: FunctionInsertResults
    methods: FunctionInsertResults

type ClassInsertResults = dict[str, ClassInsertResult]

@dataclass(slots=True)
class FileInsertResult:
    id: int
    name: str
    classes: ClassInsertResults
    functions: FunctionInsertResults