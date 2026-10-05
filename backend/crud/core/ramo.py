from sqlalchemy.orm import Session
from models.core import Ramo
from schemas.core import RamoCreate

def get_rami(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Ramo).order_by(Ramo.id).offset(skip).limit(limit).all()

def get_ramo(db: Session, ramo_id: str) -> Ramo:
    return db.query(Ramo).filter(Ramo.id == ramo_id).first()

def create_ramo_entry(db: Session, ramo: RamoCreate):
    db_comune = Ramo(**ramo.dict())
    db.add(db_comune)
    db.commit()
    db.refresh(db_comune)
    return db_comune