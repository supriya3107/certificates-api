import csv
import io
import json
import zipfile

from pydantic import ValidationError

from app.schemas import CertificateRequest
from app.services.certificate_generator import generate_certificate_pdf
from app.utils.file_utils import safe_filename

MAX_ROWS = 1000
REQUIRED_COLUMNS = {"name", "course", "date"}


class BulkInputError(Exception):
    """Raised when the uploaded file itself is invalid."""


def parse_csv(content: bytes) -> list[dict]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise BulkInputError("CSV file must be UTF-8 encoded.")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise BulkInputError("CSV file is empty.")

    headers = {h.strip().lower() for h in reader.fieldnames if h}
    missing = REQUIRED_COLUMNS - headers
    if missing:
        raise BulkInputError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

    rows = []
    for row in reader:
        rows.append(
            {k.strip().lower(): (v or "") for k, v in row.items() if k is not None}
        )
    return rows


def parse_json(content: bytes) -> list[dict]:
    try:
        data = json.loads(content.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise BulkInputError("Invalid JSON file.")

    if isinstance(data, dict) and "certificates" in data:
        data = data["certificates"]
    if not isinstance(data, list):
        raise BulkInputError(
            "JSON must be a list of objects, or an object with a 'certificates' list."
        )
    return data


def generate_bulk_zip(rows: list) -> tuple[bytes, dict]:
    if not rows:
        raise BulkInputError("No rows found in the uploaded file.")
    if len(rows) > MAX_ROWS:
        raise BulkInputError(f"Too many rows. Maximum allowed is {MAX_ROWS}.")

    report = {"total": len(rows), "success": 0, "failed": []}
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for index, row in enumerate(rows, start=1):
            try:
                cert = CertificateRequest.model_validate(row)
            except ValidationError as exc:
                errors = "; ".join(
                    f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}"
                    for e in exc.errors()
                )
                report["failed"].append({"row": index, "errors": errors})
                continue

            pdf_bytes = generate_certificate_pdf(cert.name, cert.course, cert.date)
            zf.writestr(f"{index:04d}_{safe_filename(cert.name)}.pdf", pdf_bytes)
            report["success"] += 1

        zf.writestr("report.json", json.dumps(report, indent=2))

    return buffer.getvalue(), report