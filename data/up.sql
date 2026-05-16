-- FILES --------------------------------------------------------------
CREATE TABLE IF NOT EXISTS files
(
    id   INTEGER PRIMARY KEY,
    path TEXT NOT NULL,
    name TEXT NOT NULL,

    CONSTRAINT uc_file_path UNIQUE (path)
);

CREATE INDEX IF NOT EXISTS idx_file_name ON files (name);

-- CLASSES --------------------------------------------------------------
CREATE TABLE IF NOT EXISTS classes
(
    id         INTEGER PRIMARY KEY,
    file_id    INTEGER NOT NULL,
    name       TEXT    NOT NULL,
    line_start INTEGER NOT NULL DEFAULT 0,
    line_end   INTEGER NOT NULL DEFAULT 0,
    doc        TEXT,
    fields     BLOB,

    CONSTRAINT uc_class_file UNIQUE (file_id, name),
    CONSTRAINT fk_class_file FOREIGN KEY (file_id) REFERENCES files (id)
);

CREATE INDEX IF NOT EXISTS idx_class_name ON classes (name);

-- FUNCTIONS --------------------------------------------------------------
CREATE TABLE IF NOT EXISTS functions
(
    id          INTEGER PRIMARY KEY,
    file_id     INTEGER NOT NULL,
    name        TEXT    NOT NULL,
    line_start  INTEGER NOT NULL DEFAULT 0,
    line_end    INTEGER NOT NULL DEFAULT 0,
    doc         TEXT,
    args        BLOB,
    return_type TEXT,
    is_async    BOOLEAN NOT NULL DEFAULT 0,
    class_id    INTEGER,

    CONSTRAINT uc_function_file UNIQUE (file_id, name, class_id),
    CONSTRAINT fk_function_file  FOREIGN KEY (file_id)  REFERENCES files (id),
    CONSTRAINT fk_function_class FOREIGN KEY (class_id) REFERENCES classes (id)
);

CREATE INDEX IF NOT EXISTS idx_function_name ON functions (name);
