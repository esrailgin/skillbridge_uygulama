import httpx

from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QFileDialog,
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

from desktop.api import api_get
from desktop.config import API
from desktop.ui.components import baslik, kart


class CVSayfasi(QWidget):
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
        lo.setSpacing(16)

        upload_krt = kart()
        upload_krt.setStyleSheet(
            "QFrame#card{background:#FFFFFF;"
            "border:2px dashed #CBD5E1;border-radius:8px;}"
        )

        ul = QVBoxLayout(upload_krt)
        ul.setContentsMargins(0, 34, 0, 34)
        ul.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ul.setSpacing(10)

        icon = QLabel("📄")
        icon.setStyleSheet("font-size:32pt;color:#0F766E;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ul.addWidget(icon)

        self.yukle_lbl = QLabel("CV dosyanızı seçin (PDF veya DOCX)")
        self.yukle_lbl.setStyleSheet("color:#64748B;font-size:10pt;")
        self.yukle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ul.addWidget(self.yukle_lbl)

        self.dosya_btn = QPushButton("Dosya Seç")
        self.dosya_btn.setFixedWidth(150)
        self.dosya_btn.clicked.connect(self._dosya_sec)
        ul.addWidget(self.dosya_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        lo.addWidget(upload_krt)

        self.durum_lbl = QLabel("")
        self.durum_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.durum_lbl.setStyleSheet("color:#0F766E;font-size:10pt;font-weight:600;")

        self.prog = QProgressBar()
        self.prog.setRange(0, 100)
        self.prog.setValue(0)
        self.prog.setTextVisible(False)
        self.prog.setFixedHeight(10)
        self.prog.setVisible(False)

        lo.addWidget(self.durum_lbl)
        lo.addWidget(self.prog)

        lo.addWidget(baslik("Geçmiş Analizler", renk="#0F3D3A"))
        self.gecmis_lo = QVBoxLayout()
        self.gecmis_lo.setSpacing(8)
        lo.addLayout(self.gecmis_lo)
        lo.addStretch()

        scroll.setWidget(w)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def yukle(self):
        analizler = api_get(f"/api/cv/{self.uid}")

        while self.gecmis_lo.count():
            item = self.gecmis_lo.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if isinstance(analizler, list) and analizler:
            for a in analizler[:5]:
                krt2 = kart()
                krt2_lo = QHBoxLayout(krt2)
                krt2_lo.setContentsMargins(16, 10, 16, 10)

                ad = QLabel(f"📄 {a.get('dosya_adi', '')}")
                ad.setStyleSheet("color:#1F2937;font-size:9pt;font-weight:600;")

                dur = a.get("durum", "")
                dur_renk = {
                    "completed": "#0F766E",
                    "pending": "#D97706",
                    "failed": "#B91C1C",
                }.get(dur, "#64748B")

                dur_text = {
                    "completed": "Tamamlandı",
                    "pending": "Bekliyor",
                    "failed": "Başarısız",
                }.get(dur, dur)

                dur_lbl = QLabel(dur_text)
                dur_lbl.setStyleSheet(
                    f"color:{dur_renk};font-size:8pt;font-weight:700;"
                )

                skor = QLabel(f"Skor: {a.get('gap_skoru', 0):.0f}")
                skor.setStyleSheet("color:#2563EB;font-size:9pt;font-weight:600;")

                analiz_id = a.get("id", "")
                dosya_var = bool(a.get("dosya_var", False))

                ac_btn = QPushButton("Aç")
                ac_btn.setFixedWidth(70)
                ac_btn.setEnabled(dosya_var)
                ac_btn.clicked.connect(lambda _, i=analiz_id: self._cv_ac(i))

                indir_btn = QPushButton("İndir")
                indir_btn.setFixedWidth(80)
                indir_btn.setEnabled(dosya_var)
                indir_btn.clicked.connect(
                    lambda _, i=analiz_id, d=a.get("dosya_adi", "cv.pdf"): self._cv_indir(i, d)
                )

                if not dosya_var:
                    tooltip = (
                        "Bu eski/demo kaydın fiziksel dosyası sunucuda yok. "
                        "CV tekrar yüklenirse açma ve indirme aktif olur."
                    )
                    ac_btn.setToolTip(tooltip)
                    indir_btn.setToolTip(tooltip)

                krt2_lo.addWidget(ad, stretch=1)
                krt2_lo.addWidget(dur_lbl)
                krt2_lo.addSpacing(12)
                krt2_lo.addWidget(skor)
                krt2_lo.addSpacing(10)
                krt2_lo.addWidget(ac_btn)
                krt2_lo.addWidget(indir_btn)

                self.gecmis_lo.addWidget(krt2)
        else:
            bos = QLabel("Henüz CV yüklenmemiş.")
            bos.setStyleSheet("color:#64748B;font-size:9pt;")
            self.gecmis_lo.addWidget(bos)

    def _cv_ac(self, analiz_id: str):
        if not analiz_id:
            self._hata_mesaji("Hata", "CV analiz kaydı bulunamadı.")
            return

        QDesktopServices.openUrl(QUrl(f"{API}/api/cv/dosya/{analiz_id}"))

    def _cv_indir(self, analiz_id: str, dosya_adi: str):
        if not analiz_id:
            self._hata_mesaji("Hata", "CV analiz kaydı bulunamadı.")
            return

        hedef, _ = QFileDialog.getSaveFileName(
            self,
            "CV Dosyasını Kaydet",
            dosya_adi or "cv.pdf",
            "CV Dosyaları (*.pdf *.docx);;Tüm Dosyalar (*)",
        )

        if not hedef:
            return

        try:
            r = httpx.get(f"{API}/api/cv/dosya/{analiz_id}", timeout=30)
            r.raise_for_status()
            with open(hedef, "wb") as f:
                f.write(r.content)
            self._bilgi_mesaji("CV İndirildi", "CV dosyası seçtiğiniz konuma kaydedildi.")
        except Exception as e:
            self._hata_mesaji("CV İndirilemedi", str(e))

    def _dosya_sec(self):
        yol, _ = QFileDialog.getOpenFileName(
            self,
            "CV Seç",
            "",
            "CV Dosyaları (*.pdf *.docx)",
        )

        if not yol:
            return

        dosya_adi = yol.split("/")[-1].split("\\")[-1]
        self.yukle_lbl.setText(f"Seçilen dosya: {dosya_adi}")
        self.prog.setVisible(True)
        self.prog.setValue(0)
        self.dosya_btn.setEnabled(False)

        self._mesajlar = [
            (20, "Dosya okunuyor..."),
            (45, "CV içeriği değerlendiriliyor..."),
            (70, "Beceriler tespit ediliyor..."),
            (90, "Gap analizi hazırlanıyor..."),
            (100, "Tamamlandı."),
        ]
        self._msg_idx = 0
        self._yol = yol

        self._timer = QTimer()
        self._timer.timeout.connect(self._simule_et)
        self._timer.start(700)

    def _simule_et(self):
        if self._msg_idx >= len(self._mesajlar):
            self._timer.stop()
            self._cv_yukle()
            return

        val, msg = self._mesajlar[self._msg_idx]
        self.prog.setValue(val)
        self.durum_lbl.setText(msg)
        self._msg_idx += 1

    def _cv_yukle(self):
        try:
            with open(self._yol, "rb") as f:
                icerik = f.read()

            mime = (
                "application/pdf"
                if self._yol.endswith(".pdf")
                else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

            dosya_adi = self._yol.split("\\")[-1].split("/")[-1]

            r = httpx.post(
                f"{API}/api/cv/yukle/{self.uid}",
                files={"dosya": (dosya_adi, icerik, mime)},
                timeout=15,
            )
            r.raise_for_status()
            sonuc = r.json()

            self._bilgi_mesaji(
                "CV Yüklendi",
                sonuc.get("mesaj", "CV başarıyla yüklendi."),
            )

        except Exception as e:
            self._hata_mesaji("Hata", str(e))

        finally:
            self.dosya_btn.setEnabled(True)
            self.yukle()

    def _bilgi_mesaji(self, baslik_text: str, mesaj: str):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(baslik_text)
        msg.setText(mesaj)
        msg.setStyleSheet(self._mesaj_stili("#1A8A83", "#14766F"))
        msg.exec()

    def _hata_mesaji(self, baslik_text: str, mesaj: str):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(baslik_text)
        msg.setText(mesaj)
        msg.setStyleSheet(self._mesaj_stili("#B91C1C", "#991B1B"))
        msg.exec()

    @staticmethod
    def _mesaj_stili(renk: str, hover: str) -> str:
        return f"""
            QMessageBox {{
                background-color: #FFFFFF;
                color: #1F2937;
            }}

            QLabel {{
                color: #1F2937;
                background: transparent;
                font-size: 10pt;
            }}

            QPushButton {{
                background-color: {renk};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 7px 16px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background-color: {hover};
            }}
        """
