# Mistaker

Mistaker is a Python package designed to emulate common data entry errors that occur in real-world datasets. It's particularly useful for testing data quality tools, generating synthetic training data, and simulating typical mistakes found in OCR output, manual transcription, and legacy data migration projects.

## Features

- Simulate common transcription and data entry errors for:
  - Text strings and words
  - Personal names and business names
  - Dates in various formats
  - Numeric data
  - Addresses and locations
- Configurable error types and rates
- Support for multiple input formats
- Preserves data structure while introducing realistic errors
- Deterministic error generation available for testing

## Installation

```bash
pip install mistaker
```

## Quick Start

### Command Line
Generate variations with mistakes from your CSV data:

```bash
# Basic usage
mistaker data.csv > output.csv

# Using standard input
cat data.csv | mistaker > output.csv

# The tool will automatically use config.json from current directory if it exists
# Or specify a custom config file:
mistaker data.csv -c custom_config.json

# Adjust mistake generation via command line
mistaker data.csv --min-duplicates 3 --max-duplicates 6 --min-chaos 1 --max-chaos 3
```

## Configuration

Control the mistake generation process via a JSON configuration file:

```json
{
    "min_duplicates": 2,
    "max_duplicates": 5,
    "min_chaos": 1,
    "max_chaos": 4,
    "missing_weights": {
        "full_name": 0.05,
        "dob": 0.1,
        "phone": 0.8,
        "email": 0.95,
        "ssn": 0.9,
        "dl_num": 0.5,
        "full_address": 0.1
    },
    "mistake_weights": {
        "full_name": 1.0,
        "dob": 1.0,
        "phone": 1.0,
        "email": 1.0,
        "ssn": 1.0,
        "dl_num": 1.0,
        "full_address": 1.0
    }
}
```

## Supported Fields

Mistaker handles these fields with field-specific error patterns:

- `full_name`: Name variations and misspellings
- `dob`: Date format errors and typos
- `phone`: Number transpositions and formatting errors
- `ssn`: Number mistakes preserving SSN patterns
- `dl_num`: Alphanumeric mistakes for driver's licenses
- `email`: Username and domain-specific errors
- `full_address`: Address component errors with street numbers, names, suffixes, unit numbers, and directional prefixes

## Advanced Usage

### Python API

```python
from mistaker import Generator

# Create generator with defaults
generator = Generator()

# Process a single record
record = {
    'full_name': 'John Smith',
    'dob': '1990-01-01',
    'phone': '555-123-4567',
    'full_address': '123 N Main St Apt 4B'
}

variations = generator.generate(record)  # Returns list with original + variations

# Process multiple records
records = [record1, record2, record3]
for variation in generator.generate_all(records):
    print(variation)
```

### Python API Options

```python
# Initialize with custom settings
generator = Generator(
    min_duplicates=3,
    max_duplicates=6,
    min_chaos=2,
    max_chaos=4
)

# Load from config file
generator = Generator.from_file('config.json')

# Custom configuration
config = {
    'missing_weights': {
        'full_name': 0.05,
        'phone': 0.2
    }
}
generator = Generator(config=config)
```

### CLI Options

```bash
mistaker --help

usage: mistaker [input_file] [options]

options:
  -h, --help           show this help message and exit
  -c, --config CONFIG  configuration JSON file path
  --min-duplicates N   minimum number of variations per record
  --max-duplicates N   maximum number of variations per record
  --min-chaos N        minimum number of mistakes per field
  --max-chaos N        maximum number of mistakes per field
  -v, --version        show program's version number and exit
```

## Basic Examples

```python
from mistaker import Word, Name, Date, Number, Address

# Generate word variations
Word("GRATEFUL").mistake()   # => "GRATEFU"
Word("GRATEFUL").mistake()   # => "GRATAFUL"

# Generate name variations with common mistakes
Name("KIM DEAL").mistake()   # => "KIM FEAL"
Name("KIM DEAL").mistake()   # => "KIM DEL"
Name("KIM DEAL").chaos()     # => "DEELLL KIN"

# Generate date formatting errors and typos
Date("09/04/1982").mistake() # => "1928-09-04"
Date("09/04/1982").mistake() # => "0019-82-09"

# Generate numeric transcription errors
Number("12345").mistake()    # => "12335"
Number("12345").mistake()    # => "72345"

# Generate address variations and errors
Address("123 N Main St Apt 4B").mistake()  # => "123 N MANE ST APT 4D"
Address("456 South Oak Avenue").mistake()  # => "456 S OAK AVE"
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

### Address Handling

```python
from mistaker import Address

# Create an address instance
address = Address("123 North Main Street Suite 100")

# Generate mistakes with automatic component handling
address.mistake()  # => "123 N MANE ST STE 102"

# Standardize address format
address.standardize()  # => "123 N MAIN ST STE 100"

# Handles various address components:
# - Street numbers
# - Directional prefixes (N, S, E, W, NE, NW, SE, SW)
# - Street names
# - Street suffixes (St, Ave, Rd, etc.)
# - Unit designators (Suite, Apt, Unit, etc.)
# - Unit numbers
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

### Address Errors
- **Component Dropping**: Omitting address parts (suffixes, unit numbers)
- **Standardization Issues**: Inconsistent formatting of prefixes and suffixes
- **Number Errors**: Street number and unit number mistakes
- **Text Errors**: Street name misspellings and variations
- **Unit Formatting**: Inconsistent unit designator abbreviations

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