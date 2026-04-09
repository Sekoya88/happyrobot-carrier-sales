"""MC number normalization and format checks (FMCSA-style identifiers for the PoC)."""

import re

# US MC numbers are typically 6–7 digits; allow 6–8 for edge cases in testing.
MC_MIN_LEN = 6
MC_MAX_LEN = 8


def normalize_mc_digits(raw: str) -> str:
    """Keep only ASCII digits (strips spaces, hyphens, letters, etc.)."""
    if not raw:
        return ""
    return re.sub(r"\D", "", raw.strip())


def is_valid_mc_format(digits: str) -> bool:
    if not digits:
        return False
    if len(digits) < MC_MIN_LEN or len(digits) > MC_MAX_LEN:
        return False
    return digits.isdigit()
