"""
Tests for paranoid_normalize and match_comune.
Pure-function tests need no DB; match_comune tests use the real eureka-dev DB.
"""
import pytest
from services.utils import paranoid_normalize, match_comune


# ---------------------------------------------------------------------------
# paranoid_normalize — pure function, no DB needed
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw, expected", [
    ("Arquà Polesine",       "ARQUAPOLESINE"),
    ("ARQUA` POLESINE",      "ARQUAPOLESINE"),   # backtick variant from real PDFs
    ("SAN DONÀ DI PIAVE",    "SANDONADIPIAVE"),
    ("Sant'Ambrogio",        "SANTAMBROGIO"),    # apostrophe
    ("San Donà di Piave",    "SANDONADIPIAVE"),  # mixed case + accent
    ("",                     ""),
    (None,                   ""),
    ("  ADRIA  ",            "ADRIA"),           # leading/trailing spaces
    ("Verona",               "VERONA"),
])
def test_paranoid_normalize(raw, expected):
    assert paranoid_normalize(raw) == expected


# ---------------------------------------------------------------------------
# match_comune — requires real DB
# ---------------------------------------------------------------------------

def test_match_comune_exact(db_session):
    result = match_comune(db_session, "Adria")
    assert result is not None
    assert paranoid_normalize(result.nome) == "ADRIA"


def test_match_comune_with_accent_variant(db_session):
    """PDF delivers "ARQUA` POLESINE"; DB stores "Arquà Polesine"."""
    result = match_comune(db_session, "ARQUA` POLESINE")
    assert result is not None
    assert paranoid_normalize(result.nome) == "ARQUAPOLESINE"


def test_match_comune_uppercase(db_session):
    """All-caps input as it appears in dettagliato PDFs."""
    result = match_comune(db_session, "ADRIA")
    assert result is not None


def test_match_comune_not_found(db_session):
    result = match_comune(db_session, "XYZNOTAPLACE999")
    assert result is None
