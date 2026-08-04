#!/usr/bin/env python3
"""Publish the latest selected essays and translation as static HTML pages."""

from __future__ import annotations

import html
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSP = (
    "default-src 'self'; base-uri 'self'; object-src 'none'; "
    "script-src 'self' https://static.cloudflareinsights.com; script-src-attr 'none'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src https://fonts.gstatic.com; img-src 'self' data:; "
    "connect-src https://cloudflareinsights.com; form-action 'none'; frame-src 'none'; "
    "media-src 'self'; worker-src 'none'; upgrade-insecure-requests"
)
BEACON = (
    '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
    'data-cf-beacon=\'{"token":"c4eb19608ce64552af7944785ceebd83"}\'></script>'
)

ARTICLE_CSS = """
 *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
 :root { --white: #ffffff; --black: #111111; --header: #4a5568; --sub: #718096; --rule: #e2e8f0; --yellow: #f5c842; --yellow2: #fdf3c0; --body: #2d3748; }
 html { scroll-behavior: smooth; }
 body { background: var(--white); color: var(--black); font-family: 'Libre Baskerville', serif; font-size: 16px; line-height: 1.85; overflow-x: hidden; }
 header { position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; justify-content: space-between; align-items: center; padding: 1.2rem 3rem; background: rgba(255,255,255,0.97); border-bottom: 1px solid var(--rule); }
 .logo { font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; font-weight: 400; letter-spacing: 0.12em; text-decoration: none; color: var(--black); display: flex; align-items: center; gap: 0.6rem; }
 .logo::after { content: ''; display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--yellow); margin-bottom: 2px; }
 .back-link,.article-link,.pdf-link { font-family: 'Space Mono', monospace; font-size: 0.62rem; letter-spacing: 0.18em; text-transform: uppercase; text-decoration: none; color: var(--sub); transition: color 0.2s; overflow-wrap: anywhere; }
 .back-link:hover,.article-link:hover,.pdf-link:hover { color: var(--black); }
 .tag { display: inline-block; font-family: 'Space Mono', monospace; font-size: 0.52rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--black); background: var(--yellow2); border: 1px solid var(--yellow); padding: 0.25rem 0.55rem; }
 .article-hero { max-width: 920px; margin: 0 auto; padding: 7rem 3rem 3rem; }
 .article-meta { display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
 .article-date { font-family: 'Space Mono', monospace; font-size: 0.58rem; letter-spacing: 0.1em; color: var(--sub); }
 h1 { font-family: 'Cormorant Garamond', serif; font-size: clamp(2.2rem, 5vw, 4rem); font-weight: 300; line-height: 1.08; margin-bottom: 1.2rem; }
 .subtitle { font-size: 1rem; font-style: italic; color: var(--sub); line-height: 1.7; border-left: 2px solid var(--yellow); padding-left: 1.2rem; margin-bottom: 1.6rem; }
 .deck { color: var(--body); max-width: 68ch; }
 .reader { max-width: 920px; margin: 0 auto; padding: 3rem 3rem 5rem; border-top: 1px solid var(--rule); }
 .reader p { color: var(--body); margin-bottom: 1.55rem; text-align: left; overflow-wrap: normal; word-break: normal; hyphens: none; }
 .reader h2 { font-family: 'Cormorant Garamond', serif; font-size: clamp(1.7rem, 3.5vw, 2.5rem); font-weight: 300; line-height: 1.15; margin: 2.7rem 0 1.2rem; color: var(--black); overflow-wrap: anywhere; }
 .reader h3 { font-family: 'Cormorant Garamond', serif; font-size: clamp(1.25rem, 2.4vw, 1.65rem); font-weight: 400; line-height: 1.25; margin: 2rem 0 0.8rem; color: var(--header); }
 .reader strong { color: var(--black); font-weight: 700; }
 .reader em { font-style: italic; }
 blockquote { margin: 1.4rem 0 1.7rem 1.4rem; padding-left: 1.2rem; border-left: 2px solid var(--yellow); color: var(--body); font-size: 0.96rem; line-height: 1.8; }
 blockquote p { margin-bottom: 0.9rem; }
 .translator-note { border-left: 2px solid var(--yellow); padding-left: 1.2rem; margin-bottom: 2.4rem; color: var(--body); font-size: 0.94rem; }
 .bibliografia { border-top: 1px solid var(--rule); margin-top: 3rem; padding-top: 1.5rem; font-size: 0.92rem; line-height: 1.75; }
 .bibliografia h2 { font-size: clamp(1.45rem, 3vw, 2rem); margin-top: 0; }
 .bibliografia-list { list-style: none; display: grid; gap: 0.85rem; padding: 0; margin: 0; }
 .bibliografia-list li { color: var(--body); text-align: left; padding-left: 1.25rem; text-indent: -1.25rem; overflow-wrap: break-word; }
 .reader-nav { max-width: 920px; margin: 0 auto; padding: 1.5rem 3rem 2rem; border-top: 1px solid var(--rule); display: flex; justify-content: space-between; gap: 1rem; }
 .pdf-link { color: var(--black); border-bottom: 2px solid var(--yellow); padding-bottom: 2px; }
 footer { border-top: 1px solid var(--rule); padding: 2rem 3rem; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
 .footer-name { font-family: 'Cormorant Garamond', serif; font-size: 1rem; color: var(--header); letter-spacing: 0.06em; }
 .footer-copy { font-family: 'Space Mono', monospace; font-size: 0.52rem; letter-spacing: 0.14em; color: var(--sub); }
 @media (max-width: 768px) { header { padding: 1rem 1.5rem; } .article-hero,.reader,.reader-nav { padding-left: 1.5rem; padding-right: 1.5rem; } h1,.subtitle,.deck { overflow-wrap: anywhere; } footer { flex-direction: column; gap: 0.6rem; text-align: center; padding: 1.5rem; } }
"""

CATALOG_CSS = """
 *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
 :root { --white: #ffffff; --black: #111111; --header: #4a5568; --sub: #718096; --rule: #e2e8f0; --yellow: #f5c842; --yellow2: #fdf3c0; --body: #2d3748; }
 html { scroll-behavior: smooth; }
 body { background: var(--white); color: var(--black); font-family: 'Libre Baskerville', serif; font-size: 16px; line-height: 1.85; overflow-x: hidden; }
 header { position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; justify-content: space-between; align-items: center; padding: 1.2rem 3rem; background: rgba(255,255,255,0.97); border-bottom: 1px solid var(--rule); }
 .logo { font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; font-weight: 400; letter-spacing: 0.12em; text-decoration: none; color: var(--black); display: flex; align-items: center; gap: 0.6rem; }
 .logo::after { content: ''; display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--yellow); margin-bottom: 2px; }
 .back-link { font-family: 'Space Mono', monospace; font-size: 0.62rem; letter-spacing: 0.18em; text-transform: uppercase; text-decoration: none; color: var(--sub); transition: color 0.2s; }
 .back-link:hover { color: var(--black); }
 .hero { max-width: 1040px; margin: 0 auto; padding: 7.5rem 3rem 3rem; }
 .eyebrow { font-family: 'Space Mono', monospace; font-size: 0.6rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--sub); margin-bottom: 1.2rem; display: flex; align-items: center; gap: 0.7rem; }
 .eyebrow::before { content: ''; display: inline-block; width: 28px; height: 2px; background: var(--yellow); }
 h1 { font-family: 'Cormorant Garamond', serif; font-size: clamp(2.5rem, 6vw, 5rem); font-weight: 300; line-height: 1.05; margin-bottom: 1.4rem; }
 h1 em { font-style: italic; color: var(--header); }
 .intro { max-width: 66ch; color: var(--body); }
 .toc { max-width: 1040px; margin: 0 auto; padding: 0 3rem 2rem; display: flex; gap: 1rem; flex-wrap: wrap; }
 .toc a { font-family: 'Space Mono', monospace; font-size: 0.55rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--black); text-decoration: none; border-bottom: 2px solid var(--yellow); padding-bottom: 2px; }
 .topic { max-width: 1040px; margin: 0 auto; padding: 3rem; border-top: 1px solid var(--rule); display: grid; grid-template-columns: 250px 1fr; gap: 3rem; }
 .topic-label { position: sticky; top: 6rem; align-self: start; }
 .topic-num { font-family: 'Space Mono', monospace; font-size: 0.58rem; letter-spacing: 0.2em; color: var(--yellow); display: block; margin-bottom: 0.8rem; }
 h2 { font-family: 'Cormorant Garamond', serif; font-size: 2rem; font-weight: 300; line-height: 1.15; color: var(--header); }
 h2 em { font-style: italic; color: var(--sub); }
 .topic-note { color: var(--sub); font-size: 0.86rem; margin-top: 1rem; line-height: 1.7; }
 .item { display: grid; grid-template-columns: 120px 1fr auto; gap: 1.5rem; align-items: start; padding: 1.7rem 0; border-bottom: 1px solid var(--rule); color: inherit; text-decoration: none; }
 .item:last-child { border-bottom: none; }
 .item:hover .item-title { color: var(--header); }
 .item-type { font-family: 'Space Mono', monospace; font-size: 0.55rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--sub); padding-top: 0.25rem; overflow-wrap: break-word; }
 .item-title { display: block; font-family: 'Cormorant Garamond', serif; font-size: 1.45rem; font-weight: 400; line-height: 1.25; color: var(--black); transition: color 0.2s; }
 .item-desc { display: block; color: var(--body); font-size: 0.88rem; line-height: 1.7; margin-top: 0.45rem; }
 .item-tag { font-family: 'Space Mono', monospace; font-size: 0.52rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--black); background: var(--yellow2); border: 1px solid var(--yellow); padding: 0.25rem 0.55rem; white-space: nowrap; margin-top: 0.25rem; }
 footer { border-top: 1px solid var(--rule); padding: 2rem 3rem; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
 .footer-name { font-family: 'Cormorant Garamond', serif; font-size: 1rem; color: var(--header); letter-spacing: 0.06em; }
 .footer-copy { font-family: 'Space Mono', monospace; font-size: 0.52rem; letter-spacing: 0.14em; color: var(--sub); }
 @media (max-width: 768px) { header { padding: 1rem 1.5rem; } .hero,.toc,.topic { padding-left: 1.5rem; padding-right: 1.5rem; } .topic { grid-template-columns: 1fr; gap: 1rem; } .topic-label { position: static; } .item { grid-template-columns: 1fr; gap: 0.35rem; } .item-tag { width: max-content; } footer { flex-direction: column; gap: 0.6rem; text-align: center; padding: 1.5rem; } }
"""

FIXES = {
    "V oltaire": "Voltaire",
    "V oltaire": "Voltaire",
    "e n realidad": "en realidad",
    "e ntiende": "entiende",
    "futur o": "futuro",
    "Chate aubriand": "Chateaubriand",
    "us o": "uso",
    "la s lecturas": "las lecturas",
    "expresa una reorganización": "expresa una reorganización",
    "fraca so": "fracaso",
    "qu e": "que",
    "conc retas": "concretas",
    "inmediat a": "inmediata",
    "go zó": "gozó",
    "Esto resulta muy importante por que": "Esto resulta muy importante porque",
    "p articular": "particular",
    "pretend e": "pretende",
    "e s el": "es el",
    "s e vuelve": "se vuelve",
    "d e ese": "de ese",
    "polí tico": "político",
    "transmitir se": "transmitirse",
    "lo mas": "lo más",
    "est a operación": "esta operación",
    "ma terial": "material",
    "no ten ía": "no tenía",
    "seria mas": "sería más",
    "no e ra": "no era",
    "q ue": "que",
    "nac ional": "nacional",
    "e vidente": "evidente",
    "Emili ano": "Emiliano",
    "i ndividual": "individual",
    "cam po": "campo",
    "L as": "Las",
    "es tuvieron": "estuvieron",
    "re duce": "reduce",
    "abs oluta": "absoluta",
    "esclavism o": "esclavismo",
    "revelado r": "revelador",
    "e n la realidad": "en la realidad",
    "re alidad": "realidad",
    "ho y": "hoy",
    "lect ura": "lectura",
    "est os": "estos",
}


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = text.replace(" .", ".").replace(" ,", ",").replace(" ;", ";").replace(" :", ":")
    for broken, fixed in FIXES.items():
        text = text.replace(broken, fixed)
    text = re.sub(r"(?<=\w)-\s+(?=\w)", "", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([¿¡])\s+", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def strip_front_matter(raw: str, title: str) -> str:
    if "Voltaire" in title:
        idx = raw.find("La historiografía ilustrada")
        if idx != -1:
            return raw[idx:]
    if "antinomia" in title.lower():
        idx = raw.find("En 1821 México")
        if idx != -1:
            return raw[idx:]
    idx = raw.find(title[:55])
    if idx == -1:
        return raw
    return raw[idx + len(title) :]


def extract_pdf_article(txt_file: str, title: str) -> tuple[list[str], list[str]]:
    txt_path = ROOT / txt_file
    if txt_path.exists():
        raw = txt_path.read_text(encoding="utf-8")
    else:
        from pypdf import PdfReader

        pdf_by_txt = {
            "tmp_AAMJ FINAL TEORIA.txt": ROOT / "documentos" / "autoridad-pasado-voltaire.pdf",
            "tmp_Ensayo final AMJ mx.txt": ROOT / "documentos" / "antinomia-ciudadano-liberalismo-mexicano.pdf",
        }
        reader = PdfReader(str(pdf_by_txt[txt_file]))
        raw = "\n".join(page.extract_text() or "" for page in reader.pages)
    raw = strip_front_matter(raw, title)
    raw = re.sub(r"Morales Ju[aá]rez Aar[oó]n\s+Ensayo final", "", raw)
    raw = re.sub(r"Morales Ju[aá]ez Aar[oó]n", "", raw)
    body_raw, bib_raw = re.split(r"\n\s*Bibliograf[ií]a\s*\n", raw, maxsplit=1)

    lines: list[str] = []
    skipping_note = False
    for line in body_raw.splitlines():
        line = line.strip()
        if not line:
            skipping_note = False
            lines.append("")
            continue
        if re.match(r"^\d{1,2}\s+", line):
            skipping_note = True
            continue
        if skipping_note:
            continue
        if re.match(r"^(Universidad|Facultad|Profesor:|Teorías|Análisis historiográfico)", line):
            continue
        lines.append(line)

    blocks: list[str] = []
    current: list[str] = []
    for line in lines:
        if not line:
            if current:
                blocks.append(clean_text(" ".join(current)))
                current = []
            continue
        current.append(line)
    if current:
        blocks.append(clean_text(" ".join(current)))

    body = []
    for block in blocks:
        block = re.sub(r"(?<=[a-záéíóúñü)])\d{1,2}(?=\s|$)", "", block)
        block = clean_text(block)
        if block and block != title:
            body.append(block)

    bib_items = []
    bib_raw = re.sub(r"^\s*•\s*", "", bib_raw, flags=re.M)
    bib_raw = re.sub(r"\n(?=\S)", " ", bib_raw)
    for item in re.split(r"\s*•\s*|\n\s*\n", bib_raw):
        item = clean_text(item)
        if item:
            bib_items.append(item)
    if len(bib_items) == 1:
        bib_items = [clean_text(x) for x in re.split(r"(?<=\.)\s+(?=[A-ZÁÉÍÓÚÜÑ][\wÁÉÍÓÚÜÑáéíóúüñ]+,)", bib_items[0]) if x.strip()]
    return body, bib_items


def p(text: str) -> str:
    return f"<p>{html.escape(text)}</p>"


def bibliography(items: list[str]) -> str:
    return (
        '<section class="bibliografia">\n<h2>Bibliografía</h2>\n<ul class="bibliografia-list">\n'
        + "\n".join(f"<li>{html.escape(item)}</li>" for item in items)
        + "\n</ul>\n</section>"
    )


def article_page(
    *,
    title: str,
    tag: str,
    date: str,
    subtitle: str,
    deck: str,
    body: list[str],
    bib: list[str],
    pdf_href: str,
    prev_href: str = "../catalogo.html",
    next_href: str = "../catalogo.html",
) -> str:
    body_html = "\n".join(p(x) for x in body)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
 <meta charset="UTF-8" />
 <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 <meta http-equiv="Content-Security-Policy" content="{CSP}">
 <meta name="referrer" content="no-referrer">
 <title>{html.escape(title)} — Archivo AMJ</title>
 <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Space+Mono:wght@400&display=swap" rel="stylesheet" />
 <style>{ARTICLE_CSS}</style>
 {BEACON}
</head>
<body>
 <header>
  <a class="logo" href="../index.html">A.M.J</a>
  <a class="back-link" href="../catalogo.html">← Escritos</a>
 </header>
 <main>
  <section class="article-hero">
   <div class="article-meta"><span class="tag">{html.escape(tag)}</span><span class="article-date">{html.escape(date)}</span></div>
   <h1>{html.escape(title)}</h1>
   <p class="subtitle">{html.escape(subtitle)}</p>
   <p class="deck">{html.escape(deck)} <a class="pdf-link" href="{html.escape(pdf_href)}">PDF original</a>.</p>
  </section>
  <article class="reader">
{body_html}
{bibliography(bib)}
  </article>
  <nav class="reader-nav">
   <a class="article-link" href="{html.escape(prev_href)}">← Anterior</a>
   <a class="article-link" href="../catalogo.html">Índice</a>
   <a class="article-link" href="{html.escape(next_href)}">Siguiente →</a>
  </nav>
 </main>
 <footer><span class="footer-name">Archivo AMJ</span><span class="footer-copy">© 2026 — Todos los derechos reservados</span></footer>
</body>
</html>
"""


def inline_md(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"(https?://[^\s<]+)", r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>', text)
    return text


def md_blocks_to_html(lines: list[str]) -> str:
    out: list[str] = []
    para: list[str] = []
    quote: list[str] = []

    def flush_para() -> None:
        nonlocal para
        if para:
            out.append(f"<p>{inline_md(' '.join(para))}</p>")
            para = []

    def flush_quote() -> None:
        nonlocal quote
        if quote:
            qparas = [q.strip() for q in "\n".join(quote).split("\n\n") if q.strip()]
            out.append("<blockquote>" + "".join(f"<p>{inline_md(q)}</p>" for q in qparas) + "</blockquote>")
            quote = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith(">"):
            flush_para()
            quote.append(line[1:].strip())
            continue
        flush_quote()
        if not line.strip():
            flush_para()
            continue
        if line.startswith("### "):
            flush_para()
            out.append(f"<h3>{inline_md(line[4:].strip())}</h3>")
        elif line.startswith("## "):
            flush_para()
            text = line[3:].strip()
            if text == "Referencias":
                text = "Bibliografía"
            out.append(f"<h2>{inline_md(text)}</h2>")
        elif line.startswith("# "):
            continue
        else:
            para.append(line.strip())
    flush_para()
    flush_quote()
    return "\n".join(out)


def translation_page() -> str:
    md = Path(r"D:\desscargas varias\No-hay-progreso-en-la-filosofia.md").read_text(encoding="utf-8")
    note, rest = md.split("# No hay progreso en la Filosofía", 1)
    note_paras = [x.strip() for x in note.split("\n\n") if x.strip()]
    note_html = "\n".join(f"<p>{inline_md(x)}</p>" for x in note_paras)
    rest_lines = ("# No hay progreso en la Filosofía" + rest).splitlines()
    body_html = md_blocks_to_html(rest_lines)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
 <meta charset="UTF-8" />
 <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 <meta http-equiv="Content-Security-Policy" content="{CSP}">
 <meta name="referrer" content="no-referrer">
 <title>No hay progreso en la Filosofía — Archivo AMJ</title>
 <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Space+Mono:wght@400&display=swap" rel="stylesheet" />
 <style>{ARTICLE_CSS}</style>
 {BEACON}
</head>
<body>
 <header>
  <a class="logo" href="../index.html">A.M.J</a>
  <a class="back-link" href="../traducciones.html">← Traducciones</a>
 </header>
 <main>
  <section class="article-hero">
   <div class="article-meta"><span class="tag">Traducción</span><span class="article-date">Agosto 2026</span></div>
   <h1>No hay progreso en la Filosofía</h1>
   <p class="subtitle">Eric Dietrich, traducido al español con nota introductoria.</p>
   <p class="deck">Primera traducción del archivo: una intervención filosófica sobre progreso, desacuerdo persistente y límites de la disciplina.</p>
  </section>
  <article class="reader">
   <section class="translator-note">
{note_html}
   </section>
{body_html}
  </article>
  <nav class="reader-nav">
   <a class="article-link" href="../traducciones.html">← Traducciones</a>
   <a class="article-link" href="../index.html#traducciones">Archivo</a>
   <span></span>
  </nav>
 </main>
 <footer><span class="footer-name">Archivo AMJ</span><span class="footer-copy">© 2026 — Todos los derechos reservados</span></footer>
</body>
</html>
"""


def catalog_item(href: str, kind: str, title: str, desc: str, tag: str = "Ensayo") -> str:
    return f"""<a class="item" href="{href}">
<span class="item-type">{kind}</span>
<span><span class="item-title">{title}</span><span class="item-desc">{desc}</span></span>
<span class="item-tag">{tag}</span>
</a>"""


def topic(num: str, ident: str, title: str, em: str, note: str, items: list[str]) -> str:
    return f"""<section class="topic" id="{ident}">
<div class="topic-label">
<span class="topic-num">{num}</span>
<h2>{title}<br><em>{em}</em></h2>
<p class="topic-note">{note}</p>
</div>
<div>
{''.join(items)}
</div>
</section>"""


def write_catalog() -> None:
    topics = [
        topic("01", "historia", "Historia", "y oficio", "Ensayos de reflexión sobre el sentido de la disciplina histórica, sus usos públicos y su relación con la escritura.", [
            catalog_item("articulo-01.html", "Ensayo breve", "Lo que aprendí sobre la historia en una librería cualquiera", "Una reflexión sobre la utilidad, la función social y la experiencia personal de leer historia."),
            catalog_item("articulos/invencion-america-ogorman.html", "Ensayo historiográfico", "La invención de América", "Una lectura de Edmundo O’Gorman y de la crítica al descubrimiento como problema histórico."),
            catalog_item("articulos/autoridad-pasado-voltaire.html", "Ensayo historiográfico", "La autoridad del pasado y el juicio del presente", "Régimen de historicidad, juicio ilustrado y autoridad histórica en El siglo de Luis XIV de Voltaire."),
        ]),
        topic("02", "independencia", "Independencia", "y guerra", "La serie militar vive en el Archivo Militar; aquí se reúnen los ensayos documentales que sostienen o amplían esa línea narrativa.", [
            catalog_item("articulos/batalla-aculco.html", "Ensayo documental", "Aculco: donde se hizo y deshizo la Independencia", "Ensayo documental adaptado para lectura web; funciona como base crítica de la crónica visual."),
            catalog_item("articulos/sitio-cuautla-mito-fundacional.html", "Ensayo documental", "El sitio de Cuautla y la construcción de un mito fundacional", "Ensayo documental sobre fuente militar, propaganda realista y memoria nacional."),
        ]),
        topic("03", "mexico-moderno", "México moderno", "ciudadanía y nación", "Textos sobre liberalismo, propiedad, ciudadanía y los límites sociales de la nación mexicana durante el siglo XIX.", [
            catalog_item("articulos/antinomia-ciudadano-liberalismo-mexicano.html", "Ensayo historiográfico", "La antinomia del ciudadano", "Indígena, propiedad y nación en el liberalismo mexicano del siglo XIX."),
        ]),
        topic("04", "masoneria", "Masonería", "y política", "Material para una posible serie sobre sociabilidad política, prensa y construcción del orden republicano.", [
            catalog_item("articulos/masoneria-sociabilidad-politica.html", "Estudio historiográfico", "Masonería y sociabilidad política en la Ciudad de México", "Texto base sobre el Rito Nacional Mexicano, escoceses, yorkinos y opinión pública entre 1825 y 1830."),
            catalog_item("articulos/masoneria-nueva-espana-laboratorio-voz.html", "Ensayo principal", "El origen de la masonería en la Nueva España", "El laboratorio de la voz: censura, Ilustración y sociabilidad secreta en el mundo virreinal."),
        ]),
        topic("05", "politica", "Política", "contemporánea", "Ensayos sobre discurso público, cultura política y comunicación electoral.", [
            catalog_item("articulos/campana-epn-spots-discurso-politico.html", "Análisis político-cultural", "La campaña presidencial de Enrique Peña Nieto", "Los spots de 2012 como discurso de confianza, cercanía y cambio moderado."),
        ]),
        topic("06", "britanica", "Historia", "británica", "Textos breves sobre ceremonial político, opinión pública y conflicto parlamentario en Inglaterra.", [
            catalog_item("articulos/whigs-guerras-napoleonicas.html", "Ensayo histórico", "La guerra interna antes que la guerra externa", "Los whigs ante la Revolución francesa, Pitt y las guerras napoleónicas."),
            catalog_item("articulos/isabel-i-coronacion-funeral.html", "Ensayo divulgativo", "Ante la vida y la muerte de Isabel I", "Coronación, funeral y construcción pública de la imagen de la monarca inglesa."),
        ]),
        topic("07", "medieval", "Edad Media", "y derecho", "Textos sobre documentos notariales, ciudad, comercio y tradición jurídica.", [
            catalog_item("articulos/notario-languedoc-montpellier.html", "Ensayo documental", "Un notario de Languedoc", "Actas notariales, deuda, comercio y justicia urbana en Montpellier durante el siglo XIV.", "Estudio"),
            catalog_item("articulos/siete-partidas-ordenamiento-alcala.html", "Ensayo", "Las Siete Partidas y el Ordenamiento de Alcalá", "Una lectura del derecho como instrumento de centralización política en Castilla.", "Estudio"),
        ]),
        topic("08", "economia", "Historia", "económica", "Ensayos de interpretación amplia sobre ideología, crisis y transformación del mundo contemporáneo.", [
            catalog_item("articulos/siglo-xx-paradigma-economico.html", "Ensayo", "El siglo XX y la muerte de un paradigma económico", "Guerra, crisis, liberalismo, comunismo y reorganización económica del mundo contemporáneo."),
        ]),
    ]
    toc = "".join(
        f'<a href="#{ident}">{label}</a>\n'
        for ident, label in [
            ("historia", "Historia"),
            ("independencia", "Independencia"),
            ("mexico-moderno", "México moderno"),
            ("masoneria", "Masonería"),
            ("politica", "Política contemporánea"),
            ("britanica", "Historia británica"),
            ("medieval", "Edad Media"),
            ("economia", "Economía"),
        ]
    )
    html_text = f"""<!DOCTYPE html>
<html lang="es">
<head>
 <meta charset="UTF-8" />
 <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 <meta http-equiv="Content-Security-Policy" content="{CSP}">
 <meta name="referrer" content="no-referrer">
 <title>Archivo de escritos — Archivo AMJ</title>
 <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Space+Mono:wght@400&display=swap" rel="stylesheet" />
 <style>{CATALOG_CSS}</style>
 {BEACON}
</head>
<body>
 <header><a class="logo" href="index.html">A.M.J</a><a class="back-link" href="index.html#escritos">← Volver</a></header>
 <main>
  <section class="hero">
   <p class="eyebrow">Mapa del archivo</p>
   <h1>Archivo <em>de escritos</em></h1>
   <p class="intro">Ensayos, estudios y notas organizados por líneas de trabajo. Cada entrada puede leerse dentro del sitio; cuando existe un documento original, queda reservado como respaldo documental.</p>
  </section>
  <nav class="toc">{toc}</nav>
  {''.join(topics)}
 </main>
 <footer><span class="footer-name">Archivo AMJ</span><span class="footer-copy">© 2026 — Todos los derechos reservados</span></footer>
</body>
</html>
"""
    (ROOT / "catalogo.html").write_text(html_text, encoding="utf-8")


def write_translations_index() -> None:
    html_text = f"""<!DOCTYPE html>
<html lang="es">
<head>
 <meta charset="UTF-8" />
 <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 <meta http-equiv="Content-Security-Policy" content="{CSP}">
 <meta name="referrer" content="no-referrer">
 <title>Archivo de traducciones — Archivo AMJ</title>
 <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Space+Mono:wght@400&display=swap" rel="stylesheet" />
 <style>{CATALOG_CSS}</style>
 {BEACON}
</head>
<body>
 <header><a class="logo" href="index.html">A.M.J</a><a class="back-link" href="index.html#traducciones">← Volver</a></header>
 <main>
  <section class="hero">
   <p class="eyebrow">Archivo de traducciones</p>
   <h1>Traducciones <em>& notas</em></h1>
   <p class="intro">Textos vertidos al español y acompañados por una nota editorial mínima: autor, procedencia, contexto de publicación y criterios de traducción. Esta sección reúne traducciones de filosofía, historia intelectual y ensayo.</p>
  </section>
  {topic("01", "filosofia", "Filosofía", "y ensayo", "Traducciones preparadas para lectura web, con indicación del texto fuente y notas cuando sean necesarias.", [
      catalog_item("traducciones/no-hay-progreso-filosofia.html", "Traducción", "No hay progreso en la Filosofía", "Eric Dietrich sobre progreso filosófico, desacuerdo persistente y límites de la disciplina.", "Traducción")
  ])}
 </main>
 <footer><span class="footer-name">Archivo AMJ</span><span class="footer-copy">© 2026 — Todos los derechos reservados</span></footer>
</body>
</html>
"""
    (ROOT / "traducciones.html").write_text(html_text, encoding="utf-8")


def main() -> None:
    (ROOT / "articulos").mkdir(exist_ok=True)
    (ROOT / "traducciones").mkdir(exist_ok=True)
    (ROOT / "documentos").mkdir(exist_ok=True)

    shutil.copy2(Path(r"C:\Users\SPARTAN PC\Documents\AAMJ FINAL TEORIA.pdf"), ROOT / "documentos" / "autoridad-pasado-voltaire.pdf")
    shutil.copy2(Path(r"C:\Users\SPARTAN PC\Desktop\DOCUMETNOS IMPOTANTES\Historia Unam\Ensayo final AMJ mx.pdf"), ROOT / "documentos" / "antinomia-ciudadano-liberalismo-mexicano.pdf")
    shutil.copy2(Path(r"D:\desscargas varias\No-hay-progreso-en-la-filosofia.md"), ROOT / "documentos" / "no-hay-progreso-en-la-filosofia.md")

    volt_title = "La autoridad del pasado y el juicio del presente: régimen de historicidad en El siglo de Luis XIV de Voltaire"
    volt_body, volt_bib = extract_pdf_article("tmp_AAMJ FINAL TEORIA.txt", volt_title)
    (ROOT / "articulos" / "autoridad-pasado-voltaire.html").write_text(
        article_page(
            title="La autoridad del pasado y el juicio del presente",
            tag="Historiografía",
            date="Agosto 2026",
            subtitle="Régimen de historicidad en El siglo de Luis XIV de Voltaire.",
            deck="Un ensayo sobre autoridad del pasado, presente ilustrado y juicio histórico en la historiografía de Voltaire.",
            body=volt_body,
            bib=volt_bib,
            pdf_href="../documentos/autoridad-pasado-voltaire.pdf",
            prev_href="invencion-america-ogorman.html",
            next_href="batalla-aculco.html",
        ),
        encoding="utf-8",
    )

    ant_title = "La antinomia del ciudadano: indígena, propiedad y nación en el liberalismo mexicano del siglo XIX."
    ant_body, ant_bib = extract_pdf_article("tmp_Ensayo final AMJ mx.txt", ant_title)
    (ROOT / "articulos" / "antinomia-ciudadano-liberalismo-mexicano.html").write_text(
        article_page(
            title="La antinomia del ciudadano",
            tag="México moderno",
            date="Agosto 2026",
            subtitle="Indígena, propiedad y nación en el liberalismo mexicano del siglo XIX.",
            deck="Una lectura del liberalismo mexicano como proyecto de ciudadanía atravesado por propiedad, comunidad indígena y exclusión.",
            body=ant_body,
            bib=ant_bib,
            pdf_href="../documentos/antinomia-ciudadano-liberalismo-mexicano.pdf",
            prev_href="sitio-cuautla-mito-fundacional.html",
            next_href="masoneria-sociabilidad-politica.html",
        ),
        encoding="utf-8",
    )

    (ROOT / "traducciones" / "no-hay-progreso-filosofia.html").write_text(translation_page(), encoding="utf-8")
    write_catalog()
    write_translations_index()
    print("Nuevos ensayos y traducción publicados.")


if __name__ == "__main__":
    main()
