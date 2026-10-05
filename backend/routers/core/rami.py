from typing import List
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from db.db import get_db
from schemas.core import Ramo
from crud.core.ramo import get_rami, get_ramo


router = APIRouter()

@router.get("/list", response_model=List[Ramo])
def read_rami(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_rami (db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Ramo)
def read_ramo(id: str, db: Session = Depends(get_db)):
    return get_ramo(db, ramo_id=id)
