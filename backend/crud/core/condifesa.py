from sqlalchemy.orm import Session
from models.core import Condifesa
from schemas.core import CondifesaCreate

def get_condifesa(db: Session, skip: int = 0, limit: int = 100, iniziali=None):
    stmt = db.query(Condifesa).order_by(Condifesa.id)
    if iniziali:
        stmt = stmt.filter(Condifesa.nome.ilike(f"%{iniziali}%"))
    return stmt.offset(skip).limit(limit).all()

def get_condifesa_by_id(db: Session, condifesa_id: str):
    return db.query(Condifesa).filter(Condifesa.id == condifesa_id).first()