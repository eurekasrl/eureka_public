from sqlalchemy import update


from models.grandine import Tassi
from crud.grandine.config import coverage_fields

def prepare_grandine_rows_for_csv(db, ramo_preventivo, row ):
    active_tassi_ids = [getattr(ramo_preventivo, field) for field in coverage_fields if getattr(ramo_preventivo, field) is not None]
    results = db.query(Tassi.id, Tassi.garanzia, Tassi.fr, Tassi.tabella_conversione).filter(Tassi.id.in_(active_tassi_ids)).all()

    garanzia_list = []
    tabella_conv = ""
    for r in results:
        garanzia_list.append(f"{r.garanzia}:{r.fr}")
        if str(r.id) == str(ramo_preventivo.GR_AG_id):
            tabella_conv = r.tabella_conversione
    garanzie_fr = ", ".join(garanzia_list)

    piano = ramo_preventivo.piano_utilizzo
    prodotto = piano.prodotto if piano else None
    prezzi = ramo_preventivo.prezzi

    row = row + [
        piano.condifesa.nome if piano and piano.condifesa else "",
        piano.comune.nome if piano and piano.comune else "",
        prodotto.nome if prodotto else "",
        prodotto.dettaglio if prodotto else "",
        prodotto.codice_ministeriale if prodotto else "",
        prodotto.codice_dettaglio_condifesa if prodotto else "",
        piano.serra if piano else False,
        piano.bio if piano else False,
        piano.superficie if piano else 0,
        prezzi.valore if prezzi else 0,
        ramo_preventivo.resa_cliente,
        ramo_preventivo.valore_assicurato,
        tabella_conv,
        garanzie_fr,
        ramo_preventivo.ag,
        ramo_preventivo.nag,
        ramo_preventivo.lordo,
        ramo_preventivo.premio_lordo,
        ramo_preventivo.premio_netto,
    ]

    return row

def extract_garanzie_list(preventivo_grandine):
    garanzie_list = []
    for column in preventivo_grandine.__table__.columns:
        if column.name in coverage_fields:
            if getattr(preventivo_grandine, column.key):
                garanzie_list.append(f"{column.name.split('_')[0]}")
    tipologia_polizza = _get_polizza_tipo(garanzie_list)
    num_garanzie = len(garanzie_list)
    garanzie_list = ','.join(garanzie_list)
    return garanzie_list, num_garanzie, tipologia_polizza

def _get_polizza_tipo(garanzie_list):
    garanzie_list = set(garanzie_list)
    if garanzie_list==set(['GR']):
        return 'A'
    if garanzie_list==set(['GR','VF']) or garanzie_list==set(['GR','VF', 'EP']):
        return 'C'
    else:
        return 'B'
