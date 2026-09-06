"""
Satellite fetcher — retrieves Sentinel-2 metadata from Microsoft Planetary Computer.

This integration requires the optional packages ``pystac-client`` and
``planetary-computer``, which are NOT included in the base requirements.
If they are absent or the Planetary Computer API is unreachable, the
fetcher returns ``None`` and the caller should present an honest
"satellite data unavailable" state rather than fabricated values.

External dependency:
    pip install pystac-client planetary-computer
    (requires internet access and a Planetary Computer API token for signed URLs)
"""
import logging

logger = logging.getLogger(__name__)


def fetch_satellite_metadata(city: str = "Pune", bbox: list = None):
    """
    Fetch the latest Sentinel-2 L2A tile metadata for the given bounding box.

    Args:
        city: Human-readable city name (used for logging only).
        bbox: [west, south, east, north] bounding box in WGS-84 degrees.
              Defaults to a tight box around Pune, India.

    Returns:
        dict with keys ``id``, ``date``, ``cloud_cover`` on success.
        None if the dependency is unavailable or the API call fails.
    """
    if bbox is None:
        bbox = [73.75, 18.45, 73.95, 18.65]  # Pune default

    # Gracefully handle missing optional dependencies.
    try:
        from pystac_client import Client
        import planetary_computer
    except ImportError as exc:
        logger.warning(
            "Satellite: optional dependency missing (%s). "
            "Install pystac-client and planetary-computer to enable "
            "satellite imagery.",
            exc,
        )
        return None

    try:
        catalog = Client.open(
            "https://planetarycomputer.microsoft.com/api/stac/v1",
            modifier=planetary_computer.sign_inplace,
        )

        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            limit=1,
        )

        items = list(search.items())

        if not items:
            logger.info(
                "Satellite: no Sentinel-2 items found for city=%s bbox=%s",
                city,
                bbox,
            )
            return None

        item = items[0]

        return {
            "id": item.id,
            "date": item.datetime.strftime("%Y-%m-%d"),
            "cloud_cover": item.properties.get("eo:cloud_cover"),
        }

    except Exception as exc:
        logger.warning("Satellite: API call failed for %s — %s", city, exc)
        return None


if __name__ == "__main__":
    result = fetch_satellite_metadata()
    print(result)