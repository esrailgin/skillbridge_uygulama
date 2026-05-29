from fastapi import APIRouter, HTTPException

from backend.database import db_cursor


router = APIRouter(prefix="/api/kullanicilar", tags=["kullanicilar"])


@router.get("")
def kullanicilari_getir():
    with db_cursor() as cursor:
        cursor.execute(
            """SELECT id, email, full_name, role, career_title, created_at
               FROM dbo.Users
               WHERE deleted_at IS NULL
               ORDER BY created_at DESC"""
        )
        satirlar = cursor.fetchall()

    return [
        {
            "id": str(s[0]),
            "email": s[1],
            "ad_soyad": s[2],
            "rol": s[3],
            "career_title": s[4],
            "kayit_tarihi": str(s[5]),
        }
        for s in satirlar
    ]


@router.get("/{kullanici_id}/profil")
def profil_getir(kullanici_id: str):
    with db_cursor() as cursor:
        cursor.execute(
            """SELECT id, email, full_name, role, career_title, created_at
               FROM dbo.Users
               WHERE id=? AND deleted_at IS NULL""",
            kullanici_id,
        )
        kullanici = cursor.fetchone()

        if not kullanici:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

        cursor.execute(
            """SELECT si.name, us.level, us.confidence
               FROM dbo.UserSkills us
               JOIN dbo.SkillsInventory si ON si.id=us.skill_id
               WHERE us.user_id=?""",
            kullanici_id,
        )
        beceriler = [
            {"ad": r[0], "seviye": r[1], "guven": float(r[2] or 0)}
            for r in cursor.fetchall()
        ]

        cursor.execute(
            """SELECT b.name, b.icon, b.color, ub.awarded_at
               FROM dbo.UserBadges ub
               JOIN dbo.Badges b ON b.id=ub.badge_id
               WHERE ub.user_id=?
               ORDER BY ub.awarded_at DESC""",
            kullanici_id,
        )
        rozetler = [
            {"ad": r[0], "icon": r[1], "renk": r[2], "tarih": str(r[3])}
            for r in cursor.fetchall()
        ]

    return {
        "id": str(kullanici[0]),
        "email": kullanici[1],
        "ad_soyad": kullanici[2],
        "rol": kullanici[3],
        "career_title": kullanici[4],
        "kayit_tarihi": str(kullanici[5]),
        "beceriler": beceriler,
        "rozetler": rozetler,
    }