"""Vercel entrypoint: FastAPI application.

Vercel's FastAPI preset looks for `main.py` at the project root and expects an
`app` object. The app is defined here rather than imported from `api/` so the
function bundle has no dependency on the serverless directory convention.
`api/main.py` re-exports it for projects that use the "Other" preset.
"""

from typing import List
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(
    title="Invoice QC Service",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/extract-and-validate")
@app.post("/api/extract-and-validate")
async def process(files: List[UploadFile] = File(...)):
    # Imported lazily so /health stays up even if the package bundle is broken.
    from invoice_qc.extractor import extract_from_pdf
    from invoice_qc.validator import validate_invoices

    invoices = []
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)

        inv = extract_from_pdf(tmp_path)
        inv.source_file = file.filename or tmp_path.name
        invoices.append(inv)
        tmp_path.unlink()

    results = validate_invoices(invoices)

    return {
        "total": len(invoices),
        "valid": sum(1 for r in results if r.is_valid),
        "results": [
            {
                "invoice_number": r.invoice.invoice_number,
                "is_valid": r.is_valid,
                "errors": r.errors,
            }
            for r in results
        ],
        "invoices": [i.model_dump() for i in invoices],
    }
