# migration_add_status_to_submissions.py
"""
Migration script to add 'status' column to 'submissions' table.
Run this script once to update your database schema.
"""

from sqlalchemy import create_engine, text
from config import settings

engine = create_engine(settings.database_url)

with engine.connect() as conn:
    # Add the status column if it doesn't exist
    conn.execute(text("""
        ALTER TABLE submissions ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'New';
    """))
    # Set status to 'New' for any existing rows where status is NULL
    conn.execute(text("""
        UPDATE submissions SET status = 'New' WHERE status IS NULL;
    """))
    print("Migration complete: 'status' column added to 'submissions' table.")
