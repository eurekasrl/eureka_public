import os
import re
from io import BytesIO

import pdfplumber

try:  # OCR is optional: digital PDFs work without it; scans need it.
    import pytesseract
except ImportError:
    pytesseract = None

from services.utils import match_comune, match_prodotto_smart, match_prodotto_id_coltura
from crud.grandine.prodotto import get_dettaglio_by_condifesa_and_codice_avepa, get_dettaglio_by_condifesa_and_codice_avepa_dettagliato, get_prodotto_by_codice_ministeriale
from crud.grandine.avepa import get_avepa_by_codice_avepa_dettagliato, get_nome_by_codice_avepa_dettagliato


# Optional override for the Tesseract binary (common on Windows):
#   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
_TESSERACT_CMD = os.getenv("TESSERACT_CMD")
if pytesseract and _TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = _TESSERACT_CMD

# Italian first, English fallback — needs the matching Tesseract language packs.
OCR_LANG = os.getenv("OCR_LANG", "ita+eng")
OCR_DPI = int(os.getenv("OCR_DPI", "300"))


class PdfTextExtractionError(Exception):
    """Raised when a PDF cannot be read (corrupt, or a scan with no OCR available)."""


def _correct_orientation(image):
    """Detect and correct page rotation on scans via Tesseract OSD."""
    try:
        osd = pytesseract.image_to_osd(image)
        match = re.search(r"Rotate:\s*(\d+)", osd)
        angle = int(match.group(1)) if match else 0
        if angle:
            # OSD reports clockwise degrees; PIL rotates counter-clockwise.
            return image.rotate(-angle, expand=True)
    except Exception:
        # OSD raises on sparse/blank pages — keep the original orientation.
        pass
    return image


def _ocr_page(page):
    """Rasterize a page that has no text layer and OCR it (orientation-corrected)."""
    if pytesseract is None:
        raise PdfTextExtractionError(
            "Modulo OCR non disponibile: installa 'pytesseract' e il motore Tesseract "
            "per leggere i PDF scansionati."
        )
    try:
        image = page.to_image(resolution=OCR_DPI).original
    except Exception as err:
        raise PdfTextExtractionError(f"Impossibile rasterizzare la pagina per l'OCR: {err}")
    image = _correct_orientation(image)
    try:
        return pytesseract.image_to_string(image, lang=OCR_LANG)
    except pytesseract.TesseractNotFoundError:
        raise PdfTextExtractionError(
            "Tesseract OCR non è installato sul server. Per leggere i PDF scansionati installa "
            "Tesseract (con la lingua 'ita') e, se serve, imposta TESSERACT_CMD nel file .env."
        )
    except pytesseract.TesseractError as err:
        raise PdfTextExtractionError(f"Errore OCR durante la lettura della pagina scansionata: {err}")


def extract_page_texts(pdf):
    """Return the text of each page, falling back to OCR for pages with no text
    layer (scans/photos). Digital pages use pdfplumber, which already honours the
    page /Rotate flag, so rotated digital PDFs come out upright."""
    texts = []
    for page in pdf.pages:
        text = page.extract_text() or ""
        if not text.strip():
            text = _ocr_page(page) or ""
        texts.append(text)
    return texts


def parse_piano_utilizzo(content, condifesa_id, db):
    try:
        with pdfplumber.open(BytesIO(content)) as pdf:
            # OCR (when needed) must happen while the PDF is open for rasterization.
            page_texts = extract_page_texts(pdf)
    except PdfTextExtractionError:
        raise
    except Exception as err:
        # pdfplumber/pdfminer raises its own exceptions on corrupt or non-PDF bytes;
        # convert to the route's handled error so callers get a 422, not a crash.
        raise PdfTextExtractionError(
            "Impossibile leggere il PDF: il file potrebbe essere danneggiato o non essere un PDF valido."
        ) from err

    if not any(t.strip() for t in page_texts):
        raise PdfTextExtractionError(
            "Nessun testo leggibile nel PDF. Se è una scansione verifica che Tesseract sia "
            "installato; altrimenti il file potrebbe essere danneggiato."
        )

    first_page_content = page_texts[0]
    is_riepilogativo = "Riepilogo per" in first_page_content

    if is_riepilogativo:
        if "Riepilogo per Coltura" in first_page_content:
            return parse_riepilogativo_per_coltura(page_texts, condifesa_id, db)
        elif "Riepilogo per Comune e Coltura" in first_page_content:
            return parse_riepilogativo_per_comune_e_coltura(page_texts, condifesa_id, db)
        raise PdfTextExtractionError("Tipo di Riepilogo non riconosciuto nel PDF.")
    else:
        return parse_piano_utilizzo_dettagliato(page_texts, condifesa_id, db)

def _format_mapped_prodotto(suggested_prodotto):
    """Helper to standardize the mapped_prodotto dictionary structure."""
    if not suggested_prodotto:
        return None
    return {
        "id": suggested_prodotto.id,
        "nome": suggested_prodotto.nome,
        "dettaglio": suggested_prodotto.dettaglio,
        "codice_avepa_dettagliato": suggested_prodotto.codice_avepa_dettagliato
    }

def _base_riepilogativo_parser(page_texts, regex, row_processor_func):
    """Generic loop for riepilogativo PDFs."""
    extracted_rows = []
    for text in page_texts:
        if not text:
            continue

        for line in text.split('\n'):
            line = line.strip()
            # Common skip logic
            if not line or any(header in line for header in ["ID Coltura", "Stato", "Superficie"]):
                continue

            match = regex.search(line)
            if match:
                row_data = row_processor_func(match, line)
                if row_data:
                    extracted_rows.append(row_data)
    return extracted_rows

def parse_riepilogativo_per_comune_e_coltura(page_texts, condifesa_id, db):
    # Comune (1) - Descrizione (2) - Superficie (3)
    re_riepilogo = re.compile(r'^([^-(\n]+)\([A-Z]{2}\)\s+-\s+(.*?)\s+(\d+)$')

    def process_line(match, line):
        raw_comune_str = match.group(1).strip()
        full_text_to_analyze = match.group(2).strip()
        superficie_mq = int(match.group(3))

        matched_comune_obj = match_comune(db, raw_comune_str)
        suggested_prodotto = match_prodotto_smart(db, condifesa_id, full_text_to_analyze)

        return {
            "comune": matched_comune_obj.nome if matched_comune_obj else raw_comune_str,
            "codice_comune": matched_comune_obj.codice_comune if matched_comune_obj else None,
            "prodotto_raw": full_text_to_analyze,
            "superficie": superficie_mq,
            "mapped_prodotto": _format_mapped_prodotto(suggested_prodotto),
            "raw_line": line,
            "is_manual": False
        }

    return _base_riepilogativo_parser(page_texts, re_riepilogo, process_line)

def parse_riepilogativo_per_coltura(page_texts, condifesa_id, db):
    # ID (1) - Descrizione (2) - Superficie (3)
    re_coltura = re.compile(r'^(\d+)\s+(.*?)\s+(\d+)$')

    def process_line(match, line):
        id_coltura = int(match.group(1))
        prodotto_raw = match.group(2).strip()
        superficie_mq = int(match.group(3))

        suggested_prodotto = match_prodotto_id_coltura(db, condifesa_id, id_coltura, prodotto_raw)

        return {
            "comune": "",
            "codice_comune": None,
            "prodotto_raw": f"{prodotto_raw}",
            "superficie": superficie_mq,
            "mapped_prodotto": _format_mapped_prodotto(suggested_prodotto),
            "raw_line": line,
            "is_manual": False
        }

    return _base_riepilogativo_parser(page_texts, re_coltura, process_line)

def parse_piano_utilizzo_dettagliato(page_texts, condifesa_id, db):
    extracted_rows = []

    # 1. Regex Comune: "NOME COMUNE (PR)"
    re_comune = re.compile(r'^([A-Z\s\'`\-]{3,})\s\(([A-Z]{2})\)$')

    # 2. Regex Superficie: cattura l'ultimo numero in righe che iniziano con parole chiave
    # Usiamo \d+ alla fine per assicurarci di prendere solo cifre
    re_prefix_surface = re.compile(r'^(?:ciclo|senza|rotazione).*?\s+(\d+)$', re.IGNORECASE)

    # 3. Regex Codice AVEPA (ddd-ddd-ddd-ddd-ddd)
    re_avepa = re.compile(r'\((\d{3}-\d{3}-\d{3}-\d{3}-\d{3})\)')

    current_comune_obj = None
    current_comune_raw = ""
    last_surface_found = 0

    for text in page_texts:
        if not text: continue

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue

            # --- PASSO 1: IDENTIFICAZIONE COMUNE ---
            m_comune = re_comune.match(line)
            if m_comune:
                current_comune_raw = m_comune.group(1).strip()
                current_comune_obj = match_comune(db, current_comune_raw)
                continue

            # Se non abbiamo ancora trovato un comune, ignoriamo intestazioni come "Campagna 2025"
            if not current_comune_raw:
                continue

            # --- PASSO 2: ESTRAZIONE SUPERFICIE ---
            m_surf = re_prefix_surface.search(line)
            if m_surf:
                val = m_surf.group(1)
                # Sicurezza: convertiamo solo se sono cifre
                if val.isdigit():
                    last_surface_found = int(val)

                # Se la riga non contiene dati AVEPA, passiamo alla prossima
                if "(" not in line:
                    continue

            # --- PASSO 3: ESTRAZIONE DATI CATASTALI E AVEPA ---
            m_avepa = re_avepa.search(line)
            if m_avepa:
                avepa_code = m_avepa.group(1)
                avepa_nome = 'Not in Avepa table'

                # Tokenizziamo la riga per gestire lo slittamento delle colonne
                tokens = line.split()

                # In base ai tuoi esempi:
                # "8 00132 114 non irrigua ..." -> Foglio=8 (idx 0), Part=00132 (idx 1)
                # Se il primo token è una lettera (Sezione), Foglio e Part slittano di 1
                if tokens[0].isalpha() and len(tokens[0]) == 1:
                    foglio = tokens[1]
                    particella = tokens[2]
                else:
                    foglio = tokens[0]
                    particella = tokens[1]

                # Flags Serra/Bio (solitamente gli ultimi due token: "N N" o "S N")
                # Analizziamo gli ultimi due elementi
                bio_raw = tokens[-1] if len(tokens) >= 1 else 'N'
                serra_raw = tokens[-2] if len(tokens) >= 2 else 'N'

                # Lookup Prodotto
                db_prodotto = get_dettaglio_by_condifesa_and_codice_avepa_dettagliato(db, condifesa_id, avepa_code)
                db_avepa = get_avepa_by_codice_avepa_dettagliato(db, avepa_code)
                if db_avepa:
                    avepa_nome = get_nome_by_codice_avepa_dettagliato(db, avepa_code)
                    if not db_prodotto:
                        db_prodotto = get_prodotto_by_codice_ministeriale(db, codice_ministeriale=db_avepa.codice_ministeriale)


                extracted_rows.append({
                    "comune": current_comune_obj.nome if current_comune_obj else current_comune_raw,
                    "codice_comune": current_comune_obj.codice_comune if current_comune_obj else None,
                    "foglio": foglio,
                    "particella": particella,
                    "superficie": last_surface_found,
                    "mapped_prodotto": {
                        "id": db_prodotto.id,
                        "nome": db_prodotto.nome,
                        "dettaglio": db_prodotto.dettaglio,
                        #"nome_avepa": db_prodotto.nome_avepa,
                        "codice_avepa_dettagliato": db_prodotto.codice_avepa_dettagliato
                    } if db_prodotto else None,
                    "prodotto_raw": f"{avepa_code} - {avepa_nome}",
                    "serra": True if serra_raw == 'S' else False,
                    "bio": True if bio_raw == 'S' else False,
                    "raw_line": line,
                    "is_manual": False
                })

                # Reset superficie per evitare trascinamenti errati
                last_surface_found = 0

    return extracted_rows
