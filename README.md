# Codebase Explorer

Инструмент, который анализирует исходные файлы Python, сохраняет их структуру (классы, функции, аргументы, строки документации) в SQLite и предоставляет доступ к данным через REST API.

---

## Схема базы данных

```
files
  id          INTEGER  PRIMARY KEY
  path        TEXT     NOT NULL UNIQUE   -- полный или относительный путь до файла
  name        TEXT     NOT NULL          -- название файла (пр: "parser.py")

classes
  id          INTEGER  PRIMARY KEY
  file_id     INTEGER  REFERENCES files(id)
  name        TEXT     NOT NULL
  line_start  INTEGER
  line_end    INTEGER
  doc         TEXT                       -- документация, NULL если отсутствует
  fields      BLOB                       -- закодированные пары "name:type"

  UNIQUE (file_id, name)

functions
  id          INTEGER  PRIMARY KEY
  file_id     INTEGER  REFERENCES files(id)
  class_id    INTEGER  REFERENCES classes(id)  -- NULL для функций, которые не связаны с классом
  name        TEXT     NOT NULL
  line_start  INTEGER
  line_end    INTEGER
  doc         TEXT                       -- документация, NULL если отсутствует
  args        BLOB                       -- закодированные пары "name:type"
  return_type TEXT                       -- NULL если не указан явно
  is_async    BOOLEAN  DEFAULT 0

  UNIQUE (file_id, name, class_id)
```

В столбцах `args` и `fields` используется компактная текстовая кодировка: каждая переменная представляет собой
`name` или `name:type`, соединенные запятыми.
Пример: `self,path:str,limit:int | None`.

---

## Как запускать?

### Локально

```bash
# 1. Установка зависемостей
pip install -r requirements.txt

# 2. Индексация исходных файлов (запустите один раз или повторно для обновления).
python parser.py /path/to/your/python/project

# 3. Запуск API
uvicorn main:app
```

API будет доступно по `http://127.0.0.1:8000` (вернет 404 Not Found).  
Документация: `http://127.0.0.1:8000/docs`

### Docker

```bash
# Сборка изображения
docker build -t codebase-explorer .

# Индексация исходных файлов (запустите один раз или повторно для обновления).
python parser.py /path/to/your/python/project

# Запуск контейнера
docker run -p 8000:8000 -v "$(pwd)/data:/app/data" codebase-explorer
```

---

## Примеры запросов

### 1. Посмотреть все файлы

```
GET /api/files
```

```json
[
  { "path": "core/parsers/file_parser.py", "name": "file_parser.py", "function_count": 3, "class_count": 0 },
  { "path": "database/read_database.py",   "name": "read_database.py", "function_count": 6, "class_count": 1 }
]
```

### 2. Получить полную структуру файла

```
GET /api/files/read_database.py/structure
```

```json
{
  "classes": [
    {
      "name": "ReadDatabase",
      "line_start": 10,
      "line_end": 90,
      "doc": "Read-only database interface.",
      "fields": [],
      "constructors": [],
      "methods": []
    }
  ],
  "functions": []
}
```

### 3. Поиск по слову (название или документация)

```
GET /api/search?q=parse
```

```json
[
  { "kind": "function", "value": { "name": "parse_file", "doc": null, "line_start": 12, "line_end": 28, "file_path": "core/parsers/file_parser.py", "class_name": null } },
  { "kind": "function", "value": { "name": "parse_class", "doc": null, "line_start": 8, "line_end": 30, "file_path": "core/parsers/class_parser.py", "class_name": null } }
]
```

### 4. Поиск с фильтром по типу сущности

```
GET /api/search?q=database&type=class
```

```json
[
  { "kind": "class", "value": { "name": "ReadDatabase",  "doc": null, "line_start": 10, "line_end": 90, "file_path": "database/read_database.py" } },
  { "kind": "class", "value": { "name": "WriteDatabase", "doc": null, "line_start": 10, "line_end": 85, "file_path": "database/write_database.py" } }
]
```

### 5. Статистика

```
GET /api/stats
```

```json
{ "file_count": 12, "class_count": 8, "function_count": 47 }
```

### 6. Пагинация

```
GET /api/files?limit=5&offset=0
GET /api/search?q=parse&limit=3&offset=6
```