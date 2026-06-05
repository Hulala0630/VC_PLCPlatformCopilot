from pathlib import Path
import sqlite3


BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
DATABASE_PATH = DATA_DIR / "plc_copilot.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_schema() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                industry TEXT,
                goal TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS project_intakes (
                project_id TEXT PRIMARY KEY,
                project_size TEXT,
                io_scale INTEGER,
                motion_requirement INTEGER,
                safety_requirement INTEGER,
                budget_sensitivity INTEGER,
                team_experience TEXT,
                existing_platform TEXT,
                candidate_platforms TEXT,
                constraints TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS platform_preferences (
                project_id TEXT NOT NULL,
                platform_id TEXT NOT NULL,
                preference_weight INTEGER NOT NULL,
                user_reason_note TEXT,
                PRIMARY KEY (project_id, platform_id),
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS project_attachments (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT,
                declared_purpose TEXT,
                uploaded_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS report_drafts (
                project_id TEXT PRIMARY KEY,
                version INTEGER NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS report_sections (
                project_id TEXT NOT NULL,
                id TEXT NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                assumptions TEXT,
                last_generated_at TEXT NOT NULL,
                PRIMARY KEY (project_id, id),
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );
            """
        )
