from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from backend.database import db_cursor

router = APIRouter(prefix="/api/etkilesimler", tags=["etkilesimler"])


class TalepOlusturModel(BaseModel):
    requester_id: str
    note: str | None = None


class MentorDegerlendirModel(BaseModel):
    interaction_id: str
    mentor_note: str
    status: str


class IKDegerlendirModel(BaseModel):
    interaction_id: str
    hr_note: str | None = None


def durum_etiketi(status: str) -> str:
    return {
        "pending": "Mentor değerlendirmesi bekliyor",
        "approved": "Mentor uygun gördü",
        "reviewed": "Mentor değerlendirdi",
        "rejected": "Geliştirilmesi önerildi",
        "shortlisted": "İK mülakat listesine aldı",
    }.get(status, status)


@router.post("/talep-olustur")
def talep_olustur(data: TalepOlusturModel):
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            """IF NOT EXISTS (
                   SELECT 1 FROM dbo.RoleInteractions
                   WHERE requester_id=? AND status IN ('pending', 'approved', 'reviewed')
               )
               INSERT INTO dbo.RoleInteractions (requester_id, target_role, note)
               VALUES (?, 'mentor', ?)""",
            data.requester_id,
            data.requester_id,
            data.note,
        )
    return {"mesaj": "Mentor değerlendirme talebi oluşturuldu."}


@router.get("/kullanici/{kullanici_id}")
def kullanici_etkilesimleri(kullanici_id: str):
    with db_cursor() as cursor:
        cursor.execute(
            """SELECT ri.id, ri.status, ri.note, ri.mentor_note, ri.hr_note,
                      ri.created_at, u.id, u.full_name, u.email, u.role, u.career_title
               FROM dbo.RoleInteractions ri
               JOIN dbo.Users u ON u.id = ri.requester_id
               WHERE ri.requester_id=?
               ORDER BY ri.created_at DESC""",
            kullanici_id,
        )
        rows = cursor.fetchall()
    return [_row_user(r) for r in rows]


@router.get("/mentor")
def mentor_talepleri():
    with db_cursor() as cursor:
        cursor.execute(
            """SELECT ri.id, ri.status, ri.note, ri.mentor_note, NULL AS hr_note,
                      ri.created_at, u.id, u.full_name, u.email, u.role, u.career_title
               FROM dbo.RoleInteractions ri
               JOIN dbo.Users u ON u.id = ri.requester_id
               WHERE ri.status IN ('pending', 'reviewed', 'approved', 'rejected')
               ORDER BY ri.created_at DESC"""
        )
        rows = cursor.fetchall()
    return [_row_user(r) for r in rows]


@router.get("/ik")
def ik_adaylari():
    with db_cursor() as cursor:
        cursor.execute(
            """SELECT ri.id, ri.status, ri.note, ri.mentor_note, ri.hr_note,
                      ri.created_at, u.id, u.full_name, u.email, u.role, u.career_title
               FROM dbo.RoleInteractions ri
               JOIN dbo.Users u ON u.id = ri.requester_id
               WHERE ri.status IN ('approved', 'shortlisted')
               ORDER BY ri.created_at DESC"""
        )
        rows = cursor.fetchall()
    return [_row_user(r) for r in rows]


def _row_user(r) -> dict:
    return {
        "id": str(r[0]),
        "durum": r[1],
        "durum_etiketi": durum_etiketi(r[1]),
        "not": r[2],
        "mentor_notu": r[3],
        "ik_notu": r[4],
        "tarih": str(r[5]),
        "kullanici_id": str(r[6]),
        "ad_soyad": r[7],
        "email": r[8],
        "rol": r[9],
        "career_title": r[10],
    }


@router.patch("/mentor-degerlendir")
def mentor_degerlendir(data: MentorDegerlendirModel, x_user_role: str | None = Header(default=None)):
    if x_user_role != "mentor":
        raise HTTPException(403, "Bu işlem yalnızca mentor rolüyle yapılabilir.")
    if data.status not in ("approved", "rejected", "reviewed"):
        raise HTTPException(400, "Geçersiz durum.")
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            """UPDATE dbo.RoleInteractions
               SET mentor_note=?, status=?, updated_at=GETUTCDATE()
               WHERE id=?""",
            data.mentor_note,
            data.status,
            data.interaction_id,
        )
    return {"mesaj": "Mentor değerlendirmesi kaydedildi."}


@router.patch("/ik-listeye-al")
def ik_listeye_al(data: IKDegerlendirModel, x_user_role: str | None = Header(default=None)):
    if x_user_role != "hr_manager":
        raise HTTPException(403, "Bu işlem yalnızca İK rolüyle yapılabilir.")
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            """UPDATE dbo.RoleInteractions
               SET hr_note=?, status='shortlisted', updated_at=GETUTCDATE()
               WHERE id=?""",
            data.hr_note,
            data.interaction_id,
        )
    return {"mesaj": "Aday mülakat listesine alındı."}
