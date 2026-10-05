from sqlalchemy.orm import Session
from models.core import Intermediario
from schemas.core import IntermediarioCreate

def get_intermediario(db: Session, id: str):
    return db.query(Intermediario).filter(Intermediario.id == id).first()

def get_intermediari(db: Session, skip: int = 0, limit: int = 100, iniziali=None):
    stmt = db.query(Intermediario).order_by(Intermediario.id)
    if iniziali:
        stmt = stmt.filter(Intermediario.nome.ilike(f"%{iniziali}%"))
    return stmt.offset(skip).limit(limit).all()

def create_intermediario_entry(db: Session, intermediario: IntermediarioCreate):
    db_intermediario = Intermediario(**intermediario.dict())
    db.add(db_intermediario)
    db.commit()
    db.refresh(db_intermediario)
    return db_intermediario