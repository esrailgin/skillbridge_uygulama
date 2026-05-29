USE SkillBridge;
GO

DECLARE @pwd NVARCHAR(500) =
N'03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4';

DECLARE @DemoUsers TABLE (
    email NVARCHAR(255),
    full_name NVARCHAR(255),
    role NVARCHAR(50),
    career_title NVARCHAR(100),
    target_role NVARCHAR(200),
    progress DECIMAL(5,2)
);

INSERT INTO @DemoUsers VALUES
(N'ogrenci@skillbridge.com', N'Öðrenci Demo', N'student', N'Junior Pathfinder', N'Veri Analisti', 35),
(N'mezun@skillbridge.com', N'Yeni Mezun Demo', N'graduate', N'Associate Analyst', N'Junior Data Analyst', 50),
(N'kariyer@skillbridge.com', N'Kariyer Adayý Demo', N'candidate', N'Data Analyst', N'Data Analyst', 65),
(N'mentor@skillbridge.com', N'Mentor Demo', N'mentor', N'Career Mentor', N'Teknik Mentor', 80),
(N'ik@skillbridge.com', N'ÝK Yöneticisi Demo', N'hr_manager', N'Talent Manager', N'ÝK Analitiði Uzmaný', 45);

MERGE dbo.Users AS target
USING @DemoUsers AS source
ON target.email = source.email
WHEN MATCHED THEN
    UPDATE SET
        full_name = source.full_name,
        role = source.role,
        career_title = source.career_title,
        deleted_at = NULL
WHEN NOT MATCHED THEN
    INSERT (id, email, full_name, password_hash, role, career_title)
    VALUES (NEWID(), source.email, source.full_name, @pwd, source.role, source.career_title);
GO

DECLARE @email NVARCHAR(255);
DECLARE @uid UNIQUEIDENTIFIER;
DECLARE @target NVARCHAR(200);
DECLARE @progress DECIMAL(5,2);

DECLARE demo_cursor CURSOR FOR
SELECT email, target_role, progress
FROM (
    VALUES
    (N'ogrenci@skillbridge.com', N'Veri Analisti', 35),
    (N'mezun@skillbridge.com', N'Junior Data Analyst', 50),
    (N'kariyer@skillbridge.com', N'Data Analyst', 65),
    (N'mentor@skillbridge.com', N'Teknik Mentor', 80),
    (N'ik@skillbridge.com', N'ÝK Analitiði Uzmaný', 45)
) AS d(email, target_role, progress);

OPEN demo_cursor;
FETCH NEXT FROM demo_cursor INTO @email, @target, @progress;

WHILE @@FETCH_STATUS = 0
BEGIN
    SELECT @uid = id FROM dbo.Users WHERE email = @email;

    IF NOT EXISTS (
        SELECT 1 FROM dbo.CVAnalyses
        WHERE user_id = @uid AND file_hash = CONCAT(N'demo-', @email)
    )
    BEGIN
        INSERT INTO dbo.CVAnalyses (
            id, user_id, file_name, file_hash, file_size_bytes,
            mime_type, status, ai_model, skill_gap_score, processing_time_ms
        )
        VALUES (
            NEWID(), @uid, N'demo_cv.pdf', CONCAT(N'demo-', @email),
            245000, N'application/pdf', N'completed',
            N'SkillBridge Analyzer', 70.00, 1850
        );
    END

    INSERT INTO dbo.UserSkills (id, user_id, skill_id, level, confidence, self_assessed)
    SELECT NEWID(), @uid, si.id,
           CASE
                WHEN si.name IN (N'SQL', N'Ýletiþim') THEN N'advanced'
                WHEN si.name IN (N'Python', N'FastAPI', N'Takým Çalýþmasý') THEN N'intermediate'
                ELSE N'beginner'
           END,
           0.82,
           1
    FROM dbo.SkillsInventory si
    WHERE si.name IN (
        N'Python',
        N'SQL',
        N'Docker',
        N'FastAPI',
        N'Ýletiþim',
        N'Takým Çalýþmasý'
    )
    AND NOT EXISTS (
        SELECT 1 FROM dbo.UserSkills us
        WHERE us.user_id = @uid AND us.skill_id = si.id
    );

    DECLARE @steps NVARCHAR(MAX) = N'[
      {
        "id": "step-1",
        "sira": 1,
        "baslik": "Temel Yetkinlik Analizi",
        "aciklama": "Mevcut becerilerin hedef role göre deðerlendirilmesi",
        "saat": 4,
        "durum": "completed",
        "oncelik": "high"
      },
      {
        "id": "step-2",
        "sira": 2,
        "baslik": "SQL ve Veri Okuryazarlýðý",
        "aciklama": "Veri sorgulama, filtreleme ve raporlama pratiði",
        "saat": 8,
        "durum": "completed",
        "oncelik": "high"
      },
      {
        "id": "step-3",
        "sira": 3,
        "baslik": "Portfolyo Çalýþmasý",
        "aciklama": "Hedef role uygun örnek proje hazýrlanmasý",
        "saat": 10,
        "durum": "in_progress",
        "oncelik": "medium"
      },
      {
        "id": "step-4",
        "sira": 4,
        "baslik": "Mülakat Hazýrlýðý",
        "aciklama": "Teknik ve davranýþsal görüþme pratiði",
        "saat": 6,
        "durum": "not_started",
        "oncelik": "medium"
      }
    ]';

    IF NOT EXISTS (
        SELECT 1 FROM dbo.Roadmaps
        WHERE user_id = @uid AND target_role = @target
    )
    BEGIN
        INSERT INTO dbo.Roadmaps (
            id, user_id, title, target_role, status,
            overall_progress, estimated_weeks, steps
        )
        VALUES (
            NEWID(), @uid,
            CONCAT(@target, N' Yol Haritasý'),
            @target,
            N'active',
            @progress,
            8,
            @steps
        );
    END

    INSERT INTO dbo.UserBadges (user_id, badge_id)
    SELECT @uid, b.id
    FROM dbo.Badges b
    WHERE b.name IN (N'Ýlk Adým', N'Yarý Kahraman')
    AND NOT EXISTS (
        SELECT 1 FROM dbo.UserBadges ub
        WHERE ub.user_id = @uid AND ub.badge_id = b.id
    );

    FETCH NEXT FROM demo_cursor INTO @email, @target, @progress;
END

CLOSE demo_cursor;
DEALLOCATE demo_cursor;
GO