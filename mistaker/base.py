from abc import ABC, abstractmethod
import random
from typing import Optional, Union
from .constants import ErrorType


class BaseMistaker(ABC):
    """Base class for all mistaker classes"""

    def __init__(self, text: Optional[str] = None):
        self.text = text
        self.rand = random.Random()

    @abstractmethod
    def reformat(self, text: str) -> str:
        """Reformat input text to standard format"""
        pass

    @abstractmethod
    def mistake(
        self, error_type: Optional[ErrorType] = None, index: Optional[int] = None
    ) -> str:
        """Generate a mistake in the text"""
        pass

    @classmethod
    def make_mistake(cls, text: str) -> str:
        """Class method for one-off mistake generation"""
        return cls(text).mistake()
