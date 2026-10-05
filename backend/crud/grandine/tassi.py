from uuid import UUID
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


from models.grandine import Tassi


def get_tasso_by_id(db: Session, id: UUID) -> Optional[Tassi]:
    """Retrieve a Tasso entry by its ID."""
    return db.query(Tassi).filter(Tassi.id == id).first()

def get_tassi_for_tabella_conversione(db: Session, anno: int, intermediario_id: UUID, compagnia_id: UUID, codice_ministeriale: str, codice_comune: int) -> Optional[List[Tassi]]:
    """Retrieve all tabella conversione for a given combination"""
    return db.query(Tassi).filter(
        Tassi.anno==anno,
        Tassi.intermediario_id==intermediario_id,
        Tassi.compagnia_id==compagnia_id, 
        Tassi.codice_ministeriale==codice_ministeriale, 
        Tassi.codice_comune==codice_comune
        ).order_by(Tassi.tabella_conversione).all()