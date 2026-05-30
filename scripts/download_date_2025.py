#!/usr/bin/env python3
"""Download DATE 2025 papers from an IEEE Xplore CSV export into DATE_2025/papers/."""
from __future__ import annotations

import argparse
import csv
import fcntl
import os
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CSV = REPO / "references" / "conferences" / "DATE_2025" / "ieee_xplore_export.csv"
OUT_DIR = REPO / "references" / "conferences" / "DATE_2025" / "papers"
UW_IEEE_LOGIN = (
    "https://patron.library.wisc.edu/authn/login?"
    "url=https://ieeexplore.ieee.org/search/advanced"
)
# UW EZproxy allows only 2 concurrent remote-access sessions. Do not run multiple
# download/login scripts or browsers at once — stale sessions trigger
# "Remote Access System Problem".
UW_IEEE_ENTRY = "https://search.library.wisc.edu/database/UWI12369"
TEST_ARNUMBER = "10992912"  # Cocktail
SESSION_FILE = REPO / "references" / "conferences" / "DATE_2025" / ".ieee_session.json"
LOCK_FILE = REPO / "references" / "conferences" / "DATE_2025" / ".download.lock"


class DownloadLock:
    """Ensure only one download/login browser runs at a time."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.handle = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("w")
        try:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit(
                f"Another DATE download is already running (lock: {self.path}).\n"
                "Close the other automation Chrome window or run: pkill -f download_date_2025.py"
            )
        self.handle.write(str(os.getpid()))
        self.handle.flush()
        return self

    def __exit__(self, *_args) -> None:
        if self.handle:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            self.handle.close()
            self.path.unlink(missing_ok=True)


def load_chrome_cookies(context) -> None:
    try:
        import browser_cookie3
    except ImportError:
        return

    cookies = []
    seen: set[tuple[str, str, str]] = set()
    for domain in (
        "ieee.org",
        "ieeexplore.ieee.org",
        "library.wisc.edu",
        "ezproxy.library.wisc.edu",
        "wisc.edu",
    ):
        try:
            for cookie in browser_cookie3.chrome(domain_name=domain):
                key = (cookie.domain, cookie.name, cookie.path or "/")
                if key in seen:
                    continue
                seen.add(key)
                dom = cookie.domain
                if dom and not dom.startswith("."):
                    dom = "." + dom
                cookies.append(
                    {
                        "name": cookie.name,
                        "value": cookie.value,
                        "domain": dom,
                        "path": cookie.path or "/",
                        "secure": bool(cookie.secure),
                    }
                )
        except Exception:
            continue
    if cookies:
        context.add_cookies(cookies)


def slugify(title: str) -> str:
    short = re.sub(r"[^a-zA-Z0-9]+", "_", title.lower()).strip("_")[:70]
    return f"date2025_{short}"


def arnumber_from_row(row: dict) -> str | None:
    pdf_link = row.get("PDF Link", "")
    match = re.search(r"arnumber=(\d+)", pdf_link)
    if match:
        return match.group(1)
    doi = row.get("DOI", "")
    match = re.search(r"\.(\d+)$", doi)
    return match.group(1) if match else None


def load_rows(csv_path: Path) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8", errors="replace") as handle:
        return list(csv.DictReader(handle))


def is_pdf(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 1000 and path.read_bytes()[:4] == b"%PDF"


def ezproxy(url: str) -> str:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if not parsed.hostname:
        return url
    host = parsed.hostname.replace(".", "-")
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    return f"https://{host}.ezproxy.library.wisc.edu{path}"


def pdf_urls(arnumber: str) -> list[str]:
    base = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber={arnumber}"
    return [
        ezproxy(base),
        ezproxy(f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?arnumber={arnumber}"),
        base,
    ]


def is_blocking_auth(page) -> bool:
    """Pages where we must not navigate away (Duo / NetID password entry only)."""
    url = page.url.lower()
    return "duosecurity.com" in url or "login.wisc.edu" in url


def has_pdf_access(page, *, navigate: bool = True) -> bool:
    url = ezproxy(f"https://ieeexplore.ieee.org/document/{TEST_ARNUMBER}")
    if navigate:
        page.goto(url, timeout=120_000, wait_until="domcontentloaded")
    title = page.title().lower()
    if "remote access system problem" in title or "access library resource" in title:
        return False
    btn = page.locator('[data-analytics_identifier="document-lh-action-downloadpdf"]')
    if not btn.count():
        return False
    hint = (btn.first.get_attribute("title") or "").lower()
    return "do not have access" not in hint


def attempt_netid_login(page) -> bool:
    """Fill UW NetID credentials from env (NETID, NETID_PASSWORD); Duo still required."""
    netid = os.environ.get("NETID", "").strip()
    password = os.environ.get("NETID_PASSWORD", "").strip()
    if not netid or not password:
        return False

    page.goto(UW_IEEE_LOGIN, timeout=120_000, wait_until="commit")
    if "login.wisc.edu" not in page.url:
        sign_in = page.locator("text=NetID Sign In")
        if sign_in.count():
            sign_in.first.click()
            page.wait_for_load_state("commit", timeout=60_000)

    try:
        page.wait_for_selector("#j_username", timeout=30_000)
    except Exception:
        print("Could not find UW login form.")
        return False
    page.locator("#j_username").fill(netid)
    page.locator("#j_password").fill(password)
    page.locator('button:has-text("Log In")').click()
    page.wait_for_load_state("commit", timeout=120_000)
    print("NetID submitted. Approve the Duo prompt on your phone if asked.")
    return True


def wait_for_login(page, timeout_s: int, *, auto_login: bool) -> bool:
    on_auth = is_blocking_auth(page)
    if auto_login and not on_auth:
        attempt_netid_login(page)
    elif not on_auth:
        print(
            "Opening UW IEEE login — use this browser window only.\n"
            f"If you see '2 concurrent logins', close all library/ezproxy tabs, "
            "wait ~15 minutes, then re-run once."
        )
        try:
            page.goto(UW_IEEE_ENTRY, timeout=120_000, wait_until="commit")
            go = page.locator("text=Go to this Database")
            if go.count():
                go.first.click()
                page.wait_for_load_state("commit", timeout=60_000)
        except Exception:
            pass

    print(
        "Waiting for login to finish. Approve Duo on your phone if prompted.\n"
        "The browser will NOT refresh while Duo is showing."
    )
    deadline = time.time() + timeout_s
    checked_access = False

    while time.time() < deadline:
        # Never navigate away during Duo / NetID pages — let the user finish MFA.
        if is_blocking_auth(page):
            time.sleep(2)
            continue

        # After auth pages, wait for redirects to settle once.
        if not checked_access:
            time.sleep(3)
            checked_access = True

        try:
            if has_pdf_access(page, navigate=True):
                print("Library access confirmed.")
                page.context.storage_state(path=str(SESSION_FILE))
                return True
        except Exception:
            pass

        # Re-check slowly; do not hammer the page while session may still be establishing.
        time.sleep(15)
        checked_access = False

    return False


def fetch_pdf(request, arnumber: str) -> bytes | None:
    referer = ezproxy(f"https://ieeexplore.ieee.org/document/{arnumber}")
    headers = {"Referer": referer}
    for url in pdf_urls(arnumber):
        try:
            resp = request.get(url, headers=headers, timeout=120_000)
            if resp.ok and resp.body()[:4] == b"%PDF":
                return resp.body()
        except Exception:
            continue
    return None


def download_all(
    csv_path: Path, out_dir: Path, *, login_timeout: int, auto_login: bool
) -> None:
    from playwright.sync_api import sync_playwright

    rows = load_rows(csv_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        storage = str(SESSION_FILE) if SESSION_FILE.exists() else None
        context = browser.new_context(accept_downloads=True, storage_state=storage)
        load_chrome_cookies(context)
        page = context.new_page()

        if has_pdf_access(page):
            print("IEEE library access already active.")
        elif not wait_for_login(page, login_timeout, auto_login=auto_login):
            browser.close()
            raise SystemExit(
                "Could not confirm IEEE PDF access. Log in via UW Libraries in the "
                "automation browser window and re-run."
            )
        else:
            page.context.storage_state(path=str(SESSION_FILE))

        request = context.request
        ok = skipped = failed = 0
        for index, row in enumerate(rows, start=1):
            title = row.get("Document Title", "").strip() or "untitled"
            arnumber = arnumber_from_row(row)
            if not arnumber:
                failed += 1
                print(f"[{index}/{len(rows)}] skip (no arnumber): {title[:60]}")
                continue

            dest = out_dir / f"{slugify(title)}.pdf"
            if is_pdf(dest):
                skipped += 1
                if index % 25 == 0 or index == len(rows):
                    print(f"[{index}/{len(rows)}] skip existing: {dest.name}")
                continue

            body = fetch_pdf(request, arnumber)
            if body:
                dest.write_bytes(body)
                ok += 1
                print(f"[{index}/{len(rows)}] saved {dest.name} ({len(body) // 1024} KB)")
            else:
                failed += 1
                print(f"[{index}/{len(rows)}] FAILED: {title[:60]}")
            time.sleep(0.75)

        browser.close()

    print("\nDone.")
    print(f"  downloaded: {ok}")
    print(f"  skipped (existing): {skipped}")
    print(f"  failed: {failed}")
    print(f"  output: {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download DATE 2025 papers from IEEE CSV export")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--out", type=Path, default=OUT_DIR)
    parser.add_argument(
        "--login-timeout",
        type=int,
        default=600,
        help="Seconds to wait for manual UW NetID login (default: 600)",
    )
    parser.add_argument(
        "--auto-login",
        action="store_true",
        help="Auto-fill NetID/password from NETID and NETID_PASSWORD env vars",
    )
    args = parser.parse_args()

    if not args.csv.exists():
        raise SystemExit(f"CSV not found: {args.csv}")

    with DownloadLock(LOCK_FILE):
        download_all(
            args.csv,
            args.out,
            login_timeout=args.login_timeout,
            auto_login=args.auto_login,
        )


if __name__ == "__main__":
    main()
