# QS-Berichte MAS – Dashboard

Ein interaktives Qualitätssicherungs-Dashboard auf Basis von [Streamlit](https://streamlit.io/).

## Features

- **KPI-Karten**: Gesamtberichte, Fehleranzahl, kritische Fehler, offene Meldungen, Behebungsquote
- **Monatlicher Fehlertrend** (Balkendiagramm)
- **Fehlerkategorien** (Donut-Diagramm)
- **Fehler je Abteilung** nach Schweregrad (gestapeltes Balkendiagramm)
- **Status-Übersicht** (Offen / In Bearbeitung / Behoben)
- **Heatmap** Produkt × Fehlerkategorie
- **Rohdaten-Tabelle** mit CSV-Export
- **Eigene CSV-Datei** hochladbar über die Seitenleiste

## Schnellstart

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# Dashboard starten
streamlit run app.py
```

Das Dashboard öffnet sich automatisch unter `http://localhost:8501`.

## CSV-Format (eigene Daten)

| Spalte | Beschreibung |
|---|---|
| `Datum` | ISO-Datum, z. B. `2025-01-15` |
| `Abteilung` | z. B. `Fertigung`, `Montage`, `Logistik`, `QS` |
| `Produkt` | z. B. `Produkt A` |
| `Fehlerkategorie` | z. B. `Maßabweichung`, `Oberflächenfehler` |
| `Schweregrad` | `Kritisch`, `Mittel` oder `Gering` |
| `Status` | `Offen`, `In Bearbeitung` oder `Behoben` |
| `Anzahl_Fehler` | Ganzzahl |
| `Prüfer` | Name des Prüfers |
| `Bemerkung` | Freitext |

Beispieldaten befinden sich in `data/qs_berichte.csv`.