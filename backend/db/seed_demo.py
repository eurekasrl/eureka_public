"""Synthetic demo data for a fresh database.

Every person, company, rate and price is invented. Only the comuni are real (public ISTAT data).
Codici fiscali, P.IVA and IBAN deliberately fail their checksum, so they cannot belong to anyone.
"""
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import text

from models.core import (
    CaaColdiretti, Compagnia, Condifesa, Documento, Gruppo, Intermediario,
    PersonaFisica, RagioneSociale, Ramo, RelazioneRci,
)
from models.grandine import (
    PianoUtilizzo, PianoUtilizzoDettagliato, PreventivoGrandine, Prezzi, Prodotto, Tassi,
)
from models.sale import Preventivo

ANNO = date.today().year

# codice_comune, nome, codice_provincia, sigla, provincia, nuts3, codice_catastale, cap
COMUNI = [
    (29001, "Adria", 29, "RO", "Rovigo", "ITH37", "A059", "45011"),
    (29003, "Arquà Polesine", 29, "RO", "Rovigo", "ITH37", "A435", "45031"),
    (29029, "Lendinara", 29, "RO", "Rovigo", "ITH37", "E522", "45026"),
    (29041, "Rovigo", 29, "RO", "Rovigo", "ITH37", "H620", "45100"),
    (23044, "Legnago", 23, "VR", "Verona", "ITH31", "E512", "37045"),
    (23091, "Verona", 23, "VR", "Verona", "ITH31", "L781", "37121"),
    (23096, "Villafranca di Verona", 23, "VR", "Verona", "ITH31", "L949", "37069"),
]

# The code relies on these ids (e.g. 3 = creato, 5 = approvato dal cliente).
LIFECYCLE = [
    (1, "preventivo", "rifiutato dal cliente"),
    (2, "preventivo", "rifiutata da intermediario/compagnia"),
    (3, "preventivo", "creato"),
    (4, "preventivo", "inviato al cliente"),
    (5, "preventivo", "approvato dal cliente"),
    (6, "preventivo", "richiesta inviata all'intermediario"),
    (7, "polizza", "richiesta approvata da intermediario/compagnia"),
    (8, "polizza", "copertura confermata al cliente"),
    (9, "polizza", "emissione polizza"),
    (100, "polizza", "test"),
]

# cf, nome, sesso, nascita, comune di nascita, comune di residenza, indirizzo, email
PERSONE = [
    ("SMPGLU85M52H620X", "Giulia Esempio", "F", date(1985, 8, 12), 29041, 29001, "Via dei Campi 1", "giulia.esempio@example.com"),
    ("PRVMRC78C03A059X", "Marco Prova", "M", date(1978, 3, 3), 29001, 29041, "Via del Mulino 2", "marco.prova@example.com"),
    ("DMENNA90S65E512X", "Anna Demo", "F", date(1990, 11, 25), 23044, 23044, "Strada delle Vigne 3", "anna.demo@example.com"),
]

# gruppo, nome, codice_ministeriale, codice AVEPA dettagliato, fattore di rischio, resa max (q/ha), prezzo fascia A (€/q)
PRODOTTI = [
    ("SEMINATIVI", "FRUMENTO TENERO", "C01", "002-011-000-000-392", "1.00", "75", "24.50"),
    ("SEMINATIVI", "MAIS", "C02", "004-001-000-000-101", "1.10", "120", "23.00"),
    ("SEMINATIVI", "SOIA", "C03", "010-001-000-000-110", "1.05", "45", "42.00"),
    ("SEMINATIVI", "BARBABIETOLA DA ZUCCHERO", "C04", "020-001-000-000-120", "1.15", "700", "4.80"),
    ("FRUTTA", "MELO", "D01", "301-001-000-000-200", "1.60", "550", "45.00"),
    ("FRUTTA", "PERO", "D02", "302-001-000-000-210", "1.60", "350", "70.00"),
    ("VITE", "UVA DA VINO", "H80", "410-001-000-000-300", "1.40", "200", "55.00"),
    ("INDUSTRIALI", "TABACCO", "C18", "510-001-000-000-400", "1.80", "35", "330.00"),
]

# tipo, garanzia, {franchigia: (tasso agevolato, tasso non agevolato)}; the catastrofali have no NAG part.
GARANZIE = [
    ("GRANDINE", "GR", {10: ("2.80", "0.60"), 15: ("2.50", "0.50"), 20: ("2.20", "0.40")}),
    ("AVVERSITA' DI FREQUENZA", "VF", {20: ("1.50", "0.30"), 30: ("1.20", "0.25")}),
    ("AVVERSITA' DI FREQUENZA", "EP", {20: ("1.00", "0.20"), 30: ("0.80", "0.15")}),
    ("CATASTROFALI", "GELO", {30: ("1.80", None)}),
    ("CATASTROFALI", "SICCITA", {30: ("2.20", None)}),
    ("CATASTROFALI", "ALLUVIONE", {30: ("0.90", None)}),
]

# nome, sigla, solo grandine, intermediario, codice_ministeriale, firmato, personale, obbligatorio, lifecycle_id
DOCUMENTI = [
    ("Piano Utilizzo Dettagliato", "PUD", True, None, None, False, False, False, 3),
    ("Piano Utilizzo Riepilogativo", "PUR", True, None, None, False, False, False, 3),
    ("Schedario Vitivinicolo", "SV", True, None, "H80", False, False, False, 3),
    ("Ricevuta Manifestazione Interesse", "RIC", True, None, None, False, False, True, 5),
    ("Manifestazione Interesse", "MI", True, None, None, False, False, True, 5),
    ("Conferma Ordine Copertura", "COC", True, "BROKER UNO", None, True, False, True, 5),
    ("Conferma Ordine Copertura", "COC", False, None, None, False, False, False, 5),
    ("A500", "A500", True, "BROKER DUE", None, False, False, True, 5),
    ("Vincolo tabacco", "VINCOLOTAB", True, None, "C18", True, False, False, 5),
    ("Adesione Fondo Mutualistico", "AFM", True, None, None, True, False, False, 5),
    ("Autocertificazione", "AUTOCERTIFICAZIONE", True, None, None, True, False, False, 5),
    ("Conferma Copertura Assicurazione", "CCA", False, None, None, False, False, True, 7),
    ("Mup", "MUP", False, None, None, True, False, True, 9),
    ("Certificato", "CERT", False, None, None, True, False, True, 9),
    ("Quietanza Premio", "QPPREMIO", False, None, None, True, False, False, 100),
    ("Quietanza Indennizzo", "QINDENNIZZO", False, None, None, True, False, True, 100),
    ("Carta Identità", "CI", False, None, None, False, True, False, None),
    ("Carta Identità", "CI", False, "BROKER UNO", None, False, True, False, None),
]

# ragione sociale -> [(codice_comune, prodotto, [(foglio, particella, superficie in mq)])]
PIANI = {
    "esempio": [
        (29001, "FRUMENTO TENERO", [(12, 101, 18500), (12, 102, 9300), (14, 33, 24000)]),
        (29001, "MAIS", [(15, 7, 31000), (15, 8, 12500)]),
        (29003, "SOIA", [(3, 210, 15800)]),
        (29029, "MELO", [(21, 55, 8700), (21, 56, 6400)]),
    ],
    "prova": [
        (29041, "BARBABIETOLA DA ZUCCHERO", [(40, 12, 42000)]),
        (29041, "FRUMENTO TENERO", [(40, 13, 27500)]),
        (29029, "PERO", [(8, 90, 11200)]),
    ],
    "fattoria": [
        (23044, "TABACCO", [(5, 18, 22000)]),
        (23096, "UVA DA VINO", [(11, 4, 13400), (11, 5, 9800)]),
    ],
}

# Deliberate gap between riepilogativo and dettagliato, so the PU dashboard has something to flag.
DIFFERENZE_RIEPILOGO = {("esempio", "MELO"): 900}

# ragione sociale, comune, prodotto, compagnia, intermediario, {garanzia: franchigia}, resa (q/ha), lifecycle_id
PREVENTIVI = [
    ("esempio", 29001, "FRUMENTO TENERO", "ALFA", "BROKER UNO", {"GR": 10, "VF": 20}, 70, 4),
    ("esempio", 29001, "MAIS", "BETA", "BROKER DUE", {"GR": 15}, 110, 3),
]

CENT = Decimal("0.01")


def new_id():
    # SQL Server returns uniqueidentifiers uppercase; SQLAlchemy's bulk insert matches rows by exact value.
    return str(uuid.uuid4()).upper()


def seed_demo(db):
    db.execute(
        text(
            "INSERT INTO core.comune (codice_regione, codice_unita, codice_provincia, progressivo_comune, codice_comune, nome, "
            "codice_ripartizione_geografica, ripartizione_geografica, denominazione_regione, denominazione_unita, tipologia_unita, "
            "provincia_short, codice_catastale, codice_nuts3, cap) VALUES (5, :provincia, :provincia, :progressivo, :codice, :nome, "
            "2, 'Nord-est', 'Veneto', :denominazione, 1, :sigla, :catastale, :nuts3, :cap)"
        ),
        [
            dict(codice=c, nome=n, provincia=p, progressivo=c % 1000, sigla=s, denominazione=d, nuts3=nuts, catastale=cat, cap=cap)
            for c, n, p, s, d, nuts, cat, cap in COMUNI
        ],
    )
    db.execute(
        text("INSERT INTO core.lifecycle (id, sale_reference, stato) VALUES (:id, :ref, :stato)"),
        [dict(id=i, ref=r, stato=s) for i, r, s in LIFECYCLE],
    )

    grandine = Ramo(id=new_id(), ramo="danni", numero=3, nome="Danni ai beni", dettaglio="grandine")
    condifesa = Condifesa(id=new_id(), nome="Condifesa Demo Veneto", email="condifesa@example.com", cell="0000000008")
    caa = CaaColdiretti(id=new_id(), nome="CAA Demo Rovigo", email="caa@example.com", cell="0000000009", codice_comune=29041)
    compagnie = {
        "ALFA": Compagnia(id=new_id(), short_nome="ALFA", full_nome="Compagnia Demo Alfa S.p.A.", piva="00000000040",
                          email="alfa@example.com", pec="alfa@pec.example.com", cell="0000000004",
                          indirizzo="Piazza Esempio 1", codice_comune=23091),
        "BETA": Compagnia(id=new_id(), short_nome="BETA", full_nome="Compagnia Demo Beta S.p.A.", piva="00000000050",
                          email="beta@example.com", pec="beta@pec.example.com", cell="0000000005",
                          indirizzo="Corso Prova 2", codice_comune=29041),
    }
    intermediari = {
        "BROKER UNO": Intermediario(id=new_id(), short_nome="BROKER UNO", full_nome="Broker Demo Uno S.r.l.", piva="00000000060",
                                    email="uno@example.com", pec="uno@pec.example.com", cell="0000000006",
                                    indirizzo="Via Fittizia 3", codice_comune=29041),
        "BROKER DUE": Intermediario(id=new_id(), short_nome="BROKER DUE", full_nome="Broker Demo Due S.r.l.", piva="00000000070",
                                    email="due@example.com", pec="due@pec.example.com", cell="0000000007",
                                    indirizzo="Via Inventata 4", codice_comune=23091),
    }
    persone = [
        PersonaFisica(cf=cf, nome=nome, sesso=sesso, data_di_nascita=nascita, codice_comune_di_nascita=nato_a,
                      codice_comune=residenza, indirizzo=indirizzo, email=email, cell="0000000000")
        for cf, nome, sesso, nascita, nato_a, residenza, indirizzo, email in PERSONE
    ]
    db.add_all([grandine, condifesa, caa, *compagnie.values(), *intermediari.values(), *persone])
    db.flush()

    giulia, marco, anna = (p.cf for p in persone)
    gruppo = Gruppo(id=new_id(), nome="Famiglia Esempio", referente_cf=giulia)
    gruppo_anna = Gruppo(id=new_id(), nome="Anna Demo", referente_cf=anna)
    relazioni = [
        RelazioneRci(id=new_id(), ramo_id=grandine.id, compagnia_id=c.id, intermediario_id=i.id, active=True)
        for c in compagnie.values() for i in intermediari.values()
    ]
    prodotti = {
        nome: Prodotto(id=new_id(), condifesa_id=condifesa.id, gruppo=gruppo_prodotto, nome=nome, dettaglio="",
                       codice_ministeriale=codice, codice_dettaglio_ministeriale="001", codice_dettaglio_condifesa=f"{n:03d}",
                       codice_prodotto=f"{n:03d}", codice_gis=f"GIS{n:03d}", codice_avepa_dettagliato=avepa)
        for n, (gruppo_prodotto, nome, codice, avepa, *_) in enumerate(PRODOTTI, start=1)
    }
    db.add_all([gruppo, gruppo_anna, *relazioni, *prodotti.values()])
    db.flush()

    ragioni_sociali = {
        "esempio": RagioneSociale(id=new_id(), nome="Azienda Agricola Esempio Giulia", responsabile_legale_cf=giulia, CUAA=giulia,
                                  piva="00000000010", gruppo_id=gruppo.id, codice_comune=29001, indirizzo="Via dei Campi 1",
                                  IBAN="IT00A0000000000000000000001", caa_coldiretti_id=caa.id,
                                  email="azienda.esempio@example.com", pec="azienda.esempio@pec.example.com"),
        "prova": RagioneSociale(id=new_id(), nome="Società Agricola Prova S.S.", responsabile_legale_cf=marco, CUAA="00000000020",
                                piva="00000000020", gruppo_id=gruppo.id, codice_comune=29041, indirizzo="Via del Mulino 2",
                                IBAN="IT00A0000000000000000000002", caa_coldiretti_id=caa.id,
                                email="societa.prova@example.com", pec="societa.prova@pec.example.com"),
        "fattoria": RagioneSociale(id=new_id(), nome="Fattoria Demo di Anna", responsabile_legale_cf=anna, CUAA=anna,
                                   piva="00000000030", gruppo_id=gruppo_anna.id, codice_comune=23044, indirizzo="Strada delle Vigne 3",
                                   IBAN="IT00A0000000000000000000003", email="fattoria.demo@example.com"),
    }
    documenti = [
        Documento(id=new_id(), ramo_id=grandine.id if solo_grandine else None,
                  intermediario_id=intermediari[intermediario].id if intermediario else None,
                  codice_ministeriale=codice, nome=nome, sigla=sigla, signed=firmato, personale=personale,
                  mandatory=obbligatorio, entity=False, lifecycle_id=lifecycle_id)
        for nome, sigla, solo_grandine, intermediario, codice, firmato, personale, obbligatorio, lifecycle_id in DOCUMENTI
    ]
    prezzi = {}
    for _, nome, _, _, _, resa_max, prezzo in PRODOTTI:
        for fascia, fattore in (("A", "1.00"), ("B", "0.90"), ("D", "0.95")):
            valore = (Decimal(prezzo) * Decimal(fattore)).quantize(CENT)
            prezzi[nome, fascia] = Prezzi(id=new_id(), anno=ANNO, condifesa_id=condifesa.id, prodotto_id=prodotti[nome].id,
                                          area="VENETO", resa_max=Decimal(resa_max), fascia=fascia, valore=valore,
                                          sv=valore, sv_bio=(valore * Decimal("1.20")).quantize(CENT))
    tassi = {}
    for (c_nome, compagnia), fattore_c in zip(compagnie.items(), ("1.00", "1.08")):
        for (i_nome, intermediario), fattore_i in zip(intermediari.items(), ("1.00", "0.97")):
            for codice_comune, *_rest in COMUNI:
                fattore_comune = Decimal("1.15") if codice_comune < 29000 else Decimal("1.00")
                for _, nome, codice, _, rischio, _, _ in PRODOTTI:
                    fattore = Decimal(rischio) * Decimal(fattore_c) * Decimal(fattore_i) * fattore_comune
                    for tipo, garanzia, franchigie in GARANZIE:
                        for fr, valori in franchigie.items():
                            for tasso, base in zip(("AG", "NAG"), valori):
                                if base is None:
                                    continue
                                tassi[c_nome, i_nome, codice_comune, nome, garanzia, fr, tasso] = Tassi(
                                    id=new_id(), anno=ANNO, compagnia_id=compagnia.id, intermediario_id=intermediario.id,
                                    codice_comune=codice_comune, codice_ministeriale=codice, tabella_conversione="A",
                                    tipo=tipo, garanzia=garanzia, fr=fr, tasso=tasso,
                                    valore=(Decimal(base) * fattore).quantize(CENT),
                                )
    db.add_all([*ragioni_sociali.values(), *documenti, *prezzi.values(), *tassi.values()])
    db.flush()

    piani = {}
    for rs_key, righe in PIANI.items():
        rs = ragioni_sociali[rs_key]
        for codice_comune, prodotto, particelle in righe:
            for foglio, particella, superficie in particelle:
                db.add(PianoUtilizzoDettagliato(id=new_id(), ragione_sociale_id=rs.id, condifesa_id=condifesa.id, anno=ANNO,
                                                codice_comune=codice_comune, prodotto_id=prodotti[prodotto].id,
                                                foglio=foglio, particella=particella, superficie=superficie))
            totale = sum(s for _, _, s in particelle) + DIFFERENZE_RIEPILOGO.get((rs_key, prodotto), 0)
            piani[rs_key, codice_comune, prodotto] = PianoUtilizzo(
                id=new_id(), ragione_sociale_id=rs.id, condifesa_id=condifesa.id, anno=ANNO, tipo="riepilogativo",
                codice_comune=codice_comune, prodotto_id=prodotti[prodotto].id, superficie=totale)
    db.add_all(piani.values())
    db.flush()

    # Preventivo and its grandine detail go in the same flush: the before_flush hook in models/grandine.py
    # would otherwise reset every seeded preventivo to "creato".
    for rs_key, codice_comune, prodotto, c_nome, i_nome, garanzie, resa, lifecycle_id in PREVENTIVI:
        piano = piani[rs_key, codice_comune, prodotto]
        prezzo = prezzi[prodotto, "A"]
        scelti = {
            f"{garanzia}_{tasso}_id": tassi.get((c_nome, i_nome, codice_comune, prodotto, garanzia, fr, tasso))
            for garanzia, fr in garanzie.items() for tasso in ("AG", "NAG")
        }
        ag = sum(t.valore for k, t in scelti.items() if t and k.endswith("_AG_id"))
        nag = sum(t.valore for k, t in scelti.items() if t and k.endswith("_NAG_id"))
        valore_assicurato = int(Decimal(piano.superficie) / 10000 * resa * prezzo.valore)
        premio_lordo = (valore_assicurato * (ag + nag) / 100).quantize(CENT)
        preventivo = Preventivo(id=new_id(), ragione_sociale_id=ragioni_sociali[rs_key].id, ramo_id=grandine.id,
                                intermediario_id=intermediari[i_nome].id, compagnia_id=compagnie[c_nome].id,
                                premio_lordo=premio_lordo, lifecycle_id=lifecycle_id)
        db.add_all([
            preventivo,
            PreventivoGrandine(
                sale_preventivo_id=preventivo.id, piano_utilizzo_id=piano.id, prezzo_id=prezzo.id,
                **{campo: t.id for campo, t in scelti.items() if t},
                ag=ag, nag=nag, lordo=ag + nag, resa_cliente=resa, valore_assicurato=valore_assicurato,
                premio_lordo=premio_lordo,
                premio_netto=(valore_assicurato * (Decimal("0.5") * ag + nag) / 100).quantize(CENT),
            ),
        ])
    db.flush()
