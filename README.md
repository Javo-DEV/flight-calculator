# ✈️ MSFS 2020 Flight Calculator

Ein Python-basierter Flight Calculator für Microsoft Flight Simulator 2020 mit moderner Web-Oberfläche.

## 📋 Übersicht

Diese Anwendung bietet verschiedene Berechnungstools für präzise Flugplanung und Navigation im Microsoft Flight Simulator 2020. Die App läuft lokal auf Ihrem Computer und öffnet sich automatisch im Browser.

### ✨ Features

- **📉 Top of Descent (TOD) Calculator** - Berechnet den idealen Punkt zum Einleiten des Sinkflugs
- **🌬️ Wind Correction Angle** - Ermittelt Windkorrektur und Ground Speed
- **🧭 Course Converter** - Konvertiert zwischen True und Magnetic Course (TVMDC)
- **📊 Ground Speed Calculator** - Schnelle Geschwindigkeitsberechnung bei bekanntem Heading

### 🎯 Technologie

- **Python 3.12+**
- **Streamlit** - Web-Framework für die UI
- **NumPy** - Mathematische Berechnungen
- **Git** - Versionskontrolle

## 🚀 Installation

### Voraussetzungen

- Python 3.10 oder höher ([Download](https://www.python.org/downloads/))
- Git ([Download](https://git-scm.com/downloads))

### Setup

1. **Repository klonen:**
   ```bash
   git clone https://code.siemens.com/jan.vollmar/flight_calculator.git
   cd flight_calculator
   ```

2. **Virtual Environment erstellen:**
   ```bash
   python -m venv .venv
   ```

3. **Virtual Environment aktivieren:**
   - **Windows:**
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **macOS/Linux:**
     ```bash
     source .venv/bin/activate
     ```

4. **Dependencies installieren:**
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Verwendung

1. **App starten:**
   ```bash
   streamlit run app.py
   ```

2. Die App öffnet sich automatisch in Ihrem Browser unter `http://localhost:8501`

3. Wählen Sie einen Rechner aus der Sidebar und geben Sie Ihre Werte ein

### 🧮 Verfügbare Rechner

#### Top of Descent (TOD)
Berechnet, wann Sie den Sinkflug einleiten müssen:
- Eingabe: Aktuelle Höhe, Zielhöhe, Sinkwinkel (Standard: 3°), Ground Speed
- Ausgabe: Distanz bis TOD, Sinkrate, Sinkzeit
- **Faustregel:** Höhenverlust (ft) ÷ 300 = Distanz (NM)

#### Wind Correction Angle
Berechnet Kurskorrektur bei Wind:
- Eingabe: True Airspeed, Desired Course, Wind FROM, Wind Speed
- Ausgabe: Wind Correction Angle, True Heading, Ground Speed, Drift Angle
- Inkl. Anzeige von Gegen-/Rückenwind und Seitenwind-Komponenten

#### Course Converter
Konvertiert zwischen True und Magnetic Course:
- Eingabe: Kurs-Wert, Magnetic Variation (East/West)
- Ausgabe: Konvertierter Kurs nach TVMDC-Regel
- **Merkhilfe:** "East is Least, West is Best"

#### Ground Speed Calculator
Schnelle Ground Speed Berechnung:
- Eingabe: True Airspeed, True Heading, Wind FROM, Wind Speed
- Ausgabe: Ground Speed, Actual Track, Wind-Komponenten
- Optional: Flugzeitberechnung bei bekannter Distanz

## 🎨 UI-Architektur

### Allgemeine Screen-Struktur

Alle Calculator-Screens folgen einem einheitlichen **2-Spalten-Layout** für eine konsistente Benutzererfahrung:

| **Header + Beschreibung** | |
|---------------------------|---------------------------|
| 🟢 **Eingabe-Spalte (col1)** | 🟠 **Ergebnis-Spalte (col2)** |

### Container-Typen

| Container-Typ | Verwendung | Beispiel |
|---------------|------------|----------|
| `st.columns([1, 1])` | Hauptlayout (50/50) | Eingabe/Ergebnis Trennung |
| `st.columns(2)` | Unterspalten | Metriken nebeneinander |
| `st.expander()` | Klappbare Sektion | Detaillierte Erklärungen |
| `st.info()` | Info-Box | Faustregeln, Tipps |
| `st.success()` | Erfolgs-Box | Große Ergebnisse |
| `st.metric()` | Einzelne Metrik | Zahlenwerte mit Label |
| `st.number_input()` | Zahleneingabe | TAS, Altitude, etc. |
| `st.slider()` | Schieberegler | Descent Angle |
| `st.radio()` | Auswahlbuttons | True→Magnetic |
| `st.button()` | Aktionsbutton | "Berechnen" |
| `st.pyplot()` | Plot-Anzeige | Wind Triangle |

### Typischer Workflow

**Alle Calculator folgen diesem Schema:**
```
INPUT (links) → BUTTON → RESULTS (rechts) → VISUALIZATION (unten)
```

**User Flow:**
1. User füllt **Input-Felder** aus
2. User klickt **"Berechnen"** Button (oder Auto-Berechnung bei Wertänderung)
3. **Haupt-Metriken** werden angezeigt (in 2 Sub-Spalten)
4. **Zusatz-Info** folgt (Wind-Komponenten, Faustregel, etc.)
5. **Erklärung** ist klappbar verfügbar (Expander)
6. **Visualisierung** (nur beim Wind Correction Calculator)

### Beispiel: Wind Correction Angle Calculator

| **Bereich** | **Container-Typ** | **Inhalt** | **Layout** |
|-------------|-------------------|------------|------------|
| 📋 **Header** | `st.header()` | Titel + Beschreibung | Volle Breite |
| | | | |
| **🟢 Eingabe-Spalte (col1)** | | | **50% Links** |
| ↳ Input 1 | `st.number_input()` | True Airspeed (TAS) | |
| ↳ Input 2 | `st.number_input()` | True Course | |
| ↳ Input 3 | `st.number_input()` | Wind FROM | |
| ↳ Input 4 | `st.number_input()` | Wind Speed | |
| ↳ Action | `st.button()` | 🧮 **Berechnen** | Blau #1E88E5 |
| | | | |
| **🟠 Ergebnis-Spalte (col2)** | | | **50% Rechts** |
| ↳ Haupt-Metriken | `st.columns(2)` | col_a + col_b | 2-spaltig |
| &nbsp;&nbsp;&nbsp;• WCA | `st.metric()` | Wind Correction Angle | col_a |
| &nbsp;&nbsp;&nbsp;• Ground Speed | `st.metric()` | Berechnete GS | col_b |
| &nbsp;&nbsp;&nbsp;• True Heading | `st.metric()` | Korrigierter Kurs | col_a |
| &nbsp;&nbsp;&nbsp;• Drift Angle | `st.metric()` | Abtrift | col_b |
| ↳ Wind-Details | `st.columns(2)` | col_c + col_d | 2-spaltig |
| &nbsp;&nbsp;&nbsp;• Gegen-/Rückenwind | `st.metric()` | Headwind/Tailwind | col_c |
| &nbsp;&nbsp;&nbsp;• Seitenwind | `st.metric()` | Crosswind | col_d |
| ↳ Erklärung | `st.expander()` | Klappbarer Hilfetext | Volle Breite |
| ↳ Visualisierung | `st.pyplot()` | 🎨 Wind Triangle Plot | Volle Breite |

## 📐 Einheiten

Alle Berechnungen verwenden Aviation-Standard-Einheiten:
- **Höhe:** Fuß (ft)
- **Geschwindigkeit:** Knoten (kts)
- **Distanz:** Nautische Meilen (NM)
- **Winkel:** Grad (°)
- **Vertikale Geschwindigkeit:** ft/min

## 📁 Projektstruktur

```
flight_calculator/
├── app.py                 # Haupt-Streamlit-Anwendung
├── src/
│   ├── __init__.py
│   ├── calculations.py    # Core-Berechnungslogik
│   └── constants.py       # Aviation-Konstanten
├── tests/
│   ├── __init__.py
│   └── test_calculations.py  # Unit Tests
├── assets/                # Bilder/Ressourcen
├── requirements.txt       # Python-Dependencies
├── .gitignore
└── README.md
```

## 🧪 Testing

Unit Tests ausführen:
```bash
pytest
```

Mit Coverage-Report:
```bash
pytest --cov=src tests/
```

## 🛠️ Entwicklung

### Code-Formatierung
```bash
black .
```

### Linting
```bash
flake8 src/ tests/
```

## 🗺️ Roadmap

Geplante Features für zukünftige Versionen:
- 🔧 Treibstoffberechnung
- ⚖️ Weight & Balance Calculator
- 📏 Unit Converter (ft↔m, kts↔km/h)
- 🎮 SimConnect-Integration (Live-Daten aus MSFS)
- 🖥️ Desktop-App-Version (.exe mit PyWebView)

## 🤝 Contributing

Contributions sind willkommen! Bitte erstellen Sie einen Merge Request auf code.siemens.com.

## 👤 Author

**Jan Vollmar**
- Repository: [code.siemens.com/jan.vollmar/flight_calculator](https://code.siemens.com/jan.vollmar/flight_calculator)

## 📝 Lizenz

Dieses Projekt ist für den internen Gebrauch bei Siemens.

## 🙏 Acknowledgments

- Luftfahrt-Formeln basierend auf ICAO Standard Atmosphere (ISA)
- TVMDC-Regel für Kursumrechnung
- Wind-Dreieck-Berechnungen nach standardisierten Navigations-Methoden

---

**Viel Spaß beim Fliegen! ✈️**
