"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Example schemas (you can keep using these if needed)
class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in euros")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Green'Bee domain models
class Ride(BaseModel):
    """Represents a ride booking"""
    pickup: str
    dropoff: str
    distance_km: float = Field(..., ge=0)
    passengers: int = Field(1, ge=1, le=6)
    price_eur: float = Field(..., ge=0)
    co2_saved_kg: float = Field(..., ge=0)
    status: str = Field("confirmed", description="confirmed | completed | canceled")
    driver_name: Optional[str] = None
    vehicle: Optional[str] = None

class Kpi(BaseModel):
    """High-level KPI values for dashboards"""
    total_rides: int
    monthly_rides: int
    avg_rating: float
    total_co2_saved_kg: float
    beeps_points: int
    trend: List[float] = []
    updated_at: Optional[datetime] = None
