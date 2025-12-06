# api/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
from pathlib import Path
from typing import List

from invoice_qc.extractor import extract_from_pdf
from invoice_qc.validator import validate_invoices

app = FastAPI(title="Invoice QC Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/extract-and-validate")
async def process(files: List[UploadFile] = File(...)):
    invoices = []
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)
        
        inv = extract_from_pdf(tmp_path)
        invoices.append(inv)
        tmp_path.unlink()

    results = validate_invoices(invoices)
    
    return {
        "total": len(invoices),
        "valid": sum(1 for r in results if r.is_valid),
        "results": [{"invoice_number": r.invoice.invoice_number, "is_valid": r.is_valid, "errors": r.errors} for r in results],
        "invoices": [i.model_dump() for i in invoices]
    }