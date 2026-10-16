import sys
import subprocess
import hashlib
import requests
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QMessageBox, QFrame, QApplication,
                               QFileDialog, QTextEdit, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QListWidget, QListWidgetItem
from module_ho_tro.doc_cqt import lay_danh_sach_cqt
import os
import json
from cryptography.fernet import Fernet
from module_bao_mat.device_manager import DeviceManager
from module_bao_mat.license_manager import LicenseManager



class RegisterDialog(QDialog):
    def __init__(self, auth_url, parent=None):
        super().__init__(parent)
        self.auth_url = auth_url
        self.setWindowTitle("Đăng ký Tài khoản")
        # 1. MỞ RỘNG GIAO DIỆN (Từ 400x480 lên 550x650 cho thoáng đãng)
        self.setFixedSize(550, 650)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        # 2. FIX CSS: Tương phản nền trắng tinh, ô Checkbox to rõ ràng
        self.setStyleSheet("""
            QDialog { background-color: #f1f5f9; }
            QLabel { color: #1e293b; }
            QLineEdit {
                padding: 12px; font-size: 14px; border: 1px solid #cbd5e1;
                border-radius: 6px; background-color: #ffffff; color: #0f172a;
            }
            QLineEdit:focus { border: 2px solid #3b82f6; background-color: #ffffff; }
            
            QListWidget {
                border: 1px solid #cbd5e1; border-radius: 6px; 
                background-color: #ffffff; /* Nền trắng tinh để nổi bật checkbox */
                padding: 5px; font-size: 14px; color: #0f172a;
            }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #f8fafc; }
            QListWidget::item:hover { background-color: #e2e8f0; border-radius: 4px; }
            
            /* Phóng to ô Checkbox của Windows lên một chút cho dễ bấm */
            QListWidget::indicator { width: 18px; height: 18px; }
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        lbl_title = QLabel("TẠO TÀI KHOẢN MỚI")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0f172a;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        self.txt_usr = QLineEdit()
        self.txt_usr.setPlaceholderText("Tên đăng nhập (viết liền không dấu)")

        self.txt_pwd = QLineEdit()
        self.txt_pwd.setPlaceholderText("Mật khẩu")
        self.txt_pwd.setEchoMode(QLineEdit.EchoMode.Password)

        self.txt_pwd_confirm = QLineEdit()
        self.txt_pwd_confirm.setPlaceholderText("Nhập lại mật khẩu")
        self.txt_pwd_confirm.setEchoMode(QLineEdit.EchoMode.Password)

        # ---> BỔ SUNG THANH TÌM KIẾM CƠ QUAN THUẾ <---
        lbl_cqt = QLabel("Chọn các Cơ quan Thuế quản lý:")
        lbl_cqt.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")

        self.txt_search_cqt = QLineEdit()
        self.txt_search_cqt.setPlaceholderText("🔍 Gõ để tìm nhanh tên hoặc mã Cơ quan Thuế...")
        self.txt_search_cqt.setStyleSheet("""
            QLineEdit { background-color: #f8fafc; border: 1px solid #94a3b8; font-style: italic; }
            QLineEdit:focus { font-style: normal; border: 2px solid #3b82f6; background-color: #ffffff; }
        """)
        # Bắt sự kiện gõ phím đến đâu, lọc danh sách đến đó
        self.txt_search_cqt.textChanged.connect(self.loc_danh_sach_cqt)

        self.list_cqt = QListWidget()
        self.list_cqt.setSelectionMode(QListWidget.SelectionMode.NoSelection)

        # Đổ dữ liệu từ file Excel vào List
        ds_cqt = lay_danh_sach_cqt()
        for cqt in ds_cqt:
            item = QListWidgetItem(cqt)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.list_cqt.addItem(item)

        layout.addWidget(self.txt_usr)
        layout.addWidget(self.txt_pwd)
        layout.addWidget(self.txt_pwd_confirm)
        layout.addWidget(lbl_cqt)
        layout.addWidget(self.txt_search_cqt) # Nhét thanh tìm kiếm vào ngay trên List
        layout.addWidget(self.list_cqt)

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Hủy")
        btn_cancel.setStyleSheet("background-color: #64748b; color: white; padding: 12px; border-radius: 6px; font-weight: bold;")
        btn_cancel.clicked.connect(self.reject)

        self.btn_reg = QPushButton("Đăng ký ngay")
        self.btn_reg.setStyleSheet("background-color: #10b981; color: white; padding: 12px; border-radius: 6px; font-weight: bold;")
        self.btn_reg.clicked.connect(self.handle_register)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_reg)
        layout.addLayout(btn_layout)

    def loc_danh_sach_cqt(self, text):
        """Hàm lọc CQT siêu tốc: Gõ chữ nào, ẩn dòng không liên quan đi"""
        chuoi_tim_kiem = text.lower().strip()
        for i in range(self.list_cqt.count()):
            item = self.list_cqt.item(i)
            # Nếu chữ gõ vào có nằm trong Tên hoặc Mã CQT -> Hiện. Không thì Ẩn.
            if chuoi_tim_kiem in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def handle_register(self):
        usr = self.txt_usr.text().strip()
        pwd = self.txt_pwd.text().strip()
        pwd_confirm = self.txt_pwd_confirm.text().strip()

        if not usr or not pwd:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return
        if pwd != pwd_confirm:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu nhập lại không khớp.")
            return
        if " " in usr:
            QMessageBox.warning(self, "Lỗi", "Tên đăng nhập không được chứa khoảng trắng.")
            return

        # Quét và bóc tách mã CQT từ các ô được tick chọn
        danh_sach_ma_chon = []
        for i in range(self.list_cqt.count()):
            item = self.list_cqt.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                ma_cqt = item.text().split("-")[0].strip()
                if ma_cqt == "*":
                    danh_sach_ma_chon = ["*"]
                    break
                danh_sach_ma_chon.append(ma_cqt)

        # =================================================================
        # CHỐT CHẶN MỚI: ÉP BẮT BUỘC PHẢI CHỌN ÍT NHẤT 1 CƠ QUAN THUẾ
        # =================================================================
        if not danh_sach_ma_chon:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ít nhất một Cơ quan Thuế mà bạn quản lý!")
            return

        ma_cqt_gom_nhom = ", ".join(danh_sach_ma_chon)

        self.btn_reg.setText("Đang xử lý...")
        self.btn_reg.setEnabled(False)
        QApplication.processEvents()

        from module_giao_dien.dang_nhap import DeviceManager
        pass_hash = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
        hwid = DeviceManager.get_machine_id()

        payload = {
            "app_token": "210f4879c3097d73f2685e8ffa6caea61ff6e589fd8bf910527fa1281e97d32a",
            "action": "register",
            "username": usr,
            "password_hash": pass_hash,
            "hwid": hwid,
            "ma_cqt": ma_cqt_gom_nhom  # Đẩy cục data này lên Google Sheet
        }

        try:
            res = requests.post(self.auth_url, json=payload, timeout=45)
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    QMessageBox.information(self, "Thành công", data.get("msg"))
                    self.accept()
                else:
                    QMessageBox.warning(self, "Thất bại", data.get("msg"))
            else:
                QMessageBox.critical(self, "Lỗi", f"Máy chủ trả về mã: {res.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi mạng", f"Không thể kết nối máy chủ: {str(e)}")
        finally:
            self.btn_reg.setText("Đăng ký ngay")
            self.btn_reg.setEnabled(True)


class DialogKichHoatLicense(QDialog):
    """Hộp thoại kích hoạt bản quyền RSA 2048-bit (Level 2)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kích hoạt Giấy phép Bản quyền (RSA 2048-bit)")
        self.setFixedSize(540, 480)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.hwid = DeviceManager.get_machine_id()
        self.license_activated = False
        self.license_payload = {}
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #f8fafc; }
            QLabel { color: #1e293b; font-size: 13px; }
            QLineEdit, QTextEdit {
                border: 1px solid #cbd5e1; border-radius: 6px;
                background-color: #ffffff; color: #0f172a; padding: 8px;
                font-family: Consolas, monospace; font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #2563eb;
            }
            QPushButton {
                font-size: 13px; font-weight: bold; padding: 10px 16px;
                border-radius: 6px; border: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Tiêu đề
        lbl_title = QLabel("🔑 KÍCH HOẠT GIẤY PHÉP BẢN QUYỀN")
        lbl_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #1e3a8a;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_sub = QLabel("Bản quyền gắn liền phần cứng (RSA 2048-bit) - Hoạt động ngoại tuyến 100%")
        lbl_sub.setStyleSheet("font-size: 12px; color: #64748b;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_sub)

        # Khung HWID
        hwid_box = QFrame()
        hwid_box.setStyleSheet("background-color: #e2e8f0; border-radius: 8px; padding: 8px;")
        hwid_layout = QVBoxLayout(hwid_box)
        hwid_layout.setContentsMargins(10, 8, 10, 8)
        hwid_layout.setSpacing(6)

        lbl_hwid_note = QLabel("Mã phần cứng máy tính của bạn (HWID):")
        lbl_hwid_note.setStyleSheet("font-weight: bold; color: #334155; font-size: 12px;")
        hwid_layout.addWidget(lbl_hwid_note)

        hwid_row = QHBoxLayout()
        self.txt_hwid = QLineEdit(self.hwid)
        self.txt_hwid.setReadOnly(True)
        self.txt_hwid.setStyleSheet("background-color: #ffffff; font-weight: bold; color: #0f172a; font-size: 14px;")

        btn_copy_hwid = QPushButton("📋 Sao chép")
        btn_copy_hwid.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_copy_hwid.setStyleSheet("background-color: #3b82f6; color: white;")
        btn_copy_hwid.clicked.connect(self._copy_hwid)

        hwid_row.addWidget(self.txt_hwid)
        hwid_row.addWidget(btn_copy_hwid)
        hwid_layout.addLayout(hwid_row)

        lbl_guide = QLabel("👉 Gửi mã HWID này cho Quản trị viên để nhận mã kích hoạt bản quyền.")
        lbl_guide.setStyleSheet("font-size: 11px; color: #475569; font-style: italic;")
        hwid_layout.addWidget(lbl_guide)
        layout.addWidget(hwid_box)

        # Vùng nhập key hoặc chọn file
        lbl_key = QLabel("Nhập mã kích hoạt (License Token) hoặc chọn file (.lic):")
        lbl_key.setStyleSheet("font-weight: bold; color: #1e293b; margin-top: 5px;")
        layout.addWidget(lbl_key)

        self.txt_key = QTextEdit()
        self.txt_key.setPlaceholderText("Dán chuỗi khóa bản quyền tại đây hoặc bấm nút Chọn file .lic bên dưới...")
        layout.addWidget(self.txt_key)

        file_row = QHBoxLayout()
        btn_open_file = QPushButton("📂 Chọn file License (.lic)...")
        btn_open_file.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open_file.setStyleSheet("background-color: #6366f1; color: white;")
        btn_open_file.clicked.connect(self._choose_file)
        file_row.addWidget(btn_open_file)
        file_row.addStretch()
        layout.addLayout(file_row)

        # Nút xác nhận
        btn_box = QHBoxLayout()
        btn_cancel = QPushButton("Hủy bỏ")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("background-color: #94a3b8; color: white;")
        btn_cancel.clicked.connect(self.reject)

        self.btn_activate = QPushButton("✅ Xác nhận Kích hoạt")
        self.btn_activate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_activate.setStyleSheet("background-color: #10b981; color: white; padding: 12px 24px;")
        self.btn_activate.clicked.connect(self._activate)

        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(self.btn_activate)
        layout.addLayout(btn_box)

    def _copy_hwid(self):
        QApplication.clipboard().setText(self.hwid)
        QMessageBox.information(self, "Đã sao chép", f"Đã sao chép mã HWID vào bộ nhớ tạm:\n\n{self.hwid}\n\nHãy gửi mã này cho Quản trị viên.")

    def _choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file Giấy phép Bản quyền", "", "License Files (*.lic *.key);;Tất cả file (*.*)"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                self.txt_key.setPlainText(content)
            except Exception as e:
                QMessageBox.warning(self, "Lỗi đọc file", f"Không thể đọc file: {e}")

    def _activate(self):
        token = self.txt_key.toPlainText().strip()
        if not token:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập mã kích hoạt hoặc chọn file .lic.")
            return

        hop_le, thong_diep, payload = LicenseManager.verify_license_token(token)
        if not hop_le:
            QMessageBox.critical(self, "Kích hoạt thất bại", thong_diep)
            return

        if not LicenseManager.save_license(token):
            QMessageBox.critical(self, "Lỗi lưu file", "Không thể lưu file bản quyền vào thư mục Data/license.lic.")
            return

        self.license_activated = True
        self.license_payload = payload
        user_name = payload.get("user", "Người dùng")
        role = payload.get("role", "user")
        exp = payload.get("expires_at", "Vô thời hạn")

        QMessageBox.information(
            self,
            "Kích hoạt thành công",
            f"🎉 CHÚC MỪNG BẠN!\n\n"
            f"Giấy phép bản quyền đã được kích hoạt thành công!\n"
            f"• Người sở hữu: {user_name}\n"
            f"• Quyền hạn: {role}\n"
            f"• Thời hạn: {exp}\n"
            f"• Mã máy: {payload.get('hwid')}"
        )
        self.accept()


class LoginDialog(QDialog):
    AUTH_URL = "https://script.google.com/macros/s/AKfycbyUlzoNMXzoofWHt2JlOOsLwWsi5-QCEuGt_5PmbfIqIA04i0WYo9lo7dyZezCLjop_tw/exec"
    MASTER_KEY = b'v_M_E_tqN-K0T1X-yG6PjCq4g-p3L2hX8sK_A5rZ1M0='

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Xác thực Bản quyền & Đăng nhập")
        self.setFixedSize(540, 480)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        self.is_authenticated = False
        self.username = ""
        self.role = ""
        self.allowed_cqt = []
        self.hwid = DeviceManager.get_machine_id()
        self.license_info = None

        self.setStyleSheet("""
            QDialog { background-color: #f8fafc; }
            QLabel { color: #1e293b; }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(12)

        # Tiêu đề cố định
        lbl_title = QLabel("HỆ THỐNG PHÂN TÍCH HỒ SƠ KHAI THUẾ")
        lbl_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #1e3a8a;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(lbl_title)

        # Khu vực nội dung động (Card bản quyền hoặc Form đăng nhập)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        self.main_layout.addWidget(self.content_widget)

        self._render_view(force_login_form=False)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _render_view(self, force_login_form=False):
        """Dựng giao diện động: Nếu máy đã có bản quyền hợp lệ -> Hiện thẻ sẵn sàng. Nếu chưa -> Hiện form đăng nhập."""
        self._clear_layout(self.content_layout)

        if not force_login_form:
            is_valid, msg, payload = LicenseManager.load_active_license()
            if is_valid:
                self.license_info = payload
                self._build_active_license_ui(payload)
                return

        self._build_login_form_ui()

    def _build_active_license_ui(self, payload):
        """Giao diện khi máy ĐÃ CÓ BẢN QUYỀN HỢP LỆ (Offline hoặc Cloud): 1-Click vào làm việc ngay"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #f0fdf4;
                border: 1.5px solid #10b981;
                border-radius: 10px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(8)

        lbl_badge = QLabel("🛡️ <b>BẢN QUYỀN ĐANG HOẠT ĐỘNG (SẴN SÀNG)</b>")
        lbl_badge.setStyleSheet("color: #047857; font-size: 14px; border: none; background: transparent;")
        card_layout.addWidget(lbl_badge)

        user = payload.get("username", "Người dùng")
        role = str(payload.get("role", "admin")).upper()
        exp = payload.get("expires_at", "Vĩnh viễn")
        src = payload.get("source_label", "Bản quyền hợp lệ")
        cqt = payload.get("allowed_cqt", "*")
        cqt_display = "Tất cả CQT (*)" if (cqt == "*" or not cqt) else (cqt if isinstance(cqt, str) else ", ".join(cqt))

        info_html = f"""
        <div style='font-size: 13px; color: #1e293b; line-height: 1.6;'>
            • Chủ sở hữu: <b>{user}</b><br>
            • Nguồn kích hoạt: <span style='color: #0284c7;'><b>{src}</b></span><br>
            • Quyền hạn: <b>{role}</b> | Phạm vi: <b>{cqt_display}</b><br>
            • Hạn dùng: <span style='color: #15803d;'><b>{exp}</b></span><br>
            • Thiết bị: <span style='font-family: Consolas;'>{self.hwid}</span> <i>(Đã khóa cứng máy này)</i>
        </div>
        """
        lbl_info = QLabel(info_html)
        lbl_info.setStyleSheet("border: none; background: transparent;")
        card_layout.addWidget(lbl_info)
        self.content_layout.addWidget(card)

        # Nút lớn Vào làm việc ngay
        btn_enter = QPushButton("🚀 VÀO LÀM VIỆC NGAY")
        btn_enter.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_enter.setStyleSheet("""
            QPushButton {
                background-color: #10b981; color: white; font-weight: bold;
                font-size: 14px; padding: 13px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        btn_enter.clicked.connect(lambda: self.handle_enter_active_license(payload))
        self.content_layout.addWidget(btn_enter)

        # Cụm nút phụ: Đổi tài khoản / Nạp license khác / Copy HWID
        sub_row = QHBoxLayout()
        sub_row.setSpacing(8)

        btn_switch = QPushButton("🔄 Đổi tài khoản Cloud")
        btn_switch.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_switch.setStyleSheet(self._sub_btn_style())
        btn_switch.clicked.connect(lambda: self._render_view(force_login_form=True))

        btn_lic = QPushButton("🔑 Đổi file License (.lic)")
        btn_lic.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_lic.setStyleSheet(self._sub_btn_style())
        btn_lic.clicked.connect(self.open_license_dialog)

        btn_copy_hwid = QPushButton("📋 Sao chép HWID")
        btn_copy_hwid.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_copy_hwid.setStyleSheet(self._sub_btn_style())
        btn_copy_hwid.clicked.connect(self._copy_hwid)

        sub_row.addWidget(btn_switch)
        sub_row.addWidget(btn_lic)
        sub_row.addWidget(btn_copy_hwid)
        self.content_layout.addLayout(sub_row)

    def _build_login_form_ui(self):
        """Giao diện khi máy CHƯA KÍCH HOẠT: Nhập Account để tự động cấp License hoặc nạp file .lic"""
        lbl_sub = QLabel("Đăng nhập tài khoản Cloud để tự động cấp bản quyền cho thiết bị này:")
        lbl_sub.setStyleSheet("font-size: 12px; color: #64748b; font-style: italic;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(lbl_sub)

        # Form nhập tài khoản & mật khẩu
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(0, 4, 0, 4)
        form_layout.setSpacing(8)

        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Tên đăng nhập...")
        self.txt_username.setStyleSheet(self._input_style())

        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Mật khẩu...")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setStyleSheet(self._input_style())

        self.txt_username.returnPressed.connect(self.txt_password.setFocus)
        self.txt_password.returnPressed.connect(self.handle_login)

        form_layout.addWidget(self.txt_username)
        form_layout.addWidget(self.txt_password)
        self.content_layout.addWidget(form_frame)

        # Nút Đăng nhập & Kích hoạt Tự động
        self.btn_login = QPushButton("🔐 Đăng nhập & Kích hoạt Tự động")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setStyleSheet(self._btn_style("#2563eb", "#1d4ed8"))
        self.btn_login.clicked.connect(self.handle_login)
        self.content_layout.addWidget(self.btn_login)

        # Cụm thao tác tài khoản
        acc_row = QHBoxLayout()
        acc_row.setSpacing(8)

        btn_reg = QPushButton("Đăng ký tài khoản")
        btn_reg.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reg.setStyleSheet(self._btn_style("#8e44ad", "#9b59b6", font_size="12px", padding="8px 12px"))
        btn_reg.clicked.connect(self.open_register_form)

        btn_chg_pwd = QPushButton("Đổi mật khẩu")
        btn_chg_pwd.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_chg_pwd.setStyleSheet(self._btn_style("#e67e22", "#d35400", font_size="12px", padding="8px 12px"))
        btn_chg_pwd.clicked.connect(self.open_change_password_form)

        acc_row.addWidget(btn_reg)
        acc_row.addWidget(btn_chg_pwd)
        self.content_layout.addLayout(acc_row)

        # Phân cách
        lbl_divider = QLabel("── Máy tính ở mạng nội bộ bị chặn Internet? ──")
        lbl_divider.setStyleSheet("color: #94a3b8; font-size: 11px; margin-top: 6px;")
        lbl_divider.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(lbl_divider)

        # Nút nạp file license offline
        btn_open_lic = QPushButton("📂 Kích hoạt ngoại tuyến bằng File License (.lic)...")
        btn_open_lic.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open_lic.setStyleSheet("""
            QPushButton {
                background-color: #ffffff; color: #4338ca; font-weight: bold;
                font-size: 12px; padding: 10px; border-radius: 6px; border: 1.5px dashed #6366f1;
            }
            QPushButton:hover { background-color: #eef2ff; color: #3730a3; }
        """)
        btn_open_lic.clicked.connect(self.open_license_dialog)
        self.content_layout.addWidget(btn_open_lic)

        # Nếu trước đó máy đã có bản quyền mà user bấm 'Đổi tài khoản', cho phép quay lại
        is_active, _, _ = LicenseManager.load_active_license()
        if is_active:
            btn_back = QPushButton("⬅️ Quay lại Bản quyền đang dùng")
            btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_back.setStyleSheet("color: #059669; font-size: 12px; border: none; background: transparent; text-decoration: underline;")
            btn_back.clicked.connect(lambda: self._render_view(force_login_form=False))
            self.content_layout.addWidget(btn_back)

    def _copy_hwid(self):
        QApplication.clipboard().setText(self.hwid)
        QMessageBox.information(self, "Đã sao chép", f"Đã sao chép mã HWID máy tính:\n\n{self.hwid}")

    def handle_enter_active_license(self, payload):
        """Xác nhận đăng nhập bằng Bản quyền đang hoạt động"""
        self.is_authenticated = True
        self.username = payload.get("username", "License_User")
        self.role = payload.get("role", "admin")
        cqt_str = payload.get("allowed_cqt", "*")
        if isinstance(cqt_str, list):
            self.allowed_cqt = cqt_str
        elif cqt_str and cqt_str.strip() != "*":
            self.allowed_cqt = [c.strip() for c in cqt_str.split(",") if c.strip()]
        else:
            self.allowed_cqt = ["*"]
        self.accept()

    def open_license_dialog(self):
        dlg = DialogKichHoatLicense(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            is_valid, msg, payload = LicenseManager.load_active_license()
            if is_valid:
                self.handle_enter_active_license(payload)
            else:
                self._render_view()

    def _input_style(self):
        return """
            QLineEdit {
                padding: 10px; font-size: 14px; border: 1px solid #cbd5e1;
                border-radius: 6px; background-color: #ffffff; color: #0f172a;
            }
            QLineEdit:focus {
                border: 2px solid #2563eb; background-color: #ffffff;
            }
        """

    def _btn_style(self, bg_color, hover_color, font_size="13px", padding="10px 16px"):
        return f"""
            QPushButton {{
                background-color: {bg_color}; color: white; font-weight: bold;
                font-size: {font_size}; padding: {padding}; border-radius: 6px; border: none;
            }}
            QPushButton:hover {{ background-color: {hover_color}; }}
        """

    def _sub_btn_style(self):
        return """
            QPushButton {
                background-color: #ffffff; color: #475569; font-size: 12px;
                padding: 8px 10px; border-radius: 6px; border: 1px solid #cbd5e1;
            }
            QPushButton:hover { background-color: #f1f5f9; color: #0f172a; }
        """

    def open_register_form(self):
        reg_dialog = RegisterDialog(self.AUTH_URL, self)
        reg_dialog.exec()

    def handle_login(self):
        usr = self.txt_username.text().strip()
        pwd = self.txt_password.text().strip()

        if not usr or not pwd:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Vui lòng nhập đầy đủ Tên đăng nhập và Mật khẩu.")
            return

        self.btn_login.setText("Đang kết nối xác thực...")
        self.btn_login.setEnabled(False)
        QApplication.processEvents()

        success, role, allowed_cqt_str, msg = self._authenticate_cloud(usr, pwd)

        self.btn_login.setText("🔐 Đăng nhập & Kích hoạt Tự động")
        self.btn_login.setEnabled(True)

        if success:
            QMessageBox.information(
                self,
                "Kích hoạt thành công",
                f"🎉 ĐĂNG NHẬP & KÍCH HOẠT THÀNH CÔNG!\n\n"
                f"• Tài khoản: {usr}\n"
                f"• Thiết bị: {DeviceManager.get_machine_id()}\n\n"
                f"Bản quyền đã được lưu an toàn trên máy tính này. "
                f"Từ nay bạn có thể mở phần mềm sử dụng bình thường ngay cả khi không có kết nối mạng."
            )
            self.is_authenticated = True
            self.username = usr
            self.role = role or "admin"
            if allowed_cqt_str and allowed_cqt_str != "*":
                self.allowed_cqt = [c.strip() for c in str(allowed_cqt_str).split(',') if c.strip()]
            else:
                self.allowed_cqt = ["*"]
            self.accept()
        else:
            QMessageBox.critical(self, "Xác thực thất bại", msg)
            self.txt_password.clear()
            self.txt_password.setFocus()

    def _authenticate_cloud(self, username, password):
        pass_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        hwid = DeviceManager.get_machine_id()

        payload = {
            "app_token": "210f4879c3097d73f2685e8ffa6caea61ff6e589fd8bf910527fa1281e97d32a",
            "action": "login",
            "username": username,
            "password_hash": pass_hash,
            "hwid": hwid
        }

        try:
            response = requests.post(self.AUTH_URL, json=payload, timeout=45)

            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError:
                    return self._authenticate_offline(username, pass_hash)

                if data.get("success"):
                    # Lưu phiên bản quyền Cloud xuống file ẩn mã hóa bằng Khóa phần cứng thiết bị (Level 1)
                    session_data = {
                        "username": username,
                        "password_hash": pass_hash,
                        "role": data.get("role", "admin"),
                        "allowed_cqt": data.get("allowed_cqt", "*"),
                        "expires_at": data.get("expires_at", "never"),
                        "hwid": hwid,
                        "login_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    LicenseManager.save_cloud_session(session_data)
                    return True, data.get("role"), data.get("allowed_cqt", ""), data.get("msg")
                else:
                    return False, None, None, data.get("msg")
            else:
                return self._authenticate_offline(username, pass_hash)

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            return self._authenticate_offline(username, pass_hash)
        except Exception:
            return self._authenticate_offline(username, pass_hash)

    def _authenticate_offline(self, input_usr, input_pass_hash):
        file_session = LicenseManager.SESSION_FILE
        if not os.path.exists(file_session):
            return False, None, None, (
                "Không thể kết nối máy chủ Google Drive và thiết bị này chưa từng được kích hoạt trước đây.\n\n"
                "Nếu máy tính của bạn ở trong mạng nội bộ bị chặn internet, vui lòng dùng tùy chọn "
                "'Kích hoạt ngoại tuyến bằng File License (.lic)' bên dưới để nhận mã từ Quản trị viên."
            )

        try:
            with open(file_session, "rb") as f:
                raw_bytes = f.read()

            decrypted_data = None
            try:
                device_key = DeviceManager.get_device_encryption_key()
                fernet_device = Fernet(device_key)
                decrypted_data = fernet_device.decrypt(raw_bytes).decode('utf-8')
            except Exception:
                try:
                    fernet_master = Fernet(self.MASTER_KEY)
                    decrypted_data = fernet_master.decrypt(raw_bytes).decode('utf-8')
                    LicenseManager.save_cloud_session(json.loads(decrypted_data))
                except Exception:
                    pass

            if not decrypted_data:
                return False, None, None, "❌ Phiên bản quyền ngoại tuyến không hợp lệ hoặc đã bị sao chép từ thiết bị khác!"

            token_data = json.loads(decrypted_data)

            if token_data.get("username") == input_usr and token_data.get("password_hash") == input_pass_hash:
                return True, token_data.get("role"), token_data.get(
                    "allowed_cqt"), "Đang sử dụng phiên bản quyền ngoại tuyến an toàn!"
            else:
                return False, None, None, "Sai tài khoản hoặc mật khẩu (Chế độ Ngoại tuyến)."
        except Exception:
            return False, None, None, "File dữ liệu bản quyền bị lỗi hoặc đã bị can thiệp."

    def open_change_password_form(self):
        dialog = ChangePasswordDialog(self.AUTH_URL, self)
        dialog.exec()


class ChangePasswordDialog(QDialog):
    def __init__(self, auth_url, parent=None):
        super().__init__(parent)
        self.auth_url = auth_url
        self.setWindowTitle("Đổi Mật Khẩu")
        self.setFixedSize(400, 350)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet("""
            QDialog { background-color: #f1f5f9; }
            QLabel { color: #1e293b; }
            QLineEdit {
                padding: 12px; font-size: 14px; border: 1px solid #cbd5e1;
                border-radius: 6px; background-color: #ffffff; color: #0f172a;
            }
            QLineEdit:focus { border: 2px solid #3b82f6; }
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        lbl_title = QLabel("CẬP NHẬT MẬT KHẨU")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f172a;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        self.txt_usr = QLineEdit()
        self.txt_usr.setPlaceholderText("Tên đăng nhập")

        self.txt_old_pwd = QLineEdit()
        self.txt_old_pwd.setPlaceholderText("Mật khẩu cũ")
        self.txt_old_pwd.setEchoMode(QLineEdit.EchoMode.Password)

        self.txt_new_pwd = QLineEdit()
        self.txt_new_pwd.setPlaceholderText("Mật khẩu mới")
        self.txt_new_pwd.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(self.txt_usr)
        layout.addWidget(self.txt_old_pwd)
        layout.addWidget(self.txt_new_pwd)

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Hủy")
        btn_cancel.setStyleSheet(
            "background-color: #64748b; color: white; padding: 10px; border-radius: 4px; font-weight: bold;")
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Cập nhật")
        self.btn_save.setStyleSheet(
            "background-color: #e67e22; color: white; padding: 10px; border-radius: 4px; font-weight: bold;")
        self.btn_save.clicked.connect(self.handle_change_password)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def handle_change_password(self):
        usr = self.txt_usr.text().strip()
        old_pwd = self.txt_old_pwd.text().strip()
        new_pwd = self.txt_new_pwd.text().strip()

        if not usr or not old_pwd or not new_pwd:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return

        self.btn_save.setText("Đang xử lý...")
        self.btn_save.setEnabled(False)
        QApplication.processEvents()

        old_hash = hashlib.sha256(old_pwd.encode('utf-8')).hexdigest()
        new_hash = hashlib.sha256(new_pwd.encode('utf-8')).hexdigest()

        payload = {
            "app_token": "210f4879c3097d73f2685e8ffa6caea61ff6e589fd8bf910527fa1281e97d32a",
            "action": "change_password",  # Bắn cờ action mới lên server
            "username": usr,
            "old_password_hash": old_hash,
            "new_password_hash": new_hash,
            "hwid": DeviceManager.get_machine_id()
        }

        try:
            res = requests.post(self.auth_url, json=payload, timeout=45)
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    QMessageBox.information(self, "Thành công", data.get("msg", "Đổi mật khẩu thành công!"))
                    self.accept()
                else:
                    QMessageBox.warning(self, "Thất bại", data.get("msg", "Sai thông tin đăng nhập."))
            else:
                QMessageBox.critical(self, "Lỗi", "Máy chủ phản hồi lỗi.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi mạng", f"Không thể kết nối máy chủ: {e}")
        finally:
            self.btn_save.setText("Cập nhật")
            self.btn_save.setEnabled(True)