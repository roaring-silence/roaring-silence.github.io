# Roaring Silence · Website und Kalender

Sitzgruppe der Aro gTér-Linie in Köln-Mülheim. Eine statische Seite plus eine
Kalenderdatei. Die Kalenderdatei ist die einzige Quelle für alle Termine: die
Website liest sie, und Teilnehmende abonnieren sie.

## Ordner

    site/                 das wird hochgeladen
      index.html          die Seite (wird von build.py erzeugt, nicht von Hand ändern)
      roaring-silence.ics der Kalender (wird von make_ics.py erzeugt)
      fonts/              Schriften, lokal eingebunden (keine Anfragen an Dritte)
      media/              Hintergrundfilm und Standbild, lokal eingebunden
    src/page.html         Quelltext der Seite: Texte, Gestaltung, Einstellungen
    make_ics.py           Termine pflegen
    build.py              baut site/index.html

## Termin absagen oder hinzufügen

1. In `make_ics.py` das Datum unter `CANCELLED` (mit kurzem Hinweis) oder `EXTRA` eintragen.
2. `python3 make_ics.py && python3 build.py`
3. Den Ordner `site/` hochladen.
4. Kurze Nachricht in die Signal-Gruppe. Abonnierte Kalender brauchen oft Stunden.

Termine nie löschen, immer absagen. Gelöschte Termine bleiben in manchen
Kalenderprogrammen stehen.

## Vor der Veröffentlichung eintragen

In `src/page.html`, Block `CONFIG` am Anfang des Skripts:

- `signalUrl`  Beitrittslink der Signal-Gruppe
- `donateUrl`  Link für regelmäßige Spenden
- `address`, `mapUrl`  Adresse des Zeiträume Studios

Außerdem:

- `LOCATION` in `make_ics.py` um die Straße ergänzen.
- Impressum im Fußbereich von `src/page.html` (Absatz mit `id="imprint"`).
- Zustimmung zur Verwendung des Namens einholen.

Solange ein Feld leer ist, zeigt die Seite einen Platzhaltertext statt eines toten Links.

## Fragen und Antworten

Die Antworten stehen in `src/page.html` im Abschnitt `<section id="fragen">`,
jede Frage als ein `<details>`-Block mit einer deutschen und einer englischen
Fassung (`data-l="de"` und `data-l="en"`). Neue Frage: einen Block kopieren,
beide Fassungen schreiben, `python3 build.py`.

Die Antworten stützen sich auf die Angaben der Linie (Voraussetzungen,
Zugehörigkeit, Haltung, yogischer Gesang) und verlinken dorthin. Alles, was die
Sitzgruppe selbst betrifft, steht nur dort und muss hier gepflegt werden.

## Hintergrundfilm

`site/media/rhein-abend.mp4` liegt hinter dem Kopf der Seite und löst sich nach
unten in die Seitenfarbe auf; `rhein-abend.jpg` ist das Standbild davor. Der Film
läuft ohne Ton und in Schleife, startet nicht bei „weniger Bewegung“ oder
Datensparmodus, und lässt sich oben rechts anhalten. Die Wahl bleibt gespeichert.

Anderer Film: mit demselben Rezept umwandeln (ohne Tonspur, damit die Datei klein
bleibt), als `site/media/` ablegen und die beiden Dateinamen im `<video>`-Element
in `src/page.html` eintragen.

    ffmpeg -i original.mp4 -an -vf "scale=1280:-2,format=yuv420p" \
           -c:v libx264 -preset slow -crf 31 -movflags +faststart \
           site/media/rhein-abend.mp4
    ffmpeg -ss 1 -i original.mp4 -frames:v 1 -vf scale=1280:-2 -q:v 5 \
           site/media/rhein-abend.jpg

Die Deckkraft des Schleiers über dem Film (`--scrim` in `src/page.html`) ist so
gewählt, dass die Schrift darüber den Kontrastwert AA der WCAG hält. Bei einem
helleren Film muss sie nach oben.

## Hosting

Jeder statische Webspace genügt (GitHub Pages, Netlify, Cloudflare Pages).
Wichtig ist nur, dass `roaring-silence.ics` öffentlich und dauerhaft unter
derselben Adresse erreichbar bleibt, sonst verlieren Abonnements die Verbindung.
Die Abo-Adresse leitet die Seite selbst aus ihrer eigenen Adresse ab.

Sprache: Deutsch ist Standard. `…/#en` öffnet die englische Fassung direkt.

Schriften: Archivo und Newsreader, beide unter der SIL Open Font License.
