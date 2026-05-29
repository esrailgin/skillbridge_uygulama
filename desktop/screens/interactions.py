import httpx

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from desktop.api import api_get, api_patch, api_post
from desktop.config import API
from desktop.ui.components import baslik, kart


class EtkilesimSayfasi(QWidget):
    def __init__(self, kullanici: dict):
        super().__init__()
        self.kullanici = kullanici
        self.uid = kullanici.get("kullanici_id", "")
        self.rol = kullanici.get("rol", "")
        self._build()

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        w = QWidget()
        self.lo = QVBoxLayout(w)
        self.lo.setContentsMargins(28, 24, 28, 24)
        self.lo.setSpacing(16)

        self.lo.addWidget(baslik("Rol Etkileşimleri", renk="#0F3D3A"))

        self.content_lo = QVBoxLayout()
        self.content_lo.setSpacing(10)
        self.lo.addLayout(self.content_lo)
        self.lo.addStretch()

        scroll.setWidget(w)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def yukle(self):
        self._temizle()

        if self.rol in ("student", "graduate", "candidate", "professional"):
            self._aday_gorunumu()
        elif self.rol == "mentor":
            self._mentor_gorunumu()
        elif self.rol == "hr_manager":
            self._ik_gorunumu()
        else:
            self.content_lo.addWidget(self._bos("Bu rol için etkileşim ekranı tanımlı değil."))

    def _aday_gorunumu(self):
        talep_krt = kart()
        talep_lo = QVBoxLayout(talep_krt)
        talep_lo.setContentsMargins(16, 14, 16, 14)
        talep_lo.setSpacing(8)

        aciklama = QLabel("Mentordan CV, profil ve kariyer yol haritası değerlendirmesi isteyebilirsiniz.")
        aciklama.setStyleSheet("color:#64748B;font-size:9pt;")
        aciklama.setWordWrap(True)

        self.talep_notu = QLineEdit()
        self.talep_notu.setPlaceholderText("Kısa not: Hangi konuda geri bildirim istiyorsunuz?")

        btn = QPushButton("Mentor Değerlendirmesi İste")
        btn.setObjectName("success")
        btn.clicked.connect(self._talep_olustur)

        talep_lo.addWidget(aciklama)
        talep_lo.addWidget(self.talep_notu)
        talep_lo.addWidget(btn)

        self.content_lo.addWidget(talep_krt)
        self.content_lo.addWidget(baslik("Taleplerim", renk="#0F3D3A"))

        veriler = api_get(f"/api/etkilesimler/kullanici/{self.uid}")
        self._kartlari_listele(veriler, "aday")

    def _mentor_gorunumu(self):
        self.content_lo.addWidget(baslik("Bekleyen CV İncelemeleri", renk="#0F3D3A"))
        cvler = api_get("/api/cv/bekleyen")
        self._bekleyen_cvleri_listele(cvler)

        self.content_lo.addWidget(baslik("Mentor Değerlendirme Talepleri", renk="#0F3D3A"))
        veriler = api_get("/api/etkilesimler/mentor")
        self._kartlari_listele(veriler, "mentor")

    def _ik_gorunumu(self):
        self.content_lo.addWidget(baslik("Mentor Onaylı Adaylar", renk="#0F3D3A"))
        veriler = api_get("/api/etkilesimler/ik")
        self._kartlari_listele(veriler, "ik")

    def _bekleyen_cvleri_listele(self, cvler):
        if not isinstance(cvler, list) or not cvler:
            self.content_lo.addWidget(self._bos("Bekleyen CV yok."))
            return

        for cv in cvler:
            k = kart()
            lo = QVBoxLayout(k)
            lo.setContentsMargins(16, 12, 16, 12)
            lo.setSpacing(7)

            ust = QLabel(f"{cv.get('ad_soyad', 'Kullanıcı')}  ·  {self._rol_etiketi(cv.get('rol', ''))}")
            ust.setStyleSheet("color:#1F2937;font-size:10pt;font-weight:700;")

            dosya = QLabel(f"CV dosyası: {cv.get('dosya_adi', '-')}")
            dosya.setStyleSheet("color:#475569;font-size:9pt;")

            email = QLabel(cv.get("email", ""))
            email.setStyleSheet("color:#64748B;font-size:8.5pt;")

            skor = QLineEdit()
            skor.setPlaceholderText("Gap skoru 0-100 örn: 78")

            yorum = QLineEdit()
            yorum.setPlaceholderText("Mentor CV notu")

            row = QHBoxLayout()

            ac_btn = QPushButton("CV Aç")
            ac_btn.setEnabled(bool(cv.get("dosya_var")))
            ac_btn.clicked.connect(lambda _, i=cv["id"]: self._cv_ac(i))

            indir_btn = QPushButton("CV İndir")
            indir_btn.setEnabled(bool(cv.get("dosya_var")))
            indir_btn.clicked.connect(
                lambda _, i=cv["id"], a=cv.get("dosya_adi", "cv.pdf"): self._cv_indir(i, a)
            )

            onay_btn = QPushButton("CV'yi Tamamlandı Yap")
            onay_btn.setObjectName("success")
            onay_btn.clicked.connect(
                lambda _, i=cv["id"], s=skor, y=yorum: self._cv_onayla(i, s.text(), y.text())
            )

            row.addWidget(ac_btn)
            row.addWidget(indir_btn)
            row.addWidget(onay_btn)

            if not cv.get("dosya_var"):
                uyari = QLabel("Dosya görüntülenemiyor: Bu CV dosya saklama özelliğinden önce yüklenmiş olabilir. Öğrencinin CV'yi tekrar yüklemesi gerekir.")
                uyari.setStyleSheet("color:#B91C1C;font-size:8.5pt;")
                uyari.setWordWrap(True)
                lo.addWidget(uyari)

            lo.addWidget(ust)
            lo.addWidget(email)
            lo.addWidget(dosya)
            lo.addWidget(skor)
            lo.addWidget(yorum)
            lo.addLayout(row)

            self.content_lo.addWidget(k)

    def _kartlari_listele(self, veriler, mod: str):
        if not isinstance(veriler, list) or not veriler:
            self.content_lo.addWidget(self._bos("Henüz kayıt yok."))
            return

        for item in veriler:
            k = kart()
            lo = QVBoxLayout(k)
            lo.setContentsMargins(16, 12, 16, 12)
            lo.setSpacing(7)

            ust = QLabel(f"{item.get('ad_soyad', 'Kullanıcı')}  ·  {self._rol_etiketi(item.get('rol', ''))}")
            ust.setStyleSheet("color:#1F2937;font-size:10pt;font-weight:700;")

            durum = QLabel(item.get("durum_etiketi", ""))
            durum.setStyleSheet(f"color:{self._durum_rengi(item.get('durum', ''))};font-size:9pt;font-weight:700;")

            email = QLabel(item.get("email", ""))
            email.setStyleSheet("color:#64748B;font-size:8.5pt;")

            notu = QLabel(f"Talep notu: {item.get('not') or '-'}")
            notu.setStyleSheet("color:#475569;font-size:9pt;")
            notu.setWordWrap(True)

            mentor_notu = QLabel(f"Mentor notu: {item.get('mentor_notu') or '-'}")
            mentor_notu.setStyleSheet("color:#475569;font-size:9pt;")
            mentor_notu.setWordWrap(True)

            lo.addWidget(ust)
            lo.addWidget(email)
            lo.addWidget(durum)
            lo.addWidget(notu)
            lo.addWidget(mentor_notu)

            if mod == "mentor":
                yorum = QLineEdit()
                yorum.setPlaceholderText("Mentor notu yazın")
                row = QHBoxLayout()

                onay = QPushButton("Uygun")
                onay.setObjectName("success")
                onay.clicked.connect(lambda _, i=item["id"], y=yorum: self._mentor_guncelle(i, y.text(), "approved"))

                gelistir = QPushButton("Geliştirilmeli")
                gelistir.clicked.connect(lambda _, i=item["id"], y=yorum: self._mentor_guncelle(i, y.text(), "rejected"))

                row.addWidget(onay)
                row.addWidget(gelistir)

                lo.addWidget(yorum)
                lo.addLayout(row)

            if mod == "ik":
                ik_not = QLineEdit()
                ik_not.setPlaceholderText("İK notu")
                liste_btn = QPushButton("Mülakat Listesine Al")
                liste_btn.setObjectName("success")
                liste_btn.clicked.connect(lambda _, i=item["id"], y=ik_not: self._ik_listeye_al(i, y.text()))

                lo.addWidget(ik_not)
                lo.addWidget(liste_btn)

            self.content_lo.addWidget(k)

    def _talep_olustur(self):
        sonuc = api_post("/api/etkilesimler/talep-olustur", {
            "requester_id": self.uid,
            "note": self.talep_notu.text().strip(),
        })

        if "hata" in sonuc:
            QMessageBox.warning(self, "Hata", sonuc["hata"])
        else:
            QMessageBox.information(self, "Başarılı", sonuc.get("mesaj", "Talep oluşturuldu."))
            self.yukle()

    def _cv_ac(self, analiz_id: str):
        QDesktopServices.openUrl(QUrl(f"{API}/api/cv/dosya/{analiz_id}"))

    def _cv_indir(self, analiz_id: str, dosya_adi: str):
        kayit_yolu, _ = QFileDialog.getSaveFileName(
            self,
            "CV Kaydet",
            dosya_adi or "cv.pdf",
            "CV Dosyaları (*.pdf *.docx);;Tüm Dosyalar (*)",
        )

        if not kayit_yolu:
            return

        try:
            r = httpx.get(f"{API}/api/cv/dosya/{analiz_id}", timeout=30)
            r.raise_for_status()

            with open(kayit_yolu, "wb") as f:
                f.write(r.content)

            QMessageBox.information(self, "Başarılı", "CV seçilen konuma kaydedildi.")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"CV indirilemedi: {e}")

    def _cv_onayla(self, analiz_id: str, skor_text: str, note: str):
        try:
            skor = float(skor_text.replace(",", ".")) if skor_text.strip() else 75
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Gap skoru sayı olmalı.")
            return

        sonuc = api_patch("/api/cv/mentor-onayla", {
            "analiz_id": analiz_id,
            "gap_skoru": skor,
            "mentor_notu": note,
        })

        if "hata" in sonuc:
            QMessageBox.warning(self, "Hata", sonuc["hata"])
        else:
            QMessageBox.information(self, "Başarılı", sonuc.get("mesaj", "CV tamamlandı."))
            self.yukle()

    def _mentor_guncelle(self, interaction_id: str, note: str, status: str):
        sonuc = api_patch("/api/etkilesimler/mentor-degerlendir", {
            "interaction_id": interaction_id,
            "mentor_note": note or "Değerlendirme tamamlandı.",
            "status": status,
        })

        if "hata" in sonuc:
            QMessageBox.warning(self, "Hata", sonuc["hata"])
        else:
            self.yukle()

    def _ik_listeye_al(self, interaction_id: str, note: str):
        sonuc = api_patch("/api/etkilesimler/ik-listeye-al", {
            "interaction_id": interaction_id,
            "hr_note": note,
        })

        if "hata" in sonuc:
            QMessageBox.warning(self, "Hata", sonuc["hata"])
        else:
            QMessageBox.information(self, "Başarılı", "Aday mülakat listesine alındı.")
            self.yukle()

    def _temizle(self):
        while self.content_lo.count():
            item = self.content_lo.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _bos(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color:#64748B;font-size:9pt;")
        return lbl

    @staticmethod
    def _durum_rengi(durum: str) -> str:
        return {
            "pending": "#D97706",
            "approved": "#0F766E",
            "reviewed": "#2563EB",
            "rejected": "#B91C1C",
            "shortlisted": "#7C3AED",
        }.get(durum, "#64748B")

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


