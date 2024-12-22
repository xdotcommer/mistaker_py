import pytest
from mistaker import Address
from mistaker.constants import ErrorType


def test_parse_address():
    """Test basic address parsing"""
    address = Address("123 N Main St, Portland, OR 97201")
    assert address.components["number"] == "123"
    assert address.components["pre_direction"] == "N"
    assert address.components["street_name"] == "MAIN"
    assert address.components["street_type"] == "ST"


def test_get_variations():
    """Test basic variation generation"""
    address = Address("123 N Main St")
    variations = address.get_variations()
    assert "123 N MAIN ST" in variations
    assert "123 N MAIN STREET" in variations


def test_standardize():
    """Test basic address standardization"""
    address = Address("123 N Main St, Portland, OR 97201")
    assert address.standardize() == "123 N MAIN ST, PORTLAND, OR 97201"


def test_empty_address():
    """Test empty address handling"""
    address = Address("")
    assert address.standardize() == ""


def test_invalid_address():
    """Test invalid address handling"""
    address = Address(None)
    assert address.standardize() == ""
    address = Address(123)
    assert address.standardize() == ""


@pytest.mark.parametrize(
    "error_type",
    [
        ErrorType.DROPPED_LETTER,
        ErrorType.DOUBLE_LETTER,
        ErrorType.MISREAD_LETTER,
        ErrorType.MISTYPED_LETTER,
        ErrorType.EXTRA_LETTER,
        ErrorType.MISHEARD_LETTER,
    ],
)
def test_specific_error_types(error_type):
    """Test each error type"""
    address = Address("123 Main Street")
    result = address.mistake(error_type)
    assert isinstance(result, str)
