from PyQt6.QtWidgets import (
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
from desktop.ui.components import baslik, kart, metrik_karti


class GelisimMerkeziSayfasi(QWidget):
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
        lo = QVBoxLayout(w)
        lo.setContentsMargins(28, 24, 28, 24)
        lo.setSpacing(16)

        hero = kart()
        hero.setStyleSheet(
            "QFrame#card{background:#FFFFFF;border:1px solid #D1E7E4;"
            "border-left:4px solid #0F766E;border-radius:8px;}"
        )
        hero_lo = QVBoxLayout(hero)
        hero_lo.setContentsMargins(20, 16, 20, 16)
        self.baslik_lbl = QLabel("Gelişim Merkezi")
        self.baslik_lbl.setStyleSheet("font-size:15pt;font-weight:800;color:#0F3D3A;")
        self.oneri_lbl = QLabel("")
        self.oneri_lbl.setWordWrap(True)
        self.oneri_lbl.setStyleSheet("color:#475569;font-size:10pt;")
        hero_lo.addWidget(self.baslik_lbl)
        hero_lo.addWidget(self.oneri_lbl)
        lo.addWidget(hero)

        metrik_row = QHBoxLayout()
        metrik_row.setSpacing(14)
        self.m_profil = metrik_karti("0%", "Profil Sağlığı", "#0F766E")
        self.m_sonraki = metrik_karti("-", "Sıradaki Aksiyon", "#2563EB")
        self.m_durum = metrik_karti("-", "Mentor Durumu", "#D97706")
        for m in (self.m_profil, self.m_sonraki, self.m_durum):
            metrik_row.addWidget(m)
        lo.addLayout(metrik_row)

        aksiyon = kart()
        aksiyon_lo = QVBoxLayout(aksiyon)
        aksiyon_lo.setContentsMargins(20, 16, 20, 16)
        aksiyon_lo.setSpacing(10)
        aksiyon_lo.addWidget(baslik("Hızlı Aksiyonlar", renk="#0F3D3A"))

        btn_row = QHBoxLayout()
        self.mentor_btn = QPushButton("Mentor Değerlendirmesi İste")
        self.mentor_btn.setObjectName("success")
        self.mentor_btn.clicked.connect(self._mentor_talebi_olustur)
        self.demo_btn = QPushButton("Demo Verilerini Zenginleştir")
        self.demo_btn.clicked.connect(self._demo_yenile)
        btn_row.addWidget(self.mentor_btn)
        btn_row.addWidget(self.demo_btn)
        btn_row.addStretch()
        aksiyon_lo.addLayout(btn_row)

        self.aksiyon_notu = QLabel("")
        self.aksiyon_notu.setWordWrap(True)
        self.aksiyon_notu.setStyleSheet("color:#64748B;font-size:9pt;")
        aksiyon_lo.addWidget(self.aksiyon_notu)
        lo.addWidget(aksiyon)

        plan = kart()
        plan_lo = QVBoxLayout(plan)
        plan_lo.setContentsMargins(20, 16, 20, 16)
        plan_lo.setSpacing(10)
        plan_lo.addWidget(baslik("Önerilen Haftalık Odak", renk="#0F3D3A"))
        self.plan_lo = QVBoxLayout()
        plan_lo.addLayout(self.plan_lo)
        lo.addWidget(plan)
        lo.addStretch()

        scroll.setWidget(w)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def yukle(self):
        ist = api_get(f"/api/istatistik/{self.uid}")
        cvler = api_get(f"/api/cv/{self.uid}")
        roadmaplar = api_get(f"/api/roadmap/{self.uid}")
        etkilesimler = api_get(self._etkilesim_path())

        cv_sayisi = ist.get("cv_sayisi", 0) if "hata" not in ist else 0
        beceri_sayisi = ist.get("beceri_sayisi", 0) if "hata" not in ist else 0
        ilerleme = ist.get("genel_ilerleme", 0) if "hata" not in ist else 0
        rozet = ist.get("rozet_sayisi", 0) if "hata" not in ist else 0

        profil_sagligi = min(100, cv_sayisi * 20 + min(beceri_sayisi, 10) * 5 + int(ilerleme * 0.3) + min(rozet, 10) * 3)
        self._set_val(self.m_profil, f"{profil_sagligi}%")

        son_aksiyon, aciklama = self._sonraki_aksiyon(cv_sayisi, beceri_sayisi, ilerleme, etkilesimler)
        self._set_val(self.m_sonraki, son_aksiyon)
        self.oneri_lbl.setText(aciklama)

        mentor_durum = "Yok"
        if isinstance(etkilesimler, list) and etkilesimler:
            mentor_durum = etkilesimler[0].get("durum_etiketi", "Talep var")
        self._set_val(self.m_durum, mentor_durum[:18])

        self.mentor_btn.setVisible(self.rol not in ("mentor", "hr_manager"))
        self.aksiyon_notu.setText(
            "Bu merkez; CV, beceri, rozet, yol haritası ve mentor durumunu tek ekranda yorumlar. "
            "Dashboard KPI'ları veritabanından geldiği için CV onayı, beceri ekleme veya roadmap ilerlemesi sonrası yenilenir."
        )

        self._planlari_yaz(cv_sayisi, beceri_sayisi, ilerleme, cvler, roadmaplar)

    def _etkilesim_path(self):
        if self.rol == "mentor":
            return "/api/etkilesimler/mentor"
        if self.rol == "hr_manager":
            return "/api/etkilesimler/ik"
        return f"/api/etkilesimler/kullanici/{self.uid}"

    def _sonraki_aksiyon(self, cv_sayisi, beceri_sayisi, ilerleme, etkilesimler):
        if self.rol == "mentor":
            return "CV İncele", "Mentor hesabı için öncelik bekleyen CV ve değerlendirme taleplerini sonuçlandırmaktır."
        if self.rol == "hr_manager":
            return "Aday Seç", "İK hesabı için öncelik mentor onaylı adayları mülakat listesine taşımaktır."
        if cv_sayisi == 0:
            return "CV Yükle", "İlk adım CV yükleyerek sistemin beceri ve gap analizini başlatmaktır."
        if beceri_sayisi < 5:
            return "Beceri Ekle", "Profilin daha güçlü görünmesi için en az 5 beceri seviyesi belirt."
        if ilerleme < 50:
            return "Planı İlerle", "Yol haritasında yüzde 50 eşiği mentora daha güçlü bir sinyal verir."
        if not isinstance(etkilesimler, list) or not etkilesimler:
            return "Mentor Talebi", "Hazır profilini mentor değerlendirmesine göndererek İK akışını başlatabilirsin."
        return "Mülakata Hazırlan", "Profilin iş akışına girmiş durumda; sıradaki değerli adım mülakat hazırlığı."

    def _planlari_yaz(self, cv_sayisi, beceri_sayisi, ilerleme, cvler, roadmaplar):
        while self.plan_lo.count():
            item = self.plan_lo.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        maddeler = []
        if cv_sayisi == 0:
            maddeler.append("CV yükle ve mentor incelemesine hazır hale getir.")
        if beceri_sayisi < 8:
            maddeler.append("Piyasa kataloğundan en az 3 yeni beceri ekle.")
        if isinstance(roadmaplar, list) and roadmaplar:
            maddeler.append("Yol haritasında en az bir adımı tamamlandı durumuna getir.")
        else:
            maddeler.append("Hedef rol için yeni yol haritası oluştur.")
        if ilerleme >= 50:
            maddeler.append("Mentor değerlendirmesi iste ve İK havuzuna geçmeye hazırlan.")

        for madde in maddeler:
            lbl = QLabel(f"• {madde}")
            lbl.setStyleSheet("color:#1F2937;font-size:10pt;")
            lbl.setWordWrap(True)
            self.plan_lo.addWidget(lbl)

    def _mentor_talebi_olustur(self):
        sonuc = api_post("/api/etkilesimler/talep-olustur", {
            "requester_id": self.uid,
            "note": "Profilim ve CV analizim için mentor değerlendirmesi istiyorum.",
        })
        if "hata" in sonuc:
            QMessageBox.warning(self, "Hata", sonuc["hata"])
        else:
            QMessageBox.information(self, "Başarılı", sonuc.get("mesaj", "Talep oluşturuldu."))
            self.yukle()

    def _demo_yenile(self):
        sonuc = api_post("/api/demo/yenile", {})
        if "hata" in sonuc:
            QMessageBox.warning(self, "Hata", sonuc["hata"])
        else:
            QMessageBox.information(self, "Demo Güncellendi", sonuc.get("mesaj", "Demo verileri güncellendi."))
            self.yukle()

    @staticmethod
    def _set_val(krt: QFrame, deger: str):
        lbls = krt.findChildren(QLabel)
        if lbls:
            lbls[0].setText(deger)
