from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Global database connection
SQLALCHEMY_DATABASE_URL = f"{settings.database_url}/{settings.database_name}"
global_engine = create_engine(SQLALCHEMY_DATABASE_URL)
GlobalSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=global_engine)

# Base model for all database models
GlobalBase = declarative_base() # Schema used for tables in global database
EventBase = declarative_base()  # Schema used for tables in event database
