# Smarte Elektronik-Werkstatt

Ein kleines Python-Tool zur Verwaltung von Elektronik-Bauteilen in einer SQLite-Datenbank.

Das Projekt ist die Basis für die Blogserie **„Die smarte Elektronik-Werkstatt“** auf [draeger-it.blog](https://draeger-it.blog/).

## Funktionen

- SQLite-Datenbank neu anlegen oder vorhandene Datenbank öffnen
- Elektronik-Bauteile anlegen, bearbeiten und löschen
- Suche nach Name, Kategorie, Hersteller, Reihe, Spalte, Beschreibung und Schnittstelle
- Kategorien und Hersteller als separate Stammdaten
- Schnittstellen als Mehrfachauswahl
- Funkstandards als Checkboxen:
  - WiFi
  - BLE
  - Matter
  - Zigbee
  - Thread
- Bestand sowie Lagerposition über Reihe und Spalte verwalten
- Freie Beschreibung, z. B. Displaygröße oder besondere Merkmale


## Oberfläche

Die Anwendung verwendet eine moderne dunkle Dashboard-Oberfläche auf Basis von Tkinter/ttk. Es sind keine zusätzlichen GUI-Pakete erforderlich.

Die Startansicht bietet:

- Kennzahlen zu Bauteilen, Gesamtbestand, Kategorien und Herstellern
- große Volltextsuche
- tabellarische Bestandsübersicht
- Detailformular zum Bearbeiten
- separate Stammdatenverwaltung


## Voraussetzungen

- Python 3
- Tkinter

SQLite ist bereits Bestandteil der Python-Standardbibliothek.

### Tkinter unter Linux

Auf manchen Linux-Distributionen muss Tkinter separat installiert werden.

Fedora:

```bash
sudo dnf install python3-tkinter
```

Debian / Ubuntu:

```bash
sudo apt install python3-tk
```

Unter Windows und macOS ist Tkinter bei den üblichen Python-Installationen in der Regel bereits enthalten.

## Start

Repository herunterladen oder klonen und anschließend:

```bash
python app.py
```

Beim ersten Start wird automatisch eine Datei `workshop.db` im Projektverzeichnis angelegt.

Alternativ können über **Datei → Datenbank öffnen** vorhandene SQLite-Dateien geöffnet werden.

## Datenmodell

Die Datenbank besteht aus den Tabellen:

- `components`
- `categories`
- `manufacturers`
- `interfaces`
- `component_interfaces`

Die Tabelle `component_interfaces` bildet die n:m-Beziehung zwischen Bauteilen und Schnittstellen ab. Ein Bauteil kann dadurch beispielsweise gleichzeitig GPIO, I2C, SPI und UART unterstützen.

## Warum SQLite?

SQLite benötigt keinen eigenen Datenbankserver. Die gesamte Datenbank befindet sich in einer einzelnen Datei und lässt sich problemlos sichern oder übertragen.

Gleichzeitig können die Daten später strukturiert durchsucht werden. Damit eignet sich SQLite gut als Grundlage für die geplante Anbindung an Claude über einen eigenen MCP-Server.

## Geplante Erweiterungen

- erweiterte Filter
- Import / Export
- technische Eigenschaften von Bauteilen
- MCP-Server für Claude
- Projektplanung anhand des vorhandenen Bestands
- Zuordnung von Lagerfächern
- spätere Ansteuerung eines ESP32 / LED-Systems zum Hervorheben eines Lagerfachs

## Lizenz

MIT
