# mappings.py
from pydantic_settings import BaseSettings
from schemas import core, sale, grandine

SCHEMA_MAPPING = {
    "core": {
        "comune": {
            "base": core.ComuneBase,
            "create": core.ComuneCreate,
            "read": core.Comune
        },
        "persona_fisica": {
            "base": core.PersonaFisicaBase,
            "create": core.PersonaFisicaCreate,
            "read": core.PersonaFisica
        },
        "caa_coldiretti": {
            "base": core.CaaColdirettiBase,
            "create": core.CaaColdirettiCreate,
            "read": core.CaaColdiretti
        },
        "gruppo": {
            "base": core.GruppoBase,
            "create": core.GruppoCreate,
            "read": core.Gruppo
        },
        "ramo": {
            "base": core.RamoBase,
            "create": core.RamoCreate,
            "read": core.Ramo
        },
        "compagnia": {
            "base": core.CompagniaBase,
            "create": core.CompagniaCreate,
            "read": core.Compagnia
        },
        "intermediario": {
            "base": core.IntermediarioBase,
            "create": core.IntermediarioCreate,
            "read": core.Intermediario
        },
        "condifesa": {
            "base": core.CondifesaBase,
            "create": core.CondifesaCreate,
            "read": core.Condifesa
        },
        "ragione_sociale": {
            "base": core.RagioneSocialeBase,
            "create": core.RagioneSocialeCreate,
            "read": core.RagioneSociale
        }
    },
    "sale": {
        "preventivo": {
            "base": sale.PreventivoBase,
            "create": sale.PreventivoCreate,
            "read": sale.Preventivo
        }
    },
    "grandine": {
        "piano_utilizzo": {
            "base": grandine.PianoUtilizzoBase,
            "create": grandine.PianoUtilizzoCreate,
            "read": grandine.PianoUtilizzo
        },
        "prodotto": {
            "base": grandine.ProdottoBase,
            "create": grandine.ProdottoCreate,
            "read": grandine.Prodotto
        },
        "prezzi": {
            "base": grandine.PrezziBase,
            "create": grandine.PrezziCreate,
            "read": grandine.Prezzi
        },
        "tassi": {
            "base": grandine.TassiBase,
            "create": grandine.TassiCreate,
            "read": grandine.Tassi
        },
        "preventivo_grandine": {
            "base": grandine.PreventivoGrandineBase,
            "create": grandine.PreventivoGrandineCreate,
            "read": grandine.PreventivoGrandine,
            "patch": grandine.PreventivoGrandinePatch # Added Patch here since it was in your definition
        }
    }
}

class Settings(BaseSettings):
    DATABASE_URL: str

    MOUNT_PATH_EUREKA: str

    INFO_EUREKA_MAIL_USER: str
    INFO_EUREKA_MAIL_PASSWORD: str
    INFO_EUREKA_MAIL_HOST: str
    INFO_EUREKA_MAIL_PORT: int


    class Config:
        env_file = '.env'
        case_sensitive = False
        extra = "ignore"
settings = Settings()