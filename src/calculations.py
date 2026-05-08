# Aviation Calculations Module
"""
Core calculation functions for MSFS 2020 Flight Calculator.

This module contains all mathematical functions for aviation calculations:
- Top of Descent (TOD) and descent rate calculations
- Wind correction angle and ground speed calculations
- True/Magnetic course conversions (TVMDC)
- Wind triangle solutions

All angles are in degrees, speeds in knots, distances in nautical miles,
and altitudes in feet, following aviation conventions.
"""

import math
from typing import Dict, List, Optional
from typing import Tuple, Dict
from .constants import STANDARD_DESCENT_ANGLE


def calculate_descent_rate(
    current_altitude: float,
    target_altitude: float,
    descent_angle: float = STANDARD_DESCENT_ANGLE,
    ground_speed: float = None
) -> Dict[str, float]:
    """
    Calculate descent parameters for a given descent angle.
    
    Args:
        current_altitude: Current altitude in feet
        target_altitude: Target altitude in feet
        descent_angle: Desired descent angle in degrees (default: 3°)
        ground_speed: Ground speed in knots (optional, for time calculation)
    
    Returns:
        Dictionary containing:
        - altitude_loss: Altitude to lose (feet)
        - descent_rate: Required descent rate (ft/min) if ground_speed provided
        - distance_to_tod: Horizontal distance to Top of Descent (NM)
        - descent_time: Time for descent (minutes) if ground_speed provided
    
    Formula:
        Distance = Altitude Loss / tan(descent_angle)
        For 3° descent: Distance ≈ Altitude Loss / 300 (rule of thumb)
    """
    altitude_loss = current_altitude - target_altitude
    
    if altitude_loss <= 0:
        return {
            "altitude_loss": 0,
            "descent_rate": 0,
            "distance_to_tod": 0,
            "descent_time": 0
        }
    
    # Convert descent angle to radians
    angle_rad = math.radians(descent_angle)
    
    # Calculate horizontal distance (in feet first)
    distance_feet = altitude_loss / math.tan(angle_rad)
    
    # Convert to nautical miles (1 NM = 6076.12 feet)
    distance_nm = distance_feet / 6076.12
    
    result = {
        "altitude_loss": altitude_loss,
        "descent_rate": None,
        "distance_to_tod": distance_nm,
        "descent_time": None
    }
    
    # Calculate descent rate and time if ground speed is provided
    if ground_speed and ground_speed > 0:
        # Time to descend in hours
        time_hours = distance_nm / ground_speed
        # Time in minutes
        time_minutes = time_hours * 60
        # Descent rate in feet per minute
        descent_rate = altitude_loss / time_minutes
        
        result["descent_rate"] = descent_rate
        result["descent_time"] = time_minutes
    
    return result


def calculate_wind_correction(
    true_airspeed: float,
    true_course: float,
    wind_direction: float,
    wind_speed: float
) -> Dict[str, float]:
    """
    Calculate wind correction angle and ground speed using wind triangle.
    
    Args:
        true_airspeed: True airspeed in knots
        true_course: Desired true course (track) in degrees
        wind_direction: Wind FROM direction in degrees (e.g., 270° = wind from west)
        wind_speed: Wind speed in knots
    
    Returns:
        Dictionary containing:
        - wind_correction_angle: Angle to correct for wind (degrees, + = right, - = left)
        - true_heading: True heading to fly (degrees)
        - ground_speed: Resulting ground speed (knots)
        - drift_angle: Drift caused by wind (degrees)
        - headwind_component: Headwind component (knots, negative = tailwind)
        - crosswind_component: Crosswind component (knots, + = from right)
    
    Uses vector mathematics to solve the wind triangle.
    """
    # Convert to radians
    tc_rad = math.radians(true_course)
    wd_rad = math.radians(wind_direction)
    
    # Calculate wind components relative to desired track
    # Wind angle relative to track (where wind is coming from)
    wind_angle = wind_direction - true_course
    wind_angle_rad = math.radians(wind_angle)
    
    # Headwind component (positive = headwind, negative = tailwind)
    headwind_component = wind_speed * math.cos(wind_angle_rad)
    
    # Crosswind component (positive = from right, negative = from left)
    crosswind_component = wind_speed * math.sin(wind_angle_rad)
    
    # Calculate wind correction angle (WCA)
    # Using sine formula: sin(WCA) = (crosswind / TAS)
    if true_airspeed > 0:
        sin_wca = crosswind_component / true_airspeed
        # Clamp to valid range [-1, 1] to avoid math domain errors
        sin_wca = max(-1.0, min(1.0, sin_wca))
        wca = math.degrees(math.asin(sin_wca))
    else:
        wca = 0
    
    # True heading to fly (course + wind correction)
    true_heading = true_course + wca
    
    # Normalize to 0-360
    true_heading = true_heading % 360
    
    # Calculate ground speed using vector addition
    # GS = TAS * cos(WCA) - headwind_component
    gs = true_airspeed * math.cos(math.radians(wca)) - headwind_component
    
    # Alternative more precise calculation using law of cosines
    # This accounts for the wind triangle more accurately
    # Using wind velocity components
    wind_north = -wind_speed * math.cos(wd_rad)  # Negative because wind FROM direction
    wind_east = -wind_speed * math.sin(wd_rad)
    
    # Aircraft velocity components (heading + TAS)
    heading_rad = math.radians(true_heading)
    ac_north = true_airspeed * math.cos(heading_rad)
    ac_east = true_airspeed * math.sin(heading_rad)
    
    # Ground velocity components
    gv_north = ac_north + wind_north
    gv_east = ac_east + wind_east
    
    # Ground speed
    ground_speed = math.sqrt(gv_north**2 + gv_east**2)
    
    # Drift angle (difference between heading and actual track)
    actual_track = math.degrees(math.atan2(gv_east, gv_north))
    drift_angle = (actual_track - true_heading) % 360
    if drift_angle > 180:
        drift_angle -= 360
    
    return {
        "wind_correction_angle": wca,
        "true_heading": true_heading,
        "ground_speed": ground_speed,
        "drift_angle": drift_angle,
        "headwind_component": headwind_component,
        "crosswind_component": crosswind_component
    }


def convert_course(
    course: float,
    magnetic_variation: float,
    from_true: bool = True
) -> float:
    """
    Convert between True and Magnetic course using TVMDC formula.
    
    TVMDC Mnemonic:
    T = True Course
    V = Variation (magnetic declination)
    M = Magnetic Course
    D = Deviation (compass error)
    C = Compass Course
    
    Rule: "East is Least, West is Best"
    - True to Magnetic: subtract EAST variation, add WEST variation
    - Magnetic to True: add EAST variation, subtract WEST variation
    
    Args:
        course: Course value in degrees (True or Magnetic)
        magnetic_variation: Magnetic variation in degrees
                           Positive = East, Negative = West
        from_true: If True, converts True→Magnetic; if False, converts Magnetic→True
    
    Returns:
        Converted course in degrees (0-360)
    
    Examples:
        True Course 120°, Variation 5°E → Magnetic Course 115°
        True Course 120°, Variation 5°W → Magnetic Course 125°
    """
    if from_true:
        # True to Magnetic: subtract variation
        # (East is Least - subtract positive, add negative)
        result = course - magnetic_variation
    else:
        # Magnetic to True: add variation
        result = course + magnetic_variation
    
    # Normalize to 0-360
    result = result % 360
    
    return result


def calculate_ground_speed(
    true_airspeed: float,
    wind_direction: float,
    wind_speed: float,
    true_heading: float
) -> Dict[str, float]:
    """
    Calculate ground speed given aircraft heading and wind.
    
    This is a simplified version of calculate_wind_correction that assumes
    you already know the heading you want to fly.
    
    Args:
        true_airspeed: True airspeed in knots
        wind_direction: Wind FROM direction in degrees
        wind_speed: Wind speed in knots
        true_heading: True heading aircraft is flying (degrees)
    
    Returns:
        Dictionary containing:
        - ground_speed: Resulting ground speed (knots)
        - headwind_component: Headwind component (knots)
        - crosswind_component: Crosswind component (knots)
        - track: Actual ground track (degrees)
    """
    # Convert to radians
    heading_rad = math.radians(true_heading)
    wind_rad = math.radians(wind_direction)
    
    # Wind velocity components (FROM direction, so negate)
    wind_north = -wind_speed * math.cos(wind_rad)
    wind_east = -wind_speed * math.sin(wind_rad)
    
    # Aircraft velocity components
    ac_north = true_airspeed * math.cos(heading_rad)
    ac_east = true_airspeed * math.sin(heading_rad)
    
    # Ground velocity components
    gv_north = ac_north + wind_north
    gv_east = ac_east + wind_east
    
    # Ground speed
    ground_speed = math.sqrt(gv_north**2 + gv_east**2)
    
    # Actual track
    track = math.degrees(math.atan2(gv_east, gv_north))
    track = track % 360
    
    # Wind components relative to heading
    wind_angle = wind_direction - true_heading
    wind_angle_rad = math.radians(wind_angle)
    
    headwind_component = wind_speed * math.cos(wind_angle_rad)
    crosswind_component = wind_speed * math.sin(wind_angle_rad)
    
    return {
        "ground_speed": ground_speed,
        "headwind_component": headwind_component,
        "crosswind_component": crosswind_component,
        "track": track
    }


def calculate_time_and_fuel(
    distance: float,
    ground_speed: float,
    fuel_flow: float = None
) -> Dict[str, float]:
    """
    Calculate flight time and fuel consumption.
    
    Args:
        distance: Distance in nautical miles
        ground_speed: Ground speed in knots
        fuel_flow: Fuel flow in gallons per hour (optional)
    
    Returns:
        Dictionary containing:
        - time_hours: Flight time in hours
        - time_minutes: Flight time in minutes
        - fuel_required: Fuel required in gallons (if fuel_flow provided)
    """
    if ground_speed <= 0:
        return {
            "time_hours": 0,
            "time_minutes": 0,
            "fuel_required": None
        }
    
    time_hours = distance / ground_speed
    time_minutes = time_hours * 60
    
    result = {
        "time_hours": time_hours,
        "time_minutes": time_minutes,
        "fuel_required": None
    }
    
    if fuel_flow and fuel_flow > 0:
        result["fuel_required"] = time_hours * fuel_flow
    
    return result


def calculate_rule_of_thumb_tod(altitude_loss: float) -> float:
    """
    Quick rule of thumb for Top of Descent calculation.
    
    Rule: For 3° descent, divide altitude loss by 300 to get distance in NM.
    Example: Lose 6000 feet → 6000/300 = 20 NM before target
    
    Args:
        altitude_loss: Altitude to lose in feet
    
    Returns:
        Distance to start descent in nautical miles
    """
    return altitude_loss / 300.0


def calculate_toc_by_rate(
    current_altitude: float,
    target_altitude: float,
    climb_rate: float,
    ground_speed: float
) -> Dict[str, float]:
    """
    Calculate Top of Climb (TOC) parameters given a known climb rate.
    
    Args:
        current_altitude: Current altitude in feet
        target_altitude: Target altitude in feet
        climb_rate: Climb rate in feet per minute
        ground_speed: Ground speed during climb in knots
    
    Returns:
        Dictionary containing:
        - altitude_gain: Altitude to gain (feet)
        - climb_time: Time to reach target altitude (minutes)
        - climb_distance: Horizontal distance to TOC (NM)
        - climb_angle: Average climb angle (degrees)
        - is_realistic: Whether climb rate is realistic for GA aircraft
    
    Formula:
        Time = Altitude Gain / Climb Rate
        Distance = Ground Speed × Time
        Climb Angle = arctan(Climb Rate / Ground Speed in ft/min)
    """
    altitude_gain = target_altitude - current_altitude
    
    if altitude_gain <= 0:
        return {
            "altitude_gain": 0,
            "climb_time": 0,
            "climb_distance": 0,
            "climb_angle": 0,
            "is_realistic": True
        }
    
    if climb_rate <= 0:
        return {
            "altitude_gain": altitude_gain,
            "climb_time": float('inf'),
            "climb_distance": float('inf'),
            "climb_angle": 0,
            "is_realistic": False
        }
    
    # Calculate climb time in minutes
    climb_time = altitude_gain / climb_rate
    
    # Calculate distance in nautical miles
    climb_distance = (ground_speed * climb_time) / 60  # Convert minutes to hours
    
    # Calculate climb angle
    # Convert ground speed from knots to feet per minute: kts × 101.269
    gs_fpm = ground_speed * 101.269
    climb_angle = math.degrees(math.atan(climb_rate / gs_fpm))
    
    # Check if realistic (typical GA: 500-700 fpm, high-performance: up to 1500 fpm)
    is_realistic = climb_rate <= 3000  # Jets can do up to 3000 fpm
    
    return {
        "altitude_gain": altitude_gain,
        "climb_time": climb_time,
        "climb_distance": climb_distance,
        "climb_angle": climb_angle,
        "is_realistic": is_realistic
    }


def calculate_toc_by_time(
    current_altitude: float,
    target_altitude: float,
    available_time: float,
    ground_speed: float
) -> Dict[str, float]:
    """
    Calculate Top of Climb (TOC) parameters given available time.
    
    This calculates the required climb rate to reach target altitude
    within the specified time.
    
    Args:
        current_altitude: Current altitude in feet
        target_altitude: Target altitude in feet
        available_time: Available time for climb in minutes
        ground_speed: Ground speed during climb in knots
    
    Returns:
        Dictionary containing:
        - altitude_gain: Altitude to gain (feet)
        - required_climb_rate: Required climb rate (ft/min)
        - climb_distance: Horizontal distance to TOC (NM)
        - climb_angle: Average climb angle (degrees)
        - is_realistic: Whether required climb rate is realistic
        - aircraft_category: Suggested aircraft category based on climb rate
    
    Aircraft Categories by Climb Rate:
        - Light GA (Cessna 172): 500-700 ft/min
        - High-Performance Single: 1000-1500 ft/min
        - Light Twins/Turboprops: 1500-2000 ft/min
        - Light Jets: 2000-3000 ft/min
        - Airliners: 1500-2500 ft/min (varies with weight)
    """
    altitude_gain = target_altitude - current_altitude
    
    if altitude_gain <= 0:
        return {
            "altitude_gain": 0,
            "required_climb_rate": 0,
            "climb_distance": 0,
            "climb_angle": 0,
            "is_realistic": True,
            "aircraft_category": "N/A"
        }
    
    if available_time <= 0:
        return {
            "altitude_gain": altitude_gain,
            "required_climb_rate": float('inf'),
            "climb_distance": 0,
            "climb_angle": 90,
            "is_realistic": False,
            "aircraft_category": "Rocket"
        }
    
    # Calculate required climb rate
    required_climb_rate = altitude_gain / available_time
    
    # Calculate distance
    climb_distance = (ground_speed * available_time) / 60
    
    # Calculate climb angle
    gs_fpm = ground_speed * 101.269
    climb_angle = math.degrees(math.atan(required_climb_rate / gs_fpm))
    
    # Determine aircraft category and realism
    if required_climb_rate <= 700:
        aircraft_category = "Light GA (Cessna, Piper)"
        is_realistic = True
    elif required_climb_rate <= 1500:
        aircraft_category = "High-Performance Single"
        is_realistic = True
    elif required_climb_rate <= 2000:
        aircraft_category = "Light Twin/Turboprop"
        is_realistic = True
    elif required_climb_rate <= 3000:
        aircraft_category = "Light Jet/Airliner"
        is_realistic = True
    else:
        aircraft_category = "Military/Unrealistic"
        is_realistic = False
    
    return {
        "altitude_gain": altitude_gain,
        "required_climb_rate": required_climb_rate,
        "climb_distance": climb_distance,
        "climb_angle": climb_angle,
        "is_realistic": is_realistic,
        "aircraft_category": aircraft_category
    }


def calculate_rule_of_thumb_toc(altitude_gain: float, climb_rate: float = 500) -> float:
    """
    Quick rule of thumb for Top of Climb calculation.
    
    Rule: For typical GA climb rate of 500 ft/min at 100 kts,
    distance ≈ altitude_gain / 300 (similar to TOD)
    
    Args:
        altitude_gain: Altitude to gain in feet
        climb_rate: Expected climb rate in ft/min (default: 500)
    
    Returns:
        Approximate distance to TOC in nautical miles
    """
    # Rule: at 500 fpm and ~100 kts GS, distance ≈ alt_gain / 300
    # More precise: time = alt_gain / climb_rate, dist = GS × time
    # Assuming ~100 kts GS: dist = 100 × (alt_gain / climb_rate) / 60
    # For 500 fpm: dist ≈ alt_gain / 300
    return altitude_gain / 300.0


# ============================================================================
# UNIT CONVERSION FUNCTIONS
# ============================================================================

def convert_altitude(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert altitude/length between feet, meters, and kilometers.
    
    Args:
        value: The value to convert
        from_unit: Source unit ('feet', 'meters', 'kilometers')
        to_unit: Target unit ('feet', 'meters', 'kilometers')
    
    Returns:
        Converted value
    
    Raises:
        ValueError: If invalid units are provided
    """
    from .constants import (
        FEET_TO_METERS, METERS_TO_FEET,
        FEET_TO_KILOMETERS, KILOMETERS_TO_FEET
    )
    
    # Normalize unit names
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    # If same unit, return as-is
    if from_unit == to_unit:
        return value
    
    # Convert to feet first (base unit)
    if from_unit == 'feet':
        value_in_feet = value
    elif from_unit == 'meters':
        value_in_feet = value * METERS_TO_FEET
    elif from_unit == 'kilometers':
        value_in_feet = value * KILOMETERS_TO_FEET
    else:
        raise ValueError(f"Unknown altitude unit: {from_unit}")
    
    # Convert from feet to target unit
    if to_unit == 'feet':
        return value_in_feet
    elif to_unit == 'meters':
        return value_in_feet * FEET_TO_METERS
    elif to_unit == 'kilometers':
        return value_in_feet * FEET_TO_KILOMETERS
    else:
        raise ValueError(f"Unknown altitude unit: {to_unit}")


def convert_distance(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert distance between nautical miles, kilometers, and statute miles.
    
    Args:
        value: The value to convert
        from_unit: Source unit ('nm', 'km', 'miles')
        to_unit: Target unit ('nm', 'km', 'miles')
    
    Returns:
        Converted value
    
    Raises:
        ValueError: If invalid units are provided
    """
    from .constants import (
        NM_TO_KM, KM_TO_NM,
        NM_TO_MILES, MILES_TO_NM,
        KM_TO_MILES, MILES_TO_KM
    )
    
    # Normalize unit names
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    # If same unit, return as-is
    if from_unit == to_unit:
        return value
    
    # Direct conversions
    conversion_map = {
        ('nm', 'km'): NM_TO_KM,
        ('km', 'nm'): KM_TO_NM,
        ('nm', 'miles'): NM_TO_MILES,
        ('miles', 'nm'): MILES_TO_NM,
        ('km', 'miles'): KM_TO_MILES,
        ('miles', 'km'): MILES_TO_KM,
    }
    
    key = (from_unit, to_unit)
    if key in conversion_map:
        return value * conversion_map[key]
    else:
        raise ValueError(f"Cannot convert from {from_unit} to {to_unit}")


def convert_weight(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert weight/mass between kilograms, pounds, and metric tons.
    
    Args:
        value: The value to convert
        from_unit: Source unit ('kg', 'lbs', 'tons')
        to_unit: Target unit ('kg', 'lbs', 'tons')
    
    Returns:
        Converted value
    
    Raises:
        ValueError: If invalid units are provided
    """
    from .constants import (
        KG_TO_LBS, LBS_TO_KG,
        KG_TO_TONS, TONS_TO_KG,
        LBS_TO_TONS, TONS_TO_LBS
    )
    
    # Normalize unit names
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    # If same unit, return as-is
    if from_unit == to_unit:
        return value
    
    # Direct conversions
    conversion_map = {
        ('kg', 'lbs'): KG_TO_LBS,
        ('lbs', 'kg'): LBS_TO_KG,
        ('kg', 'tons'): KG_TO_TONS,
        ('tons', 'kg'): TONS_TO_KG,
        ('lbs', 'tons'): LBS_TO_TONS,
        ('tons', 'lbs'): TONS_TO_LBS,
    }
    
    key = (from_unit, to_unit)
    if key in conversion_map:
        return value * conversion_map[key]
    else:
        raise ValueError(f"Cannot convert from {from_unit} to {to_unit}")


def convert_fuel_volume(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert fuel volume between liters, US gallons, and Imperial gallons.
    
    Args:
        value: The value to convert
        from_unit: Source unit ('liters', 'us_gal', 'imp_gal')
        to_unit: Target unit ('liters', 'us_gal', 'imp_gal')
    
    Returns:
        Converted value
    
    Raises:
        ValueError: If invalid units are provided
    """
    from .constants import (
        LITERS_TO_US_GALLONS, US_GALLONS_TO_LITERS,
        LITERS_TO_IMP_GALLONS, IMP_GALLONS_TO_LITERS,
        US_GALLONS_TO_IMP_GALLONS, IMP_GALLONS_TO_US_GALLONS
    )
    
    # Normalize unit names
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    # If same unit, return as-is
    if from_unit == to_unit:
        return value
    
    # Direct conversions
    conversion_map = {
        ('liters', 'us_gal'): LITERS_TO_US_GALLONS,
        ('us_gal', 'liters'): US_GALLONS_TO_LITERS,
        ('liters', 'imp_gal'): LITERS_TO_IMP_GALLONS,
        ('imp_gal', 'liters'): IMP_GALLONS_TO_LITERS,
        ('us_gal', 'imp_gal'): US_GALLONS_TO_IMP_GALLONS,
        ('imp_gal', 'us_gal'): IMP_GALLONS_TO_US_GALLONS,
    }
    
    key = (from_unit, to_unit)
    if key in conversion_map:
        return value * conversion_map[key]
    else:
        raise ValueError(f"Cannot convert from {from_unit} to {to_unit}")


# ============================================================================
# E6B FLIGHT COMPUTER FUNCTIONS
# ============================================================================

def calculate_true_airspeed(
    indicated_airspeed: float,
    pressure_altitude: float,
    temperature_c: float = None
) -> Dict[str, float]:
    """
    Calculate True Airspeed (TAS) from Indicated Airspeed (IAS).
    
    Uses the standard 2% rule: TAS increases by approximately 2% per 1000 feet
    of pressure altitude. For more accurate results, temperature can be provided.
    
    Args:
        indicated_airspeed: IAS in knots
        pressure_altitude: Pressure altitude in feet
        temperature_c: Outside Air Temperature in Celsius (optional for more accuracy)
    
    Returns:
        Dictionary containing:
        - tas: True Airspeed in knots
        - correction_percent: Percentage correction applied
        - isa_deviation: Temperature deviation from ISA (if temp provided)
    
    Formula:
        Simple: TAS = IAS * (1 + 0.02 * altitude / 1000)
        With temp: TAS = IAS * sqrt(T_actual / T_standard)
    """
    from .constants import STD_TEMP_C, TEMPERATURE_LAPSE_RATE, TAS_CORRECTION_PERCENT_PER_1000FT
    
    # Simple method: 2% per 1000 feet
    altitude_thousands = pressure_altitude / 1000
    correction_percent = TAS_CORRECTION_PERCENT_PER_1000FT * altitude_thousands
    tas_simple = indicated_airspeed * (1 + correction_percent / 100)
    
    result = {
        "tas": tas_simple,
        "correction_percent": correction_percent,
        "isa_deviation": None
    }
    
    # More accurate method if temperature is provided
    if temperature_c is not None:
        # Calculate ISA temperature at altitude
        isa_temp_at_altitude = STD_TEMP_C - (TEMPERATURE_LAPSE_RATE * altitude_thousands)
        isa_deviation = temperature_c - isa_temp_at_altitude
        
        # Convert to Kelvin for ratio calculation
        temp_k = temperature_c + 273.15
        isa_temp_k = isa_temp_at_altitude + 273.15
        
        # TAS correction based on temperature ratio
        temp_correction = math.sqrt(temp_k / isa_temp_k)
        tas_accurate = indicated_airspeed * temp_correction
        
        result["tas"] = tas_accurate
        result["isa_deviation"] = isa_deviation
        result["correction_percent"] = ((tas_accurate / indicated_airspeed) - 1) * 100
    
    return result


def calculate_density_altitude(
    pressure_altitude: float,
    temperature_c: float,
    altimeter_setting: float = 29.92
) -> Dict[str, float]:
    """
    Calculate Density Altitude - critical for aircraft performance.
    
    Density altitude is the pressure altitude corrected for non-standard temperature.
    High density altitude reduces aircraft performance (longer takeoff, reduced climb).
    
    Args:
        pressure_altitude: Pressure altitude in feet (or field elevation if QNH = 29.92)
        temperature_c: Outside Air Temperature in Celsius
        altimeter_setting: Current altimeter setting in inches Hg (default: 29.92)
    
    Returns:
        Dictionary containing:
        - density_altitude: Density altitude in feet
        - pressure_altitude: Calculated pressure altitude
        - isa_deviation: Deviation from ISA temperature
        - performance_impact: Text description of performance impact
    
    Formula:
        Pressure Altitude = Field Elevation + (29.92 - Altimeter Setting) * 1000
        Density Altitude = Pressure Altitude + (120 * (OAT - ISA Temp))
    """
    from .constants import STD_TEMP_C, TEMPERATURE_LAPSE_RATE, DENSITY_ALTITUDE_TEMP_CORRECTION, STD_PRESSURE_INHG
    
    # Calculate pressure altitude if altimeter setting is not standard
    if altimeter_setting != STD_PRESSURE_INHG:
        pressure_alt_correction = (STD_PRESSURE_INHG - altimeter_setting) * 1000
        pressure_alt = pressure_altitude + pressure_alt_correction
    else:
        pressure_alt = pressure_altitude
    
    # Calculate ISA temperature at this pressure altitude
    altitude_thousands = pressure_alt / 1000
    isa_temp_at_altitude = STD_TEMP_C - (TEMPERATURE_LAPSE_RATE * altitude_thousands)
    
    # Temperature deviation from ISA
    temp_deviation = temperature_c - isa_temp_at_altitude
    
    # Density altitude calculation
    density_alt = pressure_alt + (DENSITY_ALTITUDE_TEMP_CORRECTION * temp_deviation)
    
    # Performance impact assessment
    diff = density_alt - pressure_alt
    if diff < 500:
        impact = "Minimal impact on performance"
    elif diff < 1500:
        impact = "Noticeable performance reduction - exercise caution"
    elif diff < 3000:
        impact = "Significant performance reduction - careful planning required"
    else:
        impact = "CRITICAL: Severe performance degradation - consider alternatives"
    
    return {
        "density_altitude": density_alt,
        "pressure_altitude": pressure_alt,
        "isa_temp": isa_temp_at_altitude,
        "isa_deviation": temp_deviation,
        "performance_impact": impact
    }


def calculate_fuel_required(
    distance: float = None,
    time_hours: float = None,
    fuel_flow: float = None,
    ground_speed: float = None,
    include_reserve: bool = True,
    reserve_time: float = 45
) -> Dict[str, float]:
    """
    Calculate fuel requirements for a flight.
    
    Can calculate based on either distance or time. Includes reserve fuel
    calculations based on regulatory requirements.
    
    Args:
        distance: Distance in nautical miles (optional)
        time_hours: Flight time in hours (optional)
        fuel_flow: Fuel consumption in gallons per hour
        ground_speed: Ground speed in knots (required if using distance)
        include_reserve: Include reserve fuel in calculation (default: True)
        reserve_time: Reserve time in minutes (default: 45 for IFR)
    
    Returns:
        Dictionary containing:
        - fuel_required: Fuel needed for flight (gallons)
        - fuel_reserve: Reserve fuel (gallons)
        - total_fuel: Total fuel including reserve (gallons)
        - flight_time: Flight time in hours
        - endurance: Total endurance with fuel (hours)
    
    Raises:
        ValueError: If insufficient parameters provided
    """
    if fuel_flow is None or fuel_flow <= 0:
        raise ValueError("Fuel flow must be provided and greater than 0")
    
    # Calculate flight time
    if time_hours is not None:
        flight_time = time_hours
    elif distance is not None and ground_speed is not None and ground_speed > 0:
        flight_time = distance / ground_speed
    else:
        raise ValueError("Must provide either time_hours, or distance with ground_speed")
    
    # Calculate fuel required for flight
    fuel_required = flight_time * fuel_flow
    
    # Calculate reserve fuel
    reserve_hours = reserve_time / 60
    fuel_reserve = reserve_hours * fuel_flow if include_reserve else 0
    
    # Total fuel
    total_fuel = fuel_required + fuel_reserve
    
    # Calculate endurance (how long can we fly with this fuel)
    endurance = total_fuel / fuel_flow if fuel_flow > 0 else 0
    
    return {
        "fuel_required": fuel_required,
        "fuel_reserve": fuel_reserve,
        "total_fuel": total_fuel,
        "flight_time": flight_time,
        "endurance": endurance,
        "reserve_time": reserve_time
    }


def calculate_endurance_and_range(
    fuel_available: float,
    fuel_flow: float,
    ground_speed: float
) -> Dict[str, float]:
    """
    Calculate how long and how far you can fly with available fuel.
    
    Args:
        fuel_available: Available fuel in gallons
        fuel_flow: Fuel consumption in gallons per hour
        ground_speed: Ground speed in knots
    
    Returns:
        Dictionary containing:
        - endurance: Maximum flight time in hours
        - range: Maximum range in nautical miles
        - endurance_with_reserve: Endurance minus 45-min IFR reserve
        - range_with_reserve: Range minus 45-min IFR reserve
    """
    if fuel_flow <= 0:
        raise ValueError("Fuel flow must be greater than 0")
    
    # Calculate endurance (hours)
    endurance = fuel_available / fuel_flow
    
    # Calculate range (NM)
    range_nm = endurance * ground_speed
    
    # Calculate with 45-minute reserve
    reserve_fuel = (45 / 60) * fuel_flow
    usable_fuel = max(0, fuel_available - reserve_fuel)
    endurance_with_reserve = usable_fuel / fuel_flow
    range_with_reserve = endurance_with_reserve * ground_speed
    
    return {
        "endurance": endurance,
        "range": range_nm,
        "endurance_with_reserve": endurance_with_reserve,
        "range_with_reserve": range_with_reserve,
        "reserve_fuel": reserve_fuel
    }


def calculate_wind_components(
    runway_heading: float,
    wind_direction: float,
    wind_speed: float
) -> Dict[str, float]:
    """
    Calculate headwind/tailwind and crosswind components for a runway.
    
    Critical for determining takeoff/landing performance and runway selection.
    
    Args:
        runway_heading: Runway magnetic heading in degrees (e.g., 270 for runway 27)
        wind_direction: Wind FROM direction in degrees
        wind_speed: Wind speed in knots
    
    Returns:
        Dictionary containing:
        - headwind_component: Headwind component in knots (+ = headwind, - = tailwind)
        - crosswind_component: Crosswind component in knots (absolute value)
        - crosswind_direction: 'left' or 'right' from pilot perspective
        - angle_difference: Angle between runway and wind
    
    Formula:
        Headwind = Wind Speed * cos(angle difference)
        Crosswind = Wind Speed * sin(angle difference)
    """
    # Calculate angle between runway heading and wind direction
    angle_diff = wind_direction - runway_heading
    
    # Normalize to -180 to +180
    while angle_diff > 180:
        angle_diff -= 360
    while angle_diff < -180:
        angle_diff += 360
    
    # Convert to radians
    angle_rad = math.radians(angle_diff)
    
    # Calculate components
    headwind = wind_speed * math.cos(angle_rad)
    crosswind = abs(wind_speed * math.sin(angle_rad))
    
    # Determine crosswind direction
    if angle_diff > 0:
        crosswind_direction = "right"
    elif angle_diff < 0:
        crosswind_direction = "left"
    else:
        crosswind_direction = "none"
    
    return {
        "headwind_component": headwind,
        "crosswind_component": crosswind,
        "crosswind_direction": crosswind_direction,
        "angle_difference": abs(angle_diff)
    }


# ============================================================================
# WEIGHT & BALANCE CALCULATIONS
# ============================================================================

def calculate_weight_and_balance(
    aircraft_name: str,
    fuel_gallons: float,
    station_weights: Dict[str, float]
) -> Dict[str, any]:
    """
    Calculate weight and balance for an aircraft.
    
    Performs comprehensive weight and balance calculations including:
    - Total weight
    - Center of Gravity (CG) position
    - Total moment
    - CG envelope check
    - Weight limits check
    
    Args:
        aircraft_name: Name of aircraft from aircraft database
        fuel_gallons: Fuel on board in US gallons
        station_weights: Dictionary of station_name: weight_lbs
            Example: {"front_seats": 340, "rear_seats": 280, "baggage_area_1": 50}
    
    Returns:
        Dictionary containing:
        - total_weight: Total aircraft weight (lbs)
        - total_moment: Total moment (lb-in)
        - cg_position: CG position in inches from datum
        - cg_mac_percent: CG as % of Mean Aerodynamic Chord (if available)
        - within_envelope: Boolean - is CG within limits
        - forward_limit: Forward CG limit at this weight (inches)
        - aft_limit: Aft CG limit at this weight (inches)
        - weight_status: "OK", "OVER MAX TAKEOFF", "OVER MAX RAMP", "OVER MAX LANDING"
        - cg_status: "OK", "AFT OF LIMITS", "FORWARD OF LIMITS"
        - stations_detail: List of dicts with station-by-station breakdown
    
    Raises:
        KeyError: If aircraft not found in database
        ValueError: If invalid station names provided
    """
    from .aircraft_data import get_aircraft_data, interpolate_cg_limits, is_within_cg_envelope
    
    # Get aircraft data
    aircraft = get_aircraft_data(aircraft_name)
    
    # Start with empty weight
    total_weight = aircraft["empty_weight"]
    total_moment = aircraft["empty_moment"]
    
    stations_detail = []
    
    # Add empty weight to detail
    stations_detail.append({
        "name": "Empty Weight",
        "weight": aircraft["empty_weight"],
        "arm": aircraft["empty_arm"],
        "moment": aircraft["empty_moment"]
    })
    
    # Add fuel
    fuel_weight = fuel_gallons * aircraft["fuel_weight_per_gallon"]
    fuel_moment = fuel_weight * aircraft["fuel_arm"]
    total_weight += fuel_weight
    total_moment += fuel_moment
    
    stations_detail.append({
        "name": "Fuel",
        "weight": fuel_weight,
        "arm": aircraft["fuel_arm"],
        "moment": fuel_moment
    })
    
    # Add stations
    for station_name, weight in station_weights.items():
        if station_name not in aircraft["stations"]:
            raise ValueError(f"Unknown station: {station_name}. Valid stations: {list(aircraft['stations'].keys())}")
        
        station = aircraft["stations"][station_name]
        moment = weight * station["arm"]
        
        total_weight += weight
        total_moment += moment
        
        stations_detail.append({
            "name": station["name"],
            "weight": weight,
            "arm": station["arm"],
            "moment": moment
        })
    
    # Calculate CG position
    cg_position = total_moment / total_weight if total_weight > 0 else 0
    
    # Check CG envelope
    try:
        fwd_limit, aft_limit = interpolate_cg_limits(aircraft_name, total_weight)
        within_envelope = is_within_cg_envelope(aircraft_name, total_weight, cg_position)
        
        # Determine CG status
        if within_envelope:
            cg_status = "OK"
        elif cg_position < fwd_limit:
            cg_status = "FORWARD OF LIMITS"
        else:
            cg_status = "AFT OF LIMITS"
    except ValueError:
        # Weight outside envelope range
        within_envelope = False
        fwd_limit = None
        aft_limit = None
        cg_status = "WEIGHT OUTSIDE ENVELOPE RANGE"
    
    # Check weight limits
    if total_weight > aircraft["max_ramp_weight"]:
        weight_status = "OVER MAX RAMP"
    elif total_weight > aircraft["max_takeoff_weight"]:
        weight_status = "OVER MAX TAKEOFF"
    elif total_weight > aircraft["max_landing_weight"]:
        weight_status = "OVER MAX LANDING"
    else:
        weight_status = "OK"
    
    return {
        "total_weight": total_weight,
        "total_moment": total_moment,
        "cg_position": cg_position,
        "within_envelope": within_envelope,
        "forward_limit": fwd_limit,
        "aft_limit": aft_limit,
        "weight_status": weight_status,
        "cg_status": cg_status,
        "stations_detail": stations_detail,
        "max_takeoff_weight": aircraft["max_takeoff_weight"],
        "max_ramp_weight": aircraft["max_ramp_weight"],
        "max_landing_weight": aircraft["max_landing_weight"]
    }


def validate_station_weights(
    aircraft_name: str,
    fuel_gallons: float,
    station_weights: Dict[str, float]
) -> Dict[str, List[str]]:
    """
    Validate station weights against maximum limits.
    
    Args:
        aircraft_name: Name of aircraft
        fuel_gallons: Fuel on board
        station_weights: Dictionary of station weights
    
    Returns:
        Dictionary containing:
        - warnings: List of warning messages
        - errors: List of error messages (weight exceeds limits)
    """
    from .aircraft_data import get_aircraft_data
    
    aircraft = get_aircraft_data(aircraft_name)
    warnings = []
    errors = []
    
    # Check fuel capacity
    if fuel_gallons > aircraft["fuel_capacity"]:
        errors.append(f"Fuel {fuel_gallons} gal exceeds capacity {aircraft['fuel_capacity']} gal")
    
    # Check station weights
    for station_name, weight in station_weights.items():
        if station_name in aircraft["stations"]:
            station = aircraft["stations"][station_name]
            if weight > station["max_weight"]:
                errors.append(f"{station['name']}: {weight} lbs exceeds max {station['max_weight']} lbs")
            elif weight > station["max_weight"] * 0.9:
                warnings.append(f"{station['name']}: {weight} lbs approaching max {station['max_weight']} lbs")
    
    return {
        "warnings": warnings,
        "errors": errors
    }
