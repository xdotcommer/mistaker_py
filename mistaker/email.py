from typing import Optional, Tuple, List
from .base import BaseMistaker
from .constants import ErrorType
from .word import Word


class Email(BaseMistaker):
    """Class for generating email-based mistakes"""

    def __init__(self, text: str = "") -> None:
        super().__init__(text)
        self.word_mistaker = Word()
        self.original_case = ""  # Store original case

    def reformat(self, text: str) -> str:
        """Process email while preserving original case"""
        if text is None:
            return ""

        try:
            text_str = str(text)
        except (ValueError, TypeError):
            return ""

        if not text_str or text_str.isspace():
            return ""

        self.original_case = text_str
        # Always convert to lowercase
        return text_str.lower()

    def _is_tld(self, part: str) -> bool:
        """Check if a part is a TLD component"""
        common_tlds = {"com", "org", "edu", "net", "co", "uk"}
        return part in common_tlds

    def _split_email_parts(
        self, email: str
    ) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]], str]:
        """
        Split email into parts, preserving delimiters
        Returns (prefix_parts, domain_parts, tld)
        Each part is a tuple of (text, delimiter)
        """
        # Split into prefix and domain
        prefix_str, domain_full = email.split("@")

        # Handle prefix parts
        prefix_parts = []
        current_word = ""
        current_delim = ""

        for char in prefix_str:
            if char.isalnum():
                current_word += char
            else:
                if current_word:
                    prefix_parts.append((current_word, current_delim))
                    current_word = ""
                current_delim = char
        if current_word:
            prefix_parts.append((current_word, current_delim))

        # Handle domain parts and TLD
        domain_parts = []
        parts = domain_full.split(".")

        # Find TLD components
        tld_start = len(parts)
        for i in range(len(parts) - 1, -1, -1):
            if not self._is_tld(parts[i]):
                tld_start = i + 1
                break

        # Process domain parts before TLD
        for i in range(tld_start):
            domain_parts.append((parts[i], "."))

        # Combine remaining parts into TLD
        tld = ".".join(parts[tld_start:])

        return prefix_parts, domain_parts, tld

    def mistake(
        self, error_type: Optional[ErrorType] = None, index: Optional[int] = None
    ) -> str:
        """
        Generate a mistake in the email based on common transcription errors
        """
        if not self.text:
            return ""

        try:
            self.text = self.reformat(self.text)
            if not self.text:
                return ""
        except (ValueError, TypeError):
            return ""

        prefix_parts, domain_parts, tld = self._split_email_parts(self.text)

        if index is not None:
            current_pos = 0
            made_mistake = False
            result = ""

            # Handle prefix parts
            for word, delim in prefix_parts:
                if index >= current_pos and index < current_pos + len(word):
                    self.word_mistaker.text = word
                    result += self.word_mistaker.mistake(
                        error_type, index - current_pos
                    )
                    made_mistake = True
                else:
                    result += word
                result += delim
                current_pos += len(word) + len(delim)

            # Add @ symbol
            result += "@"
            current_pos += 1

            # Handle domain parts
            for word, delim in domain_parts:
                if (
                    not made_mistake
                    and index >= current_pos
                    and index < current_pos + len(word)
                ):
                    self.word_mistaker.text = word
                    result += self.word_mistaker.mistake(
                        error_type, index - current_pos
                    )
                else:
                    result += word
                result += delim
                current_pos += len(word) + len(delim)

            # Add TLD
            result += tld

            return result.lower()

        # Random mistake when no index provided
        all_parts = prefix_parts + domain_parts
        part_to_modify = self.rand.randint(0, len(all_parts) - 1)

        result = ""

        # Add prefix parts
        for i, (word, delim) in enumerate(prefix_parts):
            if i == part_to_modify:
                self.word_mistaker.text = word
                result += self.word_mistaker.mistake(error_type)
            else:
                result += word
            result += delim

        # Add @ symbol
        result += "@"

        # Add domain parts
        for i, (word, delim) in enumerate(domain_parts):
            if i + len(prefix_parts) == part_to_modify:
                self.word_mistaker.text = word
                result += self.word_mistaker.mistake(error_type)
            else:
                result += word
            result += delim

        # Add TLD
        result += tld

        return result.lower()
