from fastapi import APIRouter, HTTPException

from backend.database import get_db


router = APIRouter()


@router.get("/")
def root():
    return {"mesaj": "SkillBridge API ✅", "versiyon": "1.0.0"}


@router.get("/health")
def health():
    try:
        conn = get_db()
        conn.close()
        return {"durum": "aktif ✅", "veritabani": "bağlı ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB bağlantı hatası: {e}")