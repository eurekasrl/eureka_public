import unicodedata

from crud.core.comune import get_comuni
from crud.grandine.prodotto import get_dettaglio_by_condifesa, get_dettaglio_by_condifesa_and_codice_ministeriale
from crud.grandine.avepa import get_avepa_by_nome
from crud.core.comune import get_comuni

def get_column_match_count(element_a, element_b):
        if element_a:
            count_element = 1
            if str(element_a) == str(element_b):
                match_element = 0
            else:
                match_element = 1
        else:
            match_element = 0
            count_element = 0
        
        return match_element, count_element

def paranoid_normalize(text):
    if not text: return ""
    
    # 1. Force to string and Uppercase
    text = str(text).upper()
    
    # 2. DELETE the backticks and apostrophes instead of replacing them with 'A'
    # This turns "ARQUA` POLESINE" into "ARQUA POLESINE"
    text = text.replace("`", "").replace("'", "").replace("’", "")
    
    # 3. Decomposition: turn 'À' into 'A' + 'Grave Accent'
    nfkd_form = unicodedata.normalize('NFKD', text)
    
    # 4. Filter: Keep ONLY A-Z and 0-9.
    # This drops the accents from the DB version (turning 'à' into 'a')
    clean_chars = [c for c in nfkd_form if c.isalnum() and c.isascii()]
    result = "".join(clean_chars)
    
    return result

def match_comune(db, raw_comune):
    target = paranoid_normalize(raw_comune)
    db_comuni_list = get_comuni(db, iniziali=f"{target[:3]}")
    
    if not db_comuni_list:
        return None

    for comune in db_comuni_list:
        db_norm = paranoid_normalize(comune.nome)
        
        # Now ARQUAPOLESINE (PDF) == ARQUAPOLESINE (DB)
        if db_norm == target:
            return comune

    # Try a fallback partial match if no exact match found
    for comune in db_comuni_list:
        db_norm = paranoid_normalize(comune.nome)
        if target in db_norm or db_norm in target:
            return comune

    return None

def match_prodotto_smart(db, condifesa_id, full_text_pdf):
    """
    Matches the long PDF string against DB columns by concatenating 
    nome_avepa, nome, and dettaglio.
    """
    # 1. Fetch all products for this Condifesa (load into memory for fuzzy matching)
    # This is usually a few hundred rows, which Python handles instantly.
    full_text_pdf_splitted = full_text_pdf.split("-")
    dettaglio_avepa = full_text_pdf_splitted[-1].strip()
    nome_avepa_list = full_text_pdf_splitted[:-1]

    avepa_db = get_avepa_by_nome(db, nome_avepa_list)
    if avepa_db:
        db_prodotto = get_dettaglio_by_condifesa_and_codice_ministeriale(db, condifesa_id, avepa_db.codice_ministeriale, dettaglio_avepa=dettaglio_avepa)
        return db_prodotto
    else:
        return None

def match_prodotto_id_coltura(db, condifesa_id, id_coltura, full_text_pdf):
    """
    Matches the long PDF string against DB columns by concatenating 
    nome_avepa, nome, and dettaglio.
    """
    # 1. Fetch all products for this Condifesa (load into memory for fuzzy matching)
    # This is usually a few hundred rows, which Python handles instantly.
    full_text_pdf_splitted = full_text_pdf.split("-")
    nome_avepa_list = full_text_pdf_splitted[:-1]

    avepa_db = get_avepa_by_nome(db, nome_avepa_list)
    if avepa_db:
        db_prodotto = get_dettaglio_by_condifesa_and_codice_ministeriale(db, condifesa_id, avepa_db.codice_ministeriale, id_avepa=id_coltura)
        return db_prodotto
    else:
        return None
