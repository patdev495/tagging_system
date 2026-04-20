from sqlalchemy import text
from database import SessionLocal

def backfill():
    print("Backfilling is_reprint column...")
    db = SessionLocal()
    try:
        db.execute(text("UPDATE cartons SET is_reprint = 0 WHERE is_reprint IS NULL"))
        db.commit()
        print("Backfill successful.")
    except Exception as e:
        print(f"Backfill failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    backfill()
