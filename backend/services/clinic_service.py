import asyncio
import logging
import math

import httpx

from config import settings
from schemas.clinic import ClinicResponse

logger = logging.getLogger(__name__)

NEARBY_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# Nearby Search doesn't return a phone number — that needs a separate Place
# Details call per result. Capped to bound latency/cost; results beyond this
# (already sorted by distance) just come back with phone: null.
MAX_PHONE_LOOKUPS = 10


class ClinicServiceUnavailableError(Exception):
    """Raised when the Google Places API cannot be reached, errors, or is unconfigured."""


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r_km = 6371.0
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(d_lng / 2) ** 2
    return r_km * 2 * math.asin(math.sqrt(a))


class ClinicService:
    async def nearby(self, lat: float, lng: float, radius_m: int) -> list[ClinicResponse]:
        """Returns nearby dentists sorted by distance, closest first.

        Raises ClinicServiceUnavailableError if no API key is configured or
        on any network/API failure, so callers can surface a consistent 503.
        """
        if not settings.GOOGLE_PLACES_API_KEY:
            raise ClinicServiceUnavailableError()

        params = {
            "location": f"{lat},{lng}",
            "radius": radius_m,
            "type": "dentist",
            "key": settings.GOOGLE_PLACES_API_KEY,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(NEARBY_SEARCH_URL, params=params)
                response.raise_for_status()
                body = response.json()
                status = body.get("status")
                if status not in ("OK", "ZERO_RESULTS"):
                    raise ValueError(f"Places API returned status={status}")
                results = body.get("results", [])

                clinics = []
                for place in results:
                    location = place.get("geometry", {}).get("location", {})
                    place_lat, place_lng = location.get("lat"), location.get("lng")
                    if place_lat is None or place_lng is None:
                        continue
                    clinics.append(
                        {
                            "place_id": place["place_id"],
                            "name": place.get("name", "Unknown clinic"),
                            "address": place.get("vicinity"),
                            "rating": place.get("rating"),
                            "distance_km": round(_haversine_km(lat, lng, place_lat, place_lng), 2),
                        }
                    )
                clinics.sort(key=lambda c: c["distance_km"])

                phones = await asyncio.gather(
                    *(
                        self._fetch_phone(client, c["place_id"])
                        for c in clinics[:MAX_PHONE_LOOKUPS]
                    )
                )
                for clinic, phone in zip(clinics, phones):
                    clinic["phone"] = phone
                for clinic in clinics[MAX_PHONE_LOOKUPS:]:
                    clinic["phone"] = None

                return [ClinicResponse(**c) for c in clinics]
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            logger.warning("Google Places service unavailable: %s", exc)
            raise ClinicServiceUnavailableError() from exc

    async def _fetch_phone(self, client: httpx.AsyncClient, place_id: str) -> str | None:
        try:
            response = await client.get(
                PLACE_DETAILS_URL,
                params={
                    "place_id": place_id,
                    "fields": "formatted_phone_number",
                    "key": settings.GOOGLE_PLACES_API_KEY,
                },
            )
            response.raise_for_status()
            return response.json().get("result", {}).get("formatted_phone_number")
        except httpx.HTTPError as exc:
            # A single clinic's phone lookup failing shouldn't fail the
            # whole nearby-search response.
            logger.warning("Place Details lookup failed for place_id=%s: %s", place_id, exc)
            return None
