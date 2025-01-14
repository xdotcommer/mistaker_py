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


def test_building_name_and_city_use_word_mistaker():
    """Test that building_name and city use Word mistaker with different frequencies"""
    with mock.patch.object(Word, "mistake") as mock_word:
        # Test building name - should always make mistake
        mock_word.return_value = "ROBIE HOISE"  # HOUSE -> HOISE

        address = Address("Robie House, 5757 South Woodlawn Avenue, Chicago, IL 60637")
        result = address.make_mistake("building_name")

        assert mock_word.called
        assert "ROBIE HOISE" in result
        mock_word.reset_mock()

        # Test city - should make mistake 30% of the time
        mock_word.return_value = "CHICACO"  # CHICAGO -> CHICACO

        with mock.patch("random.random") as mock_random:
            # Test when random is under 0.3 - should make mistake
            mock_random.return_value = 0.2
            result = address.make_mistake("city")
            assert mock_word.called
            assert "CHICACO" in result
            mock_word.reset_mock()

            # Test when random is over 0.3 - should not make mistake
            mock_random.return_value = 0.4
            result = address.make_mistake("city")
            assert not mock_word.called
            assert "Chicago" in result


def test_state_mistakes():
    """Test that state can be omitted"""
    with mock.patch("random.random") as mock_random:
        # Test omitting state (25% chance)
        mock_random.return_value = 0.2
        address = Address("123 Main St, Denver, CO 80202")
        result = address.make_mistake("state")
        assert "123 Main St, Denver, 80202" in result

        # Test keeping state (75% chance)
        mock_random.return_value = 0.3
        result = address.make_mistake("state")
        assert "CO" in result


def test_street_type_mistakes():
    """Test that street_type can be swapped with alternatives"""
    with mock.patch("random.random") as mock_random:
        address = Address("123 Main Street, Denver, CO 80202")

        # Test swapping with variation (30% chance)
        mock_random.return_value = 0.2
        result = address.make_mistake("street_type")
        # Should swap with another variation that maps to 'ST' (like 'STR', 'STRT')
        assert any(
            t.title() in result
            for t in Address.STREET_TYPE_ABBREVIATIONS.keys()
            if t != "STREET" and Address.STREET_TYPE_ABBREVIATIONS[t] == "ST"
        )

        # Test swapping with different type (30% chance)
        mock_random.return_value = 0.4
        result = address.make_mistake("street_type")
        current_abbrev = Address.STREET_TYPE_ABBREVIATIONS["STREET"]  # Should be "ST"
        # Should swap with a type that maps to something other than 'ST'
        assert any(
            t.title() in result
            for t in Address.STREET_TYPE_ABBREVIATIONS.keys()
            if len(t) > 2 and Address.STREET_TYPE_ABBREVIATIONS[t] != current_abbrev
        )

        # Test keeping original (40% chance)
        mock_random.return_value = 0.8
        result = address.make_mistake("street_type")
        assert "Street" in result


def test_unit_type_mistakes():
    """Test that unit_type has correct error probabilities"""
    with mock.patch("random.random") as mock_random:
        address = Address("123 Main St, Apartment 4B, Denver, CO 80202")

        # Test random different unit type (25% chance)
        mock_random.return_value = 0.1
        result = address.make_mistake("unit_type")
        assert any(
            t.title() in result
            for t in Address.UNIT_TYPE_ABBREVIATIONS.keys()
            if t != "APARTMENT" and t != "APT"
        )

        # Test omitting unit type (25% chance)
        mock_random.return_value = 0.3
        result = address.make_mistake("unit_type")
        assert "4B" in result
        assert "Apartment" not in result and "APT" not in result

        # Test word mistake (25% chance)
        with mock.patch.object(Word, "mistake") as mock_word:
            mock_random.return_value = 0.6
            mock_word.return_value = "APERTMENT"
            result = address.make_mistake("unit_type")
            assert mock_word.called
            assert "APERTMENT" in result

        # Test keeping original (25% chance)
        mock_random.return_value = 0.9
        result = address.make_mistake("unit_type")
        assert "Apartment" in result


def test_mistake_maintains_full_address():
    """Test that mistake() always returns a full address, not just components"""
    # Test multiple times to catch random variations
    for _ in range(50):  # Run multiple times to catch different random parts
        address = Address("123 N Main St Suite 456 Denver, CO 80202")
        result = address.mistake()

        # Check that result maintains key structural elements
        parts = result.split()
        assert len(parts) >= 6, f"Address too short: {result}"

        # First part should be a number (street number)
        assert parts[0].isdigit(), f"Missing street number: {result}"

        # Should have either a state abbreviation or a comma indicating structure
        has_location_structure = ("," in result) or any(
            len(p) == 2 and p.isalpha() for p in parts
        )
        assert has_location_structure, f"Missing location structure: {result}"

        # Should have a zip code
        assert any(len(p) == 5 and p.isdigit() for p in parts), f"Missing zip: {result}"

        # Make sure we don't just get back a number
        assert not result.isdigit(), f"Got only digits: {result}"

        # Check length is reasonable (not just a component)
        assert len(result) > 10, f"Result too short: {result}"
