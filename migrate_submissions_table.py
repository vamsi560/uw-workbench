#!/usr/bin/env python3
"""
Database migration script to add missing columns to submissions table
"""

import sys
from sqlalchemy import create_engine, text, Column, DateTime, String
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from config import settings

def migrate_submissions_table():
    """Add missing columns to submissions table"""
    
    print("Starting database migration for submissions table...")
    
    # Create engine
    engine = create_engine(settings.database_url)
    
    # SQL commands to add missing columns
    migrations = [
        """
        ALTER TABLE submissions 
        ADD COLUMN IF NOT EXISTS received_at TIMESTAMP;
        """,
        """
        ALTER TABLE submissions 
        ADD COLUMN IF NOT EXISTS task_status VARCHAR(100) DEFAULT 'pending';
        """,
        """
        ALTER TABLE submissions 
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        """,
        """
        ALTER TABLE submissions 
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        """
    ]
    
    try:
        with engine.connect() as connection:
            # Start transaction
            trans = connection.begin()
            
            for i, migration_sql in enumerate(migrations, 1):
                print(f"Running migration {i}/4...")
                connection.execute(text(migration_sql))
                print(f"✅ Migration {i} completed")
            
            # Update existing records to have created_at if they don't
            print("Updating existing records with created_at timestamps...")
            update_sql = """
            UPDATE submissions 
            SET created_at = CURRENT_TIMESTAMP 
            WHERE created_at IS NULL;
            """
            connection.execute(text(update_sql))
            print("✅ Updated existing records")
            
            # Commit transaction
            trans.commit()
            print("✅ All migrations completed successfully!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        trans.rollback()
        return False
    
    return True

def verify_migrations():
    """Verify that all columns exist"""
    
    print("\nVerifying migrations...")
    
    engine = create_engine(settings.database_url)
    
    try:
        with engine.connect() as connection:
            # Check if columns exist
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'submissions' 
                AND column_name IN ('received_at', 'task_status', 'created_at', 'updated_at')
                ORDER BY column_name;
            """))
            
            columns = result.fetchall()
            
            expected_columns = ['created_at', 'received_at', 'task_status', 'updated_at']
            found_columns = [col[0] for col in columns]
            
            print("Found columns:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
            
            missing_columns = set(expected_columns) - set(found_columns)
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
                return False
            else:
                print("✅ All required columns are present!")
                return True
                
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Database Migration Tool")
    print("=" * 50)
    
    # Run migrations
    if migrate_submissions_table():
        # Verify migrations
        if verify_migrations():
            print("\n🎉 Database migration completed successfully!")
            print("Your API should now work without the 'received_at' error.")
            sys.exit(0)
        else:
            print("\n❌ Migration verification failed!")
            sys.exit(1)
    else:
        print("\n❌ Database migration failed!")
        sys.exit(1)