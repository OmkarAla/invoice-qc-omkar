"""Vercel FastAPI entrypoint.

Vercel's FastAPI preset looks for `main.py` at the project root and expects an
`app` object. The application itself lives in `api/main.py`, which also keeps
the `api/` serverless convention working when the project uses the "Other"
preset instead.
"""

from api.main import app

__all__ = ["app"]
