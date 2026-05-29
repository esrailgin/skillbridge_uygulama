from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QLabel,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from desktop.api import api_get, api_post
from desktop.ui.components import baslik, kart


class BeceriSayfasi(QWidget):
    def __init__(self, uid: str):
        super().__init__()
        self.uid = uid
        self._skill_ids = {}
        self._build()

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        w = QWidget()
        lo = QVBoxLayout(w)
        lo.setContentsMargins(28, 24, 28, 24)
        lo.setSpacing(16)

        ekle_krt = kart()
        ek_lo = QHBoxLayout(ekle_krt)
        ek_lo.setContentsMargins(16, 12, 16, 12)
        self.skill_combo = QComboBox()
        self.skill_combo.setFixedWidth(220)
        self.level_combo = QComboBox()
        self._level_values = {
            "Başlangıç": "beginner",
            "Orta": "intermediate",
            "İleri": "advanced",
            "Uzman": "expert",
        }
        self.level_combo.addItems(list(self._level_values.keys()))
        self.level_combo.setFixedWidth(140)
        ekle_btn = QPushButton("+ Beceri Ekle")
        ekle_btn.setObjectName("success")
        ekle_btn.clicked.connect(self._beceri_ekle)
        ek_lo.addWidget(QLabel("Beceri:"))
        ek_lo.addWidget(self.skill_combo)
        ek_lo.addSpacing(10)
        ek_lo.addWidget(QLabel("Seviye:"))
        ek_lo.addWidget(self.level_combo)
        ek_lo.addSpacing(10)
        ek_lo.addWidget(ekle_btn)
        ek_lo.addStretch()
        lo.addWidget(ekle_krt)

        lo.addWidget(baslik("Piyasa Beceri Kataloğu", renk="#0F3D3A"))
        self.katalog_lo = QVBoxLayout()
        self.katalog_lo.setSpacing(6)
        lo.addLayout(self.katalog_lo)
        lo.addStretch()

        scroll.setWidget(w)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def yukle(self):
        beceriler = api_get("/api/beceriler")

        while self.katalog_lo.count():
            item = self.katalog_lo.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.skill_combo.clear()
        self._skill_ids = {}

        if not isinstance(beceriler, list):
            return

        renk_map = {
            "technical": "#2563EB",
            "soft": "#0F766E",
            "language": "#D97706",
            "domain": "#7C3AED",
            "tool": "#0284C7",
        }
        kategori_map = {
            "technical": "Teknik",
            "soft": "Sosyal",
            "language": "Dil",
            "domain": "Alan",
            "tool": "Araç",
        }

        for b in beceriler:
            self._skill_ids[b["ad"]] = b["id"]
            self.skill_combo.addItem(b["ad"])

            krt2 = kart()
            krt2_lo = QHBoxLayout(krt2)
            krt2_lo.setContentsMargins(14, 8, 14, 8)

            ad = QLabel(b["ad"])
            ad.setStyleSheet("color:#1F2937;font-size:9pt;font-weight:700;")
            ad.setFixedWidth(170)

            kategori = b.get("kategori", "technical")
            kat_renk = renk_map.get(kategori, "#2563EB")
            kat = QLabel(kategori_map.get(kategori, kategori))
            kat.setStyleSheet(f"color:{kat_renk};font-size:8pt;font-weight:700;")
            kat.setFixedWidth(90)

            talep_val = int(b.get("piyasa_talebi", 0) * 100)
            talep_bar = QProgressBar()
            talep_bar.setRange(0, 100)
            talep_bar.setValue(talep_val)
            talep_bar.setTextVisible(False)
            talep_bar.setFixedHeight(7)
            talep_bar.setStyleSheet(
                f"QProgressBar{{background:#E5E7EB;border-radius:3px;}}"
                f"QProgressBar::chunk{{background:{kat_renk};border-radius:3px;}}"
            )
            talep_lbl = QLabel(f"%{talep_val}")
            talep_lbl.setStyleSheet(f"color:{kat_renk};font-size:8pt;font-weight:700;")
            talep_lbl.setFixedWidth(35)

            krt2_lo.addWidget(ad)
            krt2_lo.addWidget(kat)
            krt2_lo.addWidget(talep_bar, stretch=1)
            krt2_lo.addWidget(talep_lbl)
            self.katalog_lo.addWidget(krt2)

    def _beceri_ekle(self):
        ad = self.skill_combo.currentText()
        sid = self._skill_ids.get(ad)
        if not sid:
            return
        seviye = self._level_values.get(self.level_combo.currentText(), "beginner")
        sonuc = api_post(f"/api/beceriler/{self.uid}/ekle?skill_id={sid}&seviye={seviye}")
        if "hata" in sonuc:
            QMessageBox.warning(self, "Hata", sonuc["hata"])
        else:
            QMessageBox.information(self, "Başarılı", f"{ad} eklendi!")
