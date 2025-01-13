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
    UNIT_DESIGNATORS,
)
import random


class Address(Word):
    def __init__(self, text: str = ""):
        if text is None:
            text = ""
        try:
            self.text = str(text).strip()
        except (ValueError, TypeError):
            self.text = ""
        super().__init__(self.text)

    def _normalize_direction(self, word: str) -> Optional[str]:
        if word in ADDRESS_DIRECTIONS:
            return word
        return ADDRESS_DIRECTION_MAPPING.get(word)

    def _normalize_suffix(self, word: str) -> Optional[str]:
        if word in ADDRESS_SUFFIXES:
            return word
        return ADDRESS_SUFFIX_MAPPING.get(word)

    def _split_address_parts(
        self, address: str
    ) -> Tuple[List[str], Optional[str], List[str], Optional[str], List[str]]:
        if not address or not address.strip():
            return [], None, [], None, []

        address_parts = [p.strip() for p in address.upper().split(",")]

        street_parts = address_parts[0].split()
        location_parts = address_parts[1:] if len(address_parts) > 1 else []

        if not street_parts:
            return [], None, [], None, []

        unit_parts = []
        main_parts = []
        found_unit = False

        i = 0
        while i < len(street_parts):
            if street_parts[i] in UNIT_DESIGNATORS and i < len(street_parts) - 1:
                unit_parts = street_parts[i:]
                found_unit = True
                break
            main_parts.append(street_parts[i])
            i += 1

        direction = None
        if main_parts:
            first_dir = self._normalize_direction(main_parts[0])
            if first_dir:
                direction = first_dir
                main_parts = main_parts[1:]

        suffix = None
        if main_parts:
            potential_suffix = self._normalize_suffix(main_parts[-1])
            if potential_suffix:
                suffix = potential_suffix
                main_parts = main_parts[:-1]

        return main_parts, suffix, unit_parts, direction, location_parts

    def mistake(
        self, error_type: Optional[ErrorType] = None, index: Optional[int] = None
    ) -> str:
        if not self.text.strip() or not any(c.isalnum() for c in self.text):
            return ""

        main_parts, suffix, unit_parts, direction, location_parts = (
            self._split_address_parts(self.text)
        )
        if not main_parts:
            return ""

        modified_parts = []

        if direction and random.random() >= 0.3:
            modified_parts.append(direction)

        for part in main_parts:
            if part == ",":
                modified_parts.append(part)
            elif len(part) == 2 and part.isalpha():
                modified_parts.append(part)
            elif part.isdigit():
                handler = Number(part)
                modified_parts.append(handler.mistake(error_type))
            elif len(part) >= 3 and not any(c.isdigit() for c in part):
                handler = Word(part)
                modified_parts.append(handler.mistake(error_type))
            else:
                modified_parts.append(part)

        if suffix and random.random() >= 0.3:
            modified_parts.append(suffix)

        if unit_parts and random.random() >= 0.4:
            if len(unit_parts) >= 2:
                unit_des = unit_parts[0].upper()
                unit_num = unit_parts[1]
            if unit_des in UNIT_DESIGNATORS:
                possible_designators = [d for d in UNIT_DESIGNATORS if d != unit_des]
                if possible_designators:
                    unit_des = random.choice(possible_designators)
                if unit_num.isdigit():
                    handler = Number(unit_num)
                    unit_num = handler.mistake(error_type)
                modified_parts.extend([unit_des, unit_num])
        if location_parts:
            modified_parts.append(",")
            for i, loc_part in enumerate(location_parts):
                if i > 0:
                    modified_parts.append(",")

                loc_words = loc_part.split()
                for j, word in enumerate(loc_words):
                    if j > 0:
                        modified_parts.append(" ")
                    if len(word) == 2 and word.isalpha():
                        modified_parts.append(word)
                    elif word.isdigit():
                        handler = Number(word)
                        modified_parts.append(handler.mistake(error_type))
                    else:
                        modified_parts.append(word)

        return " ".join(part for part in modified_parts if part not in [" ", ""])

    def standardize(self) -> str:
        if not self.text.strip() or not any(c.isalnum() for c in self.text):
            return ""

        parts = self.text.upper().split()
        if not parts:
            return ""

        main_parts, suffix, unit_parts, direction, location_parts = (
            self._split_address_parts(self.text)
        )
        standardized_parts = []

        if direction:
            norm_dir = self._normalize_direction(direction)
            if norm_dir:
                standardized_parts.append(norm_dir)

        if main_parts and main_parts[0].isdigit():
            standardized_parts.append(main_parts[0])
            main_parts = main_parts[1:]

        for part in main_parts:
            norm_dir = self._normalize_direction(part)
            if norm_dir:
                standardized_parts.append(norm_dir)
            else:
                standardized_parts.append(part)

        if suffix:
            norm_suffix = self._normalize_suffix(suffix)
            if norm_suffix:
                standardized_parts.append(norm_suffix)

        if unit_parts:
            unit_des = unit_parts[0]
            if unit_des in UNIT_DESIGNATORS:
                possible_designators = [d for d in UNIT_DESIGNATORS if d != unit_des]
                if possible_designators:
                    unit_des = random.choice(possible_designators)
            standardized_parts.append(unit_des)
            if len(unit_parts) > 1:
                standardized_parts.append(unit_parts[1])

        return " ".join(standardized_parts)
