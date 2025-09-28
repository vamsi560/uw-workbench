"""
Database Investigation Script
Check for duplicate entries and inconsistencies
"""

from database import SessionLocal, Submission, WorkItem
from datetime import datetime

def investigate_database():
    print("🔍 Investigating Database State")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Count totals
        submissions_count = db.query(Submission).count()
        work_items_count = db.query(WorkItem).count()
        
        print(f"📊 Database Counts:")
        print(f"  Submissions: {submissions_count}")
        print(f"  Work Items: {work_items_count}")
        
        # Check for duplicates by subject/email
        print(f"\n🔍 Checking for Duplicate Submissions:")
        submissions = db.query(Submission).all()
        subject_counts = {}
        email_counts = {}
        
        for sub in submissions:
            subject = sub.subject or "No Subject"
            email = sub.sender_email or "No Email"
            
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
            email_counts[email] = email_counts.get(email, 0) + 1
        
        # Show duplicates
        duplicate_subjects = {k: v for k, v in subject_counts.items() if v > 1}
        duplicate_emails = {k: v for k, v in email_counts.items() if v > 1}
        
        if duplicate_subjects:
            print("  Duplicate Subjects:")
            for subject, count in duplicate_subjects.items():
                print(f"    '{subject[:50]}...' appears {count} times")
        
        if duplicate_emails:
            print("  Duplicate Emails:")
            for email, count in duplicate_emails.items():
                print(f"    '{email}' appears {count} times")
        
        # Check work items without submissions
        print(f"\n🔗 Checking Work Item Links:")
        orphaned_work_items = db.query(WorkItem).filter(
            ~WorkItem.submission_id.in_(db.query(Submission.id))
        ).count()
        
        print(f"  Orphaned Work Items (no matching submission): {orphaned_work_items}")
        
        # Check submissions without work items
        submissions_without_work_items = db.query(Submission).filter(
            ~Submission.id.in_(db.query(WorkItem.submission_id))
        ).count()
        
        print(f"  Submissions Without Work Items: {submissions_without_work_items}")
        
        # Show recent entries
        print(f"\n📝 Recent Submissions (last 5):")
        recent_subs = db.query(Submission).order_by(Submission.created_at.desc()).limit(5).all()
        for sub in recent_subs:
            print(f"  ID: {sub.id}, Ref: {sub.submission_ref}")
            print(f"      Subject: {(sub.subject or 'No subject')[:60]}...")
            print(f"      Email: {sub.sender_email or 'No email'}")
            print(f"      Created: {sub.created_at}")
            print()
        
        print(f"🔧 Recent Work Items (last 5):")
        recent_work = db.query(WorkItem).order_by(WorkItem.created_at.desc()).limit(5).all()
        for work in recent_work:
            print(f"  ID: {work.id}, Submission ID: {work.submission_id}")
            print(f"      Title: {(work.title or 'No title')[:60]}...")
            print(f"      Status: {work.status}, Priority: {work.priority}")
            print(f"      Created: {work.created_at}")
            print()
        
        # Check for specific issues
        print(f"🚨 Potential Issues:")
        
        # Multiple work items per submission
        submission_work_item_counts = db.execute("""
            SELECT submission_id, COUNT(*) as work_item_count 
            FROM work_items 
            GROUP BY submission_id 
            HAVING COUNT(*) > 1
        """).fetchall()
        
        if submission_work_item_counts:
            print("  Multiple Work Items per Submission:")
            for row in submission_work_item_counts:
                print(f"    Submission {row[0]} has {row[1]} work items")
        else:
            print("  ✅ No multiple work items per submission found")
        
    finally:
        db.close()

if __name__ == "__main__":
    investigate_database()