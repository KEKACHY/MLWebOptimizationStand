from sqlalchemy.orm import Session
from . import models, schemas

def get_glossaries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Glossary).offset(skip).limit(limit).all()

def get_glossary_by_keyword(db: Session, keyword: str):
    return db.query(models.Glossary).filter(models.Glossary.keyword == keyword).first()

def create_glossary(db: Session, glossary: schemas.GlossaryCreate):
    db_glossary = models.Glossary(keyword=glossary.keyword, description=glossary.description)
    db.add(db_glossary)
    db.commit()
    db.refresh(db_glossary)
    return db_glossary

def update_glossary(db: Session, db_glossary: models.Glossary, glossary_update: schemas.GlossaryUpdate):
    db_glossary.keyword = glossary_update.keyword
    db_glossary.description = glossary_update.description
    db.commit()
    db.refresh(db_glossary)
    return db_glossary

def delete_glossary(db: Session, db_glossary: models.Glossary):
    db.delete(db_glossary)
    db.commit()
    return db_glossary
