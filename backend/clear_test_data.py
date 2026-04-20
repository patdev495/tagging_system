import sys
import os

# Add the current directory to path so we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
from models import Carton, CartonItem
import models
from sqlalchemy import delete

def clear_test_data():
    print("--- DATABASE SCHEMA SYNC & CLEANUP UTILITY ---")
    print("This will drop and recreate the transaction tables (cartons, carton_items).")
    print("This is necessary to apply the new 'status' column and SN logic.")
    print("Customers and Products will NOT be deleted.")
    
    confirm = input("\nAre you SURE you want to clear all and sync schema? Type 'YES' to confirm: ")
    
    if confirm != "YES":
        print("Cleanup cancelled.")
        return

    db = SessionLocal()
    try:
        print("Dropping carton_items and cartons tables to sync schema...")
        # Order matters due to Foreign Keys: drop items first
        models.CartonItem.__table__.drop(engine, checkfirst=True)
        models.Carton.__table__.drop(engine, checkfirst=True)
        
        print("Recreating tables with new schema...")
        Base.metadata.create_all(bind=engine)
        
        print("\nSUCCESS: Database schema has been synchronized and data cleared.")
        print("You can now start packing from scratch.")
    except Exception as e:
        print(f"\nERROR: Cleanup failed: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_test_data()
