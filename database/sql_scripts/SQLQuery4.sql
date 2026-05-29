USE master;
GO

IF DB_ID(N'SkillBridge') IS NULL
BEGIN
    CREATE DATABASE SkillBridge;
END
GO

USE SkillBridge;
GO

DROP TABLE IF EXISTS dbo.UserBadges;
DROP TABLE IF EXISTS dbo.UserSkills;
DROP TABLE IF EXISTS dbo.Roadmaps;
DROP TABLE IF EXISTS dbo.CVAnalyses;
DROP TABLE IF EXISTS dbo.AuditLog;
DROP TABLE IF EXISTS dbo.Badges;
DROP TABLE IF EXISTS dbo.SkillsInventory;
DROP TABLE IF EXISTS dbo.Users;
GO

CREATE TABLE dbo.Users (
    id              UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    email           NVARCHAR(255) NOT NULL UNIQUE,
    full_name       NVARCHAR(255) NOT NULL,
    password_hash   NVARCHAR(500) NOT NULL,
    role            NVARCHAR(50) NOT NULL DEFAULT 'student',
    is_active       BIT NOT NULL DEFAULT 1,
    mfa_enabled     BIT NOT NULL DEFAULT 0,
    mfa_secret      NVARCHAR(500) NULL,
    career_title    NVARCHAR(100) NULL DEFAULT 'Explorer',
    created_at      DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at      DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    deleted_at      DATETIME2 NULL
);
GO

CREATE TABLE dbo.SkillsInventory (
    id              UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    name            NVARCHAR(200) NOT NULL UNIQUE,
    slug            NVARCHAR(200) NOT NULL UNIQUE,
    category        NVARCHAR(50) NOT NULL DEFAULT 'technical',
    market_demand   DECIMAL(3,2) NULL DEFAULT 0.5,
    trend_score     DECIMAL(3,2) NULL DEFAULT 0.5,
    is_active       BIT NOT NULL DEFAULT 1,
    created_at      DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);
GO

CREATE TABLE dbo.Badges (
    id              UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    name            NVARCHAR(200) NOT NULL UNIQUE,
    description     NVARCHAR(MAX) NULL,
    icon            NVARCHAR(20) NULL,
    color           NVARCHAR(20) NULL,
    type            NVARCHAR(50) NOT NULL DEFAULT 'milestone',
    created_at      DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);
GO

CREATE TABLE dbo.CVAnalyses (
    id                  UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id             UNIQUEIDENTIFIER NOT NULL REFERENCES dbo.Users(id),
    file_name           NVARCHAR(500) NOT NULL,
    file_hash           NVARCHAR(64) NOT NULL,
    file_size_bytes     INT NULL,
    mime_type           NVARCHAR(200) NULL,
    raw_text            NVARCHAR(MAX) NULL,
    status              NVARCHAR(50) NOT NULL DEFAULT 'pending',
    ai_model            NVARCHAR(100) NULL,
    analysis_result     NVARCHAR(MAX) NULL,
    skill_gap_score     DECIMAL(5,2) NULL,
    processing_time_ms  INT NULL,
    error_message       NVARCHAR(MAX) NULL,
    is_primary          BIT NOT NULL DEFAULT 0,
    created_at          DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at          DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT UQ_CVAnalyses_User_FileHash UNIQUE (user_id, file_hash)
);
GO

CREATE TABLE dbo.UserSkills (
    id               UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id          UNIQUEIDENTIFIER NOT NULL REFERENCES dbo.Users(id),
    skill_id         UNIQUEIDENTIFIER NOT NULL REFERENCES dbo.SkillsInventory(id),
    cv_analysis_id   UNIQUEIDENTIFIER NULL REFERENCES dbo.CVAnalyses(id),
    level            NVARCHAR(50) NOT NULL DEFAULT 'beginner',
    confidence       DECIMAL(3,2) NULL DEFAULT 0.5,
    self_assessed    BIT NOT NULL DEFAULT 0,
    created_at       DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT UQ_UserSkills_User_Skill UNIQUE (user_id, skill_id)
);
GO

CREATE TABLE dbo.Roadmaps (
    id                UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id           UNIQUEIDENTIFIER NOT NULL REFERENCES dbo.Users(id),
    cv_analysis_id    UNIQUEIDENTIFIER NULL REFERENCES dbo.CVAnalyses(id),
    title             NVARCHAR(500) NOT NULL,
    target_role       NVARCHAR(200) NULL,
    status            NVARCHAR(50) NOT NULL DEFAULT 'active',
    overall_progress  DECIMAL(5,2) NOT NULL DEFAULT 0,
    estimated_weeks   INT NULL,
    steps             NVARCHAR(MAX) NULL,
    ai_generated      BIT NOT NULL DEFAULT 1,
    created_at        DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at        DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);
GO

CREATE TABLE dbo.UserBadges (
    user_id     UNIQUEIDENTIFIER NOT NULL REFERENCES dbo.Users(id),
    badge_id    UNIQUEIDENTIFIER NOT NULL REFERENCES dbo.Badges(id),
    awarded_at  DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    PRIMARY KEY (user_id, badge_id)
);
GO

CREATE TABLE dbo.AuditLog (
    id          BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id     UNIQUEIDENTIFIER NULL REFERENCES dbo.Users(id),
    action      NVARCHAR(100) NOT NULL,
    table_name  NVARCHAR(100) NULL,
    record_id   UNIQUEIDENTIFIER NULL,
    ip_address  NVARCHAR(50) NULL,
    created_at  DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);
GO

INSERT INTO dbo.Badges (name, description, icon, color, type)
VALUES
(N'İlk Adım', N'Sisteme kayıt oldun.', N'🌱', N'#10B981', N'milestone'),
(N'Beceri Kaşifi', N'10 beceri ekledin.', N'🏆', N'#F59E0B', N'skill'),
(N'Yarı Kahraman', N'Roadmap ilerlemen yüzde 50 seviyesine ulaştı.', N'⭐', N'#6366F1', N'roadmap');
GO

INSERT INTO dbo.SkillsInventory (name, slug, category, market_demand, trend_score)
VALUES
(N'Python', N'python', N'technical', 0.95, 0.90),
(N'SQL', N'sql', N'technical', 0.90, 0.85),
(N'Docker', N'docker', N'tool', 0.82, 0.80),
(N'Kubernetes', N'kubernetes', N'tool', 0.78, 0.84),
(N'Redis', N'redis', N'tool', 0.70, 0.72),
(N'Apache Kafka', N'apache-kafka', N'tool', 0.75, 0.80),
(N'FastAPI', N'fastapi', N'technical', 0.72, 0.78),
(N'PyQt6', N'pyqt6', N'technical', 0.50, 0.45),
(N'İletişim', N'iletisim', N'soft', 0.85, 0.70),
(N'Takım Çalışması', N'takim-calismasi', N'soft', 0.88, 0.72);
GO

SELECT 'SkillBridge database hazır' AS durum;
GO