import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

from database import create_document, get_documents, db
from schemas import Commission, Client, Note

app = FastAPI(title="Artist Commission Organizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------- Helpers ---------

def serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    d = {**doc}
    if d.get("_id"):
        d["id"] = str(d.pop("_id"))
    # Convert datetimes to isoformat strings
    for k, v in list(d.items()):
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d


# -------- Root & Health ---------
@app.get("/")
def read_root():
    return {"message": "Artist Commission Organizer Backend"}


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
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# -------- API: Clients ---------
@app.get("/api/clients")
def list_clients(limit: Optional[int] = 200):
    docs = get_documents("client", {}, limit)
    return [serialize_doc(d) for d in docs]


@app.post("/api/clients")
def create_client(payload: Client):
    cid = create_document("client", payload)
    return {"id": cid}


# -------- API: Commissions ---------
class CommissionCreate(Commission):
    pass

@app.get("/api/commissions")
def list_commissions(status: Optional[str] = None, limit: Optional[int] = 500):
    query: Dict[str, Any] = {}
    if status:
        query["status"] = status
    docs = get_documents("commission", query, limit)
    return [serialize_doc(d) for d in docs]


@app.post("/api/commissions")
def create_commission(payload: CommissionCreate):
    cid = create_document("commission", payload)
    return {"id": cid}


@app.get("/api/commissions/stats")
def commission_stats():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    result = list(db["commission"].aggregate(pipeline))
    return {r["_id"] or "Unknown": r["count"] for r in result}


# -------- API: Notes ---------
@app.get("/api/notes")
def list_notes(commission_id: str, limit: Optional[int] = 200):
    docs = get_documents("note", {"commission_id": commission_id}, limit)
    return [serialize_doc(d) for d in docs]


@app.post("/api/notes")
def create_note(payload: Note):
    nid = create_document("note", payload)
    return {"id": nid}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
