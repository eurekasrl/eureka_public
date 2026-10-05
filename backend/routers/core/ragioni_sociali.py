from typing import List, Optional
from fastapi import Depends, APIRouter, Query, HTTPException
from sqlalchemy.orm import Session

from db.db import get_db
from schemas.core import RagioneSociale
from crud.core.ragione_sociale import get_ragioni_sociali, get_ragione_sociale_by_id

router = APIRouter()

@router.get("/list", response_model=List[RagioneSociale])
def read_ragioni_sociali(
    skip: int = 0, 
    limit: int = 100,
    q: Optional[str] = Query(None, description="Optional search for ragione sociale"),
    db: Session = Depends(get_db)
):
    query_limit = limit if not q else 100
    return get_ragioni_sociali(db, skip=skip, limit=query_limit, iniziali=q)

@router.get("/{ragione_sociale_id}", response_model=RagioneSociale)
def read_ragione_sociale(
    ragione_sociale_id: str,
    db: Session = Depends(get_db)
):
    persona = get_ragione_sociale_by_id(db, ragione_sociale_id)
    if persona is None:
        raise HTTPException(status_code=404, detail="Ragione Sociale not found")
    return persona
