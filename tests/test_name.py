import pytest
from mistaker import Name
from mistaker.constants import ErrorType


def test_reformat():
    name = Name()
    assert name.reformat("Apollo Theatre") == "APOLLO THEATRE"
    assert name.reformat("Mr. Nathaniel Wright") == "MR NATHANIEL WRIGHT"
    assert name.reformat("John  Q.  Public") == "JOHN Q PUBLIC"


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


def test_get_case_variants():
    name = Name("John Smith")
    variants = name.get_case_variants()

    assert "John Smith" in variants
    assert "JOHN SMITH" in variants
    assert "john smith" in variants

    # Test with special characters and spaces
    name = Name("Mary-Jane O'Connor")
    variants = name.get_case_variants()
    assert "Mary-Jane O'Connor" in variants
    assert "MARY-JANE O'CONNOR" in variants


def test_is_same_name():
    name = Name("John Smith")

    # Test case insensitive (default)
    assert name.is_same_name("JOHN SMITH")
    assert name.is_same_name("john smith")

    # Test case sensitive
    assert not name.is_same_name("john smith", case_sensitive=True)
    assert name.is_same_name("John Smith", case_sensitive=True)


def test_get_name_parts():
    test_cases = [
        (
            "Mr John Smith",
            {
                "prefix": "Mr",
                "first": "John",
                "middle": [],
                "last": "Smith",
                "suffix": "",
            },
        ),
        (
            "Dr Jane Marie Wilson PhD",
            {
                "prefix": "Dr",
                "first": "Jane",
                "middle": ["Marie"],
                "last": "Wilson",
                "suffix": "PhD",
            },
        ),
        (
            "James Robert Kennedy III",
            {
                "prefix": "",
                "first": "James",
                "middle": ["Robert"],
                "last": "Kennedy",
                "suffix": "III",
            },
        ),
        (
            "Mary",
            {"prefix": "", "first": "Mary", "middle": [], "last": "", "suffix": ""},
        ),
        ("", {"prefix": "", "first": "", "middle": [], "last": "", "suffix": ""}),
    ]

    name = Name()
    for input_name, expected in test_cases:
        name.text = input_name
        result = name.get_parts()
        assert result == expected


def test_get_parts_complex():
    name = Name("Prof Robert James Wilson Smith Jr PhD")
    parts = name.get_parts()

    assert parts["prefix"] == "Prof"
    assert parts["first"] == "Robert"
    assert "James" in parts["middle"]
    assert "Wilson" in parts["middle"]
    assert parts["last"] == "Smith"
    assert parts["suffix"] == "PhD"


def test_get_name_variations():
    # Test full name with middle
    name = Name("John Robert Smith")
    variations = name.get_name_variations()

    assert "Smith, John" in variations
    assert "Smith John" in variations
    assert "John Smith" in variations  # Missing middle
    assert "John R Smith" in variations  # Middle initial
    assert "J Robert Smith" in variations  # First initial

    # Test with prefix and suffix
    name = Name("Dr John Smith PhD")
    variations = name.get_name_variations()

    assert "John Smith" in variations  # No prefix/suffix
    assert any(
        v.startswith("Mr ") or v.startswith("Mrs ") for v in variations
    )  # Different prefix
    assert "Dr John Smith" in variations  # No suffix
    assert "John Smith PhD" in variations  # No prefix


def test_mistake_with_name_variations():
    name = Name("Robert James Smith")

    # Test multiple times to ensure we get different variations
    mistakes = set()
    for _ in range(20):
        mistakes.add(name.mistake())

    # Should have a mix of regular mistakes and name variations
    assert len(mistakes) > 1
    assert (
        any("Smith, Robert" in m for m in mistakes)
        or any("R James Smith" in m for m in mistakes)
        or any("Robert Smith" in m for m in mistakes)
    )
