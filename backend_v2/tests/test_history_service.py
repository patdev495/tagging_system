"""
Tests for History Service — carton search and lookup logic.
"""
import pytest
from unittest.mock import MagicMock, PropertyMock
# pyrefly: ignore [missing-import]
from src.core import models
# pyrefly: ignore [missing-import]
from src.features.history import service
# pyrefly: ignore [missing-import]
from fastapi import HTTPException


class TestGetCartonDetail:
    """Test carton detail retrieval."""

    def test_returns_carton_with_items_count(self):
        """Should set items_count on the returned carton."""
        mock_item1 = models.CartonItem(id=1, item_sn="SN001")
        mock_item2 = models.CartonItem(id=2, item_sn="SN002")
        mock_carton = models.Carton(id=1, carton_sn="VN26051100001")
        mock_carton.items = [mock_item1, mock_item2]
        mock_carton.product = models.Product(id=1, item_name="Test")

        db = MagicMock()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_carton

        result = service.get_carton_detail(db, 1)
        assert result.items_count == 2

    def test_raises_404_when_not_found(self):
        """Should raise 404 when carton doesn't exist."""
        db = MagicMock()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            service.get_carton_detail(db, 999)
        assert exc.value.status_code == 404


class TestSearchCartonBySN:
    """Test search by carton S/N."""

    def test_raises_404_when_sn_not_found(self):
        """Should raise 404 for non-existing carton S/N."""
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            service.search_carton_by_sn("NONEXISTENT", db)
        assert exc.value.status_code == 404


class TestSearchByItemSN:
    """Test search by item S/N (find which carton contains an item)."""

    def test_raises_404_when_item_sn_not_found(self):
        """Should raise 404 when item S/N doesn't exist in any carton."""
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            service.search_by_item_sn("UNKNOWN_ITEM", db)
        assert exc.value.status_code == 404


class TestDeleteCarton:
    """Test carton deletion."""

    def test_deletes_carton_and_items(self):
        """Should delete carton items first, then the carton itself."""
        mock_carton = models.Carton(id=1, carton_sn="VN26051100001")
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_carton

        result = service.delete_carton(db, 1)

        assert result["message"] == "Carton deleted successfully"
        db.delete.assert_called_once_with(mock_carton)
        db.commit.assert_called_once()

    def test_raises_404_when_deleting_nonexistent(self):
        """Should raise 404 when trying to delete a carton that doesn't exist."""
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            service.delete_carton(db, 999)
        assert exc.value.status_code == 404


class TestGetCartons:
    """Test carton listing with filters."""

    def test_returns_total_and_items(self):
        """Should return dict with total count and items list."""
        mock_carton = models.Carton(id=1, carton_sn="VN26051100001")
        mock_carton.product = models.Product(id=1, item_name="Test")

        db = MagicMock()
        query = db.query.return_value.options.return_value
        query.count.return_value = 1
        query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_carton]

        result = service.get_cartons(db)
        assert result["total"] == 1
        assert len(result["items"]) == 1

    def test_applies_search_filter(self):
        """Should apply LIKE filter when search is provided."""
        db = MagicMock()
        query = db.query.return_value.options.return_value
        filter_query = query.filter.return_value
        filter_query.count.return_value = 0
        filter_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = service.get_cartons(db, search="VN2605")
        # Verify filter was called (search applied)
        query.filter.assert_called()

    def test_applies_status_filter(self):
        """Should filter by status when provided."""
        db = MagicMock()
        query = db.query.return_value.options.return_value
        filter_query = query.filter.return_value
        filter_query.count.return_value = 0
        filter_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = service.get_cartons(db, status="SUCCESS")
        query.filter.assert_called()
