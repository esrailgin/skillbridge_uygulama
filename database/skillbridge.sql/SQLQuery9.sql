USE SkillBridge;
GO

SELECT u.email, COUNT(cv.id) AS cv, COUNT(us.id) AS beceri, COUNT(r.id) AS roadmap
FROM dbo.Users u
LEFT JOIN dbo.CVAnalyses cv ON cv.user_id = u.id
LEFT JOIN dbo.UserSkills us ON us.user_id = u.id
LEFT JOIN dbo.Roadmaps r ON r.user_id = u.id
GROUP BY u.email;