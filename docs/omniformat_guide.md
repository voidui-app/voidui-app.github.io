# Omniformat Guide

Omniformat is VoidUI's rich-content rendering layer. Your daemon publishes
items with a `format` and a `url`; the player downloads, parses and renders
them natively in the right-hand pane — no extra viewer software, no plugins.

---

## How it works

An item in the catalog selects its renderer through the `format` field:

```json
{
  "id": "rfc",
  "title": "RFC 9110 — HTTP Semantics.pdf",
  "format": "pdf",
  "url": "https://www.rfc-editor.org/rfc/rfc9110.pdf"
}
```

When the item is selected, the player:

1. **Downloads** the URL through its own backend (no CORS, no CSP, no page
   sandbox limits) and writes it into the app cache.
2. **Parses** it in the page where the format calls for it — a `.xlsx` is a
   ZIP of XML, a `.docx` is a ZIP of XML, and the player reads both itself.
3. **Renders** it with the built-in renderer for that format.

Your daemon never reads a file and never base64-encodes a spreadsheet. A
`url` is all it takes.

---

## Supported formats

| `format` | Source | Rendered as |
|----------|--------|-------------|
| `pdf` | URL | The webview's own PDF viewer, on the locally cached copy. |
| `docx` | URL or inline | A paper-style document: headings, paragraphs, lists, tables. |
| `xlsx` | URL or inline | A grid with a tab per sheet and a filterable header row. |
| `csv` | URL or inline | A filterable, scrollable data table. |
| `json` | URL or inline | A syntax-highlighted tree with a **Copy** button. |
| `m3u8` | URL | An HTML5 video player (HLS). |
| `video` | URL | An HTML5 video player (MP4, WebM, OGG). |
| `audio` | URL | A styled HTML5 audio player card. |
| `html` | inline | The item's `content`, rendered as HTML. |

---

### `pdf` — PDF documents

```json
{ "id": "rfc", "title": "RFC 9110", "format": "pdf",
  "url": "https://www.rfc-editor.org/rfc/rfc9110.pdf" }
```

The file is downloaded to the cache and displayed in the webview's native PDF
viewer, so paging, zoom and text selection all work.

---

### `docx` — Word documents

```json
{ "id": "spec", "title": "Specification", "format": "docx",
  "url": "https://example.com/spec.docx" }
```

The player unpacks the OOXML and reads `word/document.xml` directly. It
renders:

- **Headings** — Word's built-in `Heading 1`–`Heading 6` and `Title` styles
  become `<h1>`–`<h6>`.
- **Paragraphs** — runs are concatenated, with `<w:tab/>` and `<w:br/>` read
  as whitespace.
- **Lists** — paragraphs with a `<w:numPr>` become a bulleted list.
- **Tables** — `<w:tbl>` becomes an HTML table, with cells padded so the grid
  stays square.

Everything read out of the archive is treated as untrusted text and is escaped
before it reaches the DOM.

---

### `xlsx` — Excel workbooks

```json
{ "id": "sales", "title": "Sales Report", "format": "xlsx",
  "url": "https://example.com/sales.xlsx" }
```

The player unpacks the workbook and reads the parts that affect displayed
cells:

- `xl/sharedStrings.xml` — the shared string table, including rich-text runs.
- `xl/workbook.xml` — the sheet list, resolved through
  `xl/_rels/workbook.xml.rels` to each worksheet part.
- `xl/worksheets/sheetN.xml` — the rows and cells.

Cell types are handled: shared strings (`t="s"`), inline strings
(`t="inlineStr"`), booleans (`t="b"`) and errors (`t="e"`). Missing cells
are preserved as gaps so the grid keeps its shape.

---

### `csv` — Comma-separated values

```json
{ "id": "stocks", "title": "Stock Prices", "format": "csv",
  "url": "https://example.com/stocks.csv" }
```

Parsed in the page and rendered as a filterable table with a row count.

---

### `json` — JSON data

```json
{ "id": "config", "title": "Configuration", "format": "json",
  "url": "https://example.com/config.json" }
```

Rendered as a syntax-highlighted, collapsible tree, with a **Copy** button.

---

### `m3u8`, `video`, `audio` — media

```json
{ "id": "stream", "title": "Live Stream", "format": "m3u8",
  "url": "https://example.com/stream.m3u8",
  "poster": "https://example.com/thumb.jpg" }
```

Media is handed straight to the browser — it is not downloaded by the backend
first, so the player can stream it.

> **CORS applies to media.** Every other format is fetched by the player's own
> backend, which ignores cross-origin rules. Media is not: the browser requests
> the playlist and the segments itself, so the host has to send
> `Access-Control-Allow-Origin`. If a stream plays in a browser tab but not in
> VoidUI, that header is the reason.

---

## Inline data

For small payloads you can skip the file entirely and put the data in the
item. The player prefers inline fields and only downloads when one is missing.

| Format | Inline field | Shape |
|--------|--------------|-------|
| `csv` | `csv_data` | The raw CSV text. |
| `json` | `json_data` | The parsed object. |
| `xlsx` | `sheets` | `[{"name": "Sheet1", "rows": [["A1", "B1"], ["A2", "B2"]]}]` |
| `docx` | `content` | An HTML string. |
| `html` | `content` | An HTML string. |

You can set **both** an inline field and a `url`. The player uses the inline
data and keeps the URL for the "Open File" action.

---

## Serving files from your own machine

Point a `url` at your own daemon and the player will fetch it:

```python
"url": "http://127.0.0.1:8787/file/report.pdf"
```

The player requests it with the same `X-API-Key` header it uses for
`/api/data`, so the same check applies. Serve the raw bytes with the right
content type — the player does not care about the filename or the extension.

**Serving a local file from Python** (Flask's `send_file`):

```python
@app.route("/file/<path:filename>")
def serve_file(filename):
    safe = os.path.basename(filename)          # no path traversal
    path = os.path.join(FILES_DIR, safe)
    if not os.path.isfile(path):
        return {"error": "Not found"}, 404
    return send_file(path)
```

---

## Picking a format

The `format` field decides the renderer. When you generate items from
filenames, a small map is usually enough:

```python
import os

FORMAT_BY_EXT = {
    "pdf": "pdf",
    "docx": "docx", "doc": "docx",
    "xlsx": "xlsx", "xls": "xlsx",
    "csv": "csv",
    "json": "json",
    "m3u8": "m3u8",
    "mp4": "video", "webm": "video",
    "mp3": "audio", "ogg": "audio", "wav": "audio",
}

def detect_format(filename):
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    return FORMAT_BY_EXT.get(ext, "json")
```

---

## Live example

The **Omniformat Vault** example daemon (`examples/03_multiformat_vault/`)
demonstrates every format against real, publicly reachable documents. Run it:

```bash
python examples/03_multiformat_vault/app.py --port 8789
```

Then connect VoidUI to `http://127.0.0.1:8789` with the key
`default-dev-key` (or pick the **Omniformat Vault** preset in Settings).

That daemon publishes URLs only — every item is a `format` plus a `url`, and
the player does the downloading, the parsing and the rendering.
