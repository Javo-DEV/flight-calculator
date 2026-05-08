# Aircraft Database for Weight & Balance Calculations
"""
Aircraft performance data and weight & balance specifications.

This module contains detailed specifications for various aircraft types
used in weight & balance calculations, including:
- Empty weight and CG position
- Station locations (seats, fuel, baggage)
- Maximum weights and CG limits
- CG envelope coordinates

All weights in pounds (lbs), arms in inches, moments in lb-in.
"""

from typing import Dict, List, Tuple


# ============================================================================
# AIRCRAFT SPECIFICATIONS
# ============================================================================

AIRCRAFT_DATABASE = {
    "Cessna 172S Skyhawk": {
        "empty_weight": 1680,  # lbs
        "empty_arm": 39.5,  # inches aft of datum
        "empty_moment": 66360,  # lb-in
        
        # Weight Limits
        "max_ramp_weight": 2558,  # lbs
        "max_takeoff_weight": 2550,  # lbs
        "max_landing_weight": 2550,  # lbs
        
        # Fuel
        "fuel_capacity": 56,  # US gallons (usable)
        "fuel_weight_per_gallon": 6.0,  # lbs/gal (AvGas)
        "fuel_arm": 48.0,  # inches
        
        # Stations
        "stations": {
            "front_seats": {
                "name": "Front Seats (Pilot & Co-Pilot)",
                "arm": 37.0,
                "max_weight": 400  # Combined max (2 x 200)
            },
            "rear_seats": {
                "name": "Rear Seats",
                "arm": 73.0,
                "max_weight": 400  # Combined max (2 x 200)
            },
            "baggage_area_1": {
                "name": "Baggage Area 1",
                "arm": 95.0,
                "max_weight": 120
            },
            "baggage_area_2": {
                "name": "Baggage Area 2 (Extended)",
                "arm": 123.0,
                "max_weight": 50
            }
        },
        
        # CG Envelope (Forward CG, Aft CG) for different weights
        # Format: (weight_lbs, forward_limit_inches, aft_limit_inches)
        "cg_envelope": [
            (1500, 35.0, 40.5),
            (1950, 35.0, 43.5),
            (2550, 35.0, 47.3),
        ],
        
        # Description
        "description": "Popular 4-seat single-engine trainer and personal aircraft"
    },
    
    "Cessna 208B Grand Caravan": {
        "empty_weight": 4730,  # lbs (typical)
        "empty_arm": 143.5,  # inches (within envelope)
        "empty_moment": 678755,  # lb-in (4730 * 143.5)
        
        # Weight Limits
        "max_ramp_weight": 8807,  # lbs
        "max_takeoff_weight": 8750,  # lbs
        "max_landing_weight": 8500,  # lbs
        
        # Fuel
        "fuel_capacity": 335,  # US gallons (usable)
        "fuel_weight_per_gallon": 6.7,  # lbs/gal (Jet-A is heavier than AvGas)
        "fuel_arm": 141.0,  # inches (wing tanks, forward of empty CG)
        
        # Stations
        "stations": {
            "pilot_seat": {
                "name": "Pilot Seat",
                "arm": 137.0,
                "max_weight": 250
            },
            "copilot_seat": {
                "name": "Co-Pilot Seat",
                "arm": 137.0,
                "max_weight": 250
            },
            "passenger_row_1": {
                "name": "Passenger Row 1 (2 seats)",
                "arm": 194.0,
                "max_weight": 480  # 2 x 240
            },
            "passenger_row_2": {
                "name": "Passenger Row 2 (2 seats)",
                "arm": 222.0,
                "max_weight": 480
            },
            "passenger_row_3": {
                "name": "Passenger Row 3 (2 seats)",
                "arm": 250.0,
                "max_weight": 480
            },
            "passenger_row_4": {
                "name": "Passenger Row 4 (2 seats)",
                "arm": 278.0,
                "max_weight": 480
            },
            "cargo_pod": {
                "name": "Cargo Pod",
                "arm": 292.0,
                "max_weight": 1200
            }
        },
        
        # CG Envelope
        "cg_envelope": [
            (4750, 135.0, 145.0),
            (6000, 135.0, 152.0),
            (8750, 135.0, 152.0),
        ],
        
        # Description
        "description": "Single-engine turboprop utility aircraft, popular for cargo and passenger operations"
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_aircraft_list() -> List[str]:
    """
    Get list of all available aircraft models.
    
    Returns:
        List of aircraft model names
    """
    return list(AIRCRAFT_DATABASE.keys())


def get_aircraft_data(aircraft_name: str) -> Dict:
    """
    Get complete data for a specific aircraft.
    
    Args:
        aircraft_name: Name of the aircraft model
    
    Returns:
        Dictionary containing all aircraft specifications
    
    Raises:
        KeyError: If aircraft not found in database
    """
    if aircraft_name not in AIRCRAFT_DATABASE:
        raise KeyError(f"Aircraft '{aircraft_name}' not found in database")
    
    return AIRCRAFT_DATABASE[aircraft_name]


def interpolate_cg_limits(aircraft_name: str, weight: float) -> Tuple[float, float]:
    """
    Interpolate forward and aft CG limits for a given weight.
    
    The CG envelope is defined by discrete points. This function
    interpolates between them to find the limits at any weight.
    
    Args:
        aircraft_name: Name of the aircraft model
        weight: Current aircraft weight in lbs
    
    Returns:
        Tuple of (forward_limit, aft_limit) in inches
    
    Raises:
        ValueError: If weight is outside envelope range
    """
    aircraft = get_aircraft_data(aircraft_name)
    envelope = aircraft["cg_envelope"]
    
    # Sort envelope by weight
    envelope = sorted(envelope, key=lambda x: x[0])
    
    # Check if weight is within range
    if weight < envelope[0][0]:
        raise ValueError(f"Weight {weight} lbs is below minimum envelope weight {envelope[0][0]} lbs")
    if weight > envelope[-1][0]:
        raise ValueError(f"Weight {weight} lbs exceeds maximum envelope weight {envelope[-1][0]} lbs")
    
    # Find the two points to interpolate between
    for i in range(len(envelope) - 1):
        w1, fwd1, aft1 = envelope[i]
        w2, fwd2, aft2 = envelope[i + 1]
        
        if w1 <= weight <= w2:
            # Linear interpolation
            ratio = (weight - w1) / (w2 - w1) if w2 != w1 else 0
            fwd_limit = fwd1 + ratio * (fwd2 - fwd1)
            aft_limit = aft1 + ratio * (aft2 - aft1)
            return (fwd_limit, aft_limit)
    
    # If we get here, weight equals last point
    return (envelope[-1][1], envelope[-1][2])


def is_within_cg_envelope(aircraft_name: str, weight: float, cg_position: float) -> bool:
    """
    Check if a weight and CG position is within the aircraft's CG envelope.
    
    Args:
        aircraft_name: Name of the aircraft model
        weight: Current aircraft weight in lbs
        cg_position: Current CG position in inches from datum
    
    Returns:
        True if within envelope, False otherwise
    """
    try:
        fwd_limit, aft_limit = interpolate_cg_limits(aircraft_name, weight)
        return fwd_limit <= cg_position <= aft_limit
    except ValueError:
        # Weight outside envelope range
        return False
