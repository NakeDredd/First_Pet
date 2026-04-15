import pytest
import sys
import os
from unittest.mock import MagicMock, patch, Mock
from queue import Queue

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "../src/timezone-converter"))


def test_convert_to_moscow():
    with patch.dict("sys.modules", {"kafka_helper": MagicMock()}):
        from timezone_converter import convert_to_moscow

        input_date = "2024-01-20T15:30:00+07:00"
        result = convert_to_moscow(input_date)

        assert isinstance(result, str)
        assert "T" in result
        assert "+03:00" in result
