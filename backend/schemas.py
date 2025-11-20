from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, List

# Example persisted entities for Green'Bee visuals (can be extended without breaking)

class User(BaseModel):
    id: Optional[str] = Field(default=None)
    email: str
    name: Optional[str] = None
    role: str = Field(default="client")  # client | driver | admin


class Ride(BaseModel):
    id: Optional[str] = Field(default=None)
    pickup: str
    dropoff: str
    distance_km: float
    passengers: int
    price_eur: float
    co2_saved_kg: float
    status: str = Field(default="requested")  # requested | confirmed | completed | cancelled
    user_id: Optional[str] = None


class Kpi(BaseModel):
    id: Optional[str] = Field(default=None)
    name: str
    value: float
    unit: Optional[str] = None
