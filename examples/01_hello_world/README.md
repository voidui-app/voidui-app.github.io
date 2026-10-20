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

`app.py` — the whole daemon is about 60 lines. It uses the shared
`daemon_core` framework, which supplies the CLI flags, the `X-API-Key` check,
CORS headers, and the `/api/health` endpoint.

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

`daemon_core` is not bundled into the `.exe` — the frozen build has it inside.
To run from source you need it on your path:

```bash
pip install flask
python app.py
```
