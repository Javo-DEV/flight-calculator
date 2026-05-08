"""
Unit tests for aviation calculation functions.

This module contains comprehensive tests for all calculation functions
in the MSFS 2020 Flight Calculator application.

Test Coverage:
- Top of Descent (TOD) calculations
- Top of Climb (TOC) calculations (by rate and by time)
- Wind correction angle calculations
- Course conversion (True/Magnetic)
- Ground speed calculations
- Time and fuel calculations
"""

import pytest
import math
import sys
from pathlib import Path

# Add src folder to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.calculations import (
    calculate_descent_rate,
    calculate_toc_by_rate,
    calculate_toc_by_time,
    calculate_wind_correction,
    convert_course,
    calculate_ground_speed,
    calculate_time_and_fuel,
    calculate_rule_of_thumb_tod,
    calculate_rule_of_thumb_toc,
    convert_altitude,
    convert_distance,
    convert_weight,
    convert_fuel_volume,
    # E6B Functions
    calculate_true_airspeed,
    calculate_density_altitude,
    calculate_fuel_required,
    calculate_endurance_and_range,
    calculate_wind_components,
    # Weight & Balance Functions
    calculate_weight_and_balance,
    validate_station_weights
)


# ============================================================================
# TOP OF DESCENT (TOD) TESTS
# ============================================================================

class TestDescentRate:
    """Test suite for descent rate calculations"""
    
    def test_basic_descent(self):
        """Test basic descent calculation with 3° angle"""
        result = calculate_descent_rate(
            current_altitude=10000,
            target_altitude=2000,
            descent_angle=3.0,
            ground_speed=120
        )
        
        assert result['altitude_loss'] == 8000
        assert result['distance_to_tod'] == pytest.approx(26.67, rel=0.1)
        assert result['descent_rate'] == pytest.approx(600, rel=0.1)
        assert result['descent_time'] == pytest.approx(13.33, rel=0.1)
    
    def test_no_descent_needed(self):
        """Test when already at or below target altitude"""
        result = calculate_descent_rate(
            current_altitude=2000,
            target_altitude=5000,
            descent_angle=3.0
        )
        
        assert result['altitude_loss'] == 0
        assert result['distance_to_tod'] == 0
    
    def test_rule_of_thumb_tod(self):
        """Test TOD rule of thumb (altitude/300)"""
        distance = calculate_rule_of_thumb_tod(9000)
        assert distance == pytest.approx(30.0, rel=0.01)


# ============================================================================
# TOP OF CLIMB (TOC) TESTS - BY RATE
# ============================================================================

class TestTOCByRate:
    """Test suite for TOC calculations with known climb rate"""
    
    def test_basic_climb_ga_aircraft(self):
        """Test typical GA aircraft climb (500 ft/min)"""
        result = calculate_toc_by_rate(
            current_altitude=2000,
            target_altitude=10000,
            climb_rate=500,
            ground_speed=120
        )
        
        assert result['altitude_gain'] == 8000
        assert result['climb_time'] == pytest.approx(16.0, rel=0.01)
        assert result['climb_distance'] == pytest.approx(32.0, rel=0.1)
        assert result['climb_angle'] > 0
        assert result['is_realistic'] == True
    
    def test_high_performance_climb(self):
        """Test high-performance aircraft climb (1500 ft/min)"""
        result = calculate_toc_by_rate(
            current_altitude=1000,
            target_altitude=25000,
            climb_rate=1500,
            ground_speed=180
        )
        
        assert result['altitude_gain'] == 24000
        assert result['climb_time'] == pytest.approx(16.0, rel=0.01)
        assert result['climb_distance'] == pytest.approx(48.0, rel=0.1)
        assert result['is_realistic'] == True
    
    def test_jet_climb(self):
        """Test jet aircraft climb (2500 ft/min)"""
        result = calculate_toc_by_rate(
            current_altitude=5000,
            target_altitude=35000,
            climb_rate=2500,
            ground_speed=250
        )
        
        assert result['altitude_gain'] == 30000
        assert result['climb_time'] == pytest.approx(12.0, rel=0.01)
        assert result['climb_distance'] == pytest.approx(50.0, rel=0.1)
        assert result['is_realistic'] == True
    
    def test_unrealistic_climb_rate(self):
        """Test unrealistic climb rate (> 3000 ft/min)"""
        result = calculate_toc_by_rate(
            current_altitude=0,
            target_altitude=10000,
            climb_rate=5000,
            ground_speed=150
        )
        
        assert result['is_realistic'] == False
    
    def test_no_climb_needed(self):
        """Test when already at or above target altitude"""
        result = calculate_toc_by_rate(
            current_altitude=10000,
            target_altitude=5000,
            climb_rate=500,
            ground_speed=120
        )
        
        assert result['altitude_gain'] == 0
        assert result['climb_time'] == 0
        assert result['climb_distance'] == 0
    
    def test_zero_climb_rate(self):
        """Test with zero climb rate (should handle gracefully)"""
        result = calculate_toc_by_rate(
            current_altitude=1000,
            target_altitude=5000,
            climb_rate=0,
            ground_speed=120
        )
        
        assert result['climb_time'] == float('inf')
        assert result['is_realistic'] == False
    
    def test_climb_angle_calculation(self):
        """Test climb angle calculation accuracy"""
        result = calculate_toc_by_rate(
            current_altitude=0,
            target_altitude=5000,
            climb_rate=500,
            ground_speed=100
        )
        
        # At 500 ft/min and 100 kts (~10126.9 ft/min horizontal)
        # angle = arctan(500/10126.9) ≈ 2.83°
        assert result['climb_angle'] == pytest.approx(2.83, rel=0.1)


# ============================================================================
# TOP OF CLIMB (TOC) TESTS - BY TIME
# ============================================================================

class TestTOCByTime:
    """Test suite for TOC calculations with known time"""
    
    def test_basic_climb_by_time(self):
        """Test climb calculation with available time"""
        result = calculate_toc_by_time(
            current_altitude=2000,
            target_altitude=10000,
            available_time=10.0,
            ground_speed=120
        )
        
        assert result['altitude_gain'] == 8000
        assert result['required_climb_rate'] == pytest.approx(800, rel=0.01)
        assert result['climb_distance'] == pytest.approx(20.0, rel=0.1)
        assert result['is_realistic'] == True
        assert "High-Performance" in result['aircraft_category']
    
    def test_light_ga_category(self):
        """Test that light GA category is identified correctly"""
        result = calculate_toc_by_time(
            current_altitude=1000,
            target_altitude=5000,
            available_time=8.0,
            ground_speed=100
        )
        
        # Required rate: 4000 ft / 8 min = 500 ft/min
        assert result['required_climb_rate'] == pytest.approx(500, rel=0.01)
        assert "Light GA" in result['aircraft_category']
        assert result['is_realistic'] == True
    
    def test_jet_category(self):
        """Test that jet category is identified correctly"""
        result = calculate_toc_by_time(
            current_altitude=5000,
            target_altitude=35000,
            available_time=12.0,
            ground_speed=250
        )
        
        # Required rate: 30000 ft / 12 min = 2500 ft/min
        assert result['required_climb_rate'] == pytest.approx(2500, rel=0.01)
        assert "Jet" in result['aircraft_category'] or "Airliner" in result['aircraft_category']
        assert result['is_realistic'] == True
    
    def test_unrealistic_time_constraint(self):
        """Test unrealistic time constraint"""
        result = calculate_toc_by_time(
            current_altitude=0,
            target_altitude=20000,
            available_time=2.0,
            ground_speed=150
        )
        
        # Required rate: 20000 ft / 2 min = 10000 ft/min
        assert result['required_climb_rate'] == pytest.approx(10000, rel=0.01)
        assert result['is_realistic'] == False
        assert "Military" in result['aircraft_category'] or "Unrealistic" in result['aircraft_category']
    
    def test_zero_time(self):
        """Test with zero time (should handle gracefully)"""
        result = calculate_toc_by_time(
            current_altitude=1000,
            target_altitude=5000,
            available_time=0,
            ground_speed=120
        )
        
        assert result['required_climb_rate'] == float('inf')
        assert result['is_realistic'] == False
    
    def test_no_climb_needed_by_time(self):
        """Test when already at or above target altitude"""
        result = calculate_toc_by_time(
            current_altitude=10000,
            target_altitude=5000,
            available_time=10.0,
            ground_speed=120
        )
        
        assert result['altitude_gain'] == 0
        assert result['required_climb_rate'] == 0
        assert result['aircraft_category'] == "N/A"


# ============================================================================
# TOC RULE OF THUMB TESTS
# ============================================================================

class TestTOCRuleOfThumb:
    """Test suite for TOC rule of thumb calculations"""
    
    def test_rule_of_thumb_toc_default(self):
        """Test TOC rule of thumb with default climb rate"""
        distance = calculate_rule_of_thumb_toc(9000)
        assert distance == pytest.approx(30.0, rel=0.01)
    
    def test_rule_of_thumb_toc_custom_rate(self):
        """Test TOC rule of thumb with custom climb rate"""
        # At 1000 ft/min, should be half the distance of 500 ft/min
        distance = calculate_rule_of_thumb_toc(9000, climb_rate=1000)
        assert distance == pytest.approx(30.0, rel=0.01)


# ============================================================================
# WIND CORRECTION TESTS
# ============================================================================

class TestWindCorrection:
    """Test suite for wind correction calculations"""
    
    def test_direct_headwind(self):
        """Test with direct headwind"""
        result = calculate_wind_correction(
            true_airspeed=120,
            true_course=360,  # North
            wind_direction=360,  # From north
            wind_speed=20
        )
        
        assert result['wind_correction_angle'] == pytest.approx(0, abs=0.1)
        assert result['ground_speed'] == pytest.approx(100, rel=0.1)
    
    def test_direct_tailwind(self):
        """Test with direct tailwind"""
        result = calculate_wind_correction(
            true_airspeed=120,
            true_course=360,  # North
            wind_direction=180,  # From south
            wind_speed=20
        )
        
        assert result['wind_correction_angle'] == pytest.approx(0, abs=0.1)
        assert result['ground_speed'] == pytest.approx(140, rel=0.1)
    
    def test_crosswind_from_right(self):
        """Test with crosswind from right"""
        result = calculate_wind_correction(
            true_airspeed=120,
            true_course=360,  # North
            wind_direction=90,  # From east (wind from right)
            wind_speed=20
        )
        
        # Wind from right pushes aircraft left, so we must correct right (positive WCA)
        assert result['wind_correction_angle'] > 0
        assert result['crosswind_component'] == pytest.approx(20, rel=0.1)


# ============================================================================
# COURSE CONVERSION TESTS
# ============================================================================

class TestCourseConversion:
    """Test suite for True/Magnetic course conversion"""
    
    def test_true_to_magnetic_east_variation(self):
        """Test True to Magnetic with East variation"""
        # East is Least: subtract from True
        result = convert_course(120, 5, from_true=True)
        assert result == pytest.approx(115, abs=0.1)
    
    def test_true_to_magnetic_west_variation(self):
        """Test True to Magnetic with West variation"""
        # West is Best: add to Magnetic (subtract negative)
        result = convert_course(120, -5, from_true=True)
        assert result == pytest.approx(125, abs=0.1)
    
    def test_magnetic_to_true_east_variation(self):
        """Test Magnetic to True with East variation"""
        result = convert_course(115, 5, from_true=False)
        assert result == pytest.approx(120, abs=0.1)


# ============================================================================
# UNIT CONVERSION TESTS
# ============================================================================

class TestAltitudeConversion:
    """Test suite for altitude/length unit conversions"""
    
    def test_feet_to_meters(self):
        """Test feet to meters conversion"""
        result = convert_altitude(10000, 'feet', 'meters')
        assert result == pytest.approx(3048.0, rel=0.01)
    
    def test_meters_to_feet(self):
        """Test meters to feet conversion"""
        result = convert_altitude(3048, 'meters', 'feet')
        assert result == pytest.approx(10000.0, rel=0.01)
    
    def test_feet_to_kilometers(self):
        """Test feet to kilometers conversion"""
        result = convert_altitude(10000, 'feet', 'kilometers')
        assert result == pytest.approx(3.048, rel=0.01)
    
    def test_same_unit_returns_same_value(self):
        """Test that converting to same unit returns original value"""
        result = convert_altitude(5000, 'feet', 'feet')
        assert result == 5000.0
    
    def test_invalid_unit_raises_error(self):
        """Test that invalid units raise ValueError"""
        with pytest.raises(ValueError):
            convert_altitude(1000, 'feet', 'miles')


class TestDistanceConversion:
    """Test suite for distance unit conversions"""
    
    def test_nm_to_km(self):
        """Test nautical miles to kilometers conversion"""
        result = convert_distance(100, 'nm', 'km')
        assert result == pytest.approx(185.2, rel=0.01)
    
    def test_km_to_nm(self):
        """Test kilometers to nautical miles conversion"""
        result = convert_distance(185.2, 'km', 'nm')
        assert result == pytest.approx(100.0, rel=0.01)
    
    def test_nm_to_miles(self):
        """Test nautical miles to statute miles conversion"""
        result = convert_distance(100, 'nm', 'miles')
        assert result == pytest.approx(115.078, rel=0.01)
    
    def test_miles_to_nm(self):
        """Test statute miles to nautical miles conversion"""
        result = convert_distance(115.078, 'miles', 'nm')
        assert result == pytest.approx(100.0, rel=0.01)
    
    def test_same_unit_returns_same_value(self):
        """Test that converting to same unit returns original value"""
        result = convert_distance(50, 'nm', 'nm')
        assert result == 50.0
    
    def test_invalid_unit_raises_error(self):
        """Test that invalid units raise ValueError"""
        with pytest.raises(ValueError):
            convert_distance(100, 'nm', 'feet')


class TestWeightConversion:
    """Test suite for weight/mass unit conversions"""
    
    def test_kg_to_lbs(self):
        """Test kilograms to pounds conversion"""
        result = convert_weight(1000, 'kg', 'lbs')
        assert result == pytest.approx(2204.62, rel=0.01)
    
    def test_lbs_to_kg(self):
        """Test pounds to kilograms conversion"""
        result = convert_weight(2204.62, 'lbs', 'kg')
        assert result == pytest.approx(1000.0, rel=0.01)
    
    def test_kg_to_tons(self):
        """Test kilograms to metric tons conversion"""
        result = convert_weight(1000, 'kg', 'tons')
        assert result == pytest.approx(1.0, rel=0.01)
    
    def test_tons_to_kg(self):
        """Test metric tons to kilograms conversion"""
        result = convert_weight(1, 'tons', 'kg')
        assert result == pytest.approx(1000.0, rel=0.01)
    
    def test_same_unit_returns_same_value(self):
        """Test that converting to same unit returns original value"""
        result = convert_weight(500, 'kg', 'kg')
        assert result == 500.0
    
    def test_invalid_unit_raises_error(self):
        """Test that invalid units raise ValueError"""
        with pytest.raises(ValueError):
            convert_weight(1000, 'kg', 'ounces')


class TestFuelVolumeConversion:
    """Test suite for fuel volume unit conversions"""
    
    def test_liters_to_us_gal(self):
        """Test liters to US gallons conversion"""
        result = convert_fuel_volume(100, 'liters', 'us_gal')
        assert result == pytest.approx(26.4172, rel=0.01)
    
    def test_us_gal_to_liters(self):
        """Test US gallons to liters conversion"""
        result = convert_fuel_volume(26.4172, 'us_gal', 'liters')
        assert result == pytest.approx(100.0, rel=0.01)
    
    def test_liters_to_imp_gal(self):
        """Test liters to Imperial gallons conversion"""
        result = convert_fuel_volume(100, 'liters', 'imp_gal')
        assert result == pytest.approx(21.9969, rel=0.01)
    
    def test_imp_gal_to_liters(self):
        """Test Imperial gallons to liters conversion"""
        result = convert_fuel_volume(21.9969, 'imp_gal', 'liters')
        assert result == pytest.approx(100.0, rel=0.01)
    
    def test_us_gal_to_imp_gal(self):
        """Test US gallons to Imperial gallons conversion"""
        result = convert_fuel_volume(10, 'us_gal', 'imp_gal')
        assert result == pytest.approx(8.32674, rel=0.01)
    
    def test_same_unit_returns_same_value(self):
        """Test that converting to same unit returns original value"""
        result = convert_fuel_volume(50, 'liters', 'liters')
        assert result == 50.0
    
    def test_invalid_unit_raises_error(self):
        """Test that invalid units raise ValueError"""
        with pytest.raises(ValueError):
            convert_fuel_volume(100, 'liters', 'barrels')


# ============================================================================
# E6B FLIGHT COMPUTER TESTS
# ============================================================================

class TestTrueAirspeed:
    """Test suite for True Airspeed calculations"""
    
    def test_basic_tas_calculation(self):
        """Test basic TAS calculation with 2% rule"""
        result = calculate_true_airspeed(
            indicated_airspeed=120,
            pressure_altitude=5000
        )
        
        # At 5000 ft, expect ~10% increase (2% per 1000 ft)
        assert result['tas'] == pytest.approx(132, rel=0.01)
        assert result['correction_percent'] == pytest.approx(10.0, abs=0.1)
        assert result['isa_deviation'] is None
    
    def test_tas_with_temperature(self):
        """Test TAS calculation with temperature correction"""
        result = calculate_true_airspeed(
            indicated_airspeed=120,
            pressure_altitude=5000,
            temperature_c=15  # Warm day
        )
        
        assert result['tas'] > 120  # Should be higher than IAS
        assert result['isa_deviation'] is not None
    
    def test_tas_at_sea_level(self):
        """Test TAS at sea level (should equal IAS)"""
        result = calculate_true_airspeed(
            indicated_airspeed=100,
            pressure_altitude=0
        )
        
        assert result['tas'] == pytest.approx(100, rel=0.01)
        assert result['correction_percent'] == pytest.approx(0, abs=0.1)


class TestDensityAltitude:
    """Test suite for Density Altitude calculations"""
    
    def test_standard_conditions(self):
        """Test density altitude at standard conditions"""
        result = calculate_density_altitude(
            pressure_altitude=0,
            temperature_c=15,
            altimeter_setting=29.92
        )
        
        # At standard conditions, density altitude ≈ pressure altitude
        assert result['density_altitude'] == pytest.approx(0, abs=100)
        assert result['isa_deviation'] == pytest.approx(0, abs=0.5)
    
    def test_hot_day(self):
        """Test density altitude on a hot day"""
        result = calculate_density_altitude(
            pressure_altitude=1000,
            temperature_c=35,  # Hot day
            altimeter_setting=29.92
        )
        
        # Hot day means higher density altitude
        assert result['density_altitude'] > result['pressure_altitude']
        assert result['isa_deviation'] > 0
    
    def test_cold_day(self):
        """Test density altitude on a cold day"""
        result = calculate_density_altitude(
            pressure_altitude=1000,
            temperature_c=-10,  # Cold day
            altimeter_setting=29.92
        )
        
        # Cold day means lower density altitude
        assert result['density_altitude'] < result['pressure_altitude']
        assert result['isa_deviation'] < 0
    
    def test_high_pressure(self):
        """Test density altitude with high pressure"""
        result = calculate_density_altitude(
            pressure_altitude=1000,
            temperature_c=15,
            altimeter_setting=30.50  # High pressure
        )
        
        # High pressure lowers pressure altitude
        assert result['pressure_altitude'] < 1000


class TestFuelCalculations:
    """Test suite for fuel planning calculations"""
    
    def test_fuel_required_by_distance(self):
        """Test fuel required for a given distance"""
        result = calculate_fuel_required(
            distance=150,
            fuel_flow=10,
            ground_speed=120,
            reserve_time=45
        )
        
        # 150 NM at 120 kts = 1.25 hours = 12.5 gal
        assert result['fuel_required'] == pytest.approx(12.5, rel=0.01)
        # 45 min reserve = 0.75 hours = 7.5 gal
        assert result['fuel_reserve'] == pytest.approx(7.5, rel=0.01)
        # Total = 20 gal
        assert result['total_fuel'] == pytest.approx(20.0, rel=0.01)
    
    def test_fuel_required_by_time(self):
        """Test fuel required for a given time"""
        result = calculate_fuel_required(
            time_hours=2.0,
            fuel_flow=12,
            reserve_time=30
        )
        
        # 2 hours at 12 gph = 24 gal
        assert result['fuel_required'] == pytest.approx(24.0, rel=0.01)
        # 30 min reserve = 6 gal
        assert result['fuel_reserve'] == pytest.approx(6.0, rel=0.01)
    
    def test_fuel_without_reserve(self):
        """Test fuel calculation without reserve"""
        result = calculate_fuel_required(
            time_hours=1.0,
            fuel_flow=10,
            include_reserve=False
        )
        
        assert result['fuel_required'] == 10.0
        assert result['fuel_reserve'] == 0.0
        assert result['total_fuel'] == 10.0
    
    def test_invalid_parameters(self):
        """Test error handling for invalid parameters"""
        with pytest.raises(ValueError):
            calculate_fuel_required(fuel_flow=10)  # No distance or time


class TestEnduranceAndRange:
    """Test suite for endurance and range calculations"""
    
    def test_basic_endurance_range(self):
        """Test basic endurance and range calculation"""
        result = calculate_endurance_and_range(
            fuel_available=50,
            fuel_flow=10,
            ground_speed=120
        )
        
        # 50 gal at 10 gph = 5 hours
        assert result['endurance'] == pytest.approx(5.0, rel=0.01)
        # 5 hours at 120 kts = 600 NM
        assert result['range'] == pytest.approx(600, rel=0.01)
    
    def test_with_reserve(self):
        """Test endurance and range with 45-min reserve"""
        result = calculate_endurance_and_range(
            fuel_available=50,
            fuel_flow=10,
            ground_speed=120
        )
        
        # Reserve = 45/60 * 10 = 7.5 gal
        assert result['reserve_fuel'] == pytest.approx(7.5, rel=0.01)
        # Usable = 50 - 7.5 = 42.5 gal = 4.25 hours
        assert result['endurance_with_reserve'] == pytest.approx(4.25, rel=0.01)
        # Range = 4.25 * 120 = 510 NM
        assert result['range_with_reserve'] == pytest.approx(510, rel=0.01)
    
    def test_zero_fuel_flow(self):
        """Test error handling for zero fuel flow"""
        with pytest.raises(ValueError):
            calculate_endurance_and_range(50, 0, 120)
    
    def test_vfr_reserve(self):
        """Test endurance and range with 30-min VFR reserve"""
        result = calculate_endurance_and_range(
            fuel_available=50,
            fuel_flow=10,
            ground_speed=120,
            reserve_time=30
        )
        
        # Reserve = 30/60 * 10 = 5.0 gal
        assert result['reserve_fuel'] == pytest.approx(5.0, rel=0.01)
        assert result['reserve_time'] == 30
        # Usable = 50 - 5.0 = 45 gal = 4.5 hours
        assert result['endurance_with_reserve'] == pytest.approx(4.5, rel=0.01)
        # Range = 4.5 * 120 = 540 NM
        assert result['range_with_reserve'] == pytest.approx(540, rel=0.01)
    
    def test_ifr_reserve(self):
        """Test endurance and range with 45-min IFR reserve"""
        result = calculate_endurance_and_range(
            fuel_available=50,
            fuel_flow=10,
            ground_speed=120,
            reserve_time=45
        )
        
        # Reserve = 45/60 * 10 = 7.5 gal
        assert result['reserve_fuel'] == pytest.approx(7.5, rel=0.01)
        assert result['reserve_time'] == 45
        # Usable = 50 - 7.5 = 42.5 gal = 4.25 hours
        assert result['endurance_with_reserve'] == pytest.approx(4.25, rel=0.01)
        # Range = 4.25 * 120 = 510 NM
        assert result['range_with_reserve'] == pytest.approx(510, rel=0.01)


class TestWindComponents:
    """Test suite for runway wind component calculations"""
    
    def test_direct_headwind(self):
        """Test direct headwind (wind aligned with runway)"""
        result = calculate_wind_components(
            runway_heading=270,  # Runway 27
            wind_direction=270,  # Wind from west
            wind_speed=20
        )
        
        assert result['headwind_component'] == pytest.approx(20, rel=0.01)
        assert result['crosswind_component'] == pytest.approx(0, abs=0.1)
        assert result['angle_difference'] == pytest.approx(0, abs=0.1)
    
    def test_direct_tailwind(self):
        """Test direct tailwind"""
        result = calculate_wind_components(
            runway_heading=270,  # Runway 27
            wind_direction=90,   # Wind from east (tailwind)
            wind_speed=15
        )
        
        assert result['headwind_component'] == pytest.approx(-15, rel=0.01)
        assert result['crosswind_component'] == pytest.approx(0, abs=0.1)
    
    def test_90_degree_crosswind(self):
        """Test 90-degree crosswind (pure crosswind)"""
        result = calculate_wind_components(
            runway_heading=270,  # Runway 27
            wind_direction=360,  # Wind from north
            wind_speed=20
        )
        
        assert result['headwind_component'] == pytest.approx(0, abs=0.1)
        assert result['crosswind_component'] == pytest.approx(20, rel=0.01)
        assert result['crosswind_direction'] in ['left', 'right']
    
    def test_45_degree_wind(self):
        """Test wind at 45 degrees"""
        result = calculate_wind_components(
            runway_heading=270,  # Runway 27
            wind_direction=315,  # Wind from NW (45 degrees)
            wind_speed=20
        )
        
        # At 45 degrees, headwind and crosswind are roughly equal
        # Component ≈ 20 * cos(45°) ≈ 14.14
        assert result['headwind_component'] == pytest.approx(14.14, rel=0.05)
        assert result['crosswind_component'] == pytest.approx(14.14, rel=0.05)


# ============================================================================
# WEIGHT & BALANCE TESTS
# ============================================================================

class TestWeightAndBalance:
    """Test suite for Weight & Balance calculations"""
    
    def test_cessna_172_basic_loading(self):
        """Test basic W&B calculation for Cessna 172S"""
        # Basic loading: 2 people (340 lbs), half fuel
        result = calculate_weight_and_balance(
            aircraft_name="Cessna 172S Skyhawk",
            fuel_gallons=28.0,  # Half tanks
            station_weights={
                "front_seats": 340.0,
                "rear_seats": 0.0,
                "baggage_area_1": 0.0,
                "baggage_area_2": 0.0
            }
        )
        
        # Check calculations
        fuel_weight = 28.0 * 6.0  # 168 lbs
        expected_weight = 1680 + 168 + 340  # Empty + fuel + pax
        
        assert result['total_weight'] == pytest.approx(expected_weight, rel=0.01)
        assert result['weight_status'] == "OK"
        assert result['cg_status'] in ["OK", "FORWARD OF LIMITS", "AFT OF LIMITS"]
    
    def test_cessna_172_max_loading(self):
        """Test Cessna 172S at maximum weight"""
        # Full fuel, 4 people, baggage
        result = calculate_weight_and_balance(
            aircraft_name="Cessna 172S Skyhawk",
            fuel_gallons=56.0,  # Full tanks
            station_weights={
                "front_seats": 340.0,
                "rear_seats": 340.0,
                "baggage_area_1": 100.0,
                "baggage_area_2": 50.0
            }
        )
        
        # This should exceed max weight
        assert result['total_weight'] > result['max_takeoff_weight']
        assert result['weight_status'] != "OK"
    
    def test_cessna_208_basic_loading(self):
        """Test basic W&B calculation for Cessna 208B Grand Caravan"""
        result = calculate_weight_and_balance(
            aircraft_name="Cessna 208B Grand Caravan",
            fuel_gallons=200.0,
            station_weights={
                "pilot_seat": 180.0,
                "copilot_seat": 180.0,
                "passenger_row_1": 0.0,
                "passenger_row_2": 0.0,
                "passenger_row_3": 0.0,
                "passenger_row_4": 0.0,
                "cargo_pod": 0.0
            }
        )
        
        # Basic sanity checks
        assert result['total_weight'] > 4730  # Empty weight
        assert result['weight_status'] == "OK"  # Should be within limits
    
    def test_cg_within_envelope(self):
        """Test CG calculation is within envelope for normal loading"""
        # Standard loading that should be well within envelope
        result = calculate_weight_and_balance(
            aircraft_name="Cessna 172S Skyhawk",
            fuel_gallons=40.0,
            station_weights={
                "front_seats": 300.0,
                "rear_seats": 200.0,
                "baggage_area_1": 50.0,
                "baggage_area_2": 0.0
            }
        )
        
        # CG should be within limits for this normal loading
        assert result['cg_position'] > 0
        assert result['forward_limit'] is not None
        assert result['aft_limit'] is not None
        
        if result['within_envelope']:
            assert result['cg_position'] >= result['forward_limit']
            assert result['cg_position'] <= result['aft_limit']
    
    def test_cg_calculation_formula(self):
        """Test that CG is calculated correctly (moment/weight)"""
        result = calculate_weight_and_balance(
            aircraft_name="Cessna 172S Skyhawk",
            fuel_gallons=30.0,
            station_weights={
                "front_seats": 340.0,
                "rear_seats": 0.0,
                "baggage_area_1": 0.0,
                "baggage_area_2": 0.0
            }
        )
        
        # CG = Total Moment / Total Weight
        calculated_cg = result['total_moment'] / result['total_weight']
        assert result['cg_position'] == pytest.approx(calculated_cg, rel=0.001)
    
    def test_empty_aircraft(self):
        """Test calculation with just empty aircraft (no fuel, no pax)"""
        result = calculate_weight_and_balance(
            aircraft_name="Cessna 172S Skyhawk",
            fuel_gallons=0.0,
            station_weights={
                "front_seats": 0.0,
                "rear_seats": 0.0,
                "baggage_area_1": 0.0,
                "baggage_area_2": 0.0
            }
        )
        
        # Should equal empty weight and CG
        aircraft_data = {
            "Cessna 172S Skyhawk": {"empty_weight": 1680, "empty_arm": 39.5}
        }
        
        assert result['total_weight'] == 1680  # Empty weight from database
        assert result['weight_status'] == "OK"
    
    def test_invalid_aircraft_raises_error(self):
        """Test that invalid aircraft name raises KeyError"""
        with pytest.raises(KeyError):
            calculate_weight_and_balance(
                aircraft_name="Boeing 747",  # Not in database
                fuel_gallons=100.0,
                station_weights={}
            )
    
    def test_invalid_station_raises_error(self):
        """Test that invalid station name raises ValueError"""
        with pytest.raises(ValueError):
            calculate_weight_and_balance(
                aircraft_name="Cessna 172S Skyhawk",
                fuel_gallons=30.0,
                station_weights={
                    "invalid_station": 200.0  # Not a valid station
                }
            )


class TestStationWeightValidation:
    """Test suite for station weight validation"""
    
    def test_valid_weights(self):
        """Test validation with all weights within limits"""
        result = validate_station_weights(
            aircraft_name="Cessna 172S Skyhawk",
            fuel_gallons=40.0,
            station_weights={
                "front_seats": 300.0,
                "rear_seats": 300.0,
                "baggage_area_1": 80.0,
                "baggage_area_2": 50.0
            }
        )
        
        assert len(result['errors']) == 0
        # May have warnings if approaching limits
    
    def test_fuel_capacity_exceeded(self):
        """Test fuel over capacity triggers error"""
        result = validate_station_weights(
            aircraft_name="Cessna 172S Skyhawk",
            fuel_gallons=100.0,  # Way over 56 gal capacity
            station_weights={
                "front_seats": 300.0,
                "rear_seats": 0.0,
                "baggage_area_1": 0.0,
                "baggage_area_2": 0.0
            }
        )
        
        assert len(result['errors']) > 0
        assert any("Fuel" in error for error in result['errors'])
    
    def test_station_weight_exceeded(self):
        """Test station over max weight triggers error"""
        result = validate_station_weights(
            aircraft_name="Cessna 172S Skyhawk",
            fuel_gallons=40.0,
            station_weights={
                "front_seats": 500.0,  # Over 400 lbs max
                "rear_seats": 0.0,
                "baggage_area_1": 0.0,
                "baggage_area_2": 0.0
            }
        )
        
        assert len(result['errors']) > 0
        assert any("Front Seats" in error for error in result['errors'])
    
    def test_warning_approaching_limit(self):
        """Test warning when approaching station limit (>90%)"""
        result = validate_station_weights(
            aircraft_name="Cessna 172S Skyhawk",
            fuel_gallons=40.0,
            station_weights={
                "front_seats": 380.0,  # 95% of 400 lbs max
                "rear_seats": 0.0,
                "baggage_area_1": 0.0,
                "baggage_area_2": 0.0
            }
        )
        
        # Should have a warning (but no error)
        assert len(result['warnings']) > 0
        assert any("Front Seats" in warning for warning in result['warnings'])


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
