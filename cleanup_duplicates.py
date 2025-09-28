"""
Clean up duplicate entries in the database
"""

from database import SessionLocal, Submission, WorkItem
from datetime import datetime

def cleanup_duplicates():
    """Remove duplicate submissions and work items"""
    print("🧹 Cleaning up duplicate database entries")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Get all MedTech Solutions submissions
        medtech_submissions = db.query(Submission).filter(
            Submission.subject.like('%MedTech Solutions%')
        ).order_by(Submission.created_at.asc()).all()
        
        print(f"Found {len(medtech_submissions)} MedTech Solutions submissions")
        
        if len(medtech_submissions) > 1:
            # Keep the first one, delete the rest
            to_keep = medtech_submissions[0]
            to_delete = medtech_submissions[1:]
            
            print(f"Keeping submission ID {to_keep.id} (ref: {to_keep.submission_ref})")
            print(f"Deleting {len(to_delete)} duplicate submissions...")
            
            for sub in to_delete:
                # Delete associated work item first
                work_item = db.query(WorkItem).filter(WorkItem.submission_id == sub.id).first()
                if work_item:
                    print(f"  Deleting work item ID {work_item.id}")
                    db.delete(work_item)
                
                print(f"  Deleting submission ID {sub.id}")
                db.delete(sub)
            
            db.commit()
            print("✅ Duplicates cleaned up successfully")
        else:
            print("ℹ️  No duplicates found")
        
        # Final count
        submissions_count = db.query(Submission).count()
        work_items_count = db.query(WorkItem).count()
        
        print(f"\n📊 Final counts:")
        print(f"  Submissions: {submissions_count}")
        print(f"  Work Items: {work_items_count}")
        
    except Exception as e:
        print(f"❌ Error cleaning up: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_duplicates()