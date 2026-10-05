import os

from fastapi_mail import ConnectionConfig

INFO_EUREKA_MAIL_USER = os.getenv("INFO_EUREKA_MAIL_USER")
INFO_EUREKA_MAIL_PASSWORD = os.getenv("INFO_EUREKA_MAIL_PASSWORD")
INFO_EUREKA_MAIL_HOST = os.getenv("INFO_EUREKA_MAIL_HOST")
INFO_EUREKA_MAIL_PORT = int(os.getenv("INFO_EUREKA_MAIL_PORT"))

CONNECTION_CONFIG = ConnectionConfig(
        MAIL_USERNAME=INFO_EUREKA_MAIL_USER,
        MAIL_PASSWORD=INFO_EUREKA_MAIL_PASSWORD,
        MAIL_FROM=INFO_EUREKA_MAIL_USER,
        MAIL_PORT=INFO_EUREKA_MAIL_PORT,
        MAIL_SERVER=INFO_EUREKA_MAIL_HOST,
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )

try:
    from smtp.private import MAIL_BCC, MAIL_REDIRECT_TO, REFERENTE_EMAIL_BY_INTERMEDIARIO, EUREKA_EMAIL_SIGNATURE
except ModuleNotFoundError:
    # Public build: smtp/private.py (real contacts) is not exported.
    MAIL_BCC = []
    MAIL_REDIRECT_TO = None
    REFERENTE_EMAIL_BY_INTERMEDIARIO = {}
    EUREKA_EMAIL_SIGNATURE = "<p><strong>Eureka</strong></p></body></html>"

EMAIL_TABLE_STILE = """
    <style>
        .preventivi-table {
            border-collapse: collapse;
            width: 100%;
            font-family: Arial, sans-serif;
            font-size: 12px;
            color: #333;
        }
        .preventivi-table th {
            background-color: #f2f2f2;
            text-align: left;
            padding: 8px;
            border: 1px solid #ddd;
            font-weight: bold;
        }
        .preventivi-table td {
            padding: 8px;
            border: 1px solid #ddd;
            text-align: left;
        }
        .preventivi-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        /* Make numeric columns align right (optional, needs nth-child logic or specific classes) */
    </style>
    """
  