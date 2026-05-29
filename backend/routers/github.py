import re
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

from backend.database import db_cursor
from backend.routers.roadmaps import portfolyo_adimini_tamamla

router = APIRouter(prefix="/api/github", tags=["github"])


class GitHubBaglanti(BaseModel):
    kullanici_id: str
    repo_url: str
    hedef_rol: str | None = None


_GITHUB_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def _ensure_table(cursor):
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


def _repo_kimligi(repo_url: str) -> tuple[str, str]:
    temiz = repo_url.strip().removesuffix(".git")
    if not temiz:
        raise HTTPException(status_code=400, detail="GitHub repo adresi boş olamaz.")
    if _GITHUB_RE.match(temiz):
        owner, repo = temiz.split("/", 1)
        return owner, repo
    parsed = urlparse(temiz)
    host = parsed.netloc.lower()
    if host not in ("github.com", "www.github.com"):
        raise HTTPException(status_code=400, detail="Sadece github.com repo adresleri desteklenir.")
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Repo adresi owner/repo formatında olmalı.")
    owner, repo = parts[0], parts[1]
    if not _GITHUB_RE.match(f"{owner}/{repo}"):
        raise HTTPException(status_code=400, detail="Repo adı geçerli GitHub formatında değil.")
    return owner, repo



def _github_metrikleri(owner: str, repo: str) -> dict:
    try:
        with httpx.Client(timeout=4) as client:
            r = client.get(f"https://api.github.com/repos/{owner}/{repo}")
            if r.status_code != 200:
                return {"canli": False, "not": "GitHub API yanıtı alınamadı."}
            data = r.json()
            readme = client.get(f"https://api.github.com/repos/{owner}/{repo}/readme")
            return {
                "canli": True,
                "yildiz": data.get("stargazers_count", 0),
                "fork": data.get("forks_count", 0),
                "dil": data.get("language") or "Belirtilmemiş",
                "readme": readme.status_code == 200,
            }
    except Exception:
        return {"canli": False, "not": "Ağ erişimi yoksa demo metrikleri kullanılabilir."}
def _response(owner: str, repo: str, hedef: str, score: int = 82):
    repo_adi = repo.replace("-", " ").replace("_", " ").title()
    metrikler = _github_metrikleri(owner, repo)
    return {
        "durum": "baglandi",
        "owner": owner,
        "repo": repo,
        "repo_adi": repo_adi,
        "repo_url": f"https://github.com/{owner}/{repo}",
        "hedef_rol": hedef,
        "portfolyo_puani": score,
        "etiketler": ["GitHub", "Portfolyo", "Teknik Kanıt"],
        "metrikler": metrikler,
        "onerilen_aksiyonlar": [
            "README dosyasına problem, çözüm ve kullanılan teknolojileri ekle.",
            "Proje çıktısını CV analizi ve yol haritasındaki portfolyo adımıyla eşleştir.",
            "Mentor değerlendirmesinde repo bağlantısını teknik kanıt olarak paylaş.",
        ],
        "sinyaller": [
            "Repo adresi geçerli ve portfolyo profiline bağlandı.",
            "README, proje amacı ve ekran görüntüleri İK değerlendirmesinde görünür olmalı.",
            "Commit geçmişi, teknik beceriler ve yol haritası çıktılarıyla birlikte yorumlanmalı.",
        ],
    }


@router.post("/bagla")
def github_bagla(payload: GitHubBaglanti):
    owner, repo = _repo_kimligi(payload.repo_url)
    hedef = payload.hedef_rol or "Portfolyo Rolü"
    repo_url = f"https://github.com/{owner}/{repo}"
    with db_cursor(commit=True) as cursor:
        _ensure_table(cursor)
        cursor.execute(
            """IF EXISTS (SELECT 1 FROM dbo.GitHubPortfolios WHERE user_id=? AND owner=? AND repo=?)
                   UPDATE dbo.GitHubPortfolios
                   SET repo_url=?, target_role=?, portfolio_score=82, status='active', updated_at=GETUTCDATE()
                   WHERE user_id=? AND owner=? AND repo=?
               ELSE
                   INSERT INTO dbo.GitHubPortfolios (user_id, owner, repo, repo_url, target_role, portfolio_score)
                   VALUES (?, ?, ?, ?, ?, 82)""",
            payload.kullanici_id, owner, repo,
            repo_url, hedef,
            payload.kullanici_id, owner, repo,
            payload.kullanici_id, owner, repo, repo_url, hedef,
        )
        portfolyo_adimini_tamamla(cursor, payload.kullanici_id)
    return _response(owner, repo, hedef)


@router.get("/{kullanici_id}")
def github_portfolyolari(kullanici_id: str):
    with db_cursor(commit=True) as cursor:
        _ensure_table(cursor)
        cursor.execute(
            """SELECT owner, repo, repo_url, target_role, portfolio_score, status, created_at
               FROM dbo.GitHubPortfolios
               WHERE user_id=? AND status='active'
               ORDER BY updated_at DESC, created_at DESC""",
            kullanici_id,
        )
        rows = cursor.fetchall()
    return [
        {
            "owner": r[0],
            "repo": r[1],
            "repo_url": r[2],
            "hedef_rol": r[3],
            "portfolyo_puani": int(r[4] or 0),
            "durum": r[5],
            "tarih": str(r[6]),
        }
        for r in rows
    ]


