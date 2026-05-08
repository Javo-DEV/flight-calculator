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
    convert_fuel_volume
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
            wind_direction=90,  # From east
            wind_speed=20
        )
        
        # Should correct left (negative WCA)
        assert result['wind_correction_angle'] < 0
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
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
