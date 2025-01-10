from typing import Optional, Tuple
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
        # Handle invalid input types by converting to string
        if text is None:
            return ""

        try:
            text_str = str(text)
        except (ValueError, TypeError):
            return ""

        if not text_str or text_str.isspace():
            return ""

        # Store original case for later use (though we won't use it now)
        self.original_case = text_str
        # Always convert to lowercase
        return text_str.lower()

    def _split_email(self, email: str) -> Tuple[str, str, str]:
        """Split email into prefix, domain, and TLD"""
        prefix, rest = email.split("@")
        domain_parts = rest.split(".")
        tld = domain_parts[-1]
        domain = ".".join(domain_parts[:-1])
        return prefix, domain, tld

    def mistake(
        self, error_type: Optional[ErrorType] = None, index: Optional[int] = None
    ) -> str:
        """
        Generate a mistake in the email based on common transcription errors

        Args:
            error_type: Type of error to generate. If None, one is chosen randomly
            index: Position to apply the error. If None, one is chosen randomly

        Returns:
            Modified email string with the applied error
        """
        if not self.text:
            return ""

        try:
            self.text = self.reformat(self.text)
            if not self.text:
                return ""
        except (ValueError, TypeError):
            return ""

        prefix, domain, tld = self._split_email(self.text)
        # Determine whether to make mistake in prefix or domain
        if index is not None:
            # If index is in prefix range, modify prefix
            if index < len(prefix):
                self.word_mistaker.text = prefix
                prefix = self.word_mistaker.mistake(error_type, index)
            # If index is beyond prefix, modify domain
            else:
                self.word_mistaker.text = domain
                domain = self.word_mistaker.mistake(error_type, index - len(prefix) - 1)
        else:
            # Randomly choose prefix or domain
            if self.rand.random() < 0.7:  # 70% chance to modify prefix
                self.word_mistaker.text = prefix
                prefix = self.word_mistaker.mistake(error_type)
            else:
                self.word_mistaker.text = domain
                domain = self.word_mistaker.mistake(error_type)

        # Ensure the result is lowercase
        result = f"{prefix}@{domain}.{tld}".lower()
        return result
