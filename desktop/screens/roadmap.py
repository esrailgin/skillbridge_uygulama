from urllib.parse import quote

from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from desktop.api import api_get, api_patch, api_post
from desktop.ui.components import baslik, kart, metrik_karti


class RoadmapSayfasi(QWidget):
    def __init__(self, uid: str):
        super().__init__()
        self.uid = uid
        self.aktif_roadmap_id = None
        self._build()

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        w = QWidget()
        lo = QVBoxLayout(w)
        lo.setContentsMargins(28, 24, 28, 24)
        lo.setSpacing(16)

        bilgi = QLabel(
            "Yol haritası, hedef role ulaşmak için tamamlamanız gereken haftalık adımları, çıktıları ve ilerlemeyi takip eder."
        )
        bilgi.setWordWrap(True)
        bilgi.setStyleSheet("color:#64748B;font-size:9pt;")
        lo.addWidget(bilgi)

        olustur_krt = kart()
        ok_lo = QHBoxLayout(olustur_krt)
        ok_lo.setContentsMargins(16, 12, 16, 12)

        label = QLabel("Hedef Rol:")
        label.setStyleSheet("color:#1F2937;font-size:9pt;font-weight:700;")

        self.rol_input = QLineEdit()
        self.rol_input.setPlaceholderText("Örn: Veri Analisti, İK Analitiği Uzmanı")
        self.rol_input.setFixedWidth(340)

        olustur_btn = QPushButton("Yeni Plan Oluştur")
        olustur_btn.setObjectName("success")
        olustur_btn.clicked.connect(self._olustur)

        ok_lo.addWidget(label)
        ok_lo.addWidget(self.rol_input)
        ok_lo.addSpacing(10)
        ok_lo.addWidget(olustur_btn)
        ok_lo.addStretch()

        lo.addWidget(olustur_krt)

        self.ozet_krt = kart()
        ozet_lo = QVBoxLayout(self.ozet_krt)
        ozet_lo.setContentsMargins(20, 14, 20, 14)
        ozet_lo.setSpacing(10)

        self.hedef_lbl = QLabel("Aktif hedef: -")
        self.hedef_lbl.setStyleSheet("color:#0F3D3A;font-size:12pt;font-weight:800;")
        ozet_lo.addWidget(self.hedef_lbl)

        ph = QHBoxLayout()
        ph_label = QLabel("Genel İlerleme")
        ph_label.setStyleSheet("color:#1F2937;font-size:10pt;font-weight:700;")
        ph.addWidget(ph_label)
        ph.addStretch()

        self.prog_pct = QLabel("0%")
        self.prog_pct.setStyleSheet("color:#0F766E;font-weight:700;")
        ph.addWidget(self.prog_pct)
        ozet_lo.addLayout(ph)

        self.prog_bar = QProgressBar()
        self.prog_bar.setValue(0)
        self.prog_bar.setTextVisible(False)
        self.prog_bar.setFixedHeight(10)
        self.prog_bar.setStyleSheet(
            "QProgressBar{background:#E5E7EB;border-radius:4px;}"
            "QProgressBar::chunk{background:#0F766E;border-radius:4px;}"
        )
        ozet_lo.addWidget(self.prog_bar)

        metrik_row = QHBoxLayout()
        self.m_tamamlanan = metrik_karti("0", "Tamamlanan Adım", "#0E6B5C")
        self.m_toplam_saat = metrik_karti("0", "Toplam Saat", "#38546E")
        self.m_sonraki = metrik_karti("-", "Sonraki Adım", "#B7791F")
        metrik_row.addWidget(self.m_tamamlanan)
        metrik_row.addWidget(self.m_toplam_saat)
        metrik_row.addWidget(self.m_sonraki)
        ozet_lo.addLayout(metrik_row)

        lo.addWidget(self.ozet_krt)

        self.harita_krt = kart()
        self.harita_krt.setStyleSheet(
            "QFrame#card{background:#F8FBFA;border:1px solid #D7E5E1;border-radius:8px;}"
        )
        harita_dis = QVBoxLayout(self.harita_krt)
        harita_dis.setContentsMargins(20, 16, 20, 16)
        harita_dis.setSpacing(10)
        harita_dis.addWidget(baslik("Görsel Yol Haritası", renk="#0F3D3A"))
        self.harita_lo = QGridLayout()
        self.harita_lo.setHorizontalSpacing(10)
        self.harita_lo.setVerticalSpacing(10)
        harita_dis.addLayout(self.harita_lo)
        lo.addWidget(self.harita_krt)

        lo.addWidget(baslik("Haftalık Adımlar", renk="#0F3D3A"))

        self.adim_lo = QVBoxLayout()
        self.adim_lo.setSpacing(8)
        lo.addLayout(self.adim_lo)
        quote = QLabel('"Damlaya damlaya göl olur." - Türk atasözü')
        quote.setWordWrap(True)
        quote.setStyleSheet("color:#64748B;font-size:9pt;font-style:italic;padding:8px 2px;")
        lo.addWidget(quote)
        lo.addStretch()

        scroll.setWidget(w)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def yukle(self):
        roadmaplar = api_get(f"/api/roadmap/{self.uid}")

        while self.adim_lo.count():
            item = self.adim_lo.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not isinstance(roadmaplar, list) or not roadmaplar:
            self.aktif_roadmap_id = None
            self.prog_bar.setValue(0)
            self.prog_pct.setText("0%")
            self.hedef_lbl.setText("Aktif hedef: -")
            self._set_val(self.m_tamamlanan, "0")
            self._set_val(self.m_toplam_saat, "0")
            self._set_val(self.m_sonraki, "-")

            self._harita_ciz([])
            bos = QLabel("Henüz yol haritası yok. Yukarıdan hedef rol girerek oluşturabilirsiniz.")
            bos.setStyleSheet("color:#64748B;font-size:9pt;")
            self.adim_lo.addWidget(bos)
            return

        rm = roadmaplar[0]
        self.aktif_roadmap_id = rm["id"]
        adimlar = rm.get("adimlar", [])

        ilerleme = rm.get("ilerleme", 0)
        self.prog_bar.setValue(int(ilerleme))
        self.prog_pct.setText(f"{ilerleme:.0f}%")
        self.hedef_lbl.setText(f"Aktif hedef: {self._rol_tr(rm.get('hedef_rol', '-'))}")

        tamamlanan = sum(1 for a in adimlar if a.get("durum") == "completed")
        toplam_saat = sum(int(a.get("saat", 0) or 0) for a in adimlar)
        sonraki = next((a for a in adimlar if a.get("durum") != "completed"), None)

        self._set_val(self.m_tamamlanan, f"{tamamlanan}/{len(adimlar)}")
        self._set_val(self.m_toplam_saat, str(toplam_saat))
        self._set_val(self.m_sonraki, str(sonraki.get("hafta", "-")) if sonraki else "Bitti")
        self._harita_ciz(adimlar)

        for adim in adimlar:
            self._adim_karti_ekle(adim)

    def _harita_ciz(self, adimlar: list[dict]):
        while self.harita_lo.count():
            item = self.harita_lo.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not adimlar:
            bos = QLabel("Plan oluşturulduğunda adımlar burada harita gibi görünür.")
            bos.setStyleSheet("color:#64748B;font-size:9pt;")
            self.harita_lo.addWidget(bos, 0, 0)
            return

        renkler = {"completed": "#0E6B5C", "in_progress": "#B7791F", "not_started": "#94A3B8"}
        for i, adim in enumerate(adimlar[:8]):
            durum = adim.get("durum", "not_started")
            renk = renkler.get(durum, "#94A3B8")
            node = QFrame()
            node.setMinimumWidth(170)
            node.setFixedHeight(118)
            node.setStyleSheet(
                f"QFrame{{background:#FFFFFF;border:1px solid #E2E8F0;"
                f"border-top:4px solid {renk};border-radius:8px;}}"
            )
            n_lo = QVBoxLayout(node)
            n_lo.setContentsMargins(10, 8, 10, 8)
            hafta = adim.get("hafta", adim.get("sira", i + 1))
            no = QLabel(f"Hafta {hafta}")
            no.setStyleSheet(f"color:{renk};font-size:8.5pt;font-weight:900;")
            baslik = adim.get("baslik", "Adım")
            if len(baslik) > 38:
                baslik = baslik[:35] + "..."
            ad = QLabel(baslik)
            ad.setWordWrap(True)
            ad.setStyleSheet("color:#1F2937;font-size:8.5pt;font-weight:800;")
            durum_lbl = QLabel({"completed": "Bitti", "in_progress": "Sürüyor", "not_started": "Bekliyor"}.get(durum, durum))
            durum_lbl.setStyleSheet("color:#64748B;font-size:8pt;")
            n_lo.addWidget(no)
            n_lo.addWidget(ad)
            n_lo.addStretch()
            n_lo.addWidget(durum_lbl)
            self.harita_lo.addWidget(node, i // 4, i % 4)
    def _adim_karti_ekle(self, adim: dict):
        durum = adim.get("durum", "not_started")

        renkler = {
            "completed": "#0F766E",
            "in_progress": "#D97706",
            "not_started": "#94A3B8",
        }

        ikonlar = {
            "completed": "●",
            "in_progress": "◐",
            "not_started": "○",
        }

        krt2 = QFrame()
        krt2.setObjectName("card")
        krt2.setStyleSheet(
            f"QFrame#card{{background:#FFFFFF;"
            f"border:1px solid {renkler.get(durum, '#E5E7EB')};"
            f"border-radius:8px;}}"
        )

        krt_lo = QHBoxLayout(krt2)
        krt_lo.setContentsMargins(16, 12, 16, 12)
        krt_lo.setSpacing(14)

        ikon = QLabel(ikonlar.get(durum, "○"))
        ikon.setStyleSheet(
            f"font-size:16pt;color:{renkler.get(durum, '#94A3B8')};"
        )
        ikon.setFixedWidth(28)
        krt_lo.addWidget(ikon)

        icerik_lo = QVBoxLayout()
        icerik_lo.setSpacing(4)

        hafta = adim.get("hafta", adim.get("sira", ""))
        bas = QLabel(f"Hafta {hafta} · {adim.get('baslik', '')}")
        bas.setStyleSheet("font-weight:700;font-size:10pt;color:#1F2937;")

        ack = QLabel(adim.get("aciklama", ""))
        ack.setStyleSheet("color:#64748B;font-size:9pt;")
        ack.setWordWrap(True)

        cikti = QLabel(f"Beklenen çıktı: {adim.get('cikti', '-')}")
        cikti.setStyleSheet("color:#0F766E;font-size:8.5pt;font-weight:600;")
        cikti.setWordWrap(True)

        oncelik = {
            "high": "Yüksek",
            "medium": "Orta",
            "low": "Düşük",
        }.get(adim.get("oncelik", ""), adim.get("oncelik", ""))

        meta = QLabel(f"{adim.get('saat', '?')} saat  ·  Öncelik: {oncelik}")
        meta.setStyleSheet("color:#64748B;font-size:8pt;")

        icerik_lo.addWidget(bas)
        icerik_lo.addWidget(ack)
        icerik_lo.addWidget(cikti)
        icerik_lo.addWidget(meta)

        krt_lo.addLayout(icerik_lo, stretch=1)

        if durum == "completed":
            done = QLabel("Tamamlandı")
            done.setStyleSheet("color:#0F766E;font-size:9pt;font-weight:700;")
            krt_lo.addWidget(done)
        elif durum == "in_progress":
            btn = QPushButton("Tamamla")
            btn.setFixedWidth(100)
            btn.setObjectName("success")
            btn.clicked.connect(lambda _, a=adim: self._adim_guncelle(a, "completed"))
            krt_lo.addWidget(btn)
        else:
            btn = QPushButton("Başla")
            btn.setFixedWidth(100)
            btn.clicked.connect(lambda _, a=adim: self._adim_guncelle(a, "in_progress"))
            krt_lo.addWidget(btn)

        self.adim_lo.addWidget(krt2)

    def _adim_guncelle(self, adim: dict, yeni_durum: str):
        sonuc = api_patch(
            "/api/roadmap/adim-guncelle",
            {
                "roadmap_id": self.aktif_roadmap_id,
                "adim_id": adim["id"],
                "durum": yeni_durum,
            },
        )

        if "hata" in sonuc:
            QMessageBox.warning(self, "Hata", sonuc["hata"])
        else:
            self.yukle()

    def _olustur(self):
        rol = self.rol_input.text().strip()

        if not rol:
            QMessageBox.warning(self, "Uyarı", "Hedef rol boş olamaz.")
            return

        hedef_rol = quote(rol)
        sonuc = api_post(f"/api/roadmap/{self.uid}/olustur?hedef_rol={hedef_rol}&hafta=8")

        if "hata" in sonuc:
            QMessageBox.warning(self, "Hata", sonuc["hata"])
        else:
            QMessageBox.information(self, "Başarılı", "Hedef role özel yol haritası oluşturuldu.")
            self.rol_input.clear()
            self.yukle()

    @staticmethod
    def _rol_tr(rol: str) -> str:
        return {
            "Junior Data Analyst": "Junior Veri Analisti",
            "Data Analyst": "Veri Analisti",
            "Associate Analyst": "Genç Analist",
        }.get(rol, rol)

    @staticmethod
    def _set_val(krt: QFrame, deger: str):
        lbls = krt.findChildren(QLabel)
        if lbls:
            lbls[0].setText(deger)






