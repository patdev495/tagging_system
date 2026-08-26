"""
Backward compatibility wrapper for UX SN Allocator.
All core logic is canonicalized under src.features.carton.a11_sn_allocator.
"""
from src.features.carton.a11_sn_allocator import (
    A11_SEQUENCE_WIDTH,
    UX_SEQUENCE_WIDTH,
    A11CartonSNPlan,
    UXCartonSNPlan,
    current_iso_date_code,
    current_yymm,
    format_a11_carton_sn,
    format_ux_carton_sn,
    parse_a11_sequence,
    parse_ux_sequence,
    next_a11_sequence,
    next_ux_sequence,
    plan_next_a11_carton_sn,
    plan_next_ux_carton_sn,
)

__all__ = [
    "A11_SEQUENCE_WIDTH",
    "UX_SEQUENCE_WIDTH",
    "A11CartonSNPlan",
    "UXCartonSNPlan",
    "current_iso_date_code",
    "current_yymm",
    "format_a11_carton_sn",
    "format_ux_carton_sn",
    "parse_a11_sequence",
    "parse_ux_sequence",
    "next_a11_sequence",
    "next_ux_sequence",
    "plan_next_a11_carton_sn",
    "plan_next_ux_carton_sn",
]
