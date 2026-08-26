import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.models import Base, Customer, Product, Carton
from src.features.print.service import reprint_carton
from src.features.carton.a11_sn_allocator import plan_next_a11_carton_sn


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def a11_product(db_session):
    customer = Customer(code="A11", name="Customer A11")
    db_session.add(customer)
    db_session.flush()

    product = Product(
        customer_id=customer.id,
        item_name="840-00092",
        packed_qty=190,
        packing_mode="weight_scale",
        target_weight=12.500,
        min_weight=12.300,
        max_weight=12.700,
        weight_unit="kg",
        mfr_pn="NYS5998",
        pkg_prefix="VHK0010237",
        revision="B",
        template_type="a11",
        template_path=r"D:\PAT\Template\第1.btw",
    )
    db_session.add(product)
    db_session.commit()
    return product


def test_reprint_a11_carton_preserves_all_metadata(db_session, a11_product):
    # 1. Create original A11 carton
    orig = Carton(
        product_id=a11_product.id,
        carton_sn="VHK00102372608000081",
        weight=12.480,
        po_number="PO-ORIG-100",
        lot_number="LOT-ORIG-200",
        date_code="2634",
        status="SUCCESS",
        carton_origin="VN",
        packed_by="TSC_TTP_244_Pro",
        is_reprint=0,
    )
    db_session.add(orig)
    db_session.commit()
    db_session.refresh(orig)

    # 2. Execute reprint
    reprinted = reprint_carton(
        carton_id=orig.id,
        printer_name="TSC_TTP_244_Pro",
        db=db_session,
    )

    assert reprinted.id != orig.id
    assert reprinted.carton_sn == "VHK00102372608000081"
    assert reprinted.is_reprint == 1
    assert reprinted.weight == 12.480
    assert reprinted.po_number == "PO-ORIG-100"
    assert reprinted.lot_number == "LOT-ORIG-200"
    assert reprinted.date_code == "2634"
    assert reprinted.btxml is not None
    assert "<NamedSubString Name=\"CPN\"><Value>840-00092</Value></NamedSubString>" in reprinted.btxml
    assert "<NamedSubString Name=\"PONo\"><Value>PO-ORIG-100</Value></NamedSubString>" in reprinted.btxml
    assert "<NamedSubString Name=\"LotNo\"><Value>LOT-ORIG-200</Value></NamedSubString>" in reprinted.btxml
    assert "<NamedSubString Name=\"DateCode\"><Value>2634</Value></NamedSubString>" in reprinted.btxml
    assert "<NamedSubString Name=\"CartonSN\"><Value>VHK00102372608000081</Value></NamedSubString>" in reprinted.btxml

    # 3. Verify sequence allocator was NOT incremented by the reprint
    next_plan = plan_next_a11_carton_sn(db_session, a11_product, custom_yymm="2608")
    assert next_plan.sequence == 82
    assert next_plan.carton_sn == "VHK00102372608000082"
