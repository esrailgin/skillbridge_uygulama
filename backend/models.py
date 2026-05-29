from pydantic import BaseModel, Field


class KayitModel(BaseModel):
    email: str
    sifre: str = Field(min_length=4)
    ad_soyad: str = Field(min_length=2)
    rol: str = "student"


class GirisModel(BaseModel):
    email: str
    sifre: str


class RoadmapAdimModel(BaseModel):
    roadmap_id: str
    adim_id: str
    durum: str