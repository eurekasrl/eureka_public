import uuid
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, DECIMAL, text, Table, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.db import Base

documento_archivio_preventivo = Table(
    "documento_archivio_preventivo",
    Base.metadata,
    Column("documento_archivio_id", String(36), ForeignKey("sale.documento_archivio.id"), primary_key=True),
    Column("preventivo_id", String(36), ForeignKey("sale.preventivo.id"), primary_key=True),
    # Timestamps are optional in M2M tables, but if you keep them, 
    # they won't update automatically via Python unless you use the Association Object pattern.
    # For a simple link, we usually omit them or handle them via DB triggers.
    schema="sale"
)

documento_archivio_polizza = Table (
    "documento_archivio_polizza",
    Base.metadata,
    Column("documento_archivio_id", String(36), ForeignKey("sale.documento_archivio.id"), primary_key=True),
    Column("polizza_id", String(36), ForeignKey("sale.polizza.id"), primary_key=True),
    # Timestamps are optional in M2M tables, but if you keep them, 
    # they won't update automatically via Python unless you use the Association Object pattern.
    # For a simple link, we usually omit them or handle them via DB triggers.
    schema="sale"
)

class Preventivo(Base):
    __tablename__ = "preventivo"
    __table_args__ = {"schema": "sale"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ragione_sociale_id = Column(String(36), ForeignKey("core.ragione_sociale.id"), nullable=False)
    ramo_id = Column(String(36), ForeignKey("core.ramo.id"), nullable=False)
    intermediario_id = Column(String(36), ForeignKey("core.intermediario.id"), nullable=False)
    compagnia_id = Column(String(36), ForeignKey("core.compagnia.id"), nullable=False)
    premio_lordo = Column(DECIMAL(12, 2), nullable=False)
    lifecycle_id = Column(Integer, ForeignKey("core.lifecycle.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    ragione_sociale = relationship("RagioneSociale", back_populates="preventivi")
    ramo = relationship("Ramo", back_populates="preventivi")
    intermediario = relationship("Intermediario", back_populates="preventivi")
    compagnia = relationship("Compagnia", back_populates="preventivi")
    lifecycle = relationship("Lifecycle", back_populates="preventivi")
    documenti_archivi = relationship("DocumentoArchivio", secondary = documento_archivio_preventivo, back_populates= "preventivi")
    preventivo_grandine = relationship("PreventivoGrandine", back_populates="preventivo", uselist=False, cascade="all, delete-orphan")
    polizza = relationship("Polizza", back_populates="preventivo")

    def advance_lifecycle(self):
        "Increment the lifecycle state of the preventivo"
        self.lifecycle_id +=1
    
class Produttore(Base):
    __tablename__ = "produttore"
    __table_args__ = {"schema": "sale"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    persona_fisica_cf = Column(String(16), ForeignKey("core.persona_fisica.cf")) 
    ramo_id = Column(String(36), ForeignKey("core.ramo.id"))
    percentuale = Column(DECIMAL(5, 2))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # Relationships
    persona_fisica = relationship("PersonaFisica", back_populates="produttori")
    ramo = relationship("Ramo", back_populates="produttori")
    polizze = relationship("Polizza", back_populates="produttore")

class DocumentoArchivio(Base):
    __tablename__ = "documento_archivio"
    __table_args__ = {"schema": "sale"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ragione_sociale_id = Column(String(36), ForeignKey("core.ragione_sociale.id"))
    documento_id = Column(String(36), ForeignKey("core.documento.id"))
    anno = Column(Integer)
    file_path = Column(String(255), nullable=False)
    archivio = Column(Boolean, default=text("0"))
    signed = Column(Boolean, default=text("0"))
    sent = Column(Boolean, default=text("0"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

    documenti = relationship("Documento", back_populates="documenti_archivi")
    ragione_sociale = relationship("RagioneSociale", back_populates="documenti_archivi")
    preventivi = relationship("Preventivo", secondary = documento_archivio_preventivo, back_populates="documenti_archivi")
    polizze = relationship("Polizza", secondary = documento_archivio_polizza, back_populates="documenti_archivi")

class Polizza(Base):
    __tablename__ = "polizza"
    __table_args__ = {"schema": "sale"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero =Column(String(50))
    ragione_sociale_id = Column(String(36), ForeignKey("core.ragione_sociale.id"), nullable=False)
    ramo_id = Column(String(36), ForeignKey("core.ramo.id"), nullable=False)
    intermediario_id = Column(String(36), ForeignKey("core.intermediario.id"), nullable=False)
    compagnia_id = Column(String(36), ForeignKey("core.compagnia.id"), nullable=False)
    premio_lordo = Column(DECIMAL(12, 2), nullable=False)
    lifecycle_id = Column(Integer, ForeignKey("core.lifecycle.id"), nullable=False)
    produttore_id = Column(String(36), ForeignKey("sale.produttore.id"))
    preventivo_id = Column(String(36), ForeignKey("sale.preventivo.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    ragione_sociale = relationship("RagioneSociale", back_populates="polizze")
    ramo = relationship("Ramo", back_populates="polizze")
    intermediario = relationship("Intermediario", back_populates="polizze")
    compagnia = relationship("Compagnia", back_populates="polizze")
    lifecycle = relationship("Lifecycle", back_populates="polizze")
    produttore = relationship("Produttore", back_populates="polizze")
    preventivo = relationship("Preventivo", back_populates="polizza")
    documenti_archivi = relationship("DocumentoArchivio", secondary = documento_archivio_polizza, back_populates= "polizze")
    polizza_grandine = relationship("PolizzaGrandine", back_populates="polizza", uselist=False, cascade="all, delete-orphan")

    def advance_lifecycle(self):
        "Increment the lifecycle state of the preventivo"
        self.lifecycle_id +=1