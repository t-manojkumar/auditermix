#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["yt-dlp>=2024.1.0"]
# ///
"""
auditermix  v1.0.0
Lightning-fast command-line music engine. Download. Play. Repeat.

Zero-arg launch:  python auditermix.py
uv launch:        uv run auditermix.py
"""

__version__ = "1.0.0"
__app__     = "auditermix"

import itertools
import os
import re
import shutil
import sys
import threading
import time
from pathlib import Path

from yt_dlp import YoutubeDL


# ══════════════════════════════════════════════════════════════════════════════
#  COLOUR SYSTEM — auto-disabled on non-TTY / Windows without ANSI support
# ══════════════════════════════════════════════════════════════════════════════

if sys.platform == "win32":
    os.system("")   # enable VT100 on Windows 10+

_TTY = sys.stdout.isatty()

def _c(code: str, t: str) -> str:
    return f"\033[{code}m{t}\033[0m" if _TTY else t

def orange(t): return _c("38;5;214", t)   # brand accent
def smoke(t):  return _c("38;5;245", t)   # muted text
def ghost(t):  return _c("38;5;238", t)   # decorative / very dim
def green(t):  return _c("38;5;120", t)   # success
def red(t):    return _c("38;5;203", t)   # error
def yellow(t): return _c("38;5;228", t)   # warning
def white(t):  return _c("97",       t)   # primary text
def bold(t):   return _c("1",        t)


# ══════════════════════════════════════════════════════════════════════════════
#  NOISE FILTER — mute known unactionable yt-dlp warnings
# ══════════════════════════════════════════════════════════════════════════════

_MUTED = re.compile(
    r"(GVS PO Token"
    r"|SABR streaming"
    r"|Falling back"
    r"|po_token"
    r"|Remote components challenge solver"
    r"|Signature solving failed"
    r"|n challenge solving failed"
    r"|Skipping unsupported client"
    r"|has already been recorded)",
    re.IGNORECASE,
)

_JS_RE = re.compile(
    r"(Signature solving failed"
    r"|n challenge solving failed"
    r"|Remote components challenge solver)",
    re.IGNORECASE,
)

_js_warned = False   # surface JS-challenge hint only once per session


# ══════════════════════════════════════════════════════════════════════════════
#  LOGGER
# ══════════════════════════════════════════════════════════════════════════════

def _strip_prefix(msg: str) -> str:
    return re.sub(r"^\[.*?\]\s[\w-]+:\s", "", msg).strip()


class SilentLogger:
    def debug(self, _: str) -> None:   pass
    def info(self,  _: str) -> None:   pass

    def warning(self, msg: str) -> None:
        global _js_warned
        clean = _strip_prefix(msg)
        if _JS_RE.search(clean):
            if not _js_warned:
                _js_warned = True
                _print_warning(
                    "JS challenge solver unavailable  "
                    + smoke("› install Node.js: https://nodejs.org")
                )
            return
        if _MUTED.search(clean):
            return
        _print_warning(clean)

    def error(self, msg: str) -> None:
        clean = _strip_prefix(msg)
        if _MUTED.search(clean):
            return
        _print_error(clean)


# ══════════════════════════════════════════════════════════════════════════════
#  SPINNER
# ══════════════════════════════════════════════════════════════════════════════

_BRAILLE = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class Spinner:
    """Thread-safe terminal spinner."""

    def __init__(self, label: str) -> None:
        self.label   = label
        self._stop   = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def _loop(self) -> None:
        for frame in itertools.cycle(_BRAILLE):
            if self._stop.is_set():
                break
            sys.stdout.write(f"\r  {orange(frame)}  {smoke(self.label)}   ")
            sys.stdout.flush()
            time.sleep(0.08)

    def __enter__(self) -> "Spinner":
        self._thread.start()
        return self

    def __exit__(self, *_) -> None:
        self._stop.set()
        self._thread.join()
        sys.stdout.write("\r" + " " * 64 + "\r")
        sys.stdout.flush()


# ══════════════════════════════════════════════════════════════════════════════
#  PRINT HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _ln() -> None:          print()
def _rule(w: int = 56):     print("  " + ghost("─" * w))
def _print_warning(m: str): print(f"\n  {yellow('◆')}  {smoke(m)}")
def _print_error(m: str):   print(f"\n  {red('✗')}  {m}")


# ══════════════════════════════════════════════════════════════════════════════
#  SPLASH
# ══════════════════════════════════════════════════════════════════════════════

_LOGO = (
    r"   ┌─┐┬ ┬┌┬┐┬┌┬┐┌─┐┬─┐┌┬┐┬─┐ ┬",
    r"   ├─┤│ │ ││││ │ ├┤ ├┬┘│││├┬┘  │",
    r"   ┴ ┴└─┘─┴┘┴ ┴ └─┘┴└─┴ ┴┴└─  o",
)

def print_splash() -> None:
    _ln()
    for line in _LOGO:
        print("  " + orange(line))
    _ln()
    print(f"  {smoke('lightning-fast command-line music engine')}")
    print(f"  {smoke('download  ·  tagged  ·  archived')}")
    print(f"  {ghost('v' + __version__ + '  ·  github.com/t-manojkumar/auditermix')}")
    _ln()
    _rule()
    _ln()


# ══════════════════════════════════════════════════════════════════════════════
#  CROSS-PLATFORM PATHS
# ══════════════════════════════════════════════════════════════════════════════

def get_music_dir() -> Path:
    d = Path.home() / "Music"
    d.mkdir(parents=True, exist_ok=True)
    return d

def get_archive_path() -> Path:
    """
    Platform-appropriate cache location:
      Windows → %LOCALAPPDATA%\\auditermix\\
      macOS   → ~/Library/Caches/auditermix/
      Linux   → ~/.cache/auditermix/  (respects $XDG_CACHE_HOME)
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA",
                    Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Caches"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME",
                    Path.home() / ".cache"))

    cache = base / "auditermix"
    cache.mkdir(parents=True, exist_ok=True)
    return cache / "downloaded.txt"


# ══════════════════════════════════════════════════════════════════════════════
#  SETTINGS
# ══════════════════════════════════════════════════════════════════════════════

CODECS: list[str] = ["m4a", "mp3", "opus", "flac"]

DEFAULTS: dict = {
    "codec":     "m4a",
    "quality":   "192",
    "thumbnail": True,
    "archive":   True,
}

def _codec_row(cfg: dict) -> str:
    return "  ·  ".join(
        bold(orange(c)) if c == cfg["codec"] else smoke(c)
        for c in CODECS
    )

def _bool_fmt(val: bool) -> str:
    return green("on") if val else smoke("off")

def print_settings(cfg: dict) -> None:
    _ln()
    print(f"  {ghost('◆')}  {white('settings')}")
    _ln()
    print(f"  {'codec':<14}{_codec_row(cfg)}")
    print(f"  {'quality':<14}{smoke(cfg['quality'] + ' kbps')}")
    print(f"  {'save to':<14}{smoke(str(get_music_dir()))}")
    print(f"  {'thumbnail':<14}{_bool_fmt(cfg['thumbnail'])}")
    print(f"  {'skip dupes':<14}{_bool_fmt(cfg['archive'])}")
    _ln()
    _rule()
    _ln()

def _prompt_bool(label: str) -> bool | None:
    raw = input(f"  {smoke(label + ' on/off')} {ghost('›')} ").strip().lower()
    if raw in ("on",  "yes", "y", "1"): return True
    if raw in ("off", "no",  "n", "0"): return False
    return None

def ask_settings(cfg: dict) -> dict:
    cfg = dict(cfg)
    print_settings(cfg)
    print(f"  {smoke('type a setting name to change it, or press')} {white('enter')} {smoke('to start')}")
    print(f"  {ghost('  codec  ·  quality  ·  thumbnail  ·  dupes  ·  reset')}")
    _ln()

    while True:
        try:
            key = input(f"  {orange('◆')}  {white('setting')} {ghost('›')} ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt

        if not key:
            break

        changed = True
        if key in ("codec", "c"):
            raw = input(
                f"  {smoke('choose codec')} "
                f"{ghost('[' + ' / '.join(CODECS) + ']')} {ghost('›')} "
            ).strip().lower()
            if raw in CODECS:
                cfg["codec"] = raw
            else:
                print(f"  {ghost('invalid codec — unchanged')}")
                changed = False

        elif key in ("quality", "q"):
            raw = input(
                f"  {smoke('bitrate kbps')} {ghost('[128 / 192 / 320]')} {ghost('›')} "
            ).strip()
            if raw.isdigit() and int(raw) > 0:
                cfg["quality"] = raw
            else:
                print(f"  {ghost('invalid bitrate — unchanged')}")
                changed = False

        elif key in ("thumbnail", "t"):
            result = _prompt_bool("thumbnail")
            if result is not None:
                cfg["thumbnail"] = result
            else:
                changed = False

        elif key in ("dupes", "d", "archive", "a"):
            result = _prompt_bool("skip duplicates")
            if result is not None:
                cfg["archive"] = result
            else:
                changed = False

        elif key in ("reset", "defaults"):
            cfg = dict(DEFAULTS)

        else:
            print(f"  {ghost('unknown — try: codec / quality / thumbnail / dupes / reset')}")
            changed = False

        if changed:
            print_settings(cfg)
            print(f"  {smoke('change another or press')} {white('enter')} {smoke('to start')}")
            _ln()

    _ln()
    return cfg


# ══════════════════════════════════════════════════════════════════════════════
#  URL COLLECTION
# ══════════════════════════════════════════════════════════════════════════════

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)

def collect_urls() -> list[str]:
    print(f"  {ghost('◆')}  {white('queue')}")
    _ln()
    print(f"  {smoke('paste one url per line')}")
    print(f"  {smoke('press')} {white('enter')} {smoke('on an empty line when done')}")
    _ln()

    urls: list[str] = []
    idx = 1
    while True:
        try:
            raw = input(f"  {orange('◆')}  {white(str(idx))} {ghost('›')} ").strip()
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt

        if not raw:
            if not urls:
                print(f"  {ghost('add at least one url first')}")
                continue
            break

        if not _URL_RE.match(raw):
            print(f"  {red('✗')}  {smoke('not a valid url — must start with http(s)://')}")
            continue

        urls.append(raw)
        idx += 1

    _ln()
    _rule()
    return urls


# ══════════════════════════════════════════════════════════════════════════════
#  QUEUE DISPLAY
# ══════════════════════════════════════════════════════════════════════════════

_ICONS: dict[str, str] = {
    "pending": smoke("○"),
    "active":  orange("◆"),
    "done":    green("✓"),
    "skipped": smoke("◇"),
    "error":   red("✗"),
}

def print_queue(urls: list[str], states: dict[int, str]) -> None:
    _ln()
    for i, url in enumerate(urls):
        state = states.get(i, "pending")
        icon  = _ICONS[state]
        label = url if len(url) <= 54 else url[:51] + "…"
        note  = smoke("  already in library") if state == "skipped" else ""
        text  = (
            white(label)  if state == "active"  else
            green(label)  if state == "done"    else
            smoke(label)
        )
        print(f"  {icon}  {text}{note}")
    _ln()


# ══════════════════════════════════════════════════════════════════════════════
#  PROGRESS BAR
# ══════════════════════════════════════════════════════════════════════════════

BAR_W = 28

def _bar(pct: float) -> str:
    n = max(0, min(BAR_W, int(BAR_W * pct / 100)))
    return ghost("▕") + orange("█" * n) + ghost("░" * (BAR_W - n)) + ghost("▏")

def _bar_full() -> str:
    return ghost("▕") + orange("█" * BAR_W) + ghost("▏")

def make_progress_hook():
    def hook(d: dict) -> None:
        status = d["status"]

        if status == "downloading":
            total      = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            speed      = d.get("speed")
            eta        = d.get("eta")

            spd   = f"{speed / 1024 / 1024:.1f} MB/s" if speed else "··· MB/s"
            eta_s = f"eta {eta}s" if eta is not None else "eta ?s"

            if total:
                pct  = downloaded * 100 / total
                line = (
                    f"\r  {_bar(pct)} {orange(f'{pct:5.1f}%')}"
                    f"  {smoke(spd)}  {ghost(eta_s)}   "
                )
            else:
                mb   = downloaded / 1024 / 1024
                line = (
                    f"\r  {ghost('▕' + '░' * BAR_W + '▏')}"
                    f"  {smoke(f'{mb:.1f} MB')}  {smoke(spd)}   "
                )
            sys.stdout.write(line)
            sys.stdout.flush()

        elif status == "finished":
            sys.stdout.write(
                f"\r  {_bar_full()} {orange('100.0%')}   \n"
            )
            sys.stdout.flush()

        elif status == "error":
            sys.stdout.write(f"\n  {red('✗')}  fragment error — retrying\n")
            sys.stdout.flush()

    return hook


# ══════════════════════════════════════════════════════════════════════════════
#  POSTPROCESSORS
# ══════════════════════════════════════════════════════════════════════════════

def build_postprocessors(codec: str, quality: str, embed_thumb: bool) -> list[dict]:
    pp: list[dict] = [
        {"key": "FFmpegMetadata", "add_metadata": True},
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec":  codec,
            "preferredquality": quality if codec != "flac" else "0",
        },
    ]
    if embed_thumb:
        pp += [
            {"key": "FFmpegThumbnailsConvertor", "format": "jpg"},
            {"key": "EmbedThumbnail"},
            # NOTE: Do NOT also set "embedthumbnail": True in ydl_opts —
            # EmbedThumbnail postprocessor is the single source of truth.
        ]
    return pp


# ══════════════════════════════════════════════════════════════════════════════
#  TITLE RESOLVER
# ══════════════════════════════════════════════════════════════════════════════

def resolve_title(url: str) -> str:
    """Silently fetch video title for display before downloading."""
    try:
        with YoutubeDL({
            "quiet":         True,
            "no_warnings":   True,
            "skip_download": True,
            "logger":        SilentLogger(),
            "extractor_args": {
                "youtube": {"player_client": ["tv_embedded", "android"]},
            },
        }) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("title", "") if info else ""
    except Exception:
        return ""


# ══════════════════════════════════════════════════════════════════════════════
#  SINGLE DOWNLOAD
# ══════════════════════════════════════════════════════════════════════════════

def download_one(url: str, cfg: dict, archive_path: Path | None) -> str:
    """
    Download audio for one URL.
    Returns: 'done' | 'skipped' | 'error'
    """
    music_dir = get_music_dir()
    playlist  = "list=" in url

    outtmpl = str(
        music_dir / "%(playlist_title)s" / "%(playlist_index)s - %(title)s.%(ext)s"
        if playlist else
        music_dir / "%(title)s.%(ext)s"
    )

    with Spinner("resolving"):
        title = resolve_title(url)

    if title:
        print(f"  {smoke('track')}  {white(title)}")
    if playlist:
        print(f"  {smoke('type')}   {ghost('playlist')}")
    _ln()

    ydl_opts: dict = {
        "format":             "bestaudio/best",
        "outtmpl":            outtmpl,
        "logger":             SilentLogger(),
        "restrictfilenames":  True,
        "writethumbnail":     cfg["thumbnail"],
        # tv_embedded + android: no JS challenge, no PO token required
        "extractor_args": {
            "youtube": {"player_client": ["tv_embedded", "android"]},
        },
        "retries":            10,
        "fragment_retries":   10,
        "concurrent_fragment_downloads": 1,
        "postprocessors":     build_postprocessors(
            cfg["codec"], cfg["quality"], cfg["thumbnail"]
        ),
        "progress_hooks":     [make_progress_hook()],
    }

    if archive_path:
        ydl_opts["download_archive"] = str(archive_path)

    result = "done"
    try:
        with YoutubeDL(ydl_opts) as ydl:
            if ydl.download([url]) == 101:
                result = "skipped"
    except SystemExit as exc:
        result = "skipped" if exc.code == 101 else "error"
    except Exception as exc:
        _print_error(str(exc))
        result = "error"

    _ln()
    if result == "done":
        with Spinner("encoding  ·  embedding tags + artwork"):
            time.sleep(0.6)
        print(f"  {green('✓')}  {smoke('saved to')}  {white(str(music_dir))}")
    elif result == "skipped":
        print(f"  {smoke('◇')}  {smoke('already in library — skipped')}")
    else:
        _print_error("download failed")

    return result


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

def print_summary(states: dict[int, str]) -> None:
    done    = sum(1 for s in states.values() if s == "done")
    skipped = sum(1 for s in states.values() if s == "skipped")
    errors  = sum(1 for s in states.values() if s == "error")

    _rule()
    _ln()
    print(f"  {ghost('◆')}  {white('session complete')}")
    _ln()
    if done:    print(f"  {green('✓')}  {bold(str(done))}  {smoke('downloaded')}")
    if skipped: print(f"  {smoke('◇')}  {bold(str(skipped))}  {smoke('already in library')}")
    if errors:  print(f"  {red('✗')}  {bold(str(errors))}  {smoke('failed')}")
    _ln()
    print(f"  {smoke('library')}  {white(str(get_music_dir()))}")
    _ln()


# ══════════════════════════════════════════════════════════════════════════════
#  PREFLIGHT CHECK
# ══════════════════════════════════════════════════════════════════════════════

def check_deps() -> None:
    if shutil.which("ffmpeg") is None:
        print(
            f"\n  {red('✗')}  ffmpeg is required but was not found in PATH\n\n"
            f"  {smoke('Install it:')}\n"
            f"  {ghost('Windows')}  winget install Gyan.FFmpeg\n"
            f"  {ghost('macOS')}    brew install ffmpeg\n"
            f"  {ghost('Ubuntu')}   sudo apt install ffmpeg\n"
            f"  {ghost('Fedora')}   sudo dnf install ffmpeg\n",
            file=sys.stderr,
        )
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    check_deps()

    try:
        print_splash()
        urls = collect_urls()
        cfg  = ask_settings(DEFAULTS)
    except KeyboardInterrupt:
        print(f"\n\n  {smoke('bye.')}\n")
        sys.exit(0)

    archive_path = get_archive_path() if cfg["archive"] else None
    states: dict[int, str] = {}

    for i, url in enumerate(urls):
        states[i] = "active"
        print_queue(urls, states)
        _rule()
        _ln()

        try:
            states[i] = download_one(url, cfg, archive_path)
        except KeyboardInterrupt:
            states[i] = "error"
            print(f"\n\n  {smoke('cancelled.')}\n")
            break

        _ln()
        _rule()
        _ln()

    print_summary(states)


if __name__ == "__main__":
    main()
