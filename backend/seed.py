from database import SessionLocal
from models import Customer, Product

def seed():
    db = SessionLocal()
    
    # Create Customer UI
    ui_customer = db.query(Customer).filter(Customer.code == "UI").first()
    if not ui_customer:
        ui_customer = Customer(code="UI", name="UI Customer")
        db.add(ui_customer)
        db.commit()
        db.refresh(ui_customer)
        print("Customer UI created")

    # Sample products from 1.png
    products_data = [
        {"item_name": "U-Cable-Patch-RJ45", "packed_qty": 100, "start_part": "CN", "middle_part": "9", "upc": "810010075765"},
        {"item_name": "U-Cable-Patch-RJ45-BK", "packed_qty": 100, "start_part": "CN", "middle_part": "MA", "upc": "810010075772"},
        {"item_name": "U-Cable-Patch-RJ45-BL", "packed_qty": 100, "start_part": "CN", "middle_part": "MB", "upc": "810010075789"},
        {"item_name": "U-Cable-Patch-0.3M-RJ45", "packed_qty": 240, "start_part": "CN", "middle_part": "10", "upc": "810010071422"},
        {"item_name": "U-Cable-Patch-1M-RJ45", "packed_qty": 120, "start_part": "CN", "middle_part": "11", "upc": "810010071439"},
    ]

    for p in products_data:
        exists = db.query(Product).filter(Product.item_name == p["item_name"], Product.customer_id == ui_customer.id).first()
        if not exists:
            db.add(Product(customer_id=ui_customer.id, **p))
            print(f"Product {p['item_name']} added")
    
    db.commit()
    db.close()

if __name__ == "__main__":
    seed()
