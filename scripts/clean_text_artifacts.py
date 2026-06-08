#!/usr/bin/env python3
"""Remove confirmed PDF/OCR spacing artifacts from article bodies."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articulos"

REPLACEMENTS = {
    "A unque": "Aunque", "Cos tilla": "Costilla", "pres ente": "presente",
    "caballer ía": "caballería", "direcci ón": "dirección", "enter ó": "enteró",
    "Que rétaro": "Querétaro", "Arroy o": "Arroyo", "Mig uel": "Miguel",
    "e strategias": "estrategias", "final izado": "finalizado",
    "re tirada": "retirada", "ha bría": "habría", "le ería": "leería",
    "d e un": "de un", "pe nsamiento": "pensamiento", "a lcance": "alcance",
    "abogad os": "abogados", "autori dades": "autoridades",
    "R acionales": "Racionales", "T anto": "Tanto", "v iera": "viera",
    "grad os": "grados", "ciegame nte": "ciegamente", "N acional": "Nacional",
    "se creta": "secreta", "re flexiones": "reflexiones", "proye ctos": "proyectos",
    "rep ublicano": "republicano", "d onde": "donde", "f lexible": "flexible",
    "susupuesta": "su supuesta", "sunaturaleza": "su naturaleza",
    "elaspecto": "el aspecto", "susignificado": "su significado",
    "nov edosa": "novedosa", "narrativ o": "narrativo", "suporte": "su aporte",
    "rinco nes": "rincones", "T odo": "Todo", "I glesia": "Iglesia",
    "dividi do": "dividido", "org aniza": "organiza", "plur alidad": "pluralidad",
    "incompat ible": "incompatible", "en orme": "enorme", "comp leta": "completa",
    "derec ho": "derecho", "I mperio": "Imperio", "podero sa": "poderosa",
    "es cenario": "escenario", "p rincipios": "principios", "P artidas": "Partidas",
    "Sego via": "Segovia", "efecti vas": "efectivas", "durade ro": "duradero",
    "cu ltura": "cultura", "contrad icciones": "contradicciones",
    "p erspectiva": "perspectiva", "pa pel": "papel",
    "sunecesidad": "su necesidad", "susociedad": "su sociedad",
    "co ntra": "contra", "desemp leo": "desempleo", "exis tido": "existido",
    "de mocracia": "democracia", "crisi s": "crisis", "elascenso": "el ascenso",
    "susalud": "su salud", "sunovela": "su novela", "sunombre": "su nombre",
    "sunarrativa": "su narrativa", "susobrino": "su sobrino", "elasedio": "el asedio",
    "enlinea": "en línea", "der echo": "derecho", "transacci ones": "transacciones",
    "documen tos": "documentos", "cr ecientes": "crecientes",
    "ci udadanos": "ciudadanos", "c omplejidades": "complejidades",
    "sureñ os": "sureños", "compl eta": "completa", "sunegocio": "su negocio",
    "rea les": "reales", "esta ba": "estaba", "n otarios": "notarios",
    "l os": "los", "lo cales": "locales", "tamb ién": "también",
    "est aba": "estaba", "exist ían": "existían", "p rometiendo": "prometiendo",
    "respe tarían": "respetarían", "me xicano": "mexicano", "co nsiguió": "consiguió",
    "ev ocar": "evocar", "L as": "Las", "Vic arte": "Vicarte",
    "Fern ández": "Fernández", "al as": "a las", "in embargo": "sin embargo",
    "C on": "Con", "E l": "El", "e l": "el", "s u": "su",
    "r etratado": "retratado", "G uerra": "Guerra", "g uerra": "guerra",
    "nació n": "nación", "to man": "toman", "tradujer on": "tradujeron",
    "extra njeros": "extranjeros", "coher ente": "coherente",
    "prop ongo": "propongo", "divers as": "diversas", "de l": "del",
    "comenza ba": "comenzaba", "g énero": "género", "s uperó": "superó",
    "c omo": "como", "se cretas": "secretas", "par a": "para",
    "m ás": "más", "?lites": "élites", "constitucionali stas": "constitucionalistas",
    "disponibilid ad": "disponibilidad", "milita res": "militares",
    "combate s": "combates", "cano n": "canon", "desenlace s": "desenlaces",
    "susesgo": "su sesgo", "entro otros": "entre otros",
    "abast ecimientos": "abastecimientos", "estr atégica": "estratégica",
    "explicar se": "explicarse", "his tórica": "histórica",
    "cir culación": "circulación", "militarizació n": "militarización",
    "de fine": "define", "legi slado": "legislado", "imponi endo": "imponiendo",
    "senti do": "sentido", "referentes m ás": "referentes más",
    "puntos m ás": "puntos más", "come n": "comen", "fuero s": "fueros",
    "reconocer ía": "reconocería", "le yes": "leyes", "re y": "rey",
    "derecho s": "derechos", "percatad o": "percatado", "tri go": "trigo",
    "colaps o": "colapso", "garantizad o": "garantizado",
    "he e ncontrado": "he encontrado", "ec onómico": "económico",
    "convirtiera n": "convirtieran", "ent rada": "entrada", "zar e ra": "zar era",
    "estaba l a": "estaba la", "un a acelerada": "una acelerada",
    "puede e ntenderse": "puede entenderse", "Mas b ien": "Más bien",
    "ciert a manera": "cierta manera", "punto s": "puntos",
    "armas v": "armas y", "encuentre n": "encuentren", "N o": "No",
    "senti r": "sentir", "MA. PDF": "MA.PDF",
}


def clean_body(body: str) -> str:
    for broken, corrected in REPLACEMENTS.items():
        pattern = rf"(?<!\w){re.escape(broken)}(?!\w)"
        body = re.sub(pattern, corrected, body)

    body = re.sub(r"([?!])(?=[A-ZÁÉÍÓÚÜÑ¿¡])", r"\1 ", body)
    return body


def clean(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    match = re.search(r'(<article class="reader">)(.*?)(</article>)', text, re.S)
    if not match:
        return False

    body = clean_body(match.group(2))
    updated = text[: match.start(2)] + body + text[match.end(2) :]
    if updated == text:
        return False

    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    changed = sum(clean(path) for path in sorted(ARTICLES.glob("*.html")))
    print(f"Artículos modificados: {changed}")


if __name__ == "__main__":
    main()
