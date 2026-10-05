import math
from typing import List
import uuid
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select, func, delete, insert

from models.grandine import PianoUtilizzoDettagliato, Partita
from crud.grandine.piano_utilizzo import get_piani_utilizzo_dettagliati_by_ragione_sociale

MAX_PARTITA_SURFACE = 30000 # 3 Hectares

def generate_partite_draft_logic(db: Session, ragione_sociale_id: str, anno: int = None):
    # 1. Fetch all PUDs for this RS and campaign year
    # ORDER BY is critical: Group keys first, then Foglio, then Particella
    puds = get_piani_utilizzo_dettagliati_by_ragione_sociale(db, ragione_sociale_id, anno)

    draft_rows = []
    
    # State variables
    current_partita_num = 1
    current_bucket_surface = 0
    
    # Trackers to detect changes
    last_group_key = None # Tracks Product/Comune/Bio/etc.
    last_foglio = None    # Tracks Foglio changes within the same group

    for pud in puds:
        # A. Define the "Major Group" Key (Everything EXCEPT Foglio)
        # When this changes, we reset numbering to #1
        current_group_key = (
            pud.condifesa_id,
            pud.anno,
            pud.codice_comune,
            pud.prodotto_id,
            pud.serra,
            pud.bio,
            pud.secondo_raccolto
        )

        # B. Define the "Minor" Key (Foglio)
        # When this changes (but Group is same), we increment numbering (+1)
        current_foglio = pud.foglio

        # --- LOGIC TO RESET OR INCREMENT ---
        
        # 1. Check if we switched Product/Comune etc.
        if last_group_key is not None and current_group_key != last_group_key:
            current_partita_num = 1     # <--- RESET TO 1
            current_bucket_surface = 0  # Empty bucket
        
        # 2. Check if we switched Foglio (within the same Product)
        elif last_foglio is not None and current_foglio != last_foglio:
            current_partita_num += 1    # <--- INCREMENT
            current_bucket_surface = 0  # Empty bucket

        # Update trackers
        last_group_key = current_group_key
        last_foglio = current_foglio
        
        remaining_pud_surface = pud.superficie

        # --- Handling Splits and filling Buckets ---
        while remaining_pud_surface > 0:
            space_in_bucket = MAX_PARTITA_SURFACE - current_bucket_surface
            
            # If bucket is full, increment number and empty bucket
            if space_in_bucket <= 0:
                current_partita_num += 1
                current_bucket_surface = 0
                space_in_bucket = MAX_PARTITA_SURFACE

            # Determine how much of this PUD goes into the current Partita
            take_amount = min(remaining_pud_surface, space_in_bucket)
            
            # Determine suffix (p = parziale)
            is_split = take_amount < pud.superficie
            part_suffix = "p" if (is_split or remaining_pud_surface < pud.superficie) else ""

            draft_rows.append({
                "pud_id": pud.id,
                # Fields needed for prezzi lookup on the frontend
                "condifesa_id": str(pud.condifesa_id),
                "prodotto_id": str(pud.prodotto_id),
                "anno": pud.anno,
                # Frontend display info
                "comune": str(pud.comune.nome) if pud.comune else str(pud.codice_comune),
                "prodotto": f"{pud.prodotto.nome}-{pud.prodotto.dettaglio}" if pud.prodotto else str(pud.prodotto_id),
                "foglio_orig": pud.foglio,
                "particella_orig": pud.particella,
                
                # Calculated
                "numero_partita": current_partita_num,
                "foglio_assegnato": str(pud.foglio),
                "particella_assegnata": f"{pud.particella}{part_suffix}",
                "superficie_assegnata": int(take_amount),
                "is_split": is_split
            })

            # Update counters
            current_bucket_surface += take_amount
            remaining_pud_surface -= take_amount

    return draft_rows

def get_check_partite_status(db: Session, ragione_sociale_id: str, anno: int = None):
    # Resolve the campaign year: explicit param wins; otherwise the most recent
    # year with data for this client; finally the current calendar year.
    if anno is None:
        anno = db.query(func.max(PianoUtilizzoDettagliato.anno))\
            .filter(PianoUtilizzoDettagliato.ragione_sociale_id == ragione_sociale_id)\
            .scalar() or datetime.now().year

    # 1. Calc Total PUD Surface
    total_pud = db.query(func.sum(PianoUtilizzoDettagliato.superficie))\
        .filter(PianoUtilizzoDettagliato.ragione_sociale_id == ragione_sociale_id,
                PianoUtilizzoDettagliato.anno == anno)\
        .scalar() or 0

    # 2. Calc Total Partite Surface (via Join)
    total_partita = db.query(func.sum(Partita.superficie))\
        .join(PianoUtilizzoDettagliato)\
        .filter(PianoUtilizzoDettagliato.ragione_sociale_id == ragione_sociale_id,
                PianoUtilizzoDettagliato.anno == anno)\
        .scalar() or 0

    is_balanced = total_pud == total_partita and total_pud > 0

    # 3. If not balanced, generate draft
    payload = []
    if is_balanced:
        payload = db.query(Partita).join(PianoUtilizzoDettagliato).filter(PianoUtilizzoDettagliato.ragione_sociale_id == ragione_sociale_id,
                                                                          PianoUtilizzoDettagliato.anno == anno).all()
    else:
        payload = generate_partite_draft_logic(db, ragione_sociale_id, anno)

    return {
        "total_superficie_pud": total_pud,
        "total_superficie_partite": total_partita,
        "is_balanced": is_balanced,
        "payload": payload
    }

def save_partite_bulk(db: Session, ragione_sociale_id: str, payload: List[dict]):

    # 1. WIPE existing partite for this RS to avoid duplicates/mess
    # Find all PUD IDs for this RS
    pud_subquery = select(PianoUtilizzoDettagliato.id).where(
        PianoUtilizzoDettagliato.ragione_sociale_id == ragione_sociale_id
    )

    delete_stmt = delete(Partita).where(
        Partita.piano_utilizzo_dettagliato_id.in_(pud_subquery)
    )

    db.execute(delete_stmt)
    db.flush()

    # 2. Bulk Insert New Partite
    new_objects = []
    current_time = datetime.now()

    for row in payload:
        new_objects.append({
                "id": str(uuid.uuid4()), # Generate ID manually
                "piano_utilizzo_dettagliato_id": str(row.piano_utilizzo_dettagliato_id),
                "numero": row.numero,
                "foglio": row.foglio,
                "particella": row.particella,
                "superficie": row.superficie,
                # Explicitly set timestamps to avoid DB round-trips
                "created_at": current_time, 
                "updated_at": None
            })
    if new_objects:
        db.execute(insert(Partita), new_objects)
        db.commit()
        