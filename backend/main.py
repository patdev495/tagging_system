from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import models, database, schemas
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import datetime
import os

app = FastAPI(title="NY Tagging System API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to NY Tagging System API"}

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.datetime.utcnow()}

@app.get("/customers", response_model=List[schemas.Customer])
def get_customers(db: Session = Depends(database.get_db)):
    return db.query(models.Customer).all()

@app.get("/customers/{customer_id}/products", response_model=List[schemas.Product])
def get_customer_products(customer_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.Product).filter(models.Product.customer_id == customer_id).all()

@app.get("/products/{product_id}/last-carton", response_model=Optional[schemas.Carton])
def get_last_carton(product_id: int, db: Session = Depends(database.get_db)):
    # Returns the most recent carton created for this product
    return db.query(models.Carton).filter(models.Carton.product_id == product_id).order_by(models.Carton.created_at.desc()).first()

# Logic for Carton S/N Generation & Printing
def generate_btxml(carton: models.Carton, product: models.Product, items: List[str], template_path: str, printer_name: str = None):
    # Origin logic directly from carton
    raw_origin = carton.carton_origin if carton.carton_origin else "VN"
    origin_text = "MADE IN CHINA" if raw_origin == "CN" else "MADE IN VIETNAM"
    
    # QR Content: Item S/Ns separated by newline (XML entity for newline)
    qr_content = "&#xA;".join(items)
    # Target printer
    printer_tag = f"<Printer>{printer_name}</Printer>" if printer_name else ""
    
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<XMLScript Version="2.0">
    <Command Name="Job1">
        <Print>
            <Format>{template_path}</Format>
            <PrintSetup>
                {printer_tag}
            </PrintSetup>
            <NamedSubString Name="ItemName"><Value>{product.item_name}</Value></NamedSubString>
            <NamedSubString Name="QTY"><Value>{product.packed_qty}PCS</Value></NamedSubString>
            <NamedSubString Name="CartonSN"><Value>{carton.carton_sn}</Value></NamedSubString>
            <NamedSubString Name="UPC"><Value>{product.upc}</Value></NamedSubString>
            <NamedSubString Name="QR_Content"><Value>{qr_content}</Value></NamedSubString>
            <NamedSubString Name="Origin"><Value>{origin_text}</Value></NamedSubString>
        </Print>
    </Command>
</XMLScript>"""
    return xml.strip()

def get_next_carton_sn(db: Session, product: models.Product, custom_sn: int = None):
    now = datetime.datetime.now()
    yymm = now.strftime("%y%m")
    prefix = f"{product.start_part}{yymm}{product.middle_part}"
    
    if custom_sn is not None:
        return f"{prefix}{str(custom_sn).zfill(5)}"
        
    # Check max sequence for this prefix in DB with a lock
    # with_for_update() ensures other transactions wait until this one is committed
    # Check max sequence for this prefix in DB that was SUCCESSFUL
    # This ensures that if all attempts for an SN failed, we reuse that SN.
    max_sn = db.query(func.max(models.Carton.carton_sn)).filter(
        models.Carton.carton_sn.like(f"{prefix}%"),
        models.Carton.status == "SUCCESS"
    ).with_for_update().scalar()
    
    if max_sn:
        # Extract the last 5 digits and increment
        try:
            current_seq = int(max_sn[-5:])
            next_seq = current_seq + 1
        except ValueError:
            next_seq = 1
    else:
        next_seq = 1
        
    return f"{prefix}{str(next_seq).zfill(5)}"

@app.get("/products/{product_id}/next-sn")
def get_next_sn_preview(product_id: int, db: Session = Depends(database.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # We don't want to use with_for_update() for a pure preview to avoid locking,
    # but for simplicity and consistency, let's just reuse the logic without custom_sn
    # Actually, let's extract the numeric part
    now = datetime.datetime.now()
    yymm = now.strftime("%y%m")
    prefix = f"{product.start_part}{yymm}{product.middle_part}"
    
    max_sn = db.query(func.max(models.Carton.carton_sn)).filter(
        models.Carton.carton_sn.like(f"{prefix}%"),
        models.Carton.status == "SUCCESS"
    ).scalar()
    
    next_seq = 1
    if max_sn:
        try:
            next_seq = int(max_sn[-5:]) + 1
        except ValueError:
            next_seq = 1
            
    return {"next_seq": next_seq, "full_sn": f"{prefix}{str(next_seq).zfill(5)}"}

@app.get("/cartons/search", response_model=Optional[schemas.Carton])
def search_carton(carton_sn: str, db: Session = Depends(database.get_db)):
    # Search for a successful carton by exact S/N
    return db.query(models.Carton).filter(
        models.Carton.carton_sn == carton_sn,
        models.Carton.status == "SUCCESS"
    ).order_by(models.Carton.created_at.desc()).first()

@app.post("/cartons", response_model=schemas.Carton)
def create_carton(carton_in: schemas.CartonCreate, db: Session = Depends(database.get_db)):
    # 1. Get product
    product = db.query(models.Product).filter(models.Product.id == carton_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 2. Check for duplicates in the current scan
    if len(carton_in.items) != len(set(carton_in.items)):
        raise HTTPException(status_code=400, detail="Duplicate item S/Ns found in scan")
    
    # 3. Generate new S/N
    new_sn = get_next_carton_sn(db, product, carton_in.custom_sn)
    
    # Check if a successful print already exists for this exact custom sequence
    if carton_in.custom_sn is not None:
        existing = db.query(models.Carton).filter(
            models.Carton.carton_sn == new_sn,
            models.Carton.status == "SUCCESS"
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"S/N (Seq: {carton_in.custom_sn}) is already successfully printed.")

    # 4. Save to DB within a transaction
    try:
        new_carton = models.Carton(
            product_id=product.id,
            carton_sn=new_sn,
            packed_by=carton_in.printer_name or "System", 
            job_order=carton_in.job_order,
            status="FAILED", # Default until agent confirms success
            btxml=None, # Will be updated
            carton_origin=carton_in.carton_origin
        )
        db.add(new_carton)
        db.flush() # Get new_carton.id
        
        for item_sn in carton_in.items:
            new_item = models.CartonItem(
                carton_id=new_carton.id,
                item_sn=item_sn
            )
            db.add(new_item)
        
        # Phase 3: Generate BTXML but DO NOT save to DB
        btxml_content = None
        if carton_in.template_path:
            btxml_content = generate_btxml(
                new_carton, 
                product, 
                carton_in.items, 
                carton_in.template_path,
                carton_in.printer_name
            )
            new_carton.btxml = btxml_content
            
            # Phase 3: Direct write to folder if provided (Bypass browser downloads)
            if carton_in.print_folder:
                try:
                    if not os.path.exists(carton_in.print_folder):
                        os.makedirs(carton_in.print_folder)
                    
                    file_name = f"print_job_{new_carton.carton_sn}.xml"
                    file_path = os.path.join(carton_in.print_folder, file_name)
                    tmp_path = file_path + ".tmp"
                    
                    with open(tmp_path, "w", encoding="utf-8") as f:
                        f.write(btxml_content)
                    
                    # Atomic rename
                    os.rename(tmp_path, file_path)
                    print(f"Directly wrote print job (XML) to: {file_path}")
                except Exception as e:
                    print(f"Error writing print job file: {str(e)}")
                
                # New: Trigger Bartender directly via command line for reliability
                import subprocess
                # Command: bartend.exe /XMLScript="C:\...\print_job.xml" /PRN="PrinterName" /X
                # /X means exit after processing the script
                exe_path = r"C:\Program Files\Seagull\BarTender 2022\bartend.exe"
                if os.path.exists(exe_path):
                    try:
                        # Using /PRN flag to explicitly target the printer if provided
                        args = [exe_path, f"/XMLScript={file_path}"]
                        if carton_in.printer_name:
                            args.append(f"/PRN={carton_in.printer_name}")
                        args.append("/X")
                        
                        subprocess.Popen(args)
                        print(f"Triggered direct print via command line: {file_name}")
                    except Exception as pe:
                        print(f"Error triggering direct print: {str(pe)}")
                else:
                    print(f"Bartender executable not found at specified path. Relying on Watch Folder.")
            
        db.commit()
        db.refresh(new_carton)
            
        # Manually attach btxml for the response schema
        response_data = schemas.Carton.from_orm(new_carton)
        response_data.btxml = btxml_content
        return response_data
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.patch("/cartons/{carton_id}/status", response_model=schemas.Carton)
def update_carton_status(carton_id: int, status_update: schemas.CartonStatusUpdate, db: Session = Depends(database.get_db)):
    carton = db.query(models.Carton).filter(models.Carton.id == carton_id).first()
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
    
    carton.status = status_update.status
    db.commit()
    db.refresh(carton)
    return carton

@app.get("/cartons/{carton_id}/btxml")
def download_carton_btxml(carton_id: int, template_path: Optional[str] = None, db: Session = Depends(database.get_db)):
    carton = db.query(models.Carton).filter(models.Carton.id == carton_id).first()
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
    
    btxml_content = carton.btxml
    
    # If btxml is missing (old records), regenerate it on the fly
    if not btxml_content:
        product = db.query(models.Product).filter(models.Product.id == carton.product_id).first()
        item_sns = [item.item_sn for item in carton.items]
        
        # Use provided template path or fallback to a default
        path_to_use = template_path or "D:\\Labels\\carton_ui.btw"
        
        btxml_content = generate_btxml(carton, product, item_sns, path_to_use)
    
    from fastapi.responses import Response
    return Response(
        content=btxml_content,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename=print_job_{carton.carton_sn}.xml"
        }
    )

@app.post("/cartons/{carton_id}/reprint", response_model=schemas.Carton)
def reprint_carton(carton_id: int, template_path: Optional[str] = None, printer_name: Optional[str] = None, db: Session = Depends(database.get_db)):
    # 1. Fetch original record
    original = db.query(models.Carton).filter(models.Carton.id == carton_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Original carton not found")
    
    # 2. Duplicate the record
    new_carton = models.Carton(
        product_id=original.product_id,
        carton_sn=original.carton_sn,
        job_order=original.job_order,
        packed_by=printer_name or original.packed_by,
        status="SUCCESS", # Reprints are considered successful attempts by default
        is_reprint=1
    )
    db.add(new_carton)
    db.flush()
    
    # 3. Duplicate items
    for item in original.items:
        new_item = models.CartonItem(
            carton_id=new_carton.id,
            item_sn=item.item_sn
        )
        db.add(new_item)
    
    # 4. Generate BTXML
    product = db.query(models.Product).filter(models.Product.id == original.product_id).first()
    item_sns = [item.item_sn for item in original.items]
    path_to_use = template_path or "D:\\Labels\\carton_ui.btw"
    
    btxml_content = generate_btxml(new_carton, product, item_sns, path_to_use, printer_name)
    new_carton.btxml = btxml_content
    
    db.commit()
    db.refresh(new_carton)
    
    # Manually attach btxml for the response schema
    response_data = schemas.Carton.from_orm(new_carton)
    response_data.btxml = btxml_content
    return response_data

# Health check for DB
@app.get("/health")
def health_check(db: Session = Depends(database.get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# To run the backend manually with a custom port:
# uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
