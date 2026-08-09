#!/usr/bin/env python3
"""Safely update public content and regenerate permanent QR assets."""
from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
from pathlib import Path

import qrcode
from qrcode.image.svg import SvgPathImage


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
    value.add_argument("--remote-config-url", "--remote-config", dest="remote_config_url")
    for network in ("tiktok", "instagram", "linkedin"):
        value.add_argument(f"--{network}")
        value.add_argument(f"--{network}-handle")
    value.add_argument("--service")
    service_action = value.add_mutually_exclusive_group()
    service_action.add_argument("--add-service", action="store_true")
    service_action.add_argument("--remove-service", action="store_true")
    return value


def phone_values(phone: str) -> tuple[str, str]:
    digits = "".join(filter(str.isdigit, phone))[-10:]
    if len(digits) != 10:
        raise ValueError("phone must contain a 10-digit US number")
    return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}", f"+1{digits}"


def social_url(value: str, network: str) -> str:
    if not re.fullmatch(r"https://[^\s]+", value):
        raise ValueError(f"{network} URL must start with https://")
    return value


def qr_bytes(destination: str) -> tuple[bytes, bytes]:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=14,
        border=4,
    )
    qr.add_data(destination)
    qr.make(fit=True)

    png_stream = io.BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(png_stream, format="PNG")

    svg_stream = io.BytesIO()
    qr.make_image(image_factory=SvgPathImage).save(svg_stream)
    return png_stream.getvalue(), svg_stream.getvalue()


def build_qr(config: dict) -> dict[Path, bytes]:
    base = config["base_url"].rstrip("/")
    destinations = {
        "website": f"{base}/go/?to=website",
        "socials": f"{base}/go/?to=socials",
        "call": f"{base}/go/?to=call",
        "instagram": f"{base}/go/?to=instagram",
    }
    rendered: dict[Path, bytes] = {}
    for name, destination in destinations.items():
        png, svg = qr_bytes(destination)
        rendered[ROOT / "assets" / "qr" / f"{name}.svg"] = svg
        if name in {"website", "socials"}:
            rendered[ROOT / "assets" / "qr" / f"{name}.png"] = png
        if name == "socials":
            rendered[ROOT / "assets" / "qr" / "socials-copy.png"] = png
    return rendered


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
        pretty, e164 = phone_values(args.phone)
        config["contact"]["phone"] = pretty
        config["contact"]["phone_e164"] = e164
        config["routes"].update({"call": f"tel:{e164}", "text": f"sms:{e164}", "quote": f"sms:{e164}"})
    if args.email:
        if "@" not in args.email:
            raise ValueError("email is invalid")
        config["contact"]["email"] = args.email.strip()
        config["routes"]["email"] = f"mailto:{args.email.strip()}"

    for network in ("tiktok", "instagram", "linkedin"):
        url = getattr(args, network)
        handle = getattr(args, f"{network}_handle")
        if url:
            config["social"][network] = social_url(url, network)
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

    if args.remote_config_url is not None:
        config["runtime"]["remote_config_url"] = args.remote_config_url.strip()
    if args.base_url:
        config["base_url"] = args.base_url.rstrip("/")

    base = config["base_url"].rstrip("/")
    config["base_url"] = base
    config["routes"]["website"] = f"{base}/"
    config["routes"]["socials"] = f"{base}/go/?to=socials"

    qr_files = build_qr(config)
    originals = {path: path.read_bytes() if path.exists() else None for path in qr_files}
    try:
        atomic_write(CONFIG_PATH, (json.dumps(config, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        for path, content in qr_files.items():
            atomic_write(path, content)
        validation = subprocess.run([sys.executable, str(PUBLISHER), "validate"], cwd=ROOT, check=False)
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
