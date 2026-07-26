from sqlalchemy import create_engine, inspect, text

from app.migrations import migrate_legacy_schema


def test_legacy_schema_migration_is_additive_and_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'legacy.db'}")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE students (id INTEGER PRIMARY KEY, name VARCHAR(100), email VARCHAR(255), grade INTEGER)"))
        connection.execute(text("INSERT INTO students (id, name, email, grade) VALUES (42, 'Legacy Learner', 'legacy@example.test', 8)"))
        connection.execute(text("CREATE TABLE lessons (id INTEGER PRIMARY KEY, slug VARCHAR(120), title VARCHAR(180), unit VARCHAR(120), order_index INTEGER, summary TEXT, duration_minutes INTEGER)"))
        connection.execute(text("CREATE TABLE tutor_sessions (id INTEGER PRIMARY KEY, student_id INTEGER, topic VARCHAR(200), starts_at DATETIME, price_usd FLOAT, payment_status VARCHAR(30), meeting_url VARCHAR(500), status VARCHAR(30), created_at DATETIME)"))
    migrate_legacy_schema(engine)
    migrate_legacy_schema(engine)
    inspector = inspect(engine)
    student_columns = {column["name"] for column in inspector.get_columns("students")}
    lesson_columns = {column["name"] for column in inspector.get_columns("lessons")}
    tutor_columns = {column["name"] for column in inspector.get_columns("tutor_sessions")}
    assert {"user_id", "display_name", "grade_level", "curriculum_id", "learning_level", "onboarding_completed"} <= student_columns
    assert {"concept_key", "course_id", "publication_status"} <= lesson_columns
    assert "tutor_id" in tutor_columns
    with engine.connect() as connection:
        row = connection.execute(text("SELECT id, name, email, grade FROM students WHERE id = 42")).one()
    assert tuple(row) == (42, "Legacy Learner", "legacy@example.test", 8)
