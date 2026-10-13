#!/usr/bin/env python3
"""Baut site/index.html und site/impressum.html aus src/ und bettet die
aktuellen Termine (und strukturierte Daten fürs nächste Treffen) ein.

Benutzung:  python3 make_ics.py && python3 build.py
Danach den Ordner site/ hochladen (index.html, impressum.html,
roaring-silence.ics, fonts/).
"""
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SITE_URL = "https://roaring-silence.github.io"
TZ = ZoneInfo("Europe/Berlin")

here = Path(__file__).parent

head = ('<!doctype html>\n<html lang="de">\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n')

page = (here / "src" / "page.html").read_text(encoding="utf-8")
ics = (here / "site" / "roaring-silence.ics").read_text(encoding="utf-8")
assert "</script" not in ics.lower()


def next_event(ics_text: str):
    """Erstes künftiges, nicht abgesagtes VEVENT aus der ICS-Datei."""
    now = datetime.now(TZ)
    best = None
    for block in ics_text.split("BEGIN:VEVENT")[1:]:
        if "STATUS:CANCELLED" in block:
            continue
        m = re.search(r"DTSTART;TZID=Europe/Berlin:(\d{8}T\d{6})", block)
        if not m:
            continue
        start = datetime.strptime(m.group(1), "%Y%m%dT%H%M%S").replace(tzinfo=TZ)
        if start < now:
            continue
        if best is None or start < best[0]:
            e = re.search(r"DTEND;TZID=Europe/Berlin:(\d{8}T\d{6})", block)
            end = datetime.strptime(e.group(1), "%Y%m%dT%H%M%S").replace(tzinfo=TZ) if e else None
            best = (start, end)
    return best


def parse_address(addr: str):
    m = re.match(r"^(.*),\s*(\d{5})\s+(.*)$", addr.strip())
    if not m:
        return None
    street, postal, city = m.groups()
    return {"@type": "PostalAddress", "streetAddress": street,
            "postalCode": postal, "addressLocality": city, "addressCountry": "DE"}


def build_jsonld(page_src: str, ics_text: str) -> str:
    addr_m = re.search(r'address:\s*"([^"]*)"', page_src)
    address = parse_address(addr_m.group(1)) if addr_m else None
    org = {
        "@type": "Organization",
        "@id": SITE_URL + "/#organization",
        "name": "Roaring Silence",
        "url": SITE_URL + "/",
        "description": ("Offene Meditationsgruppe der Aro gTér-Linie in Köln-Mülheim: "
                         "stilles Sitzen und yogischer Gesang."),
        "sameAs": ["https://aroterlineage.org/de/"],
    }
    if address:
        org["address"] = address
        org["areaServed"] = address["addressLocality"]
    graph = [org]

    nxt = next_event(ics_text)
    if nxt:
        start, end = nxt
        event = {
            "@type": "Event",
            "name": "Roaring Silence – Stilles Sitzen und yogischer Gesang",
            "startDate": start.isoformat(),
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "organizer": {"@id": SITE_URL + "/#organization"},
            "description": ("Meditation und yogischer Gesang in der Tradition des "
                             "Vajrayana-Buddhismus (Dzogchen), findet alle zwei Wochen "
                             "sonntags statt."),
            "isAccessibleForFree": True,
            "image": SITE_URL + "/media/rhein-abend.jpg",
        }
        if end:
            event["endDate"] = end.isoformat()
        if address:
            event["location"] = {"@type": "Place", "name": "Zeiträume Studio", "address": address}
        graph.append(event)

    data = {"@context": "https://schema.org", "@graph": graph}
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    assert "</script" not in payload.lower()
    return f'<script type="application/ld+json">\n{payload}\n</script>'


page = page.replace("<!--JSONLD-->", build_jsonld(page, ics))
body = page.replace("<!--ICS_FALLBACK-->", ics)
(here / "site" / "index.html").write_text(head + body, encoding="utf-8")

# Vorschau-Fassung ohne Dokumentgerüst
(here / "build").mkdir(exist_ok=True)
(here / "build" / "roaring-silence.html").write_text(body, encoding="utf-8")

impressum = (here / "src" / "impressum.html").read_text(encoding="utf-8")
(here / "site" / "impressum.html").write_text(head + impressum, encoding="utf-8")

(here / "site" / "robots.txt").write_text(
    "User-agent: *\nAllow: /\n\nSitemap: " + SITE_URL + "/sitemap.xml\n", encoding="utf-8")
(here / "site" / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f"  <url><loc>{SITE_URL}/</loc></url>\n"
    "</urlset>\n", encoding="utf-8")

print("site/index.html, site/impressum.html, robots.txt und sitemap.xml geschrieben")
