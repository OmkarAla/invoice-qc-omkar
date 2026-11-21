"""Serverless-convention entrypoint.

Re-exports the application from the project root so both Vercel layouts work:
the FastAPI preset (root `main.py`) and the "Other" preset (`api/main.py`).
"""

from main import app

__all__ = ["app"]
