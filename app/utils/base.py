from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app import db
import os


def get_engine():
    """Create and return a database engine."""
    database_url = os.getenv('DATABASE_URL', 'sqlite:///attendance.db')
    engine = create_engine(
        database_url,
        pool_recycle=300,
        pool_pre_ping=True,
        echo=os.getenv('SQLALCHEMY_ECHO', 'false').lower() == 'true'
    )
    return engine


def get_session():
    """Create and return a database session."""
    engine = get_engine()
    Session = scoped_session(sessionmaker(bind=engine))
    return Session()


def init_db():
    """Initialize the database by creating all tables."""
    from app import create_app
    app = create_app()
    with app.app_context():
        db.create_all()
