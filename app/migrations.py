from __future__ import annotations

from sqlalchemy import Engine, inspect, text


def _add_column(engine: Engine, table: str, column: str, sql_type: str) -> None:
    columns = {item["name"] for item in inspect(engine).get_columns(table)}
    if column not in columns:
        with engine.begin() as connection:
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"))


def migrate_legacy_schema(engine: Engine) -> None:
    """Idempotent additive SQLite migration; never drops or rewrites user data."""
    tables = set(inspect(engine).get_table_names())
    if "students" in tables:
        for column, sql_type in (
            ("user_id", "INTEGER"),
            ("display_name", "VARCHAR(100) NOT NULL DEFAULT ''"),
            ("grade_level", "INTEGER NOT NULL DEFAULT 8"),
            ("curriculum_id", "INTEGER"),
            ("learning_level", "VARCHAR(20) NOT NULL DEFAULT 'standard'"),
            ("timezone", "VARCHAR(80) NOT NULL DEFAULT 'America/New_York'"),
            ("preferred_unit_system", "VARCHAR(20) NOT NULL DEFAULT 'metric'"),
            ("onboarding_completed", "BOOLEAN NOT NULL DEFAULT 0"),
            ("created_at", "DATETIME"),
            ("updated_at", "DATETIME"),
        ):
            _add_column(engine, "students", column, sql_type)
    if "lessons" in tables:
        for column, sql_type in (
            ("concept_key", "VARCHAR(140) NOT NULL DEFAULT ''"),
            ("course_id", "INTEGER"),
            ("publication_status", "VARCHAR(30) NOT NULL DEFAULT 'published'"),
        ):
            _add_column(engine, "lessons", column, sql_type)
    if "tutor_sessions" in tables:
        _add_column(engine, "tutor_sessions", "tutor_id", "INTEGER")
