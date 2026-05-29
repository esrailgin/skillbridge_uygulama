from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import auth, badges, cv, demo, github, health, interactions, opportunities, reports_export, roadmaps, skills, stats, support, users

app = FastAPI(title="SkillBridge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(cv.router)
app.include_router(skills.router)
app.include_router(roadmaps.router)
app.include_router(badges.router)
app.include_router(stats.router)
app.include_router(interactions.router)
app.include_router(github.router)
app.include_router(opportunities.router)
app.include_router(reports_export.router)
app.include_router(demo.router)
app.include_router(support.router)





