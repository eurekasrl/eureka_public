from sqlalchemy.orm import Session, joinedload

from models.core import RagioneSociale
from schemas.core import RagioneSocialeCreate

def get_ragione_sociale(db: Session, ragione_sociale_id: str):
    # Eager loading delle relazioni per evitare N+1 query
    return db.query(RagioneSociale).options(
        joinedload(RagioneSociale.responsabile_legale),
        joinedload(RagioneSociale.gruppo),
        joinedload(RagioneSociale.comune),
        joinedload(RagioneSociale.caa_coldiretti)
    ).filter(RagioneSociale.id == ragione_sociale_id).first()

def get_ragioni_sociali(db: Session, skip: int = 0, limit: int = 100, iniziali=None):
    stmt = db.query(RagioneSociale).order_by(RagioneSociale.nome)
    if iniziali:
        stmt = stmt.filter(RagioneSociale.nome.ilike(f"%{iniziali}%"))
    return stmt.offset(skip).limit(limit).all()

def create_ragione_sociale(db: Session, azienda: RagioneSocialeCreate):
    db_azienda = RagioneSociale(**azienda.dict())
    db.add(db_azienda)
    db.commit()
    db.refresh(db_azienda)
    return db_azienda

def get_ragione_sociale_by_id(db: Session, id: str)-> RagioneSociale:
    return db.query(RagioneSociale).filter(RagioneSociale.id == id).first()
