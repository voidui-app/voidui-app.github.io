# Creating Daemons for VoidUI

A VoidUI daemon is a small HTTP server on `127.0.0.1` that publishes a
**catalog** of items. The player polls it, shows the catalog, and renders
whatever the items point at.

**The daemon publishes DESCRIBE, never BYTES.** Every item carries a `format`
and a `url`. The *player* downloads that URL, caches it, and renders it. Your
daemon never reads a PDF, never unpacks a spreadsheet, never base64-encodes a
CSV.

That rule is what makes the protocol language-agnostic. A C++ daemon that
binds `127.0.0.1:8789` and returns the JSON below behaves exactly like a
Python one — the player cannot tell the difference.

---

## The whole format on one page

```
GET /api/data
Header: X-API-Key: <your key>

200 OK
Content-Type: application/json

{
  "type": "json",
  "layout": "3pane",
  "title": "My Workstation",
  "updated_at": "2026-10-20T18:00:00",
  "categories": [
    {
      "id": "docs",
      "title": "Documents",
      "icon": "📄",
      "items": [
        {
          "id": "rfc",
          "title": "RFC 9110 — HTTP Semantics.pdf",
          "format": "pdf",
          "subtitle": "194 pages",
          "preview": "The definitive HTTP reference.",
          "url": "https://www.rfc-editor.org/rfc/rfc9110.pdf",
          "meta": { "author": "IETF", "pages": 194 }
        }
      ]
    }
  ]
}
```

### Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/data` | `GET` | The catalog. This is the one the player calls. |
| `/api/health` | `GET` | Optional. Liveness info for monitoring. |

Both are authenticated with the `X-API-Key` header. A missing or wrong key
returns `401`.

The Python framework also accepts the key as a **query parameter**
(`/api/data?key=<your key>`). This is what lets you read the raw payload in a
browser's address bar, which cannot send custom headers. Treat it as a
convenience for local inspection, not as a production channel — a key in a
query string ends up in browser history and access logs. The header is the
primary channel, and the player only ever uses the header.

### Field reference

**Top level**

| Field | Type | Meaning |
|---|---|---|
| `type` | `"json"` \| `"html"` | `"json"` = the 3-pane workstation. `"html"` = raw HTML body. |
| `layout` | `"3pane"` | Present on JSON payloads. |
| `title` | string | Shown in the player's header. |
| `updated_at` | ISO-8601 string | Optional. |
| `categories` | array | The groups shown in the left pane. |
| `content` | string | **Only for `type: "html"`** — the HTML body itself. |

> **How HTML mode renders.** The markup is inserted into the reading pane
> rather than loaded as a page. Inline event handlers (`onclick`, `onerror`)
> fire normally, but a `<script>` tag inside `content` does **not** execute —
> the browser does not run scripts inserted via `innerHTML`. Send markup and
> styles; send behaviour through the daemon's own data and the player's
> built-in renderers.

**Category**

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Stable identifier. |
| `title` | string | Group heading. |
| `icon` | string | Optional emoji. |
| `badge` | number | Optional count badge. |
| `items` | array | The items in this group. |

**Item** — the important one

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Stable identifier. |
| `title` | string | Display name. |
| `format` | string | Selects the renderer. See the table below. |
| `url` | string | **Where the file is.** The player fetches this. |
| `subtitle` | string | Optional one-liner under the title. |
| `preview` | string | Optional longer description. |
| `meta` | object | Optional key/value bag shown in the detail pane. |
| `poster` | string | Optional poster image for video. |

### Formats

| `format` | Source | How the player renders it |
|---|---|---|
| `pdf` | URL | Downloads it, then the webview's own PDF viewer displays it. |
| `docx` | URL or inline | The player unpacks the OOXML and renders the text, headings, lists and tables. |
| `xlsx` | URL or inline | The player unpacks the workbook and renders a grid with sheet tabs. |
| `csv` | URL or inline | The player parses it and renders a filterable grid. |
| `json` | URL or inline | The player parses it and renders a syntax-highlighted, copyable tree. |
| `m3u8` | URL | HLS video. |
| `video` | URL | `<video>` playback. |
| `audio` | URL | `<audio>` playback. |
| `html` | inline | The item's `content` is rendered as HTML. |

**The player does the parsing.** A `.xlsx` is a ZIP of XML; a `.docx` is a ZIP
of XML. The player reads those formats itself — in the browser, with no
third-party library and no server-side round trip. Your daemon only has to
know the URL.

---

## Inline data (optional)

For small payloads you can skip the file entirely and put the data in the
item. The player prefers inline fields and only downloads when one is missing.

```json
{
  "id": "cfg",
  "title": "Config",
  "format": "json",
  "json_data": { "apiVersion": "v1" }
}
```

| Format | Inline field | Shape |
|---|---|---|
| `csv` | `csv_data` | The raw CSV text. |
| `json` | `json_data` | The parsed object. |
| `xlsx` | `sheets` | `[{"name": "Sheet1", "rows": [[...], [...]]}]` |
| `docx` | `content` | An HTML string. |
| `html` | `content` | An HTML string. |

You can set **both** an inline field and a `url`. The player uses the inline
data and keeps the URL for the "open in browser" action.

---

## Writing a daemon

### Python (the bundled helper)

`daemon_core/void_daemon.py` gives you CLI parsing, API-key auth, CORS
headers and `/api/health` for free.

```python
import sys, os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from daemon_core.void_daemon import VoidDaemon


def payload():
    return {
        "type": "json",
        "layout": "3pane",
        "title": "My Workstation",
        "updated_at": datetime.now().isoformat(),
        "categories": [{
            "id": "docs",
            "title": "Documents",
            "items": [{
                "id": "rfc",
                "title": "RFC 9110",
                "format": "pdf",
                "url": "https://www.rfc-editor.org/rfc/rfc9110.pdf",
            }],
        }],
    }


if __name__ == "__main__":
    VoidDaemon(
        name="My Daemon",
        default_port=8787,
        default_key="default-dev-key",
        data_handler=payload,
    ).run()
```

Run it:

```bash
python app.py --port 8787 --key secret123
```

The player needs to be told the port and key — see
[Connecting to VoidUI](connecting_to_voidui.md).

### C++ (any language)

There is nothing Flask-specific about the protocol. Bind a socket, check the
header, write the JSON.

```cpp
// Minimal shape — the details are yours.
std::string body = R"({
  "type": "json",
  "layout": "3pane",
  "title": "C++ Daemon",
  "categories": [{
    "id": "docs",
    "title": "Documents",
    "items": [{
      "id": "rfc",
      "title": "RFC 9110",
      "format": "pdf",
      "url": "https://www.rfc-editor.org/rfc/rfc9110.pdf"
    }]
  }]
})";

if (req.method == "GET" && req.path == "/api/data") {
    if (req.header("X-API-Key") != api_key) {
        res.status(401).json(R"({"error":"Unauthorized"})");
        return;
    }
    res.status(200).header("Content-Type", "application/json").body(body);
}
```

The same is true in Rust, Go, Node, C#, or anything with an HTTP server.

**Checklist for a non-Python daemon**

- [ ] Bind `127.0.0.1` (not `0.0.0.0` — this data is local).
- [ ] `GET /api/data` returns `Content-Type: application/json`.
- [ ] `GET /api/data` requires the `X-API-Key` header. (Optionally accept
      `?key=` as well, so the payload can be read in a browser — see
      [Endpoints](#endpoints).)
- [ ] Send `Access-Control-Allow-Origin: *` and allow the `X-API-Key` header
      (the player may be loaded from a `file://` origin).
- [ ] Answer `OPTIONS` preflights with `204`.
- [ ] The JSON is UTF-8.

---

## Serving files from your own machine

Point a `url` at your own server and the player will fetch it:

```python
"url": "http://127.0.0.1:8787/file/report.pdf"
```

Any path on your daemon works — the player requests it with the same
`X-API-Key` header it uses for `/api/data`, so the same check applies. Serve
the raw bytes with the right content type; the player does not care about the
filename or the extension.

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

## Tips

- **Publish URLs, not bytes.** A `url` is all the player needs. Do not
  base64-encode a spreadsheet into the payload.
- **Cache aggressively.** The player polls; do not re-fetch a slow upstream on
  every request.
- **Use a strong API key** in production. Anything else running on the
  machine can read your port.
- **Pick a free port.** 8787, 8788 and 8789 are used by the bundled examples.
- **Reuse downloaded files.** The player caches by URL, so a stable URL means
  the file is downloaded once.

---

## Packaging as an EXE

Once your daemon works, package it into a standalone `.exe` with PyInstaller:

```bash
pip install pyinstaller
python -m PyInstaller --onefile --name "my_daemon" app.py
```

Ship the `.exe` to users and list the dependencies in your docs — a frozen
binary needs no `requirements.txt` on the user's machine.

See `docs/packaging_daemons.md` for the complete guide.
