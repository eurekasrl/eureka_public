from sqlalchemy.orm import Session


from models.grandine import Prodotto


def get_dettaglio_by_id(db, prodotto_id)-> Prodotto:
    return db.query(Prodotto).filter(Prodotto.id == prodotto_id).first()

def get_dettaglio_by_condifesa(db: Session, skip: int = 0, limit: int = 100, condifesa_id:str="", iniziali=None, individuale=False):
    stmt = db.query(Prodotto).order_by(Prodotto.id)
    if not individuale:
        stmt = stmt.filter(Prodotto.condifesa_id==condifesa_id)
    if iniziali:
        stmt = stmt.filter(Prodotto.nome.ilike(f"%{iniziali}%") | 
                    Prodotto.dettaglio.ilike(f"%{iniziali}%")
        )
    return stmt.offset(skip).limit(limit).all()

def get_prodotti_by_codice_ministeriale(db, codice_ministeriale: str):
    return db.query(Prodotto).filter(Prodotto.codice_ministeriale == codice_ministeriale).all()

def get_prodotto_by_codice_ministeriale(db, codice_ministeriale: str):
    return db.query(Prodotto).filter(Prodotto.codice_ministeriale == codice_ministeriale).first()

def get_prodotti_by_gruppo(db, gruppo: str):
    return db.query(Prodotto).filter(Prodotto.gruppo == gruppo).all()

def get_prodotti_by_nome(db, nome:str):
    return db.query(Prodotto).filter(Prodotto.nome.ilike(f"%{nome}%")).all()

def get_dettaglio_by_condifesa_and_codice_avepa(db, condifesa_id, codice_avepa):
    return db.query(Prodotto).filter(Prodotto.condifesa_id == condifesa_id, Prodotto.codice_avepa == codice_avepa).first()

def get_dettaglio_by_condifesa_and_codice_avepa_dettagliato(db, condifesa_id, codice_avepa_dettagliato):
    return db.query(Prodotto).filter(Prodotto.condifesa_id == condifesa_id, Prodotto.codice_avepa_dettagliato == codice_avepa_dettagliato).first()

def get_dettaglio_by_condifesa_and_codice_ministeriale(db, condifesa_id, codice_ministeriale, dettaglio_avepa = None, id_avepa = None):
    if dettaglio_avepa:
        first_try = db.query(Prodotto).filter(Prodotto.condifesa_id == condifesa_id,
                                        Prodotto.codice_ministeriale == codice_ministeriale,
                                        Prodotto.dettaglio_avepa == dettaglio_avepa).first()
    elif id_avepa:
        first_try = db.query(Prodotto).filter(Prodotto.condifesa_id == condifesa_id,
                                        Prodotto.codice_ministeriale == codice_ministeriale,
                                        Prodotto.codice_avepa == id_avepa).first()
    
    if not first_try:
        return db.query(Prodotto).filter(Prodotto.condifesa_id == condifesa_id,
                                     Prodotto.codice_ministeriale == codice_ministeriale).first()
    return first_try