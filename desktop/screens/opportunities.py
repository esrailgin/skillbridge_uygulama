from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QFrame, QLabel, QMessageBox, QPushButton, QHBoxLayout, QProgressBar, QScrollArea, QVBoxLayout, QWidget

from desktop.api import api_get, api_post
from desktop.ui.components import baslik, kart, metrik_karti

class FirsatlarSayfasi(QWidget):
    def __init__(self, kullanici: dict):
        super().__init__(); self.kullanici=kullanici; self.uid=kullanici.get("kullanici_id", ""); self.rol=kullanici.get("rol", ""); self._aday_id=self.uid; self._build()
    def _build(self):
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame)
        w=QWidget(); lo=QVBoxLayout(w); lo.setContentsMargins(28,24,28,24); lo.setSpacing(16)
        hero=kart(); hero.setStyleSheet("QFrame#card{background:#F8FBFA;border:1px solid #D7E5E1;border-left:4px solid #0E6B5C;border-radius:8px;}")
        hl=QVBoxLayout(hero); hl.setContentsMargins(20,16,20,16); self.hero_baslik=QLabel("Fırsat ve Şirket Haritası"); self.hero_baslik.setStyleSheet("font-size:15pt;font-weight:900;color:#0F3D3A;")
        self.hero_metin=QLabel(""); self.hero_metin.setWordWrap(True); self.hero_metin.setStyleSheet("color:#475569;font-size:10pt;"); hl.addWidget(self.hero_baslik); hl.addWidget(self.hero_metin); lo.addWidget(hero)
        mr=QHBoxLayout(); mr.setSpacing(14); self.m_firsat=metrik_karti("3","Aktif Fırsat","#38546E"); self.m_onay=metrik_karti("0","Mentor Onaylı","#0E6B5C"); self.m_gorusme=metrik_karti("1","Görüşme Adayı","#B7791F")
        for m in (self.m_firsat,self.m_onay,self.m_gorusme): mr.addWidget(m)
        lo.addLayout(mr)
        map_k=kart(); map_k.setStyleSheet("QFrame#card{background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;}"); ml=QVBoxLayout(map_k); ml.setContentsMargins(20,16,20,16); ml.addWidget(baslik("Harita Önizlemesi", renk="#0F3D3A"))
        note=QLabel("Şirket konumları Google Maps üzerinde açılır. Demo sırasında her şirket kartındaki Haritada Aç butonu kullanılabilir."); note.setWordWrap(True); note.setStyleSheet("color:#64748B;font-size:9pt;"); ml.addWidget(note); lo.addWidget(map_k)
        self.akıs_lo=QVBoxLayout(); self.akıs_lo.setSpacing(10); lo.addWidget(baslik("Şirket Eşleşmeleri", renk="#0F3D3A")); lo.addLayout(self.akıs_lo); lo.addStretch(); scroll.setWidget(w); outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.addWidget(scroll)
    def yukle(self):
        etkilesimler=api_get(self._etkilesim_path()); onayli=0
        if isinstance(etkilesimler, list):
            onayli=sum(1 for e in etkilesimler if e.get("durum") in ("approved", "shortlisted"))
            if self.rol=="hr_manager":
                secilen=next((e for e in etkilesimler if e.get("kullanici_id")), None)
                if secilen: self._aday_id=secilen.get("kullanici_id")
        self._set_val(self.m_onay, str(onayli)); self.hero_metin.setText(self._hero_metni(onayli))
        while self.akıs_lo.count():
            item=self.akıs_lo.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        firsatlar = api_get("/api/firsatlar")
        if not isinstance(firsatlar, list):
            firsatlar = []
        self._set_val(self.m_firsat, str(len(firsatlar)))
        for f in firsatlar:
            self.akıs_lo.addWidget(self._firsat_karti(f, onayli, self.rol, self._aday_id))
    def _hero_metni(self,onayli:int)->str:
        if self.rol=="hr_manager": return "İK ekipleri mentor onaylı adayları şirket fırsatlarıyla eşleştirir, kısa liste ve görüşme akışını buradan izler."
        if onayli: return "Mentor onayın hazır. Profiline uygun şirket fırsatları ve görüşme hazırlığı burada takip edilir."
        return "Profilini güçlendirdikçe ve mentor değerlendirmesi aldıkça uygun şirket fırsatları daha görünür hale gelir."
    def _etkilesim_path(self):
        if self.rol=="mentor": return "/api/etkilesimler/mentor"
        if self.rol=="hr_manager": return "/api/etkilesimler/ik"
        return f"/api/etkilesimler/kullanici/{self.uid}"
    def _firsat_karti(self, firsat:dict,onayli:int, rol:str, uid:str)->QFrame:
        renk="#0E6B5C" if onayli else "#B7791F"; k=kart(); k.setStyleSheet(f"QFrame#card{{background:#FFFFFF;border:1px solid #E5E7EB;border-left:4px solid {renk};border-radius:8px;}}")
        lo=QHBoxLayout(k); lo.setContentsMargins(18,14,18,14); lo.setSpacing(14); sol=QVBoxLayout(); bas=QLabel(f"{firsat['rol']} · {firsat['sirket']}"); bas.setStyleSheet("color:#1F2937;font-size:11pt;font-weight:900;")
        meta=QLabel(f"{firsat['sehir']} · {firsat['durum']}"); meta.setStyleSheet(f"color:{renk};font-size:9pt;font-weight:800;"); ack=QLabel(firsat['aciklama']); ack.setWordWrap(True); ack.setStyleSheet("color:#64748B;font-size:9pt;")
        sol.addWidget(bas); sol.addWidget(meta); sol.addWidget(ack); lo.addLayout(sol,1)
        side=QVBoxLayout(); uyum=QLabel(f"%{firsat['uyum']}\nuyum"); uyum.setAlignment(Qt.AlignmentFlag.AlignCenter); uyum.setStyleSheet(f"color:{renk};background:#F8FAFC;border:1px solid #E5E7EB;border-radius:8px;padding:8px;font-weight:900;")
        btn=QPushButton("Haritada Aç"); btn.clicked.connect(lambda _, q=firsat['konum']: QDesktopServices.openUrl(QUrl("https://www.google.com/maps/search/" + q.replace(' ', '+'))))
        action=QPushButton("Eşleştir" if rol=="hr_manager" else ("Sadece Görüntüle" if rol=="mentor" else "Başvur"))
        action.setObjectName("success")
        action.setEnabled(rol != "mentor")
        action.clicked.connect(lambda _, f=firsat, target_uid=uid: self._firsat_aksiyon(f, target_uid))
        side.addWidget(uyum); side.addWidget(btn); side.addWidget(action); lo.addLayout(side); return k
    def _firsat_aksiyon(self, firsat: dict, target_uid: str):
        path = "/api/firsatlar/eslestir" if self.rol == "hr_manager" else "/api/firsatlar/basvur"
        sonuc = api_post(path, {
            "kullanici_id": target_uid,
            "sirket": firsat.get("sirket", ""),
            "rol": firsat.get("rol", ""),
            "not_metni": "Demo akışından oluşturuldu.",
        })
        if "hata" in sonuc:
            QMessageBox.warning(self, "Fırsat", sonuc["hata"])
        else:
            QMessageBox.information(self, "Fırsat", sonuc.get("mesaj", "İşlem kaydedildi."))
            self.yukle()
    @staticmethod
    def _set_val(krt:QFrame,deger:str):
        lbls=krt.findChildren(QLabel)
        if lbls: lbls[0].setText(deger)






