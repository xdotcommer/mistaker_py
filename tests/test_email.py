import pytest
from mistaker import Email
from mistaker.constants import ErrorType


def test_reformat():
    email = Email()
    # Test basic email - should always be lowercase
    assert email.reformat("Test@Example.com") == "test@example.com"
    # Test with special characters
    assert email.reformat("test.User@example.com") == "test.user@example.com"
    # Test with numbers (should preserve them but lowercase letters)
    assert email.reformat("user123@Test123.com") == "user123@test123.com"
    # Test empty string
    assert email.reformat("") == ""
    # Test invalid email
    assert email.reformat("notanemail") == "notanemail"
    assert email.reformat("test@") == "test@"
    assert email.reformat("@example.com") == "@example.com"


def test_make_mistake_classmethod():
    """Test the class method interface"""
    result = Email.make_mistake("test@example.com")
    assert result != "test@example.com"
    assert "@" in result
    assert isinstance(result, str)
    assert result == result.lower()


def test_mistake_prefix():
    """Test mistakes in the prefix part of email"""
    email = Email("test@example.com")
    result = email.mistake(ErrorType.DROPPED_LETTER, 1)
    assert result != "test@example.com"
    assert "@example.com" in result
    assert isinstance(result, str)
    assert result == result.lower()


def test_mistake_domain():
    """Test mistakes in the domain part of email"""
    email = Email("test@example.com")
    result = email.mistake(ErrorType.DROPPED_LETTER, 6)
    assert result != "test@example.com"
    assert "test@" in result
    assert ".com" in result
    assert isinstance(result, str)
    assert result == result.lower()


def test_preserve_tld():
    """Test that TLD (.com, .org, etc.) is preserved"""
    email = Email("test@example.com")
    result = email.mistake()
    assert result.endswith(".com")

    email = Email("test@example.org")
    result = email.mistake()
    assert result.endswith(".org")


def test_empty_email():
    email = Email("")
    assert email.mistake() == ""


def test_multiple_mistakes():
    """Test that multiple runs produce different results"""
    email = Email("test@example.com")
    results = set()
    for _ in range(50):
        results.add(email.mistake())
    # Should get multiple different results
    assert len(results) > 1
    # Verify all results are lowercase
    assert all(result == result.lower() for result in results)


def test_mistake_distribution():
    """Test that mistakes occur in both prefix and domain but not TLD"""
    email = Email("test@example.com")
    prefix_changed = False
    domain_changed = False
    samples = 100

    for _ in range(samples):
        result = email.mistake()
        # Split both original and result into parts
        orig_prefix, orig_rest = "test", "example.com"
        result_prefix, result_rest = result.split("@")

        # Check if prefix was modified
        if result_prefix != orig_prefix:
            prefix_changed = True

        # Check if domain (not including TLD) was modified
        result_domain = result_rest.rsplit(".", 1)[0]
        if result_domain != "example":
            domain_changed = True

        # Verify TLD remains unchanged
        assert result.endswith(".com")
        # Verify result is lowercase
        assert result == result.lower()

        if prefix_changed and domain_changed:
            break

    assert prefix_changed, "No mistakes were made in the prefix part"
    assert domain_changed, "No mistakes were made in the domain part"


def test_email_always_lowercase():
    """Test that emails are always converted to lowercase"""
    email = Email()
    # Test mixed case inputs
    assert email.reformat("Test@Example.com") == "test@example.com"
    assert email.reformat("TEST.USER@EXAMPLE.COM") == "test.user@example.com"
    assert (
        email.reformat("Mixed.Case.EMAIL@Testing.COM") == "mixed.case.email@testing.com"
    )

    # Test that mistake output is also lowercase
    email = Email("Test@Example.com")
    result = email.mistake()
    assert result == result.lower(), "Email mistake should be lowercase"

    # Test multiple mistakes to ensure they're all lowercase
    for _ in range(10):
        result = Email("TEST@EXAMPLE.COM").mistake()
        assert result == result.lower(), "All email mistakes should be lowercase"


def test_tld_variations():
    """Test that various TLDs are preserved"""
    tlds = [".com", ".org", ".edu", ".net", ".co.uk"]

    for tld in tlds:
        email = Email(f"test@example{tld}")
        for _ in range(10):
            result = email.mistake()
            assert result.endswith(tld.lower()), f"TLD {tld} was not preserved"
            # Verify that the rest of the email can be modified
            if result != f"test@example{tld}".lower():
                break
        else:
            pytest.fail(f"No mistakes were made in email with TLD {tld}")
