import uuid

from sqlalchemy import Column, String, Date, Boolean, Integer, ForeignKey, DateTime, DECIMAL, Text, text, event
from sqlalchemy.orm import relationship, Session, object_session
from sqlalchemy.sql import func

from db.db import Base
from models.sale import Preventivo
from models.core import Lifecycle

# grandine.piano_utilizzo
class PianoUtilizzo(Base):
    __tablename__ = "piano_utilizzo"
    __table_args__ = {"schema": "grandine"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ragione_sociale_id = Column(String(36), ForeignKey("core.ragione_sociale.id"))
    condifesa_id = Column(String(36), ForeignKey("core.condifesa.id"))
    anno = Column(Integer)
    tipo = Column(String(50))
    is_corrente = Column(Boolean, default=True, server_default=text("1"))
    codice_comune = Column(Integer, ForeignKey("core.comune.codice_comune"))
    prodotto_id = Column(String(36), ForeignKey("grandine.prodotto.id"))
    serra = Column(Boolean, default=False, server_default=text("0"))
    bio = Column(Boolean, default=False, server_default=text("0"))
    secondo_raccolto = Column(Boolean, default=False, server_default=text("0"))
    superficie = Column(Integer)
    note = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # Define the relationship with ragione_sociale table
    ragione_sociale = relationship("RagioneSociale", back_populates="piano_utilizzo")
    comune = relationship("Comune", back_populates="piano_utilizzo")
    prodotto = relationship("Prodotto", back_populates="piano_utilizzo")
    condifesa = relationship("Condifesa", back_populates="piano_utilizzo")
    preventivo_grandine = relationship("PreventivoGrandine", back_populates="piano_utilizzo")

# grandine.piano_utilizzo_dettagliato
class PianoUtilizzoDettagliato(Base):
    __tablename__ = "piano_utilizzo_dettagliato"
    __table_args__ = {"schema": "grandine"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ragione_sociale_id = Column(String(36), ForeignKey("core.ragione_sociale.id"))
    condifesa_id = Column(String(36), ForeignKey("core.condifesa.id"))
    anno = Column(Integer)
    is_corrente = Column(Boolean, default=True, server_default=text("1"))
    codice_comune = Column(Integer, ForeignKey("core.comune.codice_comune"))
    prodotto_id = Column(String(36), ForeignKey("grandine.prodotto.id"))
    serra = Column(Boolean, default=False, server_default=text("0"))
    bio = Column(Boolean, default=False, server_default=text("0"))
    secondo_raccolto = Column(Boolean, default=False, server_default=text("0"))
    foglio = Column(Integer)
    particella = Column(Integer)
    superficie = Column(Integer)
    data_semina_trapianto = Column(Date, nullable=True)
    note = Column(Text, nullable = True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # Define the relationship with ragione_sociale table
    ragione_sociale = relationship("RagioneSociale", back_populates="piano_utilizzo_dettagliato")
    comune = relationship("Comune", back_populates="piano_utilizzo_dettagliato")
    prodotto = relationship("Prodotto", back_populates="piano_utilizzo_dettagliato")
    condifesa = relationship("Condifesa", back_populates="piano_utilizzo_dettagliato")
    partita = relationship("Partita", back_populates = "piano_utilizzo_dettagliato")

#grandine.partita
class Partita(Base):
    __tablename__ = "partita"
    __table_args__ = {"schema": "grandine"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    piano_utilizzo_dettagliato_id = Column(String(36), ForeignKey("grandine.piano_utilizzo_dettagliato.id"))
    numero = Column(Integer)
    foglio = Column(String(6))
    particella = Column(String(6))
    superficie = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # Define the relationship with ragione_sociale table
    piano_utilizzo_dettagliato = relationship("PianoUtilizzoDettagliato", back_populates="partita")
    polizza_grandine = relationship("PolizzaGrandine", back_populates="partita")

# grandine.prodotto
class Prodotto(Base):
    __tablename__ = "prodotto"
    __table_args__ = {"schema": "grandine"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    condifesa_id = Column(String(36), ForeignKey("core.condifesa.id"))
    gruppo = Column(String(100))
    nome = Column(String(255))
    dettaglio = Column(String(255))
    codice_ministeriale = Column(String(4))
    codice_dettaglio_ministeriale = Column(String(4))
    codice_dettaglio_condifesa = Column(String(5))
    codice_prodotto = Column(String(4))
    dettaglio_avepa = Column(String(100))
    codice_avepa = Column(Integer)
    codice_avepa_dettagliato = Column(String(19))
    codice_gis = Column(String(10))  
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    
    prezzi = relationship("Prezzi", back_populates="prodotto")
    piano_utilizzo = relationship("PianoUtilizzo", back_populates="prodotto")
    piano_utilizzo_dettagliato = relationship("PianoUtilizzoDettagliato", back_populates="prodotto")
    condifesa = relationship("Condifesa", back_populates="prodotto")
    documenti = relationship("Documento", back_populates="prodotto")

# grandine.avepa
class Avepa(Base):
    __tablename__ = "avepa"
    __table_args__ = {"schema": "grandine"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    occupazione = Column(String(255))
    codice_occupazione = Column(String(3))
    destinazione = Column(String(255))
    codice_destinazione = Column(String(3))
    uso = Column(String(255))
    codice_uso = Column(String(3))
    dettaglio = Column(String(255))
    codice_dettaglio = Column(String(3))
    codice_ministeriale = Column(String(3))  
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

# grandine.prezzi
class Prezzi(Base):
    __tablename__ = "prezzi"
    __table_args__ = {"schema": "grandine"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    anno = Column(Integer)
    condifesa_id = Column(String(36), ForeignKey("core.condifesa.id"))
    prodotto_id = Column(String(36), ForeignKey("grandine.prodotto.id"))
    area = Column(String(50))
    sv = Column(DECIMAL(10, 2))
    resa_max = Column(DECIMAL(10, 2))
    sv_bio = Column(DECIMAL(10, 2))
    fascia = Column(String(1))
    valore = Column(DECIMAL(10, 2))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # Define relationships
    condifesa = relationship("Condifesa", back_populates="prezzi")
    prodotto = relationship("Prodotto", back_populates="prezzi")
    preventivo_grandine = relationship("PreventivoGrandine", back_populates="prezzi")

#grandine.tassi
class Tassi(Base):
    __tablename__ = "tassi"
    __table_args__ = {"schema": "grandine"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    anno = Column(Integer)
    intermediario_id = Column(String(36), ForeignKey("core.intermediario.id"))
    compagnia_id = Column(String(36), ForeignKey("core.compagnia.id"))
    codice_comune = Column(Integer, ForeignKey("core.comune.codice_comune"))
    codice_ministeriale = Column(String(4))
    tabella_conversione = Column(String(2))
    tipo = Column(String(50))
    garanzia = Column(String(50))
    fr = Column(Integer)
    tasso  = Column(String(3))
    valore = Column(DECIMAL(4, 2))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    intermediario = relationship("Intermediario", back_populates="tassi")
    compagnia = relationship("Compagnia", back_populates="tassi")
    comune = relationship("Comune", back_populates="tassi")

# grandine.preventivo
class PreventivoGrandine(Base):
    __tablename__ = "preventivo"
    __table_args__ = {"schema": "grandine"}

    sale_preventivo_id = Column(String(36), ForeignKey("sale.preventivo.id"), primary_key=True, )
    piano_utilizzo_id = Column(String(36), ForeignKey("grandine.piano_utilizzo.id"), nullable=False)
    prezzo_id = Column(String(36), ForeignKey("grandine.prezzi.id"))

    # Boolean flags
    contribuzione = Column(Boolean, default=True, server_default=text("1"))
    condifesa = Column(Boolean, default=True, server_default=text("1"))
    caa_coldiretti = Column(Boolean, default=True, server_default=text("1"))

    # COVERAGES
    GR_AG_id = Column(String(36))
    GR_NAG_id = Column(String(36))
    VF_AG_id = Column(String(36))
    VF_NAG_id = Column(String(36))
    EP_AG_id = Column(String(36))
    EP_NAG_id = Column(String(36))
    EP_CAT_AG_id = Column(String(36))
    EP_CAT_NAG_id = Column(String(36))
    neve_AG_id = Column(String(36))
    neve_NAG_id = Column(String(36))
    alluvione_AG_id = Column(String(36))
    gelo_brina_AG_id = Column(String(36))
    siccita_AG_id = Column(String(36))
    colpo_sole_vento_caldo_AG_id = Column(String(36))
    colpo_sole_vento_caldo_NAG_id = Column(String(36))
    colpo_sole_vento_caldo_CAT_AG_id = Column(String(36))
    colpo_sole_vento_caldo_CAT_NAG_id = Column(String(36))
    sbalzo_termico_onda_calore_AG_id = Column(String(36))
    sbalzo_termico_onda_calore_NAG_id = Column(String(36))
    sbalzo_termico_onda_calore_CAT_AG_id = Column(String(36))
    sbalzo_termico_onda_calore_CAT_NAG_id = Column(String(36))

    # Pricing fields
    ag = Column(DECIMAL(4, 2))
    nag = Column(DECIMAL(4, 2))
    lordo = Column(DECIMAL(4, 2))
    resa_cliente = Column(Integer)
    valore_assicurato = Column(Integer)
    premio_lordo = Column(DECIMAL(12, 2))
    premio_netto = Column(DECIMAL(12, 2))
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # Relationships
    preventivo = relationship("Preventivo", back_populates="preventivo_grandine")
    piano_utilizzo = relationship("PianoUtilizzo", back_populates="preventivo_grandine")
    prezzi = relationship("Prezzi", back_populates="preventivo_grandine")

def sync_grandine_to_general(session, flush_context, instances):
    # Check every object that is new or dirty in this flush
    for obj in session.new.union(session.dirty):
        if isinstance(obj, PreventivoGrandine):

            # Load parent manually (relationship may not be loaded yet)
            preventivo = session.query(Preventivo).get(obj.sale_preventivo_id)
            if not preventivo:
                continue

            # Update premio_lordo
            if obj.premio_lordo is not None:
                preventivo.premio_lordo = obj.premio_lordo

            # Update stato
            if obj.premio_lordo and obj.premio_lordo > 0:
                preventivo.lifecycle_id = session.query(Lifecycle).filter(Lifecycle.stato == "creato").first().id

event.listen(Session, "before_flush", sync_grandine_to_general)

# grandine.preventivo
class PolizzaGrandine(Base):
    __tablename__ = "polizza"
    __table_args__ = {"schema": "grandine"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sale_polizza_id = Column(String(36), ForeignKey("sale.polizza.id"), primary_key=True, )
    partita_id = Column(String(36), ForeignKey("grandine.partita.id"), nullable=False)
    ag = Column(Boolean, default=True, server_default=text("1"))
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # Relationships
    polizza = relationship("Polizza", back_populates="polizza_grandine")
    partita = relationship("Partita", back_populates="polizza_grandine")

#grandine.socio
class Socio(Base):
    __tablename__ = "socio"
    __table_args__ = {"schema": "grandine"}

    id = Column(String(36), primary_key=True)
    ragione_sociale_id = Column(String(36), ForeignKey("core.ragione_sociale.id"))
    condifesa_id = Column(String(36), ForeignKey("core.condifesa.id"))
    codice_socio = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    ragione_sociale = relationship("RagioneSociale", back_populates="soci")
    condifesa = relationship("Condifesa", back_populates="soci")