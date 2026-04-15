import pytest
import sys
import os
from unittest.mock import MagicMock, patch

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "../src/date-server"))

with patch.dict("sys.modules", {
    "kafka_helper": MagicMock(),
}):
    from date_server import get_current_date


def test_get_current_date_returns_iso_format():
    date_str = get_current_date()
    assert isinstance(date_str, str)
    assert "T" in date_str


def test_get_current_date_contains_timezone_info():
    date_str = get_current_date()
    assert "+" in date_str or "Z" in date_str or "+00:00" in date_str
