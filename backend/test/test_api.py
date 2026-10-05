"""
Integration tests for key FastAPI endpoints.
Uses the real eureka-dev DB via the TestClient fixture in conftest.py.
"""
import pytest
import io


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def test_root_returns_welcome(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Eureka" in r.json().get("message", "")


# ---------------------------------------------------------------------------
# Comuni
# ---------------------------------------------------------------------------

def test_get_comuni_returns_list(client):
    r = client.get("/comuni/list", params={"q": "Adria"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_get_comuni_with_short_query(client):
    """Single character query — API should handle it gracefully."""
    r = client.get("/comuni/list", params={"q": "A"})
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Condifesa
# ---------------------------------------------------------------------------

def test_get_all_condifesa(client):
    r = client.get("/condifesa/list")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ---------------------------------------------------------------------------
# Tables (dynamic admin)
# ---------------------------------------------------------------------------

def test_get_table_list(client):
    r = client.get("/tables/")
    assert r.status_code == 200
    tables = r.json()
    assert isinstance(tables, list)
    assert any(t["schema"] == "grandine" for t in tables)


def test_get_table_schema_known_table(client):
    r = client.get("/tables/grandine/piano_utilizzo/schema/")
    assert r.status_code == 200
    cols = r.json()
    assert isinstance(cols, list)
    col_names = [c["name"] for c in cols]
    assert "id" in col_names


def test_get_table_schema_unknown_table(client):
    r = client.get("/tables/grandine/nonexistent_table_xyz/schema/")
    assert r.status_code == 404


def test_get_table_data_returns_list(client):
    r = client.get("/tables/grandine/piano_utilizzo/data/", params={"limit": 5})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ---------------------------------------------------------------------------
# Piano Utilizzo — upload-pdf (error path, no real PDF required)
# ---------------------------------------------------------------------------

def test_upload_pdf_without_condifesa_returns_error(client):
    """Missing required form field → FastAPI returns 422."""
    fake_pdf = io.BytesIO(b"%PDF-1.4 fake content")
    r = client.post(
        "/piani-utilizzo/upload-pdf",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")},
        # condifesa_id intentionally omitted
    )
    assert r.status_code == 422


def test_upload_pdf_with_malformed_content_returns_error(client):
    """Valid form fields but corrupt PDF bytes → should return 4xx/5xx, not crash."""
    fake_pdf = io.BytesIO(b"this is not a pdf")
    r = client.post(
        "/piani-utilizzo/upload-pdf",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")},
        data={"condifesa_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert r.status_code in (400, 422, 500)


# ---------------------------------------------------------------------------
# Piani Utilizzo — bulk (validation path)
# ---------------------------------------------------------------------------

def test_bulk_create_with_missing_fields_returns_422(client):
    r = client.post("/piani-utilizzo/bulk", json={}, params={"is_dettagliato": False})
    assert r.status_code == 422
