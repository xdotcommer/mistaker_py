import csv
import json
import random
import sys
import io
from pathlib import Path
from typing import Dict, List, Any, Set
import argparse
from mistaker import Name, Date, Number, Word


class DataMistakeGenerator:
    SUPPORTED_FIELDS = {
        "full_name",
        "dob",
        "phone",
        "email",
        "ssn",
        "dl_num",
        "full_address",
    }

    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.validate_config()

    def load_config(self, config_path: str) -> Dict:
        """Load and normalize config file"""
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            print(
                f"Warning: Config file {config_path} not found. Using defaults.",
                file=sys.stderr,
            )
            config = {}

        # Set defaults if not provided
        config.setdefault("min_duplicates", 2)
        config.setdefault("max_duplicates", 5)
        config.setdefault("min_chaos", 1)
        config.setdefault("max_chaos", 3)
        config.setdefault("missing_weights", {})
        config.setdefault("mistake_weights", {})

        # Ensure all supported fields have weights
        for field in self.SUPPORTED_FIELDS:
            config["missing_weights"].setdefault(field, 0.1)
            config["mistake_weights"].setdefault(field, 1.0)

        return config

    def validate_config(self):
        """Validate config values"""
        if self.config["min_duplicates"] > self.config["max_duplicates"]:
            raise ValueError("min_duplicates cannot be greater than max_duplicates")

        if self.config["min_chaos"] > self.config["max_chaos"]:
            raise ValueError("min_chaos cannot be greater than max_chaos")

        # Validate missing weights are between 0 and 1
        for field, weight in self.config["missing_weights"].items():
            if not 0 <= weight <= 1:
                print(
                    f"Warning: Missing weight for {field} ({weight}) not between 0 and 1. Using 0.1",
                    file=sys.stderr,
                )
                self.config["missing_weights"][field] = 0.1

    def should_field_be_missing(self, field: str) -> bool:
        """Determine if a field should be missing based on its weight"""
        weight = self.config["missing_weights"].get(field, 0.1)
        return random.random() < weight

    def generate_mistakes(self, row: Dict[str, str]) -> Dict[str, str]:
        """Generate mistakes for a single row based on chaos level"""
        new_row = row.copy()
        chaos_level = random.randint(self.config["min_chaos"], self.config["max_chaos"])

        # First, handle missing fields
        for field in new_row:
            if not new_row[field] or self.should_field_be_missing(field):
                new_row[field] = ""
                continue

            try:
                if field == "full_name":
                    name = Name(new_row[field])
                    for _ in range(chaos_level):
                        new_row[field] = name.mistake()

                elif field == "dob":
                    date = Date(new_row[field])
                    for _ in range(chaos_level):
                        new_row[field] = date.mistake()

                elif field == "phone" or field == "ssn":
                    number = Number(new_row[field])
                    for _ in range(chaos_level):
                        new_row[field] = number.mistake()

                elif field == "email":
                    if "@" in new_row[field]:
                        username, domain = new_row[field].split("@")
                        username_word = Word(username)
                        domain_word = Word(domain)
                        for _ in range(chaos_level):
                            new_username = username_word.mistake()
                            new_domain = domain_word.mistake()
                            new_row[field] = f"{new_username}@{new_domain}"

                elif field == "dl_num":
                    dl = Word(new_row[field])
                    for _ in range(chaos_level):
                        new_row[field] = dl.mistake()

                elif field == "full_address":
                    parts = new_row[field].split(",")
                    new_parts = []
                    for part in parts:
                        word = Word(part.strip())
                        new_part = part
                        for _ in range(chaos_level):
                            new_part = word.mistake()
                        new_parts.append(new_part)
                    new_row[field] = ", ".join(new_parts)

            except (ValueError, AttributeError) as e:
                print(
                    f"Warning: Error processing field {field}: {str(e)}",
                    file=sys.stderr,
                )
                # Keep original value on error
                pass

        return new_row

    def process_file(self, input_path: str):
        output_wrapper = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", newline="", write_through=True
        )

        try:
            with open(input_path, "r", newline="") as infile:
                reader = csv.DictReader(infile)
                if not reader.fieldnames:
                    raise ValueError("Input CSV file has no headers")

                writer = csv.DictWriter(output_wrapper, fieldnames=reader.fieldnames)
                writer.writeheader()

                for row in reader:
                    # Write original row
                    writer.writerow(row)

                    # Generate duplicates with mistakes
                    num_duplicates = random.randint(
                        self.config["min_duplicates"], self.config["max_duplicates"]
                    )

                    for _ in range(num_duplicates):
                        mistake_row = self.generate_mistakes(row)
                        writer.writerow(mistake_row)

        except BrokenPipeError:
            sys.stderr.close()
        finally:
            output_wrapper.detach()


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic data with realistic mistakes"
    )
    parser.add_argument(
        "--input", default="mistake_generator.csv", help="Input CSV file path"
    )
    parser.add_argument(
        "--config",
        default="mistake_generator.json",
        help="Configuration JSON file path",
    )

    args = parser.parse_args()

    try:
        generator = DataMistakeGenerator(args.config)
        generator.process_file(args.input)
    except FileNotFoundError as e:
        print(f"Error: Could not find file '{e.filename}'", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
