from fastapi import FastAPI

app = FastAPI(
    title="Bulk Certificate Generator API",
    description="Generate single or bulk certificates as PDFs.",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}