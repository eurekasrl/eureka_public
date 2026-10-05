import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routers import *

API_KEY = os.getenv("API_KEY", "").strip()

# Paths reachable without the key: health check + interactive docs.
_PUBLIC_PATHS = {"/", "/docs", "/redoc", "/openapi.json"}

if not API_KEY:
    print("WARNING: API_KEY is not set — the API is running WITHOUT authentication. "
          "Set API_KEY in backend/.env (and VITE_API_KEY in frontend/.env) to enable it.")

app = FastAPI()


@app.middleware("http")
async def require_api_key(request: Request, call_next):
    # CORS preflight and public paths never require the key.
    if request.method == "OPTIONS" or request.url.path in _PUBLIC_PATHS:
        return await call_next(request)
    # If no key is configured we run open (a warning was logged at startup).
    if API_KEY and request.headers.get("X-API-Key") != API_KEY:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)

app.include_router(comuni.router, prefix="/comuni", tags=["Comuni"])
app.include_router(persone_fisiche.router, prefix="/persone-fisiche", tags=["Persone Fisiche"])
app.include_router(ragioni_sociali.router, prefix = "/ragioni-sociali", tags =["Ragione Sociale"])
app.include_router(gruppi.router, prefix="/gruppi", tags= ["Gruppi"])
app.include_router(rami.router, prefix = "/rami", tags =["Rami"])
app.include_router(intermediari.router, prefix = "/intermediari", tags =["Intermediari"])
app.include_router(compagnie.router, prefix = "/compagnie", tags =["Compagnie"])
app.include_router(preventivi.router, prefix="/preventivi", tags=["Preventivi"])
app.include_router(prodotti.router, prefix="/prodotti", tags=["Prodotti"])  
app.include_router(tables.router, prefix="/tables", tags=["Tables"])
app.include_router(piani_utilizzo.router, prefix="/piani-utilizzo", tags=["Piani Utilizzo"])
app.include_router(prezzi.router, prefix='/prezzi', tags=["Prezzi"])
app.include_router(condifesa.router, prefix="/condifesa", tags=["Condifesa"]) 
app.include_router(tassi.router, prefix="/tassi", tags=["Tassi"])
app.include_router(preventivi_grandine.router, prefix="/preventivi-grandine", tags=["Grandine Preventivo"])
app.include_router(documenti.router, prefix="/documenti", tags=["Documenti"])
app.include_router(relazione_rci.router, prefix="/relazione_rci", tags=["Relazione RCI"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Benvenuto al Gestionale Eureka!"}
