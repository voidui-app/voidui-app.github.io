# Example 01 — Hello World

A minimal daemon that returns a live HTML dashboard: the current date, the
current time, uptime, and a few system stats. It exists to show **Mode A**
(server-rendered HTML) end to end.

| | |
|---|---|
| **Port** | `8787` |
| **API key** | `default-dev-key` |
| **Endpoint** | `GET http://127.0.0.1:8787/api/data` |
| **Mode** | HTML (`"type": "html"`) |

---

## Run it

Unzip `01_hello_world-win.zip` and double-click **`01_hello_world.exe`** — no
Python needed.

Or from source:

```bash
python app.py
```

You should see:

```
==================================================
  Starting Hello World CLI Daemon
  Endpoint: http://127.0.0.1:8787/api/data
  API Key:  default-dev-key
==================================================
```

---

## View it in VoidUI

1. Launch **`VoidUI.exe`** from the unzipped `VoidUI-win.zip` (keep
   `launcher.exe` next to it — see below).
2. Click **⚙ Settings** → pick the **Hello World (8787)** preset → **Save & Connect**.

The player polls the daemon and renders the HTML in its reading pane, updating
on every refresh.

---

## View it in a normal browser

The API is protected by an `X-API-Key` header, and a browser's address bar
cannot send custom headers — so pasting the bare URL into the address bar
returns `401 Unauthorized`. That is the auth working, not a bug.

To read the raw JSON in a browser, pass the key as a **query parameter**:

```
http://127.0.0.1:8787/api/data?key=default-dev-key
```

The daemon accepts `?key=` for exactly this reason. The header is still the
primary channel — the player always uses it, and a header never lands in a URL,
a proxy log, or browser history — but a query string is what makes the payload
viewable in a browser tab.

> **Note**: a URL with `?key=` can end up in your browser's history. That is
> fine for a local demo daemon; it is not something to rely on for a daemon
> serving anything sensitive.

To read the response from a web page instead of the address bar, `fetch` it
directly — the daemon sends `Access-Control-Allow-Origin: *`, so a `file://`
page works too:

```html
<!DOCTYPE html>
<meta charset="utf-8">
<pre id="out">loading…</pre>
<script>
(async () => {
  const r = await fetch('http://127.0.0.1:8787/api/data?key=default-dev-key');
  document.getElementById('out').textContent =
    'HTTP ' + r.status + '\n\n' + JSON.stringify(await r.json(), null, 2);
})();
</script>
```

Or from a terminal — no browser needed:

```bash
curl -H "X-API-Key: default-dev-key" http://127.0.0.1:8787/api/data
```

---

## The payload

```json
{
  "type": "html",
  "title": "Hello World Monitor — 14:32:07",
  "updated_at": "2026-10-20T14:32:07Z",
  "content": "<div style=\"...\">…the dashboard markup…</div>"
}
```

`content` is raw HTML. The player injects it into its reading pane, so this
mode is the one to use when your script already produces markup.

---

## Source

| File | What it is |
|---|---|
| `app.py` | The daemon. 133 lines — the markup it serves and the CLI. |
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

### What your own daemon looks like

`app.py` is the whole thing. The framework does the rest:

```python
from daemon_core import VoidDaemon

def my_data_handler():
    return {
        "type": "html",
        "title": "My Custom Script",
        "content": "<h1>Process Completed</h1><p>Processed 42 records.</p>",
    }

if __name__ == "__main__":
    VoidDaemon(name="My Custom Script", default_port=8787,
               data_handler=my_data_handler).run()
```

The frozen `.exe` has `daemon_core` bundled inside it, so the binary needs
nothing installed. The zip ships the folder too, so the source run works out
of the box:

```bash
pip install flask
python app.py
```

That is all the source run needs: Flask, plus the `daemon_core` folder sitting
next to `app.py`.

### Compiling it yourself

`app.py` and `daemon_core/` in one folder is everything PyInstaller needs:

```bash
python -m PyInstaller --onefile --name "01_hello_world" app.py
```

The [Packaging daemons](../../docs/packaging_daemons.md) guide has the
full walkthrough, including the `.spec` file the bundled examples use.
