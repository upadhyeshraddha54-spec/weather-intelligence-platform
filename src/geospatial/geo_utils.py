"""
Geospatial utilities for the Weather Intelligence Platform.

Provides:
- City → coordinates lookup (static table for key Indian cities + geocoding fallback)
- Bounding-box generation around a point
- Haversine distance calculation
- Monsoon region classification
- GeoJSON-compatible location dict for map rendering

Data truthfulness
-----------------
All coordinates come from public geocoding (Open-Meteo) or the bundled
static table which uses publicly-available WGS-84 coordinates.
No coordinates are fabricated.
"""
import logging
import math
from typing import Optional, Tuple, Dict, Any

import requests

logger = logging.getLogger(__name__)
GEOCODING_TIMEOUT = 8  # seconds

# ---------------------------------------------------------------------------
# Static coordinate table (WGS-84)
# Source: public geographic databases
# ---------------------------------------------------------------------------

CITY_COORDS: Dict[str, Dict[str, Any]] = {
    "pune": {
        "latitude": 18.5204, "longitude": 73.8567,
        "state": "Maharashtra", "country": "India",
    },
    "mumbai": {
        "latitude": 19.0760, "longitude": 72.8777,
        "state": "Maharashtra", "country": "India",
    },
    "nagpur": {
        "latitude": 21.1458, "longitude": 79.0882,
        "state": "Maharashtra", "country": "India",
    },
    "nashik": {
        "latitude": 19.9975, "longitude": 73.7898,
        "state": "Maharashtra", "country": "India",
    },
    "delhi": {
        "latitude": 28.6139, "longitude": 77.2090,
        "state": "Delhi", "country": "India",
    },
    "bengaluru": {
        "latitude": 12.9716, "longitude": 77.5946,
        "state": "Karnataka", "country": "India",
    },
    "chennai": {
        "latitude": 13.0827, "longitude": 80.2707,
        "state": "Tamil Nadu", "country": "India",
    },
    "hyderabad": {
        "latitude": 17.3850, "longitude": 78.4867,
        "state": "Telangana", "country": "India",
    },
    "kolkata": {
        "latitude": 22.5726, "longitude": 88.3639,
        "state": "West Bengal", "country": "India",
    },
    "ahmedabad": {
        "latitude": 23.0225, "longitude": 72.5714,
        "state": "Gujarat", "country": "India",
    },
    "jaipur": {
        "latitude": 26.9124, "longitude": 75.7873,
        "state": "Rajasthan", "country": "India",
    },
    "bhopal": {
        "latitude": 23.2599, "longitude": 77.4126,
        "state": "Madhya Pradesh", "country": "India",
    },
    "patna": {
        "latitude": 25.5941, "longitude": 85.1376,
        "state": "Bihar", "country": "India",
    },
    "bhubaneswar": {
        "latitude": 20.2961, "longitude": 85.8245,
        "state": "Odisha", "country": "India",
    },
    "thiruvananthapuram": {
        "latitude": 8.5241, "longitude": 76.9366,
        "state": "Kerala", "country": "India",
    },
    "guwahati": {
        "latitude": 26.1445, "longitude": 91.7362,
        "state": "Assam", "country": "India",
    },
}

# ---------------------------------------------------------------------------
# Southwest Monsoon zone classification
# Reference: IMD monsoon classification criteria
# ---------------------------------------------------------------------------

MONSOON_ZONES = {
    "Heavy Monsoon Zone": {
        "lat_range": (8, 18), "lon_range": (73, 82),
        "description": "West coast and Deccan — core Southwest Monsoon belt",
    },
    "Moderate Monsoon Zone": {
        "lat_range": (18, 26), "lon_range": (70, 88),
        "description": "Central India — active monsoon with variability",
    },
    "Weak Monsoon Zone": {
        "lat_range": (26, 35), "lon_range": (68, 78),
        "description": "Northwest India — weak/late monsoon influence",
    },
    "Northeast Monsoon Zone": {
        "lat_range": (8, 16), "lon_range": (78, 88),
        "description": "Tamil Nadu coast — Northeast Monsoon dominant",
    },
}


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def get_city_coordinates(city: str) -> Optional[Dict[str, Any]]:
    """
    Return coordinates for a city.

    Checks the static table first (fast, offline).
    Falls back to Open-Meteo geocoding API if not found.

    Returns:
        dict with latitude, longitude, name/city, state, country  or  None
    """
    key = city.strip().lower()

    if key in CITY_COORDS:
        result = dict(CITY_COORDS[key])
        result["city"] = city.title()
        return result

    # Geocoding fallback
    try:
        resp = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=GEOCODING_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.warning("Geocoding fallback failed for '%s': %s", city, exc)
        return None

    if not data.get("results"):
        return None

    loc = data["results"][0]
    return {
        "city": loc.get("name", city),
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
        "state": loc.get("admin1", ""),
        "country": loc.get("country", ""),
    }


def bounding_box(
    latitude: float,
    longitude: float,
    radius_km: float = 50.0,
) -> Tuple[float, float, float, float]:
    """
    Return a bounding box (west, south, east, north) around a point.

    Args:
        latitude:   Centre latitude (degrees)
        longitude:  Centre longitude (degrees)
        radius_km:  Approximate radius in km

    Returns:
        (west, south, east, north) in WGS-84 degrees
    """
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * math.cos(math.radians(latitude)))

    return (
        round(longitude - lon_delta, 4),  # west
        round(latitude  - lat_delta, 4),  # south
        round(longitude + lon_delta, 4),  # east
        round(latitude  + lat_delta, 4),  # north
    )


def haversine_distance(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
) -> float:
    """
    Calculate the great-circle distance (km) between two coordinates.

    Args:
        lat1, lon1: First point (degrees)
        lat2, lon2: Second point (degrees)

    Returns:
        Distance in kilometres.
    """
    R = 6371.0  # Earth radius km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def classify_monsoon_zone(latitude: float, longitude: float) -> Dict[str, str]:
    """
    Classify a coordinate into its Indian Southwest Monsoon zone.

    Returns:
        dict with ``zone`` and ``description``, or "Unknown Zone" if outside table.
    """
    for zone_name, zone in MONSOON_ZONES.items():
        lat_lo, lat_hi = zone["lat_range"]
        lon_lo, lon_hi = zone["lon_range"]
        if lat_lo <= latitude <= lat_hi and lon_lo <= longitude <= lon_hi:
            return {"zone": zone_name, "description": zone["description"]}

    return {
        "zone": "Outside Indian Monsoon Region",
        "description": "Coordinates are outside the classified Indian monsoon zones.",
    }


def location_to_geojson(
    city: str,
    latitude: float,
    longitude: float,
    properties: Optional[Dict] = None,
) -> Dict:
    """
    Return a GeoJSON-compatible Point feature dict for map rendering.

    Args:
        city:       City name (label)
        latitude:   WGS-84 latitude
        longitude:  WGS-84 longitude
        properties: Optional additional properties to include

    Returns:
        GeoJSON Feature dict
    """
    props = {"city": city, "latitude": latitude, "longitude": longitude}
    if properties:
        props.update(properties)

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [longitude, latitude],
        },
        "properties": props,
    }


def get_location_summary(city: str) -> Dict[str, Any]:
    """
    Return a full geospatial summary for a city including coordinates,
    monsoon zone, bounding box, and GeoJSON feature.

    Returns an honest "unavailable" state if the city cannot be geocoded.
    """
    coords = get_city_coordinates(city)

    if coords is None:
        return {
            "status": "unavailable",
            "message": f"Could not geocode city: {city}",
            "city": city,
            "latitude": None,
            "longitude": None,
            "monsoon_zone": None,
            "bounding_box_50km": None,
            "geojson": None,
        }

    lat = coords["latitude"]
    lon = coords["longitude"]
    bbox = bounding_box(lat, lon, radius_km=50)
    zone = classify_monsoon_zone(lat, lon)
    geojson = location_to_geojson(coords.get("city", city), lat, lon)

    return {
        "status": "ok",
        "city": coords.get("city", city),
        "state": coords.get("state", ""),
        "country": coords.get("country", "India"),
        "latitude": lat,
        "longitude": lon,
        "monsoon_zone": zone["zone"],
        "monsoon_zone_description": zone["description"],
        "bounding_box_50km": {
            "west": bbox[0], "south": bbox[1],
            "east": bbox[2], "north": bbox[3],
        },
        "geojson": geojson,
    }
