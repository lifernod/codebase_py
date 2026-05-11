from fastapi import FastAPI, HTTPException

from database.read_database import ReadDatabase
from database.results.search_result import FileListResult, FileContentResult, SearchResult

app = FastAPI(title="Codebase Explorer API", version="1.0.0")
db = ReadDatabase("data/codebase.db")


@app.get("/api/files", response_model=list[FileListResult])
def list_files():
    return db.list_files()


@app.get("/api/files/{name}/structure", response_model=FileContentResult)
def file_structure(name: str):
    result = db.get_file_content(name)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Файл '{name}' не найден")
    return result


@app.get("/api/search", response_model=list[SearchResult])
def search(q: str = ""):
    if not q.strip():
        return []
    return db.search(q)
