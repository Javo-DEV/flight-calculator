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

# Length / Altitude
FEET_TO_METERS = 0.3048
METERS_TO_FEET = 3.28084
FEET_TO_KILOMETERS = 0.0003048
KILOMETERS_TO_FEET = 3280.84

# Distance
NM_TO_KM = 1.852
KM_TO_NM = 0.539957
NM_TO_MILES = 1.15078
MILES_TO_NM = 0.868976
KM_TO_MILES = 0.621371
MILES_TO_KM = 1.60934

# Speed
KNOTS_TO_KMH = 1.852
KMH_TO_KNOTS = 0.539957
KNOTS_TO_MPS = 0.514444

# Weight / Mass
KG_TO_LBS = 2.20462
LBS_TO_KG = 0.453592
KG_TO_TONS = 0.001
TONS_TO_KG = 1000
LBS_TO_TONS = 0.000453592
TONS_TO_LBS = 2204.62

# Volume / Fuel
LITERS_TO_US_GALLONS = 0.264172
US_GALLONS_TO_LITERS = 3.78541
LITERS_TO_IMP_GALLONS = 0.219969
IMP_GALLONS_TO_LITERS = 4.54609
US_GALLONS_TO_IMP_GALLONS = 0.832674
IMP_GALLONS_TO_US_GALLONS = 1.20095

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

# E6B Flight Computer Constants
# ============================================================================

# Standard Atmosphere Constants (for TAS and Density Altitude calculations)
STD_PRESSURE_INHG = 29.92  # Standard pressure at sea level in inches Hg
STD_TEMP_C = 15.0  # Standard temperature at sea level in Celsius
STD_TEMP_F = 59.0  # Standard temperature at sea level in Fahrenheit

# Temperature conversion
CELSIUS_TO_FAHRENHEIT = lambda c: (c * 9/5) + 32
FAHRENHEIT_TO_CELSIUS = lambda f: (f - 32) * 5/9

# Pressure Altitude Constants
PRESSURE_ALTITUDE_FACTOR = 1000  # feet per inch Hg difference from 29.92
FT_PER_HPA = 30  # Approximate feet per hectopascal

# TAS Calculation
# TAS increases approximately 2% per 1000 feet
TAS_CORRECTION_PERCENT_PER_1000FT = 2.0

# Density Altitude Constants  
DENSITY_ALTITUDE_TEMP_CORRECTION = 120  # feet per degree C above ISA

# Fuel Constants
MIN_FUEL_RESERVE_TIME = 30  # minutes (VFR day minimum)
MIN_FUEL_RESERVE_TIME_NIGHT = 45  # minutes (VFR night minimum)

# Fuel Weight (typical values)
AVGAS_WEIGHT_PER_GALLON = 6.0  # lbs per US gallon (100LL AvGas)
JET_A_WEIGHT_PER_GALLON = 6.7  # lbs per US gallon (Jet-A)
IFR_FUEL_RESERVE_TIME = 45  # minutes (IFR minimum)
