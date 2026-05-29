API = "http://localhost:8000"
OTURUM = {}

STYLE = """
QMainWindow{background:#F4F6F8;color:#1F2937;font-family:'Segoe UI';font-size:10pt;}
QWidget{color:#1F2937;font-family:'Segoe UI';font-size:10pt;}
QLabel{color:#1F2937;background:transparent;}
QFrame#card QLabel{color:#1F2937;background:transparent;}
QFrame#card QWidget{background:transparent;}

QLineEdit{
    background:#FFFFFF;
    border:1px solid #CBD5E1;
    border-radius:6px;
    padding:8px 12px;
    color:#1F2937;
}
QLineEdit:focus{border-color:#2563EB;}

QPushButton{
    background:#2563EB;
    color:white;
    border:none;
    border-radius:6px;
    padding:9px 18px;
    font-weight:600;
}
QPushButton:hover{background:#1D4ED8;}
QPushButton:disabled{background:#CBD5E1;color:#64748B;}

QPushButton#ghost{
    background:transparent;
    border:1px solid #CBD5E1;
    color:#334155;
}
QPushButton#ghost:hover{
    background:#EAF1FB;
    border-color:#2563EB;
    color:#1D4ED8;
}

QPushButton#success{background:#047857;}
QPushButton#success:hover{background:#065F46;}
QPushButton#warn{background:#D97706;color:white;}

QFrame#card{
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:8px;
}
QFrame#card QLabel,QFrame#card QWidget{background:transparent;}

QFrame#sidebar{
    background:#111827;
    border-right:1px solid #1F2937;
}

QScrollArea{border:none;background:transparent;}

QProgressBar{
    background:#E5E7EB;
    border-radius:4px;
    border:none;
}
QProgressBar::chunk{
    background:#2563EB;
    border-radius:4px;
}

QComboBox{
    background:#FFFFFF;
    border:1px solid #CBD5E1;
    border-radius:6px;
    padding:6px 12px;
    color:#1F2937;
}
QFrame#card QLabel{
    color:#1F2937;
    background:transparent;
}

QFrame#card QWidget{
    background:transparent;
}

QScrollArea QWidget{
    color:#1F2937;
}

QDialog,
QMessageBox{
    background-color:#FFFFFF;
    color:#1F2937;
}

QDialog QLabel,
QMessageBox QLabel,
QMessageBox QLabel#qt_msgbox_label,
QMessageBox QLabel#qt_msgbox_informativelabel{
    color:#1F2937;
    background:transparent;
    font-size:10pt;
}

QMessageBox QPushButton,
QDialog QPushButton{
    background:#2563EB;
    color:#FFFFFF;
    border:none;
    border-radius:6px;
    padding:8px 16px;
    min-width:76px;
    font-weight:600;
}

QMessageBox QPushButton:hover,
QDialog QPushButton:hover{
    background:#1D4ED8;
}

QMessageBox QPushButton:disabled,
QDialog QPushButton:disabled{
    background:#CBD5E1;
    color:#64748B;
}

QComboBox QAbstractItemView,
QListView,
QTableView,
QMenu{
    background:#FFFFFF;
    color:#1F2937;
    border:1px solid #CBD5E1;
    selection-background-color:#DDF7F4;
    selection-color:#0F3D3A;
}

QMenu::item:selected,
QComboBox QAbstractItemView::item:selected{
    background:#DDF7F4;
    color:#0F3D3A;
}

QTextEdit,
QPlainTextEdit{
    background:#FFFFFF;
    color:#1F2937;
    border:1px solid #CBD5E1;
    border-radius:6px;
    selection-background-color:#DDF7F4;
    selection-color:#0F3D3A;
}

QToolTip{
    background:#111827;
    color:#F9FAFB;
    border:1px solid #334155;
    padding:6px;
}
"""
