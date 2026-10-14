#!/usr/bin/env python3
"""Erzeugt site/roaring-silence.ics, die einzige Quelle für alle Termine.

Benutzung:  python3 make_ics.py   (danach: python3 build.py, dann site/ hochladen)

Termin absagen:      Datum mit Begründung in CANCELLED eintragen.
Zusatztermin:        Datum in EXTRA eintragen.
Zeitraum verlängern: UNTIL anpassen.
Termine nie löschen, sondern absagen: abonnierte Kalender behandeln
gelöschte Termine uneinheitlich, abgesagte zuverlässig.
"""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# ---- Einstellungen -------------------------------------------------------
FIRST = date(2026, 11, 15)          # erster Termin (Sonntag)
UNTIL = date(2027, 1, 31)           # letzter Tag, bis zu dem Termine erzeugt werden
EVERY_DAYS = 14                     # vierzehntägig
START, END = "180000", "190000"     # 18:00 bis 19:00 Uhr, Ortszeit Köln

TITLE = "Roaring Silence · Stilles Sitzen und yogischer Gesang"
LOCATION = "Zeiträume Studio, Köln-Mülheim"
DESCRIPTION = (
    "Sitzgruppe der Aro gTér-Linie. Auf Spendenbasis. "
    "Kontakt: aro.sangha.cologne@gmail.com"
)

# Abgesagte Termine: Datum -> kurzer Hinweis (erscheint auf der Website)
CANCELLED = {
    # date(2026, 12, 27): "Pause zwischen den Jahren",
}

# Zusätzliche Termine außerhalb des Rhythmus
EXTRA = [
    # date(2027, 1, 17),
]

# Termine vorübergehend ausgelassen (ohne offizielle Absage): erscheinen
# gar nicht erst, weder im Kalender noch auf der Website.
SKIP = set((
    # date(2027, 2, 7),
))
# --------------------------------------------------------------------------

VTIMEZONE = """BEGIN:VTIMEZONE
TZID:Europe/Berlin
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE"""


def esc(text: str) -> str:
    return (text.replace("\\", "\\\\").replace(";", "\\;")
                .replace(",", "\\,").replace("\n", "\\n"))


def fold(line: str) -> str:
    """Zeilen nach RFC 5545 auf 75 Oktette umbrechen."""
    out, cur = [], ""
    for ch in line:
        limit = 75 if not out else 74
        if len((cur + ch).encode("utf-8")) > limit:
            out.append(cur)
            cur = ch
        else:
            cur += ch
    out.append(cur)
    return "\r\n ".join(out)


def all_dates():
    days, d = [], FIRST
    while d <= UNTIL:
        days.append(d)
        d += timedelta(days=EVERY_DAYS)
    return sorted((set(days) | set(EXTRA) | set(CANCELLED)) - SKIP)


def main():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Roaring Silence Koeln//DE",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Roaring Silence Köln",
        "X-WR-TIMEZONE:Europe/Berlin",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H",
        "X-PUBLISHED-TTL:PT6H",
        *VTIMEZONE.split("\n"),
    ]
    for d in all_dates():
        ymd = d.strftime("%Y%m%d")
        off = d in CANCELLED
        lines += [
            "BEGIN:VEVENT",
            f"UID:{ymd}@roaring-silence-koeln",
            f"DTSTAMP:{stamp}",
            f"DTSTART;TZID=Europe/Berlin:{ymd}T{START}",
            f"DTEND;TZID=Europe/Berlin:{ymd}T{END}",
            "SUMMARY:" + esc(("Fällt aus: " if off else "") + TITLE),
            "LOCATION:" + esc(LOCATION),
            "DESCRIPTION:" + esc(DESCRIPTION),
            f"STATUS:{'CANCELLED' if off else 'CONFIRMED'}",
            f"SEQUENCE:{1 if off else 0}",
        ]
        if off and CANCELLED[d]:
            lines.append("COMMENT:" + esc(CANCELLED[d]))
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")

    out = Path(__file__).parent / "site" / "roaring-silence.ics"
    out.write_bytes(("\r\n".join(fold(l) for l in lines) + "\r\n").encode("utf-8"))
    n = len(all_dates())
    print(f"{out.name}: {n} Termine, davon {len(CANCELLED)} abgesagt")
    for d in all_dates():
        print("  ", d.strftime("%a %d.%m.%Y"), "(abgesagt)" if d in CANCELLED else "")


if __name__ == "__main__":
    main()
