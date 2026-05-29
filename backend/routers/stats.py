from fastapi import APIRouter

from backend.database import db_cursor


router = APIRouter(prefix="/api/istatistik", tags=["istatistik"])


@router.get("/{kullanici_id}")
def istatistik_getir(kullanici_id: str):
    with db_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM dbo.CVAnalyses WHERE user_id=?", kullanici_id)
        cv_sayisi = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dbo.UserSkills WHERE user_id=?", kullanici_id)
        beceri_sayisi = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dbo.UserBadges WHERE user_id=?", kullanici_id)
        rozet_sayisi = cursor.fetchone()[0]

        cursor.execute(
            """SELECT MAX(overall_progress)
               FROM dbo.Roadmaps
               WHERE user_id=? AND status='active'""",
            kullanici_id,
        )
        ilerleme = cursor.fetchone()[0] or 0

        cursor.execute("""IF OBJECT_ID('dbo.GitHubPortfolios', 'U') IS NULL
                   SELECT 0
               ELSE
                   SELECT COUNT(*) FROM dbo.GitHubPortfolios WHERE user_id=? AND status='active'""", kullanici_id)
        portfolyo_sayisi = cursor.fetchone()[0]

        cursor.execute("SELECT career_title FROM dbo.Users WHERE id=?", kullanici_id)
        unvan_row = cursor.fetchone()
        unvan = unvan_row[0] if unvan_row else "Explorer"

    return {
        "cv_sayisi": cv_sayisi,
        "beceri_sayisi": beceri_sayisi,
        "rozet_sayisi": rozet_sayisi,
        "genel_ilerleme": float(ilerleme),
        "career_title": unvan,
        "portfolyo_sayisi": portfolyo_sayisi,
    }
