# Smarte Elektronik-Werkstatt – Bauteilverwaltung mit KI

Dieses Repository gehört zur Blogserie **„Smarte Elektronik-Werkstatt“** auf [draeger-it.blog](https://draeger-it.blog/).

Ziel des Projekts ist es, den eigenen Elektronik-Bauteilbestand zunächst strukturiert zu erfassen und später direkt in die Projektplanung mit **Claude** einzubeziehen.

Die Idee geht damit über eine klassische Inventarverwaltung hinaus: Claude soll künftig wissen, welche Mikrocontroller, Sensoren, Displays und weiteren Komponenten tatsächlich vorhanden sind und diese Informationen bei neuen Projektideen berücksichtigen.

## Was soll das Projekt später können?

Statt Claude beispielsweise nur zu fragen:

> „Erstelle mir ein Projekt zur Messung von Temperatur und Luftfeuchtigkeit mit einem Display.“

soll die eigene Bauteildatenbank in die Planung einbezogen werden.

Claude soll dadurch unter anderem prüfen können:

- Welche passenden Komponenten sind bereits vorhanden?
- Welche Mikrocontroller stehen zur Verfügung?
- Welche Sensoren oder Displays können verwendet werden?
- Fehlt ein Bauteil?
- Gibt es eine passende Alternative im eigenen Bestand?
- Wo befindet sich das benötigte Bauteil?

Langfristig soll zusätzlich die reale Lagerposition mit eingebunden werden. Die Bauteile werden deshalb bereits jetzt über **Reihe und Spalte** einem festen Platz zugeordnet.

## Aktueller Stand – Teil 1

In der ersten Ausbaustufe liegt der Fokus auf der Grundlage des Projekts:

- Elektronik-Bauteile katalogisieren
- Bestand verwalten
- Kategorien und Hersteller pflegen
- Schnittstellen hinterlegen
- WiFi, BLE, Matter, Zigbee und Thread erfassen
- Lagerposition über Reihe und Spalte speichern
- SQLite als Datenbasis verwenden
- Bauteile über eine Python-Anwendung durchsuchen

Die spätere Anbindung an Claude und einen eigenen MCP-Server baut auf dieser Datenbasis auf.

## Blogserie

### Teil 1 – Elektronik-Bauteile mit SQLite und Python verwalten

Im ersten Teil wird die Grundidee des Projekts vorgestellt. Außerdem geht es um den Aufbau der SQLite-Datenbank, die Katalogisierung des eigenen Bestands und die Suche über Python.

**Zum Beitrag:**  
https://draeger-it.blog/smarte-elektronik-werkstatt-bauteile-sqlite-python/

Weitere Teile der Serie werden nach und nach ergänzt.

## Verzeichnisstruktur

```text
bauteilverwaltung-mit-ki/
├── bauteilverwaltung/
│   ├── app.py
│   ├── suche.py
│   ├── database.py
│   ├── schema.sql
│   └── ...
└── README.md
```

### `bauteilverwaltung/app.py`

Grafische Oberfläche zum Erfassen und Bearbeiten des eigenen Bauteilbestands.

Unter anderem können gespeichert werden:

- Name
- Kategorie
- Hersteller
- Schnittstellen
- WiFi
- BLE
- Matter
- Zigbee
- Thread
- Bestand
- Reihe
- Spalte
- Beschreibung

### `bauteilverwaltung/suche.py`

Separate, lesende Oberfläche zum schnellen Durchsuchen der SQLite-Datenbank.

Die Suche läuft über mehrere Felder gleichzeitig und berücksichtigt unter anderem:

- Name
- Kategorie
- Hersteller
- Schnittstellen
- Beschreibung
- Reihe
- Spalte

### `bauteilverwaltung/database.py`

Enthält den Datenbankzugriff und die zentrale Logik für SQLite.

### `bauteilverwaltung/schema.sql`

Definiert die Struktur der SQLite-Datenbank.

Die Daten werden normalisiert über mehrere Tabellen verwaltet:

- `components`
- `categories`
- `manufacturers`
- `interfaces`
- `component_interfaces`

## Voraussetzungen

Benötigt wird:

- **Python 3**
- **Tkinter**
- **SQLite**

SQLite ist bereits Bestandteil der Python-Standardbibliothek.

Unter Linux muss Tkinter gegebenenfalls zusätzlich installiert werden.

### Fedora

```bash
sudo dnf install python3-tkinter
```

### Debian / Ubuntu

```bash
sudo apt install python3-tk
```

## Start

Repository klonen:

```bash
git clone https://github.com/StefanDraeger/bauteilverwaltung-mit-ki.git
```

In den Projektordner wechseln:

```bash
cd bauteilverwaltung-mit-ki/bauteilverwaltung
```

### Bauteile verwalten

```bash
python app.py
```

### Bauteile durchsuchen

```bash
python suche.py
```

## Warum SQLite?

Für eine kleine Inventarliste wäre auch JSON denkbar. Das Projekt soll jedoch später deutlich mehr können als nur Daten speichern.

SQLite bietet unter anderem:

- strukturierte Abfragen
- Beziehungen zwischen mehreren Tabellen
- saubere Verwaltung von Kategorien, Herstellern und Schnittstellen
- eine einzelne, leicht zu sichernde Datenbankdatei
- direkten Zugriff mit Python
- eine gute Grundlage für die spätere MCP-Anbindung

Damit bleibt das Projekt einfach, bietet aber trotzdem genug Struktur für die kommenden Ausbaustufen.

## Roadmap

Geplant sind unter anderem:

- [x] SQLite-Datenbank für Elektronik-Bauteile
- [x] grafische Bauteilverwaltung mit Python
- [x] separates Suchinterface
- [x] Lagerposition über Reihe und Spalte
- [ ] Claude an die Bauteildatenbank anbinden
- [ ] eigener MCP-Server
- [ ] Bauteilbestand in den Kontext der Projektplanung einbeziehen
- [ ] passende Komponenten aus dem vorhandenen Bestand auswählen
- [ ] fehlende Komponenten erkennen
- [ ] Alternativen aus dem eigenen Bestand vorschlagen
- [ ] reale Lagerfächer mit LEDs hervorheben
- [ ] ESP32 zur Ansteuerung des Lager- bzw. LED-Systems

## Motivation

Mit der Zeit sammeln sich in einer Elektronik-Werkstatt viele Sensoren, Entwicklungsboards, Displays, LEDs und weitere Komponenten an. Irgendwann stellt sich nicht nur die Frage, **was vorhanden ist**, sondern auch **wo es liegt** und **ob für ein neues Projekt bereits alle benötigten Bauteile vorhanden sind**.

Dieses Projekt soll genau hier ansetzen und die klassische Bauteilverwaltung mit einer späteren KI-gestützten Projektplanung verbinden.

## Autor

**Stefan Draeger**  
https://draeger-it.blog/

## Lizenz

Siehe die im Repository enthaltene Lizenzdatei.
