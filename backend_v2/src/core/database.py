import os
import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

from src.core.config import settings

logger = logging.getLogger("Database")

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
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=1800,
            pool_size=10,
            max_overflow=20,
            fast_executemany=True,
        )
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

def seed_a11_data(db):
    """Seed Customer A11 and 3 initial products if not already present."""
    from src.core import models
    try:
        a11_customer = db.query(models.Customer).filter(models.Customer.code == "A11").first()
        if not a11_customer:
            # Check if UX exists and migrate inline
            ux_customer = db.query(models.Customer).filter(models.Customer.code == "UX").first()
            if ux_customer:
                ux_customer.code = "A11"
                ux_customer.name = "Customer A11"
                a11_customer = ux_customer
                db.flush()
                logger.info("Migrated Customer UX to Customer A11")
            else:
                a11_customer = models.Customer(code="A11", name="Customer A11")
                db.add(a11_customer)
                db.flush()
                logger.info("Seeded Customer A11")

        a11_products = [
            ("840-00083", 190, "VHK0010237", "NYS5998", "a11", r"D:\PAT\Templates\a11.btw", "weight_scale", "B", "kg", 12.500, 12.300, 12.700),
            ("840-00091", 190, "VHK0010237", "NYS5998", "a11", r"D:\PAT\Templates\a11.btw", "weight_scale", "B", "kg", 12.500, 12.300, 12.700),
            ("840-00092", 190, "VHK0010237", "NYS5998", "a11", r"D:\PAT\Templates\a11.btw", "weight_scale", "B", "kg", 12.500, 12.300, 12.700),
        ]

        for item_name, qty, prefix, mfr_pn, tmpl, tmpl_path, mode, rev, unit, target_w, min_w, max_w in a11_products:
            prod = db.query(models.Product).filter(
                models.Product.customer_id == a11_customer.id,
                models.Product.item_name == item_name
            ).first()
            if not prod:
                prod = models.Product(
                    customer_id=a11_customer.id,
                    item_name=item_name,
                    packed_qty=qty,
                    pkg_prefix=prefix,
                    mfr_pn=mfr_pn,
                    template_type=tmpl,
                    template_path=tmpl_path,
                    packing_mode=mode,
                    revision=rev,
                    weight_unit=unit,
                    target_weight=target_w,
                    min_weight=min_w,
                    max_weight=max_w,
                )
                db.add(prod)
                logger.info(f"Seeded A11 Product: {item_name}")

        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning(f"Seed A11 data notice: {e}")

seed_ux_data = seed_a11_data

def init_db():
    try:
        from src.core import models
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully (if not existed).")
        
        # Lightweight migrations for existing installations.
        inspector = inspect(engine)
        is_sqlite = "sqlite" in str(engine.url).lower()

        with engine.connect() as conn:
            # 1. Migrate job_order_carton_slots
            if inspector.has_table('job_order_carton_slots'):
                slot_cols = [c['name'] for c in inspector.get_columns('job_order_carton_slots')]
                if 'box_number' in slot_cols and 'carton_number' not in slot_cols:
                    logger.info("Migrating: renaming job_order_carton_slots.box_number to carton_number")
                    if is_sqlite:
                        conn.execute(text("ALTER TABLE job_order_carton_slots RENAME COLUMN box_number TO carton_number"))
                    else:
                        conn.execute(text("EXEC sp_rename 'job_order_carton_slots.box_number', 'carton_number', 'COLUMN'"))
                    conn.commit()

                if 'shipped' not in slot_cols:
                    logger.info("Migrating: adding job_order_carton_slots.shipped")
                    if is_sqlite:
                        conn.execute(text("ALTER TABLE job_order_carton_slots ADD COLUMN shipped INTEGER NOT NULL DEFAULT 0"))
                    else:
                        conn.execute(text("ALTER TABLE job_order_carton_slots ADD shipped INT NOT NULL CONSTRAINT DF_job_order_carton_slots_shipped DEFAULT 0 WITH VALUES"))
                    conn.commit()

            # 2. Migrate products table for A11 / UX & weight_scale columns
            if inspector.has_table('products'):
                prod_cols = [c['name'] for c in inspector.get_columns('products')]
                new_prod_cols = [
                    ('packing_mode', 'VARCHAR(50) DEFAULT \'item_scan\'', 'VARCHAR(50) DEFAULT \'item_scan\''),
                    ('target_weight', 'FLOAT NULL', 'FLOAT NULL'),
                    ('min_weight', 'FLOAT NULL', 'FLOAT NULL'),
                    ('max_weight', 'FLOAT NULL', 'FLOAT NULL'),
                    ('weight_unit', 'VARCHAR(10) DEFAULT \'kg\'', 'VARCHAR(10) DEFAULT \'kg\''),
                    ('mfr_pn', 'VARCHAR(50) NULL', 'VARCHAR(50) NULL'),
                    ('pkg_prefix', 'VARCHAR(20) NULL', 'VARCHAR(20) NULL'),
                    ('revision', 'VARCHAR(10) DEFAULT \'B\'', 'VARCHAR(10) DEFAULT \'B\''),
                ]
                for col_name, sqlite_type, mssql_type in new_prod_cols:
                    if col_name not in prod_cols:
                        logger.info(f"Migrating products table: adding column {col_name}")
                        col_type = sqlite_type if is_sqlite else mssql_type
                        conn.execute(text(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}" if is_sqlite else f"ALTER TABLE products ADD {col_name} {col_type}"))
                        conn.commit()

            # 3. Migrate cartons table for weight & PO/LOT/date_code columns
            if inspector.has_table('cartons'):
                carton_cols = [c['name'] for c in inspector.get_columns('cartons')]
                new_carton_cols = [
                    ('weight', 'FLOAT NULL', 'FLOAT NULL'),
                    ('po_number', 'VARCHAR(100) NULL', 'VARCHAR(100) NULL'),
                    ('lot_number', 'VARCHAR(100) NULL', 'VARCHAR(100) NULL'),
                    ('date_code', 'VARCHAR(20) NULL', 'VARCHAR(20) NULL'),
                ]
                for col_name, sqlite_type, mssql_type in new_carton_cols:
                    if col_name not in carton_cols:
                        logger.info(f"Migrating cartons table: adding column {col_name}")
                        col_type = sqlite_type if is_sqlite else mssql_type
                        conn.execute(text(f"ALTER TABLE cartons ADD COLUMN {col_name} {col_type}" if is_sqlite else f"ALTER TABLE cartons ADD {col_name} {col_type}"))
                        conn.commit()

            # 4. Migrate Customer UX -> A11
            if inspector.has_table('customers'):
                conn.execute(text("UPDATE customers SET code = 'A11', name = 'Customer A11' WHERE code = 'UX'"))
                conn.commit()

            # 5. Migrate historical UTC timestamps in cartons to Local Time (+7 hours)
            if inspector.has_table('cartons'):
                conn.execute(text(
                    "CREATE TABLE IF NOT EXISTS schema_migrations (version VARCHAR(100) PRIMARY KEY, applied_at DATETIME)"
                    if is_sqlite else
                    "IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='schema_migrations' AND xtype='U') CREATE TABLE schema_migrations (version VARCHAR(100) PRIMARY KEY, applied_at DATETIME)"
                ))
                conn.commit()

                res = conn.execute(text("SELECT version FROM schema_migrations WHERE version = 'cartons_timezone_utc_to_local_v1'")).first()
                if not res:
                    logger.info("Migrating: adjusting historical cartons.created_at (+7 hours to local time)")
                    if is_sqlite:
                        conn.execute(text("UPDATE cartons SET created_at = datetime(created_at, '+7 hours') WHERE created_at IS NOT NULL"))
                        conn.execute(text("INSERT INTO schema_migrations (version, applied_at) VALUES ('cartons_timezone_utc_to_local_v1', datetime('now'))"))
                    else:
                        conn.execute(text("UPDATE cartons SET created_at = DATEADD(hour, 7, created_at) WHERE created_at IS NOT NULL"))
                        conn.execute(text("INSERT INTO schema_migrations (version, applied_at) VALUES ('cartons_timezone_utc_to_local_v1', GETDATE())"))
                    conn.commit()

        # Run seed data
        with SessionLocal() as db:
            seed_a11_data(db)
            try:
                from src.features.auth.service import seed_default_users
                seed_default_users(db)
            except Exception as e:
                logger.warning(f"Seed default users notice: {e}")

    except Exception as e:
        logger.error(f"Failed to initialize or migrate database tables: {e}")
