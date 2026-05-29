from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QMainWindow,
    QPushButton,
    QHBoxLayout,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import desktop.config as config
from desktop.screens.badges import RozetSayfasi
from desktop.screens.career_center import GelisimMerkeziSayfasi
from desktop.screens.cv import CVSayfasi
from desktop.screens.dashboard import DashboardSayfasi
from desktop.screens.contact import IletisimSayfasi
from desktop.screens.integrations import GitHubEntegrasyonSayfasi
from desktop.screens.interactions import EtkilesimSayfasi
from desktop.screens.opportunities import FirsatlarSayfasi
from desktop.screens.login import GirisEkrani
from desktop.screens.reports import RaporlarSayfasi
from desktop.screens.roadmap import RoadmapSayfasi
from desktop.screens.skills import BeceriSayfasi
from desktop.screens.vision import VizyonSayfasi


class AnaPencere(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SkillBridge - Kariyer Gelişim Sistemi")
        self.setMinimumSize(1280, 800)
        self.setStyleSheet(config.STYLE)
        self._build()

    def _build(self):
        self.yigin = QStackedWidget()
        self.giris_ekrani = GirisEkrani()
        self.giris_ekrani.giris_basarili.connect(self._giris_sonrasi)
        self.yigin.addWidget(self.giris_ekrani)
        self.setCentralWidget(self.yigin)

    def _giris_sonrasi(self, kullanici: dict):
        config.OTURUM = kullanici
        self.ana = AnaEkran(kullanici)
        self.ana.cikis_istendi.connect(self._cikis_yap)
        self.yigin.addWidget(self.ana)
        self.yigin.setCurrentWidget(self.ana)

    def _cikis_yap(self):
        config.OTURUM = {}
        self.yigin.setCurrentWidget(self.giris_ekrani)

        if hasattr(self, "ana"):
            self.yigin.removeWidget(self.ana)
            self.ana.deleteLater()
            del self.ana


class AnaEkran(QWidget):
    cikis_istendi = pyqtSignal()

    def __init__(self, kullanici: dict):
        super().__init__()
        self.kullanici = kullanici
        self.rol = kullanici.get("rol", "")
        self._aktif_nav = "dashboard"
        self.page_map = {}
        self.nav_btns = {}
        self._build()
        self._navigate("dashboard")

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sb = QFrame()
        sb.setObjectName("sidebar")
        sb.setFixedWidth(235)
        sb_lo = QVBoxLayout(sb)
        sb_lo.setContentsMargins(12, 0, 12, 20)
        sb_lo.setSpacing(4)

        logo = QLabel("⬡  SkillBridge")
        logo.setStyleSheet(
            "font-size:15pt;font-weight:700;color:#A3E635;"
            "padding:22px 8px 14px 8px;"
        )
        sb_lo.addWidget(logo)

        for key, label in self._nav_items():
            btn = QPushButton(label)
            btn.setObjectName("ghost")
            btn.setStyleSheet(self._nav_style(False))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._navigate(k))
            self.nav_btns[key] = btn
            sb_lo.addWidget(btn)

        sb_lo.addStretch()

        cikis_btn = QPushButton("⎋   Çıkış Yap")
        cikis_btn.setObjectName("ghost")
        cikis_btn.setStyleSheet(self._nav_style(False))
        cikis_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cikis_btn.clicked.connect(self.cikis_istendi.emit)
        sb_lo.addWidget(cikis_btn)
        sb_lo.addSpacing(8)

        unvan = QLabel(f"🌱 {self._unvan_tr(self.kullanici.get('career_title', 'Keşif Aşaması'))}")
        unvan.setStyleSheet("color:#A3E635;font-size:9pt;font-weight:700;padding:6px 8px;")
        sb_lo.addWidget(unvan)

        kullanici_lbl = QLabel(
            f"👤 {self.kullanici.get('ad_soyad', '')}\n"
            f"   {self._rol_etiketi(self.rol)}"
        )
        kullanici_lbl.setStyleSheet("color:#CBD5E1;font-size:8pt;padding:4px 8px;")
        sb_lo.addWidget(kullanici_lbl)
        root.addWidget(sb)

        icerik = QWidget()
        ic_lo = QVBoxLayout(icerik)
        ic_lo.setContentsMargins(0, 0, 0, 0)
        ic_lo.setSpacing(0)

        self.header = QFrame()
        self.header.setFixedHeight(56)
        self.header.setStyleSheet("background:#FFFFFF;border-bottom:1px solid #E5E7EB;")
        h_lo = QHBoxLayout(self.header)
        h_lo.setContentsMargins(24, 0, 24, 0)

        self.sayfa_basligi = QLabel("Dashboard")
        self.sayfa_basligi.setStyleSheet("font-size:13pt;font-weight:700;color:#111827;")
        h_lo.addWidget(self.sayfa_basligi)
        h_lo.addStretch()

        yenile_btn = QPushButton("↻  Yenile")
        yenile_btn.setObjectName("ghost")
        yenile_btn.setFixedWidth(90)
        yenile_btn.clicked.connect(self._sayfayi_yenile)
        h_lo.addWidget(yenile_btn)

        ic_lo.addWidget(self.header)

        self.sayfalar = QStackedWidget()
        self._sayfalari_olustur()

        ic_lo.addWidget(self.sayfalar)
        root.addWidget(icerik, stretch=1)

    def _sayfalari_olustur(self):
        uid = self.kullanici.get("kullanici_id", "")

        sayfa_factory = {
            "dashboard": lambda: DashboardSayfasi(uid, self.kullanici),
            "gelisim": lambda: GelisimMerkeziSayfasi(self.kullanici),
            "cv": lambda: CVSayfasi(uid),
            "roadmap": lambda: RoadmapSayfasi(uid),
            "beceriler": lambda: BeceriSayfasi(uid),
            "rozetler": lambda: RozetSayfasi(uid),
            "etkilesimler": lambda: EtkilesimSayfasi(self.kullanici),
            "github": lambda: GitHubEntegrasyonSayfasi(self.kullanici),
            "firsatlar": lambda: FirsatlarSayfasi(self.kullanici),
            "raporlar": lambda: RaporlarSayfasi(self.kullanici),
            "vizyon": lambda: VizyonSayfasi(),
            "iletisim": lambda: IletisimSayfasi(self.kullanici),
        }

        for key, _label in self._nav_items():
            sayfa = sayfa_factory[key]()
            index = self.sayfalar.addWidget(sayfa)
            self.page_map[key] = index

    def _nav_items(self):
        aday_menusu = [
            ("dashboard", "⬡   Dashboard"),
            ("gelisim", "✦   Gelişim Merkezi"),
            ("cv", "◈   CV Analizi"),
            ("roadmap", "◎   Yol Haritası"),
            ("beceriler", "◉   Beceriler"),
            ("rozetler", "🏆  Rozetlerim"),
            ("etkilesimler", "◇   Talepler"),
            ("github", "⌘   GitHub"),
            ("firsatlar", "◌   Fırsatlar"),
            ("raporlar", "▣   Raporlar"),
            ("vizyon", "✧   Vizyon"),
            ("iletisim", "☎   İletişim"),
        ]

        mentor_menusu = [
            ("dashboard", "⬡   Dashboard"),
            ("gelisim", "✦   Gelişim Merkezi"),
            ("beceriler", "◉   Beceriler"),
            ("etkilesimler", "◇   Talepler"),
            ("github", "⌘   GitHub"),
            ("firsatlar", "◌   Fırsatlar"),
            ("raporlar", "▣   Raporlar"),
            ("vizyon", "✧   Vizyon"),
            ("iletisim", "☎   İletişim"),
        ]

        ik_menusu = [
            ("dashboard", "⬡   Dashboard"),
            ("gelisim", "✦   Gelişim Merkezi"),
            ("etkilesimler", "◇   Talepler"),
            ("github", "⌘   GitHub"),
            ("firsatlar", "◌   Fırsatlar"),
            ("raporlar", "▣   Raporlar"),
            ("vizyon", "✧   Vizyon"),
            ("iletisim", "☎   İletişim"),
        ]

        if self.rol == "mentor":
            return mentor_menusu
        if self.rol == "hr_manager":
            return ik_menusu
        return aday_menusu

    def _navigate(self, key: str):
        titles = {
            "dashboard": "Dashboard",
            "gelisim": "Gelişim Merkezi",
            "cv": "CV Analizi",
            "roadmap": "Yol Haritası",
            "beceriler": "Beceriler",
            "rozetler": "Rozetlerim",
            "etkilesimler": "Talepler",
            "github": "GitHub Entegrasyonu",
            "firsatlar": "Fırsatlar",
            "raporlar": "Raporlar",
            "vizyon": "Vizyon",
            "iletisim": "İletişim",
        }

        if key not in self.page_map:
            key = "dashboard"

        self.sayfalar.setCurrentIndex(self.page_map[key])
        self.sayfa_basligi.setText(titles.get(key, ""))
        self._aktif_nav = key

        for k, btn in self.nav_btns.items():
            btn.setStyleSheet(self._nav_style(k == key))

        self._sayfayi_yenile()

    def _sayfayi_yenile(self):
        sayfa = self.sayfalar.currentWidget()
        if hasattr(sayfa, "yukle"):
            sayfa.yukle()

    @staticmethod
    def _nav_style(aktif: bool) -> str:
        if aktif:
            return (
                "QPushButton{background:#1F2937;border:none;"
                "border-left:3px solid #A3E635;border-radius:8px;"
                "padding:10px 14px;text-align:left;color:#F9FAFB;"
                "font-size:10pt;font-weight:600;}"
            )

        return (
            "QPushButton{background:transparent;border:none;"
            "border-radius:8px;padding:10px 14px;text-align:left;"
            "color:#CBD5E1;font-size:10pt;}"
            "QPushButton:hover{background:#1F2937;color:#FFFFFF;}"
        )

    @staticmethod
    def _rol_etiketi(rol: str) -> str:
        return {
            "student": "Öğrenci",
            "graduate": "Yeni Mezun",
            "candidate": "Kariyer Adayı",
            "mentor": "Mentor",
            "hr_manager": "İK Yöneticisi",
            "professional": "Kariyer Adayı",
        }.get(rol, rol)

    @staticmethod
    def _unvan_tr(unvan: str) -> str:
        return {
            "Explorer": "Keşif Aşaması",
            "Junior Pathfinder": "Başlangıç Yolcusu",
            "Associate Analyst": "Genç Analist",
            "Data Analyst": "Veri Analisti",
            "Junior Data Analyst": "Junior Veri Analisti",
            "Career Mentor": "Kariyer Mentoru",
            "Talent Manager": "Yetenek Yöneticisi",
        }.get(unvan, unvan)








