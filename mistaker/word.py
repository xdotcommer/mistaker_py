from typing import Optional
from .base import BaseMistaker
from .constants import (
    ErrorType,
    MISREAD_LETTERS,
    MISTYPED_LETTERS,
    MISHEARD_LETTERS,
    EXTRA_LETTERS,
)


class Word(BaseMistaker):
    """Class for generating word-based mistakes"""

    def reformat(self, text: str) -> str:
        """Convert text to uppercase and remove non-alpha characters except spaces"""
        # Handle invalid input types by converting to string
        if text is None:
            return ""

        try:
            text_str = str(text)
        except (ValueError, TypeError):
            return ""

        if not text_str or text_str.isspace():
            return text_str

        return "".join(c for c in text_str.upper() if c.isalpha() or c.isspace())

    def mistake(
        self, error_type: Optional[ErrorType] = None, index: Optional[int] = None
    ) -> str:
        """
        Generate a mistake in the word based on common transcription errors

        Args:
            error_type: Type of error to generate. If None, one is chosen randomly
            index: Position to apply the error. If None, one is chosen randomly

        Returns:
            Modified string with the applied error
        """
        # Handle invalid input by returning empty string
        if self.text is None:
            return ""

        try:
            self.text = self.reformat(self.text)
        except (ValueError, TypeError):
            return ""

        length = len(self.text)

        if length == 0:
            return ""

        if error_type is None:
            word_errors = [
                ErrorType.DROPPED_LETTER,
                ErrorType.DOUBLE_LETTER,
                ErrorType.MISREAD_LETTER,
                ErrorType.MISTYPED_LETTER,
                ErrorType.EXTRA_LETTER,
                ErrorType.MISHEARD_LETTER,
            ]
            error_type = self.rand.choice(word_errors)

        if index is None:
            index = self.rand.randint(0, length - 1)

        text_list = list(self.text)

        if error_type == ErrorType.DROPPED_LETTER:
            if index < len(text_list):
                text_list.pop(index)

        elif error_type == ErrorType.DOUBLE_LETTER:
            if index < len(text_list):
                text_list.insert(index, text_list[index])

        elif error_type == ErrorType.EXTRA_LETTER:
            if text_list[-1] in EXTRA_LETTERS:
                text_list.append(EXTRA_LETTERS[text_list[-1]])

        elif error_type == ErrorType.MISREAD_LETTER:
            if index < len(text_list) and text_list[index] in MISREAD_LETTERS:
                text_list[index] = MISREAD_LETTERS[text_list[index]]

        elif error_type == ErrorType.MISTYPED_LETTER:
            if index < len(text_list) and text_list[index] in MISTYPED_LETTERS:
                text_list[index] = MISTYPED_LETTERS[text_list[index]]

        elif error_type == ErrorType.MISHEARD_LETTER:
            if index < len(text_list) and text_list[index] in MISHEARD_LETTERS:
                replacement = MISHEARD_LETTERS[text_list[index]]
                text_list[index] = replacement

        return "".join(text_list)
