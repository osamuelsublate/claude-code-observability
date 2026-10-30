"""Expõe os títulos das sessões do Claude Code como métrica Prometheus.

Lê só os registros de título e de início de cada arquivo em ~/.claude/projects.
O conteúdo das conversas não é lido nem enviado.
"""

import json
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PROJECTS_DIR = Path(os.environ.get("CLAUDE_PROJECTS_DIR", "/claude-projects"))
PORT = int(os.environ.get("PORT", "9101"))

_cache: dict[Path, tuple[tuple[int, int], dict | None]] = {}


def read_session(path: Path) -> dict | None:
    title = None
    cwd = None
    started = None
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if '"custom-title"' not in line and (cwd and started):
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("type") == "custom-title":
                title = rec.get("customTitle") or title
            cwd = cwd or rec.get("cwd")
            started = started or rec.get("timestamp")
    if not started:
        return None
    session_id = path.stem
    when = datetime.fromisoformat(started.replace("Z", "+00:00")).astimezone(timezone.utc)
    return {
        "session_id": session_id,
        "title": title or session_id[:8],
        "project_dir": Path(cwd).name if cwd else "",
        "started": when.strftime("%Y-%m-%d %H:%M"),
    }


def sessions() -> list[dict]:
    out = []
    for path in PROJECTS_DIR.glob("*/*.jsonl"):
        try:
            st = path.stat()
        except OSError:
            continue
        key = (st.st_mtime_ns, st.st_size)
        cached = _cache.get(path)
        if cached and cached[0] == key:
            info = cached[1]
        else:
            try:
                info = read_session(path)
            except OSError:
                info = None
            _cache[path] = (key, info)
        if info:
            out.append(info)
    return out


def escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def render() -> str:
    lines = [
        "# HELP claude_code_session_info Título e projeto de cada sessão local do Claude Code.",
        "# TYPE claude_code_session_info gauge",
    ]
    for s in sessions():
        labels = ", ".join(f'{k}="{escape(v)}"' for k, v in s.items())
        labels += f', display="{escape(s["started"] + " · " + s["title"])}"'
        lines.append(f"claude_code_session_info{{{labels}}} 1")
    return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/metrics":
            self.send_error(404)
            return
        body = render().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    if not PROJECTS_DIR.is_dir():
        print(f"diretório não encontrado: {PROJECTS_DIR}", file=sys.stderr)
        sys.exit(1)
    print(f"lendo {PROJECTS_DIR}, servindo em :{PORT}/metrics", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
