# Database Migration Guide

## Root Cause

The SQLAlchemy `Patient` model defines `created_at` and `updated_at` columns with `DateTime` types and default values. However, the existing SQLite `patients` table did not have these columns. 

`Base.metadata.create_all()` only creates tables that do not exist — it does **not** add new columns to existing tables. Therefore, after the initial deployment, adding new columns to the `Patient` model without a migration mechanism caused a schema mismatch:

```
sqlite3.OperationalError: no such column: patients.created_at
```

The SQLAlchemy query generated:
```sql
SELECT patients.id, ..., patients.created_at, patients.updated_at
FROM patients
WHERE patients.user_id = ?
ORDER BY patients.created_at DESC
```

But the actual SQLite table was missing the `created_at` column.

## Missing Database Columns

The following columns were missing from the `patients` table in the existing SQLite database:

- `created_at` (DATETIME)
- `updated_at` (DATETIME) — already existed in some databases, but migration ensures it's present

## Database File Used

- `endoscopy.db` (located in the backend root directory)
- Path: `sqlite:///./endoscopy.db`

## Migration Implementation

The `_migrate_schema()` function in `app/database.py:138` provides an idempotent schema migration mechanism:

1. **Inspects existing tables** using SQLAlchemy `inspect(engine)`
2. **Detects missing columns** by comparing the migration definition against `PRAGMA table_info`
3. **Adds missing columns** via `ALTER TABLE ... ADD COLUMN`
4. **Populates existing rows** with `datetime('now')` for NULL timestamps

The migration is safe to run multiple times (idempotent) — it checks if a column exists before adding it, and running it repeatedly produces no errors.

### Migration Definition for `patients` table

```python
"patients": [
    ("user_id", "INTEGER"),
    ("patient_ref", "VARCHAR"),
    ("full_name", "VARCHAR"),
    ("sex", "VARCHAR"),
    ("medical_history", "TEXT"),
    ("allergies", "TEXT"),
    ("medications", "TEXT"),
    ("previous_endoscopy", "TEXT"),
    ("family_history", "TEXT"),
    ("created_at", "DATETIME"),
    ("updated_at", "DATETIME"),
],
```

### Row Timestamp Population

After adding missing columns, the migration updates existing rows where timestamps are NULL:

```sql
UPDATE patients SET created_at = datetime('now') WHERE created_at IS NULL;
UPDATE patients SET updated_at = datetime('now') WHERE updated_at IS NULL;
```

## Verifying the Database

After the fix, the `patients` table should have all columns matching the SQLAlchemy model:

```
id, patient_ref, user_id, full_name, age, sex, medical_history,
allergies, medications, previous_endoscopy, family_history,
created_at, updated_at
```

Run the backend to verify:

```bash
cd /d F:\Multimodel\backend
"C:\Users\Shakthipriya\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn app.main:app --reload --port 8000
```

Expected output includes:
```
[DB Migration] Adding missing column 'created_at' (DATETIME) to table 'patients'...
[DB Migration] Added missing column 'created_at' (DATETIME) to table 'patients'...
[DB Migration] Schema already up to date.
✅ Database tables initialized and schema migration verified.
```

## Running the Backend

1. Start the backend: `cd /d F:\Multimodel\backend && uvicorn app.main:app --reload --port 8000`
2. The `startup_event()` calls `init_db()` which runs `create_all()` then `_migrate_schema()`
3. Migration adds any missing columns before patient queries are processed
4. AI components (Kvasir classifier, RAG, Agentic AI) load after database initialization

## Idempotency

Running the backend multiple times will NOT produce "duplicate column errors". The migration checks `if col_name not in existing_cols` before adding each column, making it safe for repeated execution.

## Existing Data Preservation

- The migration only adds missing columns — it never drops or modifies existing data
- Existing patient records are preserved with their original data
- NULL timestamps are populated with `datetime('now')` without affecting non-NULL values
- The original `.db` file is never deleted or recreated