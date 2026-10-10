from fastapi import FastAPI

from app.routes import certificates

app = FastAPI(
    title="Bulk Certificate Generator API",
    description="Generate single or bulk certificates as PDFs.",
    version="1.0.0",
)

app.include_router(certificates.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}