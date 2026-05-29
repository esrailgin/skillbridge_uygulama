import hashlib
import json

from fastapi import APIRouter

from backend.database import db_cursor

router = APIRouter(prefix="/api/demo", tags=["demo"])


BADGES = [
    ("İlk Adım", "Sisteme kayıt oldun.", "🌱", "#10B981", "milestone"),
    ("Beceri Kaşifi", "Beceri profilini genişlettin.", "🏆", "#F59E0B", "skill"),
    ("Yarı Kahraman", "Yol haritasında yüzde 50 eşiğini geçtin.", "⭐", "#6366F1", "roadmap"),
    ("CV Hazır", "CV analizini tamamladın.", "📄", "#2563EB", "cv"),
    ("SQL Temeli", "SQL yetkinliğini profiline ekledin.", "🗄", "#0F766E", "skill"),
    ("Python Başlangıcı", "Python öğrenme yoluna girdin.", "🐍", "#16A34A", "skill"),
    ("Veri Hikayecisi", "Veriden anlamlı çıktı üretmeye başladın.", "📊", "#0284C7", "skill"),
    ("Portfolyo Hazır", "Portfolyo çalışmanı tamamladın.", "🧩", "#7C3AED", "portfolio"),
    ("Mentor Onayı", "Mentordan olumlu değerlendirme aldın.", "🤝", "#0F766E", "mentor"),
    ("Mülakat Hazırlığı", "İK sürecine hazır hale geldin.", "💬", "#D97706", "hr"),
    ("Yol Takipçisi", "Roadmap adımlarını düzenli takip ettin.", "🗺", "#334155", "roadmap"),
    ("Takım Oyuncusu", "Takım çalışması becerisini öne çıkardın.", "👥", "#0891B2", "soft"),
    ("Analitik Düşünür", "Problemleri veriyle çözme becerisi gösterdin.", "🧠", "#B91C1C", "skill"),
]

SKILLS = [
    ("Python", "python", "technical", 0.95, 0.90),
    ("SQL", "sql", "technical", 0.90, 0.85),
    ("FastAPI", "fastapi", "technical", 0.72, 0.78),
    ("Docker", "docker", "tool", 0.82, 0.80),
    ("Power BI", "power-bi", "tool", 0.80, 0.76),
    ("Excel", "excel", "tool", 0.84, 0.70),
    ("Veri Görselleştirme", "veri-gorsellestirme", "domain", 0.82, 0.78),
    ("Problem Çözme", "problem-cozme", "soft", 0.86, 0.74),
    ("İletişim", "iletisim", "soft", 0.85, 0.70),
    ("Takım Çalışması", "takim-calismasi", "soft", 0.88, 0.72),
]


def _fetch_id(cursor, sql: str, *params):
    cursor.execute(sql, *params)
    row = cursor.fetchone()
    return row[0] if row else None


@router.post("/yenile")
def demo_yenile():
    pwd = hashlib.sha256("1234".encode()).hexdigest()

    with db_cursor(commit=True) as cursor:
        for name, desc, icon, color, typ in BADGES:
            cursor.execute(
                """IF NOT EXISTS (SELECT 1 FROM dbo.Badges WHERE name=?)
                   INSERT INTO dbo.Badges (name, description, icon, color, type)
                   VALUES (?, ?, ?, ?, ?)""",
                name,
                name,
                desc,
                icon,
                color,
                typ,
            )

        for name, slug, category, demand, trend in SKILLS:
            cursor.execute(
                """IF NOT EXISTS (SELECT 1 FROM dbo.SkillsInventory WHERE name=?)
                   INSERT INTO dbo.SkillsInventory (name, slug, category, market_demand, trend_score, is_active)
                   VALUES (?, ?, ?, ?, ?, 1)""",
                name,
                name,
                slug,
                category,
                demand,
                trend,
            )

        email = "mezun@skillbridge.com"
        cursor.execute(
            """IF EXISTS (SELECT 1 FROM dbo.Users WHERE email=?)
                   UPDATE dbo.Users
                   SET full_name=N'Yeni Mezun Demo', role='graduate', career_title=N'Yıldızı Parlayan Yeni Mezun',
                       password_hash=?, deleted_at=NULL, is_active=1, updated_at=GETUTCDATE()
                   WHERE email=?
               ELSE
                   INSERT INTO dbo.Users (id, email, full_name, password_hash, role, career_title)
                   VALUES (NEWID(), ?, N'Yeni Mezun Demo', ?, 'graduate', N'Yıldızı Parlayan Yeni Mezun')""",
            email,
            pwd,
            email,
            email,
            pwd,
        )

        uid = _fetch_id(cursor, "SELECT id FROM dbo.Users WHERE email=?", email)

        for name, *_rest in BADGES:
            badge_id = _fetch_id(cursor, "SELECT id FROM dbo.Badges WHERE name=?", name)
            cursor.execute(
                """IF NOT EXISTS (SELECT 1 FROM dbo.UserBadges WHERE user_id=? AND badge_id=?)
                   INSERT INTO dbo.UserBadges (user_id, badge_id) VALUES (?, ?)""",
                uid,
                badge_id,
                uid,
                badge_id,
            )

        skill_levels = {
            "Python": "intermediate",
            "SQL": "advanced",
            "FastAPI": "intermediate",
            "Docker": "beginner",
            "Power BI": "intermediate",
            "Excel": "advanced",
            "Veri Görselleştirme": "intermediate",
            "Problem Çözme": "advanced",
            "İletişim": "advanced",
            "Takım Çalışması": "advanced",
        }
        for skill_name, level in skill_levels.items():
            skill_id = _fetch_id(cursor, "SELECT id FROM dbo.SkillsInventory WHERE name=?", skill_name)
            cursor.execute(
                """IF EXISTS (SELECT 1 FROM dbo.UserSkills WHERE user_id=? AND skill_id=?)
                       UPDATE dbo.UserSkills SET level=?, confidence=0.86, self_assessed=1 WHERE user_id=? AND skill_id=?
                   ELSE
                       INSERT INTO dbo.UserSkills (id, user_id, skill_id, level, confidence, self_assessed)
                       VALUES (NEWID(), ?, ?, ?, 0.86, 1)""",
                uid,
                skill_id,
                level,
                uid,
                skill_id,
                uid,
                skill_id,
                level,
            )

        cursor.execute(
            """IF EXISTS (SELECT 1 FROM dbo.CVAnalyses WHERE user_id=? AND file_hash='demo-mezun-v2')
                   UPDATE dbo.CVAnalyses
                   SET status='completed', skill_gap_score=82, processing_time_ms=1420,
                       analysis_result=N'Demo yeni mezun profili: teknik temel güçlü, portfolyo ve mülakat hazırlığı tamamlanmış.',
                       updated_at=GETUTCDATE()
                   WHERE user_id=? AND file_hash='demo-mezun-v2'
               ELSE
                   INSERT INTO dbo.CVAnalyses (id, user_id, file_name, file_hash, file_size_bytes, mime_type, status, ai_model, analysis_result, skill_gap_score, processing_time_ms)
                   VALUES (NEWID(), ?, N'yeni_mezun_demo_cv.pdf', 'demo-mezun-v2', 268000, N'application/pdf', 'completed', N'SkillBridge Analyzer',
                           N'Demo yeni mezun profili: teknik temel güçlü, portfolyo ve mülakat hazırlığı tamamlanmış.', 82, 1420)""",
            uid,
            uid,
            uid,
        )

        steps = [
            {"id": "mezun-1", "sira": 1, "baslik": "CV ve Profil Tamamlama", "aciklama": "CV analizi, beceri profili ve rozet akışı tamamlandı.", "saat": 4, "durum": "completed", "oncelik": "high"},
            {"id": "mezun-2", "sira": 2, "baslik": "SQL Portfolyo Projesi", "aciklama": "Veri temizleme ve raporlama örneği hazırlandı.", "saat": 8, "durum": "completed", "oncelik": "high"},
            {"id": "mezun-3", "sira": 3, "baslik": "Power BI Dashboard", "aciklama": "Görsel analiz raporu portfolyoya eklendi.", "saat": 10, "durum": "completed", "oncelik": "medium"},
            {"id": "mezun-4", "sira": 4, "baslik": "Mentor Değerlendirmesi", "aciklama": "Mentor profil uygunluğunu onayladı.", "saat": 2, "durum": "completed", "oncelik": "high"},
            {"id": "mezun-5", "sira": 5, "baslik": "Mülakat Simülasyonu", "aciklama": "Teknik ve davranışsal sorular için prova yapılacak.", "saat": 6, "durum": "in_progress", "oncelik": "medium"},
            {"id": "mezun-6", "sira": 6, "baslik": "İK Görüşmesi", "aciklama": "Kısa listeye alınan aday için görüşme planlanacak.", "saat": 3, "durum": "not_started", "oncelik": "medium"},
        ]
        steps_json = json.dumps(steps, ensure_ascii=False)
        cursor.execute(
            """IF EXISTS (SELECT 1 FROM dbo.Roadmaps WHERE user_id=? AND target_role=N'Junior Veri Analisti')
                   UPDATE dbo.Roadmaps
                   SET title=N'Junior Veri Analisti Yol Haritası', status='active', overall_progress=67,
                       estimated_weeks=6, steps=?, updated_at=GETUTCDATE()
                   WHERE user_id=? AND target_role=N'Junior Veri Analisti'
               ELSE
                   INSERT INTO dbo.Roadmaps (id, user_id, title, target_role, status, overall_progress, estimated_weeks, steps)
                   VALUES (NEWID(), ?, N'Junior Veri Analisti Yol Haritası', N'Junior Veri Analisti', 'active', 67, 6, ?)""",
            uid,
            steps_json,
            uid,
            uid,
            steps_json,
        )

        cursor.execute(
            """IF EXISTS (SELECT 1 FROM dbo.RoleInteractions WHERE requester_id=?)
                   UPDATE dbo.RoleInteractions
                   SET status='approved', note=N'Demo profilim için mentor değerlendirmesi istiyorum.',
                       mentor_note=N'Yeni mezun profili güçlü. Junior Veri Analisti pozisyonları için İK havuzuna önerilir.',
                       updated_at=GETUTCDATE()
                   WHERE requester_id=?
               ELSE
                   INSERT INTO dbo.RoleInteractions (requester_id, target_role, status, note, mentor_note)
                   VALUES (?, 'mentor', 'approved', N'Demo profilim için mentor değerlendirmesi istiyorum.',
                           N'Yeni mezun profili güçlü. Junior Veri Analisti pozisyonları için İK havuzuna önerilir.')""",
            uid,
            uid,
            uid,
        )


        cursor.execute(
            """IF OBJECT_ID('dbo.GitHubPortfolios', 'U') IS NULL
               CREATE TABLE dbo.GitHubPortfolios (
                   id UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID() PRIMARY KEY,
                   user_id UNIQUEIDENTIFIER NOT NULL,
                   owner NVARCHAR(120) NOT NULL,
                   repo NVARCHAR(160) NOT NULL,
                   repo_url NVARCHAR(500) NOT NULL,
                   target_role NVARCHAR(160) NULL,
                   portfolio_score INT NOT NULL DEFAULT 82,
                   status NVARCHAR(40) NOT NULL DEFAULT 'active',
                   created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
                   updated_at DATETIME2 NULL
               )"""
        )
        cursor.execute(
            """IF EXISTS (SELECT 1 FROM dbo.GitHubPortfolios WHERE user_id=? AND owner='microsoft' AND repo='Data-Science-For-Beginners')
                   UPDATE dbo.GitHubPortfolios
                   SET target_role=N'Junior Veri Analisti', portfolio_score=88, status='active', updated_at=GETUTCDATE()
                   WHERE user_id=? AND owner='microsoft' AND repo='Data-Science-For-Beginners'
               ELSE
                   INSERT INTO dbo.GitHubPortfolios (user_id, owner, repo, repo_url, target_role, portfolio_score)
                   VALUES (?, 'microsoft', 'Data-Science-For-Beginners', 'https://github.com/microsoft/Data-Science-For-Beginners', N'Junior Veri Analisti', 88)""",
            uid,
            uid,
            uid,
        )
    return {"mesaj": "Yeni Mezun demo hesabı 13 rozet, CV, beceri, yol haritası, GitHub portfolyo kaydı ve mentor akışıyla zenginleştirildi."}




