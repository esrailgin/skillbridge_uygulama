USE SkillBridge;
GO

DECLARE @user_id UNIQUEIDENTIFIER;

IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE email = N'demo@skillbridge.com')
BEGIN
    SET @user_id = NEWID();

    INSERT INTO dbo.Users (
        id, email, full_name, password_hash, role, career_title
    )
    VALUES (
        @user_id,
        N'demo@skillbridge.com',
        N'Demo Kullanýcý',
        N'03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4',
        N'student',
        N'Junior Data Analyst'
    );
END
ELSE
BEGIN
    SELECT @user_id = id
    FROM dbo.Users
    WHERE email = N'demo@skillbridge.com';

    UPDATE dbo.Users
    SET career_title = N'Junior Data Analyst'
    WHERE id = @user_id;
END
GO

DECLARE @user_id UNIQUEIDENTIFIER;
SELECT @user_id = id FROM dbo.Users WHERE email = N'demo@skillbridge.com';

INSERT INTO dbo.CVAnalyses (
    id, user_id, file_name, file_hash, file_size_bytes,
    mime_type, status, ai_model, skill_gap_score, processing_time_ms
)
SELECT
    NEWID(),
    @user_id,
    N'demo_cv.pdf',
    N'demo-cv-hash-001',
    245000,
    N'application/pdf',
    N'completed',
    N'SkillBridge Analyzer',
    72.50,
    1850
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.CVAnalyses
    WHERE user_id = @user_id AND file_hash = N'demo-cv-hash-001'
);

INSERT INTO dbo.UserSkills (id, user_id, skill_id, level, confidence, self_assessed)
SELECT NEWID(), @user_id, id,
       CASE name
            WHEN N'Python' THEN N'intermediate'
            WHEN N'SQL' THEN N'advanced'
            WHEN N'FastAPI' THEN N'intermediate'
            WHEN N'Docker' THEN N'beginner'
            WHEN N'Ýletiþim' THEN N'advanced'
            ELSE N'beginner'
       END,
       0.80,
       1
FROM dbo.SkillsInventory
WHERE name IN (
    N'Python',
    N'SQL',
    N'FastAPI',
    N'Docker',
    N'Ýletiþim',
    N'Takým Çalýþmasý'
)
AND NOT EXISTS (
    SELECT 1
    FROM dbo.UserSkills us
    WHERE us.user_id = @user_id
      AND us.skill_id = dbo.SkillsInventory.id
);

DECLARE @steps NVARCHAR(MAX) = N'[
  {
    "id": "step-1",
    "sira": 1,
    "baslik": "SQL Sorgu Pratiði",
    "aciklama": "JOIN, GROUP BY ve alt sorgularla veri analizi çalýþmasý",
    "saat": 6,
    "durum": "completed",
    "oncelik": "high"
  },
  {
    "id": "step-2",
    "sira": 2,
    "baslik": "Python ile Veri Temizleme",
    "aciklama": "CSV okuma, eksik veri temizleme ve temel analiz",
    "saat": 8,
    "durum": "completed",
    "oncelik": "high"
  },
  {
    "id": "step-3",
    "sira": 3,
    "baslik": "Dashboard Hazýrlama",
    "aciklama": "Temel metrikleri görselleþtiren rapor ekraný oluþturma",
    "saat": 10,
    "durum": "in_progress",
    "oncelik": "medium"
  },
  {
    "id": "step-4",
    "sira": 4,
    "baslik": "API Entegrasyonu",
    "aciklama": "Backend verilerini masaüstü arayüzüne baðlama",
    "saat": 8,
    "durum": "not_started",
    "oncelik": "medium"
  }
]';

IF NOT EXISTS (
    SELECT 1 FROM dbo.Roadmaps
    WHERE user_id = @user_id AND target_role = N'Data Analyst'
)
BEGIN
    INSERT INTO dbo.Roadmaps (
        id, user_id, title, target_role, status,
        overall_progress, estimated_weeks, steps
    )
    VALUES (
        NEWID(),
        @user_id,
        N'Data Analyst Yol Haritasý',
        N'Data Analyst',
        N'active',
        50.00,
        8,
        @steps
    );
END

INSERT INTO dbo.UserBadges (user_id, badge_id)
SELECT @user_id, id
FROM dbo.Badges
WHERE name IN (N'Ýlk Adým', N'Yarý Kahraman')
AND NOT EXISTS (
    SELECT 1
    FROM dbo.UserBadges ub
    WHERE ub.user_id = @user_id
      AND ub.badge_id = dbo.Badges.id
);
GO