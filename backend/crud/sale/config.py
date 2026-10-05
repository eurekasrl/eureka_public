from typing import Optional, Dict

from crud.grandine.config import headers_preventivo_grandine_csv
from smtp.config import EMAIL_TABLE_STILE, REFERENTE_EMAIL_BY_INTERMEDIARIO
from crud.grandine.utils import extract_garanzie_list

HEADERS_PREVENTIVO_CSV_BASE = [
        "Compagnia",
        "Intermediario",
        "Stato",
        "Data Creazione",
        "Ultimo Aggiornamento"
    ]

headers_preventivo_csv = {
    'gruppo':["Ragione Sociale"] + HEADERS_PREVENTIVO_CSV_BASE,
    'ragione_sociale': HEADERS_PREVENTIVO_CSV_BASE
    }

final_headers_csv = {
    'default': headers_preventivo_csv,
    'grandine': {key: val + headers_preventivo_grandine_csv for key, val in headers_preventivo_csv.items()}
}

def get_email_preventivi_subject(ramo_dettaglio:str, anno:str, additional_info: Optional[Dict]=None):
    subject = f"Preventivi {ramo_dettaglio} {anno}"
    if additional_info:
        subject = f"{subject} - {','.join(additional_info)}"
    
    return subject

def get_email_preventivi_subject_for_intermediario(ragione_sociale_nome):
    return f"[Eureka srl] Nuova Richiesta Messa in Copertura - {ragione_sociale_nome}"
    
def _get_conferma_ordine_fermo_copertura(ramo:str, anno:str):
    if ramo=='grandine':
        return f"""
<div>
<p>
Per procedere con la copertura assicurativa 2025, La invitiamo a rispondere a questa email con <strong>“Sì”</strong> o <strong>“Confermo”</strong>.
</p>
<p>
Con tale risposta Lei dichiara di aver letto e accettato quanto segue:</p>
<ul>
    <li>I <strong>quintali/quantità assicurata</strong> indicati corrispondono alla Sua reale intenzione di assicurare.</li>
    <li>Si impegna a fornire <strong>tutta la documentazione prevista</strong> dal Decreto Ministeriale in vigore.</li>
    <li>Conferisce <strong>ordine fermo e irrevocabile</strong> di copertura per le produzioni indicate.</li>
    <li>Accetta di assicurarsi <strong>anche senza conoscere</strong> i parametri contributivi {anno} e si impegna al <strong>pagamento del premio</strong> dovuto.</li>
    <li>Autorizza l’invio ad <strong>Eureka S.r.l.</strong> della documentazione necessaria (manifestazione di interesse, schedario viticolo/fascicolo aziendale/piano di utilizzo aggiornati),
    qualsiasi <strong>modifica</strong> deve essere comunicataci nel più breve tempo possibile.
    </li>
    <li><strong>Contributo ipotizzato: 55% della spesa ammessa</strong> (2, 3 o 6 avversità).</li>
    <li>In assenza dei Prezzi {anno}, verranno applicati i valori {int(anno)-1} con <strong>aggiornamento automatico</strong>.</li>
    <li>È consapevole che il contributo MIPAAF o europeo <strong>non è garantito</strong> e si impegna comunque al pagamento totale del premio.</li>
    <li>L’assicurato deve recarsi presso il <strong>CAA</strong> per aggiornare il fascicolo aziendale e richiedere la <strong>Manifestazione di Interesse</strong>.</li>
</ul>
<p>Per confermare è sufficiente rispondere a questa email con <strong>“Sì/Confermo”</strong>.</p>
"""
    return ""
    
def get_email_preventivi_body(client_nome:str, additional_info: str, additiona_html_table:Optional[str]=None, ramo:str='', anno:str=''):
    conferma_ordine_fermo_copertura = _get_conferma_ordine_fermo_copertura(ramo, anno)
    body = f"""
    <html>
    <head>{EMAIL_TABLE_STILE}</head>
    <body style="font-family: Arial, sans-serif;">
    <p>Gentile {client_nome},</p>
    <p>In allegato trova il file Excel contenente i preventivi per {additional_info}. """
    if ramo=='grandine':
        body = f"""{body}Ricordiamo che il Premio Netto è una stima dato che la contribuzione si conoscerà solamente più tardi.</p><br>"""
    if additiona_html_table:
        body = f"""{body}<div style="overflow-x:auto;">
        {additiona_html_table}
    </div>
    <br>
    {conferma_ordine_fermo_copertura}
        
    <div style="font-size: 13px; color: #555;">
    <p>Cordiali Saluti,</p>
    </div>"""
        return body

def get_email_preventivi_body_for_intermediario(ramo_dettaglio, preventivi, anno):
    intermediario = preventivi[0].intermediario
    if ramo_dettaglio=='grandine':
        destinatario = REFERENTE_EMAIL_BY_INTERMEDIARIO.get(intermediario.short_nome, {"referente": intermediario.full_nome})
        prodotti_list = []
        bullet_points = ""
        for preventivo in preventivi:
            preventivo_grandine = preventivo.preventivo_grandine
            nome_prodotto = preventivo_grandine.piano_utilizzo.prodotto.nome
            dettaglio_prodotto = preventivo_grandine.piano_utilizzo.prodotto.dettaglio
            ragione_sociale = preventivo.ragione_sociale.nome
            comune = preventivo_grandine.piano_utilizzo.comune.nome
            garanzie, num_garanzie, tipologia_polizza = extract_garanzie_list(preventivo_grandine)
            valore_assicurato = preventivo_grandine.valore_assicurato
            consorzio = preventivo_grandine.piano_utilizzo.condifesa.nome

            bullet_points = bullet_points + f"""
<ul>
    <li>{ragione_sociale}</li>
    <li><strong>{nome_prodotto}-{dettaglio_prodotto}</strong></li>
    <li>Comune: {comune}</li>
    <li>Polizza tipo {tipologia_polizza}: {num_garanzie} garanzie <strong>{garanzie}</strong></li>
    <li>Valore Assicurato: <strong>{valore_assicurato:,}€</strong></li>
    <li>Consorzio: {consorzio}</li>
</ul>
"""
            
            
            prodotti_list.append(f"{preventivo_grandine.piano_utilizzo.prodotto.nome}-{preventivo_grandine.piano_utilizzo.prodotto.dettaglio}")
        prodotti = ','.join(set(prodotti_list))


        body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
    <p>Gentile {destinatario["referente"]},</p>
    <p> con la presente inoltro nuova richiesta messa in copertura <strong>{prodotti}</strong></p>
    {bullet_points}
    <p>In allegato manifestazione di interesse {anno} ed eventuale autocertificazione.</p>
    <p>Vi ringrazio e rimango a disposizione</p>
    <div style="font-size: 13px; color: #555;">
    <p>Cordiali Saluti,</p>
    </div>
    """
        
    return body

