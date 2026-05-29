from fastapi import APIRouter

from backend.database import db_cursor


router = APIRouter(prefix="/api/beceriler", tags=["beceriler"])


@router.get("")
def becerileri_getir():
    with db_cursor() as cursor:
        cursor.execute(
            """SELECT id, name, category, market_demand, trend_score
               FROM dbo.SkillsInventory
               WHERE is_active=1
               ORDER BY market_demand DESC"""
        )
        satirlar = cursor.fetchall()

    return [
        {
            "id": str(s[0]),
            "ad": s[1],
            "kategori": s[2],
            "piyasa_talebi": float(s[3] or 0),
            "trend_skoru": float(s[4] or 0),
        }
        for s in satirlar
    ]


@router.post("/{kullanici_id}/ekle")
def beceri_ekle(kullanici_id: str, skill_id: str, seviye: str = "beginner"):
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            """IF NOT EXISTS (
                   SELECT 1 FROM dbo.UserSkills
                   WHERE user_id=? AND skill_id=?
               )
               INSERT INTO dbo.UserSkills (id, user_id, skill_id, level, self_assessed)
               VALUES (NEWID(), ?, ?, ?, 1)""",
            kullanici_id,
            skill_id,
            kullanici_id,
            skill_id,
            seviye,
        )

        cursor.execute(
            "SELECT COUNT(*) FROM dbo.UserSkills WHERE user_id=?",
            kullanici_id,
        )
        sayi = cursor.fetchone()[0]

        if sayi >= 10:
            cursor.execute("SELECT id FROM dbo.Badges WHERE name=N'Beceri Kaşifi'")
            badge = cursor.fetchone()

            if badge:
                cursor.execute(
                    """IF NOT EXISTS (
                           SELECT 1 FROM dbo.UserBadges
                           WHERE user_id=? AND badge_id=?
                       )
                       INSERT INTO dbo.UserBadges (user_id,badge_id)
                       VALUES (?,?)""",
                    kullanici_id,
                    str(badge[0]),
                    kullanici_id,
                    str(badge[0]),
                )

    return {"mesaj": "Beceri eklendi ✅"}