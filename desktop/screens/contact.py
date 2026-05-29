from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from desktop.api import api_get, api_post
from desktop.ui.components import baslik, kart


class IletisimSayfasi(QWidget):
    def __init__(self, kullanici: dict | None = None):
        super().__init__()
        self.kullanici = kullanici or {}
        self.uid = self.kullanici.get("kullanici_id", "")
        self.rol = self.kullanici.get("rol", "")
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
        hero.setStyleSheet(
            "QFrame#card{background:#F8F3EA;border:1px solid #EADCC3;"
            "border-left:4px solid #B7791F;border-radius:8px;}"
        )
        h = QHBoxLayout(hero)
        h.setContentsMargins(20, 16, 20, 16)
        h.setSpacing(18)
        text = QVBoxLayout()
        title = QLabel("İletişim ve Destek Merkezi")
        title.setStyleSheet("font-size:16pt;font-weight:900;color:#3D2F16;")
        desc = QLabel("Sorun, öneri ve iş birliği talepleri artık sistemde kayıt altına alınır ve takip edilebilir.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#5F5138;font-size:10pt;")
        text.addWidget(title)
        text.addWidget(desc)
        text.addStretch()
        h.addLayout(text, 2)
        img = QLabel()
        img.setFixedSize(330, 132)
        img.setScaledContents(True)
        p = Path(__file__).resolve().parents[1] / "assets" / "contact_panel.png"
        if p.exists():
            img.setPixmap(QPixmap(str(p)))
        h.addWidget(img, 1)
        lo.addWidget(hero)

        row = QHBoxLayout()
        row.setSpacing(14)
        for title, value, text, color in [
            ("Ürün Ekibi", "urun@skillbridge.local", "Özellik önerileri, demo akışı ve ürün geri bildirimi.", "#38546E"),
            ("Mentor Operasyonu", "mentor@skillbridge.local", "Değerlendirme ve aday yönlendirme desteği.", "#0E6B5C"),
            ("İK İş Birliği", "ik@skillbridge.local", "Şirket fırsatları, pozisyon akışı ve kısa liste çalışmaları.", "#B7791F"),
        ]:
            row.addWidget(self._iletisim_karti(title, value, text, color))
        lo.addLayout(row)

        form = kart()
        form_lo = QVBoxLayout(form)
        form_lo.setContentsMargins(20, 16, 20, 16)
        form_lo.setSpacing(10)
        form_lo.addWidget(baslik("Yeni Destek Talebi", renk="#0F3D3A"))

        self.kategori = QComboBox()
        self.kategori.addItems(["Teknik Sorun", "CV / Rapor", "Mentor Akışı", "İK / Fırsatlar", "Öneri", "İş Birliği"])
        self.konu = QLineEdit()
        self.konu.setPlaceholderText("Konu")
        self.mesaj = QTextEdit()
        self.mesaj.setPlaceholderText("Mesajınızı yazın...")
        self.mesaj.setMinimumHeight(120)
        self.mesaj.setStyleSheet(
            "background:#FFFFFF;color:#1F2937;border:1px solid #D1D5DB;"
            "border-radius:8px;padding:8px;font-size:10pt;"
        )

        user_lbl = QLabel(f"Talep sahibi: {self.kullanici.get('ad_soyad', 'Misafir')} · {self._rol_etiketi(self.rol)}")
        user_lbl.setStyleSheet("color:#64748B;font-size:9pt;font-weight:700;")
        gonder = QPushButton("Destek Talebi Oluştur")
        gonder.setObjectName("success")
        gonder.clicked.connect(self._talep_gonder)

        form_lo.addWidget(user_lbl)
        form_lo.addWidget(self.kategori)
        form_lo.addWidget(self.konu)
        form_lo.addWidget(self.mesaj)
        form_lo.addWidget(gonder)
        lo.addWidget(form)

        liste = kart()
        liste_lo = QVBoxLayout(liste)
        liste_lo.setContentsMargins(20, 16, 20, 16)
        liste_lo.setSpacing(8)
        liste_lo.addWidget(baslik("Son Destek Talepleri", renk="#0F3D3A"))
        self.talep_lo = QVBoxLayout()
        self.talep_lo.setSpacing(8)
        liste_lo.addLayout(self.talep_lo)
        lo.addWidget(liste)

        qr = kart()
        ql = QHBoxLayout(qr)
        ql.setContentsMargins(20, 16, 20, 16)
        qtext = QVBoxLayout()
        qtext.addWidget(baslik("Aktif QR Demo Bağlantısı", renk="#0F3D3A"))
        info = QLabel("QR butonu SkillBridge API dokümantasyonuna yönlenen canlı bir QR üretir. Sunum sırasında telefondan okutulabilir.")
        info.setWordWrap(True)
        info.setStyleSheet("color:#475569;font-size:10pt;")
        qtext.addWidget(info)
        ql.addLayout(qtext, 1)
        btn = QPushButton("QR'ı Aç")
        btn.setObjectName("success")
        btn.clicked.connect(self._qr_ac)
        ql.addWidget(btn)
        lo.addWidget(qr)

        quote = QLabel('"İlim ilim bilmektir; ilim kendin bilmektir." - Yunus Emre')
        quote.setStyleSheet("color:#64748B;font-size:9pt;font-style:italic;padding:8px;")
        lo.addWidget(quote)
        lo.addStretch()
        scroll.setWidget(w)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def yukle(self):
        self._talepleri_yukle()

    def _talep_gonder(self):
        konu = self.konu.text().strip()
        mesaj = self.mesaj.toPlainText().strip()
        if not konu or not mesaj:
            QMessageBox.warning(self, "Eksik Bilgi", "Konu ve mesaj alanlarını doldurun.")
            return

        sonuc = api_post("/api/destek/talep", {
            "kullanici_id": self.uid or None,
            "ad_soyad": self.kullanici.get("ad_soyad", "Misafir"),
            "email": self.kullanici.get("email", ""),
            "rol": self.rol,
            "kategori": self.kategori.currentText(),
            "konu": konu,
            "mesaj": mesaj,
        })

        if "hata" in sonuc:
            QMessageBox.warning(self, "Destek", sonuc["hata"])
            return
        QMessageBox.information(self, "Destek", sonuc.get("mesaj", "Talep kaydedildi."))
        self.konu.clear()
        self.mesaj.clear()
        self._talepleri_yukle()

    def _talepleri_yukle(self):
        while self.talep_lo.count():
            item = self.talep_lo.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if self.rol in ("mentor", "hr_manager"):
            talepler = api_get("/api/destek")
        elif self.uid:
            talepler = api_get(f"/api/destek/kullanici/{self.uid}")
        else:
            talepler = []

        if not isinstance(talepler, list) or not talepler:
            bos = QLabel("Henüz destek talebi yok.")
            bos.setStyleSheet("color:#64748B;font-size:9pt;")
            self.talep_lo.addWidget(bos)
            return

        for talep in talepler[:8]:
            self.talep_lo.addWidget(self._talep_karti(talep))

    def _talep_karti(self, talep: dict) -> QFrame:
        k = kart()
        k.setStyleSheet("QFrame#card{background:#FFFFFF;border:1px solid #E5E7EB;border-left:4px solid #B7791F;border-radius:8px;}")
        lo = QVBoxLayout(k)
        lo.setContentsMargins(14, 10, 14, 10)
        bas = QLabel(f"{talep.get('kategori', '-')} · {talep.get('konu', '-')}")
        bas.setStyleSheet("color:#1F2937;font-size:10pt;font-weight:900;")
        meta = QLabel(f"{talep.get('ad_soyad', '-')} · {talep.get('durum', 'open')} · {talep.get('tarih', '')}")
        meta.setStyleSheet("color:#64748B;font-size:8.5pt;font-weight:700;")
        msg = QLabel(talep.get("mesaj", ""))
        msg.setWordWrap(True)
        msg.setStyleSheet("color:#475569;font-size:9pt;")
        lo.addWidget(bas)
        lo.addWidget(meta)
        lo.addWidget(msg)
        return k

    def _qr_ac(self):
        target = "http://localhost:8000/docs"
        qr_url = "https://quickchart.io/qr?text=" + target + "&size=260"
        QDesktopServices.openUrl(QUrl(qr_url))

    @staticmethod
    def _iletisim_karti(title: str, value: str, text: str, color: str) -> QFrame:
        k = kart()
        k.setStyleSheet(f"QFrame#card{{background:#FFFFFF;border:1px solid #E5E7EB;border-top:4px solid {color};border-radius:8px;}}")
        lo = QVBoxLayout(k)
        lo.setContentsMargins(18, 14, 18, 14)
        b = QLabel(title)
        b.setStyleSheet("color:#1F2937;font-size:11pt;font-weight:900;")
        v = QLabel(value)
        v.setStyleSheet(f"color:{color};font-size:9pt;font-weight:800;")
        m = QLabel(text)
        m.setWordWrap(True)
        m.setStyleSheet("color:#64748B;font-size:9pt;")
        lo.addWidget(b)
        lo.addWidget(v)
        lo.addWidget(m)
        return k

    @staticmethod
    def _rol_etiketi(rol: str) -> str:
        return {
            "student": "Öğrenci",
            "graduate": "Yeni Mezun",
            "candidate": "Kariyer Adayı",
            "mentor": "Mentor",
            "hr_manager": "İK Yöneticisi",
            "professional": "Kariyer Adayı",
        }.get(rol, rol or "Misafir")
