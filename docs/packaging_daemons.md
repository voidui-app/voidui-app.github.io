# Packaging Daemons as Standalone Executables

This guide shows how to package any VoidUI daemon into a portable `.exe` file using PyInstaller — so users can run your daemon without installing Python.

---

## What a daemon folder contains

A daemon is a folder. To compile one, that folder needs three things:

| Requirement | What it is | Which examples |
|---|---|---|
| `app.py` | The daemon itself — the data it serves and the CLI. | all three |
| `daemon_core/` | The shared framework: the `/api/data` endpoint, the `X-API-Key` check, the CORS headers and the CLI flags. **Required.** | all three |
| extra modules | Any other `.py` your daemon imports. | `rss_parser.py` in example 02 |

So a daemon folder looks like this:

```
my_daemon/
├── app.py                 ← the daemon
├── daemon_core/           ← the shared framework
│   ├── __init__.py
│   └── void_daemon.py
└── my_modules.py          ← optional: whatever else your daemon imports
```

`daemon_core/` has to be **next to `app.py`** — the same folder, or one folder
up when the daemon runs from the repo. It is the HTTP layer — the endpoint,
the auth check, the headers, the flags — and `app.py` only holds your data.
Without the folder, the import fails and the daemon never starts:

```
ModuleNotFoundError: No module named 'daemon_core'
```

### Where `daemon_core/` lives

There are two places you will meet it, and the daemon's import block looks in
both:

| Situation | Where `daemon_core/` is |
|---|---|
| Running from the repo | `examples/daemon_core/` — one copy, shared by every example |
| Running from a download | The same folder as `app.py`, inside the zip |

The bundled examples keep one shared copy at the `examples/` root. The zips
each carry their own copy next to `app.py`, so an unzipped daemon runs with
`python app.py` and nothing else to set up.

---

## Prerequisites

```bash
pip install pyinstaller
```

Verify:

```bash
python -m PyInstaller --version
# Should print: 6.x.x
```

The daemon itself needs **Flask** — that is what `daemon_core` is built on:

```bash
pip install flask
```

---

## The steps to compile

### Step 1 — get the folder right

Copy the daemon and the framework into one folder and make sure the names
match exactly:

```
my_daemon/
├── app.py
├── daemon_core/
│   ├── __init__.py
│   └── void_daemon.py
└── my_modules.py      ← optional: whatever else your daemon imports
```

`app.py` must import the framework the way the bundled examples do, so the
daemon works whether `daemon_core/` is next to it or one folder up:

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

### Step 2 — build it

There are two ways. Both produce the same result: a single `my_daemon.exe`.

#### Option A — a `.spec` file (recommended)

A `.spec` file records the build as code. The bundled examples each ship one
at the project root, named after the daemon
(`01_hello_world.spec`, `02_rss_viewer.spec`, `03_multiformat_vault.spec`).

```bash
python -m PyInstaller --noconfirm --clean \
  --distpath examples/my_daemon \
  --workpath build/my_daemon \
  my_daemon.spec
```

| Flag | Purpose |
|------|---------|
| `--noconfirm` | Overwrites output without prompting |
| `--clean` | Clears build cache before starting |
| `--distpath` | Where to place the final `.exe` |
| `--workpath` | Temp build directory (safe to delete) |

`--distpath` and `--workpath` are **required** when using a `.spec` file:
PyInstaller takes the output directory from the command line, not from the
spec. The spec controls the *inputs* — the script and the import search path.

A portable spec derives every path from `SPECPATH`, the directory holding the
spec file, so it builds the same way on any machine:

```python
import os

ROOT = SPECPATH  # the directory containing this .spec file

# `daemon_core` lives at the examples/ root and is shared by every example
# daemon; a daemon's own modules (rss_parser) live in its own folder. Both
# have to be on the search path.
PATHEX = [
    os.path.join(ROOT, 'examples'),
    os.path.join(ROOT, 'examples', 'my_daemon'),
]

a = Analysis(
    [os.path.join(ROOT, 'examples', 'my_daemon', 'app.py')],
    pathex=PATHEX,
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='my_daemon',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

`pathex` matters: PyInstaller resolves imports at **build** time, so
`daemon_core` must be on the search path or the build produces an exe that
crashes on startup with `ModuleNotFoundError`. Two entries are needed: the
folder holding `daemon_core/`, and the daemon's own folder for its extra
modules.

#### Option B — a direct command line

For a throwaway daemon with no `.spec` file, run this from the `examples/`
folder:

```bash
python -m PyInstaller \
  --noconfirm \
  --onefile \
  --clean \
  --paths "." \
  --paths "my_daemon" \
  --name "my_daemon" \
  --distpath "my_daemon" \
  --workpath "../build/my_daemon" \
  "my_daemon/app.py"
```

| Flag | Purpose |
|------|---------|
| `--onefile` | Bundles everything into a single portable `.exe` |
| `--noconfirm` | Overwrites output without prompting |
| `--clean` | Clears build cache before starting |
| `--paths` | Adds a directory to Python's import search path — needs it twice |
| `--name` | Output filename (without `.exe`) |
| `--distpath` | Where to place the final `.exe` |
| `--workpath` | Temp build directory (safe to delete) |

Two `--paths` entries again: `"."` is the folder holding `daemon_core/`, and
`"my_daemon"` is the daemon's own folder. Use relative paths — an absolute
path baked into a build command means the next person (or CI) has to edit it
before the build works.

### Step 3 — check the result

Run the `.exe` and confirm it starts:

```cmd
examples\my_daemon\my_daemon.exe --port 8800 --key testkey
```

Then connect VoidUI to `http://127.0.0.1:8800` with key `testkey`.

A quick check that the daemon is actually serving, without opening the player:

```cmd
curl -H "X-API-Key: testkey" http://127.0.0.1:8800/api/data
```

---

## Output

After a successful build (~30–60 seconds):

```
examples/
└── my_daemon/
    └── my_daemon.exe   ← Your portable daemon
```

The `build/` directory contains intermediate files — it is gitignored and safe
to delete.

The `.exe` has `daemon_core` frozen inside it, so it runs on its own. The
source still needs the folder next to it — which is why the published zips
ship both.

---

## Example: Building the Bundled Examples

```bash
python -m PyInstaller --noconfirm --clean \
  --distpath examples/01_hello_world \
  --workpath build/01_hello_world \
  01_hello_world.spec

python -m PyInstaller --noconfirm --clean \
  --distpath examples/02_rss_viewer \
  --workpath build/02_rss_viewer \
  02_rss_viewer.spec

python -m PyInstaller --noconfirm --clean \
  --distpath examples/03_multiformat_vault \
  --workpath build/03_multiformat_vault \
  03_multiformat_vault.spec
```

All three read the shared `examples/daemon_core/` — one copy of the framework
serves every daemon.

> If a build fails with `PermissionError: ... Access is denied` on the `.exe`,
> a copy of the old executable is still running. Stop it and build again.

---

## Including Extra Files

If your daemon loads templates, data files, or assets at runtime, bundle them
using `--add-data`:

```bash
python -m PyInstaller \
  --onefile \
  --add-data "my_daemon/templates;templates" \
  --add-data "my_daemon/files;files" \
  "my_daemon/app.py"
```

In a `.spec` file, the same thing goes in the `datas` list:

```python
a = Analysis(
    [SCRIPT],
    pathex=PATHEX,
    datas=[(os.path.join(ROOT, 'examples', 'my_daemon', 'templates'), 'templates')],
    ...
)
```

Then in your Python code, access bundled files via:

```python
import sys, os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller EXE."""
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, relative_path)

# Usage:
template = open(resource_path("templates/index.html")).read()
```

---

## Hidden Imports

If PyInstaller misses a module (common with dynamic imports in Flask), add it
manually:

```bash
python -m PyInstaller --onefile \
  --hidden-import flask \
  --hidden-import xml.etree.ElementTree \
  "app.py"
```

In a `.spec` file, they go in the `hiddenimports` list.

---

## Reducing EXE Size

- **Use a virtual environment** just for the daemon to avoid bundling unused packages.
- **Exclude heavy packages** with `--exclude-module`:
  ```bash
  --exclude-module matplotlib --exclude-module numpy
  ```
- Typical VoidUI daemon EXE: **~8–12MB** (Python runtime + Flask + stdlib).

---

## Windows Antivirus Notice

PyInstaller-built executables may trigger Windows Defender or other AV software because they are self-extracting archives. This is a false positive. To reduce false positives:

- Sign your EXE with a code-signing certificate
- Or distribute alongside the Python source for users who prefer to run from source

---

## Testing Your EXE

After building, test in a clean terminal (no active Python environment):

```cmd
examples\my_daemon\my_daemon.exe --port 8800 --key testkey
```

Then connect VoidUI to `http://127.0.0.1:8800` with key `testkey`.

A quick check that the daemon is actually serving, without opening the player:

```cmd
curl -H "X-API-Key: testkey" http://127.0.0.1:8800/api/data
```

---

## Distribution Structure

When distributing, every download is a zip and the folder behind it is never
published. What the user sees:

- `VoidUI-win.zip` — the player: `VoidUI.exe` and `launcher.exe`.
- `01_hello_world-win.zip` — the daemon EXE, its `app.py`, its `daemon_core/`
  and its README.
- `02_rss_viewer-win.zip` — the same, plus `rss_parser.py`.
- `03_multiformat_vault-win.zip` — the same.

Each daemon zip carries its **own** copy of `daemon_core/`, sitting next to
`app.py`. The repo keeps one shared copy at `examples/daemon_core/`; the zip
step copies that folder in, so an unzipped daemon runs with `python app.py`
and nothing else to set up:

```
01_hello_world-win.zip
├── 01_hello_world.exe
├── app.py
├── daemon_core/          ← copied in from examples/daemon_core/
│   ├── __init__.py
│   └── void_daemon.py
└── README.md
```

Users download a zip, unzip it, double-click a daemon `.exe`, then launch
`VoidUI.exe` and connect.

**Ship the viewer as a zip of both binaries.** `launcher.exe` is the native
WebView2 window and `VoidUI.exe` is the backend that talks to it; the backend
looks for the launcher beside itself at startup and exits if it is missing:

```
Error: launcher binary not found (looked at: <dir>/launcher.exe)
```

A single-file download of `VoidUI.exe` therefore arrives broken. Zip the two
together and link the zip.

> **Zip by hand.** The build tool also has a `publish` command, but it writes
> an *updater payload* for the app's own auto-update channel — the source
> bundle with the binaries prepended. That is not a runnable app for a person
> to download. Zip the two binaries yourself for the human download.
