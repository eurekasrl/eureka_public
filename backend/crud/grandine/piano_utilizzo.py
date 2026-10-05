from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import text

from models.grandine import PianoUtilizzo, PianoUtilizzoDettagliato
from schemas.grandine import PianoUtilizzo as PianoUtilizzoSchema, DettaglioRow, DashboardComparisonRow
from crud.core.comune import get_comune_by_name
from db.utils import try_commit

def get_piano_utilizzo(db: Session, piano_utilizzo_id: str)-> PianoUtilizzoSchema:
    """Get a single piano utilizzo by its ID"""
    return db.query(PianoUtilizzo).filter(PianoUtilizzo.id == piano_utilizzo_id).first()

def get_piani_utilizzo_by_ragione_sociale(
    db: Session,
    ragione_sociale_id: str,
    anno: int = None,
    skip: int = 0,
    limit: int = 100
) -> List[PianoUtilizzo]:
    """Get all piani utilizzo for a specific ragione sociale, optionally filtered by year."""
    query = db.query(PianoUtilizzo)\
        .filter(PianoUtilizzo.ragione_sociale_id == ragione_sociale_id)
    if anno is not None:
        query = query.filter(PianoUtilizzo.anno == anno)
    return query.order_by(PianoUtilizzo.id).offset(skip).limit(limit).all()

def get_piani_utilizzo_dettagliati_by_ragione_sociale(
    db: Session,
    ragione_sociale_id: str,
    anno: int = None
) -> List[PianoUtilizzoDettagliato]:
    """Get all piani utilizzo dettagliati for a ragione sociale, optionally filtered by year."""
    query = db.query(PianoUtilizzoDettagliato)\
        .filter(PianoUtilizzoDettagliato.ragione_sociale_id == ragione_sociale_id)
    if anno is not None:
        query = query.filter(PianoUtilizzoDettagliato.anno == anno)
    return query.order_by(
            PianoUtilizzoDettagliato.condifesa_id,
            PianoUtilizzoDettagliato.anno,
            PianoUtilizzoDettagliato.codice_comune,
            PianoUtilizzoDettagliato.prodotto_id,
            PianoUtilizzoDettagliato.serra,
            PianoUtilizzoDettagliato.bio,
            PianoUtilizzoDettagliato.secondo_raccolto,
            PianoUtilizzoDettagliato.foglio, # Group spatially
            PianoUtilizzoDettagliato.particella
        ).all()

def get_distinct_anni_dettagliato(db: Session, ragione_sociale_id: str) -> List[int]:
    """Return the campaign years that have dettagliato data for this client, most recent first."""
    rows = db.query(PianoUtilizzoDettagliato.anno)\
        .filter(PianoUtilizzoDettagliato.ragione_sociale_id == ragione_sociale_id)\
        .distinct()\
        .order_by(PianoUtilizzoDettagliato.anno.desc())\
        .all()
    return [r[0] for r in rows]

def create_piano_utilizzo_dettagliato_entry(
        db: Session, 
        ragione_sociale_id: str,
        condifesa_id: str,
        anno: int,
        secondo_raccolto: bool,
        data: DettaglioRow
        ):
    pud_db = PianoUtilizzoDettagliato(
        ragione_sociale_id = ragione_sociale_id,
        condifesa_id = condifesa_id,
        anno = anno,
        secondo_raccolto = secondo_raccolto,
        is_corrente = True,
        codice_comune = get_comune_by_name(db, data.comune).codice_comune,
        prodotto_id = data.prodotto_id,
        serra = data.serra,
        bio = data.bio,
        foglio = data.foglio,
        particella = int(data.particella),
        superficie = data.superficie,
        data_semina_trapianto = data.data_semina_trapianto
    )
    try_commit(db, pud_db)

def get_piani_utilizzo_comparison_dashboard(db: Session, ragione_sociale_id: str) -> List[DashboardComparisonRow]:
    query = text("EXEC grandine.sp_confronto_piano_utilizzo @ragione_sociale_id= :ragione_sociale_id")
    result = db.execute(query, {"ragione_sociale_id": ragione_sociale_id})
    
    return result.mappings().all()

def create_piano_bulk(payload, is_dettagliato: bool):
    # 1. Prepare the data list for bulk insertion
    # We map the payload fields to the actual database column names
    data_to_insert=[]

    for row in payload.rows:
        row_to_insert = {
            "ragione_sociale_id": payload.ragione_sociale_id,
            "condifesa_id": payload.condifesa_id,
            "anno": payload.anno,
            "secondo_raccolto": payload.secondo_raccolto,
            "prodotto_id": row.prodotto_id,
            "codice_comune": row.codice_comune,
            "superficie": row.superficie,
            "serra": row.serra,
            "bio": row.bio,
            "note": row.note,
        }
        if is_dettagliato:
            row_to_insert["foglio"] = row.foglio
            row_to_insert["particella"] = row.particella
            row_to_insert["data_semina_trapianto"] = row.data_semina_trapianto
        data_to_insert.append(row_to_insert)
    
    return data_to_insert