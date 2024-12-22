from typing import Optional, List
from .word import Word
from .constants import ErrorType
import random


class Name(Word):
    """
    Class for generating name-based mistakes.
    Inherits from Word class but can be extended with name-specific functionality.
    """

    COMMON_PREFIXES = {"Mr", "Mrs", "Ms", "Dr", "Prof"}
    COMMON_SUFFIXES = {"Jr", "Sr", "II", "III", "IV", "PhD", "MD", "Esq"}

    def __init__(self, text: str = ""):
        self.original_text = text
        super().__init__(text)

    def get_case_variants(self) -> List[str]:
        """Returns common case variants of the name"""
        # Handle empty string case
        if not self.original_text:
            return [""]

        # Split into words to handle each part separately
        words = self.original_text.split()

        # Title case: capitalize first letter of each word
        title_case = " ".join(word.title() for word in words)

        return [
            title_case,  # Normal: "John Smith" or "Mary-Jane O'Connor"
            self.original_text.upper(),  # All caps: "JOHN SMITH"
            self.original_text.lower(),  # All lower: "john smith"
        ]

    def is_same_name(self, other_name: str, case_sensitive: bool = False) -> bool:
        """Check if two names are the same, ignoring case by default"""
        if case_sensitive:
            return self.text == other_name
        return self.text.upper() == other_name.upper()

    def get_name_variations(self) -> List[str]:
        """Generate basic name variations"""
        parts = self.get_parts()
        variations = []

        # Base names
        variations.append(f"{parts['first']} {parts['last']}")  # Simple first last
        variations.append(f"{parts['last']}, {parts['first']}")  # Last, first
        variations.append(f"{parts['last']} {parts['first']}")  # Last first

        # Handle middle name if present
        if parts["middle"]:
            variations.append(
                f"{parts['first']} {parts['middle'][0][0]} {parts['last']}"
            )  # With middle initial
            variations.append(
                f"{parts['first'][0]} {' '.join(parts['middle'])} {parts['last']}"
            )  # First initial

        # Handle prefix/suffix
        if parts["prefix"]:
            variations.append(
                f"{parts['prefix']} {parts['first']} {parts['last']}"
            )  # With prefix, no suffix
            # Add alternate prefixes
            if parts["prefix"] == "Dr":
                variations.append(f"Mr {parts['first']} {parts['last']}")
                variations.append(f"Mrs {parts['first']} {parts['last']}")
            else:
                variations.append(f"Dr {parts['first']} {parts['last']}")

        if parts["suffix"]:
            variations.append(
                f"{parts['first']} {parts['last']} {parts['suffix']}"
            )  # With suffix, no prefix

        # Clean up any double spaces
        variations = [" ".join(v.split()) for v in variations]
        return list(set(variations))

    def get_parts(self) -> dict:
        """Split name into prefix, first, middle, last, suffix"""
        PREFIXES = {"MR", "MS", "MRS", "DR", "PROF"}
        SUFFIXES = {"JR", "SR", "II", "III", "IV", "PHD", "MD"}

        # Initialize result structure
        result = {"prefix": "", "first": "", "middle": [], "last": "", "suffix": ""}

        # Handle empty string
        if not self.text:
            return result

        # Split into original and uppercase versions
        original_parts = self.text.split()
        upper_parts = [p.upper() for p in original_parts]

        if not original_parts:
            return result

        current_pos = 0

        # Check for prefix
        if upper_parts[0] in PREFIXES:
            result["prefix"] = original_parts[0]
            current_pos += 1

        # Not enough parts remaining
        if current_pos >= len(original_parts):
            return result

        # Get first name
        result["first"] = original_parts[current_pos]
        current_pos += 1

        # Get remaining parts
        remaining = original_parts[current_pos:]
        remaining_upper = [p.upper() for p in remaining]

        # Work backwards from the end
        # First, find all suffixes
        suffix_count = 0
        for i in range(len(remaining_upper) - 1, -1, -1):
            if remaining_upper[i] in SUFFIXES:
                suffix_count += 1
                if result["suffix"] == "":  # Only keep the last suffix
                    result["suffix"] = remaining[i]
            else:
                break

        # Remove suffixes from remaining parts
        if suffix_count > 0:
            remaining = remaining[:-suffix_count]
            remaining_upper = remaining_upper[:-suffix_count]

        # Now handle the last name and middle names
        if remaining:
            result["last"] = remaining[-1]
            if len(remaining) > 1:
                result["middle"] = remaining[:-1]

        return result

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
        Generate a mistake in the name. Can either be a transcription error (like Word)
        or a variation in how the name is formatted.
        """
        # Get both types of possible changes
        variations = self.get_name_variations()

        if error_type is None:
            # 30% chance of using a name variation, 50% chance of a transcription error
            if random.random() < 0.3 and variations:
                return random.choice(variations)
            else:
                # Fall back to regular word mistakes
                return super().mistake(error_type, index)
        return super().mistake(error_type, index)

    def chaos(self) -> str:
        """
        Apply a random number (between 1 and 6) of mistakes to the name and return the new value.
        """
        errors_count = random.randint(1, 6)
        for _ in range(errors_count):
            self.text = self.mistake()
        return self.text
