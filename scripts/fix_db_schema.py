import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.append(project_root)

from sqlalchemy import create_engine, text
from config.config_production import get_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_fix")

def add_column_if_not_exists(connection, table, column, definition):
    result = connection.execute(text(f"SHOW COLUMNS FROM {table} LIKE '{column}'"))
    if not result.fetchone():
        logger.info(f"Adding {column} to {table}...")
        try:
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
            connection.commit()
            logger.info(f"Successfully added {column} to {table}.")
        except Exception as e:
            logger.error(f"Failed to add {column} to {table}: {e}")
            connection.rollback()
    else:
        logger.debug(f"Column {column} already exists in {table}.")

def fix_schema():
    config = get_config()
    engine = create_engine(config.DATABASE_URL)
    
    with engine.connect() as connection:
        # Tables to fix
        
        # 1. Jobs Table
        add_column_if_not_exists(connection, "jobs", "company_id", "INT")
        add_column_if_not_exists(connection, "jobs", "experience_required", "INT DEFAULT 0")
        add_column_if_not_exists(connection, "jobs", "location", "VARCHAR(255) DEFAULT 'Remote'")
        add_column_if_not_exists(connection, "jobs", "salary_range", "VARCHAR(255) DEFAULT 'N/A'")
        add_column_if_not_exists(connection, "jobs", "job_type", "VARCHAR(255) DEFAULT 'Full-time'")
        
        # Add foreign key for jobs.company_id if not exists
        try:
            # Check if FK exists
            fk_check = connection.execute(text("""
                SELECT CONSTRAINT_NAME 
                FROM information_schema.KEY_COLUMN_USAGE 
                WHERE TABLE_NAME = 'jobs' AND COLUMN_NAME = 'company_id' 
                AND REFERENCED_TABLE_NAME = 'companies'
            """)).fetchone()
            
            if not fk_check:
                logger.info("Adding FK for jobs.company_id...")
                connection.execute(text("ALTER TABLE jobs ADD CONSTRAINT fk_jobs_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE"))
                connection.commit()
        except Exception as e:
            logger.warning(f"Note: Could not add FK for jobs.company_id (might already exist or column missing): {e}")

        # 2. Candidates Table
        add_column_if_not_exists(connection, "candidates", "user_id", "INT")
        add_column_if_not_exists(connection, "candidates", "resume_path", "VARCHAR(255)")
        add_column_if_not_exists(connection, "candidates", "preferred_role", "VARCHAR(255)")
        
        # FIX NULLABILITY for existing columns
        logger.info("Setting columns to nullable where appropriate...")
        try:
            connection.execute(text("ALTER TABLE candidates MODIFY COLUMN resume_text LONGTEXT NULL"))
            connection.execute(text("ALTER TABLE candidates MODIFY COLUMN skills LONGTEXT NULL"))
            connection.execute(text("ALTER TABLE candidates MODIFY COLUMN experience_years INT NULL"))
            connection.execute(text("ALTER TABLE jobs MODIFY COLUMN description LONGTEXT NULL"))
            connection.commit()
            logger.info("Successfully updated column nullability.")
        except Exception as e:
            logger.warning(f"Note: Could not fix nullability (might already be correct): {e}")
            connection.rollback()
        try:
            fk_check = connection.execute(text("""
                SELECT CONSTRAINT_NAME 
                FROM information_schema.KEY_COLUMN_USAGE 
                WHERE TABLE_NAME = 'candidates' AND COLUMN_NAME = 'user_id' 
                AND REFERENCED_TABLE_NAME = 'users'
            """)).fetchone()
            
            if not fk_check:
                logger.info("Adding FK for candidates.user_id...")
                connection.execute(text("ALTER TABLE candidates ADD CONSTRAINT fk_candidates_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"))
                connection.commit()
        except Exception as e:
            logger.warning(f"Note: Could not add FK for candidates.user_id: {e}")

if __name__ == "__main__":
    fix_schema()
