from pydantic import BaseModel

class GlossaryBase(BaseModel):
    keyword: str
    description: str

class GlossaryCreate(GlossaryBase):
    pass

class GlossaryUpdate(GlossaryBase):
    pass

class Glossary(GlossaryBase):
    id: int

    class Config:
        orm_mode = True
