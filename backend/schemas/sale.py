from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from schemas.core import Ramo
from schemas.utils import ItalianDate


class PreventivoBase(BaseModel):
    ragione_sociale_id: UUID
    ramo_id: UUID
    intermediario_id: UUID
    compagnia_id: UUID
    premio_lordo: Decimal
    lifecycle_id: int

class PreventivoCreate(PreventivoBase):
    pass

class Preventivo(PreventivoBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    ramo: Optional[Ramo] = []
    stato: Optional[str] = None

    model_config = ConfigDict(from_attributes= True)

# --- Produttore Schemas ---
class ProduttoreBase(BaseModel):
    persona_fisica_cf: Optional[str] = None
    ramo_id: Optional[UUID] = None
    percentuale: Optional[Decimal] = None

class ProduttoreCreate(ProduttoreBase):
    pass

class Produttore(ProduttoreBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class DocumentoArchivioBase(BaseModel):
    id: UUID
    ragione_sociale_id: Optional[UUID] = None
    documento_id: Optional[UUID] = None
    anno: Optional[int] = None
    file_path: Optional[str] = None
    archivio: Optional[bool] = False
    signed: Optional[bool] = False
    sent: Optional[bool] = False

class DocumentoArchivioCreate(DocumentoArchivioBase):
    pass

class DocumentoArchivio(DocumentoArchivioBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class PolizzaBase(BaseModel):
    numero: str
    ragione_sociale_id: UUID
    ramo_id: UUID
    intermediario_id: UUID
    compagnia_id: UUID
    premio_lordo: Decimal
    lifecycle_id: int
    produttore_id: UUID
    preventivo_id: UUID
    start_date: Optional[ItalianDate] = None
    end_date: Optional[ItalianDate] = None

class PolizzaCreate(PolizzaBase):
    pass

class Polizza(PolizzaBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes= True)