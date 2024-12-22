from typing import Dict, List, Optional, Iterator
import random
import json
from .address import Address
from .word import Word
from .name import Name
from .date import Date
from .number import Number


class Generator:
    """
    Core generator class for creating realistic data entry mistakes
    """

    SUPPORTED_FIELDS = {
        "full_name",
        "dob",
        "phone",
        "email",
        "ssn",
        "dl_num",
        "full_address",
    }

    def __init__(
        self,
        config: Optional[Dict] = None,
        min_duplicates: int = 2,
        max_duplicates: int = 5,
        min_chaos: int = 1,
        max_chaos: int = 3,
    ):
        """Initialize the generator with configuration"""
        self.config = self._normalize_config(config or {})
        # Remove this update that was overwriting config values
        if config:
            self.config.update(
                {
                    "min_duplicates": config.get("min_duplicates", min_duplicates),
                    "max_duplicates": config.get("max_duplicates", max_duplicates),
                    "min_chaos": config.get("min_chaos", min_chaos),
                    "max_chaos": config.get("max_chaos", max_chaos),
                }
            )
        else:
            self.config.update(
                {
                    "min_duplicates": min_duplicates,
                    "max_duplicates": max_duplicates,
                    "min_chaos": min_chaos,
                    "max_chaos": max_chaos,
                }
            )
        self.validate_config()

    @classmethod
    def from_file(cls, config_path: Optional[str] = None) -> "Generator":
        """
        Create a Generator instance from a config file.
        If no config_path provided, looks for config.json in current directory.
        """
        # First try provided path
        if config_path:
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    return cls(config=config)
            except FileNotFoundError:
                pass

        # Then try config.json in current directory
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                return cls(config=config)
        except FileNotFoundError:
            return cls()  # Use defaults if no config found

    def _normalize_config(self, config: Dict) -> Dict:
        """Normalize configuration with defaults"""
        # Ensure all config sections exist
        config.setdefault("missing_weights", {})
        config.setdefault("field_weights", {})

        # Set default weights for all supported fields
        for field in self.SUPPORTED_FIELDS:
            config["missing_weights"].setdefault(field, 0.1)
            config["field_weights"].setdefault(field, 1.0)

        return config

    def validate_config(self):
        """Validate configuration values"""
        if self.config["min_duplicates"] > self.config["max_duplicates"]:
            raise ValueError("min_duplicates cannot be greater than max_duplicates")

        if self.config["min_chaos"] > self.config["max_chaos"]:
            raise ValueError("min_chaos cannot be greater than max_chaos")

        # Validate missing weights are between 0 and 1
        for field, weight in self.config["missing_weights"].items():
            if not 0 <= weight <= 1:
                raise ValueError(
                    f"Missing weight for {field} ({weight}) not between 0 and 1"
                )

    def should_field_be_missing(self, field: str) -> bool:
        """Determine if a field should be missing based on its weight"""
        weight = self.config["missing_weights"].get(field, 0.1)
        return random.random() < weight

    def generate_mistakes(self, record: Dict[str, str]) -> Dict[str, str]:
        """Generate mistakes for a single record with improved nickname handling"""
        new_record = record.copy()
        chaos_level = random.randint(self.config["min_chaos"], self.config["max_chaos"])

        for field in self.SUPPORTED_FIELDS:
            if field not in new_record:
                continue

            if not new_record[field] or self.should_field_be_missing(field):
                new_record[field] = ""
                continue

            try:
                if field == "full_name":
                    name = Name(new_record[field])

                    # First, decide if we want to use a nickname variation as the base
                    if random.random() < 0.3:  # 30% chance to start with a nickname
                        variations = name.get_name_variations()
                        nickname_variations = [v for v in variations if v != name.text]
                        if nickname_variations:
                            name.text = random.choice(nickname_variations)

                    # Now apply sequential mistakes
                    for _ in range(chaos_level):
                        # During each iteration, we might:
                        # 1. Apply a nickname transformation (20% chance)
                        # 2. Apply a standard mistake (80% chance)
                        if random.random() < 0.2:
                            variations = name.get_name_variations()
                            valid_variations = [
                                v
                                for v in variations
                                if v != name.text and len(v.split()) >= 2
                            ]
                            if valid_variations:
                                name.text = random.choice(valid_variations)
                        else:
                            # Apply standard mistake (transcription error)
                            name.text = name.mistake()

                    new_record[field] = name.text

                elif field == "dob":
                    date = Date(new_record[field])
                    for _ in range(chaos_level):
                        new_record[field] = date.mistake()

                elif field == "phone" or field == "ssn":
                    number = Number(new_record[field])
                    for _ in range(chaos_level):
                        new_record[field] = number.mistake()

                elif field == "email":
                    if "@" in new_record[field]:
                        username, domain = new_record[field].split("@")
                        username_word = Word(username)
                        domain_word = Word(domain)
                        for _ in range(chaos_level):
                            new_username = username_word.mistake()
                            new_domain = domain_word.mistake()
                            new_record[field] = f"{new_username}@{new_domain}"

                elif field == "dl_num":
                    dl = Word(new_record[field])
                    for _ in range(chaos_level):
                        new_record[field] = dl.mistake()

                elif field == "full_address":
                    address = Address(new_record[field])
                    for _ in range(chaos_level):
                        new_record[field] = address.mistake()

            except (ValueError, AttributeError) as e:
                print(f"Warning: Error processing field {field}: {str(e)}")
                pass

        return new_record

    def generate(self, record: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Generate a list of records with mistakes from a single record

        Args:
            record: Dictionary containing the original record data

        Returns:
            List of dictionaries containing the original and modified records
        """
        results = [record]  # Include original record

        num_duplicates = random.randint(
            self.config["min_duplicates"], self.config["max_duplicates"]
        )

        for _ in range(num_duplicates):
            mistake_record = self.generate_mistakes(record)
            results.append(mistake_record)

        return results

    def generate_all(
        self, records: Iterator[Dict[str, str]]
    ) -> Iterator[Dict[str, str]]:
        """
        Generate mistakes for multiple records

        Args:
            records: Iterator of dictionaries containing the original records

        Yields:
            Modified records with mistakes, including originals
        """
        for record in records:
            yield from self.generate(record)
