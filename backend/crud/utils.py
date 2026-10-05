from uuid import UUID
from decimal import Decimal, InvalidOperation
import io
import csv

from sqlalchemy.orm import Session
import pandas as pd

from crud.sale.preventivo import get_preventivo
from crud.core.ragione_sociale import get_ragione_sociale_by_id
from crud.grandine.piano_utilizzo import get_piani_utilizzo_by_ragione_sociale, get_piano_utilizzo
from crud.grandine.tassi import get_tassi_for_tabella_conversione
from crud.sale.config import final_headers_csv
from crud.grandine.utils import prepare_grandine_rows_for_csv

def get_piani_utilizzo_by_preventivo_id(db: Session, preventivo_id: str):
    preventivo_db = get_preventivo(db=db, preventivo_id=preventivo_id)
    ragione_sociale = get_ragione_sociale_by_id(db=db, id=preventivo_db.ragione_sociale_id)
    return get_piani_utilizzo_by_ragione_sociale(db=db, ragione_sociale_id= ragione_sociale.id)

def get_tassi_by_piano_utilizzo_preventivo(db: Session, piano_utilizzo_id: str, preventivo_id: str):
    piano_utilizzo_db = get_piano_utilizzo(db, piano_utilizzo_id)
    preventivo_db = get_preventivo(db, preventivo_id)

    anno = piano_utilizzo_db.anno
    codice_comune = piano_utilizzo_db.codice_comune
    codice_ministeriale = piano_utilizzo_db.prodotto.codice_ministeriale
    intermediario_id = preventivo_db.intermediario_id
    compagnia_id = preventivo_db.compagnia_id

    return get_tassi_for_tabella_conversione(db, anno, intermediario_id, compagnia_id, codice_ministeriale, codice_comune)

def get_tassi_by_piano_utilizzo_compagnia_intermediario(db:Session, piano_utilizzo_id: str, compagnia_id: str, intermediario_id: str):
    piano_utilizzo_db = get_piano_utilizzo(db, piano_utilizzo_id)

    anno = piano_utilizzo_db.anno
    codice_comune = piano_utilizzo_db.codice_comune
    codice_ministeriale = piano_utilizzo_db.prodotto.codice_ministeriale

    return get_tassi_for_tabella_conversione(db, anno, intermediario_id, compagnia_id, codice_ministeriale, codice_comune)

def uuid_to_str(data):
    for key, value in data.items():
        if isinstance(value, UUID):
            data[key] = str(value)
    return data

def compare_on_patch(new_data, old_data):
    data_changed = False

    for field, new_value in new_data.items():
        current_value = getattr(old_data, field)

        # --- 1. Handle UUIDs (Case Insensitive) ---
        if isinstance(new_value, UUID) or isinstance(current_value, UUID):
            if str(new_value).lower() != str(current_value).lower():
                print(f"DEBUG: UUID Change for {field}: {current_value} -> {new_value}")
                setattr(old_data, field, str(new_value))
                data_changed = True
            continue # Skip to next field

        # --- 2. Handle Numerics (Decimal vs Float vs String) ---
        # Check if the DB field is a Decimal (common for money)
        if isinstance(current_value, Decimal):
            try:
                # Convert the NEW value to Decimal for a fair comparison.
                # We use str() first because Decimal(float(7.09)) can result in 7.0899999...
                new_value_decimal = Decimal(str(new_value))
                
                # In Python, Decimal('70.80') == Decimal('70.8') is TRUE
                if current_value != new_value_decimal:
                    print(f"DEBUG: Decimal Change for {field}: {current_value} -> {new_value_decimal}")
                    setattr(old_data, field, new_value_decimal)
                    data_changed = True
            except (InvalidOperation, ValueError, TypeError):
                # Fallback if conversion fails
                if current_value != new_value:
                    setattr(old_data, field, new_value)
                    data_changed = True
            continue # Skip to next field

        # --- 3. Handle Standard Types (Strings, Bools, etc) ---
        if current_value != new_value:
            print(f"DEBUG: Standard Change for {field}: {current_value} -> {new_value}")
            setattr(old_data, field, new_value)
            data_changed = True

    return old_data, data_changed

def prepare_csv(db, preventivi, anno, client_level ):
    ramo_dettaglio = preventivi[0].ramo.dettaglio
    
    
    output = io.StringIO()
    writer = csv.writer(output)

    #write headers
    config_by_ramo = final_headers_csv.get(ramo_dettaglio, final_headers_csv['default'])
    writer.writerow(config_by_ramo[client_level])

    #write rows
    for preventivo in preventivi:
        ramo_preventivo = getattr(preventivo, f"preventivo_{ramo_dettaglio}", None)
        ragione_sociale_nome = preventivo.ragione_sociale.nome
        cliente_nome = ragione_sociale_nome

        row = []
        if client_level=='gruppo':
            row = [ragione_sociale_nome]
            cliente_nome = preventivo.ragione_sociale.gruppo.referente.nome
        row = row + [
            preventivo.compagnia.short_nome,
            preventivo.intermediario.short_nome,
            preventivo.lifecycle.stato,
            preventivo.created_at.strftime("%Y-%m-%d %H:%M") if preventivo.created_at else "",
            preventivo.updated_at.strftime("%Y-%m-%d %H:%M") if preventivo.created_at else "",
        ]

        if ramo_dettaglio=='grandine':
            row = prepare_grandine_rows_for_csv(db, ramo_preventivo, row)
        writer.writerow(row)
    output.seek(0)

    filename = f"preventivi_{cliente_nome}_{anno}_{ramo_dettaglio}.csv"

    return filename, output

def prepare_xlsx(db, preventivi, anno, client_level):
    ramo_dettaglio = preventivi[0].ramo.dettaglio
    config_by_ramo = final_headers_csv.get(ramo_dettaglio, final_headers_csv['default'])
    headers = config_by_ramo[client_level]

    data = []
    for preventivo in preventivi:
        ramo_preventivo = getattr(preventivo, f"preventivo_{ramo_dettaglio}", None)
        ragione_sociale_nome = preventivo.ragione_sociale.nome
        cliente_nome = ragione_sociale_nome


        row = []
        if client_level=='gruppo':
            row = [ragione_sociale_nome]
            cliente_nome = preventivo.ragione_sociale.gruppo.referente.nome
        row = row + [
            preventivo.compagnia.short_nome,
            preventivo.intermediario.short_nome,
            preventivo.lifecycle.stato,
            preventivo.created_at.strftime("%Y-%m-%d %H:%M") if preventivo.created_at else "",
            preventivo.updated_at.strftime("%Y-%m-%d %H:%M") if preventivo.created_at else "",
        ]

        if ramo_dettaglio=='grandine':
            row = prepare_grandine_rows_for_csv(db, ramo_preventivo, row)
        data.append(row)
    
    df = pd.DataFrame(data, columns=headers)
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Preventivi")
    excel_buffer.seek(0)
    filename = f"preventivi_{cliente_nome}_{anno}_{ramo_dettaglio}.xlsx"

    cols_to_show = [
        'Compagnia', 'Condifesa', 'Comune', 'Prodotto nome', 'Prodotto dettaglio', 
        'Serra', 'Bio', 'Superficie (mq)', 'Prezzo', 'Resa', 'Valore Assicurato', 
        'Tabella di Conversione', 'Garanzie e Franchigie', 
        'Tasso Agevolato', 'Tasso Non Agevolato', 'Tasso Lordo', 
        'Premio Lordo', 'Premio Netto'
    ]
    df_summary = df[cols_to_show].copy()
    currency_cols = ['Prezzo', 'Valore Assicurato', 'Premio Lordo', 'Premio Netto']
    bool_cols = ['Serra', 'Bio']
    num_cols = ['Superficie (mq)']
    perc_cols = ['Tasso Agevolato', 'Tasso Non Agevolato', 'Tasso Lordo']

    for col in df_summary.columns:
        if col in currency_cols:
            df_summary[col] = df_summary[col].apply(lambda x: fmt_curr(x) if pd.notnull(x) else '')
        elif col in bool_cols:
            df_summary[col] = df_summary[col].apply(fmt_bool)
        elif col in num_cols:
            df_summary[col] = df_summary[col].apply(lambda x: fmt_num(x) if pd.notnull(x) else '')
        elif col in perc_cols:
            df_summary[col] = df_summary[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else '')
    
    html_table = df_summary.to_html(index=False, border=0, classes='preventivi-table')

    return filename, excel_buffer, html_table

def fmt_curr(x):
    return f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
def fmt_bool(x):
    return "Sì" if x else "No"

def fmt_num(x):
    return f"{x:,.0f}".replace(",", ".")

def sanitize_name(name: str) -> str:
        """Removes unsafe characters for folder names."""
        return "".join([c for c in name if c.isalnum() or c in (' ', '-', '_',"'")]).strip()
