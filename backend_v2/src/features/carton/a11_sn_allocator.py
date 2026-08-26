import datetime
import re
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from src.core import models


A11_SEQUENCE_WIDTH = 6
UX_SEQUENCE_WIDTH = A11_SEQUENCE_WIDTH


@dataclass(frozen=True)
class A11CartonSNPlan:
    prefix: str
    yymm: str
    sequence: int
    carton_sn: str
    date_code: str


UXCartonSNPlan = A11CartonSNPlan


def current_iso_date_code() -> str:
    """Returns ISO Date Code in standard YYWW format (e.g., 2634 for Week 34 of 2026)."""
    now = datetime.datetime.now()
    yy = now.strftime("%y")
    ww = f"{now.isocalendar()[1]:02d}"
    return f"{yy}{ww}"


def current_yymm() -> str:
    return datetime.datetime.now().strftime("%y%m")


def format_a11_carton_sn(pkg_prefix: str, yymm: str, sequence: int) -> str:
    return f"{pkg_prefix}{yymm}{str(sequence).zfill(A11_SEQUENCE_WIDTH)}"


format_ux_carton_sn = format_a11_carton_sn


def parse_a11_sequence(carton_sn: Optional[str]) -> int:
    if not carton_sn:
        return 0
    sequence_text = carton_sn[-A11_SEQUENCE_WIDTH:]
    if not re.fullmatch(r"\d+", sequence_text):
        return 0
    try:
        return int(sequence_text)
    except ValueError:
        return 0


parse_ux_sequence = parse_a11_sequence


def next_a11_sequence(db: Session, pkg_prefix: str, yy: str, lock: bool = False) -> int:
    """
    Finds the maximum sequence allocated in the given year (YY) for the specified pkg_prefix.
    Resets to 1 if no cartons exist for that year.
    """
    query = db.query(models.Carton.carton_sn).filter(
        models.Carton.carton_sn.like(f"{pkg_prefix}{yy}%"),
        models.Carton.is_reprint == 0,
    )
    if lock:
        query = query.with_for_update()
    
    rows = query.all()
    if not rows:
        return 1
    
    max_seq = max(parse_a11_sequence(r[0]) for r in rows)
    return max_seq + 1


next_ux_sequence = next_a11_sequence


def plan_next_a11_carton_sn(
    db: Session,
    product: models.Product,
    custom_yymm: Optional[str] = None,
    custom_sequence: Optional[int] = None,
    lock: bool = False,
) -> A11CartonSNPlan:
    pkg_prefix = product.pkg_prefix or product.start_part or "VHK0010237"
    yymm = custom_yymm or current_yymm()
    yy = yymm[:2]
    
    if custom_sequence is not None and custom_sequence > 0:
        sequence = custom_sequence
    else:
        sequence = next_a11_sequence(db, pkg_prefix=pkg_prefix, yy=yy, lock=lock)

    carton_sn = format_a11_carton_sn(pkg_prefix, yymm, sequence)
    date_code = current_iso_date_code()
    
    return A11CartonSNPlan(
        prefix=pkg_prefix,
        yymm=yymm,
        sequence=sequence,
        carton_sn=carton_sn,
        date_code=date_code,
    )


plan_next_ux_carton_sn = plan_next_a11_carton_sn
