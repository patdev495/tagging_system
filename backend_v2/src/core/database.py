import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

from src.core.config import settings

# Connection string for pyodbc
if settings.DB_USER:
    auth_str = f"UID={settings.DB_USER};PWD={settings.DB_PASS};"
else:
    auth_str = "Trusted_Connection=yes;"

default_connection_string = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={settings.DB_SERVER};"
    f"DATABASE={settings.DB_NAME};"
    f"{auth_str}"
    "Encrypt=no;"
    "TrustServerCertificate=yes;"
)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={default_connection_string}"

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    import logging
    logger = logging.getLogger("Database")
    try:
        from src.core import models
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully (if not existed).")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
