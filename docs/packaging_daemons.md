# Packaging Daemons as Standalone Executables

This guide shows how to package any VoidUI daemon into a portable `.exe` file using PyInstaller — so users can run your daemon without installing Python.

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

---

## Two Ways to Build

### Option A — a `.spec` file (recommended)

A `.spec` file records the build as code. The bundled examples each have one
at the repo root (`01_hello_world.spec`, `02_rss_viewer.spec`,
`03_multiformat_vault.spec`).

```bash
python -m PyInstaller --noconfirm --clean \
  --distpath examples/03_multiformat_vault \
  --workpath build/03_multiformat_vault \
  03_multiformat_vault.spec
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

a = Analysis(
    [os.path.join(ROOT, 'examples', 'my_daemon', 'app.py')],
    pathex=[ROOT],  # so `daemon_core` is importable at build time
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
crashes on startup with `ModuleNotFoundError`.

### Option B — a direct command line

For a throwaway daemon with no `.spec` file:

```bash
python -m PyInstaller \
  --noconfirm \
  --onefile \
  --clean \
  --paths . \
  --name "my_daemon" \
  --distpath "examples/my_daemon" \
  --workpath "build/my_daemon" \
  "examples/my_daemon/app.py"
```

| Flag | Purpose |
|------|---------|
| `--onefile` | Bundles everything into a single portable `.exe` |
| `--noconfirm` | Overwrites output without prompting |
| `--clean` | Clears build cache before starting |
| `--paths` | Adds the repo root to Python's import search path (needed for `daemon_core`) |
| `--name` | Output filename (without `.exe`) |
| `--distpath` | Where to place the final `.exe` |
| `--workpath` | Temp build directory (safe to delete) |

Use `--paths .` — a relative path — rather than an absolute one. An absolute
path baked into a build command means the next person (or CI) has to edit it
before the build works.

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

> If a build fails with `PermissionError: ... Access is denied` on the `.exe`,
> a copy of the old executable is still running. Stop it and build again.

---

## Including Extra Files

If your daemon loads templates, data files, or assets at runtime, bundle them
using `--add-data`:

```bash
python -m PyInstaller \
  --onefile \
  --add-data "examples/my_daemon/templates;templates" \
  --add-data "examples/my_daemon/files;files" \
  "examples/my_daemon/app.py"
```

In a `.spec` file, the same thing goes in the `datas` list:

```python
a = Analysis(
    [SCRIPT],
    pathex=PATHEX,
    datas=[('examples/my_daemon/templates', 'templates')],
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

When distributing:

```
VoidUI-Release/
├── player/
│   └── VoidUI-win.zip   ← The desktop viewer: VoidUI.exe + launcher.exe
├── examples/
│   ├── 01_hello_world/
│   │   └── 01_hello_world-win.zip   ← The EXE, app.py and README.md
│   ├── 02_rss_viewer/
│   │   └── 02_rss_viewer-win.zip
│   └── 03_multiformat_vault/
│       └── 03_multiformat_vault-win.zip
└── docs/
    └── *.md
```

Users download a zip, unzip it, double-click a daemon `.exe`, then launch
`VoidUI.exe` and connect.

**Ship the viewer as a zip of both binaries.** `launcher.exe` is the native
WebView2 window and `VoidUI.exe` is the backend that talks to it; the backend
looks for the launcher beside itself at startup and exits if it is missing:

```
Error: tinyjs launcher binary not found (looked at: <dir>/launcher.exe)
```

A single-file download of `VoidUI.exe` therefore arrives broken. Zip the two
together and link the zip.

> **Not `tinyjs publish`.** That command writes an *updater payload* — the
> source bundle with the binaries prepended. Unzipping it gives you
> `bridge.js` and `frontend/`, not a runnable app. Zip `dist/` by hand for
> the human download.
