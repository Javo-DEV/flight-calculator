"""
MSFS 2020 Flight Calculator
A web-based aviation calculator for Microsoft Flight Simulator 2020

Author: Jan Vollmar
Repository: https://code.siemens.com/jan.vollmar/flight_calculator
"""

# ============================================================================
# IMPORTS
# ============================================================================

# Streamlit - Web framework for creating the UI
import streamlit as st

# System imports for path management
import sys
from pathlib import Path

# NumPy - For mathematical operations (vectors, trigonometry)
import numpy as np

# Matplotlib - For plotting the wind triangle visualization
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Add src folder to Python path so we can import our custom modules
sys.path.append(str(Path(__file__).parent / "src"))

# Import aviation calculation functions from our calculations module
from src.calculations import (
    calculate_descent_rate,      # Calculate Top of Descent (TOD) and sink rate
    calculate_toc_by_rate,        # Calculate Top of Climb by climb rate
    calculate_toc_by_time,        # Calculate Top of Climb by available time
    calculate_wind_correction,    # Calculate Wind Correction Angle (WCA)
    convert_course,               # Convert between True and Magnetic course
    calculate_ground_speed,       # Calculate ground speed from TAS and wind
    calculate_rule_of_thumb_tod,  # Quick TOD rule (altitude/300)
    calculate_rule_of_thumb_toc,  # Quick TOC rule (altitude/300)
    calculate_time_and_fuel,      # Calculate flight time and fuel consumption
    convert_altitude,             # Convert altitude between feet, meters, km
    convert_distance,             # Convert distance between NM, km, miles
    convert_weight,               # Convert weight between kg, lbs, tons
    convert_fuel_volume,          # Convert fuel volume between liters, gallons
    # E6B Flight Computer Functions
    calculate_true_airspeed,      # Calculate TAS from IAS and altitude
    calculate_density_altitude,   # Calculate density altitude
    calculate_fuel_required,      # Calculate fuel requirements
    calculate_endurance_and_range,  # Calculate endurance and range
    calculate_wind_components     # Calculate headwind/crosswind components
)

# Import aviation constants and default values
from src.constants import (
    STANDARD_DESCENT_ANGLE,    # Default 3° descent angle (ILS glideslope)
    DEFAULT_TAS,               # Default True Airspeed (120 kts)
    DEFAULT_CRUISE_ALTITUDE    # Default cruise altitude (5000 ft)
)


# ============================================================================
# STREAMLIT PAGE CONFIGURATION
# ============================================================================

# Configure the Streamlit page settings (must be first Streamlit command)
st.set_page_config(
    page_title="MSFS 2020 Flight Calculator",  # Browser tab title
    page_icon="✈️",                             # Browser tab icon
    layout="wide",                              # Use full width of browser
    initial_sidebar_state="expanded"           # Show sidebar by default
)

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================

# Inject custom CSS to improve the visual appearance of the app
st.markdown("""
    <style>
    /* Main header styling - large blue centered title */
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Calculator section containers - light gray background boxes */
    .calculator-section {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Result display boxes - light blue with accent border */
    .result-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# MAIN APPLICATION FUNCTION
# ============================================================================

def main():
    """
    Main application entry point.
    
    This function:
    1. Displays the main header
    2. Creates the sidebar navigation menu
    3. Routes to the selected calculator based on user choice
    """
    
    # Display the main application header using custom CSS class
    st.markdown('<h1 class="main-header">✈️ MSFS 2020 Flight Calculator</h1>', 
                unsafe_allow_html=True)
    
    # ========================================================================
    # SIDEBAR NAVIGATION
    # ========================================================================
    
    st.sidebar.title("🧭 Navigation")
    st.sidebar.markdown("---")  # Horizontal divider line
    
    # Create radio button menu for selecting calculators
    # The selected value is stored in 'calculator' variable
    calculator = st.sidebar.radio(
        "Wählen Sie einen Rechner:",
        [
            "🏠 Home",                      # Landing page with information
            "📉 Top of Descent (TOD)",      # TOD/descent rate calculator
            "📈 Top of Climb (TOC)",        # TOC/climb rate calculator
            "🌬️ Wind Correction Angle",   # WCA and ground speed calculator
            "🧭 Course Converter",         # True/Magnetic course conversion
            "📊 Ground Speed",             # Ground speed calculator
            "🔄 Unit Converter",           # Unit conversion tool
            "✈️ True Airspeed (TAS)",     # TAS calculator (E6B)
            "🌡️ Density Altitude",        # Density altitude calculator (E6B)
            "⛽ Fuel Planner",             # Fuel calculations (E6B)
            "🛬 Wind Components"           # Runway wind components (E6B)
        ]
    )
    
    st.sidebar.markdown("---")  # Another divider line
    
    # Display informational box in sidebar with app description and units
    st.sidebar.info(
        "**MSFS 2020 Flight Calculator**\n\n"
        "Ein Tool für präzise Flugberechnungen im Microsoft Flight Simulator.\n\n"
        "Alle Werte in Aviation-Standard-Einheiten:\n"
        "- Altitude: Fuß (ft)\n"
        "- Speed: Knoten (kts)\n"
        "- Distance: Nautische Meilen (NM)\n"
        "- Angles: Grad (°)"
    )
    
    # ========================================================================
    # ROUTE TO SELECTED CALCULATOR
    # ========================================================================
    
    # Based on user selection, call the appropriate calculator function
    if calculator == "🏠 Home":
        show_home()
    elif calculator == "📉 Top of Descent (TOD)":
        show_tod_calculator()
    elif calculator == "📈 Top of Climb (TOC)":
        show_toc_calculator()
    elif calculator == "🌬️ Wind Correction Angle":
        show_wind_correction_calculator()
    elif calculator == "🧭 Course Converter":
        show_course_converter()
    elif calculator == "📊 Ground Speed":
        show_ground_speed_calculator()
    elif calculator == "🔄 Unit Converter":
        show_unit_converter()
    elif calculator == "✈️ True Airspeed (TAS)":
        show_tas_calculator()
    elif calculator == "🌡️ Density Altitude":
        show_density_altitude_calculator()
    elif calculator == "⛽ Fuel Planner":
        show_fuel_planner()
    elif calculator == "🛬 Wind Components":
        show_wind_components_calculator()


# ============================================================================
# HOME PAGE DISPLAY
# ============================================================================

def show_home():
    """
    Display the home/landing page with information about available calculators.
    
    This page provides an overview of all calculator features and guides users
    to select a calculator from the sidebar.
    """
    st.header("Willkommen beim MSFS 2020 Flight Calculator!")
    
    st.write("""
    Diese Anwendung bietet verschiedene Berechnungstools für den Microsoft Flight Simulator 2020.
    Wählen Sie einen Rechner aus der Sidebar, um zu beginnen.
    """)
    
    # Create two columns for side-by-side calculator descriptions
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📉 Top of Descent (TOD)")
        st.write("""
        Berechnet den Punkt, an dem Sie mit dem Sinkflug beginnen müssen, um eine bestimmte 
        Zielhöhe zu erreichen. Inkl. Sinkrate und Flugzeit.
        
        **Ideal für:** ILS-Anflüge, Abstiegsplanung
        """)
        
        st.subheader("📈 Top of Climb (TOC)")
        st.write("""
        Berechnet den Punkt, an dem Sie die Zielflughöhe erreichen. Zwei Modi: 
        Berechnung nach Steigrate oder verfügbarer Zeit. Inkl. Steigprofil-Visualisierung.
        
        **Ideal für:** Steigflug-Planung, Performance-Checks
        """)
        
        st.subheader("🧭 Course Converter")
        st.write("""
        Konvertiert zwischen True Course und Magnetic Course unter Berücksichtigung 
        der magnetischen Variation.
        
        **Ideal für:** Navigation, Flugplanung
        """)
    
    with col2:
        st.subheader("🌬️ Wind Correction Angle")
        st.write("""
        Berechnet den Wind Correction Angle (WCA) und die Ground Speed basierend auf 
        True Airspeed, Kurs und Wind.
        
        **Ideal für:** Kurskorrektur, Navigation bei Wind
        """)
        
        st.subheader("📊 Ground Speed")
        st.write("""
        Schnelle Berechnung der Ground Speed bei gegebenem Heading und Windbedingungen.
        
        **Ideal für:** Schnelle Geschwindigkeitschecks
        """)
        
        st.subheader("🔄 Unit Converter")
        st.write("""
        Konvertiert zwischen verschiedenen Einheiten: Höhe, Distanz, Gewicht und Treibstoff.
        
        **Ideal für:** Umrechnung zwischen metrischen und Aviation-Einheiten
        """)
    
    st.markdown("---")
    st.subheader("🛩️ E6B Flight Computer")
    st.write("**Klassische E6B-Rechner für Performance-Berechnungen:**")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.write("""
        **✈️ True Airspeed (TAS):** Berechnet TAS aus IAS und Druckhöhe
        
        **🌡️ Density Altitude:** Performance-kritische Berechnungen für Takeoff/Landing
        """)
    
    with col4:
        st.write("""
        **⛽ Fuel Planner:** Treibstoffbedarf, Reichweite und Endurance
        
        **🛬 Wind Components:** Gegen-/Rückenwind und Seitenwind für Runway Selection
        """)
    
    st.markdown("---")
    st.info("💡 **Tipp:** Alle Rechner verwenden Aviation-Standard-Einheiten (Fuß, Knoten, Grad)")


# ============================================================================
# WIND TRIANGLE VISUALIZATION
# ============================================================================

def plot_wind_triangle(tas, true_course, wind_from, wind_speed, wca, true_heading, ground_speed):
    """
    Create a visual representation of the wind triangle using matplotlib.
    
    The wind triangle shows the relationship between:
    - True Airspeed (TAS) vector - where the aircraft points
    - Wind vector - wind effect on the aircraft
    - Ground Speed (GS) vector - actual path over ground
    
    Features dynamic zoom based on Wind Correction Angle (WCA) size:
    - Small WCA (< 5°): Close zoom for detailed view
    - Medium WCA (5-15°): Medium zoom
    - Large WCA (> 15°): Normal zoom
    
    Args:
        tas: True airspeed in knots
        true_course: Desired true course in degrees (where you want to go)
        wind_from: Wind FROM direction in degrees (e.g., 270° = wind from West)
        wind_speed: Wind speed in knots
        wca: Wind correction angle in degrees (calculated)
        true_heading: Calculated true heading in degrees (where to point aircraft)
        ground_speed: Calculated ground speed in knots (actual speed over ground)
    
    Returns:
        matplotlib.figure.Figure: The generated plot figure
    """
    # ========================================================================
    # SETUP PLOT
    # ========================================================================
    
    # Create a 10x8 inch figure with equal aspect ratio (so circles look circular)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_aspect('equal')  # Equal scaling for x and y axes
    
    # ========================================================================
    # CONVERT ANGLES AND CALCULATE VECTORS
    # ========================================================================
    
    # Convert angles from aviation convention (0°=North) to math convention (0°=East)
    # Aviation: 0°=N, 90°=E, 180°=S, 270°=W
    # Math: 0°=E, 90°=N, 180°=W, 270°=S
    tc_rad = np.radians(90 - true_course)   # Desired track (where we want to go)
    th_rad = np.radians(90 - true_heading)  # Aircraft heading (where aircraft points)
    wd_rad = np.radians(90 - wind_from)     # Wind FROM direction
    
    # Scale factor to make all vectors fit nicely in the plot
    # Normalizes the largest speed to 100 units
    scale = 100 / max(tas, wind_speed, ground_speed)
    
    # Origin point (0, 0) - where all vectors start
    origin = np.array([0, 0])
    
    # ========================================================================
    # CALCULATE VECTOR END POINTS
    # ========================================================================
    
    # Vector 1: True Airspeed (TAS) - where the aircraft points
    # This shows the heading the pilot must fly to counter the wind
    tas_end = origin + np.array([tas * scale * np.cos(th_rad), 
                                   tas * scale * np.sin(th_rad)])
    
    # Vector 2: Wind vector - shows wind effect
    # Note: Wind FROM 270° means wind is blowing TO 090° (East)
    # We negate the direction because wind blows FROM the given direction
    wind_end = origin + np.array([-wind_speed * scale * np.cos(wd_rad), 
                                    -wind_speed * scale * np.sin(wd_rad)])
    
    # Vector 3: Ground Speed (GS) - actual path over ground
    # This is the resultant vector showing where the aircraft actually goes
    gs_end = origin + np.array([ground_speed * scale * np.cos(tc_rad), 
                                 ground_speed * scale * np.sin(tc_rad)])
    
    # Calculate dynamic arrow head sizes based on vector lengths
    arrow_scale = max(tas, wind_speed, ground_speed) * scale / 100
    head_width = max(2, 3 * arrow_scale)
    head_length = max(3, 4 * arrow_scale)
    
    # Draw vectors
    # TAS vector (blue) - where aircraft points
    ax.arrow(origin[0], origin[1], tas_end[0], tas_end[1], 
             head_width=head_width, head_length=head_length, fc='blue', ec='blue', linewidth=2.5,
             label=f'TAS: {tas} kts @ {true_heading:.0f}°')
    
    # Wind vector (red) - wind effect
    ax.arrow(origin[0], origin[1], wind_end[0], wind_end[1], 
             head_width=head_width, head_length=head_length, fc='red', ec='red', linewidth=2.5,
             label=f'Wind: {wind_speed} kts FROM {wind_from:.0f}°', linestyle='--')
    
    # Ground Speed vector (green) - actual track
    ax.arrow(origin[0], origin[1], gs_end[0], gs_end[1], 
             head_width=head_width, head_length=head_length, fc='green', ec='green', linewidth=2.5,
             label=f'GS: {ground_speed:.1f} kts @ {true_course:.0f}°')
    
    # Draw the triangle (dashed lines connecting the vectors)
    triangle = plt.Polygon([origin, tas_end, gs_end], fill=False, 
                           edgecolor='gray', linestyle=':', linewidth=1)
    ax.add_patch(triangle)
    
    # Calculate dynamic axis limits based on vector positions
    # Collect all vector endpoints
    all_points = np.array([origin, tas_end, wind_end, gs_end])
    x_points = all_points[:, 0]
    y_points = all_points[:, 1]
    
    # Calculate the actual spread of the vectors
    x_range = np.max(x_points) - np.min(x_points)
    y_range = np.max(y_points) - np.min(y_points)
    max_range = max(x_range, y_range)
    
    # Dynamic margin based on WCA size and vector spread
    # Smaller WCA = larger margin factor for better zoom
    if abs(wca) < 5:
        margin_factor = 1.8  # Close zoom for very small angles
    elif abs(wca) < 15:
        margin_factor = 1.5  # Medium zoom
    else:
        margin_factor = 1.3  # Normal zoom
    
    # Calculate center point of all vectors
    center_x = (np.max(x_points) + np.min(x_points)) / 2
    center_y = (np.max(y_points) + np.min(y_points)) / 2
    
    # Set limits with dynamic margin
    half_range = max_range * margin_factor / 2
    
    # Add WCA arc
    if abs(wca) > 0.5:
        # Dynamic arc radius based on zoom level
        arc_radius = min(15, max_range * 0.15)
        angle1 = 90 - true_course
        angle2 = 90 - true_heading
        
        # Ensure angle1 < angle2 for proper arc direction
        if angle1 > angle2:
            angle1, angle2 = angle2, angle1
        
        arc = mpatches.Arc(origin, 2*arc_radius, 2*arc_radius, 
                          angle=0, theta1=angle1, theta2=angle2, 
                          color='orange', linewidth=2)
        ax.add_patch(arc)
        
        # Add WCA label - positioned left or right based on correction direction
        mid_angle = np.radians((angle1 + angle2) / 2)
        label_pos = origin + np.array([arc_radius * 1.2 * np.cos(mid_angle),
                                       arc_radius * 1.2 * np.sin(mid_angle)])
        # Shift label 20 knots to the right or left based on WCA direction
        label_pos[0] += 20 if wca < 0 else +20
        # Align text based on WCA direction: right correction = left aligned (text appears right)
        text_align = 'left' if wca > 0 else 'right'
        ax.text(label_pos[0], label_pos[1], f'WCA\n{abs(wca):.1f}°', 
               fontsize=10, ha=text_align, va='center', 
               bbox=dict(boxstyle='round', facecolor='orange', alpha=0.3))
    
    # Add compass directions at dynamic positions
    compass_radius = half_range * 0.85  # Position compass inside the view
    directions = [('N', 0, 90), ('E', 90, 0), ('S', 180, -90), ('W', 270, 180)]
    for label, deg, plot_angle in directions:
        angle_rad = np.radians(plot_angle)
        pos = origin + np.array([compass_radius * np.cos(angle_rad),
                                 compass_radius * np.sin(angle_rad)])
        ax.text(pos[0], pos[1], label, fontsize=12, fontweight='bold',
               ha='center', va='center',
               bbox=dict(boxstyle='circle', facecolor='white', alpha=0.8, edgecolor='gray'))
    
    # Set limits centered on vectors with dynamic zoom
    ax.set_xlim(center_x - half_range, center_x + half_range)
    ax.set_ylim(center_y - half_range, center_y + half_range)
    ax.set_xlabel('East/West (in kn)', fontsize=12)
    ax.set_ylabel('North/South (in kn)', fontsize=12)
    ax.set_title('Wind Triangle Visualization', fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    
    # Add info text
    info_text = (
        f"Wind Correction Angle: {wca:+.1f}° ({'right' if wca > 0 else 'left'})\n"
        f"Fly Heading {true_heading:.0f}° to track {true_course:.0f}°"
    )
    ax.text(0.5, -0.15, info_text, transform=ax.transAxes, 
           fontsize=11, ha='center', va='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    return fig


# ============================================================================
# TOP OF DESCENT (TOD) CALCULATOR UI
# ============================================================================

def show_tod_calculator():
    """
    Display the Top of Descent (TOD) calculator interface.
    
    This calculator helps pilots determine when to start descending to reach
    a target altitude. It calculates:
    - Distance to TOD (Top of Descent point)
    - Required descent rate
    - Time needed for descent
    - Rule of thumb estimation
    
    The calculation uses the descent angle (typically 3° for ILS approaches)
    and applies basic trigonometry to determine the descent profile.
    """
    st.header("📉 Top of Descent (TOD) Calculator")
    st.write("Berechnen Sie, wann Sie mit dem Sinkflug beginnen müssen.")
    
    # Create two-column layout: left for inputs, right for results
    col1, col2 = st.columns([1, 1])
    
    # ========================================================================
    # LEFT COLUMN - USER INPUTS
    # ========================================================================
    
    with col1:
        st.subheader("Eingabe")
        
        # Input field: Current altitude
        # This is the altitude you are currently flying at
        current_alt = st.number_input(
            "Aktuelle Höhe (ft)",
            min_value=0,
            max_value=50000,
            value=DEFAULT_CRUISE_ALTITUDE,  # Default: 5000 ft
            step=100,
            help="Ihre aktuelle Flughöhe in Fuß"
        )
        
        # Input field: Target altitude
        # This is the altitude you want to reach (e.g., pattern altitude, final approach)
        target_alt = st.number_input(
            "Zielhöhe (ft)",
            min_value=0,
            max_value=50000,
            value=2000,  # Default: 2000 ft (typical pattern altitude)
            step=100,
            help="Die Höhe, die Sie erreichen möchten"
        )
        
        # Input slider: Descent angle
        # Standard ILS glideslope is 3°. Steeper angles (4-6°) for emergency descents
        descent_angle = st.slider(
            "Sinkwinkel (°)",
            min_value=1.0,
            max_value=6.0,
            value=STANDARD_DESCENT_ANGLE,  # 3° = ILS standard
            step=0.5,
            help="Standard: 3° (ILS Glideslope)"
        )
        
        # Input field: Ground speed (optional)
        # If provided, calculates descent rate (ft/min) and time to descend
        ground_speed = st.number_input(
            "Ground Speed (kts) [optional]",
            min_value=0,
            max_value=500,
            value=120,  # Default: 120 kts (typical GA aircraft)
            step=10,
            help="Für Sinkraten- und Zeitberechnung"
        )
        
        # Calculate button - triggers the calculation
        calculate_btn = st.button("🧮 Berechnen", type="primary", use_container_width=True)
    
    # ========================================================================
    # RIGHT COLUMN - CALCULATION RESULTS
    # ========================================================================
    
    with col2:
        st.subheader("Ergebnis")
        
        # Trigger calculation when button is clicked OR when user changes altitude
        # (auto-calculation for better UX)
        if calculate_btn or current_alt != DEFAULT_CRUISE_ALTITUDE:
            # Call calculation function from src/calculations.py
            # Returns dict with: altitude_loss, distance_to_tod, descent_rate, descent_time
            result = calculate_descent_rate(
                current_alt, 
                target_alt, 
                descent_angle, 
                ground_speed if ground_speed > 0 else None  # Pass None if GS = 0
            )
            
            # Validation: Check if target altitude is valid
            if result["altitude_loss"] <= 0:
                st.warning("⚠️ Zielhöhe liegt über oder auf aktueller Höhe!")
            else:
                # ============================================================
                # DISPLAY MAIN RESULTS
                # ============================================================
                
                # Create two sub-columns for result metrics
                col_a, col_b = st.columns(2)
                
                # Left sub-column: Altitude and distance metrics
                with col_a:
                    # Metric: Total altitude to lose
                    st.metric(
                        "Höhenverlust",
                        f"{result['altitude_loss']:,.0f} ft"  # Format with thousands separator
                    )
                    
                    # Metric: Distance to TOD point
                    # This is where you should start descending
                    st.metric(
                        "Distanz bis TOD",
                        f"{result['distance_to_tod']:.1f} NM"  # Nautical miles
                    )
                
                # Right sub-column: Time and rate metrics (only if ground speed provided)
                with col_b:
                    if result['descent_rate']:
                        # Metric: Required descent rate in feet per minute
                        # This is what you set on the autopilot or aim for manually
                        st.metric(
                            "Sinkrate",
                            f"{result['descent_rate']:.0f} ft/min"
                        )
                        
                        # Metric: Total time for the descent
                        st.metric(
                            "Sinkzeit",
                            f"{result['descent_time']:.1f} min"
                        )
                
                # ============================================================
                # RULE OF THUMB SECTION
                # ============================================================
                
                st.markdown("---")  # Visual separator  # Visual separator
                
                # Quick rule of thumb: altitude to lose ÷ 300 = distance in NM
                # This is a simple mental math trick for 3° descents
                rule_distance = calculate_rule_of_thumb_tod(result["altitude_loss"])
                st.info(
                    f"**📐 Faustregel (3° Descent):**\n\n"
                    f"Beginnen Sie den Sinkflug ca. **{rule_distance:.0f} NM** "
                    f"vor dem Ziel.\n\n"
                    f"*Berechnung: {result['altitude_loss']:.0f} ft ÷ 300 = {rule_distance:.0f} NM*"
                )
                
                # ============================================================
                # EXPANDABLE EXPLANATION SECTION
                # ============================================================
                
                # Collapsible section with detailed calculation steps
                with st.expander("ℹ️ Erklärung"):
                    # Show step-by-step calculation
                    st.write(f"""
                    **Berechnung:**
                    - Höhenverlust: {current_alt:,.0f} ft - {target_alt:,.0f} ft = {result['altitude_loss']:,.0f} ft
                    - Distanz: Höhenverlust / tan({descent_angle}°) = {result['distance_to_tod']:.2f} NM
                    """)
                    
                    # If ground speed was provided, show time/rate calculations
                    if result['descent_rate']:
                        st.write(f"""
                        - Zeit: {result['distance_to_tod']:.2f} NM / {ground_speed} kts = {result['descent_time']:.2f} min
                        - Sinkrate: {result['altitude_loss']:,.0f} ft / {result['descent_time']:.2f} min = {result['descent_rate']:.0f} ft/min
                        """)


# ============================================================================
# TOP OF CLIMB (TOC) CALCULATOR UI
# ============================================================================

def show_toc_calculator():
    """
    Display the Top of Climb (TOC) calculator interface.
    
    This calculator helps pilots determine when to level off during climb.
    Two calculation modes:
    1. Known climb rate: Calculate time and distance to reach target altitude
    2. Known time: Calculate required climb rate to reach altitude in given time
    
    Features:
    - Climb time calculation
    - Climb distance calculation  
    - Climb angle calculation
    - Aircraft performance warnings
    - Visual climb profile
    """
    # Header section with title and description
    st.header("📈 Top of Climb (TOC) Calculator")
    st.write("Berechnet den Punkt, an dem Sie die Zielflughöhe erreichen werden.")
    
    # Create two-column layout: Input (left) and Results (right)
    col1, col2 = st.columns([1, 1])
    
    # ========================================================================
    # LEFT COLUMN: INPUT FIELDS
    # ========================================================================
    with col1:
        st.subheader("🔧 Eingabe")
        
        # Altitude inputs - current and target altitude in feet
        st.write("**📍 Höhen**")
        current_alt = st.number_input(
            "Current Altitude (ft)",
            min_value=0,
            max_value=50000,
            value=2000,
            step=100,
            help="Ihre aktuelle Flughöhe in Fuß"
        )
        
        target_alt = st.number_input(
            "Target Altitude (ft)", 
            min_value=0,
            max_value=50000,
            value=10000,
            step=100,
            help="Gewünschte Zielflughöhe in Fuß"
        )
        
        st.markdown("---")
        
        # Calculation mode selection - user chooses between known rate or known time
        st.write("**⚙️ Berechnungsmodus**")
        calc_mode = st.radio(
            "Wählen Sie den Berechnungsmodus:",
            ["Steigrate bekannt", "Zeit bekannt"],
            help="Wählen Sie, ob Sie die Steigrate kennen oder die verfügbare Zeit"
        )
        
        st.markdown("---")
        
        # Mode-specific inputs
        if calc_mode == "Steigrate bekannt":
            # MODE 1: Known climb rate
            st.write("**📈 Steigrate**")
            climb_rate = st.number_input(
                "Climb Rate (ft/min)",
                min_value=100,
                max_value=5000,
                value=500,
                step=50,
                help="Typische Werte: GA 500-700, High-Performance 1000-1500, Jets 2000-3000"
            )
            
            # Display performance reference
            st.info(
                "**Typische Steigraten:**\n"
                "- Light GA: 500-700 ft/min\n"
                "- High-Performance: 1000-1500 ft/min\n"  
                "- Light Jets: 2000-3000 ft/min"
            )
        else:
            # MODE 2: Known time
            st.write("**⏱️ Verfügbare Zeit**")
            available_time = st.number_input(
                "Available Time (min)",
                min_value=1.0,
                max_value=60.0,
                value=10.0,
                step=0.5,
                help="Zeit, die für den Steigflug zur Verfügung steht"
            )
        
        st.markdown("---")
        
        # Ground speed input - used for distance calculation
        st.write("**✈️ Flugdaten**")
        ground_speed = st.number_input(
            "Ground Speed (kts)",
            min_value=50,
            max_value=500,
            value=120,
            step=5,
            help="Geschwindigkeit über Grund während des Steigflugs"
        )
        
        # Calculate button - triggers the calculation
        calculate = st.button("🧮 Berechnen", type="primary", use_container_width=True)
    
    # ========================================================================
    # RIGHT COLUMN: RESULTS DISPLAY
    # ========================================================================
    with col2:
        st.subheader("📊 Ergebnisse")
        
        # Only show results after button click
        if calculate:
            # Validate input: target must be higher than current altitude
            if target_alt <= current_alt:
                st.error("❌ Zielhöhe muss höher als aktuelle Höhe sein!")
                return
            
            # Perform calculation based on selected mode
            if calc_mode == "Steigrate bekannt":
                # MODE 1: Calculate by climb rate
                result = calculate_toc_by_rate(
                    current_alt, target_alt, climb_rate, ground_speed
                )
                
                # Display main metrics in two sub-columns
                col_a, col_b = st.columns(2)
                
                with col_a:
                    # Time to reach TOC
                    st.metric(
                        "⏱️ Zeit bis TOC",
                        f"{result['climb_time']:.1f} min",
                        help="Benötigte Zeit zum Erreichen der Zielhöhe"
                    )
                    
                    # Climb angle
                    st.metric(
                        "📐 Steigwinkel", 
                        f"{result['climb_angle']:.2f}°",
                        help="Durchschnittlicher Steigwinkel"
                    )
                
                with col_b:
                    # Distance to TOC
                    st.metric(
                        "📏 Distanz bis TOC",
                        f"{result['climb_distance']:.1f} NM",
                        help="Horizontale Distanz bis zum Erreichen der Zielhöhe"
                    )
                    
                    # Altitude gain
                    st.metric(
                        "📈 Höhengewinn",
                        f"{result['altitude_gain']:,.0f} ft",
                        help="Zu gewinnende Höhe"
                    )
                
                # Performance warning if climb rate is unrealistic
                if not result['is_realistic']:
                    st.warning(
                        "⚠️ **Achtung:** Diese Steigrate (> 3000 ft/min) ist unrealistisch "
                        "für die meisten zivilen Luftfahrzeuge!"
                    )
                
                # Rule of thumb calculation
                rule_distance = calculate_rule_of_thumb_toc(result['altitude_gain'], climb_rate)
                
                st.info(
                    f"💡 **Faustregel:** Bei {climb_rate} ft/min Steigrate dauert der Climb "
                    f"ca. {result['climb_time']:.0f} Minuten für {result['altitude_gain']:,.0f} ft. "
                    f"Distanz ≈ {rule_distance:.0f} NM"
                )
                
            else:
                # MODE 2: Calculate by available time
                result = calculate_toc_by_time(
                    current_alt, target_alt, available_time, ground_speed
                )
                
                # Display main metrics in two sub-columns  
                col_a, col_b = st.columns(2)
                
                with col_a:
                    # Required climb rate
                    st.metric(
                        "📈 Benötigte Steigrate",
                        f"{result['required_climb_rate']:.0f} ft/min",
                        help="Erforderliche Steigrate zum Erreichen der Zielhöhe in der gegebenen Zeit"
                    )
                    
                    # Climb angle
                    st.metric(
                        "📐 Steigwinkel",
                        f"{result['climb_angle']:.2f}°",
                        help="Durchschnittlicher Steigwinkel"
                    )
                
                with col_b:
                    # Distance to TOC
                    st.metric(
                        "📏 Distanz bis TOC",
                        f"{result['climb_distance']:.1f} NM",
                        help="Horizontale Distanz bis zum Erreichen der Zielhöhe"
                    )
                    
                    # Altitude gain
                    st.metric(
                        "📈 Höhengewinn",
                        f"{result['altitude_gain']:,.0f} ft",
                        help="Zu gewinnende Höhe"
                    )
                
                # Aircraft category suggestion
                if result['is_realistic']:
                    st.success(
                        f"✅ **Flugzeug-Kategorie:** {result['aircraft_category']}\n\n"
                        f"Diese Steigrate ist realistisch für die angegebene Flugzeugkategorie."
                    )
                else:
                    st.error(
                        f"❌ **Warnung:** Die benötigte Steigrate von "
                        f"{result['required_climb_rate']:.0f} ft/min ist unrealistisch!\n\n"
                        f"Vorgeschlagene Kategorie: {result['aircraft_category']}\n\n"
                        f"Erhöhen Sie die verfügbare Zeit oder reduzieren Sie die Zielhöhe."
                    )
            
            # ================================================================
            # DETAILED EXPLANATION (EXPANDABLE)
            # ================================================================
            with st.expander("ℹ️ Detaillierte Erklärung"):
                if calc_mode == "Steigrate bekannt":
                    st.write(f"""
                    **Berechnung (Steigrate bekannt):**
                    
                    - Höhengewinn: {target_alt:,.0f} ft - {current_alt:,.0f} ft = {result['altitude_gain']:,.0f} ft
                    - Zeit: {result['altitude_gain']:,.0f} ft ÷ {climb_rate} ft/min = {result['climb_time']:.2f} min
                    - Distanz: {ground_speed} kts × {result['climb_time']:.2f} min ÷ 60 = {result['climb_distance']:.2f} NM
                    - Steigwinkel: arctan({climb_rate} / ({ground_speed} × 101.269)) = {result['climb_angle']:.2f}°
                    
                    **Hinweise:**
                    - Steigraten sind abhängig vom Flugzeugtyp und Gewicht
                    - In großer Höhe nimmt die Steigrate ab (geringere Luftdichte)
                    - Wind beeinflusst die Ground Speed und damit die Distanz
                    """)
                else:
                    st.write(f"""
                    **Berechnung (Zeit bekannt):**
                    
                    - Höhengewinn: {target_alt:,.0f} ft - {current_alt:,.0f} ft = {result['altitude_gain']:,.0f} ft
                    - Benötigte Steigrate: {result['altitude_gain']:,.0f} ft ÷ {available_time} min = {result['required_climb_rate']:.0f} ft/min
                    - Distanz: {ground_speed} kts × {available_time} min ÷ 60 = {result['climb_distance']:.2f} NM
                    - Steigwinkel: arctan({result['required_climb_rate']:.0f} / ({ground_speed} × 101.269)) = {result['climb_angle']:.2f}°
                    
                    **Flugzeug-Kategorien nach Steigrate:**
                    - Light GA (Cessna, Piper): 500-700 ft/min
                    - High-Performance Single: 1000-1500 ft/min
                    - Light Twin/Turboprop: 1500-2000 ft/min
                    - Light Jet/Airliner: 2000-3000 ft/min
                    - Military: > 3000 ft/min
                    """)
            
            # ================================================================
            # CLIMB PROFILE VISUALIZATION
            # ================================================================
            st.markdown("---")
            st.subheader("🎨 Steigflug-Profil")
            
            # Create matplotlib figure for climb profile
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Get distance from appropriate result dict
            if calc_mode == "Steigrate bekannt":
                distance = result['climb_distance']
                angle = result['climb_angle']
            else:
                distance = result['climb_distance']
                angle = result['climb_angle']
            
            # Create climb profile line (from current to target altitude)
            x_profile = [0, distance]
            y_profile = [current_alt, target_alt]
            
            # Plot climb profile
            ax.plot(x_profile, y_profile, 'b-', linewidth=3, label='Steigflug-Profil')
            
            # Mark start and end points
            ax.plot(0, current_alt, 'go', markersize=12, label='Start', zorder=5)
            ax.plot(distance, target_alt, 'ro', markersize=12, label='TOC (Top of Climb)', zorder=5)
            
            # Add altitude labels
            ax.text(0, current_alt - 500, f'{current_alt:,.0f} ft', 
                   ha='center', va='top', fontsize=10, fontweight='bold')
            ax.text(distance, target_alt + 500, f'{target_alt:,.0f} ft',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            # Add distance label
            ax.text(distance/2, current_alt - 1000, f'{distance:.1f} NM',
                   ha='center', va='top', fontsize=11, bbox=dict(boxstyle='round', 
                   facecolor='wheat', alpha=0.8))
            
            # Add climb angle annotation
            # Draw angle arc
            from matplotlib.patches import Arc
            arc_radius = distance * 0.15
            arc = Arc((0, current_alt), arc_radius*2, arc_radius*2, 
                     angle=0, theta1=0, theta2=angle, color='red', linewidth=2)
            ax.add_patch(arc)
            
            # Angle label
            ax.text(arc_radius * 0.7, current_alt + arc_radius * 0.3, 
                   f'{angle:.1f}°', color='red', fontsize=10, fontweight='bold')
            
            # Add grid and labels
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_xlabel('Distanz (NM)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Höhe (ft)', fontsize=12, fontweight='bold')
            ax.set_title(f'Steigflug-Profil: {current_alt:,.0f} ft → {target_alt:,.0f} ft', 
                        fontsize=14, fontweight='bold')
            
            # Set axis limits with some padding
            ax.set_xlim(-distance*0.1, distance*1.2)
            ax.set_ylim(current_alt - result['altitude_gain']*0.2, 
                       target_alt + result['altitude_gain']*0.2)
            
            # Add legend
            ax.legend(loc='upper left', fontsize=10)
            
            # Make layout tight
            plt.tight_layout()
            
            # Display plot in Streamlit
            st.pyplot(fig)
            
            # Add info box below visualization
            if calc_mode == "Steigrate bekannt":
                st.info(
                    f"📊 **Profil-Informationen:** Bei einer Steigrate von {climb_rate} ft/min "
                    f"und {ground_speed} kts Ground Speed benötigen Sie {result['climb_time']:.1f} Minuten "
                    f"und {distance:.1f} NM horizontale Distanz, um {result['altitude_gain']:,.0f} ft zu steigen."
                )
            else:
                st.info(
                    f"📊 **Profil-Informationen:** Um in {available_time} Minuten "
                    f"{result['altitude_gain']:,.0f} ft zu steigen, benötigen Sie eine Steigrate von "
                    f"{result['required_climb_rate']:.0f} ft/min. Die horizontale Distanz beträgt {distance:.1f} NM."
                )


# ============================================================================
# WIND CORRECTION ANGLE CALCULATOR UI
# ============================================================================

def show_wind_correction_calculator():
    """
    Display the Wind Correction Angle (WCA) calculator interface.
    
    This calculator solves the wind triangle problem to determine:
    - Wind Correction Angle (WCA): How much to adjust heading for wind
    - True Heading: The actual heading to fly to maintain desired track
    - Ground Speed: Actual speed over ground considering wind
    - Wind Components: Headwind/tailwind and crosswind breakdown
    - Drift Angle: Angle between heading and actual track
    
    The calculation uses vector mathematics to solve the wind triangle:
    - TAS vector: Aircraft's speed through the air
    - Wind vector: Wind speed and direction
    - GS vector: Resultant ground speed and track
    
    Also displays a visual wind triangle diagram to help understanding.
    """
    st.header("🌬️ Wind Correction Angle Calculator")
    st.write("Berechnen Sie Wind Correction Angle (WCA) und Ground Speed.")
    
    # Create two-column layout: left for inputs, right for results
    col1, col2 = st.columns([1, 1])
    
    # ========================================================================
    # LEFT COLUMN - USER INPUTS
    # ========================================================================
    
    with col1:
        st.subheader("Eingabe")
        
        # Input field: True Airspeed (TAS)
        # This is the speed of the aircraft through the air mass
        # (not ground speed - that's what we calculate!)
        tas = st.number_input(
            "True Airspeed (TAS) [kts]",
            min_value=50,
            max_value=500,
            value=DEFAULT_TAS,  # Default: 120 kts
            step=10,
            help="Ihre True Airspeed in Knoten"
        )
        
        # Input field: Desired True Course
        # This is the track you want to follow over the ground
        # NOT the heading you fly - that's calculated based on wind
        true_course = st.number_input(
            "Desired True Course (°)",
            min_value=0,
            max_value=359,
            value=180,  # Default: South (180°)
            step=1,
            help="Der Kurs, den Sie fliegen möchten (0-359°)"
        )
        
        # Input field: Wind FROM direction
        # IMPORTANT: Wind is always reported as the direction it comes FROM
        # E.g., 270° = wind FROM the West (blowing TO the East)
        wind_from = st.number_input(
            "Wind FROM (°)",
            min_value=0,
            max_value=359,
            value=270,  # Default: From West
            step=10,
            help="Richtung, AUS DER der Wind kommt (z.B. 270° = Wind von Westen)"
        )
        
        # Input field: Wind speed
        # Speed of the wind in knots
        wind_speed = st.number_input(
            "Wind Speed (kts)",
            min_value=0,
            max_value=200,
            value=20,  # Default: 20 kts wind
            step=5,
            help="Windgeschwindigkeit in Knoten"
        )
        
        # Calculate button - triggers the calculation
        calculate_btn = st.button("🧮 Berechnen", type="primary", use_container_width=True)
    
    # ========================================================================
    # RIGHT COLUMN - CALCULATION RESULTS
    # ========================================================================
    
    with col2:
        st.subheader("Ergebnis")
        
        # Trigger calculation when button is clicked OR when TAS changes
        # (auto-calculation for better UX)
        if calculate_btn or tas != DEFAULT_TAS:
            # Call wind correction calculation from src/calculations.py
            # This solves the wind triangle using vector mathematics
            # Returns dict with: wca, true_heading, ground_speed, drift_angle, wind components
            result = calculate_wind_correction(
                tas,
                true_course,
                wind_from,
                wind_speed
            )
            
            # ============================================================
            # DISPLAY MAIN RESULTS (Primary Navigation Values)
            # ============================================================
            
            # Create two sub-columns for primary metrics
            col_a, col_b = st.columns(2)
            
            # Left sub-column: Wind Correction Angle and Heading
            with col_a:
                # Determine WCA direction (right = positive, left = negative)
                wca_direction = "rechts" if result['wind_correction_angle'] > 0 else "links"
                
                # Metric: Wind Correction Angle (WCA)
                # This is the angle to add to your desired course to get heading
                # Positive = correct to the right, Negative = correct to the left
                st.metric(
                    "Wind Correction Angle",
                    f"{abs(result['wind_correction_angle']):.1f}° {wca_direction}",
                    help="Winkel, um den Sie korrigieren müssen"
                )
                
                # Metric: True Heading to Fly
                # This is the actual heading you must fly to maintain your desired track
                # Heading = Course + WCA
                st.metric(
                    "True Heading to Fly",
                    f"{result['true_heading']:.0f}°",
                    help="Der Heading, den Sie fliegen müssen"
                )
            
            # Right sub-column: Ground Speed and Drift
            with col_b:
                # Metric: Ground Speed
                # This is your actual speed over the ground (faster or slower than TAS)
                # Headwind reduces GS, tailwind increases GS
                st.metric(
                    "Ground Speed",
                    f"{result['ground_speed']:.1f} kts",
                    help="Ihre Geschwindigkeit über Grund"
                )
                
                # Metric: Drift Angle
                # Angle between where aircraft points (heading) and where it goes (track)
                # If you don't correct for wind, this is how far you'll drift off course
                st.metric(
                    "Drift Angle",
                    f"{result['drift_angle']:.1f}°",
                    help="Abdrift durch den Wind"
                )
            
            # ============================================================
            # WIND COMPONENTS SECTION
            # ============================================================
            
            st.markdown("---")  # Visual separator
            st.subheader("Wind-Komponenten")
            
            # Create two sub-columns for wind component metrics
            col_c, col_d = st.columns(2)
            
            # Left component: Headwind/Tailwind
            with col_c:
                # Determine if headwind (positive) or tailwind (negative)
                hw_type = "Rückenwind" if result['headwind_component'] < 0 else "Gegenwind"
                
                # Metric: Headwind or Tailwind component
                # Headwind: Wind opposing your direction (slows you down)
                # Tailwind: Wind from behind (speeds you up)
                st.metric(
                    hw_type,
                    f"{abs(result['headwind_component']):.1f} kts"
                )
            
            # Right component: Crosswind
            with col_d:
                # Determine crosswind direction (right = positive, left = negative)
                cw_direction = "von rechts" if result['crosswind_component'] > 0 else "von links"
                
                # Metric: Crosswind component
                # This is the wind perpendicular to your desired track
                # This is what causes drift and requires WCA correction
                st.metric(
                    f"Seitenwind ({cw_direction})",
                    f"{abs(result['crosswind_component']):.1f} kts"
                )
            
            # ============================================================
            # EXPANDABLE EXPLANATION SECTION
            # ============================================================
            
            # Collapsible section with detailed calculation explanation
            with st.expander("ℹ️ Erklärung"):
                # Show comprehensive explanation of the wind triangle calculation
                st.write(f"""
                **Wind-Dreieck-Berechnung:**
                
                - Ihr TAS: {tas} kts auf Kurs {true_course}°
                - Wind: {wind_speed} kts aus {wind_from}°
                
                **Ergebnis:**
                - Sie müssen Heading {result['true_heading']:.0f}° fliegen
                - Korrektur: {abs(result['wind_correction_angle']):.1f}° nach {wca_direction}
                - Ihre Ground Speed: {result['ground_speed']:.1f} kts
                
                **Wind-Komponenten:**
                - {hw_type}: {abs(result['headwind_component']):.1f} kts
                - Seitenwind: {abs(result['crosswind_component']):.1f} kts {cw_direction}
                """)
            
            # ============================================================
            # WIND TRIANGLE VISUALIZATION
            # ============================================================
            
            st.markdown("---")  # Visual separator
            st.subheader("🎨 Wind-Dreieck Visualisierung")
            
            # Generate the wind triangle plot using matplotlib
            # This creates a visual representation showing:
            # - Blue arrow: TAS vector (where aircraft points)
            # - Red arrow: Wind vector (wind effect)
            # - Green arrow: GS vector (actual track over ground)
            # - Orange arc: Wind Correction Angle
            # - Compass rose: N/E/S/W directions
            fig = plot_wind_triangle(
                tas, 
                true_course, 
                wind_from, 
                wind_speed,
                result['wind_correction_angle'],
                result['true_heading'],
                result['ground_speed']
            )
            
            # Display the plot in Streamlit
            st.pyplot(fig)
            
            # Close the figure to free memory
            # IMPORTANT: Prevents memory leaks when recalculating multiple times
            plt.close(fig)


def show_course_converter():
    """True/Magnetic Course Converter"""
    st.header("🧭 Course Converter (True ↔ Magnetic)")
    st.write("Konvertieren Sie zwischen True und Magnetic Course.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Eingabe")
        
        course_value = st.number_input(
            "Kurs (°)",
            min_value=0,
            max_value=359,
            value=120,
            step=1,
            help="Der Kurs-Wert, den Sie konvertieren möchten"
        )
        
        conversion_direction = st.radio(
            "Konvertierung:",
            ["True → Magnetic", "Magnetic → True"],
            help="Wählen Sie die Konvertierungsrichtung"
        )
        
        st.markdown("---")
        
        st.write("**Magnetische Variation:**")
        st.caption("Finden Sie die Variation auf Ihrer Karte oder unter: https://www.magnetic-declination.com/")
        
        var_degrees = st.number_input(
            "Variation (°)",
            min_value=0.0,
            max_value=90.0,
            value=5.0,
            step=0.5,
            help="Betrag der magnetischen Variation"
        )
        
        var_direction = st.radio(
            "Richtung:",
            ["East (E)", "West (W)"],
            help="East oder West Variation"
        )
        
        # Calculate variation with sign
        variation = var_degrees if var_direction == "East (E)" else -var_degrees
        
        calculate_btn = st.button("🧮 Konvertieren", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("Ergebnis")
        
        if calculate_btn or course_value != 120:
            from_true = (conversion_direction == "True → Magnetic")
            result = convert_course(course_value, variation, from_true)
            
            # Display result
            if from_true:
                st.success(f"### True Course: {course_value}°")
                st.success(f"### ↓")
                st.success(f"### Magnetic Course: {result:.0f}°")
            else:
                st.success(f"### Magnetic Course: {course_value}°")
                st.success(f"### ↓")
                st.success(f"### True Course: {result:.0f}°")
            
            # TVMDC explanation
            st.markdown("---")
            st.info(
                "**📚 TVMDC-Regel:**\n\n"
                "**T**rue Course\n\n"
                "**V**ariation (±)\n\n"
                "**M**agnetic Course\n\n"
                "**D**eviation (±)\n\n"
                "**C**ompass Course\n\n\n"
                "*Merkhilfe: \"East is Least, West is Best\"*\n\n"
                "- True → Magnetic: **Subtract** East, **Add** West\n"
                "- Magnetic → True: **Add** East, **Subtract** West"
            )
            
            # Calculation explanation
            with st.expander("ℹ️ Berechnung"):
                var_sign = "+" if variation >= 0 else ""
                if from_true:
                    st.write(f"""
                    **True → Magnetic:**
                    
                    True Course: {course_value}°
                    
                    Variation: {var_sign}{variation}° ({var_direction})
                    
                    Berechnung: {course_value}° - ({var_sign}{variation}°) = {result:.0f}°
                    
                    Magnetic Course: **{result:.0f}°**
                    """)
                else:
                    st.write(f"""
                    **Magnetic → True:**
                    
                    Magnetic Course: {course_value}°
                    
                    Variation: {var_sign}{variation}° ({var_direction})
                    
                    Berechnung: {course_value}° + ({var_sign}{variation}°) = {result:.0f}°
                    
                    True Course: **{result:.0f}°**
                    """)


def show_ground_speed_calculator():
    """Ground Speed Calculator"""
    st.header("📊 Ground Speed Calculator")
    st.write("Schnelle Berechnung der Ground Speed bei bekanntem Heading.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Eingabe")
        
        tas = st.number_input(
            "True Airspeed (TAS) [kts]",
            min_value=50,
            max_value=500,
            value=DEFAULT_TAS,
            step=10,
            help="Ihre True Airspeed"
        )
        
        true_heading = st.number_input(
            "True Heading (°)",
            min_value=0,
            max_value=359,
            value=180,
            step=1,
            help="Der Heading, den Sie fliegen"
        )
        
        wind_from = st.number_input(
            "Wind FROM (°)",
            min_value=0,
            max_value=359,
            value=270,
            step=10,
            help="Richtung, AUS DER der Wind kommt"
        )
        
        wind_speed = st.number_input(
            "Wind Speed (kts)",
            min_value=0,
            max_value=200,
            value=20,
            step=5,
            help="Windgeschwindigkeit in Knoten"
        )
        
        st.markdown("---")
        
        distance = st.number_input(
            "Distanz (NM) [optional]",
            min_value=0.0,
            max_value=5000.0,
            value=100.0,
            step=10.0,
            help="Für Zeitberechnung"
        )
        
        calculate_btn = st.button("🧮 Berechnen", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("Ergebnis")
        
        if calculate_btn or tas != DEFAULT_TAS:
            result = calculate_ground_speed(
                tas,
                wind_from,
                wind_speed,
                true_heading
            )
            
            # Main result
            st.success(f"### Ground Speed: {result['ground_speed']:.1f} kts")
            
            st.metric(
                "Actual Track",
                f"{result['track']:.0f}°",
                help="Ihr tatsächlicher Track über Grund"
            )
            
            # Wind components
            st.markdown("---")
            st.subheader("Wind-Komponenten")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                hw_type = "Rückenwind" if result['headwind_component'] < 0 else "Gegenwind"
                st.metric(
                    hw_type,
                    f"{abs(result['headwind_component']):.1f} kts"
                )
            
            with col_b:
                cw_direction = "von rechts" if result['crosswind_component'] > 0 else "von links"
                st.metric(
                    f"Seitenwind",
                    f"{abs(result['crosswind_component']):.1f} kts"
                )
            
            # Time calculation
            if distance > 0:
                time_result = calculate_time_and_fuel(
                    distance,
                    result['ground_speed']
                )
                
                st.markdown("---")
                st.subheader("Flugzeit")
                
                hours = int(time_result['time_hours'])
                minutes = int(time_result['time_minutes'] % 60)
                
                col_c, col_d = st.columns(2)
                
                with col_c:
                    st.metric(
                        "Distanz",
                        f"{distance:.1f} NM"
                    )
                
                with col_d:
                    st.metric(
                        "Flugzeit",
                        f"{hours}h {minutes}min"
                    )
            
            # Explanation
            with st.expander("ℹ️ Erklärung"):
                st.write(f"""
                **Berechnung:**
                
                - TAS: {tas} kts auf Heading {true_heading}°
                - Wind: {wind_speed} kts aus {wind_from}°
                
                **Ergebnis:**
                - Ground Speed: {result['ground_speed']:.1f} kts
                - Actual Track: {result['track']:.0f}°
                - {hw_type}: {abs(result['headwind_component']):.1f} kts
                - Seitenwind: {abs(result['crosswind_component']):.1f} kts {cw_direction}
                """)


# ============================================================================
# UNIT CONVERTER CALCULATOR
# ============================================================================

def show_unit_converter():
    """
    Display the unit converter interface.
    
    Provides conversions for:
    - Altitude/Length: feet, meters, kilometers
    - Distance: nautical miles, kilometers, statute miles
    - Weight/Mass: kilograms, pounds, metric tons
    - Fuel Volume: liters, US gallons, Imperial gallons
    """
    st.header("🔄 Unit Converter")
    
    st.write("""
    Konvertieren Sie zwischen verschiedenen Einheiten, die in der Luftfahrt häufig verwendet werden.
    Wählen Sie die Kategorie und geben Sie den Wert ein.
    """)
    
    # ========================================================================
    # SELECT CONVERSION CATEGORY
    # ========================================================================
    
    st.subheader("Wählen Sie eine Kategorie")
    
    category = st.radio(
        "Kategorie:",
        [
            "📏 Höhe / Länge",
            "📍 Distanz",
            "⚖️ Gewicht / Masse",
            "⛽ Treibstoff-Volumen"
        ],
        horizontal=True
    )
    
    st.markdown("---")
    
    # ========================================================================
    # ALTITUDE/LENGTH CONVERTER
    # ========================================================================
    
    if category == "📏 Höhe / Länge":
        st.subheader("Höhe / Länge Konverter")
        
        col1, col2 = st.columns(2)
        
        with col1:
            value = st.number_input(
                "Wert eingeben:",
                min_value=0.0,
                value=10000.0,
                step=100.0,
                format="%.2f"
            )
            
            from_unit = st.selectbox(
                "Von:",
                ["Feet", "Meters", "Kilometers"]
            )
        
        with col2:
            to_unit = st.selectbox(
                "Nach:",
                ["Feet", "Meters", "Kilometers"]
            )
        
        if st.button("🔄 Konvertieren", key="altitude_convert"):
            try:
                result = convert_altitude(value, from_unit.lower(), to_unit.lower())
                
                st.success(f"**{value:,.2f} {from_unit} = {result:,.2f} {to_unit}**")
                
                # Show common aviation references
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.write("**Referenzwerte:**")
                
                if from_unit.lower() == "feet":
                    st.write(f"""
                    - In Metern: {convert_altitude(value, 'feet', 'meters'):,.2f} m
                    - In Kilometern: {convert_altitude(value, 'feet', 'kilometers'):,.2f} km
                    """)
                elif from_unit.lower() == "meters":
                    st.write(f"""
                    - In Fuß: {convert_altitude(value, 'meters', 'feet'):,.2f} ft
                    - In Kilometern: {convert_altitude(value, 'meters', 'kilometers'):,.2f} km
                    """)
                else:  # kilometers
                    st.write(f"""
                    - In Fuß: {convert_altitude(value, 'kilometers', 'feet'):,.2f} ft
                    - In Metern: {convert_altitude(value, 'kilometers', 'meters'):,.2f} m
                    """)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            except ValueError as e:
                st.error(f"Fehler: {e}")
        
        with st.expander("ℹ️ Umrechnungsfaktoren"):
            st.write("""
            **Häufige Umrechnungen:**
            - 1 Fuß (ft) = 0.3048 Meter
            - 1 Meter = 3.28084 Fuß
            - 1 Kilometer = 3280.84 Fuß
            
            **Typische Flughöhen:**
            - 10,000 ft = 3,048 m (typische Reiseflughöhe GA)
            - 35,000 ft = 10,668 m (typische Reiseflughöhe Airliner)
            - FL100 = 10,000 ft
            """)
    
    # ========================================================================
    # DISTANCE CONVERTER
    # ========================================================================
    
    elif category == "📍 Distanz":
        st.subheader("Distanz Konverter")
        
        col1, col2 = st.columns(2)
        
        with col1:
            value = st.number_input(
                "Wert eingeben:",
                min_value=0.0,
                value=100.0,
                step=1.0,
                format="%.2f"
            )
            
            from_unit = st.selectbox(
                "Von:",
                ["NM", "KM", "Miles"]
            )
        
        with col2:
            to_unit = st.selectbox(
                "Nach:",
                ["NM", "KM", "Miles"]
            )
        
        if st.button("🔄 Konvertieren", key="distance_convert"):
            try:
                result = convert_distance(value, from_unit.lower(), to_unit.lower())
                
                st.success(f"**{value:,.2f} {from_unit} = {result:,.2f} {to_unit}**")
                
                # Show all conversions
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.write("**Alle Umrechnungen:**")
                
                if from_unit.lower() == "nm":
                    st.write(f"""
                    - In Kilometern: {convert_distance(value, 'nm', 'km'):,.2f} km
                    - In Meilen: {convert_distance(value, 'nm', 'miles'):,.2f} miles
                    """)
                elif from_unit.lower() == "km":
                    st.write(f"""
                    - In Nautischen Meilen: {convert_distance(value, 'km', 'nm'):,.2f} NM
                    - In Meilen: {convert_distance(value, 'km', 'miles'):,.2f} miles
                    """)
                else:  # miles
                    st.write(f"""
                    - In Nautischen Meilen: {convert_distance(value, 'miles', 'nm'):,.2f} NM
                    - In Kilometern: {convert_distance(value, 'miles', 'km'):,.2f} km
                    """)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            except ValueError as e:
                st.error(f"Fehler: {e}")
        
        with st.expander("ℹ️ Umrechnungsfaktoren"):
            st.write("""
            **Häufige Umrechnungen:**
            - 1 Nautische Meile (NM) = 1.852 Kilometer
            - 1 Nautische Meile = 1.15078 Statute Miles
            - 1 Kilometer = 0.539957 NM
            
            **Typische Distanzen:**
            - 100 NM = 185.2 km (typische regionale Strecke)
            - 1 NM ≈ 6076 Fuß
            - 1 Grad Breitengrad = 60 NM
            """)
    
    # ========================================================================
    # WEIGHT/MASS CONVERTER
    # ========================================================================
    
    elif category == "⚖️ Gewicht / Masse":
        st.subheader("Gewicht / Masse Konverter")
        
        col1, col2 = st.columns(2)
        
        with col1:
            value = st.number_input(
                "Wert eingeben:",
                min_value=0.0,
                value=1000.0,
                step=10.0,
                format="%.2f"
            )
            
            from_unit = st.selectbox(
                "Von:",
                ["KG", "LBS", "Tons"]
            )
        
        with col2:
            to_unit = st.selectbox(
                "Nach:",
                ["KG", "LBS", "Tons"]
            )
        
        if st.button("🔄 Konvertieren", key="weight_convert"):
            try:
                result = convert_weight(value, from_unit.lower(), to_unit.lower())
                
                st.success(f"**{value:,.2f} {from_unit} = {result:,.2f} {to_unit}**")
                
                # Show all conversions
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.write("**Alle Umrechnungen:**")
                
                if from_unit.lower() == "kg":
                    st.write(f"""
                    - In Pounds: {convert_weight(value, 'kg', 'lbs'):,.2f} lbs
                    - In Tonnen: {convert_weight(value, 'kg', 'tons'):,.4f} tons
                    """)
                elif from_unit.lower() == "lbs":
                    st.write(f"""
                    - In Kilogramm: {convert_weight(value, 'lbs', 'kg'):,.2f} kg
                    - In Tonnen: {convert_weight(value, 'lbs', 'tons'):,.4f} tons
                    """)
                else:  # tons
                    st.write(f"""
                    - In Kilogramm: {convert_weight(value, 'tons', 'kg'):,.2f} kg
                    - In Pounds: {convert_weight(value, 'tons', 'lbs'):,.2f} lbs
                    """)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            except ValueError as e:
                st.error(f"Fehler: {e}")
        
        with st.expander("ℹ️ Umrechnungsfaktoren"):
            st.write("""
            **Häufige Umrechnungen:**
            - 1 Kilogramm (kg) = 2.20462 Pounds (lbs)
            - 1 Pound = 0.453592 kg
            - 1 Metrische Tonne = 1000 kg = 2204.62 lbs
            
            **Typische Gewichte:**
            - Cessna 172 Max. Takeoff Weight: ~2,450 lbs (1,111 kg)
            - Boeing 737-800 Max. Takeoff Weight: ~79,000 kg (174,000 lbs)
            - Pilotgewicht: ~70-100 kg (154-220 lbs)
            """)
    
    # ========================================================================
    # FUEL VOLUME CONVERTER
    # ========================================================================
    
    elif category == "⛽ Treibstoff-Volumen":
        st.subheader("Treibstoff-Volumen Konverter")
        
        col1, col2 = st.columns(2)
        
        with col1:
            value = st.number_input(
                "Wert eingeben:",
                min_value=0.0,
                value=100.0,
                step=1.0,
                format="%.2f"
            )
            
            from_unit = st.selectbox(
                "Von:",
                ["Liters", "US_Gal", "Imp_Gal"]
            )
        
        with col2:
            to_unit = st.selectbox(
                "Nach:",
                ["Liters", "US_Gal", "Imp_Gal"]
            )
        
        if st.button("🔄 Konvertieren", key="fuel_convert"):
            try:
                result = convert_fuel_volume(value, from_unit.lower(), to_unit.lower())
                
                st.success(f"**{value:,.2f} {from_unit} = {result:,.2f} {to_unit}**")
                
                # Show all conversions
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.write("**Alle Umrechnungen:**")
                
                if from_unit.lower() == "liters":
                    st.write(f"""
                    - In US Gallons: {convert_fuel_volume(value, 'liters', 'us_gal'):,.2f} US gal
                    - In Imperial Gallons: {convert_fuel_volume(value, 'liters', 'imp_gal'):,.2f} Imp gal
                    """)
                elif from_unit.lower() == "us_gal":
                    st.write(f"""
                    - In Liters: {convert_fuel_volume(value, 'us_gal', 'liters'):,.2f} L
                    - In Imperial Gallons: {convert_fuel_volume(value, 'us_gal', 'imp_gal'):,.2f} Imp gal
                    """)
                else:  # imp_gal
                    st.write(f"""
                    - In Liters: {convert_fuel_volume(value, 'imp_gal', 'liters'):,.2f} L
                    - In US Gallons: {convert_fuel_volume(value, 'imp_gal', 'us_gal'):,.2f} US gal
                    """)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            except ValueError as e:
                st.error(f"Fehler: {e}")
        
        with st.expander("ℹ️ Umrechnungsfaktoren"):
            st.write("""
            **Häufige Umrechnungen:**
            - 1 Liter = 0.264172 US Gallons
            - 1 Liter = 0.219969 Imperial Gallons
            - 1 US Gallon = 3.78541 Liters
            - 1 Imperial Gallon = 4.54609 Liters
            - 1 Imperial Gallon = 1.20095 US Gallons
            
            **Typische Tankkapazitäten:**
            - Cessna 172: ~56 US gal (~212 L)
            - Boeing 737-800: ~26,000 L (~6,875 US gal)
            - Durchschnittlicher Verbrauch GA: 8-12 US gal/h (~30-45 L/h)
            """)


# ============================================================================
# E6B FLIGHT COMPUTER CALCULATORS
# ============================================================================

def show_tas_calculator():
    """
    Display the True Airspeed (TAS) Calculator interface.
    
    Calculates TAS from Indicated Airspeed using the 2% rule or 
    more accurate temperature-based calculation.
    """
    st.header("✈️ True Airspeed (TAS) Calculator")
    
    st.write("""
    Berechnet die **True Airspeed (TAS)** aus der angezeigten Geschwindigkeit (IAS).
    TAS ist die tatsächliche Geschwindigkeit durch die Luftmasse und wird für alle 
    Navigationsberechnungen benötigt.
    """)
    
    # ========================================================================
    # INPUT SECTION
    # ========================================================================
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📥 Eingabe")
        
        ias = st.number_input(
            "Indicated Airspeed (IAS):",
            min_value=0,
            max_value=500,
            value=120,
            step=5,
            help="Angezeigte Geschwindigkeit im Cockpit (in Knoten)"
        )
        
        pressure_alt = st.number_input(
            "Pressure Altitude:",
            min_value=0,
            max_value=50000,
            value=5000,
            step=500,
            help="Druckhöhe in Fuß (Altimeter auf 29.92 inHg gestellt)"
        )
        
        use_temp = st.checkbox(
            "Temperatur für genauere Berechnung verwenden",
            value=False,
            help="Aktivieren für präzisere TAS-Berechnung"
        )
        
        temp_c = None
        if use_temp:
            temp_c = st.number_input(
                "Outside Air Temperature (OAT):",
                min_value=-60,
                max_value=60,
                value=15,
                step=1,
                help="Außentemperatur in Celsius"
            )
        
        calculate_btn = st.button("🧮 Berechnen", key="tas_calc", type="primary")
    
    # ========================================================================
    # RESULTS SECTION
    # ========================================================================
    
    with col2:
        st.subheader("📊 Ergebnis")
        
        if calculate_btn:
            result = calculate_true_airspeed(ias, pressure_alt, temp_c)
            
            # Main result
            st.success(f"**TAS: {result['tas']:.1f} kts**")
            
            # Details
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("IAS", f"{ias} kts")
                st.metric("Korrektur", f"+{result['correction_percent']:.1f}%")
            
            with col_b:
                st.metric("TAS", f"{result['tas']:.1f} kts")
                if result['isa_deviation'] is not None:
                    deviation_sign = "+" if result['isa_deviation'] > 0 else ""
                    st.metric("ISA Deviation", f"{deviation_sign}{result['isa_deviation']:.1f}°C")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.expander("ℹ️ Erklärung"):
                st.write(f"""
                **Berechnung:**
                
                - IAS: {ias} kts
                - Pressure Altitude: {pressure_alt:,.0f} ft
                {f"- OAT: {temp_c}°C" if temp_c is not None else ""}
                
                **Faustregel:** TAS erhöht sich um ca. 2% pro 1000 Fuß Höhe.
                
                **Ergebnis:**
                - TAS: {result['tas']:.1f} kts
                - Korrektur: {result['correction_percent']:.1f}%
                {f"- ISA Abweichung: {result['isa_deviation']:+.1f}°C" if result['isa_deviation'] is not None else ""}
                
                **Verwendung:** TAS wird für Navigation, Wind-Berechnungen und 
                Flugplanung verwendet.
                """)


def show_density_altitude_calculator():
    """
    Display the Density Altitude Calculator interface.
    
    Calculates density altitude which is critical for aircraft performance.
    """
    st.header("🌡️ Density Altitude Calculator")
    
    st.write("""
    Berechnet die **Density Altitude** - ein kritischer Wert für Aircraft Performance.
    Hohe Density Altitude bedeutet dünnere Luft und schlechtere Performance 
    (längere Startstr Ecke, geringere Steigleistung, längere Landestrecke).
    """)
    
    # ========================================================================
    # INPUT SECTION
    # ========================================================================
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📥 Eingabe")
        
        field_elev = st.number_input(
            "Field Elevation / Pressure Altitude:",
            min_value=0,
            max_value=15000,
            value=1000,
            step=100,
            help="Flugplatzhöhe in Fuß"
        )
        
        temp_c = st.number_input(
            "Outside Air Temperature (OAT):",
            min_value=-40,
            max_value=50,
            value=25,
            step=1,
            help="Außentemperatur in Celsius"
        )
        
        qnh = st.number_input(
            "Altimeter Setting (QNH):",
            min_value=28.00,
            max_value=31.50,
            value=29.92,
            step=0.01,
            format="%.2f",
            help="Barometrischer Druck in inches Hg (29.92 = Standard)"
        )
        
        calculate_btn = st.button("🧮 Berechnen", key="da_calc", type="primary")
    
    # ========================================================================
    # RESULTS SECTION
    # ========================================================================
    
    with col2:
        st.subheader("📊 Ergebnis")
        
        if calculate_btn:
            result = calculate_density_altitude(field_elev, temp_c, qnh)
            
            # Color-code based on severity
            da_diff = result['density_altitude'] - result['pressure_altitude']
            if da_diff < 1000:
                color = "green"
            elif da_diff < 2500:
                color = "orange"
            else:
                color = "red"
            
            # Main result
            st.markdown(f"<h3 style='color:{color}'>Density Altitude: {result['density_altitude']:,.0f} ft</h3>", 
                       unsafe_allow_html=True)
            
            # Details
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Pressure Altitude", f"{result['pressure_altitude']:,.0f} ft")
                st.metric("Temperature", f"{temp_c}°C")
            
            with col_b:
                st.metric("Density Altitude", f"{result['density_altitude']:,.0f} ft")
                deviation_sign = "+" if result['isa_deviation'] > 0 else ""
                st.metric("ISA Deviation", f"{deviation_sign}{result['isa_deviation']:.1f}°C")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Performance Impact
            if da_diff >= 1000:
                st.warning(f"⚠️ **{result['performance_impact']}**")
            else:
                st.info(f"✓ {result['performance_impact']}")
            
            with st.expander("ℹ️ Erklärung"):
                st.write(f"""
                **Berechnung:**
                
                - Field Elevation: {field_elev:,.0f} ft
                - Temperature: {temp_c}°C
                - QNH: {qnh:.2f} inHg
                
                **Ergebnisse:**
                - Pressure Altitude: {result['pressure_altitude']:,.0f} ft
                - Density Altitude: {result['density_altitude']:,.0f} ft
                - Difference: {da_diff:+,.0f} ft
                - ISA Deviation: {result['isa_deviation']:+.1f}°C
                
                **Performance Impact:**
                {result['performance_impact']}
                
                **Wichtig:** Hohe Density Altitude erfordert:
                - Längere Startstrecke
                - Geringere Steigleistung
                - Längere Landestrecke
                - Höheren Fuel Flow
                """)


def show_fuel_planner():
    """
    Display the Fuel Planner interface.
    
    Calculates fuel requirements, endurance, and range.
    """
    st.header("⛽ Fuel Planner")
    
    st.write("""
    Berechnet **Treibstoffbedarf**, **Reichweite** und **Endurance** für Ihre Flugplanung.
    Inkludiert Reserve-Berechnungen nach VFR/IFR-Anforderungen.
    """)
    
    # ========================================================================
    # MODE SELECTION
    # ========================================================================
    
    mode = st.radio(
        "Berechnungsmodus:",
        ["📍 Fuel Required (Distance-based)", "⏱️ Endurance & Range (Fuel-based)"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # ========================================================================
    # FUEL REQUIRED MODE
    # ========================================================================
    
    if mode == "📍 Fuel Required (Distance-based)":
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📥 Eingabe")
            
            distance = st.number_input(
                "Distance:",
                min_value=0.0,
                max_value=3000.0,
                value=150.0,
                step=10.0,
                help="Flugdistanz in Nautischen Meilen"
            )
            
            ground_speed = st.number_input(
                "Ground Speed:",
                min_value=30,
                max_value=600,
                value=120,
                step=5,
                help="Ground Speed in Knoten"
            )
            
            fuel_flow = st.number_input(
                "Fuel Flow:",
                min_value=1.0,
                max_value=500.0,
                value=10.0,
                step=0.5,
                help="Treibstoffverbrauch in Gallons/Stunde"
            )
            
            reserve_time = st.selectbox(
                "Reserve:",
                [30, 45, 60],
                index=1,
                help="Reserve-Zeit in Minuten (45 = IFR Standard)"
            )
            
            calculate_btn = st.button("🧮 Berechnen", key="fuel_req_calc", type="primary")
        
        with col2:
            st.subheader("📊 Ergebnis")
            
            if calculate_btn:
                try:
                    result = calculate_fuel_required(
                        distance=distance,
                        fuel_flow=fuel_flow,
                        ground_speed=ground_speed,
                        reserve_time=reserve_time
                    )
                    
                    # Main result
                    st.success(f"**Total Fuel Required: {result['total_fuel']:.1f} gallons**")
                    
                    # Details
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Flight Fuel", f"{result['fuel_required']:.1f} gal")
                        st.metric("Reserve Fuel", f"{result['fuel_reserve']:.1f} gal")
                    
                    with col_b:
                        st.metric("Total Fuel", f"{result['total_fuel']:.1f} gal")
                        st.metric("Flight Time", f"{result['flight_time']*60:.0f} min")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    with st.expander("ℹ️ Details"):
                        st.write(f"""
                        **Berechnung:**
                        
                        - Distanz: {distance} NM
                        - Ground Speed: {ground_speed} kts
                        - Fuel Flow: {fuel_flow} gal/h
                        - Reserve: {reserve_time} min
                        
                        **Ergebnisse:**
                        - Flugzeit: {result['flight_time']:.2f} h ({result['flight_time']*60:.0f} min)
                        - Fuel für Flug: {result['fuel_required']:.1f} gal
                        - Reserve: {result['fuel_reserve']:.1f} gal
                        - **Total: {result['total_fuel']:.1f} gal**
                        - Endurance (mit diesem Fuel): {result['endurance']:.2f} h
                        """)
                
                except ValueError as e:
                    st.error(f"Fehler: {e}")
    
    # ========================================================================
    # ENDURANCE & RANGE MODE
    # ========================================================================
    
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📥 Eingabe")
            
            fuel_available = st.number_input(
                "Available Fuel:",
                min_value=0.0,
                max_value=500.0,
                value=50.0,
                step=1.0,
                help="Verfügbarer Treibstoff in Gallons"
            )
            
            fuel_flow = st.number_input(
                "Fuel Flow:",
                min_value=1.0,
                max_value=500.0,
                value=10.0,
                step=0.5,
                help="Treibstoffverbrauch in Gallons/Stunde",
                key="ff_endurance"
            )
            
            ground_speed = st.number_input(
                "Ground Speed:",
                min_value=30,
                max_value=600,
                value=120,
                step=5,
                help="Ground Speed in Knoten",
                key="gs_endurance"
            )
            
            calculate_btn = st.button("🧮 Berechnen", key="endurance_calc", type="primary")
        
        with col2:
            st.subheader("📊 Ergebnis")
            
            if calculate_btn:
                try:
                    result = calculate_endurance_and_range(fuel_available, fuel_flow, ground_speed)
                    
                    # Main results
                    st.success(f"**Endurance: {result['endurance']:.2f} h ({result['endurance']*60:.0f} min)**")
                    st.success(f"**Range: {result['range']:.0f} NM**")
                    
                    # Details with reserve
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    
                    st.write("**Mit 45-min IFR Reserve:**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Endurance", f"{result['endurance_with_reserve']:.2f} h")
                        st.metric("Reserve Fuel", f"{result['reserve_fuel']:.1f} gal")
                    
                    with col_b:
                        st.metric("Range", f"{result['range_with_reserve']:.0f} NM")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    with st.expander("ℹ️ Details"):
                        st.write(f"""
                        **Berechnung:**
                        
                        - Verfügbarer Fuel: {fuel_available} gal
                        - Fuel Flow: {fuel_flow} gal/h
                        - Ground Speed: {ground_speed} kts
                        
                        **Maximum (ohne Reserve):**
                        - Endurance: {result['endurance']:.2f} h ({result['endurance']*60:.0f} min)
                        - Range: {result['range']:.0f} NM
                        
                        **Mit 45-min Reserve:**
                        - Reserve Fuel: {result['reserve_fuel']:.1f} gal
                        - Usable Fuel: {fuel_available - result['reserve_fuel']:.1f} gal
                        - Endurance: {result['endurance_with_reserve']:.2f} h
                        - Range: {result['range_with_reserve']:.0f} NM
                        """)
                
                except ValueError as e:
                    st.error(f"Fehler: {e}")


def show_wind_components_calculator():
    """
    Display the Wind Components Calculator interface.
    
    Calculates headwind/tailwind and crosswind components for runway operations.
    """
    st.header("🛬 Wind Components Calculator")
    
    st.write("""
    Berechnet **Headwind/Tailwind** und **Crosswind** Komponenten für eine Runway.
    Wichtig für Runway Selection und Performance-Berechnungen.
    """)
    
    # ========================================================================
    # INPUT SECTION
    # ========================================================================
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📥 Eingabe")
        
        runway = st.number_input(
            "Runway:",
            min_value=1,
            max_value=36,
            value=27,
            step=1,
            help="Runway-Nummer (z.B. 27 für Runway 27)"
        )
        
        runway_heading = runway * 10
        
        wind_dir = st.number_input(
            "Wind Direction:",
            min_value=0,
            max_value=360,
            value=240,
            step=10,
            help="Wind FROM Richtung in Grad (0-360°)"
        )
        
        wind_speed = st.number_input(
            "Wind Speed:",
            min_value=0,
            max_value=150,
            value=15,
            step=1,
            help="Windgeschwindigkeit in Knoten"
        )
        
        calculate_btn = st.button("🧮 Berechnen", key="wind_comp_calc", type="primary")
    
    # ========================================================================
    # RESULTS SECTION
    # ========================================================================
    
    with col2:
        st.subheader("📊 Ergebnis")
        
        if calculate_btn:
            result = calculate_wind_components(runway_heading, wind_dir, wind_speed)
            
            # Determine wind type
            if result['headwind_component'] > 0:
                wind_type = "Headwind"
                wind_color = "green"
            else:
                wind_type = "Tailwind"
                wind_color = "orange"
            
            # Crosswind warning
            crosswind_warning = result['crosswind_component'] > 15
            
            # Main results
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.metric(
                    wind_type,
                    f"{abs(result['headwind_component']):.0f} kts",
                    delta=None
                )
                
                st.metric(
                    "Angle Difference",
                    f"{result['angle_difference']:.0f}°"
                )
            
            with col_b:
                crosswind_text = f"{result['crosswind_component']:.0f} kts ({result['crosswind_direction']})"
                st.metric(
                    "Crosswind",
                    crosswind_text,
                    delta=None
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Warnings
            if result['headwind_component'] < 0:
                st.warning(f"⚠️ **Tailwind:** {abs(result['headwind_component']):.0f} kts - Längere Landestrecke!")
            
            if crosswind_warning:
                st.warning(f"⚠️ **Hoher Crosswind:** {result['crosswind_component']:.0f} kts - Prüfen Sie Flugzeug-Limits!")
            elif result['crosswind_component'] > 0:
                st.info(f"✓ Crosswind im akzeptablen Bereich")
            
            with st.expander("ℹ️ Erklärung"):
                st.write(f"""
                **Eingaben:**
                
                - Runway: {runway:02d} (Heading: {runway_heading}°)
                - Wind: {wind_speed} kts aus {wind_dir}°
                
                **Ergebnisse:**
                
                - **{wind_type}:** {abs(result['headwind_component']):.0f} kts
                - **Crosswind:** {result['crosswind_component']:.0f} kts von {result['crosswind_direction']}
                - **Winkel-Differenz:** {result['angle_difference']:.0f}°
                
                **Interpretation:**
                
                - **Headwind (positiv):** Verbessert Performance, verkürzt Startstrecke
                - **Tailwind (negativ):** Verschlechtert Performance, längere Landestrecke
                - **Crosswind:** Erfordert Seitenwind-Korrektur, beachten Sie Flugzeug-Limits
                
                **Typische Crosswind-Limits:**
                - Light GA (Cessna 172): ~15 kts
                - High-Performance GA: ~20 kts
                - Twins/Turboprops: ~25-30 kts
                """)


if __name__ == "__main__":
    main()
