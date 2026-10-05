from typing import List, Optional

from fastapi import Depends, HTTPException, APIRouter, Query
from sqlalchemy.orm import Session


from db.db import get_db
from schemas.grandine import Tassi
from crud.utils import get_tassi_by_piano_utilizzo_preventivo, get_tassi_by_piano_utilizzo_compagnia_intermediario

router = APIRouter()

@router.get("/list/preventivo", response_model = List[Tassi])
def read_tassi_by_preventivo(
        db: Session = Depends(get_db),
        piano_utilizzo_id: str = Query(None, description="Optional search for piano_utilizzo_id"),
        preventivo_id: str = Query(None, description="Optional search for preventivo_id"),
):
    return get_tassi_by_piano_utilizzo_preventivo (db, piano_utilizzo_id, preventivo_id)

@router.get("/list/compagnia_intermediario", response_model = List[Tassi])
def read_tassi_by_compagnia_intermediario(
        db: Session = Depends(get_db),
        piano_utilizzo_id: str = Query(None, description="Optional search for piano_utilizzo_id"),
        compagnia_id: str = Query(None, description="Optional search for compagnia_id"),
        intermediario_id: str = Query(None, description="Optional search for intermediario_id"),
):
    return get_tassi_by_piano_utilizzo_compagnia_intermediario (db, piano_utilizzo_id, compagnia_id, intermediario_id)