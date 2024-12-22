# tests/test_date.py
import pytest
from mistaker import Date
from mistaker.constants import ErrorType


def test_reformat():
    date = Date()
    # Test empty string
    with pytest.raises(ValueError):
        date.reformat("")

    # Test invalid format
    with pytest.raises(ValueError):
        date.reformat("12-122-41411")

    # Test expected format
    assert date.reformat("1902-12-10") == "1902-12-10"

    # Test American format
    assert date.reformat("12/5/2020") == "2020-12-05"

    # Test Y2K format
    assert date.reformat("5/2/12") == "2012-05-02"


def test_make_mistake_classmethod():
    """Test the class method interface"""
    result = Date.make_mistake("1988-04-12")
    assert result != "1988-04-12"
    assert isinstance(result, str)


def test_one_digit_up():
    date = Date()
    # Test day increment
    date.text = "2010-12-05"
    assert date.mistake(ErrorType.ONE_DIGIT_UP, Date.DatePart.DAY) == "2010-12-06"
    # Test month increment
    date.text = "2010-12-05"
    assert (
        date.mistake(ErrorType.ONE_DIGIT_UP, Date.DatePart.MONTH) == "2010-01-05"
    )  # Wraps around
    # Test year increment
    date.text = "2010-12-05"
    assert date.mistake(ErrorType.ONE_DIGIT_UP, Date.DatePart.YEAR) == "2011-12-05"


def test_one_digit_down():
    date = Date("2010-12-05")
    # Test day decrement
    assert date.mistake(ErrorType.ONE_DIGIT_DOWN, Date.DatePart.DAY) == "2010-12-04"
    # Test month decrement
    assert date.mistake(ErrorType.ONE_DIGIT_DOWN, Date.DatePart.MONTH) == "2010-11-05"
    # Test year decrement
    assert date.mistake(ErrorType.ONE_DIGIT_DOWN, Date.DatePart.YEAR) == "2009-12-05"


def test_one_decade_down():
    date = Date("2010-12-05")
    assert date.mistake(ErrorType.ONE_DECADE_DOWN) == "2000-12-05"


def test_y2k():
    date = Date()
    # Test 21st century date
    date.text = "2015-12-05"
    assert date.mistake(ErrorType.Y2K) == "0015-12-05"
    # Test 20th century date
    date.text = "1915-12-05"
    assert date.mistake(ErrorType.Y2K) == "2015-12-05"


def test_month_day_swap():
    date = Date()
    # Test swappable dates
    date.text = "2010-05-12"
    assert date.mistake(ErrorType.MONTH_DAY_SWAP) == "2010-12-05"
    date.text = "2010-03-09"
    assert date.mistake(ErrorType.MONTH_DAY_SWAP) == "2010-09-03"


def test_key_swap():
    date = Date("1934-02-21")
    # Test day swap
    assert date.mistake(ErrorType.KEY_SWAP, Date.DatePart.DAY) == "1934-02-12"
    # Test month swap
    date.text = "1934-12-08"
    assert date.mistake(ErrorType.KEY_SWAP, Date.DatePart.MONTH) == "1934-21-08"
    # Test year swap
    date.text = "1934-12-05"
    assert date.mistake(ErrorType.KEY_SWAP, Date.DatePart.YEAR) == "1943-12-05"


def test_digit_shift():
    date = Date()
    # Test normal cases
    date.text = "2010-05-12"
    assert date.mistake(ErrorType.DIGIT_SHIFT) == "0020-10-05"
    date.text = "1945-03-09"
    assert date.mistake(ErrorType.DIGIT_SHIFT) == "0019-45-03"


def test_misread():
    date = Date()
    test_cases = [
        ("2010-05-12", Date.DatePart.DAY, "2010-05-15"),
        ("2010-05-09", Date.DatePart.DAY, "2010-05-04"),
        ("2010-05-23", Date.DatePart.DAY, "2010-05-28"),
        ("2010-04-12", Date.DatePart.MONTH, "2010-09-12"),
        ("2010-06-09", Date.DatePart.MONTH, "2010-05-09"),
        ("2010-07-23", Date.DatePart.MONTH, "2010-01-23"),
        ("1942-07-21", Date.DatePart.YEAR, "1992-07-21"),
        ("1925-07-21", Date.DatePart.YEAR, "1955-07-21"),
        ("2005-07-21", Date.DatePart.YEAR, "2085-07-21"),
    ]

    for input_date, date_part, expected in test_cases:
        date.text = input_date
        assert date.mistake(ErrorType.MISREAD, date_part) == expected


def test_numeric_key_pad():
    date = Date()
    test_cases = [
        ("2010-05-12", Date.DatePart.DAY, "2010-05-15"),
        ("2010-05-09", Date.DatePart.DAY, "2010-05-06"),
        ("2010-05-23", Date.DatePart.DAY, "2010-05-26"),
        ("2010-04-12", Date.DatePart.MONTH, "2010-01-12"),
        ("2010-06-09", Date.DatePart.MONTH, "2010-03-09"),
        ("2010-07-23", Date.DatePart.MONTH, "2010-04-23"),
        ("1942-07-21", Date.DatePart.YEAR, "1945-07-21"),
        ("1925-07-21", Date.DatePart.YEAR, "1922-07-21"),
        ("2000-07-21", Date.DatePart.YEAR, "2001-07-21"),
    ]

    for input_date, date_part, expected in test_cases:
        date.text = input_date
        assert date.mistake(ErrorType.NUMERIC_KEY_PAD, date_part) == expected
