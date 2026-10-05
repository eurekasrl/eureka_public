from typing import List, Optional

from fastapi import Depends, HTTPException, APIRouter, Query
from sqlalchemy.orm import Session


from db.db import get_db
from schemas.core import ComuneCreate, Comune
from crud.core.comune import create_comune_entry, get_comune, get_comuni


router = APIRouter()

@router.post("/", response_model=Comune)
def create_comune(comune: ComuneCreate, db: Session = Depends(get_db)):
    return create_comune_entry(db=db, comune=comune)

@router.get("/list", response_model=List[Comune])
def read_comuni(
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = Query(None, description="Optional search for comune name"),
    db: Session = Depends(get_db)
):
    query_limit = limit if not q else 100
    return get_comuni(db, skip=skip, limit=query_limit, iniziali=q)


@router.get("/{codice_comune}", response_model=Comune)
def read_comune(codice_comune: str, db: Session = Depends(get_db)):
    db_comune = get_comune(db, codice_comune=codice_comune)
    if db_comune is None:
        raise HTTPException(status_code=404, detail="Comune not found")
    return db_comune
