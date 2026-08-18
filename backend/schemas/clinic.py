from pydantic import BaseModel


class ClinicResponse(BaseModel):
    place_id: str
    name: str
    address: str | None
    rating: float | None
    distance_km: float
    phone: str | None


class NearbyClinicsResponse(BaseModel):
    items: list[ClinicResponse]
