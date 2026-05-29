from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from backend.database import db_cursor

router = APIRouter(prefix="/api/destek", tags=["destek"])


class DestekTalebi(BaseModel):
    kullanici_id: str | None = None
    ad_soyad: str
    email: str | None = None
    rol: str | None = None
    kategori: str
    konu: str
    mesaj: str


def _ensure_table(cursor):
    cursor.execute(
        """IF OBJECT_ID('dbo.SupportTickets', 'U') IS NULL
           CREATE TABLE dbo.SupportTickets (
               id UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID() PRIMARY KEY,
               user_id UNIQUEIDENTIFIER NULL,
               full_name NVARCHAR(255) NOT NULL,
               email NVARCHAR(255) NULL,
               role NVARCHAR(50) NULL,
               category NVARCHAR(80) NOT NULL,
               subject NVARCHAR(220) NOT NULL,
               message NVARCHAR(MAX) NOT NULL,
               status NVARCHAR(40) NOT NULL DEFAULT 'open',
               created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
               updated_at DATETIME2 NULL
           )"""
    )


def _row(r) -> dict:
    return {
        "id": str(r[0]),
        "kullanici_id": str(r[1]) if r[1] else None,
        "ad_soyad": r[2],
        "email": r[3],
        "rol": r[4],
        "kategori": r[5],
        "konu": r[6],
        "mesaj": r[7],
        "durum": r[8],
        "tarih": str(r[9]),
    }


@router.post("/talep")
def talep_olustur(data: DestekTalebi):
    if not data.ad_soyad.strip() or not data.konu.strip() or not data.mesaj.strip():
        raise HTTPException(400, "Ad soyad, konu ve mesaj alanları zorunludur.")
    with db_cursor(commit=True) as cursor:
        _ensure_table(cursor)
        cursor.execute(
            """INSERT INTO dbo.SupportTickets
               (user_id, full_name, email, role, category, subject, message)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            data.kullanici_id,
            data.ad_soyad.strip(),
            data.email,
            data.rol,
            data.kategori,
            data.konu.strip(),
            data.mesaj.strip(),
        )
        cursor.execute("SELECT TOP 1 id FROM dbo.SupportTickets ORDER BY created_at DESC")
        ticket_id = cursor.fetchone()[0]
    return {"mesaj": "Destek talebi kaydedildi.", "talep_id": str(ticket_id)}


@router.get("/kullanici/{kullanici_id}")
def kullanici_talepleri(kullanici_id: str):
    with db_cursor(commit=True) as cursor:
        _ensure_table(cursor)
        cursor.execute(
            """SELECT TOP 10 id, user_id, full_name, email, role, category, subject, message, status, created_at
               FROM dbo.SupportTickets
               WHERE user_id=?
               ORDER BY created_at DESC""",
            kullanici_id,
        )
        rows = cursor.fetchall()
    return [_row(r) for r in rows]


@router.get("")
def talepleri_getir(x_user_role: str | None = Header(default=None)):
    if x_user_role not in ("mentor", "hr_manager"):
        raise HTTPException(403, "Destek talepleri listesi yalnızca yetkili roller içindir.")
    with db_cursor(commit=True) as cursor:
        _ensure_table(cursor)
        cursor.execute(
            """SELECT TOP 25 id, user_id, full_name, email, role, category, subject, message, status, created_at
               FROM dbo.SupportTickets
               ORDER BY created_at DESC"""
        )
        rows = cursor.fetchall()
    return [_row(r) for r in rows]
