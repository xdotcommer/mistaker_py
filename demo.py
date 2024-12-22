from mistaker import Date, Name, Number, Word, ErrorType
import random
from mistaker import Generator


def demonstrate_mistakes(iterations=10):
    # Sample data
    dates = ["2023-05-15", "1995-12-25", "2010-07-04"]
    names = ["Kim Deal", "María José García", "Robert Wilson PhD"]
    numbers = ["12345", "987654", "432100"]
    words = ["COMPUTER", "KEYBOARD", "MONITOR"]

    print("=== Date Mistakes ===")
    date_obj = Date()
    for _ in range(iterations):
        date_text = random.choice(dates)
        date_obj.text = date_text
        mistake = date_obj.mistake()  # Using random error type
        print(f"Original: {date_text} -> Mistake: {mistake}")

    print("\n=== Name Mistakes ===")
    name_obj = Name()
    for _ in range(iterations):
        name_text = random.choice(names)
        name_obj.text = name_text
        mistake = name_obj.mistake()  # Using random error type
        print(f"Original: {name_text} -> Mistake: {mistake}")

    print("\n=== Number Mistakes ===")
    number_obj = Number()
    for _ in range(iterations):
        number_text = random.choice(numbers)
        number_obj.text = number_text
        mistake = number_obj.mistake()  # Using random error type
        print(f"Original: {number_text} -> Mistake: {mistake}")

    print("\n=== Word Mistakes ===")
    word_obj = Word()
    for _ in range(iterations):
        word_text = random.choice(words)
        word_obj.text = word_text
        mistake = word_obj.mistake()  # Using random error type
        print(f"Original: {word_text} -> Mistake: {mistake}")

    print("\n=== Name Variations ===")
    for name_text in names:
        name_obj = Name(name_text)
        variations = name_obj.get_name_variations()
        print(f"Original: {name_text} -> Variations: {variations}")

    print("\n=== Name Case Variants ===")
    for name_text in names:
        name_obj = Name(name_text)
        case_variants = name_obj.get_case_variants()
        print(f"Original: {name_text} -> Case Variants: {case_variants}")

    print("\n=== Name Parts ===")
    for name_text in names:
        name_obj = Name(name_text)
        parts = name_obj.get_parts()
        print(f"Original: {name_text} -> Parts: {parts}")

    print("\n=== Chaos on Names ===")
    for name_text in names:
        name_obj = Name(name_text)
        print(f"Original: {name_text} -> Multiple Errors: {name_obj.chaos()}")


def demonstrate_generator():
    # Sample records
    records = [
        {
            "full_name": "John Q Smith",
            "dob": "1980-01-15",
            "phone": "555-123-4567",
            "email": "john.smith@email.com",
            "ssn": "123-45-6789",
            "dl_num": "S123456789",
            "full_address": "123 Main St, Portland, OR 97201",
        },
        {
            "full_name": "Mary Jane Wilson",
            "dob": "1992-07-23",
            "phone": "555-987-6543",
            "email": "mary.wilson@email.com",
            "ssn": "987-65-4321",
            "dl_num": "W987654321",
            "full_address": "456 Oak Ave, Portland, OR 97202",
        },
    ]

    # Basic usage
    print("\n=== Basic Generator Usage ===")
    generator = Generator()
    for record in records:
        print("\nOriginal Record:")
        print(record)
        print("\nGenerated Variations:")
        for variant in generator.generate(record):
            print(variant)

    # Custom configuration
    print("\n=== Custom Configuration ===")
    config = {
        "min_duplicates": 1,
        "max_duplicates": 3,
        "min_chaos": 2,
        "max_chaos": 4,
        "missing_weights": {"phone": 0.3, "email": 0.2},
    }
    custom_generator = Generator(config=config)
    record = records[0]
    print("\nUsing Custom Config:")
    for variant in custom_generator.generate(record):
        print(variant)

    # Batch processing
    print("\n=== Batch Processing ===")
    generator = Generator()
    all_variants = list(generator.generate_all(records))
    print(f"Generated {len(all_variants)} total records from {len(records)} originals")


if __name__ == "__main__":
    test_names = ["Robert James Wilson", "María José García", "Kim Deal"]
    for name_text in test_names:
        name = Name(name_text)
        variations = name.get_name_variations()
        print(f"\nVariations for {name_text}:")
        for v in variations:
            print(f"  {v}")
    # demonstrate_mistakes()
    # demonstrate_generator()
