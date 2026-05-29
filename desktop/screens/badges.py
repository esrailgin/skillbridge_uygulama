from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from desktop.api import api_get
from desktop.ui.components import baslik, kart


class RozetSayfasi(QWidget):
    def __init__(self, uid: str):
        super().__init__()
        self.uid = uid
        self._build()

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        w = QWidget()
        lo = QVBoxLayout(w)
        lo.setContentsMargins(28, 24, 28, 24)
        lo.setSpacing(18)

        self.unvan_krt = kart()
        self.unvan_krt.setStyleSheet(
            "QFrame#card{background:#FFFFFF;"
            "border:1px solid #D1E7E4;border-left:4px solid #0F766E;"
            "border-radius:8px;}"
        )
        uk_lo = QHBoxLayout(self.unvan_krt)
        uk_lo.setContentsMargins(24, 18, 24, 18)
        self.unvan_lbl = QLabel("🌱  Başlangıç Yolcusu")
        self.unvan_lbl.setStyleSheet("font-size:16pt;font-weight:700;color:#0F3D3A;")
        self.rozet_say = QLabel("0 rozet kazanıldı")
        self.rozet_say.setStyleSheet("color:#64748B;font-size:9pt;font-weight:600;")
        uk_lo.addWidget(self.unvan_lbl, stretch=1)
        uk_lo.addWidget(self.rozet_say)
        lo.addWidget(self.unvan_krt)

        lo.addWidget(baslik("Kazanılan Rozetler", renk="#0F3D3A"))
        self.kazanilan_grid = QGridLayout()
        self.kazanilan_grid.setHorizontalSpacing(12)
        self.kazanilan_grid.setVerticalSpacing(12)
        lo.addLayout(self.kazanilan_grid)

        lo.addWidget(baslik("Kilitli Rozetler", renk="#64748B"))
        self.kilitli_grid = QGridLayout()
        self.kilitli_grid.setHorizontalSpacing(12)
        self.kilitli_grid.setVerticalSpacing(12)
        lo.addLayout(self.kilitli_grid)
        lo.addStretch()

        scroll.setWidget(w)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def yukle(self):
        veri = api_get(f"/api/rozetler/{self.uid}")
        if "hata" in veri:
            return

        ist = api_get(f"/api/istatistik/{self.uid}")
        if "hata" not in ist:
            self.unvan_lbl.setText(f"🌱  {self._unvan_tr(ist.get('career_title', 'Keşif Aşaması'))}")

        self._grid_temizle(self.kazanilan_grid)
        self._grid_temizle(self.kilitli_grid)

        kazanilan = veri.get("kazanilan", [])
        kilitli = veri.get("kilitli", [])
        self.rozet_say.setText(f"{len(kazanilan)} rozet kazanıldı")

        self._rozetleri_yerlestir(self.kazanilan_grid, kazanilan, True)
        self._rozetleri_yerlestir(self.kilitli_grid, kilitli[:12], False)

        if not kazanilan:
            bos = QLabel("Henüz kazanılmış rozet yok.")
            bos.setStyleSheet("color:#64748B;font-size:9pt;")
            self.kazanilan_grid.addWidget(bos, 0, 0)

    def _rozetleri_yerlestir(self, grid: QGridLayout, rozetler: list, kazanildi: bool):
        kolon = 4
        for i, rozet in enumerate(rozetler):
            grid.addWidget(self._rozet_karti(rozet, kazanildi), i // kolon, i % kolon)

    @staticmethod
    def _grid_temizle(grid: QGridLayout):
        while grid.count():
            item = grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    @staticmethod
    def _unvan_tr(unvan: str) -> str:
        return {
            "Explorer": "Keşif Aşaması",
            "Junior Pathfinder": "Başlangıç Yolcusu",
            "Associate Analyst": "Genç Analist",
            "Data Analyst": "Veri Analisti",
            "Career Mentor": "Kariyer Mentoru",
            "Talent Manager": "Yetenek Yöneticisi",
            "Yıldızı Parlayan Yeni Mezun": "Yıldızı Parlayan Yeni Mezun",
        }.get(unvan, unvan)

    def _rozet_karti(self, b: dict, kazanildi: bool) -> QFrame:
        renk = b.get("renk", "#0F766E")
        krt2 = QFrame()
        krt2.setObjectName("card")
        if kazanildi:
            krt2.setStyleSheet(
                f"QFrame#card{{background:#FFFFFF;"
                f"border:1px solid {renk};border-top:4px solid {renk};"
                f"border-radius:8px;}}"
            )
        else:
            krt2.setStyleSheet(
                "QFrame#card{background:#F8FAFC;"
                "border:1px dashed #CBD5E1;border-radius:8px;}"
            )
        krt2.setFixedWidth(170)
        krt2.setMinimumHeight(138)

        kl = QVBoxLayout(krt2)
        kl.setContentsMargins(14, 12, 14, 12)
        kl.setSpacing(6)

        ikon = QLabel(b.get("icon", "🏆") if kazanildi else "🔒")
        ikon.setStyleSheet("font-size:22pt;")
        ikon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ad = QLabel(b.get("ad", ""))
        ad.setStyleSheet("font-weight:700;color:#1F2937;font-size:9pt;")
        ad.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ad.setWordWrap(True)

        ack = QLabel(b.get("aciklama", ""))
        ack.setStyleSheet("color:#64748B;font-size:8pt;")
        ack.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ack.setWordWrap(True)

        kl.addWidget(ikon)
        kl.addWidget(ad)
        kl.addWidget(ack)
        return krt2
