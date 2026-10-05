# Eureka — Project Standards

## Stack
- **Frontend**: React 19 + Vite + MUI v7, Axios, React Router v7. Source: `frontend/src/`.
- **Backend**: FastAPI (Python 3.13), SQLAlchemy, pdfplumber. Source: `backend/`.
- **DB**: SQL Server Express (`eureka-dev`), Windows auth (`trusted_connection=yes`). Connection config: `backend/.env`. Docker: SQL Server 2022 container, SQL auth, database `eureka`.

## Business Rules — Do Not Break These
- **Wipe & Replace**: saving a Piano di Utilizzo deletes ALL existing records for that `ragione_sociale_id` + `anno` pair, then bulk-inserts the new data. Never silently change this to a partial update — it is intentional and documented to the user.
- **PDF matching pipeline**: `paranoid_normalize` in `services/utils.py` is the normalization contract (strip accents, backticks, spaces → pure alphanumeric uppercase). The segmented text match in `match_prodotto_smart` is load-bearing. Any change to `pdf_parser.py` or `services/utils.py` must be covered by tests.
- **Workflow order**: PU upload → Partite generation → Preventivo → Certificato. UI routes and state transitions must respect this sequence.
- **Pre-sorting modal**: before importing PDF rows into the table, unique prodotti (crops) AND unique comuni are validated by the user in a modal. The bulk table is only built after this step. Do not bypass the modal.

## Code Standards
- UI text is in **Italian**. No English strings in user-facing components.
- No new `npm` or `pip` packages without explicit approval.
- No `alert()` or `window.confirm()` — use MUI `Snackbar` for notifications and a MUI `Dialog`-based `ConfirmDialog` component for confirmations.
- Catch variables are always named `err`, never `error` (which silently shadows the browser global `Error` and masks stack traces).
- API calls live in `frontend/src/api/`. No inline `axios` calls inside components.
- No comments that explain what code does — only why (hidden constraint, non-obvious workaround).

## Testing
- Backend tests live in `backend/test/` and use **pytest**.
- Integration tests use the real `eureka-dev` SQL Server DB via Windows auth. Do not mock the DB session.
- Write operations in tests must be wrapped in a transaction that is rolled back after the test.
- Frontend automated tests: not yet in place (future work).

## Known Architecture Notes & Gotchas
- `PianoUtilizzoManager.jsx`: older component superseded by `PianoUtilizzoPage.jsx`. Do not add features to it; it is pending removal.
- Campaign year is parameterized end-to-end: `get_check_partite_status(db, rs_id, anno)` and the PU list CRUD take an `anno` arg; `PartitePage` has a "Campagna" selector populated from `/ragioni-sociali/{id}/anni` (distinct years with data), defaulting to the most recent. When `anno` is omitted the backend falls back to MAX(anno) then current year. Do not reintroduce hardcoded years.
- `main.py` previously had a duplicate `app = FastAPI()` call (line 20 overwrote line 18 with lifespan). Fixed — do not reintroduce.
- `TableDataPage.jsx` (Admin view) resolves FK columns to human-readable labels via FK hints returned by the `/tables/{schema}/{table}/schema/` endpoint.
- **API auth**: `main.py` has an `X-API-Key` middleware. Every request needs the header to equal `API_KEY` (backend `.env`) except `OPTIONS` and the docs/health paths. The frontend sends it from `VITE_API_KEY` (`frontend/.env`), which must match. If `API_KEY` is unset the API runs open with a startup warning. Backend tests authenticate via the `client` fixture in `conftest.py`. This is defense-in-depth behind Tailscale, not a substitute for it (the key ships in the SPA bundle).
- **Secrets**: never hardcode credentials. `backend/.env`, `frontend/.env`, and the root `.env` are gitignored; `docker-compose.yml` reads secrets via `${VAR}` interpolation from the root `.env`. `.bacpac`/`.xlsx`/`.csv` (client PII) are gitignored — never commit client data.
- **Public mirror**: the public GitHub repo is a history-free mirror built by `scripts/publish-public.sh`, which pushes HEAD as one snapshot commit and leaves out its `PRIVATE_PATHS`. Real contacts, client names and personal data go only in those paths — e.g. `backend/smtp/private.py` (staff BCC, test redirect, broker referenti, email signature), which `smtp/config.py` imports with public fallbacks. Never put them in regular files. Browser origins come from `CORS_ORIGINS` (comma-separated), never hardcoded.
- **DB init / demo data**: `python -m db.init_db` (run by the backend container before uvicorn) creates the database, applies `db/db.sql` and loads `db/seed_demo.py`, only when the `core` schema is missing. `db.sql` is the DDL source of truth — the ORM models can't create the schema (`Documento.codice_ministeriale` has an ORM-only FK to a non-unique column), and ORM inserts with an explicit `comune`/`lifecycle` integer PK make SQLAlchemy emit `SET IDENTITY_INSERT`, which fails on those non-identity columns.
- **OCR / scanned PDFs**: `pdf_parser.py` extracts each page's text once via `extract_page_texts`, falling back to Tesseract OCR (`pytesseract`) for pages with no text layer, with OSD orientation correction for rotated scans. `pytesseract` is imported defensively (digital PDFs still work if it's missing). Needs the Tesseract binary + `ita` language pack installed; configurable via `TESSERACT_CMD`/`OCR_LANG`/`OCR_DPI`. Unreadable files raise `PdfTextExtractionError` → the upload route returns 422 with an Italian message shown in the Snackbar. OCR text is noisier, so the dettagliato regexes may match scans imperfectly.
