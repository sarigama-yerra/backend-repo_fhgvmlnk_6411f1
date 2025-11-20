from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import get_db, create_document, get_documents, settings
from schemas import Ride, Kpi

app = FastAPI(title="GreenBee API", version="1.0.0")

# CORS for local + hosted frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def root():
    return {"message": "GreenBee API up", "database_url": settings.database_url, "database_name": settings.database_name}


@app.get("/test")
async def test():
    db = get_db()
    collections = await db.list_collection_names()
    return {
        "backend": "ok",
        "database": "mongodb",
        "database_url": settings.database_url,
        "database_name": settings.database_name,
        "connection_status": "connected",
        "collections": collections,
    }


class EstimateRequest(BaseModel):
    distance_km: float
    passengers: int = 1


class EstimateResponse(BaseModel):
    price_eur: float
    co2_saved_kg: float


@app.post("/estimate", response_model=EstimateResponse)
async def estimate(body: EstimateRequest):
    base = 12.0
    per_km = 1.8
    pax_extra = max(0, body.passengers - 1) * 2.0
    price = base + body.distance_km * per_km + pax_extra
    co2_saved = body.distance_km * 0.14 * 0.6
    return EstimateResponse(price_eur=round(price, 2), co2_saved_kg=round(co2_saved, 2))


@app.post("/rides")
async def create_ride(ride: Ride):
    rid = await create_document("ride", ride.dict())
    return {"id": rid}


@app.get("/rides", response_model=List[Ride])
async def list_rides(limit: int = 50):
    docs = await get_documents("ride", limit=limit)
    # Basic pydantic conversion safety
    return [Ride(**{**d, "id": d.get("_id")}) for d in docs]


@app.get("/kpis", response_model=List[Kpi])
async def list_kpis(limit: int = 20):
    docs = await get_documents("kpi", limit=limit)
    return [Kpi(**{**d, "id": d.get("_id")}) for d in docs]
