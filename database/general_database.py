import sqlite3

from core.types.variable_metadata import VariableMetadata


class GeneralDatabase:
    _connection: sqlite3.Connection
    _cursor: sqlite3.Cursor

    def __init__(self, db_path: str) -> None:
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL;")
        self._connection.execute("PRAGMA foreign_keys=ON;")
        self._cursor = self._connection.cursor()
        self.__up()

    def __up(self):
        with open("data/up.sql", "r") as f:
            self._connection.executescript(f.read())

    def __down(self):
        with open("data/down.sql", "r") as f:
            self._connection.executescript(f.read())

    def encode_variables(self, variables: list[VariableMetadata]) -> bytes:
        return ",".join(str(v) for v in variables).encode("utf-8")

    def decode_variables(self, b: bytes | None) -> list[VariableMetadata]:
        if not b:
            return []
        raw = b.decode("utf-8")
        if not raw.strip():
            return []

        result: list[VariableMetadata] = []
        for token in raw.split(","):
            token = token.strip()
            if not token:
                continue
            parts = token.split(":", 1)
            result.append(VariableMetadata(
                name=parts[0],
                ty=parts[1] if len(parts) == 2 else None,
            ))
        return result

    def close(self):
        self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
