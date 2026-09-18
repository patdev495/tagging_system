from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from src.core.database import Base, get_db
from src.core.models import Customer, Product
from src.features.auth.service import seed_default_users


def _client_with_erro_product():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine)

    setup_db = testing_session()
    seed_default_users(setup_db)
    erro = Customer(code="ERRO", name="Erro")
    setup_db.add(erro)
    setup_db.flush()
    product = Product(
        customer_id=erro.id,
        item_name="840-00083",
        packed_qty=190,
        packing_mode="weight_scale",
        template_type="erro_01",
        template_path="erro_01.btw",
        pkg_prefix="VHK0010237",
        mfr_pn="NYS5998",
        revision="B",
        min_weight=12.3,
        max_weight=12.7,
        target_weight=12.5,
    )
    setup_db.add(product)
    setup_db.commit()
    product_id = product.id
    setup_db.close()

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), product_id


def test_admin_can_create_erro_carton_with_requested_sequence_and_audit():
    client, product_id = _client_with_erro_product()
    try:
        token = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"}).json()["access_token"]

        response = client.post(
            "/api/v1/cartons/admin-create",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "product_id": product_id,
                "sequence": 725,
                "reason": "Bổ sung lịch sử tem",
                "weight": 12.5,
                "job_order": "JO-2026-001",
                "lot_number": "LOT-01",
                "po_number": "PO-01",
                "printer_name": "Zebra",
            },
        )

        assert response.status_code == 200, response.text
        carton = response.json()
        assert carton["carton_sn"] == "VHK00102372609000725"
        assert carton["station_id"] == "ADMIN"
        assert carton["packed_by"] == "admin"
        assert carton["admin_creation_reason"] == "Bổ sung lịch sử tem"
        assert carton["status"] == "FAILED"
        assert "erro_01.btw" in carton["btxml"]
    finally:
        app.dependency_overrides.clear()


def test_admin_carton_requires_a_job_order():
    client, product_id = _client_with_erro_product()
    try:
        token = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"}).json()["access_token"]
        response = client.post(
            "/api/v1/cartons/admin-create",
            headers={"Authorization": f"Bearer {token}"},
            json={"product_id": product_id, "sequence": 726, "reason": "Bổ sung lịch sử", "weight": 12.5},
        )
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
