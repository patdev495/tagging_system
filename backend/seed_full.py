from database import SessionLocal
from models import Customer, Product

def seed_products():
    db = SessionLocal()
    
    # Get or create UI customer (id=1)
    ui_customer = db.query(Customer).filter(Customer.code == "UI").first()
    if not ui_customer:
        ui_customer = Customer(code="UI", name="UI Customer")
        db.add(ui_customer)
        db.commit()
        db.refresh(ui_customer)
    
    cid = ui_customer.id

    # Clear existing data to avoid FK conflicts
    # Since this is a new setup, clearing test history is acceptable
    from models import Carton, CartonItem
    db.query(CartonItem).filter(CartonItem.carton_id.in_(
        db.query(Carton.id).filter(Carton.product_id.in_(
            db.query(Product.id).filter(Product.customer_id == cid)
        ))
    )).delete(synchronize_session=False)
    
    db.query(Carton).filter(Carton.product_id.in_(
        db.query(Product.id).filter(Product.customer_id == cid)
    )).delete(synchronize_session=False)

    db.query(Product).filter(Product.customer_id == cid).delete(synchronize_session=False)
    db.commit()

    products_data = [
        {"item_name": "U-Cable-Patch-RJ45", "packed_qty": 100, "start_part": "CN", "middle_part": "9", "upc": "810010075765"},
        {"item_name": "U-Cable-Patch-RJ45-BK", "packed_qty": 100, "start_part": "CN", "middle_part": "A", "upc": "810010075772"},
        {"item_name": "U-Cable-Patch-RJ45-BL", "packed_qty": 100, "start_part": "CN", "middle_part": "B", "upc": "810010075789"},
        {"item_name": "U-Cable-Patch-0.3M-RJ45", "packed_qty": 240, "start_part": "CN", "middle_part": "10", "upc": "810010071422"},
        {"item_name": "U-Cable-Patch-1M-RJ45", "packed_qty": 120, "start_part": "CN", "middle_part": "11", "upc": "810010071439"},
        {"item_name": "U-Cable-Patch-2M-RJ45", "packed_qty": 100, "start_part": "CN", "middle_part": "12", "upc": "810010071446"},
        {"item_name": "U-Cable-Patch-3M-RJ45", "packed_qty": 100, "start_part": "CN", "middle_part": "13", "upc": "810010071453"},
        {"item_name": "U-Cable-Patch-5M-RJ45", "packed_qty": 80, "start_part": "CN", "middle_part": "14", "upc": "810010071460"},
        {"item_name": "U-Cable-Patch-8M-RJ45", "packed_qty": 60, "start_part": "CN", "middle_part": "15", "upc": "810010071477"},
        {"item_name": "U-Cable-Patch-0.3M-RJ45-BK", "packed_qty": 240, "start_part": "CN", "middle_part": "16", "upc": "810010071484"},
        {"item_name": "U-Cable-Patch-1M-RJ45-BK", "packed_qty": 120, "start_part": "CN", "middle_part": "17", "upc": "810010071491"},
        {"item_name": "U-Cable-Patch-2M-RJ45-BK", "packed_qty": 100, "start_part": "CN", "middle_part": "18", "upc": "810010071507"},
        {"item_name": "U-Cable-Patch-3M-RJ45-BK", "packed_qty": 100, "start_part": "CN", "middle_part": "19", "upc": "810010071514"},
        {"item_name": "U-Cable-Patch-5M-RJ45-BK", "packed_qty": 80, "start_part": "CN", "middle_part": "20", "upc": "810010071521"},
        {"item_name": "U-Cable-Patch-8M-RJ45-BK", "packed_qty": 60, "start_part": "CN", "middle_part": "21", "upc": "810010071538"},
        {"item_name": "U-Cable-Patch-0.3M-RJ45-BL", "packed_qty": 240, "start_part": "CN", "middle_part": "22", "upc": "810010071545"},
        {"item_name": "U-Cable-Patch-1M-RJ45-BL", "packed_qty": 120, "start_part": "CN", "middle_part": "23", "upc": "810010071552"},
        {"item_name": "U-Cable-Patch-2M-RJ45-BL", "packed_qty": 100, "start_part": "CN", "middle_part": "24", "upc": "810010071569"},
        {"item_name": "U-Cable-Patch-3M-RJ45-BL", "packed_qty": 100, "start_part": "CN", "middle_part": "25", "upc": "810010071576"},
        {"item_name": "U-Cable-Patch-5M-RJ45-BL", "packed_qty": 80, "start_part": "CN", "middle_part": "26", "upc": "810010071583"},
        {"item_name": "U-Cable-Patch-8M-RJ45-BL", "packed_qty": 60, "start_part": "CN", "middle_part": "27", "upc": "810010071590"},
        {"item_name": "U-Cable-Patch-RJ45-50", "packed_qty": 12, "start_part": "CN", "middle_part": "28", "upc": "810010074102"},
        {"item_name": "U-Cable-Patch-RJ45-BK-50", "packed_qty": 12, "start_part": "CN", "middle_part": "29", "upc": "810010074119"},
        {"item_name": "U-Cable-Patch-RJ45-BL-50", "packed_qty": 12, "start_part": "CN", "middle_part": "30", "upc": "810010074126"},
    ]

    for p in products_data:
        db.add(Product(customer_id=cid, **p))
    
    db.commit()
    print(f"Successfully added {len(products_data)} products.")
    db.close()

if __name__ == "__main__":
    seed_products()
