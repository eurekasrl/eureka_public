from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from db.db import get_db
from schemas.core import BigGruppo
from crud.core.gruppo import get_gruppo_by_id

router = APIRouter()


@router.get("/{gruppo_id}", response_model=BigGruppo)
def read_gruppo(
    gruppo_id: str,
    db: Session = Depends(get_db)
):
    gruppo = get_gruppo_by_id(db, gruppo_id)
    if gruppo is None:
        raise HTTPException(status_code=404, detail="Gruppo not found")
    return gruppo
