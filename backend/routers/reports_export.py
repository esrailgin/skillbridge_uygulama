from html import escape
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException, Response

from backend.database import db_cursor

router = APIRouter(prefix="/api/raporlar", tags=["raporlar"])

ROLE_LABELS = {
    "student": "Öğrenci",
    "graduate": "Yeni Mezun",
    "candidate": "Kariyer Adayı",
    "mentor": "Mentor",
    "hr_manager": "İK Yöneticisi",
    "professional": "Kariyer Adayı",
}

TITLE_LABELS = {
    "Explorer": "Keşif Aşaması",
    "Junior Pathfinder": "Başlangıç Yolcusu",
    "Associate Analyst": "Genç Analist",
    "Data Analyst": "Veri Analisti",
    "Junior Data Analyst": "Junior Veri Analisti",
    "Career Mentor": "Kariyer Mentoru",
    "Talent Manager": "Yetenek Yöneticisi",
}

STATUS_LABELS = {
    "completed": "Tamamlandı",
    "pending": "Bekliyor",
    "failed": "Başarısız",
    "approved": "Mentor uygun gördü",
    "shortlisted": "İK mülakat listesine aldı",
    "rejected": "Geliştirilmesi önerildi",
    "reviewed": "Mentor değerlendirdi",
}


def _guard(kullanici_id: str, x_user_id: str | None, x_user_role: str | None):
    if x_user_role in ("mentor", "hr_manager"):
        return
    if not x_user_id:
        return
    if str(x_user_id).lower() != str(kullanici_id).lower():
        raise HTTPException(status_code=403, detail="Bu rapora erişim yetkiniz yok.")


def _label_role(role: str | None) -> str:
    return ROLE_LABELS.get(role or "", role or "-")


def _label_title(title: str | None) -> str:
    return TITLE_LABELS.get(title or "", title or "Keşif Aşaması")


def _label_status(status: str | None) -> str:
    return STATUS_LABELS.get(status or "", status or "-")


def _data(kullanici_id: str):
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT full_name, email, role, career_title FROM dbo.Users WHERE id=?",
            kullanici_id,
        )
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

        cursor.execute("SELECT COUNT(*) FROM dbo.CVAnalyses WHERE user_id=?", kullanici_id)
        cv = cursor.fetchone()[0]

        cursor.execute(
            """SELECT TOP 1 file_name, status, skill_gap_score, created_at
               FROM dbo.CVAnalyses
               WHERE user_id=?
               ORDER BY created_at DESC""",
            kullanici_id,
        )
        last_cv = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) FROM dbo.UserSkills WHERE user_id=?", kullanici_id)
        skills = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dbo.UserBadges WHERE user_id=?", kullanici_id)
        badges = cursor.fetchone()[0]

        cursor.execute(
            "SELECT MAX(overall_progress) FROM dbo.Roadmaps WHERE user_id=? AND status='active'",
            kullanici_id,
        )
        progress = cursor.fetchone()[0] or 0

        cursor.execute(
            """SELECT TOP 1 target_role, overall_progress, estimated_weeks
               FROM dbo.Roadmaps
               WHERE user_id=? AND status='active'
               ORDER BY created_at DESC""",
            kullanici_id,
        )
        roadmap = cursor.fetchone()

        cursor.execute(
            """SELECT TOP 1 status, mentor_note, hr_note
               FROM dbo.RoleInteractions
               WHERE requester_id=?
               ORDER BY updated_at DESC, created_at DESC""",
            kullanici_id,
        )
        interaction = cursor.fetchone()

        cursor.execute(
            """IF OBJECT_ID('dbo.GitHubPortfolios', 'U') IS NULL
                   SELECT 0
               ELSE
                   SELECT COUNT(*) FROM dbo.GitHubPortfolios WHERE user_id=? AND status='active'""",
            kullanici_id,
        )
        github = cursor.fetchone()[0]

    last_cv_text = "CV kaydı yok"
    cv_status = "Yok"
    gap_score = 0
    if last_cv:
        cv_status = _label_status(last_cv[1])
        gap_score = float(last_cv[2] or 0)
        last_cv_text = f"{last_cv[0]} / {cv_status} / Gap Skoru: {gap_score:.0f}"

    roadmap_text = "Yol haritası yok"
    target_role = "-"
    if roadmap:
        target_role = _label_title(roadmap[0])
        roadmap_text = f"{target_role} / İlerleme: %{float(roadmap[1] or 0):.0f} / Süre: {roadmap[2] or '-'} hafta"

    interaction_text = "Etkileşim kaydı yok"
    if interaction:
        notes = interaction[1] or interaction[2] or "Not girilmemiş"
        interaction_text = f"{_label_status(interaction[0])} / {notes}"

    progress_value = float(progress)
    profile_score = min(100, int(cv * 20 + min(skills, 10) * 5 + min(badges, 10) * 3 + progress_value * 0.3 + github * 8))

    return {
        "summary": {
            "ad_soyad": user[0],
            "email": user[1],
            "rol": _label_role(user[2]),
            "unvan": _label_title(user[3]),
            "profil_skoru": profile_score,
            "cv": cv,
            "beceri": skills,
            "rozet": badges,
            "ilerleme": progress_value,
            "github": github,
            "cv_durumu": cv_status,
            "gap_skoru": gap_score,
            "hedef_rol": target_role,
        },
        "rows": {
            "Ad Soyad": user[0],
            "E-posta": user[1],
            "Rol": _label_role(user[2]),
            "Kariyer Unvanı": _label_title(user[3]),
            "Profil Skoru": f"%{profile_score}",
            "CV Sayısı": cv,
            "Son CV": last_cv_text,
            "Beceri Sayısı": skills,
            "Rozet Sayısı": badges,
            "Yol Haritası İlerlemesi": f"%{progress_value:.0f}",
            "Aktif Yol Haritası": roadmap_text,
            "Mentor / İK Akışı": interaction_text,
            "GitHub Portfolyo": "Var" if github else "Yok",
        },
    }


def _font_paths() -> tuple[str | None, str | None]:
    regular_candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    bold_candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    regular = next((str(p) for p in regular_candidates if p.exists()), None)
    bold = next((str(p) for p in bold_candidates if p.exists()), None)
    return regular, bold


def _professional_pdf(data: dict) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    regular, bold = _font_paths()
    font = "Helvetica"
    font_bold = "Helvetica-Bold"
    if regular:
        pdfmetrics.registerFont(TTFont("SkillBridgeRegular", regular))
        font = "SkillBridgeRegular"
    if bold:
        pdfmetrics.registerFont(TTFont("SkillBridgeBold", bold))
        font_bold = "SkillBridgeBold"

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="SkillBridge Kariyer Raporu",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "SkillTitle",
        parent=styles["Title"],
        fontName=font_bold,
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#113F3B"),
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "SkillSubtitle",
        parent=styles["BodyText"],
        fontName=font,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#475569"),
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName=font_bold,
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0F3D3A"),
        spaceBefore=8,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyTR",
        parent=styles["BodyText"],
        fontName=font,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1F2937"),
        alignment=TA_LEFT,
    )
    small_style = ParagraphStyle(
        "SmallTR",
        parent=body_style,
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#475569"),
    )
    label_style = ParagraphStyle(
        "LabelTR",
        parent=body_style,
        fontName=font_bold,
        textColor=colors.HexColor("#334155"),
    )

    s = data["summary"]
    story = []

    header = Table(
        [[Paragraph("SkillBridge", title_style)], [Paragraph("Kariyer Gelişim ve Fırsat Raporu", subtitle_style)]],
        colWidths=[178 * mm],
    )
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FBFA")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#D1E7E4")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(header)
    story.append(Spacer(1, 8))

    identity = Table(
        [[
            Paragraph(f"<b>{s['ad_soyad']}</b><br/>{s['email']}", body_style),
            Paragraph(f"Rol<br/><b>{s['rol']}</b>", body_style),
            Paragraph(f"Unvan<br/><b>{s['unvan']}</b>", body_style),
            Paragraph(f"Profil Skoru<br/><b>%{s['profil_skoru']}</b>", body_style),
        ]],
        colWidths=[66 * mm, 36 * mm, 42 * mm, 34 * mm],
    )
    identity.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#E5E7EB")),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E5E7EB")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(identity)
    story.append(Spacer(1, 10))

    metric_data = [[
        Paragraph(f"CV<br/><b>{s['cv']}</b>", body_style),
        Paragraph(f"Beceri<br/><b>{s['beceri']}</b>", body_style),
        Paragraph(f"Rozet<br/><b>{s['rozet']}</b>", body_style),
        Paragraph(f"Yol Haritası<br/><b>%{s['ilerleme']:.0f}</b>", body_style),
    ]]
    metrics = Table(metric_data, colWidths=[44.5 * mm] * 4)
    metrics.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#EEF4FF")),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#ECFDF5")),
        ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#FFF7ED")),
        ("BACKGROUND", (3, 0), (3, 0), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#E5E7EB")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(metrics)

    story.append(Paragraph("Detaylı Profil Özeti", section_style))
    rows = [[Paragraph("Alan", label_style), Paragraph("Değer", label_style)]]
    for key, value in data["rows"].items():
        rows.append([Paragraph(str(key), body_style), Paragraph(str(value), body_style)])
    detail_table = Table(rows, colWidths=[54 * mm, 124 * mm], repeatRows=1)
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#113F3B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#E5E7EB")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FFFFFF")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(detail_table)

    story.append(Paragraph("Yönetici Yorumu", section_style))
    comment = (
        "Bu rapor, adayın CV hazırlığı, beceri derinliği, rozet kanıtı, yol haritası ilerlemesi ve "
        "mentor/İK etkileşimlerini birlikte değerlendirir. Profil skoru yüksek adaylar için fırsat eşleştirme "
        "ve mülakat planlama adımları hızlandırılabilir."
    )
    comment_box = Table([[Paragraph(comment, small_style)]], colWidths=[178 * mm])
    comment_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FBFA")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D1E7E4")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(comment_box)

    story.append(Spacer(1, 8))
    story.append(Paragraph("SkillBridge · Yeteneklerinizi Geliştirin, Başarıya Köprü Kurun", small_style))

    doc.build(story)
    return buffer.getvalue()


def _pdf_escape(text: str) -> str:
    replacements = {
        "ı": "i", "İ": "I", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U",
        "ş": "s", "Ş": "S", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C",
        "–": "-", "—": "-", "“": '"', "”": '"', "’": "'",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _fallback_pdf(data: dict) -> bytes:
    lines = ["SkillBridge Kariyer Raporu", ""]
    lines.extend(f"{k}: {v}" for k, v in data["rows"].items())
    lines.append("")
    lines.append("Not: Backend ortaminda ReportLab yoksa bu sade PDF yedek cikti olarak uretilir.")

    content = ["BT", "/F1 13 Tf", "17 TL", "46 790 Td"]
    for line in lines[:38]:
        safe = _pdf_escape(str(line))[:96]
        content.append(f"({safe}) Tj")
        content.append("T*")
    content.append("ET")
    stream = "\n".join(content).encode("latin-1", "replace")

    objs = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        f"5 0 obj << /Length {len(stream)} >> stream\n".encode("latin-1") + stream + b"\nendstream endobj\n",
    ]
    out = BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = []
    for obj in objs:
        offsets.append(out.tell())
        out.write(obj)
    xref = out.tell()
    out.write(f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode("latin-1"))
    for off in offsets:
        out.write(f"{off:010d} 00000 n \n".encode("latin-1"))
    out.write(f"trailer << /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode("latin-1"))
    return out.getvalue()


def _pdf_bytes(data: dict) -> bytes:
    try:
        return _professional_pdf(data)
    except Exception:
        return _fallback_pdf(data)


@router.get("/{kullanici_id}/excel")
def rapor_excel(kullanici_id: str, x_user_id: str | None = Header(default=None), x_user_role: str | None = Header(default=None)):
    _guard(kullanici_id, x_user_id, x_user_role)
    data = _data(kullanici_id)
    rows = "".join(
        f"<tr><td>{escape(k)}</td><td>{escape(str(v))}</td></tr>"
        for k, v in data["rows"].items()
    )
    html = f"""
    <html><head><meta charset='utf-8'>
    <style>
      body {{ font-family: Segoe UI, Arial, sans-serif; color:#1F2937; }}
      h2 {{ color:#113F3B; }}
      table {{ border-collapse: collapse; width: 100%; }}
      th, td {{ border:1px solid #CBD5E1; padding:8px; }}
      tr:first-child td {{ background:#113F3B; color:white; font-weight:bold; }}
    </style></head><body>
    <h2>SkillBridge Kariyer Raporu</h2>
    <table>{rows}</table>
    </body></html>
    """
    return Response(
        content=html.encode("utf-8"),
        media_type="application/vnd.ms-excel",
        headers={"Content-Disposition": "attachment; filename=skillbridge_rapor.xls"},
    )


@router.get("/{kullanici_id}/pdf")
def rapor_pdf(kullanici_id: str, x_user_id: str | None = Header(default=None), x_user_role: str | None = Header(default=None)):
    _guard(kullanici_id, x_user_id, x_user_role)
    data = _data(kullanici_id)
    return Response(
        content=_pdf_bytes(data),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=skillbridge_rapor.pdf"},
    )

