from sqlalchemy.orm import Session

from models.sale import DocumentoArchivio

def get_doc_by_ragione_sociale(db: Session, ragione_sociale_id: str):
    return db.query(DocumentoArchivio).filter(
        DocumentoArchivio.ragione_sociale_id == ragione_sociale_id
    ).all()

def get_unique_doc_arch(db: Session, ragione_sociale_id: str, documento_id: str, anno: int):
    return db.query(DocumentoArchivio).filter(
        DocumentoArchivio.ragione_sociale_id == ragione_sociale_id,
        DocumentoArchivio.documento_id == documento_id,
        DocumentoArchivio.anno == anno 
        ).first()
