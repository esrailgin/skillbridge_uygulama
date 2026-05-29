USE SkillBridge;
GO

IF OBJECT_ID(N'dbo.RoleInteractions', N'U') IS NULL
CREATE TABLE dbo.RoleInteractions (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    requester_id UNIQUEIDENTIFIER NOT NULL REFERENCES dbo.Users(id),
    target_role NVARCHAR(50) NOT NULL,
    status NVARCHAR(50) NOT NULL DEFAULT 'pending',
    note NVARCHAR(MAX) NULL,
    mentor_note NVARCHAR(MAX) NULL,
    hr_note NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);
GO