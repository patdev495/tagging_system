from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UnicodeText
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True)
    name = Column(String(200))
    
    products = relationship("Product", back_populates="customer")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)
    item_name = Column(String(200), index=True)
    upc = Column(String(50))
    packed_qty = Column(Integer)
    start_part = Column(String(10)) # E.g., CN (Carton Number)
    middle_part = Column(String(20)) # e.g. 11, 16, A, B
    template_type = Column(String(50), default="standard") # "standard" | "detailed"
    template_path = Column(String(500), nullable=True) # E.g. D:\PAT\Template\carton.btw
    allow_partial = Column(Integer, default=0) # 0 = must be full | 1 = can be partial
    
    customer = relationship("Customer", back_populates="products")
    cartons = relationship("Carton", back_populates="product")

class Carton(Base):
    __tablename__ = "cartons"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    carton_sn = Column(String(100), index=True) # Removed unique=True to allow print attempt logs
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None), index=True)
    packed_by = Column(String(100), nullable=True)
    job_order = Column(String(100), nullable=True, index=True)
    status = Column(String(20), default="FAILED", index=True) # SUCCESS or FAILED
    btxml = Column(UnicodeText, nullable=True) # Stores original print data
    is_reprint = Column(Integer, default=0) # 0 for Original, 1 for Reprint
    carton_origin = Column(String(50), default="VN") # Origin country, e.g. CN (China) or VN (Vietnam)
    station_id = Column(String(50), nullable=True) # Station ID derived from MAC address
    
    product = relationship("Product", back_populates="cartons")
    items = relationship("CartonItem", back_populates="carton")

class CartonItem(Base):
    __tablename__ = "carton_items"
    
    id = Column(Integer, primary_key=True, index=True)
    carton_id = Column(Integer, ForeignKey("cartons.id"), index=True)
    item_sn = Column(String(100), index=True)
    
    carton = relationship("Carton", back_populates="items")
