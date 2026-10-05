from typing import List, Optional, Union, Dict

from fastapi import Depends, APIRouter, Query, HTTPException, BackgroundTasks, UploadFile, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from db.db import get_db
from services.document_services import DocumentService

router = APIRouter()
doc_service = DocumentService()

@router.get("/ragioni-sociali/{ragione_sociale_id}")
def get_documents_status(
    ragione_sociale_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns the matrix of required documents and their status.
    """
    return doc_service.get_ragione_sociale_documents_stato(db, ragione_sociale_id)

@router.post("/ragioni-sociali/{ragione_sociale_id}/documento/{documento_id}")
def upload_document(
    ragione_sociale_id: str,
    documento_id: str,
    file: UploadFile,
    anno: int = Form(...),
    signed: bool = Form(False),
    sent: bool = Form(False),
    linked_ids: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """
    Uploads a document to the archive.
    """
    return doc_service.upload(
        db=db,
        file=file,
        ragione_sociale_id=ragione_sociale_id,
        documento_id=documento_id,
        anno=anno,
        signed=signed,
        sent=sent,
        linked_ids=linked_ids
    )

@router.get("/view/{archive_id}")
def view_document(
    archive_id: str,
    db: Session = Depends(get_db)
):
    return doc_service.view_document(db, archive_id)

@router.delete("/archivio/{archive_id}")
def delete_document(
    archive_id: str,
    db: Session = Depends(get_db)
):
    return doc_service.delete_document(db, archive_id)

@router.delete("/ragioni-sociali/{ragione_sociale_id}/documento/{documento_id}")
def delete_document_group(
    ragione_sociale_id: str,
    documento_id: str,
    db: Session = Depends(get_db)
):
    return doc_service.delete_document_group(db, ragione_sociale_id, documento_id)

