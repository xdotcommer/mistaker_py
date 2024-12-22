from typing import Optional, List
from .number import Number
from .word import Word
from .constants import ErrorType
import random

STREET_SUFFIXES = {"ST", "AVE", "RD", "BLVD", "DR", "LN", "CT", "WAY", "CIR", "PL"}


class Address(Word):
    """Simple address mistake generator that handles numeric and text components"""

    def __init__(self, text: str = ""):
        if text is None:
            self.text = ""
        else:
            try:
                self.text = str(text)
            except (ValueError, TypeError):
                self.text = ""
        super().__init__(self.text)

    def mistake(
        self, error_type: Optional[ErrorType] = None, index: Optional[int] = None
    ) -> str:
        if not self.text:
            return ""

        parts = self.text.upper().split()
        if not parts:
            return ""

        # Handle suffix first
        suffix = None
        if len(parts) > 2 and parts[-1] in STREET_SUFFIXES:
            suffix = parts[-1]
            parts = parts[:-1]
            if random.random() >= 0.3:  # 70% keep suffix
                parts.append(suffix)

        # Process remaining parts
        modified_parts = []
        for part in parts:
            if part == suffix:
                # Keep suffix unchanged
                modified_parts.append(part)
            elif part.isdigit():
                should_modify = random.random() < 0.6
                if should_modify:
                    handler = Number(part)
                    # Force a specific error type to ensure modification
                    modified_parts.append(handler.mistake(ErrorType.ONE_DIGIT_UP))
                else:
                    modified_parts.append(part)
            elif part.isalpha():
                # Always modify words
                handler = Word(part)
                modified_parts.append(handler.mistake())
            else:
                # Keep mixed alphanumeric unchanged
                modified_parts.append(part)

        return " ".join(modified_parts)

    def standardize(self) -> str:
        """Simple standardization - just uppercase"""
        return self.text.upper() if self.text else ""
