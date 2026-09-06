"""
Satellite analysis — classifies cloud cover from Sentinel-2 metadata.

When satellite data is unavailable (dependencies missing or API down) this
module returns an honest unavailable state rather than fabricated values.
"""
import logging

from src.satellite.satellite_fetcher import fetch_satellite_metadata

logger = logging.getLogger(__name__)

# Sentinel-2 does not provide location-specific bbox out of the box;
# extend this mapping as needed.
CITY_BBOX = {
    "pune": [73.75, 18.45, 73.95, 18.65],
    "mumbai": [72.77, 18.89, 72.99, 19.11],
    "delhi": [76.85, 28.45, 77.35, 28.80],
    "bengaluru": [77.45, 12.85, 77.75, 13.10],
    "chennai": [80.18, 12.95, 80.32, 13.15],
    "hyderabad": [78.35, 17.30, 78.60, 17.55],
    "nagpur": [78.95, 21.05, 79.15, 21.25],
    "nashik": [73.70, 19.95, 73.90, 20.10],
}

_UNAVAILABLE_STATE = {
    "status": "unavailable",
    "message": (
        "Satellite data is currently unavailable. "
        "The pystac-client / planetary-computer integration "
        "requires optional packages and internet access."
    ),
    "image_date": "N/A",
    "cloud_cover": "N/A",
    "condition": "N/A",
    "rain_potential": "N/A",
    "visibility": "N/A",
    "confidence": "N/A",
    "summary": "No satellite analysis was performed.",
}


def analyze_satellite(city: str = ""):
    """
    Fetch Sentinel-2 metadata for ``city`` and classify cloud conditions.

    Returns a dict with all analysis fields on success, or the
    ``_UNAVAILABLE_STATE`` sentinel dict when data cannot be obtained.
    """
    bbox = CITY_BBOX.get(city.lower().strip())

    try:
        metadata = fetch_satellite_metadata(city=city, bbox=bbox)
    except Exception as exc:
        logger.warning("Satellite analysis: fetch raised %s", exc)
        metadata = None

    if metadata is None:
        logger.info(
            "Satellite analysis: no data available for city=%s", city
        )
        return dict(_UNAVAILABLE_STATE)

    cloud = metadata.get("cloud_cover")

    if cloud is None:
        return dict(_UNAVAILABLE_STATE)

    # Cloud condition classification
    if cloud >= 80:
        condition = "Overcast"
        rain_potential = "High"
        visibility = "Poor"
    elif cloud >= 50:
        condition = "Mostly Cloudy"
        rain_potential = "Moderate"
        visibility = "Moderate"
    elif cloud >= 20:
        condition = "Partly Cloudy"
        rain_potential = "Low"
        visibility = "Good"
    else:
        condition = "Clear"
        rain_potential = "Low"
        visibility = "Good"

    return {
        "status": "ok",
        "image_id": metadata.get("id", "N/A"),
        "image_date": metadata.get("date", "N/A"),
        "cloud_cover": cloud,
        "condition": condition,
        "rain_potential": rain_potential,
        "visibility": visibility,
        "confidence": "High",
        "summary": (
            f"Sentinel-2 imagery (date: {metadata.get('date', 'N/A')}) "
            f"indicates {condition.lower()} conditions with "
            f"{cloud}% cloud cover. "
            f"Rain potential is {rain_potential.lower()}."
        ),
    }


if __name__ == "__main__":
    result = analyze_satellite("Pune")
    print(result)