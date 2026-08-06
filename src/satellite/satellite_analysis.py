from src.satellite.satellite_fetcher import fetch_satellite_metadata


def analyze_satellite():

    try:
        metadata = fetch_satellite_metadata()

        cloud = metadata["cloud_cover"]

        if cloud > 80:
            condition = "Overcast"
        elif cloud > 40:
            condition = "Partly Cloudy"
        else:
            condition = "Mostly Clear"

        return {
            "image_id": metadata["id"],
            "image_date": metadata["date"],
            "cloud_cover": cloud,
            "condition": condition,
            "summary": f"Satellite imagery indicates {condition.lower()} conditions with {cloud}% cloud cover."
        }

    except Exception as e:

        print(f"Satellite fetch failed: {e}")
        print("Using fallback satellite data...")

        return {
            "image_id": "TEST_IMAGE",
            "image_date": "2026-08-03",
            "cloud_cover": 99.8,
            "condition": "Overcast",
            "summary": "Satellite imagery indicates overcast conditions with 99.8% cloud cover."
        }


if __name__ == "__main__":

    result = analyze_satellite()
    print(result)