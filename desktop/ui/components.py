from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


def kart(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setObjectName("card")
    return f


def baslik(metin: str, boyut: int = 11, renk: str = "#6366F1") -> QLabel:
    l = QLabel(metin)
    l.setStyleSheet(f"font-size:{boyut}pt;font-weight:700;color:{renk};")
    return l


def metrik_karti(deger: str, etiket: str, renk: str = "#6366F1") -> QFrame:
    f = kart()
    lo = QVBoxLayout(f)
    lo.setContentsMargins(16, 14, 16, 14)
    lo.setSpacing(4)

    v = QLabel(deger)
    v.setStyleSheet(f"font-size:22pt;font-weight:700;color:{renk};")
    l = QLabel(etiket)
    l.setStyleSheet("color:#64748B;font-size:9pt;")

    lo.addWidget(v)
    lo.addWidget(l)
    return f