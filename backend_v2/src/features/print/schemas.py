from pydantic import BaseModel

class CartonStatusUpdate(BaseModel):
    status: str # SUCCESS or FAILED
