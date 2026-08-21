import pytest
from src.core.models import Product, Carton
from src.features.print.domain import BTXMLDocument


def test_a11_btxml_document_from_carton_data():
    product = Product(
        id=1,
        item_name="840-00083",
        packed_qty=190,
        mfr_pn="NYS5998",
        revision="B",
        template_type="a11",
        template_path=r"D:\PAT\Template\第1.btw",
    )
    carton = Carton(
        id=10,
        product_id=1,
        carton_sn="VHK00102372608000081",
        po_number="B432-22156381",
        lot_number="92608521",
        date_code="2634",
        carton_origin="VN",
        packed_by="TSC_TTP_244_Pro",
    )

    doc = BTXMLDocument.from_carton_data(
        carton=carton,
        product=product,
        items=[],
        template_path=product.template_path,
        printer_name="TSC_TTP_244_Pro",
    )

    assert doc.substrings["CPN"] == "840-00083"
    assert doc.substrings["QTY"] == "190"
    assert doc.substrings["MfrPN"] == "NYS5998"
    assert doc.substrings["DateCode"] == "2634"
    assert doc.substrings["LotNo"] == "92608521"
    assert doc.substrings["PONo"] == "B432-22156381"
    assert doc.substrings["CartonSN"] == "VHK00102372608000081"
    assert doc.substrings["Rev"] == "B"
    assert doc.substrings["Origin"] == "MADE IN VIETNAM"
    
    # 2D QR Code formatted with P, Q, M, D, L, K, S prefixes comma separated
    expected_qr = "P840-00083,Q190,MNYS5998,D2634,L92608521,KB432-22156381,SVHK00102372608000081"
    assert doc.substrings["QR_Content"] == expected_qr

    # XML serialization test
    xml = doc.to_xml(template_type="a11")
    assert "<Format>D:\\PAT\\Template\\第1.btw</Format>" in xml
    assert "<Printer>TSC_TTP_244_Pro</Printer>" in xml
    assert '<NamedSubString Name="CPN"><Value>840-00083</Value></NamedSubString>' in xml
    assert '<NamedSubString Name="CartonSN"><Value>VHK00102372608000081</Value></NamedSubString>' in xml
    assert f'<NamedSubString Name="QR_Content"><Value>{expected_qr}</Value></NamedSubString>' in xml
