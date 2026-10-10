from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response

from app.schemas import CertificateRequest
from app.services.bulk_processor import (
    BulkInputError,
    generate_bulk_zip,
    parse_csv,
    parse_json,
)
from app.services.certificate_generator import generate_certificate_pdf

router = APIRouter(prefix="/certificates", tags=["Certificates"])

MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 2 MB


@router.post("/single", summary="Generate a single certificate PDF")
def create_single_certificate(payload: CertificateRequest):
    pdf_bytes = generate_certificate_pdf(payload.name, payload.course, payload.date)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="certificate.pdf"'},
    )


@router.post("/bulk", summary="Generate certificates in bulk from a CSV or JSON file")
async def create_bulk_certificates(file: UploadFile = File(...)):
    filename = (file.filename or "").lower()
    if filename.endswith(".csv"):
        parser = parse_csv
    elif filename.endswith(".json"):
        parser = parse_json
    else:
        raise HTTPException(status_code=400, detail="Only .csv or .json files are supported.")

    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 2 MB.")

    try:
        rows = parser(content)
        zip_bytes, report = await run_in_threadpool(generate_bulk_zip, rows)
    except BulkInputError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if report["success"] == 0:
        raise HTTPException(
            status_code=422,
            detail={"message": "No valid rows found.", "failed": report["failed"]},
        )

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": 'attachment; filename="certificates.zip"',
            "X-Total-Count": str(report["total"]),
            "X-Success-Count": str(report["success"]),
            "X-Failed-Count": str(len(report["failed"])),
        },
    )