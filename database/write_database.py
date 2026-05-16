import sqlite3

from core.types.class_metadata import ClassMetadata
from core.types.file_metadata import FileMetadata
from core.types.function_metadata import FunctionMetadata
from database.general_database import GeneralDatabase
from database.results.insert_result import (
    ClassInsertResult,
    ClassInsertResults,
    FileInsertResult,
    FunctionInsertResult,
    FunctionInsertResults,
)


class WriteDatabase(GeneralDatabase):
    def __init__(self, path: str):
        super().__init__(path)

    def save_file(self, f: FileMetadata) -> FileInsertResult | None:
        try:
            with self._connection:
                row = self._connection.execute(
                    """
                    INSERT INTO files (path, name) VALUES (?, ?)
                    ON CONFLICT (path) DO UPDATE SET name = excluded.name
                    RETURNING id
                    """,
                    (f.path, f.name),
                ).fetchone()
                file_id: int = row[0]

                classes: ClassInsertResults = {}
                functions: FunctionInsertResults = {}

                for c in f.classes:
                    result = self.save_class(file_id, c)
                    classes[result.name] = result

                for fu in f.functions:
                    result = self.save_function(file_id, fu)
                    functions[result.name] = result

            return FileInsertResult(id=file_id, name=f.name, classes=classes, functions=functions)

        except sqlite3.Error as e:
            print(f"[WriteDatabase] Failed to save '{f.name}': {e}")
            raise

    def save_class(self, file_id: int, c: ClassMetadata) -> ClassInsertResult:
        row = self._connection.execute(
            """
            INSERT INTO classes (file_id, name, line_start, line_end, doc, fields)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (file_id, name) DO UPDATE
                SET line_start = excluded.line_start,
                    line_end   = excluded.line_end,
                    doc        = excluded.doc,
                    fields     = excluded.fields
            RETURNING id
            """,
            (file_id, c.name, c.line_start, c.line_end, c.doc, self.encode_variables(c.fields)),
        ).fetchone()
        class_id: int = row[0]

        constructors: FunctionInsertResults = {}
        for ctor in c.constructors:
            result = self.save_function(file_id, ctor, class_id)
            constructors[result.name] = result

        methods: FunctionInsertResults = {}
        for m in c.methods:
            result = self.save_function(file_id, m, class_id)
            methods[result.name] = result

        return ClassInsertResult(id=class_id, name=c.name, constructors=constructors, methods=methods)

    def save_function(
        self, file_id: int, f: FunctionMetadata, class_id: int | None = None
    ) -> FunctionInsertResult:
        row = self._connection.execute(
            """
            INSERT INTO functions
                (file_id, name, line_start, line_end, doc, args, return_type, is_async, class_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (file_id, name, class_id) DO UPDATE
                SET line_start  = excluded.line_start,
                    line_end    = excluded.line_end,
                    doc         = excluded.doc,
                    args        = excluded.args,
                    return_type = excluded.return_type,
                    is_async    = excluded.is_async
            RETURNING id
            """,
            (
                file_id,
                f.name,
                f.line_start,
                f.line_end,
                f.doc,
                self.encode_variables(f.args),
                f.return_type,
                f.is_async,
                class_id,
            ),
        ).fetchone()
        return FunctionInsertResult(id=row[0], name=f.name)
