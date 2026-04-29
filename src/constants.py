# Aviation Constants and Conversion Factors
"""
Standard aviation constants used throughout the Flight Calculator.
Based on ICAO Standard Atmosphere (ISA) and aviation conventions.
"""

# Standard Atmosphere (ISA at Sea Level)
ISA_TEMPERATURE_C = 15.0  # Celsius
ISA_TEMPERATURE_K = 288.15  # Kelvin
ISA_PRESSURE_HPA = 1013.25  # Hectopascals
ISA_PRESSURE_INHG = 29.92  # Inches of Mercury
ISA_DENSITY = 1.225  # kg/m³

# Temperature Lapse Rate
TEMPERATURE_LAPSE_RATE = 1.98  # °C per 1000 feet (standard atmosphere)

# Common Descent Angles
STANDARD_DESCENT_ANGLE = 3.0  # degrees (typical ILS glideslope)
STEEP_DESCENT_ANGLE = 5.0  # degrees

# Conversion Factors
FEET_TO_METERS = 0.3048
METERS_TO_FEET = 3.28084
KNOTS_TO_KMH = 1.852
KMH_TO_KNOTS = 0.539957
KNOTS_TO_MPS = 0.514444
NM_TO_KM = 1.852
KM_TO_NM = 0.539957

# Unit Labels
UNIT_ALTITUDE = "feet"
UNIT_SPEED = "knots"
UNIT_DISTANCE = "NM"
UNIT_VERTICAL_SPEED = "ft/min"
UNIT_ANGLE = "degrees"

# Typical Aircraft Performance (Cessna 172 as default reference)
DEFAULT_TAS = 120  # knots
DEFAULT_CRUISE_ALTITUDE = 5000  # feet
DEFAULT_DESCENT_RATE = 500  # feet per minute
DEFAULT_CLIMB_RATE = 700  # feet per minute

# Wind Calculation Limits
MAX_WIND_SPEED = 200  # knots (sanity check)
MAX_CROSSWIND_COMPONENT = 30  # knots (typical GA aircraft limit)
