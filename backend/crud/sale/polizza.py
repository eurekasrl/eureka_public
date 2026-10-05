import uuid

from sqlalchemy.orm import Session

from models import (
    Preventivo, Polizza, PolizzaGrandine,
    PianoUtilizzo, PianoUtilizzoDettagliato, Partita, Lifecycle
)
from schemas.sale import PolizzaCreate


def convert_preventivo_to_polizza(db: Session, data: PolizzaCreate):
    # 1. FETCH SOURCES
    preventivo = db.query(Preventivo).filter(Preventivo.id == data.preventivo_id).first()
    if not preventivo:
        raise Exception("Preventivo not found")
        
    # Get the Piano Utilizzo associated with the quote
    # (Assuming preventivo links to the piano via grandine_preventivo relationship)
    piano_utilizzo_id = preventivo.preventivo_grandine.piano_utilizzo_id
    
    # FETCH THE PARTITE (The data you said is already ready)
    partite = db.query(Partita).filter(Partita.piano_utilizzo_id == piano_utilizzo_id).all()
    
    if not partite:
        raise Exception("No Partite found. Please generate Partite before issuing Policy.")

    # 2. CREATE SALE HEADER (The Contract)
    # We initialize totals to 0, will sum them up in the loop
    new_sale_polizza = SalePolizza(
        id=str(uuid.uuid4()),
        numero=data.numero_polizza,
        
        # Link to Registry
        ragione_sociale_id=preventivo.ragione_sociale_id,
        ramo_id=preventivo.ramo_id,
        intermediario_id=preventivo.intermediario_id,
        compagnia_id=preventivo.compagnia_id,
        
        # Link to History
        preventivo_id=preventivo.id,
        lifecycle_id=7, # e.g., "Polizza Emessa"
        
        produttore_id=data.produttore_id,
        start_date=data.data_effetto,
        end_date=data.data_scadenza,
        
        premio_lordo=0, # Placeholder
        premio_netto=0  # Placeholder
    )
    db.add(new_sale_polizza)
    db.flush() # Flush to get the ID

    # 3. LOOP THROUGH PARTITE & CREATE TECHNICAL ROWS
    total_policy_premio_lordo = 0
    total_policy_premio_netto = 0
    
    # Retrieve rates from the quote (Assuming they are stored in grandine_preventivo)
    # You might need to adjust this depending on where exactly you store the "applied rate"
    quote_data = preventivo.preventivo_grandine
    
    for partita in partite:
        # A. Calculate Values for THIS Partita
        # Logic: Partita Surface * Yield (Resa) * Price (Prezzo) = Insured Value
        # You need to fetch the specific Price/Resa for the crop in this partita
        # For simplicity, I assume you have a helper or can calc it:
        
        valore_assicurato_partita = calculate_value(partita) 
        
        # B. Calculate Premium for THIS Partita
        # Logic: Value * Rate (from Quote)
        # Note: You might have different rates for Ag/Nag/Accessories
        
        premio_netto_partita = valore_assicurato_partita * (quote_data.tasso_totale / 100)
        premio_lordo_partita = premio_netto_partita * 1.025 # Example tax addition
        
        # C. Create the GrandinePolizza Row
        tech_row = GrandinePolizza(
            id=str(uuid.uuid4()),
            sale_polizza_id=new_sale_polizza.id, # Link to Header
            partita_id=partita.id,               # Link to Bucket
            
            valore_assicurato=valore_assicurato_partita,
            premio_netto=premio_netto_partita,
            premio_lordo=premio_lordo_partita,
            
            # Copy specific guarantees/rates from the quote if needed per row
            contribuzione=quote_data.contribuzione
        )
        db.add(tech_row)
        
        # Add to totals
        total_policy_premio_lordo += premio_lordo_partita
        total_policy_premio_netto += premio_netto_partita

    # 4. UPDATE HEADER TOTALS
    new_sale_polizza.premio_lordo = total_policy_premio_lordo
    new_sale_polizza.premio_netto = total_policy_premio_netto
    
    # 5. ADVANCE PREVENTIVO LIFECYCLE (Optional)
    # preventivo.lifecycle_id = ... (Closed/Won)

    db.commit()
    db.refresh(new_sale_polizza)
    return new_sale_polizza