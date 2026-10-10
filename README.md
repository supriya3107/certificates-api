# Bulk Certificate Generator API

**Author:** Pasupula Supriya | **GitHub:** [supriya3107](https://github.com/supriya3107)

A REST API built with **FastAPI** that generates certificates as PDFs, either one at a time or in bulk from a CSV/JSON file (returned as a ZIP).

## Features

- Generate a single certificate PDF from JSON input
- Bulk generation from a CSV or JSON upload, returned as a ZIP file
- Per-row validation: invalid rows are skipped and listed in `report.json` inside the ZIP
- File type and size validation (max 2 MB, max 1000 rows)
- Safe output filenames (protects against path traversal)
- Automatic API docs (Swagger UI)
- Pytest test suite and Dockerfile

## Tech Stack

Python, FastAPI, Pydantic, ReportLab, Pytest

## Project Structure

```
certificates-api/
├── app/
│   ├── main.py                       # App entry point
│   ├── schemas.py                    # Request validation
│   ├── routes/certificates.py        # API endpoints
│   ├── services/
│   │   ├── certificate_generator.py  # PDF drawing
│   │   └── bulk_processor.py         # CSV/JSON parsing + ZIP creation
│   └── utils/file_utils.py           # Filename sanitizing
├── tests/
├── sample_data/
├── Dockerfile
├── requirements.txt
└── README.md
```

## Setup

```bash
git clone https://github.com/supriya3107/certificates-api.git
cd certificates-api
python -m venv venv
```

Activate the virtual environment:

```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

Install dependencies and run the server:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --reload-dir app
```

Open http://127.0.0.1:8000/docs for the interactive API docs.

## Run with Docker

```bash
docker build -t certificate-api .
docker run -p 8000:8000 certificate-api
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/certificates/single` | Generate one certificate (PDF) |
| POST | `/certificates/bulk` | Generate many certificates (ZIP) |

### POST /certificates/single

```bash
curl -X POST http://127.0.0.1:8000/certificates/single \
  -H "Content-Type: application/json" \
  -d '{"name":"Pasupula Supriya","course":"Python Programming","date":"2026-10-10"}' \
  --output certificate.pdf
```

### POST /certificates/bulk

Upload a `.csv` or `.json` file.

```bash
curl -X POST http://127.0.0.1:8000/certificates/bulk \
  -F "file=@sample_data/certificates.csv" \
  --output certificates.zip
```

**CSV format**

```csv
name,course,date
Pasupula Supriya,Python Programming,2026-10-10
Priya Sharma,Data Structures,2026-10-11
```

**JSON format** (a list, or an object with a `certificates` list)

```json
[
  {"name": "Pasupula Supriya", "course": "Python Programming", "date": "2026-10-10"}
]
```

**Response:** a ZIP containing one PDF per valid row plus `report.json`.
Response headers `X-Total-Count`, `X-Success-Count` and `X-Failed-Count` summarize the result.

### Error responses

| Status | Meaning |
|--------|---------|
| 400 | Unsupported file type, invalid/empty file, missing columns |
| 413 | File larger than 2 MB |
| 422 | Invalid input (single), or every row invalid (bulk) |

## Running Tests

```bash
pytest -v
```

## Design Decisions

- **Partial success for bulk:** one bad row should not fail the whole batch, so invalid rows are skipped and reported in `report.json`.
- **In-memory generation:** PDFs and ZIPs are built in memory, so nothing is stored on the server.
- **Limits:** 2 MB upload size and 1000 rows to prevent abuse.
- **ReportLab** is used for PDF generation because it is pure Python and needs no system dependencies.

