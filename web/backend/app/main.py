from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder

from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, REGISTRY, Gauge
from app import models, schemas, crud
from app.database import SessionLocal, engine
from app.initial_data import GLOSSARIES, RELATIONS

import time

# ----------------------------
# Prometheus metrics
# ----------------------------
REQUEST_COUNT = Counter('request_count_total', 'Total number of requests')
ERROR_COUNT = Counter('http_errors_total', 'Number of HTTP 5xx errors')

# ----------------------------
# FastAPI setup
# ----------------------------
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Глоссарий ВКР")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Startup event: load initial data
# ----------------------------
@app.on_event("startup")
def load_initial_data():
    db: Session = SessionLocal()
    db.query(models.Glossary).delete()
    db.commit()

    for glossary in GLOSSARIES:
        db.add(models.Glossary(**glossary))
    db.commit()
    db.close()

# ----------------------------
# CRUD endpoints
# ----------------------------
@app.get("/glossaries/", response_model=list[schemas.Glossary])
def get_glossaries():
    REQUEST_COUNT.inc()
    db: Session = SessionLocal()
    glossaries = crud.get_glossaries(db)
    db.close()
    return glossaries

@app.get("/glossaries/{keyword}", response_model=schemas.Glossary)
def get_glossary_by_keyword(keyword: str):
    db: Session = SessionLocal()
    glossary = crud.get_glossary_by_keyword(db, keyword)
    db.close()
    if not glossary:
        raise HTTPException(status_code=404, detail="Glossary not found")
    return glossary

@app.post("/glossaries/", response_model=schemas.Glossary)
def create_glossary(glossary: schemas.GlossaryCreate):
    db: Session = SessionLocal()
    db_glossary = crud.get_glossary(db, glossary.keyword)
    if db_glossary:
        db.close()
        raise HTTPException(status_code=400, detail="Glossary already exists")
    new_glossary = crud.create_glossary(db, glossary)
    db.close()
    return new_glossary

@app.put("/glossaries/{keyword}", response_model=schemas.Glossary)
def update_glossary(keyword: str, glossary: schemas.GlossaryCreate):
    db: Session = SessionLocal()
    updated = crud.update_glossary(db, keyword, glossary)
    db.close()
    if not updated:
        raise HTTPException(status_code=404, detail="Glossary not found")
    return updated

@app.delete("/glossaries/{keyword}")
def delete_glossary(keyword: str):
    db: Session = SessionLocal()
    success = crud.delete_glossary(db, keyword)
    db.close()
    if not success:
        raise HTTPException(status_code=404, detail="Glossary not found")
    return {"detail": "Glossary deleted"}

@app.get("/glossaries/relations/")
def get_relations():
    try:
        return JSONResponse(content=jsonable_encoder(RELATIONS))
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

# ----------------------------
# Prometheus metrics endpoint
# ----------------------------
@app.get("/metrics")
def metrics():
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
