import os
import shutil
import mimetypes
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple, Set
from datetime import datetime

from sqlalchemy import distinct, Row
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse

from models.core import Documento, RagioneSociale
from models.sale import Preventivo, DocumentoArchivio
from schemas.config import settings
from crud.utils import sanitize_name
from crud.core.documento import get_documents_sigla
from services.utils import get_column_match_count

class DocumentService:
    def __init__(self):
        self.base_path = Path(settings.MOUNT_PATH_EUREKA)

    def get_ragione_sociale_documents_stato(self, db: Session, ragione_sociale_id: str) -> Dict[str, Any]:
        """
        Main Orchestrator:
        1. Checks Folder Structure.
        2. Calculates required documents.
        3. SYNC: Checks if files exist physically and updates DB if records are missing.
        4. Returns the final matrix.
        """
        # A. Diagnostic Check
        diagnostic = self.diagnose_storage_structure(db, ragione_sociale_id)
        
        # Fetch RS for path generation
        rs = db.query(RagioneSociale).filter(RagioneSociale.id == ragione_sociale_id).first()
        if not rs:
             # Basic error handling if RS doesn't exist, though diagnose handles this mostly
             return {"folder_diagnostic": diagnostic, "documents": []}

        # B. Data Fetching
        preventivi = db.query(Preventivo).filter(Preventivo.ragione_sociale_id == ragione_sociale_id).all()
        all_docs = db.query(Documento).all()
        all_docs_sigla = get_documents_sigla(db)
        
        # C. Determine required docs ("The Tournament")
        winning_docs_map = self._determine_required_documents(all_docs, all_docs_sigla, preventivi)

        # We look up existing archives *before* sync to know what's missing
        existing_archives = db.query(DocumentoArchivio).filter(DocumentoArchivio.ragione_sociale_id == ragione_sociale_id).all()
        
        # Map: Document ID -> Archive Record
        archives_by_doc = {}
        for arch in existing_archives:
            d_id = str(arch.documento_id)
            if d_id not in archives_by_doc:
                archives_by_doc[d_id] = []
            archives_by_doc[d_id].append(arch)

        # E. Build Final Response
        final_doc_list = []
        for sigla, doc_def in winning_docs_map.items():
            doc_id_str = str(doc_def.id)
            doc_archives = archives_by_doc.get(doc_id_str, [])

            doc_info = {
                "id": doc_def.id, 
                "nome": doc_def.nome, 
                "sigla": doc_def.sigla,
                "signed": doc_def.signed,
                "personale": doc_def.personale,
                "mandatory": doc_def.mandatory,
                "entity": doc_def.entity
            }

            if not doc_archives:
                final_doc_list.append({
                    "documento": doc_info,
                    "archive_id": None, # Explicitly Null
                    **self._resolve_file_stato(None) # Returns "MISSING" defaults
                })
            
            # CASE 2: ARCHIVES FOUND (1 or More)
            else:
                for arch in doc_archives:
                    final_doc_list.append({
                        "documento": doc_info,
                        
                        # --- FIX IS HERE: Inject the specific Archive UUID ---
                        "archive_id": str(arch.id), 
                        
                        **self._resolve_file_stato(arch)
                    })

        return {
            "folder_diagnostic": diagnostic,
            "documents": final_doc_list
        }
    
    def _get_storage_details(self, rs: RagioneSociale, doc_template: Documento, anno: int, unique_suffix: bool = False) -> Tuple[Path, str]:
        """
        Centralizes the logic for where a file *should* be.
        Returns (Full_Absolute_Path, Relative_Path_String)
        """
        gruppo_nome = sanitize_name(rs.gruppo.nome) if rs.gruppo else "NoGroup"
        # We assume PDF for auto-discovery, though you could check for .docx if needed
        # Or ideally, check the directory for files starting with the prefix

        if doc_template.personale:
            # Personal: {Group}/Anagrafica/{Sigla}_{Referente}.ext
            ref_name = sanitize_name(rs.gruppo.referente.nome)
            safe_filename = f"{doc_template.sigla}_{ref_name}"
            rel_folder = Path(gruppo_nome) / "Anagrafica"
        else:
            # Standard: {Group}/{Client}/{Year}/{Sigla}_{Id}.ext
            safe_filename = f"{doc_template.sigla}_{rs.id.lower()}"
            rel_folder = Path(gruppo_nome) / sanitize_name(rs.nome) / str(anno)
        
        if unique_suffix:
            short_uuid = str(uuid.uuid4())[:8]
            safe_filename = f"{safe_filename}_{short_uuid}"

        full_dir= self.base_path / rel_folder
        
        return full_dir, safe_filename
    
    def _find_physical_file(self, directory: Path, file_stem: str) -> Optional[Path]:
        """
        Scans the directory for any file matching 'file_stem.*'
        Returns the full Path of the first match found, or None.
        """
        if not directory.exists():
            return None
        
        # Iterate over files in the directory
        for item in directory.iterdir():
            if item.is_file():
                # Check if the filename (without extension) matches our expected stem
                # AND ensure it's not a hidden file (starts with .)
                if item.stem == file_stem and not item.name.startswith("."):
                    return item
        
        return None

    def _determine_required_documents(self, all_docs: List[Documento], all_docs_sigla: List[str], preventivi: List[Preventivo]) -> List[Documento]:
        """
        Iterates all documents and compares them against all preventivi.
        Returns a map keyed by 'Sigla' containing the 'Winning' document version.
        """
        winning_docs = {}

        if preventivi:
            for prev in preventivi:
                if prev.lifecycle_id==1:
                    continue
                for sigla in all_docs_sigla:
                    docs_by_sigla = [doc for doc in all_docs if doc.sigla==sigla]
                    
                    result = {}
                    for doc_by_sigla in docs_by_sigla:
                        doc_by_sigla_score, doc_by_sigla_count = self._calculate_match_score(doc_by_sigla, prev)
                        if doc_by_sigla_score>0:
                            break
                        result[doc_by_sigla.id] = {}
                        result[doc_by_sigla.id]["score"] = doc_by_sigla_score
                        result[doc_by_sigla.id]["count"] = doc_by_sigla_count
                        result[doc_by_sigla.id]["object"] = doc_by_sigla
                    
                    min_score = float('inf')  # Set to infinity to find the minimum
                    max_count = -float('inf')  # Set to negative infinity to find the maximum
                    winner_id = None
                    if result:
                        for result_id, values in result.items():
                            score = values['score']
                            count = values['score']
                            if (score<min_score) or (score == min_score and count> max_count):
                                min_score = score
                                max_count = count
                                winner_id = result_id
                        winning_docs[sigla] = result[winner_id]["object"]

        return winning_docs

    def _calculate_match_score(self, doc: Documento, prev: Preventivo) -> float:
        """
        Compares a single document definition against a single preventivo.
        Returns (Score, Reason). Score 0 means no match.
        """
        # 1. Lifecycle Check
        if doc.lifecycle_id is not None:
            if prev.lifecycle_id < doc.lifecycle_id:
                return 1, 0

        # 2. Attribute Matching
        # Helper to treat None as wildcard
        match_ramo, count_ramo = get_column_match_count(doc.ramo_id, prev.ramo_id)
        match_compagnia, count_compagnia = get_column_match_count(doc.compagnia_id, prev.compagnia_id)
        match_intermediario, count_intermediario = get_column_match_count(doc.intermediario_id, prev.intermediario_id)

        # 3. Special Logic: Grandine
        match_grandine = 0
        count_grandine = 0
        if prev.ramo and prev.ramo.dettaglio and prev.ramo.dettaglio.lower() == "grandine":
            prev_code = prev.preventivo_grandine.piano_utilizzo.prodotto.codice_ministeriale
            match_grandine, count_grandine = get_column_match_count(doc.codice_ministeriale, prev_code)
            

        score = match_ramo + match_compagnia + match_intermediario + match_grandine
        count = count_ramo + count_compagnia + count_intermediario + count_grandine
        
        return score, count

    def _resolve_file_stato(self, archive_record: Optional[DocumentoArchivio]) -> Dict[str, Any]:
        """
        Checks DB record and Physical File existence.
        """
        if not archive_record:
            return {
                "stato": "MISSING",
                "last_update": None, "anno": None, 
                "signed": False, "sent": False, "file_path": None
            }

        full_path = self.base_path / archive_record.file_path
        
        if full_path.exists():
            stato = "UPLOADED" if archive_record.archivio else "PENDING_APPROVAL"
        else:
            stato = "FILE_NOT_FOUND"

        return {
            "stato": stato,
            "last_update": archive_record.updated_at,
            "anno": archive_record.anno,
            "signed": archive_record.signed,
            "sent": archive_record.sent,
            "file_path": archive_record.file_path
        }

    def _get_doc_def_by_id(self, all_docs, doc_id):
        for d in all_docs:
            if str(d.id) == str(doc_id): return d
        return None

    def _get_doc_sigla_by_id(self, all_docs, doc_id):
        d = self._get_doc_def_by_id(all_docs, doc_id)
        return d.sigla if d else None

    def diagnose_storage_structure(self, db: Session, ragione_sociale_id: str) -> Dict[str, Any]:
        """
        Checks if Mount -> Group -> Client -> Year folders exist.
        """
        rs = db.query(RagioneSociale).filter(RagioneSociale.id == ragione_sociale_id).first()
        if not rs:
            return {"exists": False, "error_code": "RS_NOT_FOUND", "message": "Ragione Sociale non trovata", "path": ""}

        if not self.base_path.exists():
            return {"exists": False, "error_code": "MISSING_MOUNT", "message": "Mount point non raggiungibile", "path": str(self.base_path)}

        gruppo_nome = rs.gruppo.nome if rs.gruppo else "NoGroup"
        group_path = self.base_path / sanitize_name(gruppo_nome)

        if not group_path.exists():
            return {"exists": False, "error_code": "MISSING_GROUP", "message": f"Manca cartella Gruppo: {gruppo_nome}", "path": str(group_path)}

        client_path = group_path / sanitize_name(rs.nome)
        if not client_path.exists():
            return {"exists": False, "error_code": "MISSING_CLIENT", "message": f"Manca cartella Ragione Sociale: {rs.nome}", "path": str(client_path)}

        # Year check is strict for diagnostics, but we don't block logic if missing
        current_year = datetime.now().year
        year_path = client_path / str(current_year)
        if not year_path.exists():
             return {"exists": False, "error_code": "MISSING_YEAR", "message": f"Manca cartella anno: {current_year}", "path": str(year_path)}

        return {"exists": True, "error_code": "OK", "message": "Struttura valida", "path": str(client_path)}
    
    def upload(self, db: Session, file: UploadFile, ragione_sociale_id: str, documento_id: str, anno: int, signed: bool, sent: bool, linked_ids: Optional[List[str]]):
        rs = db.query(RagioneSociale).filter(RagioneSociale.id == ragione_sociale_id).first()
        if not rs: raise HTTPException(status_code=404, detail="Ragione Sociale non trovata")
        
        doc_template = db.query(Documento).filter(Documento.id == documento_id).first()
        if not doc_template: raise HTTPException(status_code=404, detail="Tipo documento non trovato")

        is_transactional = (doc_template.entity is False or doc_template.entity == 0)

        # 1. Get Target Directory and Stem
        target_dir, file_stem = self._get_storage_details(rs, doc_template, anno, unique_suffix=is_transactional)
        
        # 2. Determine Extension from uploaded file
        # Fallback to .pdf if upload has no extension, though unlikely
        file_ext = os.path.splitext(file.filename)[1] or ".pdf"
        safe_filename = f"{file_stem}{file_ext}"
        full_path = target_dir / safe_filename
        
        # 3. Write File
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            with full_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except OSError as e:
            raise HTTPException(status_code=500, detail=f"Errore scrittura disco: {e}")

        # 4. Update DB
        # Calculate relative path string
        # We assume self.base_path is the root, so we store everything after it
        relative_path_str = str(full_path.relative_to(self.base_path))

        db_archivio= None
        if not is_transactional:
            db_archivio = db.query(DocumentoArchivio).filter(
                DocumentoArchivio.ragione_sociale_id == ragione_sociale_id,
                DocumentoArchivio.documento_id == documento_id
            ).first()

        if db_archivio:
            db_archivio.file_path = relative_path_str
            db_archivio.anno = anno
            db_archivio.archivio = True
            db_archivio.signed = signed
            db_archivio.sent = sent
            db_archivio.updated_at = datetime.now()
        else:
            db_archivio = DocumentoArchivio(
                ragione_sociale_id=ragione_sociale_id,
                documento_id=documento_id,
                anno=anno,
                file_path=relative_path_str,
                archivio=True,
                signed=signed,
                sent=sent
            )
            db.add(db_archivio)

        if is_transactional and linked_ids and len(linked_ids) > 0:
            preventivi_to_link = db.query(Preventivo).filter(Preventivo.id.in_(linked_ids)).all()

            if preventivi_to_link:
                db_archivio.preventivi = preventivi_to_link
            

        try:
            db.commit()
            db.refresh(db_archivio)
            return db_archivio
        except Exception as e:
            db.rollback()
            if full_path.exists():
                os.remove(full_path)
            raise HTTPException(status_code=500, detail=f"Errore DB: {e}")

    def view_document(self, db: Session, archive_id: str):
        archive = db.query(DocumentoArchivio).filter(DocumentoArchivio.id == archive_id).first()

        if not archive:
            raise HTTPException(status_code=404, detail="Documento non trovato")

        full_path = self.base_path / archive.file_path
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File fisico non trovato")

        media_type, _ = mimetypes.guess_type(full_path)
        return FileResponse(
            path=full_path,
            filename=os.path.basename(full_path),
            media_type=media_type or 'application/octet-stream',
            content_disposition_type="inline"
        )

    def delete_document(self, db: Session, archive_id: str):
        archive = db.query(DocumentoArchivio).filter(DocumentoArchivio.id == archive_id).first()

        if not archive: raise HTTPException(status_code=404, detail="Documento non trovato")

        self._delete_physical_and_db(db, archive)       
        return {"stato": "deleted document"}
    
    def delete_document_group(self, db: Session, ragione_sociale_id: str, documento_id: str):
        """
        Deletes ALL archives for a specific document type (e.g., ALL 'Conferma Ordine' files).
        """
        archives = db.query(DocumentoArchivio).filter(
            DocumentoArchivio.ragione_sociale_id == ragione_sociale_id,
            DocumentoArchivio.documento_id == documento_id
        ).all()

        if not archives:
            raise HTTPException(status_code=404, detail="Nessun documento trovato per questa tipologia")

        count = 0
        for archive in archives:
            self._delete_physical_and_db(db, archive)
            count += 1
        
        return {"stato": "deleted_group", "count": count}

    def _delete_physical_and_db(self, db: Session, archive: DocumentoArchivio):
        """Helper to ensure clean cleanup"""
        full_path = self.base_path / archive.file_path
        
        # 1. Delete DB Record
        db.delete(archive)
        db.commit() # Commit immediately to ensure DB consistency

        # 2. Delete Physical File
        if full_path.exists():
            try:
                os.remove(full_path)
            except OSError:
                print(f"Warning: Could not delete file {full_path}")