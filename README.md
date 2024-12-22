# Mistaker

Mistaker is a Python package designed to emulate common data entry errors that occur in real-world datasets. It's particularly useful for testing data quality tools, generating synthetic training data, and simulating typical mistakes found in OCR output, manual transcription, and legacy data migration projects.

## Features

- Simulate common transcription and data entry errors for:
  - Text strings and words
  - Personal names and business names
  - Dates in various formats
  - Numeric data
- Configurable error types and rates
- Support for multiple input formats
- Preserves data structure while introducing realistic errors
- Deterministic error generation available for testing

## Installation

Install using pip:

```bash
pip install mistaker
```

For development installation:

```bash
pip install -e ".[test]"
```

## Quick Start

```python
from mistaker import Word, Name, Date, Number

# Generate word variations
Word.make_mistake("GRATEFUL")   # => "GRATEFU"
Word.make_mistake("GRATEFUL")   # => "GRATAFUL"

# Generate name variations with common mistakes
Name.make_mistake("KIM DEAL")   # => "KIM FEAL"
Name.make_mistake("KIM DEAL")   # => "KIM DEL"
Name("KIM DEAL").chaos()        # => "DEELLL KIN"

# Generate date formatting errors and typos
Date.make_mistake("09/04/1982") # => "1928-09-04"
Date.make_mistake("09/04/1982") # => "0019-82-09"

# Generate numeric transcription errors
Number.make_mistake("12345")    # => "12335"
Number.make_mistake("12345")    # => "72345"
```

## Detailed Usage

### Word and Text Errors

```python
from mistaker import Word, ErrorType

# Create a word instance
word = Word("TESTING")

# Generate specific error types
word.mistake(ErrorType.DROPPED_LETTER)  # => "TESTNG"
word.mistake(ErrorType.DOUBLE_LETTER)   # => "TESSTING"
word.mistake(ErrorType.MISREAD_LETTER)  # => "TEZTING"
word.mistake(ErrorType.MISTYPED_LETTER) # => "TEDTING"
word.mistake(ErrorType.EXTRA_LETTER)    # => "TESTINGS"
word.mistake(ErrorType.MISHEARD_LETTER) # => "TEZDING"
```

### Name Handling

```python
from mistaker import Name

# Create a name instance
name = Name("Robert James Smith")

# Generate name variations
variations = name.get_name_variations()
# Returns variations like:
# - "Smith, Robert"
# - "R James Smith"
# - "Robert Smith"
# - "Smith Robert"

# Generate case variants
cases = name.get_case_variants()
# Returns:
# - "Robert James Smith"
# - "ROBERT JAMES SMITH"
# - "robert james smith"

# Generate multiple errors
name.chaos()  # Applies 1-6 random errors
# John Smith -> JAHN SMEH
```

### Date Handling

```python
from mistaker import Date

# Create a date instance
date = Date("2023-05-15")

# Supports multiple input formats
date = Date("05/15/2023")  # US format
date = Date("15/05/2023")  # UK format

# Generate specific error types
date.mistake(ErrorType.MONTH_DAY_SWAP)    # => "2023-15-05"
date.mistake(ErrorType.ONE_DECADE_DOWN)   # => "2013-05-15"
date.mistake(ErrorType.Y2K)               # => "0023-05-15"
```

### Number Handling

```python
from mistaker import Number

# Create a number instance
number = Number("12345")

# Generate specific error types
number.mistake(ErrorType.ONE_DIGIT_UP)     # => "12346"
number.mistake(ErrorType.ONE_DIGIT_DOWN)   # => "12344"
number.mistake(ErrorType.KEY_SWAP)         # => "21345"
number.mistake(ErrorType.DIGIT_SHIFT)      # => "01234"
number.mistake(ErrorType.MISREAD)          # => "12375"
number.mistake(ErrorType.NUMERIC_KEY_PAD)  # => "12348"
```

## Error Types

### Text and Name Errors
- **Dropped Letters**: Missing characters (e.g., "testing" → "testng")
- **Double Letters**: Repeated characters (e.g., "testing" → "tessting")
- **Misread Letters**: Similar-looking character substitutions (e.g., "testing" → "tezting")
- **Mistyped Letters**: Keyboard proximity errors (e.g., "testing" → "tedting")
- **Extra Letters**: Common suffix additions (e.g., "test" → "tests")
- **Misheard Letters**: Phonetic errors (e.g., "testing" → "tesding")

### Number Errors
- **Single Digit Errors**: Off-by-one errors
- **Key Swaps**: Adjacent digit transposition
- **Digit Shifts**: Decimal/position shifts
- **Misread Numbers**: Similar-looking number substitution
- **Numeric Keypad Errors**: Based on number pad layout

### Date Errors
- **Month/Day Swaps**: Common in international formats
- **Decade Shifts**: Common in manual entry
- **Y2K Issues**: Two-digit year ambiguity
- **All Number-Based Errors**: Inherited from number handling

## Development

### Running Tests

```bash
pytest
```

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by real-world data quality challenges in government and enterprise systems
- Error patterns based on extensive analysis of common transcription mistakes
- Designed to support data quality testing and synthetic data generation