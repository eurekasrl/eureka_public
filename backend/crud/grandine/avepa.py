import itertools

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from models.grandine import Avepa

def get_avepa_by_codice_avepa_dettagliato(db, codice_avepa_dettagliato):
    split_avepa = codice_avepa_dettagliato.split("-")
    return db.query(Avepa).filter(Avepa.codice_occupazione == split_avepa[0],
                                   Avepa.codice_destinazione == split_avepa[1],
                                   Avepa.codice_uso == split_avepa[2],
                                   Avepa.codice_dettaglio == split_avepa[3]).first()


def get_avepa_by_nome(db, nome_avepa_list):
    if not nome_avepa_list:
        return None

    # 1. Fix the first element
    occupazione = nome_avepa_list[0].strip()
    
    # 2. Collect the remaining tokens (max 3)
    extra_tokens = [t.strip() for t in nome_avepa_list[1:] if t]
    
    # 3. Define the columns where these tokens could live
    other_cols = [Avepa.destinazione, Avepa.uso, Avepa.dettaglio]
    
    # We must fill 3 slots. If we have 1 token, 2 slots must be NULL.
    # If we have 2 tokens, 1 slot must be NULL.
    padded_tokens = extra_tokens + [None] * (len(other_cols) - len(extra_tokens))
    
    # 4. Generate all unique combinations
    # set() handles cases where tokens might be identical to avoid duplicate SQL
    possible_combos = set(itertools.permutations(padded_tokens))

    # 5. Build the OR conditions
    combo_filters = []
    for combo in possible_combos:
        # Each combo looks like: ('VITE', None, None)
        individual_and = []
        for i, val in enumerate(combo):
            col = other_cols[i]
            if val is not None:
                individual_and.append(col == val)
            else:
                # Based on your snippet, you want the DB value to be NULL 
                # if no token is assigned to this column
                individual_and.append(col.is_(None))
        
        combo_filters.append(and_(*individual_and))

    # 6. Execute Query
    query = db.query(Avepa).filter(
        Avepa.occupazione == occupazione,
        or_(*combo_filters)
    )

    # Optional: print(query) to see the generated SQL
    return query.first()

def get_nome_by_codice_avepa_dettagliato(db, codice_avepa_dettagliato):
    avepa = get_avepa_by_codice_avepa_dettagliato(db, codice_avepa_dettagliato)
    list_nomi = [avepa.occupazione, avepa.destinazione, avepa.uso, avepa.dettaglio]
    nome_completo = " - ".join(str(x) for x in list_nomi if x is not None and x!="")
    
    return nome_completo
