"""
Unit tests for the regex patterns used in pdf_parser.py.
No PDF file or DB needed — these test the regex logic in isolation.
"""
import re
import pytest

# Patterns copied from pdf_parser.py
RE_COMUNE = re.compile(r'^([A-Z\s\'`\-]{3,})\s\(([A-Z]{2})\)$')
RE_AVEPA  = re.compile(r'\((\d{3}-\d{3}-\d{3}-\d{3}-\d{3})\)')
RE_PREFIX_SURFACE = re.compile(r'^(?:ciclo|senza|rotazione).*?\s+(\d+)$', re.IGNORECASE)
RE_RIEPILOGO = re.compile(r'^([^-(\n]+)\([A-Z]{2}\)\s+-\s+(.*?)\s+(\d+)$')


# ---------------------------------------------------------------------------
# Comune regex
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("line", [
    "ADRIA (RO)",
    "VERONA (VR)",
    "SAN DONA` DI PIAVE (VE)",
    "ARQUA' POLESINE (RO)",
])
def test_re_comune_matches_valid_lines(line):
    assert RE_COMUNE.match(line), f"Expected match for: {line!r}"


@pytest.mark.parametrize("line", [
    "8 00132 114 non irrigua ciclo annuale 3000 (002-011-000-000-392) N N",
    "Campagna 2025",
    "",
    "ADRIA",
])
def test_re_comune_no_match_on_data_lines(line):
    assert not RE_COMUNE.match(line), f"Expected no match for: {line!r}"


# ---------------------------------------------------------------------------
# AVEPA code regex
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("line, expected_code", [
    ("8 00132 114 non irrigua ciclo annuale 3000 (002-011-000-000-392) N N", "002-011-000-000-392"),
    ("15 00200 ciclo annuale 5000 (001-001-000-000-001) S N",               "001-001-000-000-001"),
])
def test_re_avepa_extracts_code(line, expected_code):
    m = RE_AVEPA.search(line)
    assert m is not None
    assert m.group(1) == expected_code


def test_re_avepa_no_match_on_commune_line():
    assert RE_AVEPA.search("ADRIA (RO)") is None


# ---------------------------------------------------------------------------
# Surface prefix regex
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("line, expected_surface", [
    ("ciclo annuale 5000",           "5000"),
    ("senza irrigazione 12345",      "12345"),
    ("rotazione normale 300",        "300"),
    ("CICLO ANNUALE 1000",           "1000"),
])
def test_re_prefix_surface_extracts_number(line, expected_surface):
    m = RE_PREFIX_SURFACE.search(line)
    assert m is not None, f"No match on: {line!r}"
    assert m.group(1) == expected_surface


# ---------------------------------------------------------------------------
# Riepilogativo per Comune e Coltura regex
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("line, comune, descrizione, superficie", [
    (
        "ADRIA (RO) - FRUMENTO TENERO BOLOGNA 15000",
        "ADRIA ",
        "FRUMENTO TENERO BOLOGNA",
        "15000",
    ),
])
def test_re_riepilogo_parses_line(line, comune, descrizione, superficie):
    m = RE_RIEPILOGO.search(line)
    assert m is not None
    assert m.group(1) == comune
    assert m.group(2) == descrizione
    assert m.group(3) == superficie
