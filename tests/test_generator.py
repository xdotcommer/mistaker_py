import pytest
from mistaker import Generator


def test_generator_defaults():
    """Test generator initialization with defaults"""
    generator = Generator()
    assert generator.config["min_duplicates"] == 2
    assert generator.config["max_duplicates"] == 5
    assert generator.config["min_chaos"] == 1
    assert generator.config["max_chaos"] == 3
    assert isinstance(generator.config["missing_weights"], dict)


def test_generator_custom_config():
    """Test generator initialization with custom config"""
    config = {
        "min_duplicates": 3,
        "max_duplicates": 4,
        "min_chaos": 2,
        "max_chaos": 3,
        "missing_weights": {"full_name": 0.1},
    }
    generator = Generator(config=config)
    assert generator.config["min_duplicates"] == 3
    assert generator.config["max_duplicates"] == 4
    assert generator.config["min_chaos"] == 2
    assert generator.config["max_chaos"] == 3
    assert generator.config["missing_weights"]["full_name"] == 0.1


def test_invalid_config():
    """Test generator validation of invalid configs"""
    # Test min > max duplicates
    with pytest.raises(ValueError):
        Generator(min_duplicates=5, max_duplicates=3)

    # Test min > max chaos
    with pytest.raises(ValueError):
        Generator(min_chaos=4, max_chaos=2)

    # Test invalid missing weight
    with pytest.raises(ValueError):
        Generator(config={"missing_weights": {"full_name": 1.5}})


def test_generate_single_record():
    """Test generation of variations for a single record"""
    generator = Generator(min_duplicates=1, max_duplicates=1)
    record = {
        "full_name": "John Smith",
        "phone": "555-1234",
    }

    results = generator.generate(record)
    assert len(results) == 2  # Original + 1 duplicate
    assert results[0] == record  # First record should be original
    assert results[1] != record  # Second should have mistakes


def test_generate_all():
    """Test generation of variations for multiple records"""
    generator = Generator(min_duplicates=1, max_duplicates=1)
    records = [
        {"full_name": "John Smith", "phone": "555-1234"},
        {"full_name": "Jane Doe", "phone": "555-5678"},
    ]

    results = list(generator.generate_all(records))
    assert len(results) == 4  # (Original + 1 duplicate) * 2 records
    assert results[0] == records[0]  # First should be original
    assert results[2] == records[1]  # Third should be original of second record


def test_missing_fields():
    """Test handling of missing fields in records"""
    generator = Generator(
        config={"missing_weights": {"full_name": 1.0}}  # Always make full_name missing
    )
    record = {"full_name": "John Smith", "phone": "555-1234"}

    results = generator.generate(record)
    assert any(
        r["full_name"] == "" for r in results[1:]
    )  # Some variations should have empty full_name


def test_unknown_fields():
    """Test handling of fields not in SUPPORTED_FIELDS"""
    generator = Generator()
    record = {"unknown_field": "some value", "full_name": "John Smith"}

    results = generator.generate(record)
    assert all("unknown_field" in r for r in results)  # Field should be preserved
    assert all(
        r["unknown_field"] == "some value" for r in results
    )  # Value shouldn't change


def test_empty_record():
    """Test handling of empty records"""
    generator = Generator()
    record = {}

    results = generator.generate(record)
    assert len(results) > 0
    assert all(isinstance(r, dict) for r in results)


def test_from_file(tmp_path):
    """Test loading configuration from file"""
    # Create temporary config file
    config_file = tmp_path / "config.json"
    config_file.write_text('{"min_duplicates": 3, "max_duplicates": 4}')

    generator = Generator.from_file(str(config_file))
    assert generator.config["min_duplicates"] == 3
    assert generator.config["max_duplicates"] == 4


def test_from_file_missing():
    """Test graceful handling of missing config file"""
    generator = Generator.from_file("nonexistent.json")
    assert isinstance(generator, Generator)  # Should create with defaults
