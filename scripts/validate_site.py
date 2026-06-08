#!/usr/bin/env python3
"""Validate the static Archivo AMJ site before publishing."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from clean_text_artifacts import REPLACEMENTS


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = sorted(ROOT.rglob("*.html"))
ARTICLE_FILES = sorted((ROOT / "articulos").glob("*.html"))
JS_FILES = sorted(ROOT.rglob("*.js"))

IGNORED_SCHEMES = ("http:", "https:", "mailto:", "tel:", "javascript:")
BROKEN_TEXT = ("\ufffd", "Ã", "Â")
BROKEN_SPACING = tuple(REPLACEMENTS)
REQUIRED_CSP = (
    "default-src 'self'",
    "object-src 'none'",
    "script-src 'self' https://static.cloudflareinsights.com",
    "script-src-attr 'none'",
    "connect-src https://cloudflareinsights.com",
    "form-action 'none'",
)
CLOUDFLARE_ANALYTICS_TOKEN = "c4eb19608ce64552af7944785ceebd83"


def local_target(source: Path, value: str) -> Path | None:
    value = value.strip()
    if not value or value.startswith(("#", *IGNORED_SCHEMES)):
        return None

    path = unquote(urlsplit(value).path)
    if not path:
        return None

    if path.startswith("/"):
        return ROOT / path.lstrip("/")
    return (source.parent / path).resolve()


def validate_file(path: Path) -> list[str]:
    problems: list[str] = []
    text = path.read_text(encoding="utf-8")

    for marker in BROKEN_TEXT:
        if marker in text:
            problems.append(f"{path.relative_to(ROOT)}: contiene texto dañado ({marker!r})")

    for marker in BROKEN_SPACING:
        pattern = rf"(?<!\w){re.escape(marker)}(?!\w)"
        if path in ARTICLE_FILES and re.search(pattern, text):
            problems.append(
                f"{path.relative_to(ROOT)}: contiene una palabra cortada o pegada ({marker!r})"
            )

    for attribute, value in re.findall(r'\b(href|src)="([^"]+)"', text):
        target = local_target(path, value)
        if target is not None and not target.exists():
            problems.append(
                f"{path.relative_to(ROOT)}: {attribute} apunta a un archivo inexistente: {value}"
            )

    csp_match = re.search(
        r'<meta\s+http-equiv="Content-Security-Policy"\s+content="([^"]+)"',
        text,
        re.IGNORECASE,
    )
    if not csp_match:
        problems.append(f"{path.relative_to(ROOT)}: falta Content Security Policy")
    else:
        for directive in REQUIRED_CSP:
            if directive not in csp_match.group(1):
                problems.append(
                    f"{path.relative_to(ROOT)}: CSP no contiene {directive!r}"
                )

    if re.search(r"<script(?![^>]*\bsrc=)[^>]*>", text, re.IGNORECASE):
        problems.append(f"{path.relative_to(ROOT)}: contiene JavaScript en línea")

    if re.search(r"\son[a-z]+\s*=", text, re.IGNORECASE):
        problems.append(f"{path.relative_to(ROOT)}: contiene un manejador de evento en línea")

    beacon = (
        '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
        f'data-cf-beacon=\'{{"token":"{CLOUDFLARE_ANALYTICS_TOKEN}"}}\'></script>'
    )
    if text.count(beacon) != 1:
        problems.append(
            f"{path.relative_to(ROOT)}: falta el rastreador autorizado de Cloudflare"
        )

    for tag in re.findall(r'<a\b[^>]*\btarget="_blank"[^>]*>', text, re.IGNORECASE):
        if not re.search(r'\brel="[^"]*\bnoopener\b[^"]*\bnoreferrer\b[^"]*"', tag):
            problems.append(
                f"{path.relative_to(ROOT)}: enlace target=_blank sin noopener noreferrer"
            )

    if path in ARTICLE_FILES:
        if "<article" not in text or "<h1>" not in text:
            problems.append(f"{path.relative_to(ROOT)}: falta la estructura principal del artículo")
        if "<h2>Bibliografía</h2>" not in text:
            problems.append(f"{path.relative_to(ROOT)}: falta la sección Bibliografía")
        if not re.search(r"\bhyphens\s*:\s*none\b", text):
            problems.append(f"{path.relative_to(ROOT)}: falta desactivar la separación automática")

    return problems


def main() -> int:
    problems: list[str] = []

    if not HTML_FILES:
        print("No se encontraron archivos HTML.")
        return 1

    for path in HTML_FILES:
        problems.extend(validate_file(path))

    dangerous_javascript = ("innerHTML", "outerHTML", "insertAdjacentHTML", "eval(", "new Function")
    for path in JS_FILES:
        text = path.read_text(encoding="utf-8")
        for marker in dangerous_javascript:
            if marker in text:
                problems.append(
                    f"{path.relative_to(ROOT)}: contiene JavaScript peligroso ({marker!r})"
                )

    if problems:
        print("Validación fallida:\n")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print(
        f"Validación correcta: {len(HTML_FILES)} páginas HTML y "
        f"{len(ARTICLE_FILES)} artículos revisados."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
