import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

from src.core.config import settings

# Connection string for pyodbc
DATABASE_URL = os.environ.get("DATABASE_URL", "")
print(f"DEBUG: DATABASE_URL is '{DATABASE_URL}'")

if not DATABASE_URL:
    # Build MSSQL connection string only as a fallback
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
    DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={default_connection_string}"

# Create engine
if "sqlite" in DATABASE_URL.lower():
    print("DEBUG: Using SQLite engine")
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    print(f"DEBUG: Using non-SQLite engine (URL starts with {DATABASE_URL[:10]}...)")
    try:
        import pyodbc 
        engine = create_engine(DATABASE_URL)
    except ImportError:
        print("ERROR: pyodbc not found but DATABASE_URL is not SQLite. Falling back to dummy engine to prevent crash.")
        engine = create_engine("sqlite:///:memory:") 
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
        
        # Auto-migration: rename box_number to carton_number if it exists
        from sqlalchemy import inspect, text
        inspector = inspect(engine)
        if inspector.has_table('job_order_carton_slots'):
            columns = [c['name'] for c in inspector.get_columns('job_order_carton_slots')]
            if 'box_number' in columns and 'carton_number' not in columns:
                logger.info("Migrating database: renaming job_order_carton_slots.box_number to carton_number")
                with engine.connect() as conn:
                    if "sqlite" in str(engine.url).lower():
                        conn.execute(text("ALTER TABLE job_order_carton_slots RENAME COLUMN box_number TO carton_number"))
                    else:
                        conn.execute(text("EXEC sp_rename 'job_order_carton_slots.box_number', 'carton_number', 'COLUMN'"))
                    conn.commit()
                logger.info("Database migration completed successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize or migrate database tables: {e}")
