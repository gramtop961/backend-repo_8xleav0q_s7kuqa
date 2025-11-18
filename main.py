import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Table, Reservation

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Seating API ready"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
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
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Utility
class IdModel(BaseModel):
    id: str

# Seed a few extravagant demo tables if none exist
@app.post("/seed")
def seed_demo():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    existing = db["table"].count_documents({})
    if existing > 0:
        return {"status": "ok", "seeded": False, "count": existing}

    demo_tables = [
        Table(
            name="Aurora Circle",
            shape="round",
            x=200,
            y=180,
            width=160,
            height=160,
            rotation=0,
            color="#7dd3fc",
            seats=[{"index": i, "label": f"A{i+1}", "reserved": False} for i in range(10)],
        ),
        Table(
            name="Imperial Banquet",
            shape="rect",
            x=520,
            y=240,
            width=320,
            height=140,
            rotation=0,
            color="#f0abfc",
            seats=[{"index": i, "label": f"B{i+1}", "reserved": i % 3 == 0} for i in range(14)],
        ),
        Table(
            name="Velvet Nook",
            shape="round",
            x=900,
            y=420,
            width=140,
            height=140,
            rotation=15,
            color="#a7f3d0",
            seats=[{"index": i, "label": f"V{i+1}", "reserved": False} for i in range(8)],
        ),
    ]

    for t in demo_tables:
        create_document("table", t)

    count = db["table"].count_documents({})
    return {"status": "ok", "seeded": True, "count": count}

# List tables
@app.get("/tables")
def list_tables():
    docs = get_documents("table")
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return {"items": docs}

# Reserve a seat
class ReserveRequest(BaseModel):
    table_id: str
    seat_index: int
    name: str
    note: Optional[str] = None

@app.post("/reserve")
def reserve_seat(payload: ReserveRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    try:
        oid = ObjectId(payload.table_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid table id")

    table_doc = db["table"].find_one({"_id": oid})
    if not table_doc:
        raise HTTPException(status_code=404, detail="Table not found")

    seats = table_doc.get("seats", [])
    if payload.seat_index < 0 or payload.seat_index >= len(seats):
        raise HTTPException(status_code=400, detail="Invalid seat index")

    if seats[payload.seat_index].get("reserved"):
        raise HTTPException(status_code=409, detail="Seat already reserved")

    # mark seat reserved and store minimal reservation record
    seats[payload.seat_index]["reserved"] = True
    db["table"].update_one({"_id": oid}, {"$set": {"seats": seats}})

    create_document("reservation", Reservation(
        table_id=str(oid),
        seat_index=payload.seat_index,
        name=payload.name,
        note=payload.note
    ))

    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
