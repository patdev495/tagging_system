from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import models, database, schemas
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import datetime
import os
import uvicorn
import sys
import logging
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="NY Tagging System API")

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Logic in a Router ---
api_router = APIRouter(prefix="/api")

@api_router.get("/health")
def health_check(db: Session = Depends(database.get_db)):
    try:
        db.execute(text("SELECT 1"))
        # Using "ok" to match frontend expectation
        return {"status": "ok", "database": "connected", "timestamp": datetime.datetime.utcnow()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@api_router.get("/customers", response_model=List[schemas.Customer])
def get_customers(db: Session = Depends(database.get_db)):
    return db.query(models.Customer).all()

@api_router.get("/customers/{customer_id}/products", response_model=List[schemas.Product])
def get_customer_products(customer_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.Product).filter(models.Product.customer_id == customer_id).all()

@api_router.get("/products/{product_id}/last-carton", response_model=Optional[schemas.Carton])
def get_last_carton(product_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.Carton).filter(models.Carton.product_id == product_id).order_by(models.Carton.created_at.desc()).first()

# Logic for Carton S/N Generation & Printing
def generate_btxml(carton: models.Carton, product: models.Product, items: List[str], template_path: str, printer_name: str = None):
    raw_origin = carton.carton_origin if carton.carton_origin else "VN"
    origin_text = "MADE IN CHINA" if raw_origin == "CN" else "MADE IN VIETNAM"
    qr_content = "&#xA;".join(items)
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
        
    max_sn = db.query(func.max(models.Carton.carton_sn)).filter(
        models.Carton.carton_sn.like(f"{prefix}%"),
        models.Carton.status == "SUCCESS"
    ).with_for_update().scalar()
    
    if max_sn:
        try:
            next_seq = int(max_sn[-5:]) + 1
        except:
            next_seq = 1
    else:
        next_seq = 1
    return f"{prefix}{str(next_seq).zfill(5)}"

@api_router.get("/products/{product_id}/next-sn")
def get_next_sn_preview(product_id: int, db: Session = Depends(database.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
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
        except:
            next_seq = 1
    return {"next_seq": next_seq, "full_sn": f"{prefix}{str(next_seq).zfill(5)}"}

@api_router.post("/cartons", response_model=schemas.Carton)
def create_carton(carton_in: schemas.CartonCreate, db: Session = Depends(database.get_db)):
    product = db.query(models.Product).filter(models.Product.id == carton_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if len(carton_in.items) != len(set(carton_in.items)):
        raise HTTPException(status_code=400, detail="Duplicate item S/Ns found in scan")
    
    new_sn = get_next_carton_sn(db, product, carton_in.custom_sn)
    
    if carton_in.custom_sn is not None:
        existing = db.query(models.Carton).filter(models.Carton.carton_sn == new_sn, models.Carton.status == "SUCCESS").first()
        if existing:
            raise HTTPException(status_code=400, detail=f"S/N (Seq: {carton_in.custom_sn}) is already successfully printed.")

    try:
        new_carton = models.Carton(
            product_id=product.id,
            carton_sn=new_sn,
            packed_by=carton_in.printer_name or "System", 
            job_order=carton_in.job_order,
            status="FAILED",
            carton_origin=carton_in.carton_origin
        )
        db.add(new_carton)
        db.flush()
        
        for item_sn in carton_in.items:
            db.add(models.CartonItem(carton_id=new_carton.id, item_sn=item_sn))
        
        btxml_content = None
        if carton_in.template_path:
            # Generate the XML content (The core data for printing)
            btxml_content = generate_btxml(
                new_carton, 
                product, 
                carton_in.items, 
                carton_in.template_path, 
                carton_in.printer_name
            )
            new_carton.btxml = btxml_content
            
            # NOTE: Server does NOT create folders or run BarTender.
            # This is handled by the Client Agent (Local Agent) on the workstation.
            logger.info(f"BTXML generated for Carton S/N: {new_carton.carton_sn}")
            
        db.commit()
        db.refresh(new_carton)
        
        response_data = schemas.Carton.from_orm(new_carton)
        response_data.btxml = btxml_content # Return to client for local agent to use
        return response_data
    except Exception as e:
        db.rollback()
        logger.error(f"CRITICAL ERROR in create_carton: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@api_router.patch("/cartons/{carton_id}/status", response_model=schemas.Carton)
def update_carton_status(carton_id: int, status_update: schemas.CartonStatusUpdate, db: Session = Depends(database.get_db)):
    carton = db.query(models.Carton).filter(models.Carton.id == carton_id).first()
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
    carton.status = status_update.status
    db.commit()
    db.refresh(carton)
    return carton

@api_router.get("/cartons/{carton_id}/btxml")
def download_carton_btxml(carton_id: int, template_path: Optional[str] = None, db: Session = Depends(database.get_db)):
    carton = db.query(models.Carton).filter(models.Carton.id == carton_id).first()
    if not carton:
        raise HTTPException(status_code=404, detail="Carton not found")
    
    btxml_content = carton.btxml
    if not btxml_content:
        product = db.query(models.Product).filter(models.Product.id == carton.product_id).first()
        item_sns = [item.item_sn for item in carton.items]
        path_to_use = template_path or "D:\\Labels\\carton_ui.btw"
        btxml_content = generate_btxml(carton, product, item_sns, path_to_use)
    
    from fastapi.responses import Response
    return Response(content=btxml_content, media_type="application/xml", headers={"Content-Disposition": f"attachment; filename=print_job_{carton.carton_sn}.xml"})

@api_router.post("/cartons/{carton_id}/reprint", response_model=schemas.Carton)
def reprint_carton(carton_id: int, template_path: Optional[str] = None, printer_name: Optional[str] = None, db: Session = Depends(database.get_db)):
    original = db.query(models.Carton).filter(models.Carton.id == carton_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Original carton not found")
    
    new_carton = models.Carton(
        product_id=original.product_id,
        carton_sn=original.carton_sn,
        job_order=original.job_order,
        packed_by=printer_name or original.packed_by,
        status="SUCCESS",
        is_reprint=1
    )
    db.add(new_carton)
    db.flush()
    
    for item in original.items:
        db.add(models.CartonItem(carton_id=new_carton.id, item_sn=item.item_sn))
    
    product = db.query(models.Product).filter(models.Product.id == original.product_id).first()
    item_sns = [item.item_sn for item in original.items]
    path_to_use = template_path or "D:\\Labels\\carton_ui.btw"
    btxml_content = generate_btxml(new_carton, product, item_sns, path_to_use, printer_name)
    new_carton.btxml = btxml_content
    
    db.commit()
    db.refresh(new_carton)
    response_data = schemas.Carton.from_orm(new_carton)
    response_data.btxml = btxml_content
    return response_data

@api_router.get("/cartons/search", response_model=Optional[schemas.Carton])
def search_carton(carton_sn: str, db: Session = Depends(database.get_db)):
    return db.query(models.Carton).filter(models.Carton.carton_sn == carton_sn, models.Carton.status == "SUCCESS").order_by(models.Carton.created_at.desc()).first()

# --- Include Router ---
app.include_router(api_router)

# --- Serve Static Files (Vue) ---
# Determine base directory logic for PyInstaller or direct script execution
if getattr(sys, 'frozen', False):
    # Running as .exe
    base_dir = os.path.dirname(sys.executable)
else:
    # Running as .py script
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Flexible look-up for frontend/dist
# Priority: 1. ./frontend/dist (sibiling of exe) 2. ../frontend/dist (dev structure)
potential_paths = [
    os.path.join(base_dir, "frontend", "dist"),
    os.path.join(base_dir, "..", "frontend", "dist")
]

frontend_dist = None
for pt in potential_paths:
    if os.path.exists(pt):
        frontend_dist = pt
        break

if frontend_dist:
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def no_frontend():
        return {"message": f"API is running, but frontend 'dist' folder was not found at any of: {potential_paths}. Please ensure 'frontend/dist' exists next to the application."}

if __name__ == "__main__":
    # Prioritize API_PORT from .env for easier configuration
    port = int(os.getenv("API_PORT", os.getenv("PORT", 8000)))
    logger.info(f"Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
