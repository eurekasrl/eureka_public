from typing import List, Optional

from fastapi import Depends, HTTPException, APIRouter, Query
from sqlalchemy.orm import Session


from db.db import get_db
from schemas.grandine import Prodotto, ProdottoCreate
from crud.grandine.prodotto import get_dettaglio_by_condifesa, get_dettaglio_by_id
from crud.core.condifesa import get_condifesa_by_id


router = APIRouter()

#@router.post("/", response_model=Prodotto)
#def create_comune(prodotto: ProdottoCreate, db: Session = Depends(get_db)):
#    return create_prodotto_entry(db=db, prodotto=prodotto)

@router.get("/condifesa/{condifesa_id}", response_model=List[Prodotto])
def read_prodotti_by_condifesa(
    condifesa_id: str,
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = Query(None, description="Optional search for prodotto"),
    db: Session = Depends(get_db)
):
    query_limit = limit if not q else 100
    condifesa_db = get_condifesa_by_id(db, condifesa_id)
    individuale = True if condifesa_db.nome=='INDIVIDUALE' else False
    
    return get_dettaglio_by_condifesa(db, skip=skip, limit=query_limit, condifesa_id = condifesa_id, iniziali=q, individuale=individuale)

@router.get("/{id}", response_model=Prodotto)
def read_prodotto(id: str, db: Session = Depends(get_db)):
    db_prodotto = get_dettaglio_by_id(db, prodotto_id=id)
    if db_prodotto is None:
        raise HTTPException(status_code=404, detail="Prodotto not found")
    return db_prodotto
