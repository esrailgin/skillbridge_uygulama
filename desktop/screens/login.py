from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from desktop.api import api_get, api_post


ROL_MAP = {
    "Öğrenci": "student",
    "Yeni Mezun": "graduate",
    "Kariyer Adayı": "candidate",
    "Mentor": "mentor",
    "İK Yöneticisi": "hr_manager",
}

DEMO_HESAPLAR = {
    "Öğrenci": "ogrenci@skillbridge.com",
    "Yeni Mezun": "mezun@skillbridge.com",
    "Kariyer Adayı": "kariyer@skillbridge.com",
    "Mentor": "mentor@skillbridge.com",
    "İK Yöneticisi": "ik@skillbridge.com",
}


class GirisEkrani(QWidget):
    giris_basarili = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        self.setObjectName("loginPage")

        bg_path = Path(__file__).resolve().parents[1] / "assets" / "login_bg.jpg"
        if bg_path.exists():
            bg_url = str(bg_path).replace("\\", "/")
            bg_style = f'border-image: url("{bg_url}") 0 0 0 0 stretch stretch;'
        else:
            bg_style = (
                "background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                "stop:0 #eef6f5,stop:1 #d8e7e4);"
            )

        self.setStyleSheet(f"""
            QWidget#loginPage {{
                {bg_style}
            }}

            QFrame#loginCard {{
                background:#FFFFFF;
                border:1px solid #E5E7EB;
                border-radius:18px;
            }}

            QFrame#brandPanel {{
                background:#FFFFFF;
                border:none;
                border-right:1px solid #E5E7EB;
                border-top-left-radius:18px;
                border-bottom-left-radius:18px;
            }}

            QFrame#formPanel {{
                background:#FFFFFF;
                border:none;
                border-top-right-radius:18px;
                border-bottom-right-radius:18px;
            }}

            QLabel {{
                background:transparent;
                color:#1F2937;
            }}

            QLineEdit {{
                background:#FFFFFF;
                border:1px solid #D1D5DB;
                border-radius:8px;
                padding:0 12px;
                color:#1F2937;
                font-size:10pt;
                min-height:38px;
            }}

            QLineEdit:focus {{
                border-color:#1A8A83;
            }}

            QPushButton {{
                background:#1A8A83;
                color:white;
                border:none;
                border-radius:8px;
                padding:8px 14px;
                min-height:30px;
                font-weight:600;
            }}

            QPushButton:hover {{
                background:#14766F;
            }}

            QPushButton#linkButton {{
                background:transparent;
                color:#148079;
                border:none;
                padding:3px 0;
                min-height:22px;
                text-align:left;
                font-weight:600;
            }}

            QPushButton#linkButton:hover {{
                color:#0F5F5A;
                text-decoration:underline;
            }}

            QPushButton#demoButton {{
                background:#F0FDFB;
                color:#116B65;
                border:1px solid #B7E4DF;
                border-radius:7px;
                padding:5px 9px;
                min-height:28px;
                font-size:8.5pt;
                font-weight:600;
            }}

            QPushButton#demoButton:hover {{
                background:#DDF7F4;
                border-color:#1A8A83;
            }}

            QPushButton#userButton {{
                background:#FFFFFF;
                color:#1F2937;
                border:1px solid #D1D5DB;
                border-radius:7px;
                padding:6px 10px;
                min-height:30px;
                text-align:left;
                font-size:8.5pt;
                font-weight:600;
            }}

            QPushButton#userButton:hover {{
                background:#F0FDFB;
                border-color:#1A8A83;
                color:#116B65;
            }}

            QPushButton#eyeButton {{
                background:transparent;
                color:#6B7280;
                border:none;
                padding:0;
                min-height:26px;
                font-size:10pt;
            }}

            QPushButton#eyeButton:hover {{
                color:#1A8A83;
            }}

            QComboBox {{
                background:#FFFFFF;
                border:1px solid #D1D5DB;
                border-radius:8px;
                padding:0 10px;
                color:#1F2937;
                min-height:38px;
            }}

            QComboBox QAbstractItemView {{
                background:#FFFFFF;
                color:#1F2937;
                selection-background-color:#DDF7F4;
                selection-color:#0F3D3A;
                border:1px solid #D1D5DB;
                outline:0;
            }}

            QScrollArea {{
                border:none;
                background:transparent;
            }}

            QScrollArea QWidget {{
                background:transparent;
            }}
        """)

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.setContentsMargins(28, 28, 28, 28)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedSize(920, 640)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        card_layout.addWidget(self._brand_panel(), stretch=1)
        card_layout.addWidget(self._form_panel(), stretch=1)

        outer.addWidget(card)

    def _brand_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("brandPanel")

        lo = QVBoxLayout(panel)
        lo.setContentsMargins(34, 34, 34, 34)
        lo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lo.setSpacing(12)

        logo_path = Path(__file__).resolve().parents[1] / "assets" / "skillbridge_logo.svg"
        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedSize(360, 360)

        pixmap = QPixmap(str(logo_path))
        if not pixmap.isNull():
            logo.setPixmap(
                pixmap.scaled(
                    logo.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            logo.setText("SkillBridge")
            logo.setStyleSheet("color:#113F3B;font-size:26pt;font-weight:900;")

        alt_marka = QLabel("Kariyer Gelişim Platformu")
        alt_marka.setAlignment(Qt.AlignmentFlag.AlignCenter)
        alt_marka.setStyleSheet("""
            QLabel {
                color:#0F766E;
                font-size:10pt;
                font-weight:800;
            }
        """)

        lo.addStretch()
        lo.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        lo.addWidget(alt_marka)
        lo.addStretch()

        return panel
    def _form_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("formPanel")

        lo = QVBoxLayout(panel)
        lo.setContentsMargins(44, 34, 44, 28)
        lo.setSpacing(8)

        self.form_stack = QStackedWidget()
        self.form_stack.addWidget(self._giris_form())
        self.form_stack.addWidget(self._kayit_form())

        lo.addWidget(self.form_stack)

        self.hata_lbl = QLabel("")
        self.hata_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hata_lbl.setWordWrap(True)
        self.hata_lbl.setStyleSheet("color:#DC2626;font-size:9pt;")
        lo.addWidget(self.hata_lbl)

        return panel

    def _giris_form(self) -> QWidget:
        w = QWidget()
        lo = QVBoxLayout(w)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(7)

        title = QLabel("Giriş Yap | SkillBridge")
        title.setStyleSheet("color:#113F3B;font-size:19pt;font-weight:800;")
        lo.addWidget(title)
        lo.addSpacing(6)

        lo.addWidget(self._label("E-posta"))
        self.g_email = QLineEdit()
        self.g_email.setPlaceholderText("E-posta")
        self.g_email.setFixedHeight(40)
        lo.addWidget(self.g_email)

        lo.addWidget(self._label("Şifre"))
        self.g_sifre = QLineEdit()
        self.g_sifre.setPlaceholderText("Şifre")
        self.g_sifre.setFixedHeight(40)
        self.g_sifre.setEchoMode(QLineEdit.EchoMode.Password)
        self.g_sifre.returnPressed.connect(self._giris_yap)
        lo.addWidget(self._password_box(self.g_sifre))

        giris_btn = QPushButton("Giriş Yap")
        giris_btn.setFixedHeight(40)
        giris_btn.clicked.connect(self._giris_yap)
        lo.addSpacing(5)
        lo.addWidget(giris_btn)

        demo_title = QLabel("Demo girişleri")
        demo_title.setStyleSheet("color:#64748B;font-size:8.5pt;font-weight:700;")
        lo.addSpacing(5)
        lo.addWidget(demo_title)

        demo_grid_1 = QHBoxLayout()
        demo_grid_1.setSpacing(6)
        demo_grid_2 = QHBoxLayout()
        demo_grid_2.setSpacing(6)

        for i, (etiket, email) in enumerate(DEMO_HESAPLAR.items()):
            btn = QPushButton(etiket)
            btn.setObjectName("demoButton")
            btn.clicked.connect(lambda _, e=email: self._demo_doldur(e))
            if i < 3:
                demo_grid_1.addWidget(btn)
            else:
                demo_grid_2.addWidget(btn)

        lo.addLayout(demo_grid_1)
        lo.addLayout(demo_grid_2)

        kayitli_title = QLabel("Kayıtlı kullanıcılar")
        kayitli_title.setStyleSheet("color:#64748B;font-size:8.5pt;font-weight:700;")
        lo.addSpacing(5)
        lo.addWidget(kayitli_title)

        self.kayitli_kullanicilar_widget = QWidget()
        self.kayitli_kullanicilar_lo = QVBoxLayout(self.kayitli_kullanicilar_widget)
        self.kayitli_kullanicilar_lo.setContentsMargins(0, 0, 0, 0)
        self.kayitli_kullanicilar_lo.setSpacing(5)

        self.kayitli_scroll = QScrollArea()
        self.kayitli_scroll.setWidgetResizable(True)
        self.kayitli_scroll.setFixedHeight(118)
        self.kayitli_scroll.setWidget(self.kayitli_kullanicilar_widget)
        lo.addWidget(self.kayitli_scroll)

        self._kayitli_kullanicilari_yukle()

        sifrem_btn = QPushButton("Şifremi Unuttum")
        sifrem_btn.setObjectName("linkButton")
        sifrem_btn.clicked.connect(self._sifremi_unuttum)

        kayit_btn = QPushButton("Kayıt Ol")
        kayit_btn.setObjectName("linkButton")
        kayit_btn.clicked.connect(lambda: self._sekme(False))

        link_row = QHBoxLayout()
        link_row.addWidget(sifrem_btn)
        link_row.addSpacing(18)
        link_row.addWidget(kayit_btn)
        link_row.addStretch()
        lo.addLayout(link_row)
        lo.addStretch()

        return w

    def _kayit_form(self) -> QWidget:
        w = QWidget()
        lo = QVBoxLayout(w)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(7)

        title = QLabel("Kayıt Ol | SkillBridge")
        title.setStyleSheet("color:#113F3B;font-size:19pt;font-weight:800;")
        lo.addWidget(title)
        lo.addSpacing(5)

        self.k_ad = QLineEdit()
        self.k_ad.setPlaceholderText("Ad Soyad")
        self.k_ad.setFixedHeight(40)

        self.k_email = QLineEdit()
        self.k_email.setPlaceholderText("E-posta")
        self.k_email.setFixedHeight(40)

        self.k_sifre = QLineEdit()
        self.k_sifre.setPlaceholderText("Şifre")
        self.k_sifre.setFixedHeight(40)
        self.k_sifre.setEchoMode(QLineEdit.EchoMode.Password)

        self.k_rol = QComboBox()
        self.k_rol.setFixedHeight(40)
        self.k_rol.addItems(list(ROL_MAP.keys()))

        for label, widget in (
            ("Ad Soyad", self.k_ad),
            ("E-posta", self.k_email),
            ("Şifre", self.k_sifre),
            ("Rol", self.k_rol),
        ):
            lo.addWidget(self._label(label))
            lo.addWidget(widget)

        kayit_btn = QPushButton("Kayıt Ol")
        kayit_btn.setFixedHeight(40)
        kayit_btn.clicked.connect(self._kayit_ol)

        giris_btn = QPushButton("Giriş Yap")
        giris_btn.setObjectName("linkButton")
        giris_btn.clicked.connect(lambda: self._sekme(True))

        lo.addSpacing(8)
        lo.addWidget(kayit_btn)
        lo.addWidget(giris_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        lo.addStretch()

        return w

    def _label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("color:#1F2937;font-size:9pt;font-weight:700;")
        return label

    def _password_box(self, line_edit: QLineEdit) -> QWidget:
        box = QWidget()
        box.setFixedHeight(42)
        box.setStyleSheet("""
            QWidget {
                background:#FFFFFF;
                border:1px solid #D1D5DB;
                border-radius:8px;
            }

            QLineEdit {
                border:none;
                background:transparent;
                padding:0 8px 0 11px;
                min-height:38px;
            }
        """)

        lo = QHBoxLayout(box)
        lo.setContentsMargins(0, 0, 8, 0)
        lo.setSpacing(0)

        eye_btn = QPushButton("👁")
        eye_btn.setObjectName("eyeButton")
        eye_btn.setFixedSize(30, 28)
        eye_btn.clicked.connect(lambda: self._toggle_password(line_edit))

        lo.addWidget(line_edit)
        lo.addWidget(eye_btn)

        return box

    def _toggle_password(self, line_edit: QLineEdit):
        if line_edit.echoMode() == QLineEdit.EchoMode.Password:
            line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def _demo_doldur(self, email: str):
        self.g_email.setText(email)
        self.g_sifre.setText("1234")

    def _kayitli_kullanicilari_yukle(self):
        if not hasattr(self, "kayitli_kullanicilar_lo"):
            return

        while self.kayitli_kullanicilar_lo.count():
            item = self.kayitli_kullanicilar_lo.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        kullanicilar = api_get("/api/kullanicilar")

        if not isinstance(kullanicilar, list) or not kullanicilar:
            bos = QLabel("Henüz kayıtlı kullanıcı yok.")
            bos.setStyleSheet("color:#64748B;font-size:8.5pt;")
            self.kayitli_kullanicilar_lo.addWidget(bos)
            return

        for kullanici in kullanicilar[:8]:
            ad = kullanici.get("ad_soyad", "Kullanıcı")
            email = kullanici.get("email", "")
            rol = self._rol_etiketi(kullanici.get("rol", ""))

            btn = QPushButton(f"{ad}  ·  {rol}")
            btn.setObjectName("userButton")
            btn.setToolTip(email)
            btn.clicked.connect(lambda _, e=email: self._kayitli_kullanici_sec(e))
            self.kayitli_kullanicilar_lo.addWidget(btn)

        self.kayitli_kullanicilar_lo.addStretch()

    def _kayitli_kullanici_sec(self, email: str):
        self.g_email.setText(email)
        self.g_sifre.clear()
        self.g_sifre.setFocus()

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

    def _sekme(self, giris: bool):
        self.form_stack.setCurrentIndex(0 if giris else 1)
        self.hata_lbl.setText("")
        if giris:
            self._kayitli_kullanicilari_yukle()

    def _giris_yap(self):
        self.hata_lbl.setText("")
        sonuc = api_post(
            "/api/auth/giris",
            {
                "email": self.g_email.text().strip(),
                "sifre": self.g_sifre.text(),
            },
        )

        if "hata" in sonuc:
            self.hata_lbl.setText(sonuc["hata"])
        else:
            self.giris_basarili.emit(sonuc)

    def _kayit_ol(self):
        self.hata_lbl.setText("")
        rol = ROL_MAP.get(self.k_rol.currentText(), "student")

        sonuc = api_post(
            "/api/auth/kayit",
            {
                "email": self.k_email.text().strip(),
                "sifre": self.k_sifre.text(),
                "ad_soyad": self.k_ad.text().strip(),
                "rol": rol,
            },
        )

        if "hata" in sonuc:
            self.hata_lbl.setText(sonuc["hata"])
        else:
            self._bilgi_mesaji(
                "Başarılı",
                f"Hoş geldin {sonuc['ad_soyad']}!\nŞimdi giriş yapabilirsin.",
            )
            self.g_email.setText(self.k_email.text().strip())
            self.g_sifre.clear()
            self._sekme(True)
            self._kayitli_kullanicilari_yukle()

    def _sifremi_unuttum(self):
        email = self.g_email.text().strip()
        if not email:
            self._uyari_mesaji("E-posta gerekli", "Şifre sıfırlama için önce e-posta alanını doldurun.")
            return

        kullanicilar = api_get("/api/kullanicilar")
        if isinstance(kullanicilar, list) and any(k.get("email") == email for k in kullanicilar):
            self._bilgi_mesaji(
                "Şifre Sıfırlama",
                "Demo modunda şifre sıfırlama bağlantısı gönderilmiş gibi işaretlendi.\nSunum hesaplarında varsayılan şifre: 1234",
            )
        else:
            self._uyari_mesaji("Kullanıcı bulunamadı", "Bu e-posta ile kayıtlı kullanıcı bulunamadı.")

    def _bilgi_mesaji(self, baslik: str, mesaj: str):
        self._mesaj_kutusu(QMessageBox.Icon.Information, baslik, mesaj, "#1A8A83", "#14766F")

    def _uyari_mesaji(self, baslik: str, mesaj: str):
        self._mesaj_kutusu(QMessageBox.Icon.Warning, baslik, mesaj, "#B91C1C", "#991B1B")

    def _mesaj_kutusu(self, ikon, baslik: str, mesaj: str, renk: str, hover: str):
        msg = QMessageBox(self)
        msg.setIcon(ikon)
        msg.setWindowTitle(baslik)
        msg.setText(mesaj)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color:#FFFFFF;
                color:#1F2937;
            }}

            QLabel {{
                color:#1F2937;
                background:transparent;
                font-size:10pt;
            }}

            QPushButton {{
                background-color:{renk};
                color:white;
                border:none;
                border-radius:6px;
                padding:7px 16px;
                min-width:72px;
                font-weight:600;
            }}

            QPushButton:hover {{
                background-color:{hover};
            }}
        """)
        msg.exec()



