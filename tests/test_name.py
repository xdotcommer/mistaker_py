import pytest
from mistaker import Name
from mistaker.constants import ErrorType


def test_reformat():
    name = Name()
    assert name.reformat("Apollo Theatre") == "APOLLO THEATRE"
    assert name.reformat("Mr. Nathaniel Wright") == "MR NATHANIEL WRIGHT"
    assert name.reformat("John  Q.  Public") == "JOHN Q PUBLIC"


def test_make_mistake_classmethod():
    """Test the class method interface"""
    assert Name.make_mistake("Cathy") != "Cathy"
    assert Name.make_mistake("Martin") != "Martin"


def test_dropped_letter():
    name = Name("CATHY")
    assert name.mistake(ErrorType.DROPPED_LETTER, 3) == "CATY"


def test_double_letter():
    name = Name("CATHY")
    assert name.mistake(ErrorType.DOUBLE_LETTER, 3) == "CATHHY"


def test_misread_letter():
    name = Name()
    test_cases = [
        ("Cathy", 2, "CAIHY"),  # Normal case
        ("A B", 1, "A B"),  # Space in middle of string should be preserved
    ]

    for input_name, index, expected in test_cases:
        name.text = input_name
        assert name.mistake(ErrorType.MISREAD_LETTER, index) == expected


def test_mistyped_letter():
    name = Name()
    test_cases = [("Cathy", 4, "CATHU")]

    for input_name, index, expected in test_cases:
        name.text = input_name
        assert name.mistake(ErrorType.MISTYPED_LETTER, index) == expected


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

    for input_name, expected in test_cases:
        name = Name(input_name)
        assert name.mistake(ErrorType.EXTRA_LETTER) == expected


def test_misheard_letters():
    name = Name()
    test_cases = [("Maximum", 2, "MACKSIMUM"), ("Clover", 3, "CLOFER")]

    for input_name, index, expected in test_cases:
        name.text = input_name
        assert name.mistake(ErrorType.MISHEARD_LETTER, index) == expected
