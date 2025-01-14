from typing import Optional
import re
import random
from .number import Number
from .constants import ErrorType
from .base import BaseMistaker


class LicenseNumber(BaseMistaker):
    """Class for generating license number mistakes that only affect numeric portions"""

    def __init__(self, text: str = ""):
        super().__init__(text)

    def mistake(
        self, error_type: Optional[ErrorType] = None, index: Optional[int] = None
    ) -> str:
        """Generate a mistake in the license number, only affecting numeric portions"""
        if not self.text:
            return ""

        # Split the text into numeric and non-numeric parts while preserving positions
        parts = []
        current_part = ""
        current_type = None  # None, 'num', or 'alpha'

        for char in self.text:
            new_type = "num" if char.isdigit() else "alpha"
            if current_type != new_type and current_part:
                parts.append((current_type, current_part))
                current_part = ""
            current_type = new_type
            current_part += char

        if current_part:
            parts.append((current_type, current_part))

        # Only make mistakes in the numeric parts
        result = ""
        for part_type, part in parts:
            if part_type == "num":
                # Create a temporary Number instance for this numeric part
                temp_number = Number(part)
                result += temp_number.mistake(error_type)
            else:
                result += part

        return result

    @classmethod
    def make_mistake(cls, text: str) -> str:
        """Class method for one-off mistake generation"""
        instance = cls(text)
        # Force a modification by using a random error type from Number class
        number_errors = [
            ErrorType.ONE_DIGIT_UP,
            ErrorType.ONE_DIGIT_DOWN,
            ErrorType.KEY_SWAP,
            ErrorType.DIGIT_SHIFT,
            ErrorType.MISREAD,
            ErrorType.NUMERIC_KEY_PAD,
        ]
        error_type = random.choice(number_errors)
        return instance.mistake(error_type)

    def reformat(self, text: str) -> str:
        """Reformat the license number (optional implementation)"""
        return text
