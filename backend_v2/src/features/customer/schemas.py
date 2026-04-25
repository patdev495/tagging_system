from pydantic import BaseModel
from typing import Optional

class CustomerBase(BaseModel):
    code: str
    name: str

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None

class Customer(CustomerBase):
    id: int

    class Config:
        from_attributes = True
