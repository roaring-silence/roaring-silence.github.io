#!/usr/bin/env python3
"""Baut site/index.html und site/impressum.html aus src/ und bettet die
aktuellen Termine ein.

Benutzung:  python3 make_ics.py && python3 build.py
Danach den Ordner site/ hochladen (index.html, impressum.html,
roaring-silence.ics, fonts/).
"""
from pathlib import Path

here = Path(__file__).parent

head = ('<!doctype html>\n<html lang="de">\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n')

page = (here / "src" / "page.html").read_text(encoding="utf-8")
ics = (here / "site" / "roaring-silence.ics").read_text(encoding="utf-8")
assert "</script" not in ics.lower()
body = page.replace("<!--ICS_FALLBACK-->", ics)
(here / "site" / "index.html").write_text(head + body, encoding="utf-8")

# Vorschau-Fassung ohne Dokumentgerüst
(here / "build").mkdir(exist_ok=True)
(here / "build" / "roaring-silence.html").write_text(body, encoding="utf-8")

impressum = (here / "src" / "impressum.html").read_text(encoding="utf-8")
(here / "site" / "impressum.html").write_text(head + impressum, encoding="utf-8")

print("site/index.html und site/impressum.html geschrieben")
