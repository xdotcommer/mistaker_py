from unittest.mock import patch
import pytest
from mistaker import Address
from mistaker.constants import ErrorType
from mistaker.number import Number
from mistaker.word import Word
from mistaker.constants import (
    ADDRESS_SUFFIXES,
    ADDRESS_UNITS,
    ADDRESS_DIRECTIONS,
    ADDRESS_DIRECTION_MAPPING,
    ADDRESS_SUFFIX_MAPPING,
    UNIT_DESIGNATORS,
)


def test_init():
    address = Address("123 Main St")
    assert address.text == "123 Main St"

    address = Address("123 Main ST SUITE 100")
    assert "SUITE" in address.text.upper()

    address = Address(None)
    assert address.text == ""

    address = Address("")
    assert address.text == ""

    address = Address("   ")
    assert address.text == ""


def test_split_address_parts():
    address = Address("123 Main St Suite 100")
    main_parts, suffix, unit_parts, direction = address._split_address_parts(
        address.text
    )
    assert main_parts == ["123", "MAIN"]
    assert suffix == "ST"
    assert unit_parts == ["SUITE", "100"]
    assert direction is None

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
    address = Address(input_addr)
    result = address._split_address_parts(input_addr)
    assert result == expected_parts


def test_direction_mapping():
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
    address = Address("123 N Main St Suite 100")

    with patch("random.random", return_value=0.9):
        result = address.mistake()
        assert "ST" in result.upper()
        assert "SUITE" in result.upper() or "STE" in result.upper()

    with patch("random.random", return_value=0.2):
        result = address.mistake()
        parts = result.upper().split()
        assert not any(suf in parts for suf in ADDRESS_SUFFIXES)
        assert not any(des in parts for des in ADDRESS_UNITS)


def test_standardize():
    test_cases = [
        {
            "input": "123 North Main Street Suite 100",
            "components": {"123", "N", "MAIN", "ST"},
        },
        {
            "input": "456 South Oak Avenue Apartment 2B",
            "components": {"456", "S", "OAK", "AVE"},
        },
        {
            "input": "789 Northwest Pine Road Suite 300",
            "components": {"789", "NW", "PINE", "RD"},
        },
    ]

    for case in test_cases:
        address = Address(case["input"])
        result = address.standardize()
        result_parts = set(result.upper().split())

        # Debug print statements
        print(f"\nInput: {case['input']}")
        print(f"Result: {result}")
        print(f"Result parts: {result_parts}")
        print(f"Expected components: {case['components']}")
        print(f"Missing components: {case['components'] - result_parts}")

        assert all(
            comp in result_parts for comp in case["components"]
        ), f"Missing components: {[comp for comp in case['components'] if comp not in result_parts]}"


def test_random_unit_designator():
    """Test that unit designators are randomly substituted"""
    address = Address("123 Main St Suite 100")

    # Run multiple times to ensure we get different substitutions
    results = set()
    for _ in range(10):
        result = address.mistake()
        unit_des = [part for part in result.upper().split() if part in UNIT_DESIGNATORS]
        if unit_des:
            results.add(unit_des[0])

    # Should get at least 2 different unit designators in 10 tries
    assert len(results) > 1, f"Only got {results} as unit designators"


def test_unit_designator_not_duplicated():
    """Test that the same unit designator isn't used when substituting"""
    address = Address("123 Main St SUITE 100")

    for _ in range(10):
        result = address.mistake()
        result_parts = result.upper().split()
        unit_des = [part for part in result_parts if part in UNIT_DESIGNATORS]
        # Should never have more than one unit designator
        assert len(unit_des) <= 1, f"Found multiple unit designators: {unit_des}"


@pytest.mark.parametrize("unit_des", UNIT_DESIGNATORS)
def test_all_unit_designators(unit_des):
    """Test that each unit designator can be used and substituted"""
    address = Address(f"123 Main St {unit_des} 100")
    result = address.mistake()
    result_parts = result.upper().split()
    found_des = [part for part in result_parts if part in UNIT_DESIGNATORS]

    if found_des:  # If we kept the unit designator (not dropped)
        assert (
            found_des[0] != unit_des
        ), f"Unit designator wasn't substituted: {unit_des}"


def test_unit_designator_case_insensitive():
    """Test that unit designators are recognized regardless of case"""
    test_cases = [
        "123 Main St suite 100",
        "123 Main St SUITE 100",
        "123 Main St Suite 100",
        "123 Main St sUiTe 100",
    ]

    for case in test_cases:
        address = Address(case)
        result = address.mistake()
        result_parts = result.upper().split()
        unit_des = [part for part in result_parts if part in UNIT_DESIGNATORS]
        if unit_des:  # If we kept the unit designator (not dropped)
            assert (
                unit_des[0] != "SUITE"
            ), f"Original unit designator wasn't substituted in: {case}"


def test_unit_designator_with_various_number_formats():
    """Test unit designators with different number formats"""
    test_cases = [
        "123 Main St Suite 100",
        "123 Main St Suite 100A",
        "123 Main St Suite A100",
        "123 Main St Suite A-100",
        "123 Main St Suite #100",
    ]

    for case in test_cases:
        address = Address(case)
        result = address.mistake()
        # Verify the number part is preserved in some form
        assert any(c.isdigit() for c in result), f"Lost unit number in: {result}"
