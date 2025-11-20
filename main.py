import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime

from database import db, create_document, get_documents
from schemas import Ride as RideSchema, Kpi as KpiSchema

app = FastAPI(title="GreenBee API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "ok", "name": "GreenBee API", "version": "1.0.0"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


class EstimateRequest(BaseModel):
    pickup: str
    dropoff: str
    distance_km: float = Field(..., ge=0)
    passengers: int = Field(1, ge=1, le=6)


class EstimateResponse(BaseModel):
    price_eur: float
    co2_saved_kg: float


@app.post("/estimate", response_model=EstimateResponse)
def estimate(req: EstimateRequest):
    # Business logic preserved as discussed
    base = 12.0
    per_km = 1.8
    extra_per_passenger = 2.0
    pax = max(1, req.passengers)
    price = base + req.distance_km * per_km + (pax - 1) * extra_per_passenger
    co2_saved = req.distance_km * 0.14 * 0.6
    return EstimateResponse(price_eur=round(price, 2), co2_saved_kg=round(co2_saved, 2))


@app.post("/rides")
def create_ride(ride: RideSchema):
    try:
        inserted_id = create_document("ride", ride)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rides")
def list_rides(limit: Optional[int] = 50):
    try:
        docs = get_documents("ride", {}, limit=limit or 50)
        # Convert ObjectId and datetimes
        def normalize(doc):
            d = {**doc}
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
            for k, v in list(d.items()):
                if hasattr(v, "isoformat"):
                    d[k] = v.isoformat()
            return d
        return [normalize(x) for x in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/kpis")
def get_kpis():
    """Return high-level KPIs for admin dashboard.
    If none stored, compute lightweight defaults from available data.
    """
    try:
        # Basic aggregates from rides
        rides = get_documents("ride", {})
        total_rides = len(rides)
        monthly_rides = sum(1 for r in rides if str(r.get("created_at", "")).startswith(str(datetime.utcnow().date())[:7]))
        total_co2_saved = 0.0
        ratings = []
        for r in rides:
            total_co2_saved += float(r.get("co2_saved_kg", 0) or 0)
            if "rating" in r:
                try:
                    ratings.append(float(r["rating"]))
                except Exception:
                    pass
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 4.9
        beeps_points = int(total_rides * 100)
        trend = [max(20, min(100, beeps_points // 10 + i * 3)) for i in range(12)]

        data = KpiSchema(
            total_rides=total_rides,
            monthly_rides=monthly_rides,
            avg_rating=avg_rating,
            total_co2_saved_kg=round(total_co2_saved, 2),
            beeps_points=beeps_points,
            trend=trend,
            updated_at=datetime.utcnow(),
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
