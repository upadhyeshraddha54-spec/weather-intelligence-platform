from pystac_client import Client
import planetary_computer


def fetch_satellite_metadata():
    """
    Fetch the latest Sentinel-2 metadata from Microsoft's Planetary Computer.
    """

    catalog = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1"
    )

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=[73.75, 18.45, 73.95, 18.65],  # Pune
        limit=1
    )

    items = list(search.items())

    if len(items) == 0:
        return None

    item = planetary_computer.sign(items[0])

    return {
        "id": item.id,
        "date": item.datetime.strftime("%Y-%m-%d"),
        "cloud_cover": item.properties.get("eo:cloud_cover")
    }


if __name__ == "__main__":

    result = fetch_satellite_metadata()

    print(result)