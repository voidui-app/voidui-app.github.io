#!/usr/bin/env python3
"""
VoidUI Example 3: Omniformat Vault Daemon
Demonstrates full 3-Pane workstation support for diverse file types and media:
PDF, DOCX, XLSX, CSV, JSON, M3U8 (HLS video), Audio, and HTML.

THE CONTRACT IN ONE SENTENCE
----------------------------
A daemon publishes DESCRIBE, never BYTES. Every item carries a `format` and a
`url`; the player downloads that URL itself (in its own backend), caches the
file, and renders it. The daemon never reads a file, never parses a PDF, and
never base64-encodes a spreadsheet.

That is what makes the protocol language-agnostic: a C++ daemon that binds
127.0.0.1:8789 and returns this JSON works exactly like this Python one.

    curl -H "X-API-Key: default-dev-key" http://127.0.0.1:8789/api/data
"""

import os
import sys
from datetime import datetime

# Add project root for daemon_core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from daemon_core.void_daemon import VoidDaemon
except ImportError:
    from void_daemon import VoidDaemon

# The port the daemon actually binds to. Updated from the CLI arguments in
# main() so the URLs handed to the viewer always match the real endpoint.
PORT = 8789


# ---------------------------------------------------------------------------
# Remote sources.
#
# These are real, publicly reachable documents. The player fetches them over
# HTTP and renders them, so the demo exercises the same path a production
# daemon would use when it points at a document store.
# ---------------------------------------------------------------------------

PDF_URL = "https://www.rfc-editor.org/rfc/rfc9110.pdf"
DOCX_URL = "https://calibre-ebook.com/downloads/demos/demo.docx"
XLSX_URL = "https://filesamples.com/samples/document/xlsx/sample1.xlsx"
CSV_URL = "https://raw.githubusercontent.com/vega/vega-datasets/main/data/stocks.csv"
JSON_URL = "https://raw.githubusercontent.com/typicode/demo/master/db.json"


def get_omniformat_payload():
    return {
        "type": "json",
        "layout": "3pane",
        "title": "VoidUI Omniformat Workstation",
        "updated_at": datetime.now().isoformat(),
        "categories": [
            {
                "id": "docs",
                "title": "Documents & Reports",
                "icon": "📄",
                "badge": 2,
                "items": [
                    {
                        "id": "pdf-doc-1",
                        "title": "RFC 9110 — HTTP Semantics.pdf",
                        "format": "pdf",
                        "subtitle": "Multi-page PDF • fetched by the player",
                        "preview": "The IETF's HTTP Semantics specification: 194 pages of the definitive HTTP reference.",
                        "url": PDF_URL,
                        "meta": {
                            "author": "IETF / HTTP Working Group",
                            "published": "June 2022",
                            "pages": 194
                        }
                    },
                    {
                        "id": "docx-doc-2",
                        "title": "Demonstration of DOCX Support.docx",
                        "format": "docx",
                        "subtitle": "Word Document • parsed in the player",
                        "preview": "A real .docx exercising headings, lists, tables, footnotes, and hyperlinks.",
                        "url": DOCX_URL,
                        "meta": {
                            "author": "Calibre",
                            "published": "Open format demonstration"
                        }
                    }
                ]
            },
            {
                "id": "tabular",
                "title": "Data & Spreadsheets",
                "icon": "📊",
                "badge": 3,
                "items": [
                    {
                        "id": "csv-data-1",
                        "title": "Stock Prices.csv",
                        "format": "csv",
                        "subtitle": "CSV Dataset • filterable grid",
                        "preview": "Historical stock prices for MSFT, AMZN, GOOG, AAPL and others, parsed straight from the CSV.",
                        "url": CSV_URL
                    },
                    {
                        "id": "xlsx-data-2",
                        "title": "Sales Report Sample.xlsx",
                        "format": "xlsx",
                        "subtitle": "Excel Workbook • 391 rows",
                        "preview": "A real .xlsx with shared strings and a styled header row — unpacked and parsed by the player.",
                        "url": XLSX_URL
                    },
                    {
                        "id": "json-data-3",
                        "title": "Database Configuration.json",
                        "format": "json",
                        "subtitle": "JSON Schema • Formatted & Copyable",
                        "preview": "A small document-store configuration, fetched and pretty-printed by the player.",
                        "url": JSON_URL
                    }
                ]
            },
            {
                "id": "media",
                "title": "Streaming Media",
                "icon": "🎬",
                "badge": 2,
                "items": [
                    {
                        "id": "m3u8-stream-1",
                        "title": "Live Adaptive HLS Stream (Tears of Steel).m3u8",
                        "format": "m3u8",
                        "subtitle": "HLS Video • Adaptive Multi-Bitrate",
                        "preview": "Interactive video player streaming live adaptive bitrate HLS (.m3u8) video.",
                        "url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
                        "poster": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80"
                    },
                    {
                        "id": "audio-track-2",
                        "title": "Developer Radio & Synth Ambience.mp3",
                        "format": "audio",
                        "subtitle": "Audio Broadcast • Stereo 320kbps",
                        "preview": "Embedded audio player for background ambient soundscapes and developer podcasts.",
                        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
                    }
                ]
            }
        ]
    }


def main():
    global PORT

    daemon = VoidDaemon(
        name="Omniformat Vault Daemon",
        default_port=8789,
        default_key="default-dev-key",
        data_handler=get_omniformat_payload
    )

    # Parse the CLI arguments once so the generated URLs match the real port.
    args = daemon.parse_args(sys.argv[1:])
    PORT = args.port

    daemon.run(sys.argv[1:])


if __name__ == "__main__":
    main()
