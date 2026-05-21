import pytest
from unittest.mock import MagicMock, patch
from src.features.print import service
from src.core import models

def test_generate_btxml_standard():
    # Mock data
    product = models.Product(
        item_name="Test Product",
        upc="1234567890",
        packed_qty=10,
        template_type="standard"
    )
    carton = models.Carton(
        carton_sn="VN-11-2605001",
        carton_origin="VN"
    )
    items = ["SN001", "SN002"]
    
    # Mock template content
    mock_template = "<XML>{item_name} - {qty} - {carton_sn}</XML>"
    
    with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=mock_template)))))):
        with patch("os.path.exists", return_value=True):
            result = service.generate_btxml(carton, product, items, "dummy.btw")
            
    assert "Test Product" in result
    assert "2PCS" in result
    assert "VN-11-2605001" in result

def test_generate_btxml_detailed_sn_grid():
    # Mock data for detailed template
    product = models.Product(
        item_name="Detailed Product",
        upc="0987654321",
        packed_qty=30,
        template_type="detailed"
    )
    carton = models.Carton(
        carton_sn="CN-16-2605001",
        carton_origin="CN"
    )
    # Only 2 items scanned
    items = ["SN_A", "SN_B"]
    
    # Detailed template uses {sn_grid_tags}
    mock_template = "<XML>{sn_grid_tags}</XML>"
    
    with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=mock_template)))))):
        with patch("os.path.exists", return_value=True):
            result = service.generate_btxml(carton, product, items, "dummy.btw")
            
    # Check if SN_1 and SN_2 are present
    assert "SN_A" in result
    assert "SN_B" in result
    # Check if SN_3 is empty space (as per service.py logic)
    assert '<NamedSubString Name="SN_3"><Value> </Value></NamedSubString>' in result
    # Check if SN_30 is present
    assert '<NamedSubString Name="SN_30"><Value> </Value></NamedSubString>' in result

def test_origin_text_logic():
    product = models.Product(item_name="P", packed_qty=1)
    
    # VN Origin
    carton_vn = models.Carton(carton_origin="VN", carton_sn="S")
    with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value="{origin_text}")))))):
        with patch("os.path.exists", return_value=True):
            res_vn = service.generate_btxml(carton_vn, product, ["I"], "D")
            assert "MADE IN VIETNAM" in res_vn
            
    # CN Origin
    carton_cn = models.Carton(carton_origin="CN", carton_sn="S")
    with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value="{origin_text}")))))):
        with patch("os.path.exists", return_value=True):
            res_cn = service.generate_btxml(carton_cn, product, ["I"], "D")
            assert "MADE IN CHINA" in res_cn
