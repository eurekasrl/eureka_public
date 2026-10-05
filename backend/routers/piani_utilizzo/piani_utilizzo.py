from typing import List, Dict, Any


from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import insert


from crud.grandine.piano_utilizzo import get_piani_utilizzo_by_ragione_sociale, get_piano_utilizzo, create_piano_utilizzo_dettagliato_entry, get_piani_utilizzo_dettagliati_by_ragione_sociale, get_piani_utilizzo_comparison_dashboard, create_piano_bulk, get_distinct_anni_dettagliato
from crud.utils import get_piani_utilizzo_by_preventivo_id
from schemas.grandine import PianoUtilizzo as PianoUtilizzoSchema, PianoCreateResponse, PianoBulkCreate, PianoUtilizzoDettagliato as PianoUtilizzoDettagliatoSchema, DashboardComparisonRow, PartiteCheckResponse, PartitaCreate, PianoUtilizzoBulkPayload
from db.db import get_db
from services.partite import get_check_partite_status, save_partite_bulk
from services.pdf_parser import parse_piano_utilizzo, PdfTextExtractionError
from models.grandine import PianoUtilizzo, PianoUtilizzoDettagliato

router = APIRouter()

@router.get("/ragioni-sociali/{ragione_sociale_id}/riepilogativi", response_model=List[PianoUtilizzoSchema])
def read_piani_utilizzo_by_ragione_sociale(
    ragione_sociale_id: str,
    anno: int = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all piani utilizzo for a specific ragione sociale, optionally filtered by year.
    """
    piani = get_piani_utilizzo_by_ragione_sociale(
        db=db,
        ragione_sociale_id=ragione_sociale_id,
        anno=anno,
        skip=skip,
        limit=limit
    )
    return piani

@router.get("/ragioni-sociali/{ragione_sociale_id}/dettagliati", response_model=List[PianoUtilizzoDettagliatoSchema])
def read_piani_utilizzo_dettagliati_by_ragione_sociale(
    ragione_sociale_id: str,
    anno: int = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get all piani utilizzo dettagliati for a specific ragione sociale, optionally filtered by year.
    """
    piani = get_piani_utilizzo_dettagliati_by_ragione_sociale(
        db=db,
        ragione_sociale_id=ragione_sociale_id,
        anno=anno
    )
    return piani

@router.get("/ragioni-sociali/{ragione_sociale_id}/anni", response_model=List[int])
def read_distinct_anni(ragione_sociale_id: str, db: Session = Depends(get_db)):
    """Return the campaign years that have dettagliato data for this client (desc)."""
    return get_distinct_anni_dettagliato(db, ragione_sociale_id)

@router.get("/ragioni-sociali/{ragione_sociale_id}/comparison", response_model=List[DashboardComparisonRow])
def read_comparison(
    ragione_sociale_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all piani utilizzo for a specific ragione sociale
    """
    try:
        return get_piani_utilizzo_comparison_dashboard(db, ragione_sociale_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preventivo/{preventivo_id}", response_model = List[PianoUtilizzoSchema])
def read_piani_utilizzo_by_preventivo_id(
    preventivo_id: str,
    db:Session = Depends(get_db)
):
    return get_piani_utilizzo_by_preventivo_id(db, preventivo_id=preventivo_id)

@router.get("/{id}", response_model = PianoUtilizzoSchema)
def read_piano_utilizzo(
    id: str,
    db:Session = Depends(get_db)
):
    return get_piano_utilizzo(db, id=id)

@router.post("/ragioni-sociali/{ragione_sociale_id}/dettagliati", response_model=PianoCreateResponse, status_code=status.HTTP_201_CREATED)
def create_piano_utilizzo_dettagliato(ragione_sociale_id:str, payload: PianoBulkCreate, db:Session = Depends(get_db)):
    """
    Create a new Grandine Preventivo.
    Accepts payload defined in PreventivoGrandineCreate schema.
    """
    try:
        for row in payload.rows:
            create_piano_utilizzo_dettagliato_entry(db, ragione_sociale_id, payload.condifesa_id, payload.anno, payload.secondo_raccolto, row)
        return {
            "message": "Salvataggio completato", 
            "rows_processed": len(payload.rows)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il salvataggio del preventivo: {str(e)}"
        )

@router.get("/ragioni-sociali/{ragione_sociale_id}/partite/check", response_model=PartiteCheckResponse)
def check_partite_status(ragione_sociale_id: str, anno: int = Query(None), db: Session = Depends(get_db)):
    return get_check_partite_status(db, ragione_sociale_id, anno)

@router.post("/ragioni-sociali/{ragione_sociale_id}/partite/confirm", status_code=status.HTTP_201_CREATED)
def confirm_partite_mapping(ragione_sociale_id: str, payload: list[PartitaCreate], db: Session = Depends(get_db)):
    try:
        save_partite_bulk(db, ragione_sociale_id, payload)
        return {"message": "Partite generate con successo"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    condifesa_id: str = Form(...),
    db: Session = Depends(get_db)
):
    content = await file.read()
    try:
        rows = parse_piano_utilizzo(content, condifesa_id, db)
    except PdfTextExtractionError as err:
        # Unreadable scan / corrupt file / OCR not available — show the reason to the user.
        raise HTTPException(status_code=422, detail=str(err))

    # Unique prodotti for the pre-sorting modal
    uniques = {}
    for row in rows:
        raw_str = row.get("prodotto_raw", "")
        if raw_str not in uniques:
            uniques[raw_str] = {
                "mapped_prodotto": row.get("mapped_prodotto"),
                "selected": row.get("mapped_prodotto") is not None,
            }

    # Unique comuni for the pre-sorting modal — same pattern as prodotti.
    # Only expose comuni where the automatic match failed (codice_comune is None),
    # so the user only needs to fix actual mismatches.
    unique_comuni = {}
    for row in rows:
        raw_str = row.get("comune", "")
        if raw_str and raw_str not in unique_comuni:
            unique_comuni[raw_str] = {
                "codice_comune": row.get("codice_comune"),
                "nome_comune": row.get("comune"),
                "matched": row.get("codice_comune") is not None,
            }

    return {"raw_rows": rows, "uniques": uniques, "unique_comuni": unique_comuni}

@router.post("/apply-mapping")
async def apply_mapping(
    payload: Dict[str, Any],
    # Receives { "raw_rows": [], "mapping": {prodotto_raw: {...}}, "comune_mapping": {raw_comune: {...}} }
):
    import time

    raw_rows = payload.get("raw_rows", [])
    mapping = payload.get("mapping", {})
    comune_mapping = payload.get("comune_mapping", {})
    timestamp = int(time.time() * 1000)

    final_rows = []
    for idx, item in enumerate(raw_rows):
        prod_info = mapping.get(item["prodotto_raw"], {"selected": False, "mapped_prodotto": None})

        # Resolve comune: prefer user-confirmed mapping, fall back to parser result
        raw_comune = item.get("comune", "")
        com_info = comune_mapping.get(raw_comune)
        if com_info:
            resolved_comune = com_info.get("nome_comune") or raw_comune
            resolved_codice = com_info.get("codice_comune")
        else:
            resolved_comune = raw_comune
            resolved_codice = item.get("codice_comune")

        final_rows.append({
            "tempId": f"pdf-{timestamp}-{idx}",
            "selected": prod_info["selected"],
            "comune": resolved_comune,
            "codice_comune": resolved_codice,
            "foglio": item.get("foglio", ""),
            "particella": item.get("particella", ""),
            "superficie": item.get("superficie", 0),
            "data_semina_trapianto": item.get("data_semina_trapianto", ""),
            "mapped_prodotto": prod_info["mapped_prodotto"],
            "prodotto_raw": item.get("prodotto_raw", ""),
            "serra": item.get("serra", False),
            "bio": item.get("bio", False),
            "secondo_raccolto": False,
            "note": "",
            "raw_line": item.get("raw_line", ""),
            "isManual": False,
        })

    return final_rows

@router.post("/bulk")
async def create_piano_utilizzo_bulk(
    payload: PianoUtilizzoBulkPayload,
    is_dettagliato: bool,
    db: Session = Depends(get_db)
):
    try:
        TargetModel = PianoUtilizzoDettagliato if is_dettagliato else PianoUtilizzo
        # A. WIPE: Delete ALL existing rows for this client and year
        # This makes the "Save" act as a "Sync"
        db.query(TargetModel).filter(
            TargetModel.ragione_sociale_id == payload.ragione_sociale_id,
            TargetModel.anno == payload.anno
        ).delete()

        # B. PREPARE NEW ROWS
        data_to_insert = create_piano_bulk(payload, is_dettagliato)
        if not data_to_insert:
            return {"message": "Nessun dato da inserire"}

        # C. INSERT
        stmt = insert(TargetModel).values(data_to_insert)
        db.execute(stmt)
        db.commit()

        return {
            "status": "success", 
            "message": f"Inserite con successo {len(data_to_insert)} righe."
        }

    except Exception as e:
        db.rollback()
        print(f"Error during bulk insert: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail=f"Errore durante il salvataggio: {str(e)}"
        )
    
@router.delete("/{id}")
async def delete_piano_utilizzo(
    id: str, 
    is_dettagliato: bool, 
    db: Session = Depends(get_db)
):
    TargetModel = PianoUtilizzoDettagliato if is_dettagliato else PianoUtilizzo
    db_row = db.query(TargetModel).filter(TargetModel.id == id).first()
    if not db_row:
        raise HTTPException(status_code=404, detail="Riga non trovata")
    
    db.delete(db_row)
    db.commit()
    return {"message": "Riga eliminata con successo"}
    