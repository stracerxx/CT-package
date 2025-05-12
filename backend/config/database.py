from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database connection settings
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ct5_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# Log database connection info (without password)
logger.info(f"Connecting to database at {DB_HOST}:{DB_PORT}/{DB_NAME} with user {DB_USER}")

# Create SQLAlchemy engine
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# For development/testing, can use SQLite
# SQLALCHEMY_DATABASE_URL = "sqlite:///./ct5.db"

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    # Test connection
    with engine.connect() as conn:
        logger.info("Successfully connected to the database")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

except Exception as e:
    logger.error(f"Failed to connect to the database: {e}")
    # Still define these to avoid import errors, but they won't work
    SessionLocal = None
    Base = declarative_base()

# Dependency to get DB session
def get_db():
    if SessionLocal is None:
        logger.error("Database session is not available")
        raise Exception("Database connection failed. Check your database configuration.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
