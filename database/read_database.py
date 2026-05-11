from core.types.class_metadata import ClassMetadata
from core.types.function_metadata import FunctionMetadata
from database.general_database import GeneralDatabase
from database.results.search_result import FileListResult, FileContentResult, SearchResult


class ReadDatabase(GeneralDatabase):
    def __init__(self, path: str):
        super().__init__(path)

    def list_files(self) -> list[FileListResult]:
        self._cursor.execute(
            """
            SELECT f.path, f.name, COUNT (fu.id) as function_count, COUNT(cl.id) as class_count
            FROM files f
            LEFT JOIN functions fu ON fu.file_id = f.id
            LEFT JOIN classes cl ON cl.file_id = f.id
            GROUP BY f.id
            """
        )

        results: list[FileListResult] = []
        for row in self._cursor.fetchall():
            print(row)
            if row is not None:
                results.append(FileListResult(
                    path=row[0],
                    name=row[1],
                    function_count=row[2],
                    class_count=row[3]
                ))
        print(results)
        return results

    def get_file_content(self, name: str) -> FileContentResult | None:
        self._cursor.execute("SELECT id FROM files WHERE name = ?", (name,))
        file_id = self._cursor.fetchone()[0]
        if file_id is None:
            return None

        classes = self.list_classes(file_id)
        functions = self.list_functions(file_id)

        return FileContentResult(
            classes=classes,
            functions=functions
        )

    def search(self, keyword: str) -> list[SearchResult]:
        pattern = f"%{keyword}%"
        results: list[SearchResult] = []

        class_rows = self._cursor.execute(
            """
            SELECT c.name,
                   c.doc,
                   c.line_start,
                   c.line_end,
                   f.path AS file_path
            FROM classes c
                     JOIN files f ON c.file_id = f.id
            WHERE c.name LIKE ? COLLATE NOCASE
               OR c.doc LIKE ? COLLATE NOCASE
            ORDER BY f.path, c.line_start
            """,
            (pattern, pattern),
        ).fetchall()

        for r in class_rows:
            results.append(SearchResult(
                kind="class",
                value=dict(r)
            ))

        func_rows = self._cursor.execute(
            """
            SELECT fu.name,
                   fu.doc,
                   fu.line_start,
                   fu.line_end,
                   f.path AS file_path,
                   c.name AS class_name
            FROM functions fu
                     JOIN files f ON fu.file_id = f.id
                     LEFT JOIN classes c ON fu.class_id = c.id
            WHERE fu.name LIKE ? COLLATE NOCASE
               OR fu.doc LIKE ? COLLATE NOCASE
            ORDER BY f.path, fu.line_start
            """,
            (pattern, pattern),
        ).fetchall()

        for r in func_rows:
            results.append(SearchResult(
                kind="function",
                value=dict(r)
            ))

        return results

    def list_classes(self, file_id: int) -> list[ClassMetadata]:
        self._cursor.execute(
            """
            SELECT 
                name,
                line_start,
                line_end,
                doc,
                fields
            FROM classes
            WHERE file_id = ?
            """,
            (file_id,)
        )

        results: list[ClassMetadata] = []
        for row in self._cursor.fetchall():
            if row is not None:
                results.append(ClassMetadata(
                    name=row[0],
                    line_start=row[1],
                    line_end=row[2],
                    doc=row[3],
                    fields=self.decode_variables(row[4]),
                ))

        return results

    def list_functions(self, file_id: int) -> list[FunctionMetadata]:
        self._cursor.execute(
            """
            SELECT name,
                   line_start,
                   line_end,
                   doc,
                   args,
                   is_async,
                   return_type,
                    class_id
            FROM functions
            WHERE file_id = ?
            """,
            (file_id,)
        )

        results: list[FunctionMetadata] = []
        for row in self._cursor.fetchall():
            if row is not None:
                results.append(FunctionMetadata(
                    name=row[0],
                    line_start=row[1],
                    line_end=row[2],
                    doc=row[3],
                    args=self.decode_variables(row[4]),
                    is_async=row[5],
                    return_type=row[6],
                    is_class_method=True if row[7] is not None else False
                ))

        return results