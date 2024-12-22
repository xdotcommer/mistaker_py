from mistaker import Date, Name, Number, Word, ErrorType
import random


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


if __name__ == "__main__":
    demonstrate_mistakes()
