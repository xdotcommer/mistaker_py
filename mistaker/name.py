# mistaker/name.py
from typing import Optional
from .word import Word
from .constants import ErrorType


class Name(Word):
    """
    Class for generating name-based mistakes.
    Inherits from Word class but can be extended with name-specific functionality.
    """

    def reformat(self, text: str) -> str:
        """
        Format names consistently:
        - Convert to uppercase
        - Remove special characters except spaces
        - Normalize whitespace
        """
        # Remove special characters but keep spaces
        cleaned = "".join(c for c in str(text).upper() if c.isalpha() or c.isspace())
        # Normalize whitespace
        return " ".join(cleaned.split())

    def mistake(
        self, error_type: Optional[ErrorType] = None, index: Optional[int] = None
    ) -> str:
        """
        Generate a mistake in the name. Currently uses Word's mistake implementation
        but can be extended with name-specific error types.
        """
        # For now, use the Word implementation
        # Could be extended with name-specific error types like:
        # - Common nickname substitutions
        # - Cultural variations
        # - Marriage/maiden name errors
        return super().mistake(error_type, index)
