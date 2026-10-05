# Eureka

Management platform for an Italian agricultural insurance broker: it turns farmers' *Piano di Utilizzo* PDFs into insurance units (*partite*) and hail-insurance quotes (*preventivi*). The UI is in Italian.

## Quick start (Docker)

```bash
cp .env.example .env   # then change MSSQL_SA_PASSWORD and API_KEY
docker compose up --build
```

Open http://localhost:3000 (API docs at http://localhost:8000/docs). The first start creates the `eureka` database from `backend/db/db.sql` and loads synthetic demo data — fictitious farms, rates and prices for the current year — so every page has something to show. Later starts leave the database untouched; `docker compose down -v` wipes it.

## Local development

- **Backend** (Python 3.13, SQL Server + ODBC driver): in `backend/`, copy `.env.example` to `.env`, `pip install -r requirements.txt`, `python -m db.init_db` (creates the database in `DATABASE_URL` with demo data, if missing), then `uvicorn main:app --reload`.
- **Frontend**: in `frontend/`, copy `.env.example` to `.env`, `npm install`, `npm run dev` (http://localhost:5173).
- **Tests**: `cd backend && pytest` (integration tests need the database).

---

This documentation provides a comprehensive overview of the **Grandine (Hail/Multi-risk) Insurance Business** as implemented in the Eureka platform. It covers the logic from land registry data to the final insurance quotation.

---

# 🌾 Grandine Insurance Business Logic & Workflow

## 1. Executive Summary
The "Grandine" business manages subsidized agricultural insurance in Italy. Farmers protect their crops against atmospheric adverse events (hail, frost, drought, etc.). The system relies on official documents (Piano di Utilizzo) to determine exactly what land is being cultivated, which crops are present, and how they should be grouped into insurance units called **Partite**.
The app is meant to deal (in the future) with all the types of insurance, but for the moment it is focused on agricoltural sector. The business flow is the following:
1. First meeting with the client where we understand their needs and we discuss the market news and eventually we get their first idea of what they will produce (usuallu between February and March)
2. once the Condifesa and Insurance companies release their respectively price table and tasso the analytical work (making a quotation can be done), these happen in different stages aka not all at once, and each compagnia and condifesa has a different template.
3. Eureka comes up with a preventivo (quotation) to be sent to the client in which there are different combination of garanzie and companies 
4. FInally the preventivo is either accepted or rejected, in case its accepted the request of copertura needs to be sent to the intermidiary/company for confirmation, and only once that is also gone through, we need to build the certificato (contract) which implies extracting the piano di utilizzo for a perfect match between: reality of the crops, declaration of the farmer (Piano di Utilizzo) and then eventually the insurance certificate
5. The certificate needs to be signed
6. In case of damage there's also a declaration to be made and communication to intermediary or company via their channel.
7. At the end of the year Eureka must have the overall view of its portfolio, performance and revenues thanks to which it needs to reconcile to accounting

---

## 2. Key Stakeholders
*   **Ragione Sociale (The Farmer/Company):** The entity owning or managing the land.
*   **Condifesa (The Consortium):** A regional body that aggregates farmers to negotiate better rates with insurance companies and manages government subsidies.
*   **AVEPA / National Bodies:** Official agencies that track land usage and provide the "Plan of Use" (Piano di Utilizzo).
*   **Eureka Platform:** The software that digitizes the PDF documents, matches crops to the database, and calculates the insurance "Partite."

---

## 3. The Technical Foundation: Product & Land Data

### 3.1 The Prodotto (Crop)
In the database, a `Prodotto` is more than just a name (e.g., "Wheat"). It is identified by several layers of coding:
*   **Nome/Dettaglio:** The common name and specific variety (e.g., "Wheat" - "Bologna").
*   **Codice Ministeriale:** A 4-digit code used for government reporting.
*   **Codice AVEPA:** A unique identifier for the crop type.
*   **Codice AVEPA Dettagliato:** A 19-digit string in the format `ddd-ddd-ddd-ddd-ddd` (e.g., `002-011-000-000-392`) that identifies the exact crop, category, and usage.

### 3.2 Land Registry (Catasto)
Land is identified by:
*   **Comune:** The municipality.
*   **Foglio (Sheet):** The map section.
*   **Particella (Plot):** The specific piece of land.
*   **Subalterno (Sub-plot):** An optional further division.

---


---

## 4. Phase 1: The "Piano di Utilizzo" (Plan of Use)
The starting point of any insurance policy is the **Piano di Utilizzo (PU)**. This is a PDF document provided by the farmer. There are two main types of PU:

### A. Riepilogativo (Summary)
*   **Granularity:** Low.
*   **Content:** Grouped by Municipality and Crop.
*   **Format:** `COMUNE(PR) - CROP NAME - AREA`.
*   **Use Case:** Quick quotes where specific plot numbers aren't required.

### B. Dettagliato (Detailed)
*   **Granularity:** High.
*   **Content:** Every single cadastral plot (`Foglio`/`Particella`) is listed individually with its specific `Codice AVEPA`.
*   **Use Case:** Formal insurance policies and "Partite" generation.

---

## 5. Phase 2: The Digital Extraction (PDF Parsing)
Because these documents are PDFs, Eureka uses a Python-based parser (`pdfplumber`) to convert them into structured data.

### 5.1 The Normalization Challenge
A major business hurdle is the inconsistency of text. 
*   **Accents:** A municipality might be "Arquà Polesine" in the DB but "ARQUA` POLESINE" in the PDF.
*   **Regex Strategy:** The parser uses "Brute Force Normalization"—removing all spaces, backticks, and accents to compare strings in their purest alphanumeric form (e.g., `ARQUAPOLESINE`).

### 5.2 The Matching Logic
1.  **Direct ID Match:** If a 19-digit AVEPA code is found, the system looks for an exact match in the `grandine.prodotto` table.
2.  **Fuzzy/Weighted Match:** If only text is available, the system uses "Segmented Weighting." It prioritizes the **Crop Type** (80% weight) and then the **Variety** (20% weight), applying penalties to prevent common errors (e.g., confusing "Wheat" with "Corn").

---

### 5.3 The Pre-Sorting Workflow
To ensure speed and accuracy, Eureka uses a **Pre-Sorting Modal**:
1.  User uploads a 200-line PDF.
2.  The backend identifies **unique** products (e.g., all 50 rows of "Wheat").
3.  The user validates the mapping **once** for each unique type.
4.  The system propagates those choices to all 200 rows instantly.

---

## 6. Phase 3: "Partite" Generation
Insurance companies do not insure 500 individual plots. They group them into **Partite**.

### 6.1 Logic of a "Partita"
A Partita is a unique combination of:
**Municipality + Crop (Prodotto) + Insurance Number.**

### 6.2 The Algorithm
1.  Take all rows from the `Piano Utilizzo Dettagliato`.
2.  Group all rows that have the same Municipality and the same Product.
3.  Assign them a `Numero Partita`.
4.  If a single plot contains multiple crops, the algorithm "splits" the surface area accordingly.

### 6.3 User Overrides
The system generates a **Draft (Bozza)**. The user can manually edit the `Numero Partita` in the UI if they want to group terrains differently based on their unique experience with the client.

---

## 7. Phase 4: Persistence (Wipe & Replace)
Data is saved using a "Sync" strategy:
1.  When a user saves a new Plan of Use for Company X and Year 2025, the system **deletes all existing records** for that specific company and year.
2.  It then performs a **Bulk Insert** of the new data.
This ensures that the database is always a "mirror" of the latest uploaded document, preventing duplicate or orphaned rows.

---

## 8. Final Goal: The Quotation
Once the land and crops are digitized into Partite:
1.  **Prezzi (Prices):** The system fetches the official market prices per quintal.
2.  **Tassi (Rates):** The user selects an insurance company and an intermediary to apply specific percentage rates.
3.  **Quotation:** `Surface * Yield * Price * Rate = Premium (Premio)`.

---

## Summary of Eureka Features
| Feature | Business Value |
| :--- | :--- |
| **PDF Parsing** | Eliminates hours of manual data entry. |
| **Normalization** | Resolves naming mismatches automatically. |
| **Mapping Modal** | Ensures 100% accurate crop identification before saving. |
| **Partite Logic** | Transforms complex land registry data into simple insurance units. |
| **Bulk Sync** | Guarantees data integrity and "One Source of Truth". |