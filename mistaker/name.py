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

    @classmethod
    def make_mistake(cls, text: str) -> str:
        """Class method for one-off mistake generation"""
        instance = cls(text)
        # Force a modification by using a random error type
        error_types = [
            ErrorType.ONE_DIGIT_UP,
            ErrorType.ONE_DIGIT_DOWN,
            ErrorType.KEY_SWAP,
            ErrorType.DIGIT_SHIFT,
            ErrorType.MISREAD,
            ErrorType.NUMERIC_KEY_PAD,
        ]
        return instance.mistake(random.choice(error_types))

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

    def _get_nickname_variations(self, first_name: str) -> List[str]:
        """Get nickname variations for a given first name using the correct nicknames_of method"""
        try:
            from nicknames import NickNamer

            namer = NickNamer()
            variations = set()  # Use a set to avoid duplicates

            # Get nicknames using the correct nicknames_of method
            nicknames = namer.nicknames_of(first_name)
            if nicknames:
                variations.update(nicknames)

            # Optionally also get canonical forms
            canonicals = namer.canonicals_of(first_name)
            if canonicals:
                variations.update(canonicals)

            # Filter out empty strings and the original name
            variations = {v for v in variations if v and v != first_name}

            return list(variations)
        except ImportError:
            print(
                "Warning: nicknames package not installed. Run 'pip install nicknames' to enable nickname generation."
            )
            return []
        except Exception as e:
            print(f"Warning: Error getting nicknames for {first_name}: {str(e)}")
            return []

    def get_name_variations(self) -> List[str]:
        """Generate basic name variations including nicknames"""
        parts = self.get_parts()
        variations = []

        # Generate base name variations (without prefix/suffix)
        base_variations = [
            f"{parts['first']} {parts['last']}",
            f"{parts['last']}, {parts['first']}",
            f"{parts['last']} {parts['first']}",
        ]

        # Add these base variations first
        variations.extend(base_variations)

        # Handle middle names
        if parts["middle"]:
            # With full middle name
            variations.append(
                f"{parts['first']} {' '.join(parts['middle'])} {parts['last']}"
            )
            # With middle initial
            variations.append(
                f"{parts['first']} {parts['middle'][0][0]} {parts['last']}"
            )
            # First initial with middle name
            variations.append(
                f"{parts['first'][0]} {' '.join(parts['middle'])} {parts['last']}"
            )

        # Create base names for prefix/suffix variations
        base_names = [f"{parts['first']} {parts['last']}"]  # Simple first last
        if parts["middle"]:
            base_names.append(
                f"{parts['first']} {' '.join(parts['middle'])} {parts['last']}"
            )  # With middle

        # Add variations with suffix but no prefix
        if parts["suffix"]:
            for base in base_names:
                variations.append(
                    f"{base} {parts['suffix']}"
                )  # Just add suffix to each base name

        # Add prefix/suffix combinations
        for base_name in base_names:
            if parts["prefix"] and parts["suffix"]:
                # Full name with both
                variations.append(f"{parts['prefix']} {base_name} {parts['suffix']}")
                # With prefix variations
                if parts["prefix"] == "Dr":
                    variations.append(f"Mr {base_name} {parts['suffix']}")
                    variations.append(f"Mrs {base_name} {parts['suffix']}")
                else:
                    variations.append(f"Dr {base_name} {parts['suffix']}")
            elif parts["prefix"]:
                # Just prefix
                variations.append(f"{parts['prefix']} {base_name}")
                if parts["prefix"] == "Dr":
                    variations.append(f"Mr {base_name}")
                    variations.append(f"Mrs {base_name}")
                else:
                    variations.append(f"Dr {base_name}")

        # Add nickname variations
        nicknames = self._get_nickname_variations(parts["first"])
        for nickname in nicknames:
            # Basic nickname variations
            variations.extend(
                [
                    f"{nickname} {parts['last']}",
                    f"{parts['last']}, {nickname}",
                    f"{parts['last']} {nickname}",
                ]
            )

            # With middle name if present
            if parts["middle"]:
                variations.append(
                    f"{nickname} {' '.join(parts['middle'])} {parts['last']}"
                )
                variations.append(f"{nickname} {parts['middle'][0][0]} {parts['last']}")

            # Add suffix to nickname variations
            if parts["suffix"]:
                variations.append(f"{nickname} {parts['last']} {parts['suffix']}")

            # With prefix/suffix combinations
            if parts["prefix"]:
                variations.append(f"{parts['prefix']} {nickname} {parts['last']}")
                if parts["suffix"]:
                    variations.append(
                        f"{parts['prefix']} {nickname} {parts['last']} {parts['suffix']}"
                    )

        # Clean up and deduplicate
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
        """Generate a mistake in the name"""
        if (
            error_type is None
        ):  # Always generate a variation if no specific error type is provided
            parts = self.text.split()
            if len(parts) >= 2:
                variations = [
                    f"{parts[-1]}, {' '.join(parts[:-1])}",  # Last, First [Middle]
                    f"{parts[0][0]} {parts[1]} {parts[-1]}",  # R James Smith
                    f"{parts[0]} {parts[-1]}",  # Robert Smith
                ]
                if len(parts) > 2:
                    variations.append(
                        f"{parts[0][0]} {' '.join(parts[1:])}"
                    )  # F. Middle Last
                return random.choice(variations)

        return super().mistake(error_type, index)

    def chaos(self) -> str:
        """
        Apply a random number (between 1 and 6) of mistakes to the name and return the new value.
        """
        errors_count = random.randint(1, 6)
        for _ in range(errors_count):
            self.text = self.mistake()
        return self.text
