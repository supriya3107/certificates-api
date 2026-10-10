import io
import json
import zipfile

CSV_MIXED = (
    "name,course,date\n"
    "pasupula supriya,Python Programming,2026-10-10\n"
    "Priya Sharma,Data Structures,2026-10-11\n"
    ",Web Development,not-a-date\n"
)

CSV_ALL_BAD = "name,course,date\n,,\n,Web,xyz\n"

JSON_VALID = [
    {"name": "pasupula supriya", "course": "Python", "date": "2026-10-10"},
    {"name": "Priya Sharma", "course": "DSA", "date": "2026-10-11"},
]


def upload(client, filename, content, content_type="text/csv"):
    return client.post(
        "/certificates/bulk",
        files={"file": (filename, content, content_type)},
    )


def test_bulk_csv_partial_success(client):
    response = upload(client, "certs.csv", CSV_MIXED)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert response.headers["x-total-count"] == "3"
    assert response.headers["x-success-count"] == "2"
    assert response.headers["x-failed-count"] == "1"

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        names = zf.namelist()
        pdfs = [n for n in names if n.endswith(".pdf")]
        assert len(pdfs) == 2
        assert "report.json" in names
        report = json.loads(zf.read("report.json"))
        assert report["failed"][0]["row"] == 3


def test_bulk_json(client):
    response = upload(
        client, "certs.json", json.dumps(JSON_VALID), "application/json"
    )
    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        assert len([n for n in zf.namelist() if n.endswith(".pdf")]) == 2


def test_bulk_json_with_wrapper_object(client):
    body = json.dumps({"certificates": JSON_VALID})
    response = upload(client, "certs.json", body, "application/json")
    assert response.status_code == 200


def test_bulk_unsupported_file_type(client):
    response = upload(client, "certs.txt", "hello", "text/plain")
    assert response.status_code == 400


def test_bulk_csv_missing_column(client):
    response = upload(client, "certs.csv", "name,course\nRavi,Python\n")
    assert response.status_code == 400
    assert "date" in response.json()["detail"]


def test_bulk_all_rows_invalid(client):
    response = upload(client, "certs.csv", CSV_ALL_BAD)
    assert response.status_code == 422


def test_bulk_invalid_json(client):
    response = upload(client, "certs.json", "{not valid json", "application/json")
    assert response.status_code == 400


def test_bulk_file_too_large(client):
    big = "name,course,date\n" + ("Ravi,Python,2026-10-10\n" * 120000)
    response = upload(client, "big.csv", big)
    assert response.status_code == 413


def test_bulk_empty_csv(client):
    response = upload(client, "empty.csv", "")
    assert response.status_code == 400