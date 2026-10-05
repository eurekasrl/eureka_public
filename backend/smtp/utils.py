from fastapi import HTTPException

from smtp.smtp import send_email
from crud.sale.utils import get_preventivi_smtp_data_for_client, get_preventivi_smtp_data_for_intermediario
from crud.core.gruppo import get_gruppo_by_id
from crud.core.ragione_sociale import get_ragione_sociale_by_id

def send_smtp_email(request, background_tasks, destinatario, db):
    preventivo_subject=''
    recipient_email=''
    preventivo_body=''
    virtual_files = None


    if destinatario=="cliente":
        if request.client_level=='gruppo':
            client = get_gruppo_by_id(db, request.client_level_id)
            recipient_email = client.referente.email
        elif request.client_level=='ragione_sociale':
            client = get_ragione_sociale_by_id(db, request.client_level_id)
            recipient_email = client.email
        else:
            raise HTTPException(status_code=400, detail="Client has no email address")
        
        preventivo_subject, preventivo_body, virtual_files = get_preventivi_smtp_data_for_client(
        request= request,
        db = db,
        client = client
        )
    
    elif destinatario=="intermediario":
        preventivo_subject, recipient_email, preventivo_body, virtual_files = get_preventivi_smtp_data_for_intermediario (request= request, db=db)
    
    send_email(
        subject= preventivo_subject,
        recipients= recipient_email,
        body= preventivo_body,
        attachments= virtual_files,
        background_tasks= background_tasks
        )
    