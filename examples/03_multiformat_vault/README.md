# Example 3: Omniformat Vault Daemon (3-Pane Mode)

Demonstrates VoidUI's format support across documents, spreadsheets, data
payloads, and live media streaming:

- **PDF:** Native embedded PDF reader with page zoom and open-in-browser support.
- **DOCX:** Formatted Word document paper view with clean margins and typography.
- **XLSX:** Multi-sheet workbook spreadsheet with tab navigation and cell grids.
- **CSV:** Interactive tabular data grid with live row filtering and row indexing.
- **JSON:** Pretty-printed JSON tree with syntax coloring and one-click copy to clipboard.
- **M3U8 / Video:** Integrated HTML5 & HLS adaptive video stream player.
- **Audio:** Embedded audio player with track metadata.

## The rule

A daemon publishes **DESCRIBE, never BYTES**. Every item in this example
carries a `format` and a `url` — nothing more:

```json
{
  "id": "pdf-doc-1",
  "title": "RFC 9110 — HTTP Semantics.pdf",
  "format": "pdf",
  "url": "https://www.rfc-editor.org/rfc/rfc9110.pdf"
}
```

The **player** downloads that URL in its own backend, caches the file, and
parses it. This daemon never reads a file, never parses a PDF, and never
base64-encodes a spreadsheet.

That is what makes the protocol language-agnostic: a C++ daemon that binds
`127.0.0.1:8789` and returns the same JSON works exactly like this Python
one.

## The documents

Every URL points at a real, publicly reachable document — an RFC, a
calibre demo, a spreadsheet sample, a CSV dataset, a JSON file. Nothing is
generated locally, so the demo exercises the same path a production daemon
would use when it points at a document store.

## Running the daemon

Unzip `03_multiformat_vault-win.zip` and double-click
**`03_multiformat_vault.exe`** — no Python needed. Or run it from source:

```bash
python app.py
```

- **Default port:** `8789`
- **API key:** `default-dev-key`
- **Override:** `python app.py --port 9000 --key my-secret-key`

In VoidUI, open **Settings (⚙)**, pick the **Omniformat Vault** preset (or
set the port to `8789`), and click **Save & Connect**.

## Check it with curl

```bash
curl -H "X-API-Key: default-dev-key" http://127.0.0.1:8789/api/data
```
