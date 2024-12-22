from typing import Optional
from .base import BaseMistaker
from .constants import ErrorType, MISREAD_NUMBERS, TEN_KEYS
import random


class Number(BaseMistaker):
    """Class for generating number-based mistakes"""

    def reformat(self, text: str) -> str:
        """Strip everything except digits"""
        return "".join(c for c in str(text) if c.isdigit())

    @classmethod
    def make_mistake(cls, text: str) -> str:
        """Class method for one-off mistake generation"""
        instance = cls(text)
        # Force a modification by using a random error type
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

    def mistake(
        self, error_type: Optional[ErrorType] = None, index: Optional[int] = None
    ) -> str:
        """
        Generate a mistake in the number based on common data entry errors

        Args:
            error_type: Type of error to generate. If None, one is chosen randomly
            index: Position to apply the error. If None, one is chosen randomly

        Returns:
            Modified string with the applied error
        """
        self.text = self.reformat(self.text)
        length = len(self.text)

        if length == 0:
            return self.text

        if error_type is None:
            number_errors = [
                ErrorType.ONE_DIGIT_UP,
                ErrorType.ONE_DIGIT_DOWN,
                ErrorType.NUMERIC_KEY_PAD,
                ErrorType.DIGIT_SHIFT,
                ErrorType.MISREAD,
                ErrorType.KEY_SWAP,
            ]
            error_type = self.rand.choice(number_errors)

        if index is None:
            index = self.rand.randint(0, length - 1)

        text_list = list(self.text)

        if error_type == ErrorType.ONE_DIGIT_UP:
            if index < len(text_list):
                digit = int(text_list[index])
                text_list[index] = str((digit + 1) % 10)

        elif error_type == ErrorType.ONE_DIGIT_DOWN:
            if index < len(text_list):
                digit = int(text_list[index])
                text_list[index] = str((digit - 1) % 10)

        elif error_type == ErrorType.KEY_SWAP:
            if length < 2:
                return self.text

            if index < len(text_list):
                prev_index = abs(index - 1)
                text_list[index], text_list[prev_index] = (
                    text_list[prev_index],
                    text_list[index],
                )

        elif error_type == ErrorType.NUMERIC_KEY_PAD:
            if index < len(text_list):
                if text_list[index] in TEN_KEYS:
                    text_list[index] = TEN_KEYS[text_list[index]]

        elif error_type == ErrorType.DIGIT_SHIFT:
            if index >= length:
                return "0" * length
            else:
                shifted = ("0" * index + self.text)[:length]
                return shifted

        elif error_type == ErrorType.MISREAD:
            if index < len(text_list):
                if text_list[index] in MISREAD_NUMBERS:
                    text_list[index] = MISREAD_NUMBERS[text_list[index]]

        return "".join(text_list)
