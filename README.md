# Mistaker

Mistaker is a Python package for emulating common data entry errors that arise from transcription, OCR and numerical data entry. Use the package to generate common variations of strings, numerics and dates you might find in older, hand entered data sets.

## Installation

You can install the package using pip:

```bash
pip install mistaker
```

## Usage

```python
from mistaker import Word, Name, Date, Number

Word.make_mistake("GRATEFUL")   # => "GRATEFU"
Word.make_mistake("GRATEFUL")   # => "GRATAFUL"
Word.make_mistake("GRATEFUL")   # => "GRAEFUL"
Word.make_mistake("GRATEFUL")   # => "GRATEFULL"

Name.make_mistake("KIM DEAL")   # => "KIM FEAL"
Name.make_mistake("KIM DEAL")   # => "KIM DEL"
Name.make_mistake("KIM DEAL")   # => "KIM DEALL"
Name.make_mistake("KIM DEAL")   # => "KIM DEAP"

Date.make_mistake("09/04/1982") # => "1928-09-04"
Date.make_mistake("09/04/1982") # => "0019-82-09"
Date.make_mistake("09/04/1982") # => "1932-09-04"

Number.make_mistake("12345")    # => "12335"
Number.make_mistake("12345")    # => "72345"
Number.make_mistake("12345")    # => "13345"
```

## Error Types

The package simulates various types of common data entry errors:

### For Words and Names:
- Dropped letters
- Double-entered letters
- Misread letters (similar looking characters)
- Mistyped letters (keyboard proximity errors)
- Extra letters
- Misheard letters (phonetic errors)

### For Numbers:
- Single digit errors (up/down)
- Numeric keypad errors
- Digit shifts
- Misread numbers
- Key swaps

### For Dates:
- All number-based errors
- Month/day swaps
- Decade shifts
- Y2K formatting issues

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/yourusername/mistaker. This project is intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the code of conduct.

## License

This package is available as open source under the terms of the MIT License.