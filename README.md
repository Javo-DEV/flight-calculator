# ✈️ MSFS 2020 Flight Calculator

Ein Python-basierter Flight Calculator für Microsoft Flight Simulator 2020 mit moderner Web-Oberfläche.

## 📋 Übersicht

Diese Anwendung bietet verschiedene Berechnungstools für präzise Flugplanung und Navigation im Microsoft Flight Simulator 2020. Die App läuft lokal auf Ihrem Computer und öffnet sich automatisch im Browser.

### ✨ Features

#### Navigation & Flight Planning
- **📉 Top of Descent (TOD) Calculator** - Berechnet den idealen Punkt zum Einleiten des Sinkflugs
- **📈 Top of Climb (TOC) Calculator** - Berechnet Steigflug-Parameter mit zwei Modi und Visualisierung
- **🌬️ Wind Correction Angle** - Ermittelt Windkorrektur und Ground Speed
- **🧭 Course Converter** - Konvertiert zwischen True und Magnetic Course (TVMDC)
- **📊 Ground Speed Calculator** - Schnelle Geschwindigkeitsberechnung bei bekanntem Heading

#### E6B Flight Computer (Tabbed Interface)
- **✈️ True Airspeed (TAS) Calculator** - Berechnet TAS aus IAS, Höhe und Temperatur
- **🌡️ Density Altitude Calculator** - Performance-kritische Berechnungen für Takeoff/Landing
- **⛽ Fuel Planner** - Treibstoffbedarf, Reichweite und Endurance-Berechnungen
- **🛬 Wind Components** - Gegen-/Rückenwind und Seitenwind für Runway Selection

#### Weight & Balance
- **⚖️ Weight & Balance Calculator** - Schwerpunkt-Berechnungen mit Aircraft Database
  - Cessna 172S Skyhawk
  - Cessna 208B Grand Caravan
  - Erweiterbar für weitere Aircraft-Modelle

#### Utilities
- **🔄 Unit Converter** - Konvertiert zwischen Höhe, Distanz, Gewicht und Treibstoff-Einheiten

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

#### Top of Climb (TOC)
Berechnet, wann Sie die Zielflughöhe erreichen:
- **Modus 1 (Steigrate bekannt):** Zeit, Distanz und Steigwinkel berechnen
- **Modus 2 (Zeit bekannt):** Benötigte Steigrate für gegebene Zeit berechnen
- Eingabe: Aktuelle Höhe, Zielhöhe, Steigrate ODER Zeit, Ground Speed
- Ausgabe: Zeit/Distanz bis TOC, Steigwinkel, Flugzeug-Kategorie-Empfehlung
- Inkl. **Steigflug-Profil Visualisierung**
- **Faustregel:** Bei 500 ft/min dauert Climb 1 Minute pro 500 ft

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

#### Unit Converter
Konvertiert zwischen verschiedenen Einheiten:
- **Höhe/Länge:** Feet ↔ Meters ↔ Kilometers
- **Distanz:** Nautical Miles ↔ Kilometers ↔ Statute Miles
- **Gewicht/Masse:** Kilograms ↔ Pounds ↔ Metric Tons
- **Treibstoff-Volumen:** Liters ↔ US Gallons ↔ Imperial Gallons
- Inkl. Referenzwerte und typischen Beispielen für jede Kategorie

### 🛩️ E6B Flight Computer

#### True Airspeed (TAS) Calculator
Berechnet True Airspeed aus Indicated Airspeed:
- Eingabe: IAS, Pressure Altitude, optional OAT (Temperatur)
- Ausgabe: TAS, Korrektur in %, ISA Deviation
- **Methode 1:** 2% Regel (TAS = IAS + 2% pro 1000 ft)
- **Methode 2:** Temperatur-basiert (präziser)
- **Verwendung:** Basis für alle Navigationsberechnungen

#### Density Altitude Calculator
Berechnet Density Altitude für Performance-Berechnungen:
- Eingabe: Field Elevation, OAT, QNH
- Ausgabe: Density Altitude, Pressure Altitude, ISA Deviation, Performance Impact
- **Wichtig:** Hohe Density Altitude = schlechtere Performance
- **Auswirkungen:** Längere Startstrecke, geringere Steigleistung
- Color-Coding: Grün (< 1000 ft diff) → Orange → Rot (kritisch)

#### Fuel Planner
Berechnet Treibstoffbedarf und Reichweite:
- **Modus 1 - Fuel Required:** Berechnet benötigten Fuel für Strecke
  - Eingabe: Distance, Ground Speed, Fuel Flow, Reserve
  - Ausgabe: Flight Fuel, Reserve Fuel, Total Fuel, Flight Time
- **Modus 2 - Endurance & Range:** Berechnet Reichweite mit vorhandenem Fuel
  - Eingabe: Available Fuel, Fuel Flow, Ground Speed
  - Ausgabe: Endurance, Range (mit und ohne Reserve)
- **Reserves:** VFR Day (30 min), VFR Night (45 min), IFR (45 min)

#### Wind Components Calculator
Berechnet Wind-Komponenten für Runway Operations:
- Eingabe: Runway, Wind Direction, Wind Speed
- Ausgabe: Headwind/Tailwind, Crosswind (mit Richtung), Angle Difference
- **Wichtig für:** Runway Selection, Performance Calculations
- **Warnings:** Tailwind-Warnung, High Crosswind Alert
- **Limits:** Typische GA Crosswind Limits angezeigt

#### Weight & Balance Calculator
Berechnet Gewicht und Schwerpunkt für verschiedene Flugzeuge:
- **Aircraft Database:** Cessna 172S Skyhawk, Cessna 208B Grand Caravan
- **Eingabe:** Aircraft Type, Fuel Amount, Passenger/Cargo Weights
- **Ausgabe:** Total Weight, CG Position, CG Limits, Weight Status, CG Status
- **Features:**
  - Automatische CG-Envelope-Prüfung
  - Weight Limits Checking (Max Ramp, Takeoff, Landing)
  - Station-by-Station Breakdown
  - Input Validation (Fuel Capacity, Station Limits)
  - Warning System (Approaching Limits)
- **Erweiterbar:** Neue Aircraft können einfach zur Datenbank hinzugefügt werden

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
│   ├── constants.py       # Aviation-Konstanten
│   └── aircraft_data.py   # Aircraft Database für W&B
├── tests/
│   ├── __init__.py
│   └── test_calculations.py  # Unit Tests (78 Tests)
├── assets/                # Bilder/Ressourcen
├── requirements.txt       # Python-Dependencies
├── .gitignore
└── README.md
```

## 🧪 Testing

Das Projekt verfügt über umfassende Unit Tests (**78 Tests**):

**Test Coverage:**
- TOD/TOC Calculations (19 Tests)
- Wind Correction & Ground Speed (6 Tests)  
- Unit Conversions (24 Tests)
- E6B Flight Computer (18 Tests)
  - True Airspeed
  - Density Altitude
  - Fuel Planning
  - Wind Components
- Weight & Balance (12 Tests)
  - W&B Calculations (Cessna 172, Cessna 208)
  - CG Envelope Validation
  - Station Weight Validation
  - Error Handling

Unit Tests ausführen:
```bash
pytest
```

Alle Tests ausführen mit Details:
```bash
pytest tests/test_calculations.py -v
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
- ✅ ~~Weight & Balance Calculator~~ (Implementiert!)
- ✅ ~~Unit Converter~~ (Implementiert!)
- ✅ ~~E6B Flight Computer~~ (Implementiert!)
- 📊 CG Envelope Visualization (Matplotlib Charts)
- 🎮 SimConnect-Integration (Live-Daten aus MSFS)
- 🗺️ Little Navmap Integration
- 🖥️ Desktop-App-Version (.exe mit PyWebView)
- ✈️ Weitere Aircraft (King Air, Citation, etc.)

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
