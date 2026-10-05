from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from schemas.utils import ItalianDate
from schemas.sale import Preventivo, Polizza
from schemas.core import Comune


# grandine.prodotto
class ProdottoBase(BaseModel):
    condifesa_id: UUID
    gruppo: Optional[str]
    nome: str
    dettaglio: str
    codice_ministeriale: str
    codice_dettaglio_ministeriale: str
    codice_dettaglio_condifesa: str
    codice_prodotto: str
    dettaglio_avepa: Optional[str] = None
    codice_avepa: Optional[int] = None
    codice_avepa_dettagliato: Optional[str] = None
    codice_gis: str

class ProdottoCreate(ProdottoBase):
    pass

class Prodotto(ProdottoBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

#grandine.avepa
class AvepaBase(BaseModel):
    occupazione: str
    codice_occupazione:str
    destinazione: str
    codice_destinazione:str
    uso: str
    codice_uso:str
    dettaglio: str
    codice_dettaglio:str
    codice_ministeriale: str

class AvepaCreate(AvepaBase):
    pass

class Avepa(AvepaBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# grandine.prezzi
class PrezziBase(BaseModel):
    anno: int
    condifesa_id: UUID
    prodotto_id: UUID
    area: str
    sv: float
    resa_max: float
    sv_bio: float
    fascia: str
    valore: float

class PrezziCreate(PrezziBase):
    pass

class Prezzi(PrezziBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# grandine.tassi
class TassiBase(BaseModel):
    anno: int
    intermediario_id: Optional[UUID] = None
    compagnia_id: Optional[UUID] = None
    codice_comune: Optional[int] = None
    codice_ministeriale: Optional[str] = None
    tabella_conversione: Optional[str] = None
    tipo: Optional[str] = None
    garanzia: Optional[str] = None
    fr: Optional[int] = None
    tasso: Optional[str] = None
    valore: float

class TassiCreate(TassiBase):
    pass

class Tassi(TassiBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# grandine.preventivo_grandine
class PreventivoGrandineBase(BaseModel):
    piano_utilizzo_id: UUID
    prezzo_id: Optional[UUID] = None

    # Boolean flags
    contribuzione: Optional[bool] = None
    condifesa: Optional[bool] = None
    caa_coldiretti: Optional[bool] = None

    # COVERAGES – now *_id references
    GR_AG_id: Optional[UUID] = None
    GR_NAG_id: Optional[UUID] = None
    VF_AG_id: Optional[UUID] = None
    VF_NAG_id: Optional[UUID] = None
    EP_AG_id: Optional[UUID] = None
    EP_NAG_id: Optional[UUID] = None
    EP_CAT_AG_id: Optional[UUID] = None
    EP_CAT_NAG_id: Optional[UUID] = None
    neve_AG_id: Optional[UUID] = None
    neve_NAG_id: Optional[UUID] = None
    alluvione_AG_id: Optional[UUID] = None
    gelo_brina_AG_id: Optional[UUID] = None
    siccita_AG_id: Optional[UUID] = None
    colpo_sole_vento_caldo_AG_id: Optional[UUID] = None
    colpo_sole_vento_caldo_NAG_id: Optional[UUID] = None
    colpo_sole_vento_caldo_CAT_AG_id: Optional[UUID] = None
    colpo_sole_vento_caldo_CAT_NAG_id: Optional[UUID] = None
    sbalzo_termico_onda_calore_AG_id: Optional[UUID] = None
    sbalzo_termico_onda_calore_NAG_id: Optional[UUID] = None
    sbalzo_termico_onda_calore_CAT_AG_id: Optional[UUID] = None
    sbalzo_termico_onda_calore_CAT_NAG_id: Optional[UUID] = None

    # Pricing fields
    ag: Optional[float] = None
    nag: Optional[float] = None
    lordo: Optional[float] = None
    resa_cliente: Optional[int] = None
    valore_assicurato: Optional[int] = None
    premio_lordo: Optional[float] = None
    premio_netto: Optional[float] = None

class PreventivoGrandineCreate(PreventivoGrandineBase):
    ragione_sociale_id: UUID
    ramo_id: UUID
    intermediario_id: UUID
    compagnia_id: UUID

    model_config = ConfigDict(from_attributes=True)

class PreventivoGrandine(PreventivoGrandineBase):
    sale_preventivo_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    preventivo: Optional[Preventivo] = None

    model_config = ConfigDict(from_attributes=True)
 
class PreventivoGrandinePatch(BaseModel):
    sale_preventivo_id: UUID
    piano_utilizzo_id: UUID
    prezzo_id: Optional[UUID] = None

    # Boolean flags
    contribuzione: Optional[bool] = None
    condifesa: Optional[bool] = None
    caa_coldiretti: Optional[bool] = None

    # COVERAGES – now *_id references
    GR_AG_id: Optional[UUID] = None
    GR_NAG_id: Optional[UUID] = None
    VF_AG_id: Optional[UUID] = None
    VF_NAG_id: Optional[UUID] = None
    EP_AG_id: Optional[UUID] = None
    EP_NAG_id: Optional[UUID] = None
    EP_CAT_AG_id: Optional[UUID] = None
    EP_CAT_NAG_id: Optional[UUID] = None
    neve_AG_id: Optional[UUID] = None
    neve_NAG_id: Optional[UUID] = None
    alluvione_AG_id: Optional[UUID] = None
    gelo_brina_AG_id: Optional[UUID] = None
    siccita_AG_id: Optional[UUID] = None
    colpo_sole_vento_caldo_AG_id: Optional[UUID] = None
    colpo_sole_vento_caldo_NAG_id: Optional[UUID] = None
    colpo_sole_vento_caldo_CAT_AG_id: Optional[UUID] = None
    colpo_sole_vento_caldo_CAT_NAG_id: Optional[UUID] = None
    sbalzo_termico_onda_calore_AG_id: Optional[UUID] = None
    sbalzo_termico_onda_calore_NAG_id: Optional[UUID] = None
    sbalzo_termico_onda_calore_CAT_AG_id: Optional[UUID] = None
    sbalzo_termico_onda_calore_CAT_NAG_id: Optional[UUID] = None

    # Pricing fields
    ag: Optional[float] = None
    nag: Optional[float] = None
    lordo: Optional[float] = None
    resa_cliente: Optional[int] = None
    valore_assicurato: Optional[int] = None
    premio_lordo: Optional[float] = None
    premio_netto: Optional[float] = None

# grandine.polizza_grandine
class PolizzaGrandineBase(BaseModel):
    sale_polizza_id: UUID
    partita_id: UUID
    ag: Optional[bool] = None

class PolizzaGrandineCreate(PolizzaGrandineBase):
    pass

class PolizzaGrandine(PolizzaGrandineBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    polizza: Optional[Polizza] = None

    model_config = ConfigDict(from_attributes=True)
 
class PolizzaGrandinePatch(BaseModel):
    sale_polizza_id: UUID
    partita_id: UUID
    ag: Optional[bool] = None

# grandine.socio
class SocioBase(BaseModel):
    ragione_sociale_id: Optional[UUID] = None
    condifesa_id: Optional[UUID] = None
    codice_socio: Optional[str] = None

class SocioCreate(SocioBase):
    pass

class Socio(SocioBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# grandine.piano_utilizzo
class PianoUtilizzoBase(BaseModel):
    ragione_sociale_id: UUID
    condifesa_id: UUID
    anno: int
    tipo: Optional[str] = None
    is_corrente: bool = True
    codice_comune: Optional[int] = None
    prodotto_id: UUID
    serra: bool = False
    bio: bool = False
    secondo_raccolto: bool = False
    superficie: Optional[int] = None
    note: Optional[str] = None

class PianoUtilizzoCreate(PianoUtilizzoBase):
    pass

class PianoUtilizzo(PianoUtilizzoBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    comune: Optional[Comune] = None
    prodotto: Optional[Prodotto] = None
    model_config = ConfigDict(from_attributes=True)

class PianoUtilizzoRow(BaseModel):
    codice_comune: int
    prodotto_id: str
    superficie: int
    foglio: Optional[int] = None
    particella: Optional[int] = None
    data_semina_trapianto: Optional[ItalianDate] = None
    serra: bool = False
    bio: bool = False
    secondo_raccolto: bool = False
    note: Optional[str] = None

class PianoUtilizzoBulkPayload(BaseModel):
    ragione_sociale_id: str
    condifesa_id: str
    anno: int
    secondo_raccolto: bool
    rows: List[PianoUtilizzoRow]

# grandine.piano_utilizzo_dettagliato
class PianoUtilizzoDettagliatoBase(BaseModel):
    ragione_sociale_id: UUID
    condifesa_id: UUID
    anno: int
    is_corrente: bool = True
    codice_comune: Optional[int] = None
    prodotto_id: UUID
    serra: bool = False
    bio: bool = False
    secondo_raccolto: bool = False
    foglio: int
    particella: int
    superficie: Optional[int] = None
    data_semina_trapianto: Optional[ItalianDate] = None
    note: Optional[str] = None

class PianoUtilizzoDettagliatoCreate(PianoUtilizzoDettagliatoBase):
    pass

class PianoUtilizzoDettagliato(PianoUtilizzoDettagliatoBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    comune: Optional[Comune] = None
    prodotto: Optional[Prodotto] = None
    model_config = ConfigDict(from_attributes=True)

class DashboardComparisonRow(BaseModel):
    condifesa_id: str
    anno: int
    codice_comune: int
    prodotto_id: str
    serra: bool
    bio: bool
    secondo_raccolto: bool
    
    # Aggregated Values
    sup_riepilogo: int
    sup_dettaglio: int
    diff: int

    condifesa_nome: str
    comune_nome: str
    prodotto_nome:str
    prodotto_dettaglio:str
    
    class Config:
        from_attributes = True

class DettaglioRow(BaseModel):
    prodotto_id: str
    data_semina_trapianto: Optional[ItalianDate] = None
    comune: str
    foglio: int
    particella: int
    superficie: int
    serra: bool = False
    bio: bool = False

class PianoBulkCreate(BaseModel):
    condifesa_id: str
    anno: int
    secondo_raccolto: bool
    rows: List[DettaglioRow] # Validates the list automatically

class PianoCreateResponse(BaseModel):
    message: str
    rows_processed: int


# grandine.partita
class PartitaBase(BaseModel):
    piano_utilizzo_dettagliato_id: UUID
    numero: int
    foglio: str
    particella: str
    superficie: int

class PartitaCreate(PartitaBase):
    pass

class Partita(PartitaBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    piano_utilizzo_dettagliato: Optional[PianoUtilizzoDettagliato] = None

    model_config = ConfigDict(from_attributes=True)

class PartitaDraftResponse(BaseModel):
    pud_id: str
    condifesa_id: str
    prodotto_id: str
    anno: int
    comune: str
    prodotto: str
    foglio_orig: int
    particella_orig: int

    # Calculated Fields
    numero_partita: int
    foglio_assegnato: str
    particella_assegnata: str
    superficie_assegnata: int
    is_split: bool

class PartiteCheckResponse(BaseModel):
    total_superficie_pud: int
    total_superficie_partite: int
    is_balanced: bool
    payload: List[PartitaDraftResponse] | List[Partita]= []