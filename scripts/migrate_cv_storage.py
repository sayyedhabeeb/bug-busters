import sys
import os
from sqlalchemy import text, inspect
from src.database.connection import DatabaseManager

def migrate():
    print("🚀 Starting Database Migration: Adding CV Storage Columns...")
    
    # Initialize DB
    DatabaseManager.initialize()
    engine = DatabaseManager._engine
    
    inspector = inspect(engine)
    existing_columns = [col['name'] for col in inspector.get_columns('candidates')]
    
    with engine.connect() as conn:
        try:
            print(f"Current columns in 'candidates': {existing_columns}")
            
            if 'cv_content' not in existing_columns:
                print("Adding 'cv_content' column...")
                conn.execute(text("ALTER TABLE candidates ADD COLUMN cv_content LONGBLOB"))
            
            if 'cv_filename' not in existing_columns:
                print("Adding 'cv_filename' column...")
                conn.execute(text("ALTER TABLE candidates ADD COLUMN cv_filename VARCHAR(255)"))
            
            if 'status' not in [col['name'] for col in inspector.get_columns('applications')]:
                print("Adding 'status' column to 'applications' table...")
                conn.execute(text("ALTER TABLE applications ADD COLUMN status VARCHAR(50) DEFAULT 'Applied'"))
            
            conn.commit()
            print("✅ Migration successful: Database is up to date.")
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")

if __name__ == "__main__":
    # Ensure src is in path
    sys.path.append(os.getcwd())
    migrate()
