from pathlib import Path

import httpx
from PyQt6.QtGui import QPageSize, QTextDocument
from PyQt6.QtPrintSupport import QPrinter
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

from desktop.api import api_get, api_headers
from desktop.config import API
from desktop.ui.components import baslik, kart, metrik_karti


class RaporlarSayfasi(QWidget):
    def __init__(self, kullanici: dict):
        super().__init__()
        self.kullanici = kullanici
        self.uid = kullanici.get("kullanici_id", "")
        self.rol = kullanici.get("rol", "")
        self._report_cache = {}
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
            "QFrame#card{background:#F8FBFA;border:1px solid #D7E5E1;"
            "border-left:4px solid #0E6B5C;border-radius:8px;}"
        )
        hl = QVBoxLayout(hero)
        hl.setContentsMargins(20, 16, 20, 16)
        t = QLabel("Kariyer Raporu ve Demo Paneli")
        t.setStyleSheet("font-size:15pt;font-weight:900;color:#0F3D3A;")
        d = QLabel(
            "CV, beceri, rozet, yol haritası ve rol talepleri tek ekranda okunabilir ürün hikayesine dönüşür."
        )
        d.setWordWrap(True)
        d.setStyleSheet("color:#475569;font-size:10pt;")
        hl.addWidget(t)
        hl.addWidget(d)
        lo.addWidget(hero)

        m = QHBoxLayout()
        m.setSpacing(14)
        self.m_cv = metrik_karti("0", "CV", "#38546E")
        self.m_beceri = metrik_karti("0", "Beceri", "#0E6B5C")
        self.m_rozet = metrik_karti("0", "Rozet", "#B7791F")
        self.m_ilerleme = metrik_karti("0%", "İlerleme", "#263241")
        for x in (self.m_cv, self.m_beceri, self.m_rozet, self.m_ilerleme):
            m.addWidget(x)
        lo.addLayout(m)

        export_row = QHBoxLayout()
        pdf_btn = QPushButton("Profesyonel PDF İndir")
        pdf_btn.clicked.connect(lambda: self._export("pdf"))
        xls_btn = QPushButton("Excel Al")
        xls_btn.clicked.connect(lambda: self._export("excel"))
        export_row.addWidget(pdf_btn)
        export_row.addWidget(xls_btn)
        export_row.addStretch()
        lo.addLayout(export_row)

        body = QHBoxLayout()
        body.setSpacing(14)
        self.chart_krt = kart()
        self.chart_lo = QVBoxLayout(self.chart_krt)
        self.chart_lo.setContentsMargins(20, 16, 20, 16)
        body.addWidget(self.chart_krt, 2)

        self.ozet_krt = kart()
        self.ozet_lo = QVBoxLayout(self.ozet_krt)
        self.ozet_lo.setContentsMargins(20, 16, 20, 16)
        body.addWidget(self.ozet_krt, 1)
        lo.addLayout(body)

        self.akıs_krt = kart()
        self.akıs_lo = QVBoxLayout(self.akıs_krt)
        self.akıs_lo.setContentsMargins(20, 16, 20, 16)
        self.akıs_lo.setSpacing(8)
        lo.addWidget(self.akıs_krt)

        quote = QLabel('"Başarı, hazırlık ile fırsatın buluştuğu yerdir." - Seneca')
        quote.setStyleSheet("color:#64748B;font-size:9pt;font-style:italic;padding:8px;")
        lo.addWidget(quote)
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

        vals = {"cv": 0, "beceri": 0, "rozet": 0, "ilerleme": 0, "unvan": "Keşif Aşaması"}
        if "hata" not in ist:
            vals = {
                "cv": ist.get("cv_sayisi", 0),
                "beceri": ist.get("beceri_sayisi", 0),
                "rozet": ist.get("rozet_sayisi", 0),
                "ilerleme": ist.get("genel_ilerleme", 0),
                "unvan": self._rol_tr(ist.get("career_title", "Keşif Aşaması")),
            }
            self._set_val(self.m_cv, str(vals["cv"]))
            self._set_val(self.m_beceri, str(vals["beceri"]))
            self._set_val(self.m_rozet, str(vals["rozet"]))
            self._set_val(self.m_ilerleme, f"{vals['ilerleme']:.0f}%")

        self._temizle(self.chart_lo)
        self._temizle(self.ozet_lo)
        self._temizle(self.akıs_lo)

        self.chart_lo.addWidget(baslik("Profil Güç Grafiği", renk="#0F3D3A"))
        chart_items = [
            ("CV Hazırlığı", vals["cv"] * 35, 100, "#38546E"),
            ("Beceri Derinliği", min(vals["beceri"] * 12, 100), 100, "#0E6B5C"),
            ("Rozet Kanıtı", min(vals["rozet"] * 8, 100), 100, "#B7791F"),
            ("Yol Haritası", vals["ilerleme"], 100, "#263241"),
        ]
        for ad, val, maxv, renk in chart_items:
            self._bar(self.chart_lo, ad, val, maxv, renk)

        son_cv = "CV kaydı yok"
        if isinstance(cvler, list) and cvler:
            son_cv = self._durum_tr(cvler[0].get("durum", ""))

        roadmap = "Yol haritası yok"
        if isinstance(roadmaplar, list) and roadmaplar:
            roadmap = f"{self._rol_tr(roadmaplar[0].get('hedef_rol', 'Hedef rol'))} - %{roadmaplar[0].get('ilerleme', 0):.0f}"

        self.ozet_lo.addWidget(baslik("Özet", renk="#0F3D3A"))
        self._satir(self.ozet_lo, "Son CV Durumu", son_cv)
        self._satir(self.ozet_lo, "Aktif Yol Haritası", roadmap)
        self._satir(self.ozet_lo, "Kariyer Unvanı", vals["unvan"])

        akis = []
        self.akıs_lo.addWidget(baslik("Talep ve Rol Akışı", renk="#0F3D3A"))
        if isinstance(etkilesimler, list) and etkilesimler:
            for e in etkilesimler[:6]:
                ad = e.get("ad_soyad", self.kullanici.get("ad_soyad", ""))
                durum = e.get("durum_etiketi", e.get("durum", ""))
                akis.append((ad, durum))
                self._satir(self.akıs_lo, ad, durum)
        else:
            bos = QLabel("Bu rolde henüz talep kaydı yok.")
            bos.setStyleSheet("color:#64748B;font-size:9pt;")
            self.akıs_lo.addWidget(bos)

        self._report_cache = {
            "vals": vals,
            "son_cv": son_cv,
            "roadmap": roadmap,
            "akis": akis,
            "chart_items": chart_items,
            "ad_soyad": self.kullanici.get("ad_soyad", "Kullanıcı"),
            "rol": self._rol_etiketi(self.rol),
            "email": self.kullanici.get("email", ""),
        }

    def _export(self, tur: str):
        ext = "pdf" if tur == "pdf" else "xls"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Raporu Kaydet",
            str(Path.home() / f"skillbridge_rapor.{ext}"),
            f"*.{ext}",
        )
        if not path:
            return

        if not path.lower().endswith(f".{ext}"):
            path = f"{path}.{ext}"

        try:
            if tur == "pdf":
                self._export_pdf_local(path)
            else:
                r = httpx.get(f"{API}/api/raporlar/{self.uid}/{tur}", headers=api_headers(), timeout=20)
                r.raise_for_status()
                Path(path).write_bytes(r.content)
            QMessageBox.information(self, "Rapor", "Rapor dışa aktarıldı.")
        except Exception as e:
            QMessageBox.warning(self, "Rapor", f"Rapor alınamadı: {e}")

    def _export_pdf_local(self, path: str):
        if not self._report_cache:
            self.yukle()
        html = self._rapor_html()
        doc = QTextDocument()
        doc.setHtml(html)

        printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        doc.print(printer)

    def _rapor_html(self) -> str:
        c = self._report_cache
        vals = c["vals"]
        chart_html = "".join(
            f"""
            <div class='bar-row'>
                <div class='bar-label'>{ad}<span>%{min(int(val), 100)}</span></div>
                <div class='bar-bg'><div class='bar-fill' style='width:{min(int(val), 100)}%; background:{renk};'></div></div>
            </div>
            """
            for ad, val, _maxv, renk in c["chart_items"]
        )
        akis_html = "".join(
            f"<tr><td>{ad}</td><td>{durum}</td></tr>" for ad, durum in c["akis"]
        ) or "<tr><td colspan='2'>Bu rolde henüz talep kaydı yok.</td></tr>"

        return f"""
        <!doctype html>
        <html>
        <head>
        <meta charset='utf-8'>
        <style>
            body {{ font-family:'Segoe UI', Arial, sans-serif; color:#1F2937; margin:0; font-size:14pt; }}
            .page {{ padding:18pt; }}
            .hero {{ background:#F8FBFA; border:1px solid #D7E5E1; border-left:5pt solid #0E6B5C; padding:16pt; border-radius:8pt; }}
            h1 {{ margin:0; color:#113F3B; font-size:26pt; line-height:1.15; }}
            .subtitle {{ color:#475569; margin-top:7pt; font-size:14pt; line-height:1.45; }}
            .identity {{ display:grid; grid-template-columns:1.5fr 1fr 1.2fr; gap:10pt; margin-top:14pt; }}
            .box {{ border:1px solid #E5E7EB; border-radius:8pt; padding:12pt; background:#FFFFFF; }}
            .label {{ color:#64748B; font-size:11pt; font-weight:700; }}
            .value {{ color:#113F3B; font-size:15pt; font-weight:800; margin-top:4pt; line-height:1.25; }}
            .metrics {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10pt; margin:14pt 0; }}
            .metric {{ border-radius:8pt; padding:13pt; border:1px solid #E5E7EB; }}
            .metric strong {{ display:block; font-size:24pt; color:#113F3B; line-height:1.05; }}
            .metric span {{ color:#64748B; font-size:11pt; font-weight:700; }}
            .section {{ margin-top:15pt; }}
            h2 {{ color:#0F3D3A; font-size:18pt; margin:0 0 9pt 0; line-height:1.2; }}
            table {{ width:100%; border-collapse:collapse; font-size:12.5pt; line-height:1.45; }}
            td, th {{ border:1px solid #E5E7EB; padding:9pt; vertical-align:top; }}
            th {{ background:#113F3B; color:white; text-align:left; }}
            .bar-row {{ margin-bottom:10pt; }}
            .bar-label {{ font-size:12.5pt; font-weight:800; margin-bottom:5pt; color:#334155; }}
            .bar-label span {{ float:right; color:#0E6B5C; }}
            .bar-bg {{ height:10pt; border-radius:99px; background:#E5E7EB; overflow:hidden; }}
            .bar-fill {{ height:10pt; border-radius:99px; }}
            .comment {{ background:#F8FBFA; border:1px solid #D7E5E1; border-radius:8pt; padding:12pt; color:#475569; font-size:12.5pt; line-height:1.5; }}
            .footer {{ margin-top:14pt; color:#64748B; font-size:11pt; text-align:center; }}
        </style>
        </head>
        <body>
        <div class='page'>
            <div class='hero'>
                <h1>SkillBridge Kariyer Raporu</h1>
                <div class='subtitle'>CV, beceri, rozet, yol haritası ve rol etkileşimlerinden oluşturulan profesyonel gelişim özeti.</div>
            </div>

            <div class='identity'>
                <div class='box'><div class='label'>Aday</div><div class='value'>{c['ad_soyad']}</div></div>
                <div class='box'><div class='label'>Rol</div><div class='value'>{c['rol']}</div></div>
                <div class='box'><div class='label'>Unvan</div><div class='value'>{vals['unvan']}</div></div>
            </div>

            <div class='metrics'>
                <div class='metric' style='background:#EEF4FF;'><strong>{vals['cv']}</strong><span>CV Analizi</span></div>
                <div class='metric' style='background:#ECFDF5;'><strong>{vals['beceri']}</strong><span>Beceri</span></div>
                <div class='metric' style='background:#FFF7ED;'><strong>{vals['rozet']}</strong><span>Rozet</span></div>
                <div class='metric' style='background:#F8FAFC;'><strong>%{vals['ilerleme']:.0f}</strong><span>Yol Haritası</span></div>
            </div>

            <div class='section'>
                <h2>Profil Güç Grafiği</h2>
                {chart_html}
            </div>

            <div class='section'>
                <h2>Özet Bilgiler</h2>
                <table>
                    <tr><th>Alan</th><th>Durum</th></tr>
                    <tr><td>Son CV Durumu</td><td>{c['son_cv']}</td></tr>
                    <tr><td>Aktif Yol Haritası</td><td>{c['roadmap']}</td></tr>
                    <tr><td>Kariyer Unvanı</td><td>{vals['unvan']}</td></tr>
                </table>
            </div>

            <div class='section'>
                <h2>Talep ve Rol Akışı</h2>
                <table><tr><th>Kişi</th><th>Durum</th></tr>{akis_html}</table>
            </div>

            <div class='section comment'>
                Bu rapor, adayın iş gücüne hazırlığını tek bir metrik yerine çoklu sinyallerle değerlendirir. CV durumu, beceri derinliği, rozet kanıtı ve yol haritası ilerlemesi birlikte okunduğunda adayın hangi fırsata daha hazır olduğu daha net görünür.
            </div>

            <div class='footer'>SkillBridge · Yeteneklerinizi Geliştirin, Başarıya Köprü Kurun</div>
        </div>
        </body>
        </html>
        """

    def _etkilesim_path(self):
        if self.rol == "mentor":
            return "/api/etkilesimler/mentor"
        if self.rol == "hr_manager":
            return "/api/etkilesimler/ik"
        return f"/api/etkilesimler/kullanici/{self.uid}"

    @staticmethod
    def _bar(layout, ad, val, maxv, renk):
        lbl = QLabel(f"{ad}  %{min(int(val), 100)}")
        lbl.setStyleSheet("color:#1F2937;font-size:9pt;font-weight:800;")
        bar = QProgressBar()
        bar.setRange(0, maxv)
        bar.setValue(min(int(val), 100))
        bar.setTextVisible(False)
        bar.setFixedHeight(10)
        bar.setStyleSheet(
            f"QProgressBar{{background:#E5E7EB;border-radius:5px;}}"
            f"QProgressBar::chunk{{background:{renk};border-radius:5px;}}"
        )
        layout.addWidget(lbl)
        layout.addWidget(bar)

    @staticmethod
    def _durum_tr(durum):
        return {"completed": "Tamamlandı", "pending": "Bekliyor", "failed": "Başarısız"}.get(durum, durum)

    @staticmethod
    def _rol_tr(rol):
        return {
            "Junior Data Analyst": "Junior Veri Analisti",
            "Data Analyst": "Veri Analisti",
            "Explorer": "Keşif Aşaması",
            "Junior Pathfinder": "Başlangıç Yolcusu",
        }.get(rol, rol)

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
    def _temizle(layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    @staticmethod
    def _satir(layout, sol, sag):
        row = QWidget()
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        l = QLabel(sol)
        l.setStyleSheet("color:#1F2937;font-size:9pt;font-weight:800;")
        r = QLabel(str(sag))
        r.setWordWrap(True)
        r.setStyleSheet("color:#0E6B5C;font-size:9pt;font-weight:800;")
        rl.addWidget(l)
        rl.addStretch()
        rl.addWidget(r)
        layout.addWidget(row)

    @staticmethod
    def _set_val(krt, deger):
        lbls = krt.findChildren(QLabel)
        if lbls:
            lbls[0].setText(deger)


