# 🎯 Betting Analyzer Pro

**Betting Analyzer Pro** ist ein mit Python entwickeltes Programm zur Berechnung und Analyse von Sportwetten. Es bietet verschiedene Werkzeuge zur Absicherung von Wetten, zur Berechnung von Kombinationsquoten und zur Analyse von Wettkombinationen.

Zusätzlich enthält das Programm einen Kapitalmanager, mit dem sich das Startkapital, abgeschlossene Wetten und die aktuelle Bilanz verwalten lassen.

Die grafische Benutzeroberfläche basiert auf **PySide6**. Daten können lokal im JSON-Format gespeichert und wieder geladen werden.

## ✨ Features

### 🛡️ Absicherungsrechner
- Berechnung von Wettabsicherungen mit zwei möglichen Ausgängen.
- Berechnung von Absicherungen mit drei möglichen Ausgängen (Dutching).
- Berechnung anhand verschiedener Gewinnziele.
- Ermittlung des benötigten Einsatzes und der erforderlichen Gegenquote.

### 📊 Kombi-Zielquoten-Rechner
- Berechnung der benötigten Einzelquoten für Kombiwetten.
- Unterstützung von Kombinationen mit 2 bis 5 Auswahlen.
- Berechnung von Gesamtquote, möglicher Auszahlung und Nettogewinn.

### 🔍 Kombi-Analysator
- Beliebig viele Quoten können hinzugefügt werden.
- Einzelne Quoten können entfernt werden.
- Berechnung der Gesamtquote aller eingegebenen Auswahlen.
- Anzeige von Auszahlung und Nettogewinn.

### 💰 Kapitalmanager
- Verwaltung des Startkapitals.
- Erfassung abgeschlossener Wetten mit Gewinn oder Verlust.
- Anzeige der aktuellen Kapitalentwicklung.
- Speicherung einer Wett-Historie.
- Einzelne Einträge können gelöscht werden.

### 💾 Datenspeicherung
- Speichern und Laden der Daten im JSON-Format.
- Lokale Speicherung der Eingaben und der Wett-Historie.

### 💱 Währungsauswahl
- Unterstützung für Euro (€), US-Dollar ($), USDT und Britische Pfund (£).
- Auswahl der gewünschten Anzeigewährung.

## ⚙️ Voraussetzungen

- Python 3.10 oder höher
- PySide6

## 📥 Installation

### 1. Projekt herunterladen

Öffne das GitHub-Repository und klicke auf **Code → Download ZIP**.

### 2. ZIP-Datei entpacken

Entpacke die heruntergeladene ZIP-Datei in einen beliebigen Ordner auf deinem Computer.

### 3. PySide6 installieren

Öffne ein Terminal und führe folgenden Befehl aus:

```bash
pip install PySide6
```

### 4. Programm starten

Wechsle im Terminal in den Ordner, in dem sich die Datei `Betting_Analyzer_Pro.py` befindet, und starte das Programm mit:

```bash
python Betting_Analyzer_Pro.py
```

## 🖥️ Programmoberfläche

Betting Analyzer Pro verfügt über eine übersichtliche grafische Benutzeroberfläche mit vier Hauptbereichen:

1. **Absicherungsrechner** – Berechnung von Wettabsicherungen mit zwei oder drei möglichen Ausgängen.
2. **Kombi-Zielquoten-Rechner** – Ermittlung der benötigten Einzelquoten für Kombiwetten.
3. **Kombi-Analysator** – Analyse von Wettkombinationen mit mehreren Auswahlen.
4. **Kapitalmanager** – Verwaltung des Startkapitals und der abgeschlossenen Wetten.

Im oberen Bereich werden das aktuelle Kapital, die Bilanz seit dem Start und die Anzahl der erfassten Wetten angezeigt.

Über die Schaltflächen im unteren Bereich können Daten gespeichert, geladen oder die Anwendung zurückgesetzt werden.

## 💾 Datenspeicherung

Betting Analyzer Pro verwendet JSON-Dateien zur lokalen Speicherung der Anwendungsdaten.

Folgende Informationen können gespeichert und wieder geladen werden:

- Ausgewählte Währung
- Startkapital
- Erfasste Wett-Historie
- Eingaben des Kombi-Analysators
- Eingaben der verschiedenen Rechner

Über die Schaltfläche **Speichern** können die Daten als JSON-Datei auf dem Computer abgelegt werden.

Mit **Laden** können zuvor gespeicherte Daten wiederhergestellt werden.

Die Schaltfläche **Zurücksetzen** setzt die Anwendung auf ihre Ausgangswerte zurück und löscht die aktuell erfasste Wett-Historie innerhalb der Anwendung.


## ⚠️ Hinweise zur Verwendung

- Alle Berechnungen basieren auf den eingegebenen Einsätzen und Quoten.
- Die eingegebenen Quoten müssen größer als 1 sein.
- Die Einsätze müssen größer als 0 sein.
- Bei Absicherungsberechnungen müssen alle möglichen Ausgänge berücksichtigt werden, damit die geplante Absicherung funktioniert.
- Die Berechnungen berücksichtigen keine Buchmachergebühren, Steuern, Einsatzlimits oder Quotenänderungen.
- Die Kapitalverwaltung basiert auf manuell eingetragenen Wett-Ergebnissen und ist nicht direkt mit Buchmachern verbunden.
- Die Währungsauswahl dient ausschließlich der Anzeige. Es findet keine automatische Währungsumrechnung statt.

**Wichtiger Hinweis:** Betting Analyzer Pro ist ein Berechnungs- und Verwaltungstool. Es garantiert keine Gewinne und ersetzt keine eigenständige Prüfung der Wettbedingungen.


## 🛠️ Verwendete Technologien

- **Python 3** – Programmiersprache
- **PySide6** – Erstellung der grafischen Benutzeroberfläche
- **JSON** – Speicherung und Wiederherstellung der Anwendungsdaten
- **Decimal** – Präzise Berechnung von Einsätzen, Quoten und Gewinnen

## 🤖 Entwicklung

Betting Analyzer Pro wurde mit Unterstützung von **ChatGPT (OpenAI)** entwickelt.

## 📁 Projektstruktur

```text
Betting-Analyzer-Pro/
│
├── betting_analyzer_pro.py
└── README.md
```

## 🎥 YouTube-Tutorial

Du möchtest sehen, wie Betting Analyzer Pro funktioniert und wie das Programm verwendet wird?

In meinem YouTube-Tutorial zeige ich dir die Anwendung und ihre verschiedenen Funktionen Schritt für Schritt.

👉 **Zum YouTube-Tutorial:** [Hier klicken](DEIN-YOUTUBE-LINK)

## 👨‍💻 Autor

Entwickelt von **RONIN**.

Vielen Dank für dein Interesse an Betting Analyzer Pro!
