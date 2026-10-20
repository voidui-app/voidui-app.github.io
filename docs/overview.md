# VoidUI: Architectural Overview

**VoidUI** is a universal developer tool consisting of a lightweight desktop viewer (`viewer/dist/VoidUI.exe` plus `launcher.exe`, shipped together as a 4.6 MB zip) and a drop-in local Python daemon framework. It acts as an empty, skin-agnostic GUI shell that brings local scripts, scrapers, ML models, or data pipelines to life instantly without requiring developers to build custom frontends or wrestle with browser CORS restrictions.

---

## The Core Philosophy: "Anti-Electron" & Local-First

Most developers write brilliant backend scripts, scrapers, AI agents, or data pipelines, but hate the friction of building a frontend. If they want a UI, they are forced to choose between a clunky terminal, a heavy Electron app (100MB+ RAM), or spinning up a local web server and fighting browser CORS issues.

VoidUI changes this paradigm:
1. **Micro-Footprint (4.6 MB zip):** Powered by TinyJS (`txiki.js` runtime + Windows native WebView2), VoidUI launches instantaneously and consumes negligible memory.
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
         │ (Serves raw HTML DOM or 3-Pane structured JSON)
         ▼
[ VoidUI Desktop Viewer (VoidUI.exe + launcher.exe) ] ──> Configured via Settings Panel (URL, Port, Key, Polling)
```

---

## Directory Organization

```text
voidUI/
├── viewer/                      # The TinyJS desktop player — the product
│   ├── tinyjs.json              # App config & window properties
│   ├── src/
│   │   ├── main.js              # Native backend (txiki.js) — downloads files
│   │   └── frontend/
│   │       ├── index.html       # Single Page Application
│   │       ├── style.css        # Responsive dark workstation styles
│   │       ├── app.js           # Fetcher, router, 3-pane controller
│   │       └── lib/             # The player's own parsers
│   │           ├── zip.js       # ZIP reader (DEFLATE)
│   │           ├── xlsx.js      # SpreadsheetML reader
│   │           ├── docx.js      # WordprocessingML reader
│   │           └── omniformat.js# Format detection, download + parse
│   └── dist/
│       ├── VoidUI.exe           # Desktop viewer backend
│       └── launcher.exe         # Native WebView2 window (required)
├── examples/                    # Runnable examples in both Python & Standalone .EXE
│   ├── 01_hello_world/          # Example 1: Dynamic HTML Mode
│   │   ├── app.py
│   │   └── 01_hello_world.exe
│   ├── 02_rss_viewer/           # Example 2: 3-Feed RSS Aggregator
│   │   ├── app.py
│   │   ├── rss_parser.py
│   │   └── 02_rss_viewer.exe
│   └── 03_multiformat_vault/    # Example 3: Omniformat Workstation (PDF, DOCX, XLSX, CSV, JSON, M3U8)
│       ├── app.py
│       └── 03_multiformat_vault.exe
├── docs/                        # In-depth technical documentation
│   ├── overview.md              # This overview
│   ├── connecting_to_voidui.md  # How VoidUI connects and communicates
│   ├── creating_daemons.md      # How to build custom daemons in Python
│   ├── omniformat_guide.md      # Full specification for PDF, XLSX, CSV, M3U8, etc.
│   └── packaging_daemons.md     # How to compile daemons to standalone .EXE
└── Publish/                     # Web distribution package
    ├── index.html               # Use-oriented product showcase & interactive demo
    └── readme.md                # Deployment instructions
```
