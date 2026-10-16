import os
import json
import binascii
import win32crypt
from PySide6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QVBoxLayout,
                               QPushButton, QMessageBox, QLabel, QFrame, QHBoxLayout)
from PySide6.QtCore import Qt


class TMSConfig:
    FILE_PATH = "Data/config_tms.json"

    @staticmethod
    def ma_hoa(text):
        if not text: return ""
        try:
            khuon = win32crypt.CryptProtectData(text.encode('utf-8'), 'TMS_BOT', None, None, None, 0)
            return binascii.hexlify(khuon).decode('utf-8')
        except:
            return ""

    @staticmethod
    def giai_ma(encrypted_hex):
        if not encrypted_hex: return ""
        try:
            khuon = binascii.unhexlify(encrypted_hex.encode('utf-8'))
            _, data = win32crypt.CryptUnprotectData(khuon, None, None, None, 0)
            return data.decode('utf-8')
        except:
            return ""

    @classmethod
    def load(cls):
        if os.path.exists(cls.FILE_PATH):
            try:
                with open(cls.FILE_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['pass_tms'] = cls.giai_ma(data.get('pass_tms', ''))
                    return data
            except:
                pass
        return {"cqt": "", "tu_ngay": "", "den_ngay": "", "user_tms": "", "pass_tms": ""}

    @classmethod
    def save(cls, data):
        os.makedirs("Data", exist_ok=True)
        data_to_save = data.copy()
        data_to_save['pass_tms'] = cls.ma_hoa(data_to_save['pass_tms'])
        with open(cls.FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)


class DialogCauHinhTMS(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cấu hình Kết nối TMS")
        self.resize(420, 420)
        self.config = TMSConfig.load()

        # Phủ CSS phong cách UI hiện đại
        self.setStyleSheet("""
            QDialog {
                background-color: #F3F4F6;
            }
            QLabel {
                color: #374151;
                font-size: 13px;
                font-weight: 500;
            }
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                background-color: #FFFFFF;
                color: #111827;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6;
                outline: none;
            }
            QFrame#Card {
                background-color: #FFFFFF; 
                border-radius: 8px; 
                border: 1px solid #E5E7EB;
            }
        """)
        self.thiet_lap_ui()

    def thiet_lap_ui(self):
        layout_chinh = QVBoxLayout(self)
        layout_chinh.setContentsMargins(24, 20, 24, 20)
        layout_chinh.setSpacing(16)

        # Tiêu đề Popup
        lbl_title = QLabel("CÀI ĐẶT TMS")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1F2937;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_chinh.addWidget(lbl_title)

        # ---------------------------------------------------------
        # KHỐI 1: CẤU HÌNH THỜI GIAN & CƠ QUAN THUẾ
        # ---------------------------------------------------------
        card_thong_so = QFrame()
        card_thong_so.setObjectName("Card")
        form_thong_so = QFormLayout(card_thong_so)
        form_thong_so.setContentsMargins(16, 16, 16, 16)
        form_thong_so.setSpacing(12)

        self.txt_cqt = QLineEdit(self.config.get("cqt", "50500"))
        self.txt_tu_ngay = QLineEdit(self.config.get("tu_ngay", ""))
        self.txt_tu_ngay.setPlaceholderText("Trống = Tự động nội suy từ XML")
        self.txt_den_ngay = QLineEdit(self.config.get("den_ngay", ""))
        self.txt_den_ngay.setPlaceholderText("Trống = Tự động lấy ngày hôm nay")

        form_thong_so.addRow("Mã Cơ quan thuế:", self.txt_cqt)
        form_thong_so.addRow("Từ ngày cố định:", self.txt_tu_ngay)
        form_thong_so.addRow("Đến ngày cố định:", self.txt_den_ngay)
        layout_chinh.addWidget(card_thong_so)

        # ---------------------------------------------------------
        # KHỐI 2: TÀI KHOẢN ĐĂNG NHẬP (BẢO MẬT)
        # ---------------------------------------------------------
        card_tai_khoan = QFrame()
        card_tai_khoan.setObjectName("Card")
        form_tai_khoan = QFormLayout(card_tai_khoan)
        form_tai_khoan.setContentsMargins(16, 16, 16, 16)
        form_tai_khoan.setSpacing(12)

        self.txt_user = QLineEdit(self.config.get("user_tms", ""))
        self.txt_user.setPlaceholderText("Tên đăng nhập hệ thống SAP")

        self.txt_pass = QLineEdit(self.config.get("pass_tms", ""))
        self.txt_pass.setPlaceholderText("Mật khẩu sẽ được mã hóa an toàn")
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)

        form_tai_khoan.addRow("Tài khoản TMS:", self.txt_user)
        form_tai_khoan.addRow("Mật khẩu TMS:", self.txt_pass)
        layout_chinh.addWidget(card_tai_khoan)

        layout_chinh.addStretch()

        # ---------------------------------------------------------
        # KHỐI 3: NÚT THAO TÁC
        # ---------------------------------------------------------
        khung_nut = QHBoxLayout()

        btn_huy = QPushButton("Hủy bỏ")
        btn_huy.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_huy.setStyleSheet("""
            QPushButton { background-color: #F3F4F6; color: #4B5563; font-weight: bold; border-radius: 6px; padding: 10px; border: 1px solid #D1D5DB; }
            QPushButton:hover { background-color: #E5E7EB; }
        """)
        btn_huy.clicked.connect(self.reject)

        btn_luu = QPushButton("Lưu Cấu Hình")
        btn_luu.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_luu.setStyleSheet("""
            QPushButton { background-color: #10B981; color: white; font-weight: bold; border-radius: 6px; padding: 10px; border: none; }
            QPushButton:hover { background-color: #059669; }
        """)
        btn_luu.clicked.connect(self.luu_lai)

        khung_nut.addWidget(btn_huy)
        khung_nut.addWidget(btn_luu)
        layout_chinh.addLayout(khung_nut)

    def luu_lai(self):
        TMSConfig.save({
            "cqt": self.txt_cqt.text().strip(),
            "tu_ngay": self.txt_tu_ngay.text().strip(),
            "den_ngay": self.txt_den_ngay.text().strip(),
            "user_tms": self.txt_user.text().strip(),
            "pass_tms": self.txt_pass.text().strip()
        })

        msg = QMessageBox(self)
        msg.setWindowTitle("Lưu thành công")
        msg.setText("Đã mã hóa và lưu an toàn cấu hình hệ thống.")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet(
            "QLabel { color: #1F2937; } QPushButton { padding: 6px 16px; background-color: #3B82F6; color: white; border-radius: 4px; }")
        msg.exec()

        self.accept()