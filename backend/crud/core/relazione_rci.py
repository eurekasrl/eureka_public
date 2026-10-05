from sqlalchemy.orm import Session
from models.core import RelazioneRci

def get_relazione_by_ramo(db: Session, ramo_id:str):
    return db.query(RelazioneRci).filter(RelazioneRci.ramo_id == ramo_id, RelazioneRci.active).all()