import httpx

from .config import API, OTURUM


def api_headers() -> dict:
    return {
        "X-User-Id": str(OTURUM.get("kullanici_id", "")),
        "X-User-Role": str(OTURUM.get("rol", "")),
    }


def api_get(path: str) -> dict | list:
    try:
        r = httpx.get(f"{API}{path}", headers=api_headers(), timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"hata": str(e)}


def api_post(path: str, data: dict = None) -> dict:
    try:
        r = httpx.post(f"{API}{path}", json=data, headers=api_headers(), timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"hata": str(e)}


def api_patch(path: str, data: dict = None) -> dict:
    try:
        r = httpx.patch(f"{API}{path}", json=data, headers=api_headers(), timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"hata": str(e)}
