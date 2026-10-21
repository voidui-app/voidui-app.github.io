# VoidUI

**Point it at an API. It becomes an app.**

VoidUI is a small native Windows viewer (4.6 MB zipped) that renders whatever
an HTTP API returns — your own markup, a 3-pane JSON catalog, a PDF, a
spreadsheet. The backend can be written in any language, and it does not have
to run on your machine: a local daemon and a hosted endpoint work the same way.

This is the published distribution. The viewer, the example daemons and the
documentation are here as they are served.

| Download | Size | What's inside |
|---|---|---|
| [VoidUI-win.zip](player/VoidUI-win.zip) | 4.6 MB | `VoidUI.exe`, `launcher.exe` |
| [01_hello_world-win.zip](examples/01_hello_world/01_hello_world-win.zip) | 15.4 MB | the daemon EXE, `app.py`, `void_daemon.py`, `README.md` |
| [02_rss_viewer-win.zip](examples/02_rss_viewer/02_rss_viewer-win.zip) | 15.5 MB | the daemon EXE, `app.py`, `rss_parser.py`, `void_daemon.py`, `README.md` |
| [03_multiformat_vault-win.zip](examples/03_multiformat_vault/03_multiformat_vault-win.zip) | 15.4 MB | the daemon EXE, `app.py`, `void_daemon.py`, `README.md` |

The viewer is 4.6 MB as a zip and 7.8 MB unpacked — it ships as two binaries
and both are needed. The daemon zips are PyInstaller builds, which bundle a
Python runtime; that is where their 15 MB comes from, and it is why they need
no interpreter on the target machine.

Each daemon zip also carries the daemon's source, so you can read it or run
it yourself. `void_daemon.py` is the shared framework flattened out of
`daemon_core` — with it and Flask, `python app.py` starts the daemon from
source.

---

## Get it running in 60 seconds

1. **Download the player.** `player/VoidUI-win.zip` is the viewer. Unzip it,
   then run `VoidUI.exe`. Keep `launcher.exe` in the same folder — the viewer
   will not start without it.
2. **Start something for it to show.** The three example daemons are
   standalone EXEs inside zips; unzip one, double-click the EXE, and a local
   server comes up. Or run any daemon you already have.
3. **Point VoidUI at it.** Open the viewer, click **Settings**, enter the host,
   port and API key, and press **Save & Connect**.

The examples are the fastest way in:

| Example | Port | What it shows |
|---|---|---|
| [Hello World](examples/01_hello_world/README.md) | 8787 | HTML mode — live clock and system stats |
| [RSS Viewer](examples/02_rss_viewer/README.md) | 8788 | 3-pane mode — three live feeds |
| [Omniformat Vault](examples/03_multiformat_vault/README.md) | 8789 | PDF, DOCX, XLSX, CSV, JSON and media |

Each has a README with the run instructions, the API key, and how to read the
raw JSON in a normal browser.

---

## The idea

Most developers write a good script and then stall at the UI. The options are
a terminal, a 100–200 MB Electron app, or a browser tab and a CORS fight.

VoidUI takes a third route: the script serves JSON over HTTP, and the viewer
renders it. There is no frontend to build and no framework to adopt.

**One endpoint, two shapes.** The response is always JSON; the `type` field
picks what the player does with it:

| `type` | What you send | What you get |
|---|---|---|
| `html` | `content` with your markup | Your HTML, in the reading pane |
| `json` | `layout: "3pane"` and `categories[]` | A browsing workspace: categories, items, detail |

So the markup in `html` mode travels as a string *inside* a JSON object — the
daemon never writes an HTML document to the socket. The 3-pane JSON shape has
to match the one the player expects — the exact field list is in
[Creating daemons](docs/creating_daemons.md).

**The protocol is language-agnostic.** A daemon is any HTTP server that returns
the right JSON. The bundled examples are Python and ship as Windows binaries,
but the protocol itself is HTTP and JSON — Rust, C++, Go, Node and a static
JSON file on someone else's server all work identically. The player cannot tell
them apart, and it does not care.

**A daemon publishes DESCRIBE, never BYTES.** Every item carries a `format`
and a `url`; the player downloads and parses the file itself. Your server
never reads a PDF or base64-encodes a spreadsheet, so a 40 MB document costs
your daemon nothing.

**Local or hosted, your call.** A daemon on `127.0.0.1` is the usual case. A
hosted endpoint works too — put the address in **Daemon Host / URL**, the port
in **Port**, and hand out API keys yourself. The player talks to it over plain
HTTPS.

**One exception: streaming playlists.** Files are fetched by the player's own
backend, so they work whatever headers your server sends. `m3u8` is different
— the browser fetches the playlist itself, so the host has to allow
cross-origin requests.

Read the docs for the details:

| Document | What it covers |
|---|---|
| [Overview](docs/overview.md) | The architecture and why it is built this way |
| [Connecting to VoidUI](docs/connecting_to_voidui.md) | Settings, endpoints, status, reading the payload in a browser |
| [Creating daemons](docs/creating_daemons.md) | The full response format, in Python and in C++ |
| [Omniformat guide](docs/omniformat_guide.md) | Every supported format and exactly how it is parsed |
| [Packaging daemons](docs/packaging_daemons.md) | Shipping your own daemon as a standalone EXE |

---

## Hosting this yourself

The whole distribution is static — HTML, markdown, and a few zip files. Serve
it from any static host.

**GitHub Pages** — the site is published from the `voidui.github.io` repository:
the contents of this folder are the repository root, and Pages serves the
`main` branch. Push and it goes live.

**Netlify / Vercel** — drag the folder onto Netlify Drop, or point a build at
it with no command and the root as the publish directory.

**Your own server** — any static file server will do:

```bash
npx serve -s . --listen 3000
```

For a custom domain, drop a `CNAME` file in the repository root and point an
`A` or `CNAME` record at GitHub's servers.

---

## What is in here

```
index.html                      the landing page
readme.md                       this file
icon.png, favicon.png           the app icon
player/VoidUI-win.zip           the viewer — VoidUI.exe + launcher.exe
examples/                       three daemon zips, each with the EXE, source and README
docs/                           the five documents the site links to
```

Every download on the page is a zip. The loose `.exe` files are not published
— a single-file download of `VoidUI.exe` would arrive without its launcher and
would not start.

The viewer's source is not part of this distribution. The protocol and the
file formats are documented in `docs/`, and a daemon can be written in any
language that can serve HTTP. The example daemons do ship their source, since
they are meant to be read and rewritten.
