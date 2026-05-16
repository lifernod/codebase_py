from typing import Literal

from fastapi import FastAPI, HTTPException, Query

from database.read_database import ReadDatabase
from database.results.search_result import FileListResult, FileContentResult, SearchResult, StatsResult

app = FastAPI(title="Codebase Explorer API", version="1.0.0")
db = ReadDatabase("data/codebase.db")


@app.get("/api/files", response_model=list[FileListResult])
def list_files(
    limit: int | None = Query(default=None, ge=10, description="Максимальное количество записей для возврата"),
    offset: int = Query(default=0, ge=0, description="Количество записей для пропуска"),
):
    return db.list_files(limit=limit, offset=offset)


@app.get("/api/files/{name}/structure", response_model=FileContentResult)
def file_structure(name: str):
    result = db.get_file_content(name)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Файл '{name}' не найден")
    return result


@app.get("/api/search", response_model=list[SearchResult])
def search(
    q: str = Query(default="", description="Слово для поиска"),
    type: Literal["class", "function"] | None = Query(
        default=None, description="Фильтр для типа сущности: 'class' | 'function'"
    ),
    limit: int | None = Query(default=None, ge=1, description="Максимальное количество записей для возврата"),
    offset: int = Query(default=0, ge=0, description="Количество записей для пропуска"),
):
    if not q.strip():
        return []
    return db.search(keyword=q, kind=type, limit=limit, offset=offset)


@app.get("/api/stats", response_model=StatsResult)
def stats():
    return db.get_stats()
