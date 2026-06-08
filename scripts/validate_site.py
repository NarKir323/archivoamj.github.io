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

IGNORED_SCHEMES = ("http:", "https:", "mailto:", "tel:", "javascript:")
BROKEN_TEXT = ("\ufffd", "Ã", "Â")
BROKEN_SPACING = tuple(REPLACEMENTS)


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
