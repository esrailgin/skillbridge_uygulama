USE SkillBridge;
GO

IF COL_LENGTH('dbo.CVAnalyses', 'file_path') IS NULL
BEGIN
    ALTER TABLE dbo.CVAnalyses
    ADD file_path NVARCHAR(1000) NULL;
END
GO