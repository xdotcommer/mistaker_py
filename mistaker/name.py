from typing import Optional, List, Dict
import random
from .word import Word
from .constants import ErrorType


class Name(Word):
    """
    Class for generating name-based mistakes.
    Inherits from Word class but can be extended with name-specific functionality.
    """

    COMMON_PREFIXES = {"MR", "MRS", "MS", "DR", "PROF"}
    COMMON_SUFFIXES = {"JR", "SR", "II", "III", "IV", "PHD", "MD", "ESQ"}

    @classmethod
    def make_mistake(cls, text: str) -> str:
        """Class method for one-off mistake generation"""
        instance = cls(text)
        # Force a modification by using a random error type
        error_types = [
            ErrorType.DROPPED_LETTER,
            ErrorType.DOUBLE_LETTER,
            ErrorType.MISREAD_LETTER,
            ErrorType.MISTYPED_LETTER,
            ErrorType.EXTRA_LETTER,
            ErrorType.MISHEARD_LETTER,
        ]
        return instance.mistake(random.choice(error_types))

    def __init__(self, text: str = ""):
        self.original_text = text
        super().__init__(text)

    def get_case_variants(self) -> List[str]:
        """Returns common case variants of the name"""
        if not self.original_text:
            return [""]

        words = self.original_text.split()
        title_case = " ".join(word.title() for word in words)

        return [
            title_case,
            self.original_text.upper(),
            self.original_text.lower(),
        ]

    def is_same_name(self, other_name: str, case_sensitive: bool = False) -> bool:
        """Check if two names are the same, ignoring case by default"""
        if case_sensitive:
            return self.text == other_name
        return self.text.upper() == other_name.upper()

    def _get_nickname_variations(self, first_name: str) -> List[str]:
        """Get nickname variations for a given first name"""
        try:
            from nicknames import NickNamer

            namer = NickNamer()

            variations = set()
            nicknames = namer.nicknames_of(first_name)
            if nicknames:
                variations.update(nicknames)

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

        # Start with original first name
        first_names = [parts["first"]]

        # Add nicknames
        nicknames = self._get_nickname_variations(parts["first"])
        first_names.extend(nicknames)

        # Generate variations for each first name (original + nicknames)
        for first in first_names:
            # Basic variations
            variations.extend(
                [
                    f"{first} {parts['last']}",
                    f"{parts['last']}, {first}",
                    f"{parts['last']} {first}",
                ]
            )

            # Handle middle names
            if parts["middle"]:
                variations.extend(
                    [
                        f"{first} {' '.join(parts['middle'])} {parts['last']}",
                        f"{first} {parts['middle'][0][0]} {parts['last']}",
                        f"{first[0]} {' '.join(parts['middle'])} {parts['last']}",
                    ]
                )

            # Create variations with prefix/suffix
            base_variations = [f"{first} {parts['last']}"]  # Simple first last
            if parts["middle"]:
                base_variations.append(
                    f"{first} {' '.join(parts['middle'])} {parts['last']}"
                )

            # Add prefix/suffix combinations
            for base in base_variations:
                if parts["prefix"] and parts["suffix"]:
                    variations.append(f"{parts['prefix']} {base} {parts['suffix']}")
                elif parts["prefix"]:
                    variations.append(f"{parts['prefix']} {base}")
                elif parts["suffix"]:
                    variations.append(f"{base} {parts['suffix']}")

            # Additional prefix variations
            if parts["prefix"]:
                if parts["prefix"] == "Dr":
                    variations.extend([f"Mr {base}", f"Mrs {base}"])
                else:
                    variations.append(f"Dr {base}")

        # Clean up and deduplicate
        variations = [" ".join(v.split()) for v in variations]
        return list(set(variations))

    def get_parts(self) -> Dict[str, str]:
        """Split name into prefix, first, middle, last, suffix"""
        result = {
            "prefix": "",
            "first": "",
            "middle": [],
            "last": "",
            "suffix": "",
        }

        if not self.text:
            return result

        parts = self.text.split()
        if not parts:
            return result

        current_pos = 0

        # Check for prefix
        if parts[0].upper() in self.COMMON_PREFIXES:
            result["prefix"] = parts[0]
            current_pos += 1

        if current_pos >= len(parts):
            return result

        # Get first name
        result["first"] = parts[current_pos]
        current_pos += 1

        # Get remaining parts
        remaining = parts[current_pos:]
        remaining_upper = [p.upper() for p in remaining]

        # Check for suffix from the end
        suffix_count = 0
        for i in range(len(remaining_upper) - 1, -1, -1):
            if remaining_upper[i] in self.COMMON_SUFFIXES:
                suffix_count += 1
                if result["suffix"] == "":
                    result["suffix"] = remaining[i]
            else:
                break

        # Remove suffixes from remaining parts
        if suffix_count > 0:
            remaining = remaining[:-suffix_count]

        # Now handle last name and middle names
        if remaining:
            result["last"] = remaining[-1]
            if len(remaining) > 1:
                result["middle"] = remaining[:-1]

        return result

    def reformat(self, text: str) -> str:
        """Format names consistently"""
        cleaned = "".join(c for c in str(text).upper() if c.isalpha() or c.isspace())
        return " ".join(cleaned.split())

    def mistake(
        self, error_type: Optional[ErrorType] = None, index: Optional[int] = None
    ) -> str:
        """Generate a mistake in the name"""
        if error_type is None:
            # Get variations if no specific error type
            variations = self.get_name_variations()
            if variations:
                return random.choice(variations)

        return super().mistake(error_type, index)

    def chaos(self) -> str:
        """Apply multiple random mistakes to the name"""
        errors_count = random.randint(1, 6)
        current_text = self.text
        for _ in range(errors_count):
            self.text = self.mistake()
        result = self.text
        self.text = current_text  # Restore original text
        return result
