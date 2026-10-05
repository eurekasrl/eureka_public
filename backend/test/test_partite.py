"""
Tests for the partite generation algorithm.

generate_partite_draft_logic takes a DB session; we call it with a real
ragione_sociale_id that has PUD rows in eureka-dev.
The session is rolled back after each test so no data is written.

If no PUD rows exist for the provided ID the draft will be empty — that is
still a valid (non-crashing) result and we assert on structure only.
"""
import pytest
from services.partite import generate_partite_draft_logic, MAX_PARTITA_SURFACE


# ---------------------------------------------------------------------------
# Pure-logic tests — no DB, use synthetic PUD-like objects
# ---------------------------------------------------------------------------

class FakePUD:
    """Minimal stand-in for a PianoUtilizzoDettagliato ORM row."""
    def __init__(self, condifesa_id, anno, codice_comune, prodotto_id,
                 foglio, particella, superficie,
                 serra=False, bio=False, secondo_raccolto=False,
                 comune=None, prodotto=None):
        self.condifesa_id = condifesa_id
        self.anno = anno
        self.codice_comune = codice_comune
        self.prodotto_id = prodotto_id
        self.foglio = foglio
        self.particella = particella
        self.superficie = superficie
        self.serra = serra
        self.bio = bio
        self.secondo_raccolto = secondo_raccolto
        self.comune = comune
        self.prodotto = prodotto
        self.id = f"{codice_comune}-{foglio}-{particella}"


def _run_algorithm(puds: list) -> list:
    """Run the partite algorithm directly on a list without a DB call."""
    from services import partite as partite_mod

    original = partite_mod.get_piani_utilizzo_dettagliati_by_ragione_sociale

    try:
        # Signature now includes anno (defaults to None) — accept and ignore it here.
        partite_mod.get_piani_utilizzo_dettagliati_by_ragione_sociale = lambda db, rs_id, anno=None: puds
        result = generate_partite_draft_logic(db=None, ragione_sociale_id="fake", anno=2025)
    finally:
        partite_mod.get_piani_utilizzo_dettagliati_by_ragione_sociale = original

    return result


def _make_puds(surfaces, foglio=1, comune="001"):
    return [
        FakePUD("c1", 2025, comune, "p1", foglio, str(i), s)
        for i, s in enumerate(surfaces)
    ]


def test_empty_puds_returns_empty_draft():
    assert _run_algorithm([]) == []


def test_single_small_plot_creates_one_partita():
    puds = _make_puds([5000])
    draft = _run_algorithm(puds)
    assert len(draft) == 1
    assert draft[0]["numero_partita"] == 1
    assert draft[0]["superficie_assegnata"] == 5000
    assert draft[0]["is_split"] is False


def test_plot_exceeding_max_is_split():
    """A single plot larger than MAX_PARTITA_SURFACE must produce two rows."""
    puds = _make_puds([MAX_PARTITA_SURFACE + 1000])
    draft = _run_algorithm(puds)
    assert len(draft) == 2
    total = sum(r["superficie_assegnata"] for r in draft)
    assert total == MAX_PARTITA_SURFACE + 1000
    # First fragment should be flagged as split
    assert draft[0]["is_split"] is True


def test_foglio_change_increments_partita_number():
    """Two plots with the same product but different foglio → partita increments."""
    puds = [
        FakePUD("c1", 2025, "001", "p1", foglio=1, particella="100", superficie=1000),
        FakePUD("c1", 2025, "001", "p1", foglio=2, particella="200", superficie=1000),
    ]
    draft = _run_algorithm(puds)
    assert draft[0]["numero_partita"] == 1
    assert draft[1]["numero_partita"] == 2


def test_product_change_resets_partita_number():
    """Switching to a different product resets partita numbering to 1."""
    puds = [
        FakePUD("c1", 2025, "001", "p1", foglio=2, particella="200", superficie=1000),
        FakePUD("c1", 2025, "001", "p2", foglio=1, particella="100", superficie=1000),
    ]
    draft = _run_algorithm(puds)
    assert draft[0]["numero_partita"] == 1
    assert draft[1]["numero_partita"] == 1  # reset because product changed


def test_surface_totals_are_conserved():
    """Total surface in draft must equal total surface of input PUDs."""
    surfaces = [5000, 18000, 32000, 7500]
    puds = _make_puds(surfaces)
    draft = _run_algorithm(puds)
    assert sum(r["superficie_assegnata"] for r in draft) == sum(surfaces)


# ---------------------------------------------------------------------------
# DB integration test — smoke test with real data
# ---------------------------------------------------------------------------

def test_generate_draft_does_not_crash_on_real_db(db_session):
    """
    Smoke test: call with a real ragione_sociale_id that may or may not have
    PUD rows. We only assert it returns a list without raising.
    Replace the ID below with one that has actual PUD rows for a stronger test.
    """
    result = generate_partite_draft_logic(
        db_session,
        ragione_sociale_id="00000000-0000-0000-0000-000000000000",
        anno=2025,
    )
    assert isinstance(result, list)


def test_check_status_defaults_year_when_none(db_session):
    """
    With anno=None and no data for a bogus client, the status check should not
    crash and should report an unbalanced (empty) result.
    """
    from services.partite import get_check_partite_status
    result = get_check_partite_status(
        db_session,
        ragione_sociale_id="00000000-0000-0000-0000-000000000000",
        anno=None,
    )
    assert result["is_balanced"] is False
    assert result["total_superficie_pud"] == 0
