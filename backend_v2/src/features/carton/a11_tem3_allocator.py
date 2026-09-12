import datetime
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from src.core import models

DEFAULT_A11_TEM3_SUPPLIER_CODE = "1012665"
TEM3_SEQUENCE_WIDTH = 4


@dataclass(frozen=True)
class A11Tem3CartonPlan:
    supplier_code: str
    yymmdd: str
    sequence: int
    carton_sn: str


def format_a11_tem3_carton_sn(supplier_code: str, yymmdd: str, sequence: int) -> str:
    """
    Constructs full 17-character carton SN for A11 Tem 3 (Luxshare NME):
    supplier_code(7 chars) + yymmdd(6 chars) + sequence(4 digits)
    Example: '1012665' + '260911' + '0001' = '10126652609110001'
    """
    clean_code = "".join(c for c in str(supplier_code) if c.isdigit()) or DEFAULT_A11_TEM3_SUPPLIER_CODE
    seq_str = str(sequence).zfill(TEM3_SEQUENCE_WIDTH)
    return f"{clean_code}{yymmdd}{seq_str}"


def parse_a11_tem3_sequence(carton_sn: Optional[str], supplier_code: str, yymmdd: str) -> int:
    """
    Extracts the 4-digit sequence number from a 17-character Tem 3 carton SN.
    Format: supplier_code(7) + yymmdd(6) + sequence(4)
    """
    if not carton_sn:
        return 0
    clean_sn = "".join(c for c in carton_sn if c.isdigit())
    clean_code = "".join(c for c in str(supplier_code) if c.isdigit()) or DEFAULT_A11_TEM3_SUPPLIER_CODE
    prefix = f"{clean_code}{yymmdd}"
    if not clean_sn.startswith(prefix) or len(clean_sn) != (len(clean_code) + len(yymmdd) + TEM3_SEQUENCE_WIDTH):
        return 0

    seq_part = clean_sn[len(prefix) : len(prefix) + TEM3_SEQUENCE_WIDTH]
    try:
        return int(seq_part)
    except ValueError:
        return 0


def next_a11_tem3_sequence(db: Session, supplier_code: str, yymmdd: str, lock: bool = False) -> int:
    """
    Finds the maximum sequence allocated in the day `yymmdd` for the given supplier_code.
    Sequence starts from 1 (0001) and resets daily.
    """
    clean_code = "".join(c for c in str(supplier_code) if c.isdigit()) or DEFAULT_A11_TEM3_SUPPLIER_CODE
    lead_prefix = f"{clean_code}{yymmdd}"

    query = db.query(models.Carton.carton_sn).filter(
        models.Carton.carton_sn.like(f"{lead_prefix}%"),
        models.Carton.is_reprint == 0,
    )
    if lock:
        query = query.with_for_update()

    rows = query.all()
    if not rows:
        return 1

    max_seq = 0
    for r in rows:
        seq = parse_a11_tem3_sequence(r[0], clean_code, yymmdd)
        if seq > max_seq:
            max_seq = seq

    return max_seq + 1


def plan_next_a11_tem3_carton_sn(
    db: Session,
    product: models.Product,
    custom_yymmdd: Optional[str] = None,
    custom_sequence: Optional[int] = None,
    lock: bool = False,
) -> A11Tem3CartonPlan:
    """
    Allocates the next Tem 3 carton SN plan for a product.
    """
    supplier_code = getattr(product, 'pkg_prefix', None) or DEFAULT_A11_TEM3_SUPPLIER_CODE
    clean_code = "".join(c for c in str(supplier_code) if c.isdigit()) or DEFAULT_A11_TEM3_SUPPLIER_CODE

    if custom_yymmdd:
        yymmdd = custom_yymmdd
    else:
        now = datetime.datetime.now()
        yymmdd = now.strftime("%y%m%d")

    if custom_sequence is not None and custom_sequence > 0:
        sequence = custom_sequence
    else:
        sequence = next_a11_tem3_sequence(db, clean_code, yymmdd, lock=lock)

    carton_sn = format_a11_tem3_carton_sn(clean_code, yymmdd, sequence)

    return A11Tem3CartonPlan(
        supplier_code=clean_code,
        yymmdd=yymmdd,
        sequence=sequence,
        carton_sn=carton_sn,
    )
