import uuid

from fastapi import APIRouter, HTTPException

from backend.database import db_cursor
from backend.models import GirisModel, KayitModel
from backend.security import sifre_hashle


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/kayit")
def kayit_ol(data: KayitModel):
    yeni_id = str(uuid.uuid4())

    with db_cursor(commit=True) as cursor:
        cursor.execute("SELECT id FROM dbo.Users WHERE email=? AND deleted_at IS NULL", data.email)
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Bu email zaten kayıtlı.")

        cursor.execute(
            """INSERT INTO dbo.Users
               (id, email, full_name, password_hash, role)
               VALUES (?,?,?,?,?)""",
            yeni_id,
            data.email,
            data.ad_soyad,
            sifre_hashle(data.sifre),
            data.rol,
        )

        cursor.execute("SELECT id FROM dbo.Badges WHERE name=N'İlk Adım'")
        badge = cursor.fetchone()
        if badge:
            cursor.execute(
                """IF NOT EXISTS (
                       SELECT 1 FROM dbo.UserBadges WHERE user_id=? AND badge_id=?
                   )
                   INSERT INTO dbo.UserBadges (user_id,badge_id) VALUES (?,?)""",
                yeni_id,
                str(badge[0]),
                yeni_id,
                str(badge[0]),
            )

    return {
        "mesaj": "Kayıt başarılı ✅",
        "kullanici_id": yeni_id,
        "ad_soyad": data.ad_soyad,
        "rol": data.rol,
        "career_title": "Explorer",
    }


@router.post("/giris")
def giris_yap(data: GirisModel):
    with db_cursor() as cursor:
        cursor.execute(
            """SELECT id, full_name, role, career_title, mfa_enabled
               FROM dbo.Users
               WHERE email=? AND password_hash=? AND deleted_at IS NULL""",
            data.email,
            sifre_hashle(data.sifre),
        )
        kullanici = cursor.fetchone()

    if not kullanici:
        raise HTTPException(status_code=401, detail="Email veya şifre hatalı.")

    return {
        "kullanici_id": str(kullanici[0]),
        "ad_soyad": kullanici[1],
        "rol": kullanici[2],
        "career_title": kullanici[3] or "Explorer",
        "mfa_enabled": bool(kullanici[4]),
    }