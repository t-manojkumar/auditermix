<div align="center">

```
   ┌─┐┬ ┬┌┬┐┬┌┬┐┌─┐┬─┐┌┬┐┬─┐ ┬
   ├─┤│ │ ││││ │ ├┤ ├┬┘│││├┬┘  │
   ┴ ┴└─┘─┴┘┴ ┴ └─┘┴└─┴ ┴┴└─  o
```

**Lightning-fast command-line music engine.**  
Download. Play. Repeat.

[![Python](https://img.shields.io/badge/python-3.11+-orange?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey?style=flat-square)](https://github.com/t-manojkumar/auditermix)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![yt-dlp](https://img.shields.io/badge/powered%20by-yt--dlp-red?style=flat-square)](https://github.com/yt-dlp/yt-dlp)

</div>

---

## What it looks like

```
   ┌─┐┬ ┬┌┬┐┬┌┬┐┌─┐┬─┐┌┬┐┬─┐ ┬
   ├─┤│ │ ││││ │ ├┤ ├┬┘│││├┬┘  │
   ┴ ┴└─┘─┴┘┴ ┴ └─┘┴└─┴ ┴┴└─  o

  lightning-fast command-line music engine
  download  ·  tagged  ·  archived
  v1.0.0  ·  github.com/t-manojkumar/auditermix
  ────────────────────────────────────────────────────────

  ◆  queue

  paste one url per line
  press enter on an empty line when done

  ◆  1 ›  https://music.youtube.com/watch?v=xxxx
  ◆  2 ›  https://www.youtube.com/watch?v=yyyy
  ◆  3 ›

  ◆  settings

  codec          m4a  ·  mp3  ·  opus  ·  flac
  quality        192 kbps
  save to        ~/Music
  thumbnail      on
  skip dupes     on

  ◆  setting ›  [enter]

  ○  https://music.youtube.com/watch?v=xxxx  ← queued
  ◆  https://www.youtube.com/watch?v=yyyy    ← downloading
  ○  ...

  track   Daft Punk - Get Lucky
  ▕████████████████████████████▏ 100.0%
  ⠹  encoding · embedding tags + artwork
  ✓  saved to  ~/Music

  ◆  session complete
  ✓  2  downloaded
  ◇  1  already in library
```

---

## Features

| | Feature | Details |
|---|---|---|
| 🎯 | **Zero args** | Just run — prompts guide you through everything |
| 📋 | **Queue system** | Paste multiple URLs, live status per track |
| 🎵 | **Codecs** | M4A (default) · MP3 · Opus · FLAC |
| 🏷️ | **Metadata** | Title, artist, album tags auto-embedded |
| 🖼️ | **Cover art** | Thumbnail fetched and embedded as artwork |
| 🔁 | **Duplicate skip** | Persistent archive — never re-downloads |
| 📂 | **Playlists** | Auto-grouped into `~/Music/<playlist>/` |
| 📊 | **Progress** | Live bar with speed + ETA |
| 🔇 | **Clean output** | Noisy yt-dlp warnings filtered intelligently |
| 🌈 | **Colours** | ANSI palette — auto-disabled in piped output |
| 🖥️ | **Cross-platform** | Windows · macOS · Linux |

---

## Installation

### Windows — one click

> `install.bat` auto-installs Python 3.11, ffmpeg, and yt-dlp if missing.

```
1.  Download and unzip this repo
2.  Double-click  install.bat       ← run once
3.  Double-click  run.bat           ← run every time
    or  double-click  auditermix.bat  on your Desktop
```

### macOS — one click

```bash
# Run once
bash install.sh

# Run every time
bash run.sh
# or double-click auditermix.command in Finder
```

> `install.sh` auto-installs Python + ffmpeg via Homebrew if missing.

### Linux (Ubuntu / Debian / Fedora / Arch / Alpine)

```bash
bash install.sh   # auto-detects distro, installs deps
bash run.sh
```

### uv — zero setup

[uv](https://docs.astral.sh/uv/) reads the inline dependency block and handles
everything — no venv, no pip install, no installer script needed.

```bash
# Install uv once
curl -LsSf https://astral.sh/uv/install.sh | sh          # macOS/Linux
powershell -c "irm https://astral.sh/uv/install.ps1|iex" # Windows

# Run auditermix directly
uv run auditermix.py
```

---

## Requirements

| Dependency | Purpose | Auto-installed? |
|---|---|---|
| Python 3.11+ | Runtime | ✅ `winget` / `brew` / `apt` |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube extraction | ✅ `pip` |
| [ffmpeg](https://ffmpeg.org) | Encoding + tag/art embedding | ✅ `winget` / `brew` / `apt` |

---

## Build a standalone executable

Distribute a single `.exe` with no Python required on the target machine:

```bash
pip install pyinstaller
pyinstaller --onefile --console --name auditermix \
    --collect-all yt_dlp auditermix.py

# Output:
#   dist/auditermix.exe   (Windows)
#   dist/auditermix       (macOS / Linux)
```

> **Note:** ffmpeg must still be installed on the target machine.

---

## File structure

```
auditermix/
├── auditermix.py              ← the entire app (single file)
├── install.bat                ← Windows setup (run once)
├── install.sh                 ← macOS / Linux setup (run once)
├── requirements.txt
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md
    │   └── feature_request.md
    └── PULL_REQUEST_TEMPLATE.md
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).  
Bug reports → use the [issue template](.github/ISSUE_TEMPLATE/bug_report.md).

---

## Legal

For personal use only. Respect YouTube's [Terms of Service](https://www.youtube.com/t/terms)  
and only download content you have rights to access.

---

## License

MIT — see [LICENSE](LICENSE).
