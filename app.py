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
    calculate_wind_correction,    # Calculate Wind Correction Angle (WCA)
    convert_course,               # Convert between True and Magnetic course
    calculate_ground_speed,       # Calculate ground speed from TAS and wind
    calculate_rule_of_thumb_tod,  # Quick TOD rule (altitude/300)
    calculate_time_and_fuel       # Calculate flight time and fuel consumption
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
            "🌬️ Wind Correction Angle",   # WCA and ground speed calculator
            "🧭 Course Converter",         # True/Magnetic course conversion
            "📊 Ground Speed"              # Ground speed calculator
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
    elif calculator == "🌬️ Wind Correction Angle":
        show_wind_correction_calculator()
    elif calculator == "🧭 Course Converter":
        show_course_converter()
    elif calculator == "📊 Ground Speed":
        show_ground_speed_calculator()


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
        
        # Add WCA label
        mid_angle = np.radians((angle1 + angle2) / 2)
        label_pos = origin + np.array([arc_radius * 1.5 * np.cos(mid_angle),
                                       arc_radius * 1.5 * np.sin(mid_angle)])
        ax.text(label_pos[0], label_pos[1], f'WCA\n{abs(wca):.1f}°', 
               fontsize=10, ha='center', va='center', 
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
    ax.set_xlabel('East/West (skaliert in Knoten)', fontsize=12)
    ax.set_ylabel('North/South (skaliert in Knoten)', fontsize=12)
    ax.set_title('Wind Triangle Visualization', fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    
    # Add info text
    info_text = (
        f"Wind Correction Angle: {wca:+.1f}° ({'right' if wca > 0 else 'left'})\n"
        f"Fly Heading {true_heading:.0f}° to track {true_course:.0f}°"
    )
    ax.text(0.5, -0.05, info_text, transform=ax.transAxes, 
           fontsize=11, ha='center', va='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    return fig


def show_tod_calculator():
    """Top of Descent Calculator"""
    st.header("📉 Top of Descent (TOD) Calculator")
    st.write("Berechnen Sie, wann Sie mit dem Sinkflug beginnen müssen.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Eingabe")
        
        current_alt = st.number_input(
            "Aktuelle Höhe (ft)",
            min_value=0,
            max_value=50000,
            value=DEFAULT_CRUISE_ALTITUDE,
            step=100,
            help="Ihre aktuelle Flughöhe in Fuß"
        )
        
        target_alt = st.number_input(
            "Zielhöhe (ft)",
            min_value=0,
            max_value=50000,
            value=2000,
            step=100,
            help="Die Höhe, die Sie erreichen möchten"
        )
        
        descent_angle = st.slider(
            "Sinkwinkel (°)",
            min_value=1.0,
            max_value=6.0,
            value=STANDARD_DESCENT_ANGLE,
            step=0.5,
            help="Standard: 3° (ILS Glideslope)"
        )
        
        ground_speed = st.number_input(
            "Ground Speed (kts) [optional]",
            min_value=0,
            max_value=500,
            value=120,
            step=10,
            help="Für Sinkraten- und Zeitberechnung"
        )
        
        calculate_btn = st.button("🧮 Berechnen", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("Ergebnis")
        
        if calculate_btn or current_alt != DEFAULT_CRUISE_ALTITUDE:
            result = calculate_descent_rate(
                current_alt, 
                target_alt, 
                descent_angle, 
                ground_speed if ground_speed > 0 else None
            )
            
            if result["altitude_loss"] <= 0:
                st.warning("⚠️ Zielhöhe liegt über oder auf aktueller Höhe!")
            else:
                # Main results
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.metric(
                        "Höhenverlust",
                        f"{result['altitude_loss']:,.0f} ft"
                    )
                    
                    st.metric(
                        "Distanz bis TOD",
                        f"{result['distance_to_tod']:.1f} NM"
                    )
                
                with col_b:
                    if result['descent_rate']:
                        st.metric(
                            "Sinkrate",
                            f"{result['descent_rate']:.0f} ft/min"
                        )
                        
                        st.metric(
                            "Sinkzeit",
                            f"{result['descent_time']:.1f} min"
                        )
                
                # Rule of thumb
                st.markdown("---")
                rule_distance = calculate_rule_of_thumb_tod(result["altitude_loss"])
                st.info(
                    f"**📐 Faustregel (3° Descent):**\n\n"
                    f"Beginnen Sie den Sinkflug ca. **{rule_distance:.0f} NM** "
                    f"vor dem Ziel.\n\n"
                    f"*Berechnung: {result['altitude_loss']:.0f} ft ÷ 300 = {rule_distance:.0f} NM*"
                )
                
                # Explanation
                with st.expander("ℹ️ Erklärung"):
                    st.write(f"""
                    **Berechnung:**
                    - Höhenverlust: {current_alt:,.0f} ft - {target_alt:,.0f} ft = {result['altitude_loss']:,.0f} ft
                    - Distanz: Höhenverlust / tan({descent_angle}°) = {result['distance_to_tod']:.2f} NM
                    """)
                    
                    if result['descent_rate']:
                        st.write(f"""
                        - Zeit: {result['distance_to_tod']:.2f} NM / {ground_speed} kts = {result['descent_time']:.2f} min
                        - Sinkrate: {result['altitude_loss']:,.0f} ft / {result['descent_time']:.2f} min = {result['descent_rate']:.0f} ft/min
                        """)


def show_wind_correction_calculator():
    """Wind Correction Angle Calculator"""
    st.header("🌬️ Wind Correction Angle Calculator")
    st.write("Berechnen Sie Wind Correction Angle (WCA) und Ground Speed.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Eingabe")
        
        tas = st.number_input(
            "True Airspeed (TAS) [kts]",
            min_value=50,
            max_value=500,
            value=DEFAULT_TAS,
            step=10,
            help="Ihre True Airspeed in Knoten"
        )
        
        true_course = st.number_input(
            "Desired True Course (°)",
            min_value=0,
            max_value=359,
            value=180,
            step=1,
            help="Der Kurs, den Sie fliegen möchten (0-359°)"
        )
        
        wind_from = st.number_input(
            "Wind FROM (°)",
            min_value=0,
            max_value=359,
            value=270,
            step=10,
            help="Richtung, AUS DER der Wind kommt (z.B. 270° = Wind von Westen)"
        )
        
        wind_speed = st.number_input(
            "Wind Speed (kts)",
            min_value=0,
            max_value=200,
            value=20,
            step=5,
            help="Windgeschwindigkeit in Knoten"
        )
        
        calculate_btn = st.button("🧮 Berechnen", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("Ergebnis")
        
        if calculate_btn or tas != DEFAULT_TAS:
            result = calculate_wind_correction(
                tas,
                true_course,
                wind_from,
                wind_speed
            )
            
            # Main results
            col_a, col_b = st.columns(2)
            
            with col_a:
                wca_direction = "rechts" if result['wind_correction_angle'] > 0 else "links"
                st.metric(
                    "Wind Correction Angle",
                    f"{abs(result['wind_correction_angle']):.1f}° {wca_direction}",
                    help="Winkel, um den Sie korrigieren müssen"
                )
                
                st.metric(
                    "True Heading to Fly",
                    f"{result['true_heading']:.0f}°",
                    help="Der Heading, den Sie fliegen müssen"
                )
            
            with col_b:
                st.metric(
                    "Ground Speed",
                    f"{result['ground_speed']:.1f} kts",
                    help="Ihre Geschwindigkeit über Grund"
                )
                
                st.metric(
                    "Drift Angle",
                    f"{result['drift_angle']:.1f}°",
                    help="Abdrift durch den Wind"
                )
            
            # Wind components
            st.markdown("---")
            st.subheader("Wind-Komponenten")
            
            col_c, col_d = st.columns(2)
            
            with col_c:
                hw_type = "Rückenwind" if result['headwind_component'] < 0 else "Gegenwind"
                st.metric(
                    hw_type,
                    f"{abs(result['headwind_component']):.1f} kts"
                )
            
            with col_d:
                cw_direction = "von rechts" if result['crosswind_component'] > 0 else "von links"
                st.metric(
                    f"Seitenwind ({cw_direction})",
                    f"{abs(result['crosswind_component']):.1f} kts"
                )
            
            # Explanation
            with st.expander("ℹ️ Erklärung"):
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
            
            # Wind Triangle Visualization
            st.markdown("---")
            st.subheader("🎨 Wind-Dreieck Visualisierung")
            
            fig = plot_wind_triangle(
                tas, 
                true_course, 
                wind_from, 
                wind_speed,
                result['wind_correction_angle'],
                result['true_heading'],
                result['ground_speed']
            )
            st.pyplot(fig)
            plt.close(fig)  # Close figure to free memory


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


if __name__ == "__main__":
    main()
