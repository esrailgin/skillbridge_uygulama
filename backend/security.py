import hashlib


def sifre_hashle(sifre: str) -> str:
    return hashlib.sha256(sifre.encode("utf-8")).hexdigest()