from sqlalchemy.orm import Session
from sqlalchemy import select
from models.core import PersonaFisica
from schemas.core import PersonaFisicaCreate

def get_persona_fisica(db: Session, persona_fisica_cf: str):
    return db.query(PersonaFisica).filter(PersonaFisica.cf == persona_fisica_cf).first()

def get_persone_fisiche(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PersonaFisica).offset(skip).limit(limit).all()

def create_persona_fisica_entry(db: Session, persona_fisica: PersonaFisicaCreate):
    db_persona_fisica = PersonaFisica(**persona_fisica.dict())
    db.add(db_persona_fisica)
    db.commit()
    db.refresh(db_persona_fisica)
    return db_persona_fisica