import pytest
from unittest import mock
import random
from mistaker.license_number import LicenseNumber
from mistaker.constants import ErrorType
from mistaker.number import Number


class TestLicenseNumber:
    """Test suite for LicenseNumber class"""

    def test_license_number_only_affects_numbers(self):
        """Test that LicenseNumber only modifies numeric portions"""
        # Test with mixed alphanumeric
        license_num = LicenseNumber("AB123CD456")

        # Mock Number's mistake method to return predictable results
        with mock.patch("mistaker.number.Number.mistake") as mock_mistake:
            mock_mistake.side_effect = (
                lambda x: "999"
            )  # Replace any numeric portion with 999

            result = license_num.mistake(ErrorType.ONE_DIGIT_UP)

            # Should preserve AB and CD, but change numbers
            assert result == "AB999CD999"
            assert (
                mock_mistake.call_count == 2
            )  # Called twice, once for each number group

    def test_license_number_preserves_format(self):
        """Test that LicenseNumber preserves the original format structure"""
        test_cases = [
            "A12345",  # Leading letter
            "12345A",  # Trailing letter
            "A1B2C3",  # Alternating
            "123ABC",  # Numbers then letters
            "ABC123",  # Letters then numbers
        ]

        for case in test_cases:
            license_num = LicenseNumber(case)
            result = license_num.mistake()

            # Check that letter positions remain unchanged
            for i, char in enumerate(case):
                if char.isalpha():
                    assert result[i].isalpha()
                else:
                    assert result[i].isdigit()

    def test_empty_and_edge_cases(self):
        """Test edge cases for license numbers"""
        # Empty string
        assert LicenseNumber("").mistake() == ""

        # Only letters
        license_num = LicenseNumber("ABC")
        assert license_num.mistake() == "ABC"

        # Only numbers
        license_num = LicenseNumber("123")
        result = license_num.mistake()
        assert result != "123"
        assert result.isdigit()
