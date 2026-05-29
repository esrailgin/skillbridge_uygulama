import hashlib
import re
import uuid
from pathlib import Path
from random import randint

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.database import db_cursor


router = APIRouter(prefix="/api/cv", tags=["cv"])
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads" / "cv"


class CVOnayModel(BaseModel):
    analiz_id: str
    gap_skoru: float = 75
    mentor_notu: str | None = None


def guvenli_dosya_adi(dosya_adi: str) -> str:
    ad = Path(dosya_adi or "cv.pdf").name
    ad = re.sub(r"[^\w.\-ığüşöçİĞÜŞÖÇ ]+", "_", ad, flags=re.UNICODE).strip()
    return ad or "cv.pdf"


@router.post("/yukle/{kullanici_id}")
async def cv_yukle(kullanici_id: str, dosya: UploadFile = File(...)):
    icerik = await dosya.read()
    file_hash = hashlib.sha256(icerik).hexdigest()
    yeni_id = str(uuid.uuid4())

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dosya_adi = guvenli_dosya_adi(dosya.filename)
    kayit_adi = f"{yeni_id}_{dosya_adi}"
    dosya_yolu = UPLOAD_DIR / kayit_adi

    with db_cursor(commit=True) as cursor:
        cursor.execute(
            "SELECT id, file_path FROM dbo.CVAnalyses WHERE user_id=? AND file_hash=?",
            kullanici_id,
            file_hash,
        )
        onceki = cursor.fetchone()
        if onceki:
            if not onceki[1]:
                dosya_yolu.write_bytes(icerik)
                cursor.execute(
                    "UPDATE dbo.CVAnalyses SET file_path=?, updated_at=GETUTCDATE() WHERE id=?",
                    str(dosya_yolu),
                    str(onceki[0]),
                )
            return {"mesaj": "Bu CV daha önce yüklendi.", "analiz_id": str(onceki[0])}

        dosya_yolu.write_bytes(icerik)

        cursor.execute(
            """INSERT INTO dbo.CVAnalyses
               (id, user_id, file_name, file_hash, file_size_bytes, mime_type, status, file_path)
               VALUES (?,?,?,?,?,?,?,?)""",
            yeni_id,
            kullanici_id,
            dosya_adi,
            file_hash,
            len(icerik),
            dosya.content_type,
            "pending",
            str(dosya_yolu),
        )

    return {
        "analiz_id": yeni_id,
        "durum": "pending",
        "mesaj": "CV yüklendi, mentor incelemesi için sıraya alındı.",
    }


@router.get("/bekleyen")
def bekleyen_cvleri_getir():
    with db_cursor() as cursor:
        cursor.execute(
            """SELECT c.id, c.user_id, c.file_name, c.status, c.created_at, c.file_path,
                      u.full_name, u.email, u.role, u.career_title
               FROM dbo.CVAnalyses c
               JOIN dbo.Users u ON u.id = c.user_id
               WHERE c.status = 'pending' AND u.deleted_at IS NULL
               ORDER BY c.created_at DESC"""
        )
        satirlar = cursor.fetchall()

    return [
        {
            "id": str(s[0]),
            "kullanici_id": str(s[1]),
            "dosya_adi": s[2],
            "durum": s[3],
            "tarih": str(s[4]),
            "dosya_var": bool(s[5] and Path(str(s[5])).exists()),
            "dosya_url": f"/api/cv/dosya/{s[0]}",
            "ad_soyad": s[6],
            "email": s[7],
            "rol": s[8],
            "career_title": s[9],
        }
        for s in satirlar
    ]


@router.get("/dosya/{analiz_id}")
def cv_dosya_getir(analiz_id: str):
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT file_name, mime_type, file_path FROM dbo.CVAnalyses WHERE id=?",
            analiz_id,
        )
        row = cursor.fetchone()

    if not row:
        raise HTTPException(404, "CV kaydı bulunamadı.")

    file_name, mime_type, file_path = row
    if not file_path or not Path(str(file_path)).exists():
        raise HTTPException(404, "CV dosyası sunucuda bulunamadı. Bu kayıt dosya saklama özelliğinden önce yüklenmiş olabilir.")

    return FileResponse(
        path=str(file_path),
        media_type=mime_type or "application/octet-stream",
        filename=file_name or "cv.pdf",
    )


@router.patch("/mentor-onayla")
def mentor_cv_onayla(data: CVOnayModel):
    skor = max(0, min(float(data.gap_skoru), 100))

    with db_cursor(commit=True) as cursor:
        cursor.execute(
            "SELECT user_id, status FROM dbo.CVAnalyses WHERE id=?",
            data.analiz_id,
        )
        row = cursor.fetchone()

        if not row:
            raise HTTPException(404, "CV analizi bulunamadı.")

        user_id = str(row[0])

        cursor.execute(
            """UPDATE dbo.CVAnalyses
               SET status='completed',
                   skill_gap_score=?,
                   processing_time_ms=?,
                   ai_model=?,
                   analysis_result=?,
                   updated_at=GETUTCDATE()
               WHERE id=?""",
            skor,
            randint(1200, 2600),
            "Mentor İncelemesi",
            data.mentor_notu or "Mentor tarafından incelendi ve tamamlandı.",
            data.analiz_id,
        )

        if skor >= 80:
            yeni_unvan = "Güçlü Aday"
        elif skor >= 60:
            yeni_unvan = "Gelişen Aday"
        else:
            yeni_unvan = "Gelişim Aşamasında"

        cursor.execute(
            """UPDATE dbo.Users
               SET career_title=?, updated_at=GETUTCDATE()
               WHERE id=?""",
            yeni_unvan,
            user_id,
        )

        cursor.execute("SELECT id FROM dbo.Badges WHERE name=N'İlk Adım'")
        badge = cursor.fetchone()
        if badge:
            cursor.execute(
                """IF NOT EXISTS (
                       SELECT 1 FROM dbo.UserBadges
                       WHERE user_id=? AND badge_id=?
                   )
                   INSERT INTO dbo.UserBadges (user_id, badge_id)
                   VALUES (?, ?)""",
                user_id,
                str(badge[0]),
                user_id,
                str(badge[0]),
            )

    return {
        "mesaj": "CV mentor tarafından onaylandı ve tamamlandı.",
        "durum": "completed",
        "gap_skoru": skor,
    }


@router.get("/{kullanici_id}")
def cv_analizleri_getir(kullanici_id: str):
    with db_cursor() as cursor:
        cursor.execute(
            """SELECT id, file_name, status, skill_gap_score, processing_time_ms, created_at, file_path
               FROM dbo.CVAnalyses
               WHERE user_id=?
               ORDER BY created_at DESC""",
            kullanici_id,
        )
        satirlar = cursor.fetchall()

    return [
        {
            "id": str(s[0]),
            "dosya_adi": s[1],
            "durum": s[2],
            "gap_skoru": float(s[3]) if s[3] else 0,
            "sure_ms": s[4],
            "tarih": str(s[5]),
            "dosya_var": bool(s[6] and Path(str(s[6])).exists()),
            "dosya_url": f"/api/cv/dosya/{s[0]}",
        }
        for s in satirlar
    ]


