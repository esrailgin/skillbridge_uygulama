from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from backend.database import db_cursor

router = APIRouter(prefix="/api/firsatlar", tags=["firsatlar"])


class FirsatAksiyon(BaseModel):
    kullanici_id: str
    sirket: str
    rol: str
    not_metni: str | None = None

DEFAULTS = [
    ("Anka Veri", "Junior Veri Analisti", "Kısa liste", "İstanbul / Hibrit", 86, "Maslak Istanbul", "SQL, Excel ve Power BI temeli güçlü yeni mezun profilleri için giriş seviyesi analiz ekibi."),
    ("Mavi Bulut Teknoloji", "İş Zekası Stajyeri", "Mentor onayı bekliyor", "Ankara / Uzaktan", 78, "ODTU Teknokent Ankara", "Dashboard hazırlama, veri temizleme ve raporlama pratikleri olan adaylar öncelikli."),
    ("Kuzey Finans", "Raporlama Uzman Yardımcısı", "Görüşme planlanacak", "İzmir / Ofis", 73, "Konak Izmir", "Finansal raporlama, Excel ve iletişim becerilerini birlikte kullanan başlangıç rolü."),
]


def _ensure_table(cursor):
    cursor.execute(
        """IF OBJECT_ID('dbo.Opportunities', 'U') IS NULL
           CREATE TABLE dbo.Opportunities (
               id UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID() PRIMARY KEY,
               company_name NVARCHAR(180) NOT NULL,
               role_title NVARCHAR(180) NOT NULL,
               status_label NVARCHAR(120) NOT NULL,
               city NVARCHAR(120) NOT NULL,
               match_score INT NOT NULL,
               map_query NVARCHAR(240) NOT NULL,
               description NVARCHAR(700) NOT NULL,
               is_active BIT NOT NULL DEFAULT 1,
               created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE()
           )"""
    )
    cursor.execute(
        """IF OBJECT_ID('dbo.OpportunityApplications', 'U') IS NULL
           CREATE TABLE dbo.OpportunityApplications (
               id UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID() PRIMARY KEY,
               user_id UNIQUEIDENTIFIER NOT NULL,
               company_name NVARCHAR(180) NOT NULL,
               role_title NVARCHAR(180) NOT NULL,
               status NVARCHAR(40) NOT NULL DEFAULT 'applied',
               note NVARCHAR(500) NULL,
               created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
               updated_at DATETIME2 NULL
           )"""
    )
    for row in DEFAULTS:
        cursor.execute(
            """IF NOT EXISTS (SELECT 1 FROM dbo.Opportunities WHERE company_name=? AND role_title=?)
               INSERT INTO dbo.Opportunities (company_name, role_title, status_label, city, match_score, map_query, description)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            row[0], row[1], *row,
        )


@router.get("")
def firsatlari_getir():
    with db_cursor(commit=True) as cursor:
        _ensure_table(cursor)
        cursor.execute(
            """SELECT company_name, role_title, status_label, city, match_score, map_query, description
               FROM dbo.Opportunities
               WHERE is_active=1
               ORDER BY match_score DESC"""
        )
        rows = cursor.fetchall()
    return [
        {
            "sirket": r[0],
            "rol": r[1],
            "durum": r[2],
            "sehir": r[3],
            "uyum": int(r[4] or 0),
            "konum": r[5],
            "aciklama": r[6],
        }
        for r in rows
    ]


@router.post("/basvur")
def firsata_basvur(data: FirsatAksiyon, x_user_role: str | None = Header(default=None)):
    if x_user_role in ("mentor", "hr_manager"):
        raise HTTPException(403, "Bu işlem aday rolleri içindir.")
    with db_cursor(commit=True) as cursor:
        _ensure_table(cursor)
        cursor.execute(
            """IF EXISTS (SELECT 1 FROM dbo.OpportunityApplications WHERE user_id=? AND company_name=? AND role_title=?)
                   UPDATE dbo.OpportunityApplications
                   SET status='applied', note=?, updated_at=GETUTCDATE()
                   WHERE user_id=? AND company_name=? AND role_title=?
               ELSE
                   INSERT INTO dbo.OpportunityApplications (user_id, company_name, role_title, status, note)
                   VALUES (?, ?, ?, 'applied', ?)""",
            data.kullanici_id, data.sirket, data.rol,
            data.not_metni,
            data.kullanici_id, data.sirket, data.rol,
            data.kullanici_id, data.sirket, data.rol, data.not_metni,
        )
    return {"mesaj": "Fırsat başvurusu kaydedildi."}


@router.post("/eslestir")
def firsata_eslestir(data: FirsatAksiyon, x_user_role: str | None = Header(default=None)):
    if x_user_role != "hr_manager":
        raise HTTPException(403, "Bu işlem yalnızca İK rolüyle yapılabilir.")
    with db_cursor(commit=True) as cursor:
        _ensure_table(cursor)
        cursor.execute(
            """IF EXISTS (SELECT 1 FROM dbo.OpportunityApplications WHERE user_id=? AND company_name=? AND role_title=?)
                   UPDATE dbo.OpportunityApplications
                   SET status='matched', note=?, updated_at=GETUTCDATE()
                   WHERE user_id=? AND company_name=? AND role_title=?
               ELSE
                   INSERT INTO dbo.OpportunityApplications (user_id, company_name, role_title, status, note)
                   VALUES (?, ?, ?, 'matched', ?)""",
            data.kullanici_id, data.sirket, data.rol,
            data.not_metni,
            data.kullanici_id, data.sirket, data.rol,
            data.kullanici_id, data.sirket, data.rol, data.not_metni,
        )
    return {"mesaj": "Aday şirket fırsatıyla eşleştirildi."}


@router.get("/basvurular/{kullanici_id}")
def firsat_basvurulari(kullanici_id: str):
    with db_cursor(commit=True) as cursor:
        _ensure_table(cursor)
        cursor.execute(
            """SELECT company_name, role_title, status, note, created_at
               FROM dbo.OpportunityApplications
               WHERE user_id=?
               ORDER BY updated_at DESC, created_at DESC""",
            kullanici_id,
        )
        rows = cursor.fetchall()
    return [
        {"sirket": r[0], "rol": r[1], "durum": r[2], "not": r[3], "tarih": str(r[4])}
        for r in rows
    ]

