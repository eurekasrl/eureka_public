from typing import List
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from db.db import get_db
from schemas.core import RelazioneRci
from crud.core.relazione_rci import get_relazione_by_ramo


router = APIRouter()

@router.get("/{ramo_id}", response_model=List[RelazioneRci])
def read_relazione_by_ramo(ramo_id:str, db: Session = Depends(get_db)):
    return get_relazione_by_ramo(db, ramo_id)