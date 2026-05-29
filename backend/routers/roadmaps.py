import json
import uuid

from fastapi import APIRouter, HTTPException

from backend.database import db_cursor
from backend.models import RoadmapAdimModel


router = APIRouter(prefix="/api/roadmap", tags=["roadmap"])


def roadmap_sablonu(hedef_rol: str) -> list[dict]:
    rol = hedef_rol.lower()

    if "veri" in rol or "data" in rol or "analist" in rol:
        plan = [
            ("SQL Sorgu Pratiği", "JOIN, GROUP BY ve alt sorgularla analiz pratiği", 1, 6, "high", "Mini satış raporu çıkar"),
            ("Python ile Veri Temizleme", "CSV okuma, eksik veri temizleme ve temel pandas kullanımı", 2, 8, "high", "Temizlenmiş veri seti oluştur"),
            ("Görselleştirme", "Temel metrikleri grafiklerle açıklama", 3, 6, "medium", "3 grafik içeren rapor hazırla"),
            ("Dashboard Taslağı", "KPI kartları ve tablo görünümü hazırlama", 4, 8, "medium", "Basit dashboard ekranı çıkar"),
            ("Portfolyo Projesi", "Tek bir analiz projesini sunuma hazır hale getirme", 5, 10, "high", "GitHub/rapor çıktısı oluştur"),
            ("Mülakat Hazırlığı", "Teknik sorular ve proje anlatımı çalışması", 6, 5, "medium", "5 dakikalık proje anlatımı yap"),
        ]
    elif "ik" in rol or "hr" in rol or "insan" in rol:
        plan = [
            ("Aday Profili Okuma", "CV, beceri ve kariyer hedefi üzerinden aday değerlendirme", 1, 4, "high", "Aday değerlendirme notu yaz"),
            ("Yetkinlik Matrisi", "Rol için gerekli teknik ve davranışsal yetkinlikleri çıkarma", 2, 6, "high", "Yetkinlik matrisi oluştur"),
            ("Mülakat Planı", "Teknik ve davranışsal görüşme akışı hazırlama", 3, 5, "medium", "Mülakat soru seti hazırla"),
            ("Aday Kıyaslama", "Kısa listeye alınacak adayları karşılaştırma", 4, 6, "medium", "Aday kısa listesi oluştur"),
            ("Raporlama", "İşe alım kararını veriyle destekleme", 5, 5, "low", "Yönetici özeti hazırla"),
        ]
    elif "mentor" in rol:
        plan = [
            ("Profil Değerlendirme", "Adayın güçlü ve gelişime açık yönlerini belirleme", 1, 4, "high", "Mentor notu oluştur"),
            ("Gelişim Planı Yazma", "Adaya kısa vadeli öğrenme hedefleri verme", 2, 5, "high", "3 maddelik gelişim planı yaz"),
            ("CV Geri Bildirimi", "CV düzeni, beceri vurgusu ve proje anlatımını inceleme", 3, 5, "medium", "CV iyileştirme listesi çıkar"),
            ("Simülasyon Görüşmesi", "Adaya rol bazlı pratik yaptırma", 4, 6, "medium", "Görüşme notu kaydet"),
        ]
    else:
        plan = [
            ("Hedef Rol Analizi", "Rolün gerektirdiği temel becerileri belirleme", 1, 4, "high", "Beceri ihtiyaç listesi çıkar"),
            ("Mevcut Durum Değerlendirmesi", "CV ve beceri profiline göre eksikleri belirleme", 2, 5, "high", "Gap analizi notu oluştur"),
            ("Temel Beceri Çalışması", "Eksik görülen iki ana beceriye odaklanma", 3, 8, "medium", "Öğrenme notları hazırla"),
            ("Uygulamalı Mini Proje", "Hedef role uygun küçük bir çıktı üretme", 4, 10, "high", "Mini proje tamamla"),
            ("Sunum ve Mülakat Hazırlığı", "Üretilen çıktıyı kısa ve net anlatma", 5, 5, "medium", "Proje sunumu hazırla"),
        ]

    return [
        {
            "id": str(uuid.uuid4()),
            "sira": i,
            "baslik": baslik,
            "aciklama": aciklama,
            "hafta": hafta,
            "saat": saat,
            "durum": "not_started",
            "oncelik": oncelik,
            "cikti": cikti,
        }
        for i, (baslik, aciklama, hafta, saat, oncelik, cikti) in enumerate(plan, start=1)
    ]


@router.get("/{kullanici_id}")
def roadmap_getir(kullanici_id: str):
    with db_cursor() as cursor:
        cursor.execute(
            """SELECT id, title, target_role, status, overall_progress, estimated_weeks, steps
               FROM dbo.Roadmaps
               WHERE user_id=?
               ORDER BY created_at DESC""",
            kullanici_id,
        )
        satirlar = cursor.fetchall()

    return [
        {
            "id": str(s[0]),
            "baslik": s[1],
            "hedef_rol": s[2],
            "durum": s[3],
            "ilerleme": float(s[4] or 0),
            "tahmini_hafta": s[5],
            "adimlar": json.loads(s[6]) if s[6] else [],
        }
        for s in satirlar
    ]


@router.post("/{kullanici_id}/olustur")
def roadmap_olustur(kullanici_id: str, hedef_rol: str, hafta: int = 8):
    adimlar = roadmap_sablonu(hedef_rol)
    yeni_id = str(uuid.uuid4())
    tahmini_hafta = max(hafta, max(a.get("hafta", 1) for a in adimlar))

    with db_cursor(commit=True) as cursor:
        cursor.execute(
            """UPDATE dbo.Roadmaps
               SET status='archived', updated_at=GETUTCDATE()
               WHERE user_id=? AND status='active'""",
            kullanici_id,
        )
        cursor.execute(
            """INSERT INTO dbo.Roadmaps
               (id, user_id, title, target_role, status, overall_progress, estimated_weeks, steps)
               VALUES (?,?,?,?,?,?,?,?)""",
            yeni_id,
            kullanici_id,
            f"{hedef_rol} Yol Haritası",
            hedef_rol,
            "active",
            0,
            tahmini_hafta,
            json.dumps(adimlar, ensure_ascii=False),
        )

    return {
        "roadmap_id": yeni_id,
        "mesaj": "Yol haritası oluşturuldu.",
        "adimlar": adimlar,
    }


@router.patch("/adim-guncelle")
def adim_guncelle(data: RoadmapAdimModel):
    with db_cursor(commit=True) as cursor:
        cursor.execute("SELECT user_id, steps FROM dbo.Roadmaps WHERE id=?", data.roadmap_id)
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Roadmap bulunamadı.")

        uid = str(row[0])
        adimlar = json.loads(row[1]) if row[1] else []
        bulundu = False
        for adim in adimlar:
            if adim["id"] == data.adim_id:
                adim["durum"] = data.durum
                bulundu = True
                break

        if not bulundu:
            raise HTTPException(status_code=404, detail="Roadmap adımı bulunamadı.")

        tamamlanan = sum(1 for a in adimlar if a["durum"] == "completed")
        ilerleyen = sum(1 for a in adimlar if a["durum"] == "in_progress")
        ilerleme = round((tamamlanan / len(adimlar)) * 100, 1) if adimlar else 0

        cursor.execute(
            """UPDATE dbo.Roadmaps
               SET steps=?, overall_progress=?, updated_at=GETUTCDATE()
               WHERE id=?""",
            json.dumps(adimlar, ensure_ascii=False),
            ilerleme,
            data.roadmap_id,
        )

        if ilerleme >= 100:
            unvan = "Hedefe Hazır Aday"
        elif ilerleme >= 50:
            unvan = "Planlı Gelişen Aday"
        elif ilerleyen > 0 or tamamlanan > 0:
            unvan = "Yol Haritasında İlerliyor"
        else:
            unvan = None

        if unvan:
            cursor.execute(
                "UPDATE dbo.Users SET career_title=?, updated_at=GETUTCDATE() WHERE id=?",
                unvan,
                uid,
            )

        if ilerleme >= 50:
            cursor.execute("SELECT id FROM dbo.Badges WHERE name=N'Yarı Kahraman'")
            badge = cursor.fetchone()
            if badge:
                cursor.execute(
                    """IF NOT EXISTS (
                           SELECT 1 FROM dbo.UserBadges
                           WHERE user_id=? AND badge_id=?
                       )
                       INSERT INTO dbo.UserBadges (user_id,badge_id)
                       VALUES (?,?)""",
                    uid,
                    str(badge[0]),
                    uid,
                    str(badge[0]),
                )

    return {"mesaj": "Adım güncellendi.", "genel_ilerleme": ilerleme}


def portfolyo_adimini_tamamla(cursor, kullanici_id: str):
    cursor.execute(
        """SELECT TOP 1 id, steps
           FROM dbo.Roadmaps
           WHERE user_id=? AND status='active'
           ORDER BY created_at DESC""",
        kullanici_id,
    )
    row = cursor.fetchone()
    if not row:
        return
    roadmap_id = row[0]
    adimlar = json.loads(row[1]) if row[1] else []
    changed = False
    for adim in adimlar:
        text = f"{adim.get('baslik', '')} {adim.get('cikti', '')}".lower()
        if "portfolyo" in text or "github" in text:
            if adim.get("durum") != "completed":
                adim["durum"] = "completed"
                changed = True
            break
    if not changed:
        return
    tamamlanan = sum(1 for a in adimlar if a.get("durum") == "completed")
    ilerleme = round((tamamlanan / len(adimlar)) * 100, 1) if adimlar else 0
    cursor.execute(
        """UPDATE dbo.Roadmaps
           SET steps=?, overall_progress=?, updated_at=GETUTCDATE()
           WHERE id=?""",
        json.dumps(adimlar, ensure_ascii=False),
        ilerleme,
        roadmap_id,
    )
