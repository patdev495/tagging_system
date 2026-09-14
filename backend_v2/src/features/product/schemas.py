from datetime import datetime
from pydantic import BaseModel, model_validator, field_validator
from typing import Optional, List


class InternalFactoryPartNumberBase(BaseModel):
    internal_factory_part_number: str
    source_drawing_code: str

    @field_validator("internal_factory_part_number")
    @classmethod
    def validate_and_normalize_part_number(cls, v: str) -> str:
        val = (v or "").strip().upper()
        if not val:
            raise ValueError("Factory P/N cannot be empty")
        return val

    @field_validator("source_drawing_code")
    @classmethod
    def validate_and_normalize_drawing_code(cls, v: str) -> str:
        val = (v or "").strip().upper()
        if not val:
            raise ValueError("source_drawing_code cannot be empty")
        return val


class InternalFactoryPartNumberCreate(InternalFactoryPartNumberBase):
    pass


class InternalFactoryPartNumberBatchCreate(BaseModel):
    items: List[InternalFactoryPartNumberCreate]


class InternalFactoryPartNumberOut(InternalFactoryPartNumberBase):
    id: int
    product_id: int
    customer_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    item_name: str
    upc: Optional[str] = None
    packed_qty: int
    start_part: Optional[str] = "VN"
    middle_part: Optional[str] = ""
    template_type: Optional[str] = "standard"
    template_path: Optional[str] = None
    allow_partial: Optional[int] = 0
    customer_id: int
    packing_mode: Optional[str] = "item_scan"
    target_weight: Optional[float] = None
    min_weight: Optional[float] = None
    max_weight: Optional[float] = None
    weight_unit: Optional[str] = "kg"
    mfr_pn: Optional[str] = None
    pkg_prefix: Optional[str] = None
    revision: Optional[str] = None
    asin: Optional[str] = None
    product_desc: Optional[str] = None
    customer_project: Optional[str] = None
    production_stage: Optional[str] = None
    luxshare_part_number: Optional[str] = None
    internal_factory_part_number: Optional[str] = None
    factory_item_code: Optional[str] = None
    carton_id_prefix: Optional[str] = None

    @model_validator(mode="after")
    def validate_label_metadata(self):
        if self.template_type == "erro_03":
            required = {
                "customer_project": self.customer_project,
                "production_stage": self.production_stage,
                "luxshare_part_number": self.luxshare_part_number,
            }
            missing = [name for name, value in required.items() if not (value or "").strip()]
            if missing:
                raise ValueError(f"Erro 03 Product requires: {', '.join(missing)}")
            return self

        if self.template_type != "erro_04":
            return self

        required = {
            "upc": self.upc,
            "mfr_pn": self.mfr_pn,
            "product_desc": self.product_desc,
            "factory_item_code": self.factory_item_code,
            "revision": self.revision,
        }
        missing = [name for name, value in required.items() if not (value or "").strip()]
        if missing:
            raise ValueError(f"Erro 04 Product requires: {', '.join(missing)}")

        prefix = (self.carton_id_prefix or "").strip().upper()
        if prefix not in {"H", "K"}:
            raise ValueError("Erro 04 Product requires carton_id_prefix H or K")
        if self.packing_mode != "weight_scale":
            raise ValueError("Erro 04 Product requires weight_scale packing_mode")
        return self


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    item_name: Optional[str] = None
    upc: Optional[str] = None
    packed_qty: Optional[int] = None
    start_part: Optional[str] = None
    middle_part: Optional[str] = None
    template_type: Optional[str] = None
    template_path: Optional[str] = None
    allow_partial: Optional[int] = None
    customer_id: Optional[int] = None
    packing_mode: Optional[str] = None
    target_weight: Optional[float] = None
    min_weight: Optional[float] = None
    max_weight: Optional[float] = None
    weight_unit: Optional[str] = None
    mfr_pn: Optional[str] = None
    pkg_prefix: Optional[str] = None
    revision: Optional[str] = None
    asin: Optional[str] = None
    product_desc: Optional[str] = None
    customer_project: Optional[str] = None
    production_stage: Optional[str] = None
    luxshare_part_number: Optional[str] = None
    internal_factory_part_number: Optional[str] = None
    factory_item_code: Optional[str] = None
    carton_id_prefix: Optional[str] = None


class Product(ProductBase):
    id: int
    internal_factory_part_numbers: List[InternalFactoryPartNumberOut] = []

    class Config:
        from_attributes = True
