from typing import Optional, Dict, Tuple
from collections import OrderedDict
import usaddress
from .word import Word
from .number import Number
import re
import random


class Address:
    DIRECTIONAL_REPLACEMENTS = [
        "EAST",
        "E",
        "WEST",
        "W",
        "NORTH",
        "N",
        "SOUTH",
        "S",
        "NORTHEAST",
        "NE",
        "NORTHWEST",
        "NW",
        "SOUTHEAST",
        "SE",
        "SOUTHWEST",
        "SW",
        "NORTH-WEST",
        "NORTH-EAST",
        "SOUTH-WEST",
        "SOUTH-EAST",
    ]

    def __init__(self, text: str = ""):
        if text is None:
            text = ""
        self.text = str(text).strip()
        self.word_mistaker = Word()

    def _empty_components(self) -> dict:
        """Return empty component dictionary."""
        return {
            "building_name": None,
            "street_number": None,
            "street_direction": None,
            "street_name": None,
            "street_type": None,
            "unit_type": None,
            "unit_id": None,
            "city": None,
            "state": None,
            "zip": None,
        }

    def parse(self) -> dict:
        """Parse address into its component parts using usaddress."""
        if not self.text:
            return self._empty_components()

        try:
            tagged_address, _ = usaddress.tag(
                self.text,
                tag_mapping={
                    "BuildingName": "building_name",  # Added this
                    "AddressNumber": "street_number",
                    "StreetNamePreDirectional": "street_direction",
                    "StreetName": "street_name",
                    "StreetNamePostType": "street_type",
                    "OccupancyType": "unit_type",
                    "OccupancyIdentifier": "unit_id",
                    "PlaceName": "city",
                    "StateName": "state",
                    "ZipCode": "zip",
                },
            )

            components = self._empty_components()
            components.update(tagged_address)

            # Clean up the components
            if components.get("building_name"):
                components["building_name"] = components["building_name"].upper()
            if components.get("street_direction"):
                components["street_direction"] = components["street_direction"].upper()
            if components.get("street_name"):
                components["street_name"] = components["street_name"].upper()
            if components.get("street_type"):
                components["street_type"] = components["street_type"].upper()
            if components.get("unit_type"):
                components["unit_type"] = components["unit_type"].upper()
            if components.get("city"):
                components["city"] = components["city"].upper()
            if components.get("state"):
                components["state"] = components["state"].upper()

            # Special handling for unit with pound sign
            if components.get("unit_id") and components["unit_id"].startswith("# "):
                components["unit_type"] = "#"
                components["unit_id"] = components["unit_id"].replace("# ", "")

            return components

        except usaddress.RepeatedLabelError:
            return self._empty_components()

    def make_mistake(self, part: str) -> str:
        """Generate a mistake in the specified address part"""
        components = self.parse()

        if components[part] is None:
            return self.text

        if part in ["street_number", "zip"]:
            return Number.make_mistake(components[part])

        if part == "unit_id":
            match = re.match(r"(\d+)([A-Za-z]*)", components[part])
            if match:
                numeric_part, alpha_part = match.groups()
                mistaken_number = Number.make_mistake(numeric_part)
                new_unit_id = mistaken_number + alpha_part
                return self.text.replace(components[part], new_unit_id)

        if part == "street_name":
            mistaken_name = self.word_mistaker.mistake()
            return self.text.replace(components[part], mistaken_name)

        if part == "street_direction":
            chance = random.random()
            orig_direction = components[part]

            if chance < 0.25:  # Skip direction
                # Case-insensitive removal of direction and surrounding spaces
                return re.sub(
                    rf"\s*{orig_direction}\s*", " ", self.text, flags=re.IGNORECASE
                ).strip()
            elif chance < 0.5:  # Swap direction
                new_direction = random.choice(
                    [d for d in self.DIRECTIONAL_REPLACEMENTS if d != orig_direction]
                )
                # Case-insensitive replacement
                return re.sub(
                    rf"{orig_direction}", new_direction, self.text, flags=re.IGNORECASE
                )
            elif chance < 0.75:  # Word mistake
                word_mistaker = Word(orig_direction)
                mistaken_direction = word_mistaker.mistake()
                # Case-insensitive replacement
                return re.sub(
                    rf"{orig_direction}",
                    mistaken_direction,
                    self.text,
                    flags=re.IGNORECASE,
                )
            else:  # Remain same
                return self.text

        return self.text
