"""Report export formatters: CSV, HTML, XLSX (stdlib OOXML), PDF (stdlib)."""

from __future__ import annotations

import csv
import html
import io
from collections.abc import Iterable
from typing import Any

from app.reports import ColumnSpec


def _stringify(v: object) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def export_csv(columns: list[ColumnSpec], rows: Iterable[dict[str, Any]]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow([c.label for c in columns])
    for r in rows:
        writer.writerow([_stringify(r.get(c.key)) for c in columns])
    return buf.getvalue().encode("utf-8")


def export_html(
    title: str, columns: list[ColumnSpec], rows: Iterable[dict[str, Any]]
) -> bytes:
    head = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>{html.escape(title)}</title>"
        "<style>"
        "body{font-family:ui-sans-serif,system-ui,sans-serif;color:#0f172a;}"
        "h1{font-size:18px;margin:0 0 12px;}"
        "table{border-collapse:collapse;width:100%;font-size:13px;}"
        "th,td{text-align:left;padding:6px 10px;border-bottom:1px solid #e5e7eb;}"
        "thead{background:#f1f5f9;}"
        "</style></head><body>"
        f"<h1>{html.escape(title)}</h1><table><thead><tr>"
    )
    out = [head]
    for c in columns:
        out.append(f"<th>{html.escape(c.label)}</th>")
    out.append("</tr></thead><tbody>")
    for r in rows:
        out.append("<tr>")
        for c in columns:
            out.append(f"<td>{html.escape(_stringify(r.get(c.key)))}</td>")
        out.append("</tr>")
    out.append("</tbody></table></body></html>")
    return "".join(out).encode("utf-8")


def export_xlsx(
    title: str, columns: list[ColumnSpec], rows: Iterable[dict[str, Any]]
) -> bytes:
    """Minimal XLSX writer via the standard zipfile module.

    Avoids a hard dependency on openpyxl. Produces a valid OOXML workbook
    with one sheet, a frozen header row, and inline strings.
    """
    import zipfile
    from xml.sax.saxutils import escape as xescape

    materialized = list(rows)

    def cell(col_letter: str, row_idx: int, value: object) -> str:
        text = xescape(_stringify(value))
        return (
            f'<c r="{col_letter}{row_idx}" t="inlineStr">'
            f"<is><t xml:space='preserve'>{text}</t></is></c>"
        )

    def col_letter(n: int) -> str:
        s = ""
        while n > 0:
            n, r = divmod(n - 1, 26)
            s = chr(65 + r) + s
        return s

    sheet_rows = [
        '<row r="1">'
        + "".join(cell(col_letter(i + 1), 1, c.label) for i, c in enumerate(columns))
        + "</row>"
    ]
    for ri, row in enumerate(materialized, start=2):
        sheet_rows.append(
            f'<row r="{ri}">'
            + "".join(
                cell(col_letter(i + 1), ri, row.get(c.key))
                for i, c in enumerate(columns)
            )
            + "</row>"
        )

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetViews><sheetView workbookViewId="0">'
        '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
        '</sheetView></sheetViews>'
        "<sheetData>" + "".join(sheet_rows) + "</sheetData></worksheet>"
    )

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Report" sheetId="1" r:id="rId1"/></sheets></workbook>'
    )
    rels_xml = (        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    )
    workbook_rels_xml = (        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        "</Relationships>"
    )
    content_types_xml = (        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        "</Types>"
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types_xml)
        z.writestr("_rels/.rels", rels_xml)
        z.writestr("xl/workbook.xml", workbook_xml)
        z.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        z.writestr("xl/worksheets/sheet1.xml", sheet_xml)
    return buf.getvalue()


def export_pdf(
    title: str, columns: list[ColumnSpec], rows: Iterable[dict[str, Any]]
) -> bytes:
    """Minimal single-page PDF — a real Phase 10 build swaps this for WeasyPrint.

    Generates a single-page text-only PDF using just stdlib so we don't pull a
    heavy dependency. Not paginated. Use HTML/CSV/XLSX for now.
    """
    lines = [title, "=" * len(title), ""]
    header = " | ".join(c.label for c in columns)
    lines.append(header)
    lines.append("-" * min(len(header), 100))
    for r in rows:
        lines.append(" | ".join(_stringify(r.get(c.key)) for c in columns))
    text = "\n".join(lines)

    text_bytes = text.encode("utf-8")
    # Very small PDF: one page with embedded text via Tj. Not pretty, but valid.
    pdf_text = (
        "BT /F1 9 Tf 36 800 Td "
        + " ".join(
            f"({line.replace('(', '\\(').replace(')', '\\)')}) Tj T*"
            for line in text.split("\n")[:80]
        )
        + " ET"
    )
    objs: list[bytes] = []
    objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objs.append(b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>")
    objs.append(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
    )
    stream_body = pdf_text.encode("latin-1", errors="replace")
    objs.append(
        b"<< /Length " + str(len(stream_body)).encode("ascii") + b" >>\nstream\n"
        + stream_body
        + b"\nendstream"
    )
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")

    buf = io.BytesIO()
    buf.write(b"%PDF-1.4\n")
    offsets = [0]
    for i, body in enumerate(objs, start=1):
        offsets.append(buf.tell())
        buf.write(f"{i} 0 obj\n".encode("ascii"))
        buf.write(body)
        buf.write(b"\nendobj\n")
    xref_pos = buf.tell()
    buf.write(b"xref\n")
    buf.write(f"0 {len(objs) + 1}\n".encode("ascii"))
    buf.write(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        buf.write(f"{off:010d} 00000 n \n".encode("ascii"))
    buf.write(b"trailer\n")
    buf.write(f"<< /Size {len(objs) + 1} /Root 1 0 R >>\n".encode("ascii"))
    buf.write(b"startxref\n")
    buf.write(f"{xref_pos}\n".encode("ascii"))
    buf.write(b"%%EOF")
    _ = text_bytes
    return buf.getvalue()


def export(
    fmt: str,
    *,
    title: str,
    columns: list[ColumnSpec],
    rows: Iterable[dict[str, Any]],
) -> tuple[bytes, str]:
    """Return (body, content_type) for the chosen format."""
    rows_list = list(rows)
    if fmt == "csv":
        return export_csv(columns, rows_list), "text/csv; charset=utf-8"
    if fmt == "html":
        return export_html(title, columns, rows_list), "text/html; charset=utf-8"
    if fmt == "xlsx":
        return (
            export_xlsx(title, columns, rows_list),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    if fmt == "pdf":
        return export_pdf(title, columns, rows_list), "application/pdf"
    raise ValueError(f"unknown format: {fmt}")
