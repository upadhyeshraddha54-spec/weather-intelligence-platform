"""
Unit tests for the Geospatial module.
All tests are offline — static coordinate table is used, no network required.
"""
import os
import sys
import math
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.geospatial.geo_utils import (
    get_city_coordinates,
    bounding_box,
    haversine_distance,
    classify_monsoon_zone,
    location_to_geojson,
    get_location_summary,
    CITY_COORDS,
)


class TestGetCityCoordinates:
    def test_pune_known(self):
        coords = get_city_coordinates("Pune")
        assert coords is not None
        assert abs(coords["latitude"] - 18.5204) < 0.01
        assert abs(coords["longitude"] - 73.8567) < 0.01

    def test_mumbai_known(self):
        coords = get_city_coordinates("mumbai")
        assert coords is not None
        assert coords["latitude"] is not None

    def test_case_insensitive(self):
        c1 = get_city_coordinates("PUNE")
        c2 = get_city_coordinates("pune")
        assert c1 is not None
        assert c2 is not None
        assert abs(c1["latitude"] - c2["latitude"]) < 0.001

    def test_all_static_cities_have_lat_lon(self):
        for city in CITY_COORDS:
            c = get_city_coordinates(city)
            assert c is not None, f"No coords for {city}"
            assert isinstance(c["latitude"], float)
            assert isinstance(c["longitude"], float)


class TestBoundingBox:
    def test_returns_four_values(self):
        bbox = bounding_box(18.52, 73.86, radius_km=50)
        assert len(bbox) == 4

    def test_west_less_than_east(self):
        w, s, e, n = bounding_box(18.52, 73.86, radius_km=50)
        assert w < e

    def test_south_less_than_north(self):
        w, s, e, n = bounding_box(18.52, 73.86, radius_km=50)
        assert s < n

    def test_centre_is_inside_bbox(self):
        lat, lon = 18.52, 73.86
        w, s, e, n = bounding_box(lat, lon, radius_km=50)
        assert w < lon < e
        assert s < lat < n

    def test_larger_radius_gives_bigger_box(self):
        w1, s1, e1, n1 = bounding_box(18.52, 73.86, radius_km=10)
        w2, s2, e2, n2 = bounding_box(18.52, 73.86, radius_km=100)
        assert (e2 - w2) > (e1 - w1)


class TestHaversineDistance:
    def test_same_point_zero(self):
        d = haversine_distance(18.52, 73.86, 18.52, 73.86)
        assert d == pytest.approx(0.0, abs=0.001)

    def test_pune_to_mumbai_approx(self):
        # Approximate straight-line ~119 km
        d = haversine_distance(18.5204, 73.8567, 19.0760, 72.8777)
        assert 110 < d < 135

    def test_symmetry(self):
        d1 = haversine_distance(18.52, 73.86, 19.07, 72.88)
        d2 = haversine_distance(19.07, 72.88, 18.52, 73.86)
        assert abs(d1 - d2) < 0.001

    def test_positive_distance(self):
        d = haversine_distance(0, 0, 1, 1)
        assert d > 0


class TestClassifyMonsoonZone:
    def test_pune_is_moderate(self):
        result = classify_monsoon_zone(18.5204, 73.8567)
        assert "Moderate" in result["zone"]

    def test_mumbai_is_heavy_or_moderate(self):
        result = classify_monsoon_zone(19.0760, 72.8777)
        assert result["zone"] in (
            "Heavy Monsoon Zone", "Moderate Monsoon Zone"
        )

    def test_delhi_has_zone(self):
        result = classify_monsoon_zone(28.6139, 77.2090)
        assert "zone" in result
        assert "description" in result

    def test_outside_india_returns_outside(self):
        # Coordinates in Europe
        result = classify_monsoon_zone(51.5, 0.1)
        assert "Outside" in result["zone"]

    def test_result_has_description(self):
        result = classify_monsoon_zone(18.52, 73.86)
        assert len(result["description"]) > 0


class TestLocationToGeoJSON:
    def test_valid_feature(self):
        feat = location_to_geojson("Pune", 18.52, 73.86)
        assert feat["type"] == "Feature"
        assert feat["geometry"]["type"] == "Point"
        assert feat["geometry"]["coordinates"] == [73.86, 18.52]
        assert feat["properties"]["city"] == "Pune"

    def test_coordinates_order_lon_lat(self):
        """GeoJSON coordinates are [longitude, latitude]."""
        feat = location_to_geojson("Test", 10.0, 20.0)
        assert feat["geometry"]["coordinates"][0] == 20.0  # lon
        assert feat["geometry"]["coordinates"][1] == 10.0  # lat

    def test_extra_properties(self):
        feat = location_to_geojson("Pune", 18.52, 73.86, {"aqi": 42})
        assert feat["properties"]["aqi"] == 42


class TestGetLocationSummary:
    def test_pune_full_summary(self):
        result = get_location_summary("Pune")
        assert result["status"] == "ok"
        assert result["latitude"] is not None
        assert result["longitude"] is not None
        assert result["monsoon_zone"] is not None
        assert result["bounding_box_50km"] is not None
        assert result["geojson"] is not None

    def test_geojson_is_valid_feature(self):
        result = get_location_summary("Pune")
        gj = result["geojson"]
        assert gj["type"] == "Feature"

    def test_bounding_box_keys(self):
        result = get_location_summary("Pune")
        bbox = result["bounding_box_50km"]
        for k in ("west", "south", "east", "north"):
            assert k in bbox

    def test_unknown_city_returns_unavailable_or_geocoded(self):
        result = get_location_summary("xyznonexistentcity12345")
        assert result["status"] in ("ok", "unavailable")
