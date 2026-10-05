from decimal import Decimal
from typing import Optional, List
import traceback

from sqlalchemy import extract, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

# Import your ORM models
from models.sale import Preventivo
from models.core import Gruppo, RagioneSociale
from crud.core.ragione_sociale import get_ragione_sociale
from crud.core.ramo import get_ramo
from crud.core.intermediari import get_intermediario
from crud.core.compagnie import get_compagnia
from schemas.sale import Preventivo as PreventivoSchema


def create_preventivo_entry(
    ragione_sociale_id: str,
    ramo_id: str,
    intermediario_id: str,
    compagnia_id: str,
    db: Session,
) -> PreventivoSchema:
    """
    Insert a new row into the `sale.preventivo` table using ORM models.

    - db: SQLAlchemy Session
    - ragione_sociale_id, ramo_id, intermediario_id, compagnia_id: UUID PKs referencing their tables
    - premio_lordo: Decimal value for the proposed premium
    - stato: String for the status of the preventivo

    Returns the created Preventivo ORM object.
    Raises HTTPException if referenced rows are missing.
    """
    if not get_ragione_sociale(db, ragione_sociale_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ragione Sociale with id={ragione_sociale_id} not found."
        )
    if not get_ramo(db, ramo_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ramo with id={ramo_id} not found."
        )
    if not get_intermediario(db, intermediario_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intermediario with id={intermediario_id} not found."
        )
    if not get_compagnia(db, compagnia_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compagnia with id={compagnia_id} not found."
        )

    # Create the Preventivo ORM object
    db_preventivo = Preventivo(
        ragione_sociale_id=ragione_sociale_id,
        ramo_id=ramo_id,
        intermediario_id=intermediario_id,
        compagnia_id=compagnia_id,
        premio_lordo=0,
        lifecycle_id=3
    )
    # Add to session, commit, and refresh
    try:
        db.add(db_preventivo)
        db.flush()
        return db_preventivo
    except Exception as e:
        db.rollback()
         # --- IMPORTANT CHANGE HERE ---
        traceback.print_exc() # Print the full traceback to the console
        print(f"ERROR: Failed to create preventivo. Details: {e}") # Also print the exception message
        # --- END IMPORTANT CHANGE ---
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create preventivo: {e}"
        )

def update_preventivo(
    db: Session,
    preventivo_id: str,
    stato: Optional[str] = None,
    premio_lordo: Optional[Decimal] = None
) -> PreventivoSchema:
    """
    Update stato and/or premio_lordo for a specific preventivo using ORM.
    """
    db_preventivo = db.query(Preventivo).get(str(preventivo_id))


    if not db_preventivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preventivo with id={preventivo_id} not found."
        )

    if stato=='add':
        db_preventivo.lifecycle_id += 1
    elif stato=='detract':
        db_preventivo.lifecycle_id -= 1
    else:
        db_preventivo.lifecycle_id = int(stato)
    if premio_lordo is not None:
        db_preventivo.premio_lordo = premio_lordo
    # updated_at will be set automatically by onupdate=datetime.utcnow if defined in ORM model

    try:
        db.add(db_preventivo) # Add the modified object back to the session (optional for existing, good practice)
        db.commit()
        db.refresh(db_preventivo)
        return PreventivoSchema.model_validate(db_preventivo)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preventivo: {e}"
        )
    
def get_preventivi_by_ragione_sociale_id(
        db: Session,
        ragione_sociale_id:str,
        ):
    return db.query(Preventivo)\
            .filter(Preventivo.ragione_sociale_id == ragione_sociale_id)\
            .order_by(Preventivo.created_at).all()

def get_preventivi_by_gruppo_id(
        db: Session,
        gruppo_id:str,
        ):
    gruppo_db =  db.query(Gruppo).filter(Gruppo.id == gruppo_id).first()
    return {pg.id: pg.preventivi for pg in gruppo_db.ragione_sociale}

def get_preventivo(db: Session, preventivo_id: str)-> Preventivo:
    return db.query(Preventivo).filter(Preventivo.id == preventivo_id).first()

def delete_preventivo_entry(db: Session, preventivo_id: str, ramo_nome: str):
    """
    Deletes a preventivo. 
    Uses ramo_nome to identify if specific sub-table deletion is required.
    """
    db_preventivo = db.query(Preventivo).get(str(preventivo_id))

    if not db_preventivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preventivo with id={preventivo_id} not found."
        )

    try:
        db.delete(db_preventivo)
        db.commit()
        return {"message": f"Preventivo {preventivo_id} ({ramo_nome}) deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete preventivo: {e}"
        )

def get_preventivi_by_pgid_anno_ramo(db: Session, ragione_sociale_id: str, ramo_id: str, anno: int, preventivo_ids: Optional[List[str]]=None):
    query = db.query(Preventivo).filter(
        Preventivo.ragione_sociale_id == ragione_sociale_id,
        Preventivo.ramo_id == ramo_id,
        extract('year', Preventivo.created_at) == anno
    ).order_by(Preventivo.compagnia_id)

    if preventivo_ids:
        query = query.filter(Preventivo.id.in_(preventivo_ids))
        
    return query.all()

def get_preventivi_by_gruppo_id_anno_ramo(db: Session, gruppo_id: str, ramo_id: str, anno: int, preventivo_ids: Optional[List[str]]=None):
    query = db.query(Preventivo)\
    .join(RagioneSociale, Preventivo.ragione_sociale)\
    .filter(Preventivo.ramo_id == ramo_id)\
    .filter(extract('year', Preventivo.created_at) == anno)\
    .filter(RagioneSociale.gruppo_id == gruppo_id)\
    .order_by(Preventivo.compagnia_id)

    if preventivo_ids:
        query = query.filter(Preventivo.id.in_(preventivo_ids))
        
    return query.all()

def get_preventivi_for_send(db, ragione_sociale_id: str, ramo_id: str, anno: int, lifecycle_id: int):
    return db.query(Preventivo).filter(
        Preventivo.ragione_sociale_id == ragione_sociale_id,
        Preventivo.ramo_id == ramo_id,
        extract('year', Preventivo.created_at) == anno,
        Preventivo.lifecycle_id == lifecycle_id
    ).all() 

def get_preventivi_for_doc(db, ragione_sociale_id: str, anno: int, lifecycle_id: int):
    return db.query(Preventivo).filter(
        Preventivo.ragione_sociale_id == ragione_sociale_id,
        extract('year', Preventivo.created_at) == anno,
        Preventivo.lifecycle_id > lifecycle_id
    ).all() 
