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

def migrate_legacy_erro_data(db):
    """Idempotently preserve the existing Customer ID while canonicalizing Erro data."""
    from src.core import models

    erro_customer = db.query(models.Customer).filter(models.Customer.code == "ERRO").first()
    a11_customer = db.query(models.Customer).filter(models.Customer.code == "A11").first()
    if erro_customer and a11_customer and erro_customer.id != a11_customer.id:
        raise RuntimeError("Cannot migrate A11 to ERRO because both Customer records already exist")

    customer = erro_customer or a11_customer
    if not customer:
        return None

    customer.code = "ERRO"
    customer.name = "Erro"
    template_types = {
        "a11": ("erro_01", "a11.btw", "erro_01.btw"),
        "a11_tem2": ("erro_02", "a11_02.btw", "erro_02.btw"),
        "a11_tem3": ("erro_03", "a11_03.btw", "erro_03.btw"),
    }
    for product in db.query(models.Product).filter(models.Product.customer_id == customer.id):
        migration = template_types.get(product.template_type)
        if migration:
            new_type, old_filename, new_filename = migration
            product.template_type = new_type
            if product.template_path:
                product.template_path = product.template_path.replace(old_filename, new_filename)

    db.commit()
    logger.info("Migrated Customer A11 to ERRO and canonicalized Erro template codes")
    return customer


def seed_erro_data(db):
    """Seed Customer Erro and its three active label templates if absent."""
    from src.core import models
    try:
        erro_customer = db.query(models.Customer).filter(models.Customer.code == "ERRO").first()
        if not erro_customer:
            erro_customer = models.Customer(code="ERRO", name="Erro")
            db.add(erro_customer)
            db.flush()
            logger.info("Seeded Customer Erro")

        erro_products = [
            ("840-00083", 190, "VHK0010237", "NYS5998", "erro_01", r"D:\PAT\Templates\erro_01.btw", "weight_scale", "B", "kg", 12.500, 12.300, 12.700, None, None, None),
            ("840-00091", 190, "VHK0010237", "NYS5998", "erro_01", r"D:\PAT\Templates\erro_01.btw", "weight_scale", "B", "kg", 12.500, 12.300, 12.700, None, None, None),
            ("840-00092", 190, "VHK0010237", "NYS5998", "erro_01", r"D:\PAT\Templates\erro_01.btw", "weight_scale", "B", "kg", 12.500, 12.300, 12.700, None, None, None),
            ("G012C1B", 190, "37033907", "NYS5998", "erro_02", r"D:\PAT\Templates\erro_02.btw", "weight_scale", "B", "kg", 6.000, 5.000, 7.000, "852582006785", "B08G9M4HXS", "ASSY,BAND WRAPPED,CAT5E ETHERNET CABLE 4.0mm OD:91CM,WHITE,RUBBER BAND"),
            ("G112C1B", 190, "37033907", "NYS5996", "erro_02", r"D:\PAT\Templates\erro_02.btw", "weight_scale", "B", "kg", 6.000, 5.000, 7.000, "840268969493", "B0C32N712K", "ASSY, BAND WRAPPED, CAT6A ETHERNET CABLE 4.7MM OD, 91CM , WHITE,RUBBER BAND"),
            ("2M21-00508-0004H", 190, "1012665", None, "erro_03", r"D:\PAT\Templates\erro_03.btw", "weight_scale", "/", "kg", 6.000, 5.000, 7.000, None, None, "CAT5E ETHERNET CABLE"),
        ]

        # PD027032 Table 1 Erro 04 products (exactly 16 complete rows):
        # Note: The incomplete row NYS6248 is not created and is documented as pending source data (lacks UPC and SKU).
        erro_04_products = [
            ("115-00020", "840268939793", "G111A1A", "NYS5896", 120, "H", "Accessory, Ethernet Cable CAT6a, 15cm, Black, 1PK, Basic Box"),
            ("115-00021", "840268971793", "G111B1A", "NYS5944", 96, "H", "Accessory, Ethernet Cable CAT6a, 30cm, Black, 1PK, Basic Box"),
            ("115-00022", "840268917517", "G111C1A", "NYS5850", 90, "H", "Accessory, Ethernet Cable CAT6a, 91cm, Black, 1PK, Basic Box"),
            ("115-00023", "840268972110", "G111D1A", "NYS5945", 66, "H", "Accessory, Ethernet Cable CAT6a, 152cm, Black, 1PK, Basic Box"),
            ("115-00024", "840268922047", "G111F1A", "NYS5946", 54, "H", "Accessory, Ethernet Cable CAT6a, 305cm, Black, 1PK, Basic Box"),
            ("115-00025", "840268995669", "G111A1B", "NYS5895", 120, "H", "Accessory, Ethernet Cable CAT6a, 15cm, White, 1PK, Basic Box"),
            ("115-00026", "840268992958", "G111B1B", "NYS5940", 96, "H", "Accessory, Ethernet Cable CAT6a, 30cm, White, 1PK, Basic Box"),
            ("115-00027", "840268921125", "G111C1B", "NYS5849", 90, "H", "Accessory, Ethernet Cable CAT6a, 91cm, White, 1PK, Basic Box"),
            ("115-00028", "840268976620", "G111D1B", "NYS5941", 66, "H", "Accessory, Ethernet Cable CAT6a, 152cm, White, 1PK, Basic Box"),
            ("115-00029", "840268911294", "G111F1B", "NYS5943", 54, "H", "Accessory, Ethernet Cable CAT6a, 305cm, White, 1PK, Basic Box"),
            ("115-00030", "840268936198", "G111A1C", "NYS5897", 120, "H", "Accessory, Ethernet Cable CAT6a, 15cm, Midnight Blue, 1PK, Basic Box"),
            ("115-00031", "840268937065", "G111B1C", "NYS5947", 96, "H", "Accessory, Ethernet Cable CAT6a, 30cm, Midnight Blue, 1PK, Basic Box"),
            ("115-00032", "840268938062", "G111C1C", "NYS5851", 90, "H", "Accessory, Ethernet Cable CAT6a, 91cm, Midnight Blue, 1PK, Basic Box"),
            ("115-00033", "840268902889", "G111D1C", "NYS5949", 66, "H", "Accessory, Ethernet Cable CAT6a, 152cm, Midnight Blue, 1PK, Basic Box"),
            ("115-00034", "840268936235", "G111F1C", "NYS5950", 54, "H", "Accessory, Ethernet Cable CAT6a, 305cm, Midnight Blue, 1PK, Basic Box"),
            ("115-00035", "840080582474", "G011C1B", "NYS5989", 90, "K", "Accessory, Ethernet Cable CAT5e, 91cm, White, 1PK, Basic Box"),
        ]

        for item_name, qty, prefix, mfr_pn, tmpl, tmpl_path, mode, rev, unit, target_w, min_w, max_w, upc, asin, product_desc in erro_products:
            prod = db.query(models.Product).filter(
                models.Product.customer_id == erro_customer.id,
                models.Product.item_name == item_name
            ).first()
            if not prod:
                prod = models.Product(
                    customer_id=erro_customer.id,
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
                    upc=upc,
                    asin=asin,
                    product_desc=product_desc,
                )
                db.add(prod)
                logger.info(f"Seeded Erro Product: {item_name}")
            else:
                updated = False
                if asin and not prod.asin:
                    prod.asin = asin
                    updated = True
                if product_desc and not prod.product_desc:
                    prod.product_desc = product_desc
                    updated = True
                if upc and not prod.upc:
                    prod.upc = upc
                    updated = True
                if updated:
                    db.add(prod)

        for factory_item_code, upc, sku, supplier_pn, qty, carton_id_prefix, product_desc in erro_04_products:
            prod = db.query(models.Product).filter(
                models.Product.customer_id == erro_customer.id,
                models.Product.item_name == sku,
            ).first()
            if not prod:
                db.add(models.Product(
                    customer_id=erro_customer.id,
                    item_name=sku,
                    upc=upc,
                    packed_qty=qty,
                    template_type="erro_04",
                    template_path=r"D:\PAT\Templates\erro_04.btw",
                    packing_mode="weight_scale",
                    mfr_pn=supplier_pn,
                    product_desc=product_desc,
                    factory_item_code=factory_item_code,
                    carton_id_prefix=carton_id_prefix,
                    revision="B",
                    weight_unit="kg",
                    min_weight=0.0,
                    max_weight=10.0,
                    target_weight=5.0,
                ))

        # PD016906 Page 3 Erro 05 (Pegatron NN9) products (all 38 items):
        erro_05_products = [
            ("1401-02BP0W3", "1CAU0002M2WH07NX9", "USB2.0 AM TO 90° TYPE-C TPE 2M"),
            ("1412-04FH0W3", "1CAH0007C0XX01NX9", "FFC CABLE 40p"),
            ("1412-04FJ0W3", "1CAH0003C0XX01NX9", "FFC CABLE 16P"),
            ("1412-04M80W3", "1CAH0032A0XX01NX9", "FFC CABLE 16P P:0.5mm L:32mm"),
            ("1412-04T50W3", "1CAH0007C0XX03NX9", "FFC CABLE 40p,325-00274-03"),
            ("1414-0E5A0W3", "1HWN2870A2BK06NX9", "WIRE CABLE 10P TO 10P L:70mm"),
            ("1414-0EG10W3", "1HWU2825C2BK04NX9", "28AWG*1C FEP JACKET BK 250MM"),
            ("1414-0EKE0W3", "1HWN2817C2BK01NX9", "HSG 10P-10P L BLACK 17CM"),
            ("1414-0EP50W3", "1HWU1870A2BK05NX9", "18AWG*1C GROUNDING CABLE 70MM"),
            ("1414-0F0W0W3", "1LAX2812C2U003NX9", "28AWG*1C FEP JACKET BLACK"),
            ("1414-0F0X0W3", "1LAX2860A2U003NX9", "28AWG*1C HSG 4P TO 4P L=60mm"),
            ("1401-02DC0W3", "1CAU3202M2WH02NN9", "USB2.0 AM TO 90° TYPE-C TPE JAC"),
            ("1401-02HF0W9", "1CAD2420D2WH01M22P", "USB 2.0,USB A TO MICRO B"),
            ("1401-02QK0W9", "1CAC2402M2WH02M22Q", "CBL,USB A TO MICRO B, L=2M"),
            ("1401-02QK0W9", "1CAC2402M2WH03M22Q", "CBL,USB A TO MICRO B, L=2M"),
            ("1401-02QK0W9", "1CAC2402M2WH04M22Q", "CBL,USB A TO MICRO B, L=2M"),
            ("1401-02QK0W9", "1CAD2420D1WH03M22P", "CBL,USB A TO MICRO B, L=2M"),
            ("1401-02QK0W9", "1CAD2420D1WH03M22Q", "CBL,USB A TO MICRO B, L=2M"),
            ("1401-02QK0W9", "1CAD2420D2WH01M22Q", "CBL,USB A TO MICRO B, L=2M"),
            ("1401-02QK0W9", "1CAD2420D2WH02M22P", "CBL,USB A TO MICRO B, L=2M"),
            ("1401-02QK0W9", "1CAD2420D2WH02M22Q", "CBL,USB A TO MICRO B, L=2M"),
            ("1401-02QK0W9", "1CAD2420D2WH02M22V", "CBL,USB A TO MICRO B, L=2M"),
            ("1401-02QK0W9", "1CAD2420D2WH03M22V", "CBL,USB A TO MICRO B, L=2M"),
            ("1402-00GD000", "1LAE2403M2U001NN9", "LAN CAT.5E 8P8C CABLE YELLOW"),
            ("1402-01060DL", "1LA62615D2F001NN9", "26AWG*4P CAT6 CABLE YELLOW15DM"),
            ("1412-04HK0W3", "1CAH0007C0XX02NN9", "FFC CABLE 40p"),
            ("1414-0E600W3", "1CAC2050C2BK02NN9", "20AWG*10C PVC JACKET BLACK"),
            ("1414-0G1M0BV", "1HWU3023C1XX01NN9", "X LED CABLE 30AWG 230mm PD030625"),
            ("1414-0G1N0BV", "1HWU3006C1XX01NN9", "W LED CABLE 30AWG 60mm PD030627"),
            ("1414-0G3C0BV", "1HWU1895A2XX03NN9", "CABLE,EXT TEMP,SFP"),
            ("1417-0062000", "1CAC2815D2BK02NN9", "RCA CABLE (RYW) L=1.5M"),
            ("1417-0063000", "1CAC2815D2BK01NN9", "RCA CABLE (RBG) L=1.5M"),
            ("1401-03GN0W9", "1CAU0010D2XX02NN9", "inbox cable,USB2.0 AM TO TYPE-C L=1M"),
            ("1414-0GD90BV", "1HWU3006C1XX02NN9", "W LED CABLE 30AWG 60mm"),
            ("1414-0GDA0BV", "1HWU3023C1XX02NN9", "X LED CABLE 30AWG 230mm"),
            ("1401-03L40BV", "1CAC2822C2BK02MAA", "CABLE,DEBUG,USB-C,W4"),
            ("1401-03L50BV", "1CAC2811C2BK02MAA", "CABLE,DEBUG,USB-C,X4/W2/X2"),
            ("0A02-02WF0BV", "1MA00PCBAXX045NN9", "LED PCBA BOARD NIENYI/NYS6994"),
        ]

        for item_name, factory_item_code, product_desc in erro_05_products:
            prod = db.query(models.Product).filter(
                models.Product.customer_id == erro_customer.id,
                models.Product.factory_item_code == factory_item_code,
            ).first()
            if not prod:
                db.add(models.Product(
                    customer_id=erro_customer.id,
                    item_name=item_name,
                    factory_item_code=factory_item_code,
                    product_desc=product_desc,
                    pkg_prefix="MC220TW1",
                    packed_qty=1000,
                    template_type="erro_05",
                    template_path=r"D:\PAT\Templates\erro_05.btw",
                    packing_mode="weight_scale",
                    min_weight=0.0,
                    max_weight=10.0,
                    target_weight=5.0,
                    weight_unit="kg",
                    revision="",
                ))
            else:
                updated = False
                if not prod.template_type:
                    prod.template_type = "erro_05"
                    updated = True
                if not prod.pkg_prefix:
                    prod.pkg_prefix = "MC220TW1"
                    updated = True
                if updated:
                    db.add(prod)

        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning(f"Seed Erro data notice: {e}")

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

            # 2. Migrate products table for weight_scale columns
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
                    ('asin', 'VARCHAR(50) NULL', 'VARCHAR(50) NULL'),
                    ('product_desc', 'VARCHAR(255) NULL', 'VARCHAR(255) NULL'),
                    ('factory_item_code', 'VARCHAR(50) NULL', 'VARCHAR(50) NULL'),
                    ('carton_id_prefix', 'VARCHAR(1) NULL', 'VARCHAR(1) NULL'),
                ]
                for col_name, sqlite_type, mssql_type in new_prod_cols:
                    if col_name not in prod_cols:
                        logger.info(f"Migrating products table: adding column {col_name}")
                        col_type = sqlite_type if is_sqlite else mssql_type
                        conn.execute(text(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}" if is_sqlite else f"ALTER TABLE products ADD {col_name} {col_type}"))
                        conn.commit()

                # Factory P/N was never used by the Erro label formats. Remove
                # the obsolete storage column and its optional index.
                if 'factory_pn' in prod_cols:
                    logger.info("Migrating products table: removing obsolete factory_pn")
                    if is_sqlite:
                        conn.execute(text("DROP INDEX IF EXISTS ix_products_factory_pn"))
                        conn.execute(text("ALTER TABLE products DROP COLUMN factory_pn"))
                    else:
                        conn.execute(text(
                            "IF EXISTS (SELECT 1 FROM sys.indexes "
                            "WHERE name = 'ix_products_factory_pn' "
                            "AND object_id = OBJECT_ID('products')) "
                            "DROP INDEX ix_products_factory_pn ON products"
                        ))
                        conn.execute(text("ALTER TABLE products DROP COLUMN factory_pn"))
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

            # 4. Migrate historical UTC timestamps in cartons to Local Time (+7 hours)
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
            migrate_legacy_erro_data(db)
            seed_erro_data(db)
            try:
                from src.features.auth.service import seed_default_users
                seed_default_users(db)
            except Exception as e:
                logger.warning(f"Seed default users notice: {e}")

    except Exception as e:
        logger.error(f"Failed to initialize or migrate database tables: {e}")
