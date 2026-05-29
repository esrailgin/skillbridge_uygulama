from fastapi import APIRouter

from backend.database import db_cursor


router = APIRouter(prefix="/api/rozetler", tags=["rozetler"])


@router.get("/{kullanici_id}")
def rozetleri_getir(kullanici_id: str):
    with db_cursor() as cursor:
        cursor.execute(
            """SELECT b.name, b.description, b.icon, b.color, b.type, ub.awarded_at
               FROM dbo.UserBadges ub
               JOIN dbo.Badges b ON b.id=ub.badge_id
               WHERE ub.user_id=?
               ORDER BY ub.awarded_at DESC""",
            kullanici_id,
        )
        kazanilanlar = [
            {
                "ad": r[0],
                "aciklama": r[1],
                "icon": r[2],
                "renk": r[3],
                "tip": r[4],
                "tarih": str(r[5]),
                "kazanildi": True,
            }
            for r in cursor.fetchall()
        ]

        cursor.execute(
            """SELECT b.name, b.description, b.icon, b.color, b.type
               FROM dbo.Badges b
               WHERE b.id NOT IN (
                   SELECT badge_id FROM dbo.UserBadges WHERE user_id=?
               )""",
            kullanici_id,
        )
        kilitliler = [
            {
                "ad": r[0],
                "aciklama": r[1],
                "icon": r[2],
                "renk": r[3],
                "tip": r[4],
                "kazanildi": False,
            }
            for r in cursor.fetchall()
        ]

    return {
        "kazanilan": kazanilanlar,
        "kilitli": kilitliler,
        "toplam_kazanilan": len(kazanilanlar),
    }