# Connecting to VoidUI

This guide explains how VoidUI talks to your local daemon.

---

## Overview

VoidUI is a native desktop viewer that polls a local HTTP endpoint you control.
Your daemon serves one JSON document describing a catalog; VoidUI renders it
in a three-pane workstation — categories on the left, items in the middle, the
rendered document on the right.

```
[Your Daemon] ← HTTP → [VoidUI.exe]
   127.0.0.1:PORT                 ▲
      any language                └── tinyjs backend: downloads files, caches them
```

The daemon can be written in **any language**. Python is only the bundled
example — see [Creating Daemons](creating_daemons.md).

---

## Step 1: Launch your daemon

Any daemon built on `VoidDaemon` (see `daemon_core/void_daemon.py`) accepts
these CLI flags:

```bash
python app.py --port 8787 --key my-secret-key
```

| Flag | Default | Description |
|------|---------|-------------|
| `--port` | `8787` | Port to listen on |
| `--key` | `default-dev-key` | API key (sent as the `X-API-Key` header) |
| `--host` | `127.0.0.1` | Bind address (keep local!) |

> **Note**: if you change the key, set the same key in VoidUI's settings. Any
> other process running on the machine can reach your port, so use a real key
> for anything beyond a demo.

---

## Step 2: Open VoidUI settings

Launch `VoidUI.exe` and click the **⚙ Settings** button (top right):

| Field | Example | Description |
|-------|---------|-------------|
| **Daemon Host / URL** | `http://127.0.0.1` | Scheme and host of your daemon. |
| **Port** | `8787` | The port your daemon binds to. |
| **Endpoint Path** | `/api/data` | The path the player calls. |
| **API Key (X-API-Key)** | `default-dev-key` | Must match the daemon's `--key`. |
| **Auto-Refresh Interval** | `Every 5 seconds` | Poll cadence. `Manual Only` disables polling. |

**Test Connection** performs one request and reports the payload's `type` and
`title`. **Save & Connect** persists the settings and starts polling
immediately.

### Presets

The Settings modal ships quick presets for the bundled example daemons:

| Preset | Port | Description |
|--------|------|-------------|
| Hello World (HTML) | 8787 | HTML mode — live time & stats |
| RSS 3-Pane (JSON) | 8788 | 3-pane JSON — three live RSS feeds |
| Omniformat Vault | 8789 | 3-pane JSON — PDF, DOCX, XLSX, CSV, JSON, M3U8 |

---

## Step 3: What the endpoint returns

VoidUI calls **one** endpoint on your daemon:

```
GET /api/data
X-API-Key: <your-key>
Accept: application/json
```

The response must be `Content-Type: application/json` and contain either:

### Mode A — Your markup

```json
{ "type": "html", "content": "<h1>Hello World</h1>" }
```

The response is still JSON — the markup travels as a string in `content`. The
player injects that string into the reading pane as a full HTML document.

### Mode B — 3-pane catalog (the usual case)

```json
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
      "badge": 1,
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

The shape is `categories[] → items[]`. Each item carries a `format` and a
`url`, and the **player** downloads and renders it — see the
[Omniformat Guide](omniformat_guide.md) for every supported format.

**A daemon publishes DESCRIBE, never BYTES.** Do not base64-encode a
spreadsheet into the payload; hand over a URL and let the player fetch it.

---

## Health check

`/api/health` is optional. It is not polled by the player, but it is handy
for monitoring and for your own start-up scripts:

```
GET /api/health
```

```json
{ "name": "My Daemon", "status": "ok", "timestamp": "…", "uptime_seconds": 419 }
```

---

## Reading the payload in a browser

The player is not the only way to look at what your daemon publishes. The
`/api/data` endpoint is plain HTTP, so you can inspect it with curl, with
Postman, or in a browser tab.

The catch is authentication: the endpoint wants an `X-API-Key` header, and a
browser's address bar can only send a URL. So the bare URL returns `401` —
that is the auth working, not a fault.

The Python framework accepts the key as a query parameter for exactly this
case:

```
http://127.0.0.1:8787/api/data?key=default-dev-key
```

Paste that into a browser and you get the raw JSON. To load it from a page
instead (which lets you pretty-print it), use `fetch`:

```html
<script>
(async () => {
  const r = await fetch('http://127.0.0.1:8787/api/data?key=default-dev-key');
  document.body.textContent = JSON.stringify(await r.json(), null, 2);
})();
</script>
```

This works from a `file://` page too — the daemon sends
`Access-Control-Allow-Origin: *` and answers the `OPTIONS` preflight.

A key in a query string can end up in browser history and in access logs, so
use the query form for local inspection only. The header is the real channel.

---

## Connection status indicators

| Indicator | Meaning |
|-----------|---------|
| 🟢 Green dot | Daemon reachable, last poll successful |
| 🟡 Yellow dot | Polling, last response slow (>2s) |
| 🔴 Red dot | Daemon unreachable or returned an error |

The header also shows the last successful sync time and a **Refresh** button
to poll immediately.

---

## How the player fetches your files

When an item is selected, the player asks its **own backend** to download the
item's `url`:

1. The backend fetches the URL (no CORS, no CSP, no page sandbox limits).
2. It writes the bytes into the app cache directory.
3. It hands the page a **path**, not the bytes.
4. The page reads that file back and parses it — ZIP/OOXML for `.xlsx` and
   `.docx`, CSV and JSON for text formats.

The page then displays it: a grid for spreadsheets, a document for Word files,
the webview's own PDF viewer for PDFs, `<video>`/`<audio>` for media.

**Your daemon never has to read a file, parse a PDF, or encode a spreadsheet.**
Point the item at a URL — on your own machine or anywhere on the internet —
and the player handles the rest.

### Caching

Downloaded files land in the app's cache directory:

```
<app cache>/documents/<name><ext>
```

The extension is guessed from the URL or the response's `Content-Type`, so a
URL like `…/rfc9110` still lands as `rfc9110.pdf`. Files are reused on the
next visit, and the cache can be cleared at any time.
