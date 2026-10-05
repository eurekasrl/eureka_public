from sqlalchemy.orm import Session

from models.core import Gruppo

def get_gruppo_by_id(db: Session, id: str)-> Gruppo:
    return db.query(Gruppo).filter(Gruppo.id == id).first()
