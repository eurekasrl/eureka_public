from typing import List, Optional

from fastapi import Depends, HTTPException, APIRouter, Query
from sqlalchemy.orm import Session


from db.db import get_db
from schemas.core import PersonaFisicaCreate, PersonaFisica
from crud.core.persona_fisica import create_persona_fisica_entry, get_persona_fisica, get_persone_fisiche


router = APIRouter()


@router.post("/", response_model=PersonaFisica)
def create_persona_fisica(persona_fisica: PersonaFisicaCreate, db: Session = Depends(get_db)):
    return create_persona_fisica_entry(db=db, persona_fisica=persona_fisica)

@router.get("/", response_model=List[PersonaFisica])
def read_persone_fisiche(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    persone_fisiche = get_persone_fisiche(db, skip=skip, limit=limit)
    return persone_fisiche

@router.get("/{persona_fisica_cf}", response_model=PersonaFisica)
def read_persona_fisica(persona_fisica_cf: str, db: Session = Depends(get_db)):
    db_persona_fisica = get_persona_fisica(db, persona_fisica_cf=persona_fisica_cf)
    if db_persona_fisica is None:
        raise HTTPException(status_code=404, detail="Persona Fisica not found")
    return db