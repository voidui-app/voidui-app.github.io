# Example 02 — RSS 3-Pane Aggregator

Aggregates three live RSS/Atom feeds into the VoidUI **3-Pane JSON** layout:
categories in the left rail, headlines in the middle, the article in the
reading pane.

| | |
|---|---|
| **Port** | `8788` |
| **API key** | `default-dev-key` |
| **Endpoint** | `GET http://127.0.0.1:8788/api/data` |
| **Mode** | 3-Pane JSON (`"type": "json"`, `"layout": "3pane"`) |

## The feeds

1. **BBC World News** — global headlines and current events.
2. **Ars Technica** — tech news, software and hardware analysis.
3. **Python Developer Blog** — official announcements from the Python team.

## Architecture

- **No feed-parsing dependencies** — the feed side is standard library only
  (`urllib.request` + `xml.etree.ElementTree`). The HTTP server around it is
  Flask, same as the other examples.
- **In-memory caching** with a 5-minute TTL, so a refresh cycle does not
  hammer three news sites.
- Handles both **RSS 2.0** and **Atom**.

---

## Run it

Unzip `02_rss_viewer-win.zip` and double-click **`02_rss_viewer.exe`** — no
Python needed.

Or from source:

```bash
python app.py
```

Custom port or key:

```bash
python app.py --port 9001 --key my-rss-key
```

Help:

```bash
python app.py --help
```

---

## View it in VoidUI

1. Launch **`VoidUI.exe`** from the unzipped `VoidUI-win.zip` (keep
   `launcher.exe` next to it).
2. Click **⚙ Settings** → pick the **RSS 3-Pane (8788)** preset → **Save & Connect**.

---

## View the raw JSON in a normal browser

The API requires the `X-API-Key` header, and a browser's address bar cannot
send custom headers — so the bare URL returns `401 Unauthorized`. Pass the key
as a **query parameter** to read the payload in a browser tab:

```
http://127.0.0.1:8788/api/data?key=default-dev-key
```

The daemon accepts `?key=` for exactly this reason. The header remains the
primary channel — the player always uses it, and a header never lands in a
URL, a proxy log, or browser history — but the query string is what makes the
payload viewable in a browser.

> A URL with `?key=` can end up in your browser's history. Fine for a local
> demo daemon; not something to rely on for anything sensitive.

To load it from a page instead of the address bar:

```html
<!DOCTYPE html>
<meta charset="utf-8">
<pre id="out">loading…</pre>
<script>
(async () => {
  const r = await fetch('http://127.0.0.1:8788/api/data?key=default-dev-key');
  document.getElementById('out').textContent =
    'HTTP ' + r.status + '\n\n' + JSON.stringify(await r.json(), null, 2);
})();
</script>
```

Or from a terminal:

```bash
curl -H "X-API-Key: default-dev-key" http://127.0.0.1:8788/api/data
```

The JSON is large — 70 articles with full HTML bodies — so a pretty-printed
browser view is genuinely useful here for inspecting the structure.

---

## The payload

```json
{
  "type": "json",
  "layout": "3pane",
  "title": "RSS News Aggregator",
  "updated_at": "2026-10-20T14:32:07Z",
  "categories": [
    {
      "id": "bbc_world",
      "title": "BBC World News",
      "icon": "🌍",
      "badge": 25,
      "items": [
        {
          "id": "bbc-1",
          "title": "Headline text",
          "subtitle": "2 hours ago",
          "preview": "Short snippet…",
          "content": "<div class=\"article-reader\">…</div>",
          "url": "https://www.bbc.co.uk/news/…"
        }
      ]
    }
  ]
}
```

Each category is one feed. Each item is one article. The `url` is the
original link — the player can open it in your system browser.

---

## Source

| File | What it is |
|---|---|
| `app.py` | The daemon. 42 lines. |
| `rss_parser.py` | Feed fetching, XML parsing, and the TTL cache. |
| `daemon_core/` | The shared framework, as a package folder. **Required.** |
| `README.md` | This file. |

### `daemon_core/` is not optional

`app.py` does not implement the HTTP layer itself. It hands its data to
`VoidDaemon`, which lives in `daemon_core/void_daemon.py`, and that class
supplies everything a VoidUI daemon needs to be a daemon:

- the `GET /api/data` endpoint the player polls
- the `X-API-Key` check that returns `401` without the right key
- the CORS headers and `OPTIONS` preflight
- the `GET /api/health` endpoint
- the `--port`, `--host`, `--key` and `--debug` command-line flags

Without the folder, the import fails and the daemon never starts:

```
ModuleNotFoundError: No module named 'daemon_core'
```

The `.exe` has the framework frozen inside, which is why running the binary
needs nothing; running the source needs the folder.

### Where the framework sits

There are two layouts, and the import block in `app.py` looks in both:

| Situation | Where `daemon_core/` is |
|---|---|
| Unzipped download | the same folder as `app.py` |
| Working in the repo | one folder up, at `examples/daemon_core/` |

That is the whole of the import block — the first path is the download, the
second is the repo:

```python
import os
import sys

# `daemon_core/` is the shared framework this daemon is built on. It sits in
# the same folder as this file when the daemon runs from an unzipped download,
# and one folder up when the daemon runs from the repo. Try both.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                    # next to app.py
sys.path.insert(1, os.path.dirname(_HERE))  # one level up

try:
    from daemon_core.void_daemon import VoidDaemon
except ImportError:
    # Standalone fallback if copied outside repo
    from void_daemon import VoidDaemon
```

`rss_parser.py` is this daemon's own module, so it sits in the same folder as
`app.py` in both layouts.

### Running it from source

`daemon_core` is bundled inside the `.exe`. The zip ships it as a folder too,
so the source run works out of the box:

```bash
pip install flask
python app.py
```

That is all the source run needs: Flask, plus the `daemon_core` folder sitting
next to `app.py`.

### Compiling it yourself

`app.py`, `rss_parser.py` and `daemon_core/` in one folder is everything
PyInstaller needs:

```bash
python -m PyInstaller --onefile --name "02_rss_viewer" app.py
```

The [Packaging daemons](../../docs/packaging_daemons.md) guide has the
full walkthrough, including the `.spec` file the bundled examples use.
