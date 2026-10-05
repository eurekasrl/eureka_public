from collections import defaultdict
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import UploadFile

from crud.sale.preventivo import get_preventivi_by_ragione_sociale_id, get_preventivi_by_pgid_anno_ramo, get_preventivi_for_send, get_preventivi_by_gruppo_id, get_preventivi_by_gruppo_id_anno_ramo, get_preventivo, get_preventivi_for_doc
from crud.utils import prepare_csv, prepare_xlsx
from crud.sale.config import get_email_preventivi_body, get_email_preventivi_subject, get_email_preventivi_subject_for_intermediario, get_email_preventivi_body_for_intermediario
from crud.core.ramo import get_ramo
from services.document_services import DocumentService
from models.core import Documento
from crud.core.documento import get_documents_sigla
from crud.sale.documento import get_unique_doc_arch

doc_service = DocumentService()

def get_preventivo_by_ragione_sociale_id_for_page(db: Session, ragione_sociale_id: str, page: str, ramo_id: Optional[str]=None, anno:Optional[int] = None, lifecycle_id:Optional[int] = None):
    preventivi_db = get_preventivi_by_ragione_sociale_id(db, ragione_sociale_id)
    if page=='preventivi':
        valid_preventivi = _build_preventivi_output(preventivi_db) if preventivi_db else []
    elif page=='admin':
        valid_preventivi = _build_admin_output(preventivi_db) if preventivi_db else []
    elif page=='email-cliente':
        preventivi_db = get_preventivi_for_send(db, ragione_sociale_id, ramo_id, anno, lifecycle_id=3)
        valid_preventivi = _build_email_output(preventivi_db)
    elif page=='email-intermediario':
        preventivi_db = get_preventivi_for_send(db, ragione_sociale_id, ramo_id, anno, lifecycle_id=5)
        valid_preventivi = _build_email_output(preventivi_db)
    elif page=='documenti':
        preventivi_db = get_preventivi_for_doc(db, ragione_sociale_id, anno, lifecycle_id=4)
        valid_preventivi = _build_email_output(preventivi_db)
    return valid_preventivi

def get_preventivo_by_gruppo_id_for_page(db: Session, gruppo_id: str, page: str, ramo_id: Optional[str]=None, anno:Optional[int] = None):
    gruppo_preventivi_db = get_preventivi_by_gruppo_id(db, gruppo_id)
    valid_gruppo_preventivi = {}
    for pg_id, preventivi_list in gruppo_preventivi_db.items():

        if page=='admin':
            valid_gruppo_preventivi[pg_id] = _build_admin_output(preventivi_list) if preventivi_list else []
        elif page=='email':
            preventivi_db = get_preventivi_for_send(db, pg_id, ramo_id, anno)
            valid_gruppo_preventivi[pg_id] = _build_email_output(preventivi_db)
    return valid_gruppo_preventivi

def _build_preventivi_output(preventivi_db):
    result = []
    grouped = defaultdict(list)

    for item in preventivi_db:
        dettaglio = item.ramo.dettaglio  # e.g. 'rca', 'grandine'
        attr_name = f"preventivo_{dettaglio}"  # dynamically builds attribute name

        if getattr(item, attr_name, None):
            grouped[item.ramo.id].append(item)
        
    for ramo_id, items in grouped.items():
        dettaglio = items[0].ramo.dettaglio

        ramo_block = {
            "ramo_nome": dettaglio,
            "ramo_id": ramo_id,
            "preventivi": []
        }

        for item in items:
            serialized = _serialize_preventivo(item, dettaglio)
            if serialized:
                ramo_block["preventivi"].append(serialized)
        
        result.append(ramo_block)

    return result

def _build_admin_output(preventivi_db):
    grouped = defaultdict(lambda: defaultdict(int))

    for p in preventivi_db:
        ramo_id = p.ramo_id
        ramo_dettaglio = p.ramo.dettaglio
        anno = p.created_at.year
        stato = p.lifecycle.stato.lower()
        
        grouped[(ramo_id, anno)][stato] += 1

        output = []
        for (ramo_id, anno), stato_counts in grouped.items():
            output.append({
                "ramo_id": ramo_id,
                "ramo_dettaglio":ramo_dettaglio,
                "anno": anno,
                "stato": stato_counts
            })

    return output

def _build_email_output(preventivi_db):
    ramo_dettaglio = preventivi_db[0].ramo.dettaglio

    result = []
    for preventivo in preventivi_db:
        serialized = _serialize_preventivo(preventivo, ramo_dettaglio)
        result.append(serialized)
    return result

def _serialize_preventivo(preventivo, dettaglio):
    """
    dettaglio = item.ramo.dettaglio  (e.g. 'grandine', 'agricoltura')
    """

    # Example: preventivo_agricoltura / preventivo_grandine
    ramo_preventivo_table = f"preventivo_{dettaglio}"
    ramo_preventivo = getattr(preventivo, ramo_preventivo_table, None)

    if not ramo_preventivo:
        return None

    # Extract normalized attributes from the sub-table
    # Adjust to match your actual model attributes.
    if dettaglio=='grandine':
        return {
            "id": preventivo.id,
            "intermediario_nome": preventivo.intermediario.short_nome,
            "compagnia_nome": preventivo.compagnia.short_nome,
            "stato": preventivo.lifecycle.stato,
            "comune_nome": ramo_preventivo.piano_utilizzo.comune.nome,
            "prodotto_nome": f"{ramo_preventivo.piano_utilizzo.prodotto.nome} - {ramo_preventivo.piano_utilizzo.prodotto.dettaglio}",
            "superficie": ramo_preventivo.piano_utilizzo.superficie,
            "valore_assicurato": ramo_preventivo.valore_assicurato,
            "premio_lordo": preventivo.premio_lordo,
            "created_at": preventivo.created_at.isoformat(),
            "updated_at": preventivo.updated_at.isoformat() if preventivo.updated_at else None,
        }
    return {
        "id": preventivo.id,
        "intermediario_nome": preventivo.intermediario.short_nome,
        "compagnia_nome": preventivo.compagnia.short_nome,
        "stato": preventivo.lifecycle.stato,
        "premio_lordo": preventivo.premio_lordo,
        "created_at": preventivo.created_at.isoformat(),
        "updated_at": preventivo.updated_at.isoformat(),

    }

def preventivi_for_download(db: Session, client_level_id: str, client_level:str, ramo_id: str, anno:int, preventivo_ids: Optional[List[str]] = None, extension: str = 'csv'):
    if client_level=='ragione_sociale':
        preventivi = get_preventivi_by_pgid_anno_ramo(db, client_level_id, ramo_id, anno, preventivo_ids)
    elif client_level=='gruppo':
        preventivi = get_preventivi_by_gruppo_id_anno_ramo(db, client_level_id, ramo_id, anno, preventivo_ids)

    if extension=='csv':
        return prepare_csv(db, preventivi, anno, client_level)
    if extension=='xlsx':
        return prepare_xlsx(db, preventivi, anno, client_level)

def get_preventivi_smtp_data_for_client(request, db, client):
    filename, xlsx_buffer, html_table_string = preventivi_for_download(
        db, 
        request.client_level_id,
        request.client_level, 
        request.ramo_id, 
        request.anno, 
        request.selected_ids,
        "xlsx"
    )

    preventivi_db = [get_preventivo(db,preventivo_id) for preventivo_id in request.selected_ids]
    ramo_dettaglio = get_ramo(db, request.ramo_id).dettaglio

    nome_cliente = client.nome
    if request.client_level=='gruppo':
        nome_cliente = client.referente.nome

    unique_products=ramo_dettaglio
    if ramo_dettaglio=='grandine':
        unique_products = {preventivo.preventivo_grandine.piano_utilizzo.prodotto.nome for preventivo in preventivi_db}

    virtual_files = [UploadFile( filename=filename, file=xlsx_buffer, headers={"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"})]
    
    preventivo_subject = get_email_preventivi_subject(
        ramo_dettaglio=ramo_dettaglio, 
        anno= request.anno,
        additional_info=unique_products
        )
    preventivo_body = get_email_preventivi_body(
        client_nome= nome_cliente,
        additional_info= ','.join(unique_products),
        additiona_html_table= html_table_string,
        ramo= ramo_dettaglio,
        anno= request.anno
        )
    return preventivo_subject, preventivo_body, virtual_files

def get_preventivi_smtp_data_for_intermediario(request, db):
    preventivi_db = [get_preventivo(db,preventivo_id) for preventivo_id in request.selected_ids]
    ramo_dettaglio = get_ramo(db, request.ramo_id).dettaglio
    rs = preventivi_db[0].ragione_sociale

    preventivo_subject = get_email_preventivi_subject_for_intermediario(rs.nome)
    recipient_email = preventivi_db[0].intermediario.email
    preventivo_body = get_email_preventivi_body_for_intermediario(ramo_dettaglio, preventivi_db, request.anno)
    virtual_files = get_attachments_for_intermediario(db, rs, preventivi_db, request.anno)

    return preventivo_subject, recipient_email, preventivo_body, virtual_files

def get_attachments_for_intermediario(db, rs, preventivi_db, anno):
    all_docs = db.query(Documento).all()
    all_docs_sigla = get_documents_sigla(db)
    required_documents = doc_service._determine_required_documents(all_docs=all_docs, all_docs_sigla=all_docs_sigla, preventivi=preventivi_db)
    virtual_files = []
    for doc_type, doc in required_documents.items():
        if doc.lifecycle_id==5 and doc.mandatory:
            doc_arch_for_intermediario = get_unique_doc_arch(db = db, ragione_sociale_id = rs.id, documento_id = doc.id, anno = anno)
            virtual_files.append(str(doc_service.base_path / doc_arch_for_intermediario.file_path))
    
    return virtual_files