import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.models import Base, Customer, Product, Carton

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_product_model_has_a11_fields(db_session):
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
        template_type="a11"
    )
    db_session.add(product)
    db_session.commit()

    saved = db_session.query(Product).filter(Product.item_name == "840-00092").first()
    assert saved is not None
    assert saved.packing_mode == "weight_scale"
    assert saved.target_weight == 12.500
    assert saved.min_weight == 12.300
    assert saved.max_weight == 12.700
    assert saved.weight_unit == "kg"
    assert saved.mfr_pn == "NYS5998"
    assert saved.pkg_prefix == "VHK0010237"
    assert saved.revision == "B"

def test_carton_model_has_a11_weight_fields(db_session):
    customer = Customer(code="A11", name="Customer A11")
    db_session.add(customer)
    db_session.flush()

    product = Product(
        customer_id=customer.id,
        item_name="840-00083",
        packed_qty=190,
        packing_mode="weight_scale"
    )
    db_session.add(product)
    db_session.flush()

    carton = Carton(
        product_id=product.id,
        carton_sn="VHK00102372608000001",
        weight=12.480,
        po_number="B432-22156381",
        lot_number="92608521",
        date_code="2634",
        status="SUCCESS"
    )
    db_session.add(carton)
    db_session.commit()

    saved_carton = db_session.query(Carton).filter(Carton.carton_sn == "VHK00102372608000001").first()
    assert saved_carton is not None
    assert saved_carton.weight == 12.480
    assert saved_carton.po_number == "B432-22156381"
    assert saved_carton.lot_number == "92608521"
    assert saved_carton.date_code == "2634"

def test_ui_customer_backward_compatibility(db_session):
    # Existing UI product without weight fields should default cleanly
    ui_customer = Customer(code="UI", name="Ubiquiti")
    db_session.add(ui_customer)
    db_session.flush()

    ui_product = Product(
        customer_id=ui_customer.id,
        item_name="U-Cable-Patch-RJ45-50",
        upc="810010074102",
        packed_qty=12,
        start_part="CN",
        middle_part="11",
        template_type="standard"
    )
    db_session.add(ui_product)
    db_session.commit()

    saved_ui = db_session.query(Product).filter(Product.item_name == "U-Cable-Patch-RJ45-50").first()
    assert saved_ui is not None
    assert saved_ui.packing_mode == "item_scan"
    assert saved_ui.target_weight is None

def test_seed_a11_data(db_session):
    from src.core.database import seed_a11_data
    seed_a11_data(db_session)

    a11 = db_session.query(Customer).filter(Customer.code == "A11").first()
    assert a11 is not None

    prods = db_session.query(Product).filter(Product.customer_id == a11.id).all()
    assert len(prods) == 5
    tem1_prods = [p for p in prods if p.template_type == "a11"]
    assert len(tem1_prods) == 3
    tem1_names = {p.item_name for p in tem1_prods}
    assert tem1_names == {"840-00083", "840-00091", "840-00092"}
    for p in tem1_prods:
        assert p.packed_qty == 190
        assert p.pkg_prefix == "VHK0010237"
        assert p.mfr_pn == "NYS5998"
        assert p.packing_mode == "weight_scale"

    tem2_prods = [p for p in prods if p.template_type == "a11_tem2"]
    assert len(tem2_prods) == 2
    tem2_names = {p.item_name for p in tem2_prods}
    assert tem2_names == {"G012C1B", "G112C1B"}
