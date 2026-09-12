import pytest
from src.core.models import Product, Carton
from src.features.print.domain import BTXMLDocument


def test_erro_03_btxml_document_from_carton_data():
    product = Product(
        id=30,
        item_name="2M21-00508-0004H",
        packed_qty=190,
        pkg_prefix="1012665",
        product_desc="CAT5E ETHERNET CABLE",
        revision="/",
        template_type="erro_03",
        template_path=r"D:\PAT\Templates\erro_03.btw",
    )
    carton = Carton(
        id=50,
        product_id=30,
        carton_sn="10126652609110001",
        lot_number="92607933",
        packed_by="TSC_TTP_244_Pro",
    )

    doc = BTXMLDocument.from_carton_data(
        carton=carton,
        product=product,
        items=[],
        template_path=str(product.template_path or ""),
        printer_name="TSC_TTP_244_Pro",
    )

    # Verify all 12 Named SubStrings are present and mapped
    substrings = doc.substrings
    assert substrings["CartonSN"] == "10126652609110001"
    assert substrings["SupplierCode"] == "1012665"
    assert substrings["SupplierName"] == "NIENYI VIETNAM INDUSTRIAL COMPANY LIMITED"
    assert substrings["PartNo"] == "2M21-00508-0004H"
    assert substrings["APNRev"] == "/"
    assert substrings["LotNo"] == "92607933"
    assert substrings["QTY"] == "190"
    assert substrings["PartDesc"] == "CAT5E ETHERNET CABLE"
    assert substrings["Origin"] == "VIETNAM"
    assert "Andy Town/ Firefly" in substrings["ProjectStage"]
    assert "QB/CR" in substrings["ProjectStage"]
    assert len(substrings["Date"]) == 8  # YYYYMMDD
    
    # Verify QR Code content format
    expected_qr = f"10126652609110001$1012665$NIENYI VIETNAM INDUSTRIAL COMPANY LIMITED$2M21-00508-0004H$$92607933${substrings['Date']}$190$$$$$$"
    assert substrings["QRCode_Content"] == expected_qr

    # XML serialization test
    xml = doc.to_xml(template_type="erro_03")
    assert "<Format>D:\\PAT\\Templates\\erro_03.btw</Format>" in xml
    assert "<Printer>TSC_TTP_244_Pro</Printer>" in xml
    assert '<NamedSubString Name="CartonSN"><Value>10126652609110001</Value></NamedSubString>' in xml
    assert '<NamedSubString Name="PartNo"><Value>2M21-00508-0004H</Value></NamedSubString>' in xml
    assert f'<NamedSubString Name="QRCode_Content"><Value>{expected_qr}</Value></NamedSubString>' in xml

    # Parse back
    parsed = BTXMLDocument.from_xml(xml)
    assert parsed.substrings["CartonSN"] == "10126652609110001"
    assert parsed.substrings["PartNo"] == "2M21-00508-0004H"
    assert parsed.substrings["QRCode_Content"] == expected_qr
