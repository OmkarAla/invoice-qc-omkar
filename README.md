### Full-stack Invoice Quality Control system that extracts, validates, and visually reviews B2B invoices from PDFs.

### Features:
• Real-world PDF parsing (pdfplumber + custom German invoice heuristics)
• Pydantic-based schema + business rule validation
• Professional React + Tailwind web console
• FastAPI backend with file upload
• Fully containerized (Docker Compose + multi-stage builds)

### Run with one command: 
```bash
docker compose up --build
```