# VoidUI

**Point it at an API. It becomes an app.**

VoidUI is a small native Windows viewer (6.7 MB) that renders whatever an HTTP
API returns — your own HTML, a 3-pane JSON catalog, a PDF, a spreadsheet. The
backend can be written in any language, and it does not have to run on your
machine: a local daemon and a hosted endpoint work the same way.

This folder is the public distribution. Its contents go online as-is — GitHub
Pages, Netlify, or any static host.

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
a terminal, a 100 MB Electron app, or a browser tab and a CORS fight.

VoidUI takes a third route: the script serves JSON over HTTP, and the viewer
renders it. There is no frontend to build and no framework to adopt.

**One endpoint, two shapes.** The `type` field picks the shape:

| `type` | What you send | What you get |
|---|---|---|
| `html` | `content` with your markup | Your HTML, in the reading pane |
| `json` | `layout: "3pane"` and `categories[]` | A browsing workspace: categories, items, detail |

The 3-pane JSON shape has to match the one the player expects — the exact
field list is in [Creating daemons](docs/creating_daemons.md).

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
hosted endpoint works too — put the host in **Daemon Host**, the port in
**Port**, and hand out API keys yourself. The player talks to it over plain
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

## Deploying the site

### GitHub Pages (recommended)

1. Push the repo to GitHub.
2. **Settings → Pages** → Source: `main` branch, folder `/Publish`.
3. The site is served at `https://your-org.github.io/voidui/`.

Everything the page links to lives inside this folder, so the site is
self-contained — there are no `../` paths to break.

For a custom domain, drop a `CNAME` file here and point an `A` or `CNAME`
record at GitHub's servers.

> **On GitHub Releases:** Pages serves files from the repository, but a
> Release asset is served from a different URL behind a redirect. Linking the
> download button to a Release asset is more reliable for large binaries and
> gives you versioned downloads. To switch, change the `href` on the download
> button in `index.html` to the Release URL — the `download` attribute is
> harmless either way.

### Netlify / Vercel Drop

Zip this folder and drag it onto Netlify Drop. The publish directory is the
root of the zip.

### Self-hosted

```bash
npx serve -s Publish --listen 3000
```

---

## Keeping the site current

**New player build**

```bash
cd viewer && tinyjs build
```

That produces `viewer/dist/VoidUI.exe` and `viewer/dist/launcher.exe`. Repack
them into the download zip:

```bash
python - <<'PY'
import zipfile, os
out = 'Publish/player/VoidUI-win.zip'
os.remove(out) if os.path.exists(out) else None
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for name in ['VoidUI.exe', 'launcher.exe']:
        zi = zipfile.ZipInfo(name, date_time=(2026, 10, 21, 0, 0, 0))
        zi.external_attr = 0o755 << 16
        z.writestr(zi, open(os.path.join('viewer/dist', name), 'rb').read())
print(round(os.path.getsize(out) / 1048576, 2), 'MB')
PY
```

Then update the size quoted in `index.html` — the meta description, the hero
fineprint, the comparison table and the download button all point at the zip,
and a stale number is the easiest thing to get wrong.

> **Do not ship `tinyjs publish`'s zip.** `tinyjs publish` writes
> `dist/publish/VoidUI-1.0.0-win.zip`, which is the *updater payload* — a
> source bundle with the binaries prepended, and unzipping it gives you
> `bridge.js` and `frontend/`, not a runnable app. The download zip above is
> the plain folder a person can unzip and run.

**Changed docs**

```bash
cp docs/*.md Publish/docs/
```

**New or changed example**

```bash
python -m PyInstaller --noconfirm --clean \
  --distpath examples/03_multiformat_vault --workpath build/03_multiformat_vault \
  03_multiformat_vault.spec
```

Then repack the example zip — it carries the EXE and the source together:

```bash
python - <<'PY'
import zipfile, os
src, out = 'examples/03_multiformat_vault', 'Publish/examples/03_multiformat_vault/03_multiformat_vault-win.zip'
os.remove(out) if os.path.exists(out) else None
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for f in ['03_multiformat_vault.exe', 'app.py', 'README.md']:
        zi = zipfile.ZipInfo(f, date_time=(2026, 10, 21, 0, 0, 0))
        zi.external_attr = 0o755 << 16
        z.writestr(zi, open(os.path.join(src, f), 'rb').read())
print(round(os.path.getsize(out) / 1048576, 2), 'MB')
PY
```

The `--distpath` and `--workpath` flags are required — PyInstaller takes the
output directory from the command line, not from the spec file. A spec cannot
redirect it.

The daemon EXEs bundle `daemon_core`, so a change to the framework means
every daemon EXE has to be rebuilt:

```bash
for n in 01_hello_world 02_rss_viewer 03_multiformat_vault; do
  python -m PyInstaller --noconfirm --clean \
    --distpath "examples/$n" --workpath "build/$n" "$n.spec"
done
```

Then repack all three example zips the same way as above.

**Changed landing page**

`index.html` is hand-written HTML and CSS — no build step, no framework, no
CDN scripts. Edit it and reload.

---

## Two things to know before publishing

**`launcher.exe` is not optional.** `VoidUI.exe` looks for it in the same
directory at startup and exits immediately if it is missing:

```
Error: tinyjs launcher binary not found (looked at: <dir>/launcher.exe)
```

Both files are tinyjs build artifacts, and the download zip carries them
together. Do not rename `launcher.exe`, and do not drop it from the zip.

**`idea.md` is not published.** It is internal working notes, so it is ignored
by git and will not reach the public folder.

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

Everything else in the repository — the viewer source, the daemon framework,
the build specs, the tests — lives outside this folder and is not published.
