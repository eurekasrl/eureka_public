"""
Tests for the OCR / rotation fallback in pdf_parser.

These use fakes for pytesseract and pdfplumber pages, so they run WITHOUT the
Tesseract binary or any real PDF installed.
"""
import pytest
import services.pdf_parser as pp
from services.pdf_parser import PdfTextExtractionError


# --- Fakes ----------------------------------------------------------------

class FakeImage:
    """Records rotate() calls so we can assert orientation correction."""
    def __init__(self):
        self.rotated_to = None

    def rotate(self, angle, expand=False):
        self.rotated_to = (angle, expand)
        return self


class FakePageImage:
    def __init__(self, image):
        self.original = image


class FakePage:
    """Stand-in for a pdfplumber Page."""
    def __init__(self, text="", image=None):
        self._text = text
        self._image = image or FakeImage()

    def extract_text(self):
        return self._text

    def to_image(self, resolution=300):
        return FakePageImage(self._image)


class FakeTess:
    """Minimal pytesseract replacement."""
    TesseractNotFoundError = type("TesseractNotFoundError", (Exception,), {})
    TesseractError = type("TesseractError", (Exception,), {})

    def __init__(self, osd="Rotate: 0\n", text="OCR TEXT", raise_on_string=None):
        self._osd = osd
        self._text = text
        self._raise_on_string = raise_on_string

    def image_to_osd(self, image):
        return self._osd

    def image_to_string(self, image, lang=None):
        if self._raise_on_string:
            raise self._raise_on_string
        return self._text


# --- _correct_orientation -------------------------------------------------

def test_orientation_rotates_when_osd_reports_angle(monkeypatch):
    monkeypatch.setattr(pp, "pytesseract", FakeTess(osd="Rotate: 90\nOrientation: 270\n"))
    img = FakeImage()
    result = pp._correct_orientation(img)
    # OSD's clockwise 90 -> PIL counter-clockwise -90, expanded.
    assert result.rotated_to == (-90, True)


def test_orientation_noop_when_upright(monkeypatch):
    monkeypatch.setattr(pp, "pytesseract", FakeTess(osd="Rotate: 0\n"))
    img = FakeImage()
    result = pp._correct_orientation(img)
    assert result.rotated_to is None


def test_orientation_survives_osd_failure(monkeypatch):
    class Boom(FakeTess):
        def image_to_osd(self, image):
            raise RuntimeError("too few characters for OSD")
    monkeypatch.setattr(pp, "pytesseract", Boom())
    img = FakeImage()
    # Must not raise; returns the original image unrotated.
    assert pp._correct_orientation(img) is img


# --- extract_page_texts ---------------------------------------------------

class FakePdf:
    def __init__(self, pages):
        self.pages = pages


def test_digital_pages_skip_ocr(monkeypatch):
    # If OCR is ever invoked for a page that already has text, fail loudly.
    monkeypatch.setattr(pp, "_ocr_page", lambda page: pytest.fail("OCR should not run on digital pages"))
    pdf = FakePdf([FakePage(text="ADRIA (RO)"), FakePage(text="some text")])
    assert pp.extract_page_texts(pdf) == ["ADRIA (RO)", "some text"]


def test_empty_pages_fall_back_to_ocr(monkeypatch):
    monkeypatch.setattr(pp, "_ocr_page", lambda page: "FROM OCR")
    pdf = FakePdf([FakePage(text=""), FakePage(text="   ")])
    assert pp.extract_page_texts(pdf) == ["FROM OCR", "FROM OCR"]


# --- _ocr_page error handling --------------------------------------------

def test_ocr_missing_binary_raises_clear_error(monkeypatch):
    tess = FakeTess(raise_on_string=FakeTess.TesseractNotFoundError("not found"))
    monkeypatch.setattr(pp, "pytesseract", tess)
    with pytest.raises(PdfTextExtractionError) as exc:
        pp._ocr_page(FakePage(text=""))
    assert "Tesseract" in str(exc.value)


def test_ocr_module_absent_raises_clear_error(monkeypatch):
    monkeypatch.setattr(pp, "pytesseract", None)
    with pytest.raises(PdfTextExtractionError) as exc:
        pp._ocr_page(FakePage(text=""))
    assert "OCR" in str(exc.value)
