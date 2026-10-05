from uuid import UUID
from typing import Tuple

from sqlalchemy.orm import Session

from models.grandine import PreventivoGrandine
from schemas.grandine import PreventivoGrandineCreate, PreventivoGrandine as PreventivoGrandineSchema, PreventivoGrandinePatch
from crud.sale.preventivo import create_preventivo_entry, update_preventivo
from crud.utils import uuid_to_str, compare_on_patch
from db.utils import try_commit
from crud.grandine.piano_utilizzo import get_piano_utilizzo

def get_grandine_preventivo(db: Session, sale_preventivo_id: UUID):
    """Get a single piano utilizzo by its ID"""
    return db.query(PreventivoGrandine).filter(PreventivoGrandine.sale_preventivo_id == str(sale_preventivo_id)).first()

def create_grandine_preventivo_entry(db: Session, preventivo_in: PreventivoGrandineCreate) -> str:
    data = preventivo_in.model_dump(exclude_unset=True)
    data = uuid_to_str(data)
    
     # 1️⃣ CREATE GENERAL PREVENTIVO FIRST
    preventivo_db = create_preventivo_entry(
        data["ragione_sociale_id"],
        data["ramo_id"],
        data["intermediario_id"],
        data["compagnia_id"],
        db
    )

    # 2️⃣ REMOVE these fields so they don’t conflict with PreventivoGrandine
    del data["ragione_sociale_id"]
    del data["ramo_id"]
    del data["intermediario_id"]
    del data["compagnia_id"]

    # 3️⃣ CREATE PREVENTIVO GRANDINE
    preventivo_grandine_db = PreventivoGrandine(
        sale_preventivo_id = preventivo_db.id,
        **data
    )

    new_entry = try_commit(db, preventivo_grandine_db)
    return new_entry.preventivo.ragione_sociale_id
    
def patch_grandine_preventivo_entry(db: Session, existing_preventivo: PreventivoGrandineSchema, new_preventivo_data: PreventivoGrandinePatch) -> Tuple[bool, str]:
    data_to_add, data_changed = compare_on_patch(new_preventivo_data.model_dump(), existing_preventivo)

    if data_changed:
        db.add(data_to_add)
        db.flush()
        #patching the grandine preventivo means resetting the underling sale preventivo
        update_preventivo(db, preventivo_id= existing_preventivo.sale_preventivo_id, stato=3)
        return True, data_to_add.preventivo.ragione_sociale_id
    return False, data_to_add.preventivo.ragione_sociale_id

def reset_preventivo_grandine_by_pu(db, piano_utilizzo_id=None, piano_utilizzo_dettagliato_id=None):
    if piano_utilizzo_id:
        piano_utilizzo_db = get_piano_utilizzo(db, piano_utilizzo_id)
        for preventivo_grandine in piano_utilizzo_db.preventivo_grandine:
            resetted_preventivo_grandine = PreventivoGrandinePatch(
                sale_preventivo_id=preventivo_grandine.preventivo.id, 
                piano_utilizzo_id=preventivo_grandine.piano_utilizzo.id,
                premio_lordo=0
                )
            patch_grandine_preventivo_entry(db, existing_preventivo=preventivo_grandine, new_preventivo_data=resetted_preventivo_grandine)
