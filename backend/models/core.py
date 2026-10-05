import uuid
from sqlalchemy import Column, String, Date, Boolean, Integer, ForeignKey, DateTime, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.db import Base


class Comune(Base):
    __tablename__ = "comune"
    __table_args__ = {"schema": "core"}
    codice_regione = Column(Integer)
    codice_unita = Column(Integer)
    codice_provincia = Column(Integer)
    progressivo_comune = Column(Integer)
    codice_comune = Column(Integer, primary_key = True)
    nome = Column(String(255), nullable=False)
    codice_ripartizione_geografica = Column(Integer)
    ripartizione_geografica = Column(String(50))
    denominazione_regione = Column(String(50))
    denominazione_unita = Column(String(50))
    tipologia_unita = Column(Integer)
    provincia_short =  Column(String(2))
    codice_catastale = Column(String(8))
    codice_nuts3 = Column(String(10))
    cap = Column(String(5))

    persone_fisiche_residenza = relationship("PersonaFisica", back_populates="comune_residenza", foreign_keys='PersonaFisica.codice_comune')
    persone_fisiche_nascita = relationship("PersonaFisica", back_populates="comune_nascita", foreign_keys='PersonaFisica.codice_comune_di_nascita')
    ragione_sociale = relationship("RagioneSociale", back_populates="comune")
    caa_coldiretti_sedi = relationship("CaaColdiretti", back_populates="comune")
    compagnie = relationship("Compagnia", back_populates="comune")
    intermediari = relationship("Intermediario", back_populates="comune")
    piano_utilizzo = relationship("PianoUtilizzo", back_populates="comune")
    piano_utilizzo_dettagliato = relationship("PianoUtilizzoDettagliato", back_populates="comune")
    tassi = relationship("Tassi", back_populates="comune")

class PersonaFisica(Base):
    __tablename__ = "persona_fisica"
    __table_args__ = {"schema": "core"}
    nome = Column(String(255), nullable=False)
    cf = Column(String(16), primary_key = True)
    codice_comune = Column(Integer, ForeignKey("core.comune.codice_comune"))
    indirizzo = Column(String(255))
    sesso = Column(String(1))
    cell = Column(String(16))
    email = Column(String(255))
    pec = Column(String(255))
    data_di_nascita = Column (Date)
    codice_comune_di_nascita = Column(Integer, ForeignKey("core.comune.codice_comune"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    comune_residenza = relationship("Comune", back_populates="persone_fisiche_residenza", foreign_keys=[codice_comune])
    comune_nascita = relationship("Comune", back_populates="persone_fisiche_nascita", foreign_keys=[codice_comune_di_nascita])
    ragione_sociale = relationship("RagioneSociale", back_populates="responsabile_legale")
    referente_gruppo = relationship("Gruppo", back_populates="referente")
    produttori = relationship("Produttore", back_populates="persona_fisica")

class CaaColdiretti(Base):
    __tablename__ = "caa_coldiretti"
    __table_args__ = {"schema": "core"}
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(255), nullable=False)
    email = Column(String(255))
    cell = Column(String(16))
    codice_comune = Column(Integer, ForeignKey("core.comune.codice_comune"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    comune = relationship("Comune", back_populates="caa_coldiretti_sedi")
    ragione_sociale = relationship("RagioneSociale", back_populates="caa_coldiretti")

class Gruppo(Base):
    __tablename__ = "gruppo"
    __table_args__ = {"schema": "core"}
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(255), nullable=False)
    referente_cf = Column(String(16), ForeignKey("core.persona_fisica.cf"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    referente = relationship("PersonaFisica", back_populates="referente_gruppo")
    ragione_sociale = relationship("RagioneSociale", back_populates="gruppo")

class RagioneSociale(Base):
    __tablename__ = "ragione_sociale"
    __table_args__ = {"schema": "core"}
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(255), nullable=False)
    responsabile_legale_cf = Column(String(16), ForeignKey("core.persona_fisica.cf"))
    CUAA = Column(String(16), unique=True, nullable=False)
    piva = Column(String(16), unique=True, nullable=False)
    gruppo_id = Column(String(36), ForeignKey("core.gruppo.id"))
    codice_comune = Column(Integer, ForeignKey("core.comune.codice_comune"))
    indirizzo = Column(String(255))
    IBAN = Column(String(50))
    caa_coldiretti_id = Column(String(36), ForeignKey("core.caa_coldiretti.id"))
    email = Column(String(255))
    pec = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    responsabile_legale = relationship("PersonaFisica", back_populates="ragione_sociale")
    gruppo = relationship("Gruppo", back_populates="ragione_sociale")
    comune = relationship("Comune", back_populates="ragione_sociale")
    caa_coldiretti = relationship("CaaColdiretti", back_populates="ragione_sociale")
    preventivi = relationship("Preventivo", back_populates="ragione_sociale")
    piano_utilizzo = relationship("PianoUtilizzo", back_populates="ragione_sociale")
    piano_utilizzo_dettagliato = relationship("PianoUtilizzoDettagliato", back_populates="ragione_sociale")
    soci = relationship("Socio", back_populates="ragione_sociale")
    documenti_archivi = relationship("DocumentoArchivio", back_populates="ragione_sociale")
    polizze = relationship("Polizza", back_populates="ragione_sociale")

class Ramo(Base):
    __tablename__ = "ramo"
    __table_args__ = {"schema": "core"}
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ramo = Column(String(255), nullable=False)
    numero = Column(Integer())
    nome = Column(String(255), nullable=False)
    dettaglio = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    preventivi = relationship("Preventivo", back_populates="ramo") 
    produttori = relationship("Produttore", back_populates="ramo")
    relazioni_rci = relationship("RelazioneRci", back_populates="ramo")
    documenti = relationship("Documento", back_populates="ramo")
    polizze = relationship("Polizza", back_populates="ramo")

class Compagnia(Base):
    __tablename__ = "compagnia"
    __table_args__ = {"schema": "core"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    short_nome = Column(String(100), nullable=False)
    full_nome = Column(String(255), nullable=False)
    piva = Column(String(16), nullable=False)
    email = Column(String(255), nullable=False)
    pec = Column(String(255))
    cell = Column(String(16), nullable=False)
    indirizzo = Column(String(255), nullable=False)
    codice_comune = Column(Integer, ForeignKey("core.comune.codice_comune"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    comune = relationship("Comune", back_populates="compagnie")
    preventivi = relationship("Preventivo", back_populates="compagnia")
    tassi = relationship("Tassi", back_populates="compagnia")
    relazioni_rci = relationship("RelazioneRci", back_populates="compagnia")
    documenti = relationship("Documento", back_populates="compagnia")
    polizze = relationship("Polizza", back_populates="compagnia")

class Intermediario(Base):
    __tablename__ = "intermediario"
    __table_args__ = {"schema": "core"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    short_nome = Column(String(100), nullable=False)
    full_nome = Column(String(255), nullable=False)
    piva = Column(String(16), nullable=False)
    email = Column(String(255), nullable=False)
    pec = Column(String(255))
    cell = Column(String(16), nullable=False)
    indirizzo = Column(String(255), nullable=False)
    codice_comune = Column(Integer, ForeignKey("core.comune.codice_comune"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    comune = relationship("Comune", back_populates="intermediari")
    preventivi = relationship("Preventivo", back_populates="intermediario")
    tassi = relationship("Tassi", back_populates="intermediario")
    relazioni_rci = relationship("RelazioneRci", back_populates="intermediario")
    documenti = relationship("Documento", back_populates="intermediario")
    polizze = relationship("Polizza", back_populates="intermediario")

class Condifesa(Base):
    __tablename__ = "condifesa"
    __table_args__ = {"schema": "core"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(255), nullable=False)
    email = Column(String(255))
    cell = Column(String(16))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    prezzi = relationship("Prezzi", back_populates="condifesa")
    piano_utilizzo = relationship("PianoUtilizzo", back_populates="condifesa")
    piano_utilizzo_dettagliato = relationship("PianoUtilizzoDettagliato", back_populates="condifesa")
    prodotto = relationship("Prodotto", back_populates="condifesa")
    soci = relationship("Socio", back_populates="condifesa")

class RelazioneRci(Base):
    __tablename__ = "relazione_rci"
    __table_args__ = {"schema": "core"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ramo_id = Column(String(36), ForeignKey("core.ramo.id"))
    compagnia_id = Column(String(36), ForeignKey("core.compagnia.id"))
    intermediario_id = Column(String(36), ForeignKey("core.intermediario.id"))
    active = Column(Boolean, default=text("1"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # Relationships
    ramo = relationship("Ramo", back_populates="relazioni_rci")
    compagnia = relationship("Compagnia", back_populates="relazioni_rci")
    intermediario = relationship("Intermediario", back_populates="relazioni_rci")

class Documento(Base):
    __tablename__ = "documento"
    __table_args__ = {"schema": "core"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ramo_id = Column(String(36), ForeignKey("core.ramo.id"))
    compagnia_id = Column(String(36), ForeignKey("core.compagnia.id"))
    intermediario_id = Column(String(36), ForeignKey("core.intermediario.id"))
    codice_ministeriale = Column(String(4), ForeignKey("grandine.prodotto.codice_ministeriale"))
    nome = Column(String(255))
    sigla = Column(String(50))
    signed = Column(Boolean, default=text("0"))
    personale = Column(Boolean, default=text("0"))
    mandatory = Column(Boolean, default=text('0'))
    entity = Column(Boolean, default = text("0"))
    lifecycle_id = Column(Integer, ForeignKey("core.lifecycle.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # Relationships
    ramo = relationship("Ramo", back_populates="documenti")
    compagnia = relationship("Compagnia", back_populates="documenti")
    intermediario = relationship("Intermediario", back_populates="documenti")
    prodotto = relationship("Prodotto", back_populates="documenti")
    documenti_archivi = relationship("DocumentoArchivio", back_populates="documenti")
    lifecycle = relationship("Lifecycle", back_populates="documenti")

class Lifecycle(Base):
    __tablename__= "lifecycle"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_reference = Column(String(20))
    stato = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    preventivi = relationship("Preventivo", back_populates="lifecycle")
    documenti = relationship("Documento", back_populates="lifecycle")
    polizze = relationship("Polizza", back_populates="lifecycle")