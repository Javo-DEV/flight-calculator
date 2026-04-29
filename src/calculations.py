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
