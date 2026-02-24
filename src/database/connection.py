"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
import logging
from config.config_production import get_config

logger = logging.getLogger(__name__)

config = get_config()


class DatabaseManager:
    """Manage database connections and sessions."""
    
    _engine = None
    _SessionLocal = None
    
    @classmethod
    def initialize(cls):
        """Initialize database engine and session factory."""
        try:
            cls._engine = create_engine(
                config.DATABASE_URL,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True
            )
            cls._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=cls._engine
            )
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise
    
    @classmethod
    def get_session(cls) -> Session:
        """Get a database session."""
        if cls._SessionLocal is None:
            cls.initialize()
        return cls._SessionLocal()
    
    @classmethod
    def create_tables(cls):
        """Create all tables."""
        if cls._engine is None:
            cls.initialize()
        
        from src.database.models import Base
        Base.metadata.create_all(bind=cls._engine)
        logger.info("All tables created successfully")
    
    @classmethod
    def close(cls):
        """Close all connections."""
        if cls._engine:
            cls._engine.dispose()
            logger.info("Database connections closed")


# Create global session dependency
def get_db() -> Session:
    """Dependency for getting database session."""
    db = DatabaseManager.get_session()
    try:
        yield db
    finally:
        db.close()
