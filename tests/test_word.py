import pytest
from mistaker import Word
from mistaker.constants import ErrorType


def test_reformat():
    word = Word()
    # Test mixed case
    assert word.reformat("GrAtEfUl") == "GRATEFUL"
    # Test with special characters
    assert word.reformat("Hello!@#$%^&*()") == "HELLO"
    # Test with spaces
    assert word.reformat("HELLO WORLD") == "HELLO WORLD"
    # Test with numbers
    assert word.reformat("ABC123") == "ABC"
    # Test empty string
    assert word.reformat("") == ""


def test_make_mistake_classmethod():
    """Test the class method interface"""
    result = Word.make_mistake("GRATEFUL")
    assert result != "GRATEFUL"
    assert isinstance(result, str)


def test_dropped_letter():
    word = Word("TESTING")
    result = word.mistake(ErrorType.DROPPED_LETTER, 1)
    assert result == "TSTING"
    assert len(result) == len("TESTING") - 1


def test_double_letter():
    word = Word("TESTING")
    result = word.mistake(ErrorType.DOUBLE_LETTER, 1)
    assert result == "TEESTING"
    assert len(result) == len("TESTING") + 1


def test_misread_letter():
    word = Word("TESTING")
    result = word.mistake(ErrorType.MISREAD_LETTER, 0)
    assert result != "TESTING"
    assert len(result) == len("TESTING")
    # Ensure the misread letter is from our mapping
    assert result[0] in "TESTING"


def test_mistyped_letter():
    word = Word("TESTING")
    result = word.mistake(ErrorType.MISTYPED_LETTER, 0)
    assert result != "TESTING"
    assert len(result) == len("TESTING")


def test_extra_letter():
    test_cases = [
        ("DRUM", "DRUMN"),
        ("CART", "CARTT"),
        ("CATALOG", "CATALOGUE"),
        ("TRAP", "TRAPH"),
        ("MATE", "MATES"),
        ("MAD", "MADT"),
        ("MAC", "MACE"),
        ("RAY", "RAYS"),
        ("TAZ", "TAZE"),
    ]
    word = Word()
    for input_str, expected in test_cases:
        word.text = input_str
        result = word.mistake(ErrorType.EXTRA_LETTER)
        assert result == expected


def test_misheard_letter():
    word = Word("TESTING")
    result = word.mistake(ErrorType.MISHEARD_LETTER, 0)
    assert result != "TESTING"


def test_empty_string():
    word = Word("")
    assert word.mistake() == ""


def test_single_character():
    word = Word("A")
    result = word.mistake()
    assert isinstance(result, str)
    assert len(result) in [0, 1, 2]  # Could be dropped, same, or doubled


def test_with_spaces():
    word = Word("HELLO WORLD")
    result = word.mistake()
    assert isinstance(result, str)
    assert " " in result  # Space should be preserved


def test_random_error_type():
    """Test that random error selection works"""
    word = Word("TESTING")
    results = set()
    # Run multiple times to ensure we get different errors
    for _ in range(50):
        results.add(word.mistake())
    # Should get multiple different results
    assert len(results) > 1


@pytest.mark.parametrize("invalid_input", [None, 123, 3.14, [], {}])
def test_invalid_input_types(invalid_input):
    """Test handling of invalid input types"""
    word = Word(invalid_input)
    result = word.mistake()
    assert isinstance(result, str)
