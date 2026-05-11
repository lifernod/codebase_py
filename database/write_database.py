import sqlite3

from core.types.class_metadata import ClassMetadata
from core.types.file_metadata import FileMetadata
from core.types.function_metadata import FunctionMetadata
from database.general_database import GeneralDatabase
from database.insert_result import FunctionInsertResult, ClassInsertResult, ClassInsertResults, FunctionInsertResults, \
    FileInsertResult


class WriteDatabase(GeneralDatabase):
    def __init__(self, path: str):
        super().__init__(path)

    def save_file(self, f: FileMetadata) -> FileInsertResult | None:
        self._connection.execute("BEGIN")

        try:
            self._cursor.execute(
                """
                INSERT INTO files (path, name)
                VALUES (?, ?)
                ON CONFLICT DO NOTHING
                """,
                (f.path, f.name,)
            )

            self._cursor.execute("SELECT id FROM files WHERE path = ?", (f.path,))

            file_id = self._cursor.fetchone()[0]
            if file_id is None:
                return None

            classes: ClassInsertResults = {}
            functions: FunctionInsertResults = {}
            if f.classes:
                for c in f.classes:
                    result = self.save_class(file_id, c)
                    classes[result.name] = result

            if f.functions:
                for fu in f.functions:
                    result = self.save_function(file_id, fu)
                    functions[result.name] = result

            self._connection.commit()

            return FileInsertResult(
                id=file_id,
                name=f.name,
                classes=classes,
                functions=functions
            )
        except sqlite3.IntegrityError as e:
            self._connection.rollback()
            raise e

    def save_class(self, file_id: int, c: ClassMetadata) -> ClassInsertResult:
        self._cursor.execute(
            """
            INSERT INTO classes (file_id, name, line_start, line_end, doc, fields)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (file_id, name) DO UPDATE
                SET name        = excluded.name,
                    line_start  = excluded.line_start,
                    line_end    = excluded.line_end,
                    doc         = excluded.doc,
                    fields      = excluded.fields
            RETURNING id
            """,
            (
                file_id,
                c.name,
                c.line_start,
                c.line_end,
                c.doc,
                self.encode_variables(c.fields),
            )
        )
        class_id = self._cursor.fetchone()[0]

        methods: FunctionInsertResults = {}
        constructors: FunctionInsertResults = {}
        if c.constructors:
            for ctor in c.constructors:
                result = self.save_function(file_id, ctor, class_id)
                constructors[result.name] = result

        if c.methods:
            for m in c.methods:
                result = self.save_function(file_id, m, class_id)
                methods[result.name] = result

        return ClassInsertResult(
            id=class_id,
            name=c.name,
            constructors=constructors,
            methods=methods
        )

    def save_function(self, file_id: int, f: FunctionMetadata, class_id: int | None = None) -> FunctionInsertResult:
        self._cursor.execute(
            """
            INSERT INTO functions (file_id, name, line_start, line_end, doc, args, return_type, is_async, class_id) 
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT (file_id, name) DO UPDATE 
                SET name = excluded.name,
                    line_start = excluded.line_start,
                    line_end = excluded.line_end,
                    doc = excluded.doc,
                    args = excluded.args,
                    return_type = excluded.return_type,
                    is_async = excluded.is_async,
                    class_id = excluded.class_id
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
            )
        )
        return FunctionInsertResult(
            id=self._cursor.fetchone()[0],
            name=f.name
        )