"""
Database Migration Script for Cyber Insurance Enhancements
This script safely migrates existing submission data to the new enhanced work item structure.
"""

import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import Base, Submission, WorkItem, WorkItemStatus, WorkItemPriority
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """
    Main migration function to upgrade database schema and migrate data
    """
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    logger.info("Starting database migration...")
    
    # Create new tables
    logger.info("Creating new database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ New tables created successfully")
    
    # Migrate existing data
    db = SessionLocal()
    try:
        # Get all submissions that don't have corresponding work items
        submissions_without_workitems = db.query(Submission).filter(
            ~Submission.id.in_(
                db.query(WorkItem.submission_id)
            )
        ).all()
        
        logger.info(f"Found {len(submissions_without_workitems)} submissions to migrate")
        
        migrated_count = 0
        for submission in submissions_without_workitems:
            # Create a work item for each submission
            work_item = WorkItem(
                submission_id=submission.id,
                title=submission.subject or "Imported Submission",
                description=f"Email from {submission.sender_email}",
                assigned_to=submission.assigned_to,
                status=map_legacy_status(submission.task_status),
                priority=WorkItemPriority.MEDIUM,  # Default priority
                created_at=submission.created_at,
                updated_at=submission.created_at
            )
            
            # Try to extract industry and other details from extracted_fields
            if submission.extracted_fields:
                extracted = submission.extracted_fields
                if isinstance(extracted, dict):
                    work_item.industry = extracted.get('industry')
                    work_item.policy_type = extracted.get('policy_type')
                    
                    # Try to parse coverage amount
                    coverage = extracted.get('coverage_amount')
                    if coverage:
                        try:
                            # Remove $ and commas, convert to float
                            if isinstance(coverage, str):
                                coverage_clean = coverage.replace('$', '').replace(',', '')
                                work_item.coverage_amount = float(coverage_clean)
                        except (ValueError, TypeError):
                            pass
            
            db.add(work_item)
            migrated_count += 1
        
        db.commit()
        logger.info(f"✅ Successfully migrated {migrated_count} work items")
        
        # Add database indexes for performance
        logger.info("Creating database indexes...")
        create_indexes(engine)
        logger.info("✅ Database indexes created")
        
        logger.info("🎉 Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def map_legacy_status(legacy_status: str) -> WorkItemStatus:
    """Map legacy submission status to new work item status"""
    if not legacy_status:
        return WorkItemStatus.PENDING
    
    status_mapping = {
        'pending': WorkItemStatus.PENDING,
        'in_progress': WorkItemStatus.IN_REVIEW,
        'completed': WorkItemStatus.APPROVED,
        'rejected': WorkItemStatus.REJECTED
    }
    
    return status_mapping.get(legacy_status.lower(), WorkItemStatus.PENDING)


def create_indexes(engine):
    """Create database indexes for performance"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_work_items_status ON work_items(status);",
        "CREATE INDEX IF NOT EXISTS idx_work_items_priority ON work_items(priority);",
        "CREATE INDEX IF NOT EXISTS idx_work_items_assigned_to ON work_items(assigned_to);",
        "CREATE INDEX IF NOT EXISTS idx_work_items_created_at ON work_items(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_work_items_industry ON work_items(industry);",
        "CREATE INDEX IF NOT EXISTS idx_comments_work_item_id ON comments(work_item_id);",
        "CREATE INDEX IF NOT EXISTS idx_risk_assessments_work_item_id ON risk_assessments(work_item_id);",
        "CREATE INDEX IF NOT EXISTS idx_work_item_history_work_item_id ON work_item_history(work_item_id);",
        "CREATE INDEX IF NOT EXISTS idx_work_item_history_timestamp ON work_item_history(timestamp);"
    ]
    
    with engine.connect() as conn:
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                logger.info(f"Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
            except Exception as e:
                logger.warning(f"Index creation warning: {str(e)}")


def add_sample_users():
    """Add sample users for testing"""
    from database import User, UserRole
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            logger.info("Users already exist, skipping sample user creation")
            return
        
        sample_users = [
            User(
                id="underwriter1",
                name="Alice Johnson",
                email="alice.johnson@company.com",
                role=UserRole.UNDERWRITER,
                specializations=["Healthcare", "Technology"],
                max_capacity=20,
                current_workload=5,
                is_available=True,
                success_rate=92.5
            ),
            User(
                id="underwriter2",
                name="Bob Smith",
                email="bob.smith@company.com",
                role=UserRole.UNDERWRITER,
                specializations=["Financial Services", "Manufacturing"],
                max_capacity=25,
                current_workload=8,
                is_available=True,
                success_rate=88.3
            ),
            User(
                id="senior_uw1",
                name="Carol Davis",
                email="carol.davis@company.com",
                role=UserRole.SENIOR_UNDERWRITER,
                specializations=["Healthcare", "Financial Services", "Technology"],
                max_capacity=30,
                current_workload=12,
                is_available=True,
                success_rate=95.1
            ),
            User(
                id="risk_analyst1",
                name="David Wilson",
                email="david.wilson@company.com",
                role=UserRole.RISK_ANALYST,
                specializations=["Risk Assessment", "Compliance"],
                max_capacity=15,
                current_workload=3,
                is_available=True,
                success_rate=89.7
            )
        ]
        
        for user in sample_users:
            db.add(user)
        
        db.commit()
        logger.info(f"✅ Added {len(sample_users)} sample users")
        
    except Exception as e:
        logger.error(f"❌ Failed to add sample users: {str(e)}")
        db.rollback()
    finally:
        db.close()


def verify_migration():
    """Verify that migration was successful"""
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Count records
        submission_count = db.query(Submission).count()
        work_item_count = db.query(WorkItem).count()
        
        logger.info(f"Verification Results:")
        logger.info(f"  - Submissions: {submission_count}")
        logger.info(f"  - Work Items: {work_item_count}")
        
        if work_item_count > 0:
            logger.info("✅ Migration verification passed")
            return True
        else:
            logger.warning("⚠️  No work items found after migration")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration verification failed: {str(e)}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    try:
        # Run the main migration
        run_migration()
        
        # Add sample users for testing
        add_sample_users()
        
        # Verify migration success
        if verify_migration():
            print("\n🎉 Database migration completed successfully!")
            print("\nNext steps:")
            print("1. Update your frontend to use the new polling endpoint")
            print("2. Test the enhanced filtering and search capabilities")
            print("3. Start implementing the risk assessment features")
        else:
            print("\n❌ Migration verification failed. Please check the logs.")
            
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        print("Please check the error logs and try again.")