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
    """Test that name variations include key patterns we care about"""
    name = Name("William James Smith")
    variations = name.get_name_variations()

    # Test we get a reasonable number of variations
    assert len(variations) > 3, "Should generate multiple variations"

    # Test nickname functionality (if package available)
    try:
        from nicknames import NickNamer

        # Check we get any nickname-like variations (Bill, Will, etc)
        nickname_patterns = ["BILL", "WILL", "BILLY"]
        has_nickname = any(
            any(nick in v.upper() for nick in nickname_patterns) for v in variations
        )
        assert has_nickname, "Should include some form of nickname"
    except ImportError:
        pass


def test_name_variations_with_prefix_suffix():
    """Test that prefixes and suffixes are handled reasonably"""
    name = Name("Dr William James Smith Jr")
    variations = name.get_name_variations()

    # Test we get a reasonable number of variations
    assert len(variations) > 3, "Should generate multiple variations"

    # Test basic components appear in some variations
    has_prefix = any("DR" in v.upper() for v in variations)
    has_suffix = any("JR" in v.upper() for v in variations)
    has_middle = any("JAMES" in v.upper() for v in variations)

    assert has_prefix, "Should include prefix in some variations"
    assert has_suffix, "Should include suffix in some variations"
    assert has_middle, "Should include middle name in some variations"
