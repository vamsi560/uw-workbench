#!/usr/bin/env python3
"""
Add attachment_content column to existing submissions table
"""

from database import SessionLocal, engine
from sqlalchemy import text

def add_attachment_content_column():
    """Add attachment_content column to submissions table"""
    print("Adding attachment_content column to submissions table...")
    
    db = SessionLocal()
    try:
        # Check if column already exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'submissions' 
            AND column_name = 'attachment_content'
        """))
        
        column_exists = result.fetchone() is not None
        
        if column_exists:
            print("✅ attachment_content column already exists")
            return True
        
        # Add the column
        db.execute(text("""
            ALTER TABLE submissions 
            ADD COLUMN attachment_content TEXT
        """))
        
        db.commit()
        print("✅ attachment_content column added successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error adding column: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = add_attachment_content_column()
    if success:
        print("🎉 Database migration completed successfully!")
    else:
        print("❌ Database migration failed!")