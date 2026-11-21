# Invoice QC

Extract, validate and review German B2B invoices from PDFs — FastAPI service, React console, one Docker Compose command.

> Demo project. The parser is heuristic and tuned for German `Bestellung` / invoice layouts, not a general document-AI product.

## What it does

Upload one or more PDFs. The service extracts the header fields and line items, validates them against a Pydantic schema plus business rules (totals, tax, dates, missing fields), and returns a per-invoice pass/fail result with the exact errors. The React console shows the parsed values next to the errors so a reviewer can see what the machine saw.

```
PDF upload → pdfplumber + German-layout heuristics → Pydantic schema
           → business rules (totals, tax, dates)     → JSON result + review UI
```

## API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/extract-and-validate` | Multipart upload (`files`); returns totals, validity, errors and the parsed invoices |

Example response (trimmed):

```json
{
  "total": 1,
  "valid": 1,
  "results": [{ "invoice_number": "AUFNR34343", "is_valid": true, "errors": [] }],
  "invoices": [{ "invoice_number": "AUFNR34343", "invoice_date": "2024-05-22", "total_amount": 1234.5 }]
}
```

## Run it

Requires Docker Desktop.

```bash
docker compose up --build
```

- Console: <http://localhost:5173>
- API: <http://localhost:8000/docs>

Without Docker:

```bash
python -m venv .venv && source .venv/Scripts/activate   # Windows
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

cd frontend && npm install && npm run dev
```

`sample_pdfs/` has five German invoices you can drag in.

## Tests

There is no automated suite yet. Validation covers required fields, negative totals, totals reconciliation (`gross = net + tax`), line-item sums, date ordering and duplicate invoice numbers; the five sample PDFs are the current regression set. An automated pytest suite is the next piece of work.

## Deploy

One Vercel project, two services, configured in `vercel.json`:

| Service | Root | Framework | Public path |
|---|---|---|---|
| `api` | `.` | FastAPI | `/api/*` and `/health` |
| `web` | `frontend` | Vite | everything else |

The console calls `/api` on the same origin, so the browser is the caller and no cross-origin setup is needed. `docker compose` and `Dockerfile.backend` remain the portable path for Render, Railway or Fly.

## Limitations

- First page only; multi-page invoices with line items continuing onto page two are not handled.
- Heuristics are German-specific (`Bestellung`, comma decimal separators). Other locales will parse poorly.
- No OCR — scanned PDFs need a text layer.
- In-memory processing, no persistence: results are not stored between requests.
