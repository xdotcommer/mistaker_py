from typing import Optional, List, Tuple
from .constants import ErrorType
from .number import Number
from .word import Word
from .constants import (
    ADDRESS_SUFFIXES,
    ADDRESS_UNITS,
    ADDRESS_DIRECTIONS,
    ADDRESS_DIRECTION_MAPPING,
    ADDRESS_SUFFIX_MAPPING,
)
import random


class Address(Word):
    """Address mistake generator that handles numeric, text components, and unit designators"""

    def __init__(self, text: str = ""):
        if text is None:
            text = ""
        try:
            self.text = str(text).strip()
        except (ValueError, TypeError):
            self.text = ""
        super().__init__(self.text)

    def _normalize_direction(self, word: str) -> Optional[str]:
        """Convert direction words to abbreviations"""
        if word in ADDRESS_DIRECTIONS:
            return word
        return ADDRESS_DIRECTION_MAPPING.get(word)

    def _normalize_suffix(self, word: str) -> Optional[str]:
        """Convert street suffix words to abbreviations"""
        if word in ADDRESS_SUFFIXES:
            return word
        return ADDRESS_SUFFIX_MAPPING.get(word)

    def _split_address_parts(
        self, address: str
    ) -> Tuple[List[str], Optional[str], List[str], Optional[str]]:
        """Split address into main address and unit parts"""
        if not address or not address.strip():
            return [], None, [], None

        parts = address.upper().split()
        if not parts:
            return [], None, [], None

        # Handle unit designators
        unit_parts = []
        main_parts = []
        found_unit = False

        i = 0
        while i < len(parts):
            if parts[i] in ADDRESS_UNITS and i < len(parts) - 1:
                unit_parts = parts[i:]
                found_unit = True
                break
            main_parts.append(parts[i])
            i += 1

        if not found_unit:
            unit_parts = []

        # Check for direction
        direction = None
        if main_parts:
            # Check first part for direction
            first_dir = self._normalize_direction(main_parts[0])
            if first_dir:
                direction = first_dir
                main_parts = main_parts[1:]

        # Check for street suffix
        suffix = None
        if main_parts:
            potential_suffix = self._normalize_suffix(main_parts[-1])
            if potential_suffix:
                suffix = potential_suffix
                main_parts = main_parts[:-1]

        return main_parts, suffix, unit_parts, direction

    def mistake(
        self, error_type: Optional[ErrorType] = None, index: Optional[int] = None
    ) -> str:
        """Generate address mistakes"""
        if not self.text.strip() or not any(c.isalnum() for c in self.text):
            return ""

        # Split address into components
        main_parts, suffix, unit_parts, direction = self._split_address_parts(self.text)
        if not main_parts:
            return ""

        modified_parts = []

        # Handle direction
        if direction and random.random() >= 0.3:  # 70% keep direction
            modified_parts.append(direction)

        # Process main address parts
        for part in main_parts:
            if part.isdigit():
                if random.random() < 0.6:  # 60% chance to modify numbers
                    handler = Number(part)
                    modified_parts.append(handler.mistake())
                else:
                    modified_parts.append(part)
            else:
                handler = Word(part)
                modified_parts.append(handler.mistake())

        # Handle suffix
        if suffix and random.random() >= 0.3:  # 70% keep suffix
            modified_parts.append(suffix)

        # Handle unit parts
        if unit_parts and random.random() >= 0.4:  # 60% keep unit info
            # Modify unit number but keep designator
            if len(unit_parts) >= 2:
                unit_des = "STE" if unit_parts[0] == "SUITE" else unit_parts[0]
                unit_num = unit_parts[1]
                if unit_num.isdigit():
                    handler = Number(unit_num)
                    unit_num = handler.mistake()
                modified_parts.extend([unit_des, unit_num])

        return " ".join(modified_parts)

    def standardize(self) -> str:
        """Standardize address format"""
        if not self.text.strip() or not any(c.isalnum() for c in self.text):
            return ""

        parts = self.text.upper().split()
        if not parts:
            return ""

        main_parts, suffix, unit_parts, direction = self._split_address_parts(self.text)

        standardized_parts = []

        # Add direction if present
        if direction:
            norm_dir = self._normalize_direction(direction)
            if norm_dir:
                standardized_parts.append(norm_dir)

        # Add main number
        if main_parts and main_parts[0].isdigit():
            standardized_parts.append(main_parts[0])
            main_parts = main_parts[1:]

        # Add remaining main parts, normalizing directions
        for part in main_parts:
            norm_dir = self._normalize_direction(part)
            if norm_dir:
                standardized_parts.append(norm_dir)
            else:
                standardized_parts.append(part)

        # Add suffix if present
        if suffix:
            norm_suffix = self._normalize_suffix(suffix)
            if norm_suffix:
                standardized_parts.append(norm_suffix)

        # Add unit parts if present
        if unit_parts:
            # Standardize common variations
            unit_des = unit_parts[0]
            if unit_des == "SUITE":
                unit_des = "STE"
            elif unit_des == "APARTMENT":
                unit_des = "APT"
            standardized_parts.append(unit_des)
            if len(unit_parts) > 1:
                standardized_parts.append(unit_parts[1])

        return " ".join(standardized_parts)
