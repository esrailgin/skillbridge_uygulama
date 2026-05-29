from PyQt6.QtWidgets import (
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

from desktop.api import api_get, api_post
from desktop.ui.components import baslik, kart, metrik_karti


class GitHubEntegrasyonSayfasi(QWidget):
    def __init__(self, kullanici: dict):
        super().__init__()
        self.kullanici = kullanici
        self.uid = kullanici.get("kullanici_id", "")
        self.email = kullanici.get("email", "")
        self._demo_loaded = False
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
        hero_lo.setContentsMargins(22, 18, 22, 18)
        title = QLabel("GitHub Entegrasyonu")
        title.setStyleSheet("font-size:16pt;font-weight:900;color:#0F3D3A;")
        desc = QLabel("Repo bağlantısını portfolyo kanıtına dönüştür ve mentor/İK akışında görünür hale getir.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#475569;font-size:10pt;")
        hero_lo.addWidget(title)
        hero_lo.addWidget(desc)
        lo.addWidget(hero)

        form = kart()
        form_lo = QHBoxLayout(form)
        form_lo.setContentsMargins(16, 12, 16, 12)
        self.repo_input = QLineEdit()
        self.repo_input.setPlaceholderText("https://github.com/kullanici/proje veya kullanici/proje")
        self.repo_input.setMinimumWidth(420)
        self.role_input = QLineEdit()
        self.role_input.setPlaceholderText("Hedef rol: Veri Analisti")
        self.role_input.setFixedWidth(220)
        bagla_btn = QPushButton("GitHub'a Bağla")
        bagla_btn.setObjectName("success")
        bagla_btn.clicked.connect(self._github_bagla)
        demo_btn = QPushButton("Yeni Mezun Demo Repo")
        demo_btn.clicked.connect(self._demo_repo_yukle)
        form_lo.addWidget(QLabel("Repo:"))
        form_lo.addWidget(self.repo_input, stretch=1)
        form_lo.addWidget(self.role_input)
        form_lo.addWidget(bagla_btn)
        form_lo.addWidget(demo_btn)
        lo.addWidget(form)

        metric_row = QHBoxLayout()
        metric_row.setSpacing(14)
        self.m_durum = metrik_karti("Hazır", "Bağlantı", "#2563EB")
        self.m_puan = metrik_karti("-", "Portfolyo Puanı", "#0F766E")
        self.m_etiket = metrik_karti("0", "Sinyal", "#D97706")
        for m in (self.m_durum, self.m_puan, self.m_etiket):
            metric_row.addWidget(m)
        lo.addLayout(metric_row)

        self.sonuc_krt = kart()
        self.sonuc_lo = QVBoxLayout(self.sonuc_krt)
        self.sonuc_lo.setContentsMargins(20, 16, 20, 16)
        self.sonuc_lo.setSpacing(8)
        self.sonuc_lo.addWidget(baslik("Bağlantı Özeti", renk="#0F3D3A"))
        self.bos_lbl = QLabel("Henüz repo bağlanmadı.")
        self.bos_lbl.setStyleSheet("color:#64748B;font-size:9pt;")
        self.sonuc_lo.addWidget(self.bos_lbl)
        lo.addWidget(self.sonuc_krt)

        lo.addStretch()
        scroll.setWidget(w)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def yukle(self):
        kayitlar = api_get(f"/api/github/{self.uid}")
        if isinstance(kayitlar, list) and kayitlar:
            son = kayitlar[0]
            self.repo_input.setText(son.get("repo_url", ""))
            self.role_input.setText(son.get("hedef_rol", "") or "Portfolyo Rolü")
            self._sonucu_yaz({
                "owner": son.get("owner"),
                "repo": son.get("repo"),
                "repo_url": son.get("repo_url"),
                "hedef_rol": son.get("hedef_rol"),
                "portfolyo_puani": son.get("portfolyo_puani", 82),
                "sinyaller": ["Kayıtlı GitHub portfolyosu bulundu.", "Portfolyo mentor ve İK akışına hazır.", "Repo bağlantısı rapor ekranında portfolyo sinyali üretir."],
                "onerilen_aksiyonlar": [
                    "README dosyasını güncel tut.",
                    "Projeyi yol haritasındaki portfolyo adımıyla eşleştir.",
                    "Mentor değerlendirmesinde repo bağlantısını paylaş.",
                ],
            })
            return
        if self.email == "mezun@skillbridge.com" and not self._demo_loaded:
            self._demo_repo_yukle()
            self._demo_loaded = True


    def _demo_repo_yukle(self):
        self.repo_input.setText("https://github.com/microsoft/Data-Science-For-Beginners")
        self.role_input.setText("Junior Veri Analisti")
        self._github_bagla()
    def _github_bagla(self):
        repo = self.repo_input.text().strip()
        if not repo:
            QMessageBox.warning(self, "Uyarı", "GitHub repo adresi boş olamaz.")
            return

        sonuc = api_post("/api/github/bagla", {
            "kullanici_id": self.uid,
            "repo_url": repo,
            "hedef_rol": self.role_input.text().strip() or "Portfolyo Rolü",
        })

        if "hata" in sonuc:
            QMessageBox.warning(self, "GitHub Bağlantısı", sonuc["hata"])
            return

        self._sonucu_yaz(sonuc)

    def _sonucu_yaz(self, sonuc: dict):
        self._set_val(self.m_durum, "Bağlandı")
        self._set_val(self.m_puan, f"%{sonuc.get('portfolyo_puani', 0)}")
        self._set_val(self.m_etiket, str(len(sonuc.get("sinyaller", []))))

        while self.sonuc_lo.count():
            item = self.sonuc_lo.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.sonuc_lo.addWidget(baslik("Bağlantı Özeti", renk="#0F3D3A"))
        self._satir("Repo", f"{sonuc.get('owner')}/{sonuc.get('repo')}")
        self._satir("Adres", sonuc.get("repo_url", "-"))
        self._satir("Hedef Rol", sonuc.get("hedef_rol", "-"))
        metrikler = sonuc.get("metrikler", {})
        if metrikler:
            self.sonuc_lo.addSpacing(8)
            self.sonuc_lo.addWidget(baslik("GitHub Metrikleri", renk="#0F3D3A"))
            if metrikler.get("canli"):
                self._satir("Dil", metrikler.get("dil", "-"))
                self._satir("Yıldız / Fork", f"{metrikler.get('yildiz', 0)} / {metrikler.get('fork', 0)}")
                self._satir("README", "Var" if metrikler.get("readme") else "Eksik")
            else:
                self._satir("Canlı Kontrol", metrikler.get("not", "GitHub API bilgisi alınamadı."))

        self.sonuc_lo.addSpacing(8)
        self.sonuc_lo.addWidget(baslik("Önerilen Aksiyonlar", renk="#0F3D3A"))
        for madde in sonuc.get("onerilen_aksiyonlar", []):
            lbl = QLabel(f"• {madde}")
            lbl.setWordWrap(True)
            lbl.setStyleSheet("color:#1F2937;font-size:10pt;")
            self.sonuc_lo.addWidget(lbl)

    def _satir(self, sol: str, sag: str):
        row = QWidget()
        row_lo = QHBoxLayout(row)
        row_lo.setContentsMargins(0, 0, 0, 0)
        left = QLabel(sol)
        left.setStyleSheet("color:#1F2937;font-size:9pt;font-weight:800;")
        right = QLabel(sag)
        right.setWordWrap(True)
        right.setStyleSheet("color:#0F766E;font-size:9pt;font-weight:700;")
        row_lo.addWidget(left)
        row_lo.addStretch()
        row_lo.addWidget(right)
        self.sonuc_lo.addWidget(row)

    @staticmethod
    def _set_val(krt: QFrame, deger: str):
        lbls = krt.findChildren(QLabel)
        if lbls:
            lbls[0].setText(deger)



