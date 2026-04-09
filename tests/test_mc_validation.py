import pytest

from infrastructure.mc_validation import normalize_mc_digits, is_valid_mc_format


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("123456", "123456"),
        ("MC 123 456", "123456"),
        ("12-34-56", "123456"),
        ("", ""),
        ("abc", ""),
        ("a b c", ""),
    ],
)
def test_normalize_mc_digits(raw, expected):
    assert normalize_mc_digits(raw) == expected


@pytest.mark.parametrize(
    "digits,ok",
    [
        ("123456", True),
        ("1234567", True),
        ("12345678", True),
        ("12345", False),
        ("0000", False),
        ("0", False),
        ("", False),
        ("123456789", False),
    ],
)
def test_is_valid_mc_format(digits, ok):
    assert is_valid_mc_format(digits) is ok
