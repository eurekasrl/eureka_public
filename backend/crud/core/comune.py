from sqlalchemy.orm import Session
from models.core import Comune
from schemas.core import ComuneCreate

def get_comune(db: Session, codice_comune: str):
    return db.query(Comune).filter(Comune.codice_comune == codice_comune).first()

def get_comuni(db: Session, skip: int = 0, limit: int = 100, iniziali=None):
    stmt = db.query(Comune).order_by(Comune.codice_comune)
    if iniziali:
        stmt = stmt.filter(Comune.nome.ilike(f"{iniziali}%"))
    return stmt.offset(skip).limit(limit).all()

def create_comune_entry(db: Session, comune: ComuneCreate):
    db_comune = Comune(**comune.dict())
    db.add(db_comune)
    db.commit()
    db.refresh(db_comune)
    return db_comune

def get_comune_by_name(db: Session, nome: str):
    return db.query(Comune).filter(Comune.nome == nome).first()