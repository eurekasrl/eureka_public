from typing import List

from sqlalchemy import distinct
from sqlalchemy.orm import Session

from models.core import Documento

def get_documents_sigla(db: Session) -> List[str]:
    return [sigla[0] for sigla in db.query(distinct(Documento.sigla)).all()]
