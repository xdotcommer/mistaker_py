import pytest
from mistaker import Number
from mistaker.constants import ErrorType


def test_reformat():
    number = Number()
    # Test with mixed input
    assert number.reformat("123abc456") == "123456"
    # Test with special characters
    assert number.reformat("12!@#$%^&*()34") == "1234"
    # Test with spaces
    assert number.reformat("123 456") == "123456"
    # Test with empty string
    assert number.reformat("") == ""
    # Test with non-numeric string
    assert number.reformat("abc") == ""


def test_make_mistake_classmethod():
    """Test the class method interface"""
    result = Number.make_mistake("2018122")
    assert result != "2018122"
    assert isinstance(result, str)
    assert result.isdigit()


def test_one_digit_up():
    test_cases = [
        ("198012", 5, "198013"),
        ("201005", 0, "301005"),
        ("28122", 2, "28222"),
    ]
    number = Number()
    for input_str, index, expected in test_cases:
        number.text = input_str
        result = number.mistake(ErrorType.ONE_DIGIT_UP, index)
        assert result == expected


def test_one_digit_down():
    test_cases = [
        ("198012", 5, "198011"),
        ("201005", 0, "101005"),
        ("28122", 2, "28022"),
    ]
    number = Number()
    for input_str, index, expected in test_cases:
        number.text = input_str
        result = number.mistake(ErrorType.ONE_DIGIT_DOWN, index)
        assert result == expected


def test_key_swap():
    test_cases = [
        ("2006780", 4, "2007680"),
        ("12345", 0, "21345"),
        ("12345", 4, "12354"),
    ]
    number = Number()
    for input_str, index, expected in test_cases:
        number.text = input_str
        result = number.mistake(ErrorType.KEY_SWAP, index)
        assert result == expected


def test_digit_shift():
    test_cases = [
        ("12345", 2, "00123"),
        ("01234", 2, "00012"),
        ("45645", 8, "00000"),
        ("45645", 4, "00004"),
    ]
    number = Number()
    for input_str, index, expected in test_cases:
        number.text = input_str
        result = number.mistake(ErrorType.DIGIT_SHIFT, index)
        assert result == expected


def test_misread():
    test_cases = [
        ("010012", 5, "010015"),
        ("010009", 5, "010004"),
        ("010023", 5, "010028"),
        ("942021", 1, "992021"),
        ("925021", 1, "955021"),
        ("005021", 1, "085021"),
    ]
    number = Number()
    for input_str, index, expected in test_cases:
        number.text = input_str
        result = number.mistake(ErrorType.MISREAD, index)
        assert result == expected


def test_numeric_key_pad():
    test_cases = [
        ("010012", 5, "010015"),
        ("010009", 5, "010006"),
        ("010023", 5, "010026"),
        ("942021", 1, "912021"),
        ("925021", 1, "955021"),
        ("005021", 1, "015021"),
    ]
    number = Number()
    for input_str, index, expected in test_cases:
        number.text = input_str
        result = number.mistake(ErrorType.NUMERIC_KEY_PAD, index)
        assert result == expected


def test_empty_string():
    number = Number("")
    assert number.mistake() == ""


def test_single_digit():
    number = Number("5")
    result = number.mistake()
    assert isinstance(result, str)
    assert len(result) == 1
    assert result.isdigit()


def test_random_error_type():
    """Test that random error selection works"""
    number = Number("12345")
    results = set()
    # Run multiple times to ensure we get different errors
    for _ in range(50):
        results.add(number.mistake())
    # Should get multiple different results
    assert len(results) > 1


@pytest.mark.parametrize("invalid_input", [None, 3.14, [], {}, "abc"])
def test_invalid_input_types(invalid_input):
    """Test handling of invalid input types"""
    number = Number(invalid_input)
    result = number.mistake()
    assert isinstance(result, str)
    assert result == "" or result.isdigit()
