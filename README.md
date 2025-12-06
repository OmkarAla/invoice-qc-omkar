# Invoice QC Service – SUPEDIO Bestellung  
**Take-home Assignment – Software Engineer Intern (Data & Development)**  
**Candidate:** [Your Full Name] | December 2025  

![Demo](https://i.imgur.com/6jK8sL2.png) <!-- optional – replace with real screenshot or delete -->

A complete **Invoice Extraction & Quality Control** pipeline that:

1. Extracts structured data from German B2B “Bestellung” PDF invoices  
2. Validates against a realistic schema + business rules  
3. Exposes the logic via **CLI** and **FastAPI**  
4. Provides a **professional React + Tailwind** web console (full bonus)

---

## ✅ Completed Scope

| Part | Status | Details |
|------|--------|---------|
| Schema & Validation Design | ✔️ Done | Documented below + Pydantic models |
| PDF → JSON Extraction | ✔️ Done | Heuristics + table parsing for provided samples |
| Validation Core | ✔️ Done | Pydantic + custom business rules |
| CLI | ✔️ Done | `extract`, `validate`, `full-run` |
| HTTP API | ✔️ Done | FastAPI with `/extract-and-validate` |
| Bonus Fullstack QC Console | ✔️ Done | Drag & drop UI, live results |
| Dockerfile & pyproject.toml | ✔️ Done | Production-ready |

---

## 📄 Schema & Validation Design

### Invoice Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `invoice_number` | str | Yes | Example: `AUFNR123456` |
| `invoice_date` | date | Yes | From “vom DD.MM.YYYY” |
| `due_date` | date | No | Optional |
| `seller_name` | str | Yes | Extracted heuristically |
| `buyer_name` | str | Yes | From “Kundenanschrift” |
| `currency` | str | Yes | Always EUR for samples |
| `net_total` | float | Yes | Subtotal |
| `tax_amount` | float | Yes | 19% MwSt typical |
| `gross_total` | float | Yes | Final amount |
| `line_items` | list | Yes | description, qty, price, total |
| `source_file` | str | – | Traceability |

### Validation Rules

| Type | Rule | Purpose |
|------|------|---------|
| Completeness | Required fields + ≥1 line item | Minimum usable invoice |
| Format | Valid dates, amounts ≥ 0 | Prevent garbage |
| Business | `gross ≈ net + tax` | Verify accounting |
| Business | `sum(lines) ≈ net` | Reconciliation |
| Business | `qty × price ≈ line_total` | Line correctness |
| Anomaly | Prevent duplicate invoices | Avoid double-processing |

---


## 🏗️ Architecture
~~~
pdfs/
 └→ invoice_qc/extractor.py → Invoice (Pydantic)
                     ↓
               invoice_qc/validator.py → ValidationResult[]
                     ↓
   CLI (typer) ← FastAPI ←→ React + Tailwind UI
~~~

## 🚀 Quick Start

### Backend

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
uvicorn api.main:app --reload
```


### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker build -t invoice-qc .
docker run -p 8000:8000 invoice-qc
```


## Example

### CLI

```bash
python -m invoice_qc.cli full-run --pdf-dir samples --report report.json
```


