import sys
import os

# Add the current directory to path so we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Carton, CartonItem
from sqlalchemy import delete

def clear_test_data():
    print("--- DATABASE CLEANUP UTILITY ---")
    print("This will delete all packing history (cartons and scanned items).")
    print("Customers and Products will NOT be deleted.")
    
    confirm = input("\nAre you SURE you want to clear all test data? Type 'YES' to confirm: ")
    
    if confirm != "YES":
        print("Cleanup cancelled.")
        return

    db = SessionLocal()
    try:
        print("Clearing carton items table...")
        db.execute(delete(CartonItem))
        
        print("Clearing cartons table...")
        db.execute(delete(Carton))
        
        db.commit()
        print("\nSUCCESS: All test data has been cleared.")
        print("You can now start packing from scratch.")
    except Exception as e:
        db.rollback()
        print(f"\nERROR: Cleanup failed: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_test_data()
