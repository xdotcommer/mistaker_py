from unittest.mock import patch
import pytest
from mistaker import Address
from mistaker.constants import ErrorType
from mistaker.number import Number
from mistaker.word import Word
from mistaker.address import (
    STREET_SUFFIXES,
    UNIT_DESIGNATORS,
    DIRECTION_PREFIXES,
    DIRECTION_MAPPING,
    SUFFIX_MAPPING,
)


def test_init():
    """Test address initialization with various inputs"""
    # Test normal initialization
    address = Address("123 Main St")
    assert address.text == "123 Main St"

    # Test case insensitivity
    address = Address("123 Main ST SUITE 100")
    assert "SUITE" in address.text.upper()

    # Test None handling
    address = Address(None)
    assert address.text == ""

    # Test empty string
    address = Address("")
    assert address.text == ""

    # Test whitespace
    address = Address("   ")
    assert address.text == ""


def test_split_address_parts():
    """Test internal address parsing"""
    address = Address("123 Main St Suite 100")
    main_parts, suffix, unit_parts, direction = address._split_address_parts(
        address.text
    )

    assert main_parts == ["123", "MAIN"]
    assert suffix == "ST"
    assert unit_parts == ["SUITE", "100"]
    assert direction is None

    # Test with direction
    address = Address("N 123 Main St")
    main_parts, suffix, unit_parts, direction = address._split_address_parts(
        address.text
    )
    assert main_parts == ["123", "MAIN"]
    assert direction == "N"


@pytest.mark.parametrize(
    "input_addr,expected_parts",
    [
        ("123 Main St", (["123", "MAIN"], "ST", [], None)),
        ("N 456 Oak Ave Apt 2B", (["456", "OAK"], "AVE", ["APT", "2B"], "N")),
        ("SW 789 Pine Rd Suite 300", (["789", "PINE"], "RD", ["SUITE", "300"], "SW")),
        ("321 Washington", (["321", "WASHINGTON"], None, [], None)),
        ("555 Broadway Fl 5", (["555", "BROADWAY"], None, ["FL", "5"], None)),
    ],
)
def test_address_parsing_variations(input_addr, expected_parts):
    """Test parsing of various address formats"""
    address = Address(input_addr)
    result = address._split_address_parts(input_addr)
    assert result == expected_parts


def test_direction_mapping():
    """Test direction word to abbreviation mapping"""
    test_cases = [
        ("North Main St", "N"),
        ("SOUTH Oak Ave", "S"),
        ("northwest Pine Rd", "NW"),
        ("Southeast Broadway", "SE"),
    ]

    address = Address()
    for input_text, expected in test_cases:
        direction = address._normalize_direction(input_text.split()[0].upper())
        assert direction == expected


def test_suffix_mapping():
    """Test street suffix word to abbreviation mapping"""
    test_cases = [
        ("Street", "ST"),
        ("AVENUE", "AVE"),
        ("Boulevard", "BLVD"),
        ("Road", "RD"),
    ]

    address = Address()
    for input_text, expected in test_cases:
        suffix = address._normalize_suffix(input_text.upper())
        assert suffix == expected


def test_mistake_generation():
    """Test mistake generation with mocked randomization"""
    address = Address("123 N Main St Suite 100")

    # Test with fixed random values to keep all components
    with patch("random.random", return_value=0.9):
        result = address.mistake()
        assert "ST" in result.upper()
        assert "SUITE" in result.upper() or "STE" in result.upper()

    # Test with fixed random values to drop components
    with patch("random.random", return_value=0.2):
        result = address.mistake()
        parts = result.upper().split()
        assert not any(suf in parts for suf in STREET_SUFFIXES)
        assert not any(des in parts for des in UNIT_DESIGNATORS)


def test_standardize():
    """Test address standardization"""
    test_cases = [
        {
            "input": "123 North Main Street Suite 100",
            "components": {"123", "N", "MAIN", "ST", "STE", "100"},
        },
        {
            "input": "456 South Oak Avenue Apartment 2B",
            "components": {"456", "S", "OAK", "AVE", "APT", "2B"},
        },
        {
            "input": "789 Northwest Pine Road Suite 300",
            "components": {"789", "NW", "PINE", "RD", "STE", "300"},
        },
    ]

    for case in test_cases:
        address = Address(case["input"])
        result = address.standardize()
        result_parts = set(result.upper().split())
        assert all(
            comp in result_parts for comp in case["components"]
        ), f"Missing components in '{result}'. Expected {case['components']}"


def test_empty_and_invalid_addresses():
    """Test handling of empty and invalid addresses"""
    test_cases = ["", None, "   ", "###"]

    for case in test_cases:
        address = Address(case)
        assert address.mistake() == ""
        assert address.standardize() == ""


def test_numeric_modification():
    """Test modification of numeric components"""
    address = Address("123 Main St")

    # Force number modification
    with patch("random.random", return_value=0.1):
        with patch.object(Number, "mistake", return_value="124"):
            result = address.mistake()
            assert result.startswith("124")


def test_word_modification():
    """Test modification of word components"""
    address = Address("123 Main St")

    with patch.object(Word, "mistake", return_value="MANE"):
        result = address.mistake()
        assert "MANE" in result.upper()


def test_mixed_case_input():
    """Test handling of mixed case input"""
    test_cases = [
        "123 Main St",
        "123 MAIN ST",
        "123 main st",
        "123 MaIn St",
    ]

    for case in test_cases:
        address = Address(case)
        standardized = address.standardize()
        assert "MAIN" in standardized
        assert "ST" in standardized


@pytest.mark.parametrize("suffix", STREET_SUFFIXES)
def test_all_street_suffixes(suffix):
    """Test handling of all street suffix variations"""
    address = Address(f"123 Main {suffix}")
    main_parts, suffix_result, unit_parts, direction = address._split_address_parts(
        address.text
    )
    assert suffix_result == suffix


def test_unit_number_modification():
    """Test modification of unit numbers"""
    address = Address("123 Main St Apt 456")

    # Force unit number modification
    with patch("random.random", return_value=0.9):  # Keep unit designator
        with patch.object(Number, "mistake", return_value="457"):
            result = address.mistake()
            assert "APT" in result.upper()


def test_alphanumeric_unit_handling():
    """Test handling of alphanumeric unit numbers"""
    address = Address("123 Main St Suite 4B")

    # Keep unit and modify it
    with patch("random.random", return_value=0.9):
        result = address.mistake()
        assert "SUITE" in result.upper() or "STE" in result.upper()
