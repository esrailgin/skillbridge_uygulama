from pathlib import Path

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFrame, QLabel, QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from desktop.ui.components import baslik, kart


class VizyonSayfasi(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        w = QWidget()
        lo = QVBoxLayout(w)
        lo.setContentsMargins(28, 24, 28, 24)
        lo.setSpacing(16)

        hero = kart()
        hero.setStyleSheet("QFrame#card{background:#F8FBFA;border:1px solid #D7E5E1;border-left:4px solid #0E6B5C;border-radius:8px;}")
        hero_row = QHBoxLayout(hero)
        hero_row.setContentsMargins(22, 18, 22, 18)
        hero_row.setSpacing(18)
        hero_lo = QVBoxLayout()
        bas = QLabel("SkillBridge Vizyonu")
        bas.setStyleSheet("font-size:16pt;font-weight:900;color:#0F3D3A;")
        metin = QLabel("Yeni mezun, mentor ve İK ekiplerini aynı kariyer akışında buluşturan ölçülebilir bir gelişim platformu.")
        metin.setWordWrap(True)
        metin.setStyleSheet("color:#475569;font-size:10pt;")
        hero_lo.addWidget(bas)
        hero_lo.addWidget(metin)
        hero_lo.addStretch()
        hero_row.addLayout(hero_lo, 2)
        img = QLabel()
        img.setFixedSize(330, 132)
        img.setScaledContents(True)
        p = Path(__file__).resolve().parents[1] / "assets" / "vision_panel.png"
        if p.exists():
            img.setPixmap(QPixmap(str(p)))
        hero_row.addWidget(img, 1)
        lo.addWidget(hero)

        row = QHBoxLayout()
        row.setSpacing(14)
        for title, text, color in [
            ("Aday İçin", "CV, beceri, rozet ve yol haritasını tek kariyer profiline dönüştürür.", "#38546E"),
            ("Mentor İçin", "Değerlendirme taleplerini yapılandırır ve adayın hazır oluşunu görünür kılar.", "#0E6B5C"),
            ("İK İçin", "Mentor onaylı adayları şirket fırsatları ve görüşme akışına taşır.", "#B7791F"),
        ]:
            row.addWidget(self._vizyon_karti(title, text, color))
        lo.addLayout(row)

        prensip_krt = kart()
        prensip_krt.setStyleSheet("QFrame#card{background:#FFFFFF;border:1px solid #D7E5E1;border-radius:8px;}")
        prensip_lo = QVBoxLayout(prensip_krt)
        prensip_lo.setContentsMargins(20, 16, 20, 16)
        prensip_lo.setSpacing(10)
        prensip_lo.addWidget(baslik("Ürün Prensipleri", renk="#0F3D3A"))
        for no, madde in enumerate([
            "Her kullanıcı rolü için ayrı ama birbirine bağlı iş akışı.",
            "Kararları sadece metinle değil; ilerleme, beceri ve mentor sinyalleriyle destekleyen ekranlar.",
            "Demo veriden gerçek ürün hissine geçebilecek sade, genişletilebilir yapı.",
        ], start=1):
            lbl = QLabel(f"0{no}  {madde}")
            lbl.setWordWrap(True)
            lbl.setStyleSheet("background:#F8FBFA;color:#1F2937;border:1px solid #E2E8F0;border-left:4px solid #0E6B5C;border-radius:7px;padding:10px;font-size:10pt;font-weight:650;")
            prensip_lo.addWidget(lbl)
        lo.addWidget(prensip_krt)
        quote = QLabel('"Hayatta en hakiki mürşit ilimdir." - Mustafa Kemal Atatürk')
        quote.setWordWrap(True)
        quote.setStyleSheet("color:#64748B;font-size:9pt;font-style:italic;padding:8px 2px;")
        lo.addWidget(quote)
        lo.addStretch()
        scroll.setWidget(w)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    @staticmethod
    def _vizyon_karti(title: str, text: str, color: str) -> QFrame:
        k = kart()
        k.setStyleSheet(f"QFrame#card{{background:#FFFFFF;border:1px solid #E5E7EB;border-top:4px solid {color};border-radius:8px;}}")
        lo = QVBoxLayout(k)
        lo.setContentsMargins(18, 14, 18, 14)
        icon = QLabel("■")
        icon.setStyleSheet(f"color:{color};font-size:15pt;")
        b = QLabel(title)
        b.setStyleSheet("color:#1F2937;font-size:11pt;font-weight:900;")
        m = QLabel(text)
        m.setWordWrap(True)
        m.setStyleSheet("color:#64748B;font-size:9pt;")
        lo.addWidget(icon)
        lo.addWidget(b)
        lo.addWidget(m)
        return k



