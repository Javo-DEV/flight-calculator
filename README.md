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
