from sqlalchemy.orm import Session
from src.core import models
from . import schemas

def get_all_customers(db: Session):
    return db.query(models.Customer).all()
