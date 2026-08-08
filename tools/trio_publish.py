#!/usr/bin/env python3
"""Validate and safely publish the Lawn-A-Mercy public website.

This repository is intentionally separate from the private Lawn-A-Mercy
manager. The publisher refuses unexpected paths, concurrent edits, remote
divergence, and unapproved public gallery images.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data" / "site.json"
EXPECTED_REMOTE = "https://github.com/scasimir2021/lawn-a-mercy.git"
EXPECTED_BRANCH = "main"
LIVE_URL = "https://scasimir2021.github.io/lawn-a-mercy/"
ACTION_URL = "https://github.com/scasimir2021/lawn-a-mercy/actions"

ALLOWED_EXACT_PATHS = {
    ".gitignore",
    ".nojekyll",
    "404.html",
    "AGENTS.md",
    "README.md",
    "assets/brand/logo.svg",
    "assets/css/site.css",
    "assets/hero/crew-art.png",
    "assets/js/site.js",
    "assets/qr/call.svg",
    "assets/qr/instagram.svg",
    "assets/qr/socials-copy.png",
    "assets/qr/socials.svg",
    "assets/work/README.md",
    "data/site.json",
    "go/index.html",
    "index.html",
    "tools/requirements.txt",
    "tools/trio_publish.py",
    "tools/trio_update.py",
    "trio/CONTRACT.md",
}
DELETION_ONLY_PATHS = {"assets/hero/reference-mockup.png"}
WORK_IMAGE_SUFFIXES = {".avif", ".jpeg", ".jpg", ".png", ".webp"}


class PublishError(RuntimeError):
    pass


def run(*args: str, timeout: int = 180, check: bool = True) -> str:
    result = subprocess.run(
        list(args),
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "command failed").strip()
        raise PublishError(f"{' '.join(args[:3])}: {detail[:500]}")
    # Preserve leading status columns (for example ` M .gitignore`). Only
    # remove line terminators; callers normalize scalar output as needed.
    return (result.stdout or "").rstrip("\r\n")


def normalize_remote(value: str) -> str:
    value = value.strip().replace("git@github.com:", "https://github.com/")
    return value if value.endswith(".git") else f"{value}.git"


def changed_entries() -> list[tuple[str, str]]:
    raw = run("git", "status", "--porcelain=v1", "-z", "--untracked-files=all")
    records = raw.split("\0")
    entries: list[tuple[str, str]] = []
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if len(record) < 4:
            continue
        status = record[:2]
        path = record[3:].replace("\\", "/")
        entries.append((status, path))
        if "R" in status or "C" in status:
            if index < len(records) and records[index]:
                entries.append((status, records[index].replace("\\", "/")))
                index += 1
    return sorted(set(entries), key=lambda item: item[1])


def changed_paths() -> list[str]:
    return sorted({path for _, path in changed_entries()})


def approved_work_images(config: dict[str, Any]) -> set[str]:
    items = ((config.get("portfolio") or {}).get("items") or [])
    return {
        str(item.get("image") or "").replace("\\", "/")
        for item in items
        if isinstance(item, dict)
        and item.get("published") is True
        and item.get("approved_for_public") is True
    }


def path_allowed(status: str, path: str, config: dict[str, Any]) -> bool:
    normalized = str(PurePosixPath(path.replace("\\", "/")))
    if normalized.startswith("../") or normalized == "..":
        return False
    if normalized in DELETION_ONLY_PATHS:
        return "D" in status
    if normalized in ALLOWED_EXACT_PATHS:
        return True
    if normalized.startswith("assets/work/"):
        if PurePosixPath(normalized).suffix.lower() not in WORK_IMAGE_SUFFIXES:
            return False
        return normalized in approved_work_images(config)
    return False


def change_hash(paths: list[str] | None = None) -> str:
    digest = hashlib.sha256()
    selected = paths if paths is not None else changed_paths()
    for relative in selected:
        digest.update(relative.encode("utf-8"))
        path = ROOT / relative
        if path.is_file():
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
        else:
            digest.update(b"<deleted-or-directory>")
    return digest.hexdigest()


def validate_url(value: Any, *, protocols: tuple[str, ...], label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise PublishError(f"{label} must be a non-empty URL")
    parsed = urlparse(value)
    if parsed.scheme not in protocols:
        raise PublishError(f"{label} must use {', '.join(protocols)}")
    if parsed.scheme in ("http", "https") and not parsed.netloc:
        raise PublishError(f"{label} must include a host")


class LocalAssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src", "poster"} and value:
                self.references.append(value)
            elif name == "srcset" and value:
                self.references.extend(part.strip().split()[0] for part in value.split(",") if part.strip())


def validate_local_assets() -> None:
    root = ROOT.resolve()

    def check_reference(source: Path, reference: str) -> None:
        reference = reference.strip()
        parsed = urlparse(reference)
        if not reference or reference.startswith("#") or parsed.scheme or parsed.netloc:
            return
        clean = unquote(parsed.path)
        if not clean:
            return
        if clean.startswith("/"):
            raise PublishError(f"root-relative local asset is unsafe for project Pages: {reference}")
        candidate = (source.parent / clean).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise PublishError(f"local asset escapes repository: {reference}") from exc
        if not candidate.exists():
            raise PublishError(f"missing local asset from {source.relative_to(ROOT)}: {reference}")

    for relative in ("index.html", "go/index.html", "404.html"):
        source = ROOT / relative
        parser = LocalAssetParser()
        parser.feed(source.read_text(encoding="utf-8"))
        for reference in parser.references:
            check_reference(source, reference)

    stylesheet = ROOT / "assets/css/site.css"
    css = stylesheet.read_text(encoding="utf-8")
    for reference in re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", css, flags=re.IGNORECASE):
        if reference.startswith("data:"):
            continue
        check_reference(stylesheet, reference)


def validate_work_image_privacy(path: Path) -> None:
    if path.stat().st_size > 15 * 1024 * 1024:
        raise PublishError(f"portfolio image is larger than 15 MB: {path.relative_to(ROOT)}")
    try:
        from PIL import Image, UnidentifiedImageError
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            exif = image.getexif()
            if exif and exif.get(34853):  # GPSInfo
                raise PublishError(
                    f"portfolio image contains GPS metadata; strip it before publishing: {path.relative_to(ROOT)}"
                )
    except ImportError as exc:
        raise PublishError("Pillow is required to validate portfolio image privacy") from exc
    except UnidentifiedImageError as exc:
        raise PublishError(f"invalid portfolio image: {path.relative_to(ROOT)}") from exc


def validate_config() -> dict[str, Any]:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublishError(f"invalid data/site.json: {exc}") from exc

    if config.get("base_url") != LIVE_URL.rstrip("/"):
        raise PublishError("base_url is locked to the permanent GitHub Pages URL")

    contact = config.get("contact") or {}
    if not re.fullmatch(r"[0-9()+. -]{10,24}", str(contact.get("phone") or "")):
        raise PublishError("contact.phone is invalid")
    if "@" not in str(contact.get("email") or ""):
        raise PublishError("contact.email is invalid")

    social = config.get("social") or {}
    if not isinstance(social, dict) or not social:
        raise PublishError("at least one social profile is required")
    for network, value in social.items():
        validate_url(value, protocols=("https",), label=f"social.{network}")

    routes = config.get("routes") or {}
    validate_url(routes.get("call"), protocols=("tel",), label="routes.call")
    validate_url(routes.get("quote"), protocols=("sms",), label="routes.quote")
    validate_url(routes.get("socials"), protocols=("https",), label="routes.socials")
    remote_config = str((config.get("runtime") or {}).get("remote_config_url") or "").strip()
    if remote_config:
        validate_url(remote_config, protocols=("https",), label="runtime.remote_config_url")

    services = config.get("services") or []
    if not isinstance(services, list) or not services:
        raise PublishError("services must be a non-empty list")
    if len(services) > 30:
        raise PublishError("services is limited to 30 entries")
    for service in services:
        name = service if isinstance(service, str) else service.get("name") if isinstance(service, dict) else ""
        if not str(name).strip() or len(str(name)) > 80:
            raise PublishError("each service needs a name of 80 characters or fewer")

    portfolio = config.get("portfolio") or {}
    items = portfolio.get("items") or []
    if not isinstance(items, list):
        raise PublishError("portfolio.items must be a list")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise PublishError(f"portfolio.items[{index}] must be an object")
        if item.get("published") is not True:
            continue
        if item.get("approved_for_public") is not True:
            raise PublishError(f"portfolio.items[{index}] is published without approved_for_public=true")
        image = str(item.get("image") or "").replace("\\", "/")
        if not image.startswith("assets/work/") or ".." in PurePosixPath(image).parts:
            raise PublishError(f"portfolio.items[{index}].image must stay under assets/work/")
        image_path = ROOT / image
        if not image_path.is_file():
            raise PublishError(f"portfolio image does not exist: {image}")
        if not str(item.get("alt") or "").strip():
            raise PublishError(f"portfolio.items[{index}] needs accessible alt text")
        validate_work_image_privacy(image_path)

    index_text = (ROOT / "index.html").read_text(encoding="utf-8")
    forbidden = ("TRIO READY", "JSON-driven: Trio", "/api/clients", "licensed & insured")
    found = [phrase for phrase in forbidden if phrase.lower() in index_text.lower()]
    if found:
        raise PublishError(f"public index contains forbidden/internal claim: {found[0]}")

    run("node", "--check", "assets/js/site.js", timeout=60)
    run("git", "diff", "--check", timeout=60)
    for required in (
        "index.html", "404.html", "go/index.html", "data/site.json",
        "assets/brand/logo.svg", "assets/css/site.css", "assets/hero/crew-art.png",
        "assets/js/site.js", "assets/qr/socials.svg", ".nojekyll",
    ):
        if not (ROOT / required).exists():
            raise PublishError(f"required public asset missing: {required}")
    validate_local_assets()
    return config


def repository_state(config: dict[str, Any]) -> dict[str, Any]:
    if not (ROOT / ".git").is_dir():
        raise PublishError(f"not a Git repository: {ROOT}")
    branch = run("git", "branch", "--show-current")
    remote = normalize_remote(run("git", "remote", "get-url", "origin"))
    if branch != EXPECTED_BRANCH:
        raise PublishError(f"refusing branch {branch!r}; expected {EXPECTED_BRANCH!r}")
    if remote.lower() != EXPECTED_REMOTE.lower():
        raise PublishError(f"refusing unexpected origin: {remote}")
    entries = changed_entries()
    paths = sorted({path for _, path in entries})
    unexpected = [path for status, path in entries if not path_allowed(status, path, config)]
    if unexpected:
        raise PublishError(f"unexpected changed path: {unexpected[0]}")
    head = run("git", "rev-parse", "HEAD")
    try:
        counts = run("git", "rev-list", "--left-right", "--count", "HEAD...origin/main").split()
        ahead, behind = (int(counts[0]), int(counts[1])) if len(counts) == 2 else (0, 0)
    except (PublishError, ValueError):
        ahead, behind = 0, 0
    return {
        "root": str(ROOT),
        "branch": branch,
        "origin": remote,
        "head": head,
        "changed_paths": paths,
        "change_hash": change_hash(paths),
        "ahead": ahead,
        "behind": behind,
    }


def status() -> dict[str, Any]:
    config = validate_config()
    state = repository_state(config)
    return {
        "ok": True,
        "app": "lawn-a-mercy-public",
        "kind": "remote_git",
        "public": True,
        "live_url": LIVE_URL,
        "actions_url": ACTION_URL,
        "has_pending_changes": bool(state["changed_paths"] or state["ahead"]),
        **state,
    }


def publish(*, confirmed: bool, expected_head: str, expected_change_hash: str, message: str) -> dict[str, Any]:
    if not confirmed:
        raise PublishError("public publish requires --confirm-public")
    config = validate_config()
    before = repository_state(config)
    if not expected_head or before["head"] != expected_head:
        raise PublishError("repository HEAD changed; refresh status before publishing")
    if not expected_change_hash or before["change_hash"] != expected_change_hash:
        raise PublishError("pending files changed; refresh status before publishing")

    run("git", "fetch", "origin", EXPECTED_BRANCH, timeout=180)
    after_fetch = repository_state(validate_config())
    if after_fetch["head"] != before["head"] or after_fetch["change_hash"] != before["change_hash"]:
        raise PublishError("repository changed during remote refresh; review status again")
    counts = run("git", "rev-list", "--left-right", "--count", "HEAD...origin/main").split()
    ahead, behind = (int(counts[0]), int(counts[1])) if len(counts) == 2 else (0, 0)
    if behind:
        raise PublishError("origin/main is ahead or diverged; refusing automatic merge or force-push")
    if ahead:
        raise PublishError(
            "unpushed commits are not accepted by the public gate; review them manually "
            "before publishing"
        )

    committed = False
    paths = changed_paths()
    if paths:
        if change_hash(paths) != expected_change_hash:
            raise PublishError("pending files changed before staging; review status again")
        run("git", "add", "--all", "--", *paths, timeout=120)
        if change_hash(paths) != expected_change_hash:
            raise PublishError("pending files changed during staging; review status again")
        run("git", "diff", "--cached", "--check", timeout=60)
        clean_message = " ".join((message or "").strip().split())[:120] or "content: update public website"
        run("git", "commit", "-m", clean_message, timeout=120)
        committed = True
    if not committed:
        return {
            "ok": True,
            "app": "lawn-a-mercy-public",
            "published": False,
            "reason": "nothing to publish",
            "live_url": LIVE_URL,
        }

    run("git", "push", "origin", "HEAD:main", timeout=240)
    head = run("git", "rev-parse", "HEAD")
    remote_line = run("git", "ls-remote", "origin", "refs/heads/main", timeout=120)
    remote_head = remote_line.split()[0] if remote_line else ""
    if remote_head != head:
        raise PublishError("push returned but origin/main does not match local HEAD")
    return {
        "ok": True,
        "app": "lawn-a-mercy-public",
        "published": True,
        "committed": committed,
        "commit": head[:12],
        "live_url": LIVE_URL,
        "actions_url": ACTION_URL,
        "deploy": "GitHub Pages deployment started; verify the Actions run and public URL.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("validate")
    publish_parser = sub.add_parser("publish")
    publish_parser.add_argument("--confirm-public", action="store_true")
    publish_parser.add_argument("--expected-head", default="")
    publish_parser.add_argument("--expected-change-hash", default="")
    publish_parser.add_argument("--message", default="")
    publish_parser.add_argument("--message-base64", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "status":
            result = status()
        elif args.command == "validate":
            validate_config()
            result = {"ok": True, "app": "lawn-a-mercy-public", "validated": True}
        else:
            message = args.message
            if args.message_base64:
                try:
                    message = base64.b64decode(args.message_base64, validate=True).decode("utf-8")
                except Exception as exc:
                    raise PublishError(f"invalid encoded commit message: {exc}") from exc
            result = publish(
                confirmed=args.confirm_public,
                expected_head=args.expected_head,
                expected_change_hash=args.expected_change_hash,
                message=message,
            )
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
