"""Machine-readable run log for the scheduled scripts (Backup / Dubstep / LoFi).

Each run appends ONE JSON line to the run log (default ``<repo>/runs/runs.jsonl``,
override with env ``AUTOFY_RUNLOG``). The file is pruned to the last ``KEEP`` runs.
A dashboard aggregator (nas repo: deploy/autofy-stats.py) reads it.

Usage::

    from util import runlog

    with runlog.Run("Backup"):
        runlog.target("Techno", set_id="...")       # start a per-playlist record
        runlog.source("<playlist id>", ok=True, tracks=120)
        runlog.update(status="added", added=12)
        runlog.error(exc, where="fetch")            # non-fatal error

Guarantees: every function here swallows its own errors — the run log can never
break the script it observes. No track data, tokens or config are recorded: only
playlist ids/names, counts, statuses and (redacted, truncated) error messages.
Stdlib only.
"""

import datetime
import json
import os
import re
import socket
import sys
import time
import traceback

SCHEMA = 1
KEEP = 500           # runs kept after pruning
PRUNE_AT = KEEP + 50  # prune only when this many lines exist (avoid rewriting every run)
MAX_MSG = 300

_current = None

try:
    import fcntl  # POSIX only; on Windows we just skip locking
except ImportError:  # pragma: no cover
    fcntl = None


def _now():
    return datetime.datetime.now().astimezone()


def _log_path():
    p = os.environ.get("AUTOFY_RUNLOG")
    if p:
        return p
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runs", "runs.jsonl")


_REDACT = [
    (re.compile(r"(?i)(access_token|refresh_token|client_secret|token|secret|password|auth_code)([\"']?\s*[:=]\s*[\"']?)[^\s\"'&,}]+"), r"\1\2***"),
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+"), "Bearer ***"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"), "gh*_***"),
]


def _clean(msg) -> str:
    try:
        s = str(msg)
        s = re.sub(r"\x1b\[[0-9;]*m", "", s)  # ANSI colours
        for rx, rep in _REDACT:
            s = rx.sub(rep, s)
        s = " ".join(s.split())
        return s[:MAX_MSG] + ("…" if len(s) > MAX_MSG else "")
    except Exception:
        return "<unprintable>"


def _err(exc, where=None) -> dict:
    d = {"type": type(exc).__name__ if isinstance(exc, BaseException) else "str", "msg": _clean(exc)}
    status = getattr(exc, "http_status", None)
    if isinstance(status, int):
        d["http"] = status
    if where:
        d["where"] = str(where)[:60]
    return d


class Run:
    """Context manager around one script run. Records exit code and fatal errors."""

    def __init__(self, script: str):
        self.rec = None
        try:
            self.t0 = time.monotonic()
            self.rec = {
                "v": SCHEMA,
                "script": str(script),
                "start": _now().isoformat(timespec="seconds"),
                "end": None,
                "duration_s": None,
                "exit_code": None,
                "status": None,
                "argv": [_clean(a)[:60] for a in sys.argv[1:4]],
                "host": socket.gethostname()[:40],
                "errors": [],
                "targets": [],
                "extra": {},
            }
            self.target = None
        except Exception:
            self.rec = None

    def __enter__(self):
        global _current
        if self.rec is not None:
            _current = self
        return self

    def __exit__(self, exc_type, exc, tb):
        global _current
        try:
            if self.rec is not None:
                if exc_type is None:
                    code = 0
                elif issubclass(exc_type, SystemExit):
                    c = exc.code if exc is not None else 0
                    code = c if isinstance(c, int) else (0 if c is None else 1)
                elif issubclass(exc_type, KeyboardInterrupt):
                    code = 130
                    self.rec["errors"].append({"type": "KeyboardInterrupt", "msg": "interrupted", "where": "fatal"})
                else:
                    code = 1
                    e = _err(exc, "fatal")
                    try:
                        fr = traceback.extract_tb(tb)[-1]
                        e["at"] = f"{os.path.basename(fr.filename)}:{fr.lineno}"
                    except Exception:
                        pass
                    self.rec["errors"].append(e)
                self._finish(code)
        except Exception:
            pass
        finally:
            _current = None
        return False  # never swallow the script's own exception

    def _finish(self, code):
        r = self.rec
        r["end"] = _now().isoformat(timespec="seconds")
        r["duration_s"] = round(time.monotonic() - self.t0, 1)
        r["exit_code"] = code
        has_err = bool(r["errors"]) or any(
            t.get("status") == "error" or t.get("errors") or any(not s.get("ok") for s in t.get("sources", []))
            for t in r["targets"]
        )
        if code != 0:
            r["status"] = "failed"
        elif has_err:
            r["status"] = "partial"
        else:
            r["status"] = "ok"
        _append(r)
        _refresh_stats()


def _append(rec: dict):
    path = _log_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        line = json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n"
        for _ in range(5):
            f = open(path, "a+", encoding="utf-8")
            if not fcntl:
                break
            fcntl.flock(f, fcntl.LOCK_EX)
            # a concurrent prune may have replaced the file while we waited for the lock
            try:
                if os.fstat(f.fileno()).st_ino == os.stat(path).st_ino:
                    break
            except FileNotFoundError:
                pass
            f.close()
        with f:
            try:
                f.write(line)
                f.flush()
                f.seek(0)
                lines = f.readlines()
                if len(lines) > PRUNE_AT:
                    tmp = path + ".tmp"
                    with open(tmp, "w", encoding="utf-8") as t:
                        t.writelines(lines[-KEEP:])
                        t.flush()
                        os.fsync(t.fileno())
                    os.replace(tmp, path)
            finally:
                if fcntl:
                    fcntl.flock(f, fcntl.LOCK_UN)
    except Exception as e:
        print(f"[runlog] could not write run log {path}: {e}", file=sys.stderr)


def _refresh_stats():
    """Optionally rebuild the dashboard data right after a run (env AUTOFY_STATS_SCRIPT)."""
    script = os.environ.get("AUTOFY_STATS_SCRIPT")
    if not script or not os.path.isfile(script):
        return
    try:
        import subprocess

        subprocess.run([sys.executable, script], timeout=120, check=False)
    except Exception as e:
        print(f"[runlog] stats refresh failed: {e}", file=sys.stderr)


# ---- recording helpers: all no-ops outside a Run, none of them ever raise ----

def target(name, set_id=None, **fields):
    """Start a new per-playlist record; later source()/update() calls attach to it."""
    try:
        if _current is None:
            return
        t = {"name": str(name)[:120], "set": set_id, "status": None, "added": 0, "sources": [], "errors": []}
        t.update(fields)
        _current.rec["targets"].append(t)
        _current.target = t
    except Exception:
        pass


def source(source_id, ok: bool, error=None, tracks=None):
    try:
        if _current is None or _current.target is None:
            return
        s = {"id": str(source_id)[:100], "ok": bool(ok)}
        if tracks is not None:
            s["tracks"] = int(tracks)
        if error is not None:
            s.update({k: v for k, v in _err(error).items() if k != "where"})
        _current.target["sources"].append(s)
    except Exception:
        pass


def update(**fields):
    """Set fields on the current target (status, added, existing, …)."""
    try:
        if _current is None or _current.target is None:
            return
        _current.target.update(fields)
    except Exception:
        pass


def error(exc, where=None):
    """Record a non-fatal error — on the current target if there is one, else on the run."""
    try:
        if _current is None:
            return
        e = _err(exc, where)
        if _current.target is not None:
            _current.target["errors"].append(e)
        else:
            _current.rec["errors"].append(e)
    except Exception:
        pass


def run_error(exc, where=None):
    """Record an error on the run itself (e.g. auth failure), regardless of target."""
    try:
        if _current is None:
            return
        _current.rec["errors"].append(_err(exc, where))
    except Exception:
        pass


def extra(**fields):
    """Script-specific summary values (small scalars only)."""
    try:
        if _current is None:
            return
        _current.rec["extra"].update(fields)
    except Exception:
        pass


def end_target():
    try:
        if _current is not None:
            _current.target = None
    except Exception:
        pass
