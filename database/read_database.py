from core.types.class_metadata import ClassMetadata
from core.types.function_metadata import FunctionMetadata
from database.general_database import GeneralDatabase
from database.results.search_result import (
    FileListResult,
    FileContentResult,
    SearchResult,
    StatsResult,
)


class ReadDatabase(GeneralDatabase):
    def __init__(self, path: str):
        super().__init__(path)

    def list_files(self, limit: int | None = None, offset: int = 0) -> list[FileListResult]:
        sql = """
            SELECT f.path,
                   f.name,
                   COUNT(DISTINCT fu.id) AS function_count,
                   COUNT(DISTINCT cl.id) AS class_count
            FROM   files f
            LEFT JOIN functions fu ON fu.file_id = f.id
            LEFT JOIN classes   cl ON cl.file_id = f.id
            GROUP  BY f.id
            ORDER  BY f.path
        """
        params: list = []
        if limit is not None:
            sql += " LIMIT ? OFFSET ?"
            params = [limit, offset]

        rows = self._connection.execute(sql, params).fetchall()
        return [
            FileListResult(
                path=row["path"],
                name=row["name"],
                function_count=row["function_count"],
                class_count=row["class_count"],
            )
            for row in rows
        ]

    def get_file_content(self, name: str) -> FileContentResult | None:
        row = self._connection.execute(
            "SELECT id FROM files WHERE name = ?", (name,)
        ).fetchone()
        if row is None:
            return None
        file_id: int = row["id"]

        return FileContentResult(
            classes=self._list_classes(file_id),
            functions=self._list_functions(file_id),
        )

    def _list_classes(self, file_id: int) -> list[ClassMetadata]:
        rows = self._connection.execute(
            """
            SELECT name, line_start, line_end, doc, fields
            FROM   classes
            WHERE  file_id = ?
            ORDER  BY line_start
            """,
            (file_id,),
        ).fetchall()
        return [
            ClassMetadata(
                name=row["name"],
                line_start=row["line_start"],
                line_end=row["line_end"],
                doc=row["doc"],
                fields=self.decode_variables(row["fields"]),
            )
            for row in rows
        ]

    def _list_functions(self, file_id: int) -> list[FunctionMetadata]:
        rows = self._connection.execute(
            """
            SELECT name, line_start, line_end, doc, args,
                   is_async, return_type, class_id
            FROM   functions
            WHERE  file_id = ?
            ORDER  BY line_start
            """,
            (file_id,),
        ).fetchall()
        return [
            FunctionMetadata(
                name=row["name"],
                line_start=row["line_start"],
                line_end=row["line_end"],
                doc=row["doc"],
                args=self.decode_variables(row["args"]),
                is_async=bool(row["is_async"]),
                return_type=row["return_type"],
                is_class_method=row["class_id"] is not None,
            )
            for row in rows
        ]

    def search(
        self,
        keyword: str,
        kind: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[SearchResult]:
        pattern = f"%{keyword}%"
        results: list[SearchResult] = []

        if kind != "function":
            class_rows = self._connection.execute(
                """
                SELECT c.name, c.doc, c.line_start, c.line_end, f.path AS file_path
                FROM   classes c
                JOIN   files f ON c.file_id = f.id
                WHERE  c.name LIKE ? COLLATE NOCASE
                   OR  c.doc  LIKE ? COLLATE NOCASE
                ORDER  BY f.path, c.line_start
                """,
                (pattern, pattern),
            ).fetchall()
            for r in class_rows:
                results.append(SearchResult(kind="class", value=dict(r)))

        if kind != "class":
            func_rows = self._connection.execute(
                """
                SELECT fu.name, fu.doc, fu.line_start, fu.line_end,
                       f.path AS file_path, c.name AS class_name
                FROM   functions fu
                JOIN   files f ON fu.file_id = f.id
                LEFT JOIN classes c ON fu.class_id = c.id
                WHERE  fu.name LIKE ? COLLATE NOCASE
                   OR  fu.doc  LIKE ? COLLATE NOCASE
                ORDER  BY f.path, fu.line_start
                """,
                (pattern, pattern),
            ).fetchall()
            for r in func_rows:
                results.append(SearchResult(kind="function", value=dict(r)))

        if limit is not None:
            results = results[offset : offset + limit]

        return results

    def get_stats(self) -> StatsResult:
        row = self._connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM files)     AS file_count,
                (SELECT COUNT(*) FROM classes)   AS class_count,
                (SELECT COUNT(*) FROM functions) AS function_count
            """
        ).fetchone()
        return StatsResult(
            file_count=row["file_count"],
            class_count=row["class_count"],
            function_count=row["function_count"],
        )
