from sqlalchemy.orm import Session
from models.core import Compagnia
from schemas.core import CompagniaCreate

def get_compagnia(db: Session, id: str):
    return db.query(Compagnia).filter(Compagnia.id == id).first()

def get_compagnie(db: Session, skip: int = 0, limit: int = 100, iniziali=None):
    stmt = db.query(Compagnia).order_by(Compagnia.id)
    if iniziali:
        stmt = stmt.filter(Compagnia.nome.ilike(f"%{iniziali}%"))
    return stmt.offset(skip).limit(limit).all()

def create_compagnia_entry(db: Session, compagnia: CompagniaCreate):
    db_compagnia = Compagnia(**compagnia.dict())
    db.add(db_compagnia)
    db.commit()
    db.refresh(db_compagnia)
    return db_compagnia