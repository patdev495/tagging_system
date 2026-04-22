from pydantic import BaseModel

class CustomerBase(BaseModel):
    code: str
    name: str

class Customer(CustomerBase):
    id: int
    
    class Config:
        from_attributes = True
