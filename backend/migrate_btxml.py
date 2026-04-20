from database import engine
from sqlalchemy import text

def migrate():
    print("Starting migration: Adding btxml to cartons table...")
    with engine.connect() as conn:
        try:
            # check if column exists
            check_sql = text("""
                IF NOT EXISTS (
                    SELECT * FROM sys.columns 
                    WHERE object_id = OBJECT_ID('cartons') 
                    AND name = 'btxml'
                )
                BEGIN
                    ALTER TABLE cartons ADD btxml NVARCHAR(MAX);
                    PRINT 'Column btxml added successfully.';
                END
                ELSE
                BEGIN
                    PRINT 'Column btxml already exists.';
                END
            """)
            conn.execute(check_sql)
            conn.execute(text("COMMIT"))
            print("Migration complete.")
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
