from typing import Optional, List, Dict
from .word import Word
from .constants import ErrorType
import random


class Address(Word):
    """Class for generating simple address-based mistakes and variations"""

    def __init__(self, text: str = ""):
        if text is None:
            self.text = ""
        else:
            # Handle numeric input by converting to string but marking as invalid
            try:
                self.text = str(text)
                if self.text.isdigit():
                    self.text = ""
            except (ValueError, TypeError):
                self.text = ""

        super().__init__(self.text)
        self.components = self.parse_address()

    def parse_address(self) -> Dict[str, str]:
        """Parse address into basic components"""
        components = {
            "number": "",
            "pre_direction": "",
            "street_name": "",
            "street_type": "",
            "post_direction": "",
            "unit_type": "",
            "unit_number": "",
            "city": "",
            "state": "",
            "zip": "",
        }

        if not self.text:
            return components

        try:
            # Convert to string and uppercase
            address = str(self.text).upper().strip()

            # Split into street address and location parts
            parts = [p.strip() for p in address.split(",")]
            if not parts:
                return components

            # Parse street address part
            words = parts[0].split()

            # Get number if it exists and is numeric
            if words and words[0].isdigit():
                components["number"] = words[0]
                words = words[1:]
            else:
                # If first word isn't numeric, this might be an invalid address
                return components

            # Get direction if it's single letter or two letters
            if words and (
                len(words[0]) == 1
                or (len(words[0]) == 2 and words[0] in ["NW", "SW", "NE", "SE"])
            ):
                components["pre_direction"] = words[0].rstrip(".")
                words = words[1:]

            # Last word is likely street type
            if words:
                components["street_type"] = words[-1].rstrip(".")
                # Get street name from remaining words
                if len(words) > 1:
                    components["street_name"] = " ".join(words[:-1])

            # Parse city, state, zip if present
            if len(parts) > 1:
                location_parts = parts[1].strip().split()

                # Handle city
                if location_parts:
                    # Check if last part is a ZIP code
                    if location_parts[-1].isdigit() and len(location_parts[-1]) == 5:
                        components["zip"] = location_parts[-1]
                        location_parts = location_parts[:-1]

                    # Check if second-to-last part is a state
                    if len(location_parts) >= 2:
                        components["state"] = location_parts[-1]
                        components["city"] = " ".join(location_parts[:-1])
                    else:
                        components["city"] = " ".join(location_parts)

            # If there's a third part (often contains state and zip)
            if len(parts) > 2:
                state_zip = parts[2].strip().split()
                if len(state_zip) >= 1:
                    components["state"] = state_zip[0]
                if len(state_zip) >= 2 and state_zip[1].isdigit():
                    components["zip"] = state_zip[1]

        except (AttributeError, IndexError, TypeError):
            return components

        return components

    def get_variations(self) -> List[str]:
        """Generate basic address variations"""
        c = self.components
        variations = []

        # Just create a few basic variations
        if c["number"] and c["street_name"]:
            base = f"{c['number']} {c['pre_direction']} {c['street_name']}".strip()
            variations.append(f"{base} ST")
            variations.append(f"{base} STREET")

            if c["city"] and c["state"]:
                for var in variations[:]:
                    variations.append(f"{var}, {c['city']}, {c['state']}")
                    if c["zip"]:
                        variations.append(
                            f"{var}, {c['city']}, {c['state']} {c['zip']}"
                        )

        return variations

    def standardize(self) -> str:
        """Return address in standardized format"""
        if not self.text:
            return ""

        c = self.components

        # If we don't have a valid street number, return empty string
        if not c["number"]:
            return ""

        parts = []

        # Build street address
        parts.append(c["number"])
        if c["pre_direction"]:
            parts.append(c["pre_direction"])
        if c["street_name"]:
            parts.append(c["street_name"])
        if c["street_type"]:
            parts.append(c["street_type"])

        result = " ".join(parts)

        # Add city, state, zip if present
        if c["city"]:
            result += f", {c['city']}"
            if c["state"]:
                result += f", {c['state']}"
                if c["zip"]:
                    result += f" {c['zip']}"

        return result
