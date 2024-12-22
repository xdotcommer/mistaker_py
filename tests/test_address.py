from unittest.mock import patch
import pytest
from mistaker import Address
from mistaker.constants import ErrorType
from mistaker.number import Number
from mistaker.word import Word
from mistaker.address import STREET_SUFFIXES


def test_init():
    """Test address initialization"""
    address = Address("123 Main St")
    assert address.text == "123 Main St"

    address = Address(None)
    assert address.text == ""

    address = Address("")
    assert address.text == ""


def test_mistake():
    """Test basic mistake generation"""
    address = Address("123 Main St")
    with patch(
        "mistaker.address.random.random", return_value=0.9
    ):  # Always keep suffix
        result = address.mistake()
        assert result != "123 Main St"
        assert isinstance(result, str)
        assert len(result.split()) == len("123 Main St".split())


def test_number_mistakes():
    """Test numeric component handling"""
    address = Address("123 Main St")

    # Test number modification
    with patch(
        "mistaker.address.random.random", side_effect=[0.9, 0.2]
    ):  # Keep suffix, modify number
        result = address.mistake()
        assert result.split()[0] != "123"

    # Test number preservation
    with patch(
        "mistaker.address.random.random", side_effect=[0.9, 0.8]
    ):  # Keep suffix, preserve number
        result = address.mistake()
        assert result.split()[0] == "123"


def test_word_mistakes():
    """Test word component handling"""
    address = Address("123 Main St")

    with patch.object(Word, "mistake", return_value="STREET") as mock_word:
        result = address.mistake()
        assert mock_word.called
        assert "STREET" in result


def test_empty_address():
    """Test empty input handling"""
    address = Address("")
    assert address.mistake() == ""

    address = Address(None)
    assert address.mistake() == ""


def test_mixed_components():
    """Test handling of mixed numeric and text components"""
    address = Address("123 Main St 45B")

    # Simple validation that mixed components are handled
    result = address.mistake()
    parts = result.split()

    # Basic assertions about structure
    assert len(parts) >= 3  # Should have at least 3 parts
    assert any(
        part.isdigit() or (part.isalnum() and not part.isalpha()) for part in parts
    )  # Should contain numbers or alphanumeric
    assert any(part.isalpha() for part in parts)  # Should contain words


@pytest.mark.parametrize(
    "error_type",
    [
        ErrorType.DROPPED_LETTER,
        ErrorType.DOUBLE_LETTER,
        ErrorType.MISREAD_LETTER,
    ],
)
def test_specific_error_types(error_type):
    """Test specific error type handling"""
    address = Address("123 Main St")
    result = address.mistake(error_type=error_type)
    assert result != "123 Main St"
    assert isinstance(result, str)


def test_suffix_dropping():
    """Test that street suffixes can be dropped"""
    address = Address("123 Main St")

    # Force suffix dropping
    with patch("mistaker.address.random.random", return_value=0.1):
        result = address.mistake()
        assert len(result.split()) == 2
        assert "ST" not in result

    # Force suffix keeping
    with patch("mistaker.address.random.random", return_value=0.9):
        result = address.mistake()
        assert len(result.split()) == 3
        assert result.split()[-1] in STREET_SUFFIXES
