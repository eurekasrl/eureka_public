from typing import List, Optional, Union, Dict

from fastapi import Depends, APIRouter, Query, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session



from db.db import get_db
from schemas.sale import Preventivo, PreventivoCreate
from crud.sale.preventivo import (
    create_preventivo_entry, get_preventivi_by_ragione_sociale_id, 
    get_preventivo, update_preventivo, delete_preventivo_entry, get_preventivi_by_gruppo_id)
from crud.sale.utils import get_preventivo_by_ragione_sociale_id_for_page, preventivi_for_download, get_preventivo_by_gruppo_id_for_page
from schemas.admin import EmailRequest
from smtp.utils import send_smtp_email
from models.sale import Preventivo as PreventivoORM

router = APIRouter()

@router.post("/", response_model=Preventivo)
def create_preventivo(preventivo_data: PreventivoCreate, db: Session = Depends(get_db)):
    ragione_sociale_id = str(preventivo_data.ragione_sociale_id)
    ramo_id = str(preventivo_data.ramo_id)
    intermediario_id = str(preventivo_data.intermediario_id)
    compagnia_id = str(preventivo_data.compagnia_id)

    return create_preventivo_entry(ragione_sociale_id, ramo_id, intermediario_id, compagnia_id, db)

@router.get("/ragioni-sociali/{ragione_sociale_id}", response_model=List[Preventivo])
def read_preventivi_by_ragione_sociale_id(
    ragione_sociale_id: str,
    db: Session = Depends(get_db),
):
    """
    Get all preventivi for a specific ragione sociale
    """
    return get_preventivi_by_ragione_sociale_id(
        db=db,
        ragione_sociale_id=ragione_sociale_id
    )

@router.get("/page/ragioni-sociali/{ragione_sociale_id}")
def read_preventivi_by_ragione_sociale_id_for_page(
    ragione_sociale_id: str,
    page: str,
    db: Session = Depends(get_db),
    ramo_id: Optional[str] = Query(None, description="Optional search for ramo_id"),
    anno: Optional[int] = Query(None, description="Optional search for anno"),
    lifecycle_id: Optional[int] = Query(None, description="Optional search for lifecycle")
):
    """
    Get all preventivi for a specific ragione sociale
    """
    return get_preventivo_by_ragione_sociale_id_for_page(db, ragione_sociale_id, page, ramo_id, anno, lifecycle_id)

@router.get("/gruppi/{gruppo_id}", response_model=Dict[str, List[Preventivo]])
def read_preventivi_by_gruppo_id(
    gruppo_id: str,
    db: Session = Depends(get_db),
):
    """
    Get all preventivi for a specific ragione sociale
    """
    return get_preventivi_by_gruppo_id(
        db=db,
        gruppo_id=gruppo_id
    )

@router.get("/page/gruppi/{gruppo_id}")
def read_preventivi_by_gruppo_id_for_page(
    gruppo_id: str,
    page: str,
    db: Session = Depends(get_db),
    ramo_id: Optional[str] = Query(None, description="Optional search for ramo_id"),
    anno: Optional[int] = Query(None, description="Optional search for anno")
):
    """
    Get all preventivi for a specific Gruppo
    """
    return get_preventivo_by_gruppo_id_for_page(db, gruppo_id, page, ramo_id, anno)

@router.get("/edit/{preventivo_id}", response_model=Union[Preventivo, str])
def read_preventivo (
    preventivo_id:str,
    db:Session= Depends(get_db),
    q: Optional[str] = Query(None, description="Optional search for specific field")
    ):
    data = get_preventivo(db=db, preventivo_id = preventivo_id)
    if q:
        parts = q.split('.')
        current_value = data
        try:
            for part in parts:
                current_value = getattr(current_value, part)
            return current_value
        except AttributeError:
            raise HTTPException(status_code=404, detail=f"Field '{q}' not found for this preventivo.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error accessing field '{q}': {str(e)}")
    return data

@router.delete("/delete/{preventivo_id}")
def delete_preventivo(
    preventivo_id: str, 
    ramo_nome: str = Query(..., description="The branch name to identify sub-tables"), # Query param
    db: Session = Depends(get_db)
):
    return delete_preventivo_entry(db, preventivo_id, ramo_nome)

@router.patch("/{esito}/{preventivo_id}")
def patch_preventivo(esito: str, preventivo_id: str, db:Session= Depends(get_db)):
    return update_preventivo(db, preventivo_id, stato = esito)

@router.get("/download/csv", response_class=StreamingResponse)
def download_preventivi_csv(
    client_level_id:str,
    client_level:str,
    ramo_id: str,
    anno: int,
    ids: Optional[str] = Query(None, description="Comma separated list of IDs to include"),
    db: Session = Depends(get_db)
):
    """
    Generates and downloads a CSV file of Preventivi filtered by 
    Ragione Sociale, Ramo, and Year.
    """
    id_list = ids.split(",") if ids else None

    filename, output = preventivi_for_download(db, client_level_id, client_level, ramo_id, anno, id_list, "csv")
    return StreamingResponse(
        output, 
        media_type="text/csv", 
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
            }
    )

@router.post("/send-email/{destinatario}")
async def send_preventivi_email(
    destinatario: str,
    request: EmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    send_smtp_email( request, background_tasks, destinatario, db)
    for preventivo_id in request.selected_ids:
        db.query(PreventivoORM).get(str(preventivo_id)).advance_lifecycle()
        db.commit()
    return {"message": "Email inviata con successo"}
