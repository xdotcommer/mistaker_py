import pytest
import usaddress
from mistaker import Address
from mistaker.number import Number
from mistaker.word import Word
from mistaker.constants import ErrorType
from unittest import mock
import random


@pytest.mark.parametrize(
    "input_addr,expected",
    [
        # Original test cases
        (
            "123 N Main St Suite 100 Denver, CO 80202",
            {
                "building_name": None,
                "street_number": "123",
                "street_direction": "N",
                "street_name": "MAIN",
                "street_type": "ST",
                "unit_type": "SUITE",
                "unit_id": "100",
                "city": "DENVER",
                "state": "CO",
                "zip": "80202",
            },
        ),
        (
            "456 East Washington Avenue Apt 2B",
            {
                "building_name": None,
                "street_number": "456",
                "street_direction": "EAST",
                "street_name": "WASHINGTON",
                "street_type": "AVENUE",
                "unit_type": "APT",
                "unit_id": "2B",
                "city": None,
                "state": None,
                "zip": None,
            },
        ),
        (
            "789 SW Broadway",
            {
                "building_name": None,
                "street_number": "789",
                "street_direction": "SW",
                "street_name": "BROADWAY",
                "street_type": None,
                "unit_type": None,
                "unit_id": None,
                "city": None,
                "state": None,
                "zip": None,
            },
        ),
        (
            "1234 Northeast MLK Jr Blvd #505 Portland, OR 97232",
            {
                "building_name": None,
                "street_number": "1234",
                "street_direction": "NORTHEAST",
                "street_name": "MLK JR",
                "street_type": "BLVD",
                "unit_type": "#",
                "unit_id": "505",
                "city": "PORTLAND",
                "state": "OR",
                "zip": "97232",
            },
        ),
        # New test case with building name
        (
            "Robie House, 5757 South Woodlawn Avenue, Chicago, IL 60637",
            {
                "building_name": "ROBIE HOUSE",
                "street_number": "5757",
                "street_direction": "SOUTH",
                "street_name": "WOODLAWN",
                "street_type": "AVENUE",
                "unit_type": None,
                "unit_id": None,
                "city": "CHICAGO",
                "state": "IL",
                "zip": "60637",
            },
        ),
    ],
)
def test_address_parsing(input_addr, expected):
    """Test that addresses are correctly parsed into their component parts"""
    address = Address(input_addr)
    components = address.parse()
    assert components == expected, f"\nExpected: {expected}\nGot: {components}"


def test_address_zip_calls_number_mistaker():
    """Test that zip code mistakes delegate to Number mistaker"""
    with mock.patch("mistaker.number.Number.make_mistake") as mock_number:
        mock_number.return_value = "90202"

        address = Address("123 Main St, Denver CO 80202")
        address.make_mistake("zip")

        # Verify Number.make_mistake was called with the zip code
        mock_number.assert_called_once_with("80202")


def test_address_street_number_calls_number_mistaker():
    """Test that street number mistakes delegate to Number mistaker"""
    with mock.patch("mistaker.number.Number.make_mistake") as mock_number:
        mock_number.return_value = "223"

        address = Address("123 Main St, Denver CO 80202")
        address.make_mistake("street_number")

        # Verify Number.make_mistake was called with the street number
        mock_number.assert_called_once_with("123")


def test_unit_id_numeric_part_calls_number_mistaker():
    """Test that numeric portion of unit_id delegates to Number mistaker"""
    with mock.patch("mistaker.number.Number.make_mistake") as mock_number:
        mock_number.return_value = "202"

        address = Address("123 Main St Apt 101A Denver CO 80202")
        address.make_mistake("unit_id")

        # Verify Number.make_mistake was called with just the numeric part
        mock_number.assert_called_once_with("101")

    # Test that the alpha portion is preserved
    with mock.patch("mistaker.number.Number.make_mistake") as mock_number:
        mock_number.return_value = "202"

        address = Address("123 Main St Apt 101A Denver CO 80202")
        result = address.make_mistake("unit_id")

        assert "202A" in result


def test_street_name_calls_word_mistaker():
    """Test that street_name uses Word mistaker's mistake method"""
    with mock.patch.object(Word, "mistake") as mock_word:
        mock_word.return_value = "MOIN"  # MAIN -> MOIN

        address = Address("123 Main St Denver CO 80202")
        address.make_mistake("street_name")

        # Verify Word.mistake was called
        mock_word.assert_called_once()


def test_street_direction_mistakes():
    """Test that street_direction handles all error cases"""
    # Set up our test data
    directions = [
        "EAST",
        "E",
        "WEST",
        "W",
        "NORTH",
        "N",
        "SOUTH",
        "S",
        "NORTHEAST",
        "NE",
        "NORTHWEST",
        "NW",
        "SOUTHEAST",
        "SE",
        "SOUTHWEST",
        "SW",
        "NORTH-WEST",
        "NORTH-EAST",
        "SOUTH-WEST",
        "SOUTH-EAST",
    ]

    # Mock random.random() to test each case
    with mock.patch("random.random") as mock_random:
        address = Address("123 North Main St")

        # Test skip direction (first quarter)
        mock_random.return_value = 0.1  # in first quarter
        result = address.make_mistake("street_direction")
        assert "123 Main St" in result

        # Test swap direction (second quarter)
        mock_random.return_value = 0.3  # in second quarter
        result = address.make_mistake("street_direction")
        assert any(d.title() in result for d in directions if d != "NORTH")

        # Test word mistake (third quarter)
        with mock.patch.object(Word, "mistake") as mock_word:
            mock_random.return_value = 0.6  # in third quarter
            mock_word.return_value = "NROTH"
            result = address.make_mistake("street_direction")
            assert mock_word.called
            assert "NROTH" in result

        # Test remain same (fourth quarter)
        mock_random.return_value = 0.9  # in fourth quarter
        result = address.make_mistake("street_direction")
        assert "North" in result  # Changed from "NORTH" to "North"
