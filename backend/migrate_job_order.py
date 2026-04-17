from database import engine
from sqlalchemy import text

def migrate():
    print("Starting migration: Adding job_order to cartons table...")
    with engine.connect() as conn:
        try:
            # check if column exists
            check_sql = text("""
                IF NOT EXISTS (
                    SELECT * FROM sys.columns 
                    WHERE object_id = OBJECT_ID('cartons') 
                    AND name = 'job_order'
                )
                BEGIN
                    ALTER TABLE cartons ADD job_order NVARCHAR(100);
                    PRINT 'Column job_order added successfully.';
                END
                ELSE
                BEGIN
                    PRINT 'Column job_order already exists.';
                END
            """)
            conn.execute(check_sql)
            # Need to commit for some DB connections if not auto-commit
            conn.execute(text("COMMIT"))
            print("Migration complete.")
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
