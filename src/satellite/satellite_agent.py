from src.satellite.satellite_fetcher import fetch_satellite_metadata
from src.satellite.satellite_analysis import analyze_satellite


def run_satellite_agent():

    print("\n==============================")
    print("🛰 SATELLITE AGENT")
    print("==============================")

    try:
        result = analyze_satellite()
        return result

    except Exception as e:

        print(f"Satellite API unavailable: {e}")
        print("Using fallback satellite data...")

        return {
            "image_id": "TEST_IMAGE",
            "image_date": "2026-08-03",
            "cloud_cover": 99.8,
            "condition": "Overcast",
            "summary": "Satellite imagery indicates overcast conditions with 99.8% cloud cover."
        }


if __name__ == "__main__":

    print("\n==============================")
    print("🛰 SATELLITE AGENT")
    print("==============================\n")

    result = run_satellite_agent()

    print(result)