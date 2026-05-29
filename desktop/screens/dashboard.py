from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QScrollArea, QVBoxLayout, QWidget

from desktop.api import api_get
from desktop.ui.components import baslik, kart, metrik_karti


class DashboardSayfasi(QWidget):
    def __init__(self, uid: str, kullanici: dict | None = None):
        super().__init__(); self.uid = uid; self.kullanici = kullanici or {}; self.rol = self.kullanici.get("rol", ""); self._build()

    def _build(self):
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame)
        w = QWidget(); lo = QVBoxLayout(w); lo.setContentsMargins(28, 24, 28, 24); lo.setSpacing(16)

        hero = kart(); hero.setStyleSheet("QFrame#card{background:#F8FBFA;border:1px solid #D7E5E1;border-left:4px solid #0E6B5C;border-radius:8px;}")
        hero_lo = QHBoxLayout(hero); hero_lo.setContentsMargins(22, 18, 22, 18); hero_lo.setSpacing(18)
        mark = QLabel("SB"); mark.setFixedSize(54, 54); mark.setStyleSheet("background:#FFFFFF;color:#0E6B5C;border:1px solid #D7E5E1;border-radius:10px;font-size:13pt;font-weight:900;")
        title_col = QVBoxLayout(); self.unvan_lbl = QLabel("Başlangıç Yolcusu"); self.unvan_lbl.setStyleSheet("font-size:16pt;font-weight:900;color:#0F3D3A;")
        self.odak_lbl = QLabel("CV yükle, becerilerini güncelle ve mentor değerlendirmesi iste."); self.odak_lbl.setWordWrap(True); self.odak_lbl.setStyleSheet("color:#475569;font-size:10pt;")
        title_col.addWidget(self.unvan_lbl); title_col.addWidget(self.odak_lbl); hero_lo.addWidget(mark); hero_lo.addLayout(title_col, 1)
        self.sonraki_lbl = QLabel("Canlı profil özeti"); self.sonraki_lbl.setStyleSheet("color:#64748B;font-size:9pt;font-weight:700;"); hero_lo.addWidget(self.sonraki_lbl)
        lo.addWidget(hero)

        m_row = QHBoxLayout(); m_row.setSpacing(14)
        self.m_cv = metrik_karti("0", "CV Analizi", "#38546E")
        self.m_beceri = metrik_karti("0", "Beceri", "#0E6B5C")
        self.m_rozet = metrik_karti("0", "Rozet", "#B7791F")
        self.m_ilerleme = metrik_karti("0%", "Yol Haritası", "#263241")
        for m in (self.m_cv, self.m_beceri, self.m_rozet, self.m_ilerleme): m_row.addWidget(m)
        lo.addLayout(m_row)

        main = QHBoxLayout(); main.setSpacing(14)
        bc = kart(); bc_lo = QVBoxLayout(bc); bc_lo.setContentsMargins(20,16,20,16); bc_lo.setSpacing(10); bc_lo.addWidget(baslik("Beceri Profili", renk="#0F3D3A")); self.beceri_lo = QVBoxLayout(); bc_lo.addLayout(self.beceri_lo); main.addWidget(bc, 2)
        akis = self._akis_karti(); main.addWidget(akis, 1)
        lo.addLayout(main)

        quote = QLabel('"Emek, yolunu bulan fikirdir."')
        quote.setWordWrap(True); quote.setStyleSheet("color:#64748B;font-size:9pt;font-style:italic;padding:8px 2px;")
        lo.addWidget(quote); lo.addStretch()
        scroll.setWidget(w); outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.addWidget(scroll)

    def yukle(self):
        ist = api_get(f"/api/istatistik/{self.uid}"); cv_sayisi = beceri_sayisi = rozet_sayisi = ilerleme = 0
        if "hata" not in ist:
            cv_sayisi = ist.get("cv_sayisi", 0); beceri_sayisi = ist.get("beceri_sayisi", 0); rozet_sayisi = ist.get("rozet_sayisi", 0); ilerleme = ist.get("genel_ilerleme", 0)
            self._set_val(self.m_cv, str(cv_sayisi)); self._set_val(self.m_beceri, str(beceri_sayisi)); self._set_val(self.m_rozet, str(rozet_sayisi)); self._set_val(self.m_ilerleme, f"{ilerleme:.0f}%")
            self.unvan_lbl.setText(self._unvan_tr(ist.get("career_title", "Keşif Aşaması")))
        if self.rol == "mentor":
            talepler = api_get("/api/etkilesimler/mentor")
            bekleyen = len(talepler) if isinstance(talepler, list) else 0
            self.unvan_lbl.setText("Mentor Değerlendirme Paneli")
            self.odak_lbl.setText(f"Bugün {bekleyen} aday değerlendirme akışında. Öncelik CV ve mentor notlarını sonuçlandırmak.")
            self.sonraki_lbl.setText("Mentor rol görünümü")
        elif self.rol == "hr_manager":
            adaylar = api_get("/api/etkilesimler/ik")
            firsatlar = api_get("/api/firsatlar")
            aday_sayisi = len(adaylar) if isinstance(adaylar, list) else 0
            firsat_sayisi = len(firsatlar) if isinstance(firsatlar, list) else 0
            self.unvan_lbl.setText("İK Aday Havuzu Paneli")
            self.odak_lbl.setText(f"{aday_sayisi} mentor onaylı aday ve {firsat_sayisi} aktif şirket fırsatı izleniyor.")
            self.sonraki_lbl.setText("İK rol görünümü")
        else:
            self.odak_lbl.setText(self._odak_metni(cv_sayisi, beceri_sayisi, ilerleme))

        profil = api_get(f"/api/kullanicilar/{self.uid}/profil")
        while self.beceri_lo.count():
            item = self.beceri_lo.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        if "hata" in profil: return
        renkler = ["#0E6B5C", "#38546E", "#B7791F", "#64748B", "#6B7D5E", "#8A4F3D"]
        lvl_map = {"beginner":25,"intermediate":55,"advanced":80,"expert":100}; lvl_label = {"beginner":"Başlangıç","intermediate":"Orta","advanced":"İleri","expert":"Uzman"}
        beceriler = profil.get("beceriler", [])[:6]
        if not beceriler:
            bos = QLabel("Henüz beceri eklenmemiş. Beceriler sayfasından profilini güçlendirebilirsin."); bos.setWordWrap(True); bos.setStyleSheet("color:#64748B;font-size:9pt;"); self.beceri_lo.addWidget(bos); return
        for i, b in enumerate(beceriler):
            row = QHBoxLayout(); ad = QLabel(b["ad"]); ad.setFixedWidth(150); ad.setStyleSheet("color:#1F2937;font-size:9pt;font-weight:700;")
            bar = QProgressBar(); bar.setRange(0,100); seviye = b.get("seviye", "beginner"); bar.setValue(lvl_map.get(seviye, 50)); bar.setTextVisible(False); bar.setFixedHeight(9)
            clr = renkler[i % len(renkler)]; bar.setStyleSheet(f"QProgressBar{{background:#E5E7EB;border-radius:4px;}}QProgressBar::chunk{{background:{clr};border-radius:4px;}}")
            pct = QLabel(lvl_label.get(seviye, seviye)); pct.setFixedWidth(85); pct.setStyleSheet(f"color:{clr};font-size:8pt;font-weight:700;")
            row.addWidget(ad); row.addWidget(bar, 1); row.addWidget(pct); wrap = QWidget(); wrap.setLayout(row); self.beceri_lo.addWidget(wrap)

    @staticmethod
    def _akis_karti() -> QFrame:
        k = kart(); k.setStyleSheet("QFrame#card{background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;}")
        lo = QVBoxLayout(k); lo.setContentsMargins(20,16,20,16); lo.setSpacing(10); lo.addWidget(baslik("Ürün Akışı", renk="#0F3D3A"))
        for i, (ad, alt, renk) in enumerate([("Profil", "CV + beceri", "#38546E"), ("Kanıt", "rozet + GitHub", "#0E6B5C"), ("Onay", "mentor notu", "#B7791F"), ("Fırsat", "İK kısa liste", "#263241")], 1):
            row = QFrame(); row.setStyleSheet(f"QFrame{{background:#F8FBFA;border:1px solid #E2E8F0;border-left:4px solid {renk};border-radius:7px;}}")
            rl = QHBoxLayout(row); rl.setContentsMargins(10,8,10,8); no = QLabel(f"0{i}"); no.setFixedWidth(28); no.setStyleSheet(f"color:{renk};font-weight:900;")
            txt = QLabel(f"{ad}\n{alt}"); txt.setStyleSheet("color:#1F2937;font-size:9pt;font-weight:700;"); rl.addWidget(no); rl.addWidget(txt); lo.addWidget(row)
        return k

    @staticmethod
    def _odak_metni(cv_sayisi: int, beceri_sayisi: int, ilerleme: float) -> str:
        if cv_sayisi == 0: return "Öncelik CV yüklemek. CV yüklendiğinde mentor incelemesi ve İK fırsat akışı başlar."
        if beceri_sayisi < 5: return "Beceri profilini güçlendir. En az 5 beceri eklemek eşleşme kalitesini artırır."
        if ilerleme < 50: return "Yol haritasındaki ilk yarıyı tamamla. Yüzde 50 eşiği mentor onayı için güçlü bir sinyaldir."
        return "Profil güçlü görünüyor. Mentor değerlendirmesi ve İK fırsatlarına hazırsın."

    @staticmethod
    def _unvan_tr(unvan: str) -> str:
        return {"Explorer":"Keşif Aşaması","Junior Pathfinder":"Başlangıç Yolcusu","Associate Analyst":"Genç Analist","Data Analyst":"Veri Analisti","Junior Data Analyst":"Junior Veri Analisti","Career Mentor":"Kariyer Mentoru","Talent Manager":"Yetenek Yöneticisi"}.get(unvan, unvan)

    @staticmethod
    def _set_val(krt: QFrame, deger: str):
        lbls = krt.findChildren(QLabel)
        if lbls: lbls[0].setText(deger)


