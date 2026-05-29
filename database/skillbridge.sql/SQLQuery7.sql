USE SkillBridge;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE email = N'ogrenci@skillbridge.com')
INSERT INTO dbo.Users (id, email, full_name, password_hash, role, career_title)
VALUES (NEWID(), N'ogrenci@skillbridge.com', N'Öðrenci Demo',
N'03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4',
N'student', N'Junior Pathfinder');

IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE email = N'mezun@skillbridge.com')
INSERT INTO dbo.Users (id, email, full_name, password_hash, role, career_title)
VALUES (NEWID(), N'mezun@skillbridge.com', N'Yeni Mezun Demo',
N'03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4',
N'graduate', N'Associate Analyst');

IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE email = N'kariyer@skillbridge.com')
INSERT INTO dbo.Users (id, email, full_name, password_hash, role, career_title)
VALUES (NEWID(), N'kariyer@skillbridge.com', N'Kariyer Adayý Demo',
N'03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4',
N'candidate', N'Data Analyst');

IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE email = N'mentor@skillbridge.com')
INSERT INTO dbo.Users (id, email, full_name, password_hash, role, career_title)
VALUES (NEWID(), N'mentor@skillbridge.com', N'Mentor Demo',
N'03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4',
N'mentor', N'Career Mentor');

IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE email = N'ik@skillbridge.com')
INSERT INTO dbo.Users (id, email, full_name, password_hash, role, career_title)
VALUES (NEWID(), N'ik@skillbridge.com', N'ÝK Yöneticisi Demo',
N'03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4',
N'hr_manager', N'Talent Manager');
GO