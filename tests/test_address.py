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
    result = address.mistake()
    assert result != "123 Main St"
    assert isinstance(result, str)
    assert len(result.split()) == len("123 Main St".split())


def test_number_mistakes():
    """Test numeric component handling with 1/3 chance"""
    address = Address("123 Main St")

    # Test number modification (random < 0.33)
    with patch("random.random", side_effect=[0.9, 0.2]):  # Keep suffix, modify number
        result = address.mistake()
        assert result.split()[0] != "123"

    # Test number preservation (random >= 0.33)
    with patch("random.random", side_effect=[0.9, 0.5]):  # Keep suffix, preserve number
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

    # Test number modification path - need THREE random values:
    # 1. Suffix decision (0.9 = keep)
    # 2. First number decision (0.2 = modify)
    # 3. Second number decision (0.9 = keep)
    with patch("random.random", side_effect=[0.9, 0.2, 0.9]):
        result = address.mistake()
        parts = result.split()
        assert parts[0] != "123"  # Number modified
        assert "45B" in parts  # Mixed preserved
        assert len(parts) == 4  # All parts present

    # Test number preservation path
    with patch("random.random", side_effect=[0.9, 0.5, 0.9]):
        result = address.mistake()
        parts = result.split()
        assert parts[0] == "123"  # Number preserved
        assert "45B" in parts  # Mixed preserved
        assert len(parts) == 4  # All parts present


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

    # Force suffix dropping by patching random
    with patch("random.random", return_value=0.1):
        result = address.mistake()
        assert len(result.split()) == 2
        assert "ST" not in result

    # Force suffix keeping by patching random
    with patch("random.random", return_value=0.9):
        result = address.mistake()
        assert len(result.split()) == 3
        assert result.split()[-1] in STREET_SUFFIXES
