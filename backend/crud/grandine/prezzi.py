from uuid import UUID
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


from models.grandine import Prezzi


def get_prezzo_by_id(db: Session, id: UUID) -> Optional[Prezzi]:
    """Retrieve a Prezzi entry by its ID."""
    return db.query(Prezzi).filter(Prezzi.id == id).first()

def get_prezzo(db: Session, anno: int, condifesa_id: UUID, prodotto_id: UUID, area: str, fascia: str) -> Optional[Prezzi]:
    """Retrieve a Prezzi entry by its unique combination of fields."""
    return db.query(Prezzi).filter(
        Prezzi.anno == anno,
        Prezzi.condifesa_id == condifesa_id,
        Prezzi.prodotto_id == prodotto_id,
        Prezzi.area == area,
        Prezzi.fascia == fascia
    ).first()

def get_prezzi_for_area(db: Session, anno: int, condifesa_id: UUID, prodotto_id: UUID, individuale=False) -> Optional[List[Prezzi]]:
    stmt = db.query(Prezzi).filter(Prezzi.anno == anno, Prezzi.prodotto_id == prodotto_id)
    if not individuale:
        stmt = stmt.filter(Prezzi.condifesa_id == condifesa_id)
    
    return stmt.all()
