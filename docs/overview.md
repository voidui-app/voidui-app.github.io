# VoidUI: Architectural Overview

**VoidUI** is a universal developer tool consisting of a lightweight desktop viewer (two binaries, `VoidUI.exe` and `launcher.exe`, shipped together as a 4.6 MB zip) and a drop-in local Python daemon framework. It acts as an empty, skin-agnostic GUI shell that brings local scripts, scrapers, ML models, or data pipelines to life instantly without requiring developers to build custom frontends or wrestle with browser CORS restrictions.

---

## The Core Philosophy: "Anti-Electron" & Local-First

Most developers write brilliant backend scripts, scrapers, AI agents, or data pipelines, but hate the friction of building a frontend. If they want a UI, they are forced to choose between a clunky terminal, a heavy Electron app (100MB+ RAM), or spinning up a local web server and fighting browser CORS issues.

VoidUI changes this paradigm:
1. **Micro-Footprint (4.6 MB zip):** Built on a native JavaScript runtime with the Windows WebView2 window, VoidUI launches instantaneously and consumes negligible memory.
2. **Dual-Mode Engine:** Switch between dynamic server-rendered HTML cards (Mode A) and a structured 3-Pane workstation (Mode B).
3. **Omniformat Support:** Native viewing for PDF documents, DOCX layouts, multi-sheet XLSX spreadsheets, interactive CSV data grids, JSON syntax-colored trees, and M3U8/HLS video streams.
4. **Zero-CORS Security:** Communicates over private localhost loopback via native fetch, keeping confidential local data completely offline and secure.

---

## System Architecture

```
[ Local Developer Script / Python Daemon ]
         │ (Runs background HTTP server on 127.0.0.1:PORT)
         ▼
[ VoidDaemon Engine ] ──> Secured via X-API-Key Header
         │ (Serves JSON: your markup, or 3-Pane structured)
         ▼
[ VoidUI Desktop Viewer (VoidUI.exe + launcher.exe) ]
         │ (Configured via Settings: URL, Port, Key, Polling)
```

---

## What you get

VoidUI ships as binaries, not as a source tree. What you download is what you
run — there is nothing to compile. The player itself is a closed binary: you
connect to it over HTTP and you never need to know what is inside it.

This is the whole distribution:

```
VoidUI/
├── index.html                      the landing page
├── readme.md                       the readme
├── icon.png, favicon.png           the app icon
├── banner.jpg                      the social banner
├── player/
│   └── VoidUI-win.zip              the player — VoidUI.exe + launcher.exe
├── examples/
│   ├── daemon_core/                the shared framework
│   ├── 01_hello_world/
│   │   ├── 01_hello_world-win.zip  the EXE, app.py, daemon_core/, README
│   │   ├── app.py                  the daemon source
│   │   └── README.md               run instructions
│   ├── 02_rss_viewer/
│   │   ├── 02_rss_viewer-win.zip
│   │   ├── app.py
│   │   ├── rss_parser.py
│   │   └── README.md
│   └── 03_multiformat_vault/
│       ├── 03_multiformat_vault-win.zip
│       ├── app.py
│       └── README.md
└── docs/
    ├── overview.md                 this overview
    ├── connecting_to_voidui.md     how VoidUI connects and communicates
    ├── creating_daemons.md         how to build custom daemons
    ├── omniformat_guide.md         PDF, XLSX, CSV, M3U8, and the rest
    └── packaging_daemons.md        compiling daemons to a standalone EXE
```

Every document also ships as a rendered `.html` next to its `.md` source, so
the site can link to a page and the repository can keep the editable original.

## Anatomy of a daemon

The example daemons are the reference implementation of the protocol. Each one
is a small folder:

```
01_hello_world/
├── app.py               the daemon — the data it serves and the CLI
└── README.md            run instructions, API key, what the JSON looks like
```

`app.py` is built on `daemon_core/`, the shared framework, which holds the
HTTP layer: the `/api/data` endpoint, the `X-API-Key` check, the CORS headers
and the command-line flags. `app.py` holds only your data. Write a daemon, and
you write `app.py`.

In the repo the framework sits once, at `examples/daemon_core/`, and every
example daemon imports it from there. In a download it sits next to `app.py`,
inside the zip, so the daemon runs with nothing else to set up. The import
block in `app.py` looks in both places.

To compile a daemon, the folder needs `app.py` and `daemon_core/` side by
side, plus any other module the daemon imports. The
[Packaging Daemons](packaging_daemons.md) guide has the full walkthrough.
