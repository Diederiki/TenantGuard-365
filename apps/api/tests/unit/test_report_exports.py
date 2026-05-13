"""Smoke tests for report exporters: CSV / HTML / XLSX / PDF produce valid bodies."""

from __future__ import annotations

import io
import zipfile

from app.reports import ColumnSpec
from app.reports.export import export, export_csv, export_html, export_pdf, export_xlsx

COLUMNS = [
    ColumnSpec("name", "Name", 20),
    ColumnSpec("age", "Age", 8),
]
ROWS = [
    {"name": "alice", "age": 30},
    {"name": "bob", "age": None},
]


def test_csv_produces_header_and_rows() -> None:
    body = export_csv(COLUMNS, ROWS)
    text = body.decode("utf-8")
    lines = text.strip().splitlines()
    assert lines[0] == "Name,Age"
    assert lines[1] == "alice,30"
    assert lines[2] == "bob,"


def test_html_escapes_and_wraps_in_table() -> None:
    rows = [{"name": "<script>", "age": 1}]
    body = export_html("My report", COLUMNS, rows).decode("utf-8")
    assert "&lt;script&gt;" in body
    assert "<table" in body
    assert "</table>" in body


def test_xlsx_is_a_valid_zip_with_workbook() -> None:
    body = export_xlsx("Title", COLUMNS, ROWS)
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        names = z.namelist()
        assert "xl/workbook.xml" in names
        assert "xl/worksheets/sheet1.xml" in names
        sheet = z.read("xl/worksheets/sheet1.xml").decode("utf-8")
        assert "alice" in sheet
        assert "bob" in sheet
        assert "Name" in sheet


def test_pdf_starts_with_signature_and_ends_with_eof() -> None:
    body = export_pdf("R", COLUMNS, ROWS)
    assert body.startswith(b"%PDF-")
    assert body.rstrip().endswith(b"%%EOF")


def test_export_dispatch_returns_content_type() -> None:
    body, ct = export("csv", title="t", columns=COLUMNS, rows=ROWS)
    assert ct.startswith("text/csv")
    assert body
    body, ct = export("html", title="t", columns=COLUMNS, rows=ROWS)
    assert ct.startswith("text/html")
    body, ct = export("xlsx", title="t", columns=COLUMNS, rows=ROWS)
    assert "spreadsheetml" in ct
    body, ct = export("pdf", title="t", columns=COLUMNS, rows=ROWS)
    assert ct == "application/pdf"
