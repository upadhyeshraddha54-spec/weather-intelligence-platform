"""
Satellite Agent — orchestrates satellite data fetch and analysis.

Accepts an optional ``city`` argument so analysis can be location-specific.
When satellite dependencies are unavailable, returns an honest status dict
rather than fabricated values.
"""
import logging

from src.satellite.satellite_analysis import analyze_satellite

logger = logging.getLogger(__name__)


def run_satellite_agent(city: str = ""):
    """
    Run satellite analysis for the given city.

    Args:
        city: City name (used for bbox selection in the fetcher).

    Returns:
        dict with satellite analysis fields, including a ``status`` key:
        - ``"ok"``          — real Sentinel-2 data obtained
        - ``"unavailable"`` — honest state when data cannot be retrieved
    """
    print("\n==============================")
    print("🛰 SATELLITE AGENT")
    print("==============================")

    try:
        result = analyze_satellite(city=city)
        status = result.get("status", "unknown")
        if status == "ok":
            print(f"🛰 Satellite data retrieved for {city or 'default location'}.")
        else:
            print(
                "⚠️  Satellite data unavailable (pystac-client / "
                "planetary-computer dependency not installed or API unreachable)."
            )
        return result

    except Exception as exc:
        logger.error("Satellite agent raised an unexpected error: %s", exc)
        return {
            "status": "error",
            "message": f"Satellite agent failed: {exc}",
            "image_date": "N/A",
            "cloud_cover": "N/A",
            "condition": "N/A",
            "rain_potential": "N/A",
            "visibility": "N/A",
            "confidence": "N/A",
            "summary": "Satellite analysis could not be performed.",
        }


if __name__ == "__main__":
    import sys
    city_arg = sys.argv[1] if len(sys.argv) > 1 else "Pune"
    print("\n==============================")
    print("🛰 SATELLITE AGENT")
    print("==============================\n")
    result = run_satellite_agent(city=city_arg)
    print(result)