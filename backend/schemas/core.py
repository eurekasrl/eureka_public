from uuid import UUID

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

from schemas.utils import ItalianDate


class ComuneBase(BaseModel):
    codice_regione: int
    codice_unita: int
    codice_provincia: int
    progressivo_comune: int
    codice_comune: int
    nome: str
    codice_ripartizione_geografica: int
    ripartizione_geografica: str
    denominazione_regione: str
    denominazione_unita: str
    tipologia_unita: int
    provincia_short: str
    codice_catastale: str
    codice_nuts3: str
    cap: str

class ComuneCreate(ComuneBase):
    pass

class Comune(ComuneBase):
    codice_comune: int
    model_config = {"from_attributes": True}

class PersonaFisicaBase(BaseModel):
    nome: str
    cf: str
    codice_comune: Optional[int] = None
    indirizzo: Optional[str] = None
    sesso: Optional[str] = None
    cell: Optional[str] = None
    email: Optional[EmailStr] = None
    pec: Optional[EmailStr] = None
    data_di_nascita: Optional[ItalianDate] = None
    codice_comune_di_nascita: Optional[int] = None

class PersonaFisicaCreate(PersonaFisicaBase):
    pass

class PersonaFisica(PersonaFisicaBase):
    cf: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    comune: Optional[Comune] = None

    model_config = {"from_attributes": True}

class CaaColdirettiBase(BaseModel):
    nome: str
    email: Optional[EmailStr] = None
    cell: Optional[str] = None
    comune_id: Optional[str] = None

class CaaColdirettiCreate(CaaColdirettiBase):
    pass

class CaaColdiretti(CaaColdirettiBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class GruppoBase(BaseModel):
    nome: str
    referente_cf: Optional[str] = None

class GruppoCreate(GruppoBase):
    pass

class Gruppo(GruppoBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    referente: Optional[PersonaFisica] = None

    model_config = {"from_attributes": True}

class RamoBase(BaseModel):
    ramo: str
    numero: int
    nome: str
    dettaglio: str

class RamoCreate(RamoBase):
    pass

class Ramo(RamoBase):
    id: UUID
    ramo: str
    numero: int
    nome: str
    dettaglio: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class CompagniaBase(BaseModel):
    short_nome: str
    full_nome: str
    piva: str
    email: EmailStr
    pec: Optional[EmailStr] = None
    cell: str
    indirizzo: str
    codice_comune: int

class CompagniaCreate(CompagniaBase):
    pass

class Compagnia(CompagniaBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class IntermediarioBase(BaseModel):
    short_nome: str
    full_nome: str
    piva: str
    email: EmailStr
    pec: Optional[EmailStr] = None
    cell: str
    indirizzo: str
    codice_comune: int

class IntermediarioCreate(IntermediarioBase):
    pass

class Intermediario(IntermediarioBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class CondifesaBase(BaseModel):
    nome: str
    email: Optional[EmailStr] = None
    cell: Optional[str] = None

class CondifesaCreate(CondifesaBase):
    pass    

class Condifesa(CondifesaBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class RelazioneRciBase(BaseModel):
    ramo_id: Optional[UUID] = None
    compagnia_id: Optional[UUID] = None
    intermediario_id: Optional[UUID] = None
    active: Optional[bool] = True

class RelazioneRciCreate(RelazioneRciBase):
    pass

class RelazioneRci(RelazioneRciBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    ramo: Optional[Ramo]
    intermediario: Optional[Intermediario]
    compagnia: Optional[Compagnia]

    model_config = {"from_attributes": True}

# --- Documento Schemas ---
class DocumentoBase(BaseModel):
    ramo_id: Optional[UUID] = None
    compagnia_id: Optional[UUID] = None
    intermediario_id: Optional[UUID] = None
    codice_ministeriale: Optional[str] = None
    nome: Optional[str] = None
    sigla: Optional[str] = None
    signed: Optional[bool] = False
    personale: Optional[bool] = False
    mandatory: Optional[bool] = False
    entity: Optional[bool] = False
    lifecycle_id: Optional[UUID] = None

class DocumentoCreate(DocumentoBase):
    pass

class Documento(DocumentoBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class LifecycleBase(BaseModel):
    sale_reference: Optional[str] = None
    stato: Optional[str] = None

class LifecycleCreate(LifecycleBase):
    pass

class Lifecycle(LifecycleBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}



from schemas.sale import Preventivo


class RagioneSocialeBase(BaseModel):
    nome: str
    CUAA: str
    piva: str
    indirizzo: Optional[str] = None
    IBAN: Optional[str] = None
    email: Optional[EmailStr] = None
    pec: Optional[EmailStr] = None
    responsabile_legale_id: Optional[str] = None
    gruppo_id: Optional[str] = None
    comune_id: Optional[str] = None
    caa_coldiretti_id: Optional[str] = None

class RagioneSocialeCreate(RagioneSocialeBase):
    pass

class RagioneSociale(RagioneSocialeBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    responsabile_legale: Optional[PersonaFisica] = None
    gruppo: Optional[Gruppo] = None
    comune: Optional[Comune] = None
    caa_coldiretti: Optional[CaaColdiretti] = None

    preventivi: List[Preventivo] = []

    model_config = {"from_attributes": True}

class BigGruppo(Gruppo):
    ragione_sociale: List[RagioneSociale] = []
