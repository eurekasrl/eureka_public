from typing import List
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from db.db import get_db
from schemas.core import Intermediario
from crud.core.intermediari import get_intermediari


router = APIRouter()

@router.get("/list", response_model=List[Intermediario])
def read_intermediari(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_intermediari (db, skip=skip, limit=limit)