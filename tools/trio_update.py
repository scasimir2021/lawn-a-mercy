#!/usr/bin/env python3
"""Edit JSON-backed public-site content without publishing it."""
from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import qrcode
    import qrcode.image.svg
except ImportError:
    qrcode = None


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "site.json"
PUBLISHER = ROOT / "tools" / "trio_publish.py"


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Update Lawn-A-Mercy public site content")
    value.add_argument("--headline")
    value.add_argument("--description")
    value.add_argument("--about")
    value.add_argument("--phone")
    value.add_argument("--email")
    value.add_argument("--base-url")
    value.add_argument("--remote-config")
    value.add_argument("--tiktok")
    value.add_argument("--instagram")
    value.add_argument("--linkedin")
    value.add_argument("--tiktok-handle")
    value.add_argument("--instagram-handle")
    value.add_argument("--linkedin-handle")
    value.add_argument("--service")
    service_action = value.add_mutually_exclusive_group()
    service_action.add_argument("--add-service", action="store_true")
    service_action.add_argument("--remove-service", action="store_true")
    return value


def phone_routes(phone: str) -> tuple[str, str]:
    digits = "".join(filter(str.isdigit, phone))[-10:]
    if len(digits) != 10:
        raise ValueError("phone must contain a 10-digit US number")
    destination = f"+1{digits}"
    return f"tel:{destination}", f"sms:{destination}"


def validate_social_url(value: str, network: str) -> str:
    if not re.match(r"^https://[^\s]+$", value):
        raise ValueError(f"{network} URL must start with https://")
    return value


def build_qr(config: dict) -> dict[Path, bytes]:
    if qrcode is None:
        raise RuntimeError("QR support missing; run: python -m pip install -r tools/requirements.txt")
    base = config["base_url"].rstrip("/")
    routes = {
        "socials": f"{base}/go/?to=socials",
        "call": f"{base}/go/?to=call",
        "instagram": f"{base}/go/?to=instagram",
    }
    rendered: dict[Path, bytes] = {}
    for name, destination in routes.items():
        image = qrcode.make(
            destination,
            image_factory=qrcode.image.svg.SvgPathImage,
            box_size=10,
            border=2,
        )
        stream = io.BytesIO()
        image.save(stream)
        rendered[ROOT / "assets" / "qr" / f"{name}.svg"] = stream.getvalue()
    return rendered


def atomic_write(path: Path, content: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def main() -> int:
    args = parser().parse_args()
    original_config = CONFIG_PATH.read_bytes()
    config = json.loads(original_config.decode("utf-8"))

    for argument, key in (
        (args.headline, "headline"),
        (args.description, "description"),
        (args.about, "about"),
    ):
        if argument:
            config["brand"][key] = argument.strip()

    if args.phone:
        call, text = phone_routes(args.phone)
        config["contact"]["phone"] = args.phone.strip()
        config["routes"].update({"call": call, "text": text, "quote": text})
    if args.email:
        if "@" not in args.email:
            raise ValueError("email is invalid")
        config["contact"]["email"] = args.email.strip()
        config["routes"]["email"] = f"mailto:{args.email.strip()}"
    if args.base_url:
        config["base_url"] = args.base_url.rstrip("/")
        config["routes"]["socials"] = f"{config['base_url']}/go/?to=socials"
    if args.remote_config is not None:
        config["runtime"]["remote_config_url"] = args.remote_config.strip()

    for network in ("tiktok", "instagram", "linkedin"):
        url = getattr(args, network)
        handle = getattr(args, f"{network}_handle")
        if url:
            config["social"][network] = validate_social_url(url, network)
        if handle:
            config.setdefault("social_handles", {})[network] = handle.strip()

    if args.service and args.add_service:
        service = args.service.strip()
        if service and service not in config["services"]:
            config["services"].append(service)
    if args.service and args.remove_service:
        config["services"] = [
            item for item in config["services"]
            if str(item).lower() != args.service.strip().lower()
        ]

    qr_files = build_qr(config)
    originals = {path: path.read_bytes() if path.exists() else None for path in qr_files}
    try:
        atomic_write(CONFIG_PATH, (json.dumps(config, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        for path, content in qr_files.items():
            atomic_write(path, content)
        validation = subprocess.run(
            [sys.executable, str(PUBLISHER), "validate"],
            cwd=ROOT,
            check=False,
        )
        if validation.returncode != 0:
            raise RuntimeError(f"validation failed with exit code {validation.returncode}")
    except Exception:
        atomic_write(CONFIG_PATH, original_config)
        for path, content in originals.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, content)
        raise
    print(f"Updated {CONFIG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
