# Changelog

All notable changes are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/)

---

## [1.0.0] — 2025-02-17

### Added
- Interactive terminal UI — no command-line arguments needed
- Queue system — paste multiple URLs, processed in order with live state display
- Inline settings editor — codec, quality, thumbnail, duplicate detection
- Codec support: M4A (default), MP3, Opus, FLAC
- Live progress bar with speed + ETA
- Braille spinner for resolving and encoding phases
- Title pre-fetch before download starts (shown as track header)
- Duplicate detection via persistent download archive
- Cross-platform archive paths: `%LOCALAPPDATA%`, `~/Library/Caches`, `$XDG_CACHE_HOME`
- Playlist detection — auto-grouped into `~/Music/<playlist>/` subfolders
- Metadata embedding — title, artist, album tags via FFmpegMetadata
- Cover art embedding — thumbnail → JPEG → embedded (no double-embed bug)
- Player clients: `tv_embedded` + `android` — no JS challenge, no PO token
- Noise filter — known unactionable yt-dlp warnings silenced
- JS-challenge hint collapsed from 3 raw lines into one actionable message
- ANSI colour system — auto-disabled on non-TTY / piped output
- Windows ANSI enablement via `os.system("")` + VT100 registry key
- Auto-install scripts: Windows (`winget`), macOS (`brew`), Linux (`apt/dnf/pacman/apk`)
- uv inline script metadata (`# /// script`) for zero-setup launch
- Session summary: downloaded / skipped / failed counts
- MIT licence
