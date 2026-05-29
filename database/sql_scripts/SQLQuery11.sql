USE SkillBridge;
GO

UPDATE dbo.Users
SET career_title = N'Baþlangýç Yolcusu'
WHERE career_title = N'Junior Pathfinder';

UPDATE dbo.Users
SET career_title = N'Yardýmcý Analist'
WHERE career_title = N'Associate Analyst';

UPDATE dbo.Users
SET career_title = N'Veri Analisti'
WHERE career_title = N'Data Analyst';

UPDATE dbo.Users
SET career_title = N'Kariyer Mentoru'
WHERE career_title = N'Career Mentor';

UPDATE dbo.Users
SET career_title = N'Yetenek Yöneticisi'
WHERE career_title = N'Talent Manager';

UPDATE dbo.Users
SET career_title = N'Keþif Aþamasý'
WHERE career_title = N'Explorer';
GO