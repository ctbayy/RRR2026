import requests
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QTextEdit, QPushButton, QHBoxLayout, QMessageBox
import qtawesome as qta


class DialogGopY(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gửi Góp ý - Báo lỗi")
        self.resize(450, 350)
        self.setStyleSheet("QDialog { background-color: #FFFFFF; }")

        layout = QVBoxLayout(self)

        # 1. HỘP CHỌN PHÂN LOẠI
        lbl_loai = QLabel("1. Vấn đề bạn gặp phải là gì?")
        lbl_loai.setStyleSheet("font-weight: bold; color: #1E3A8A; font-size: 13px;")
        layout.addWidget(lbl_loai)

        self.cb_phan_loai = QComboBox()
        self.cb_phan_loai.addItems([
            "Lỗi ứng dụng",
            "Góp ý Công thức phân tích",
            "Lỗi cấu trúc Biểu mẫu",
            "Đề xuất tính năng mới",
            "Khác..."
        ])
        self.cb_phan_loai.setStyleSheet("padding: 8px; border: 1px solid #D1D5DB; border-radius: 4px;")
        layout.addWidget(self.cb_phan_loai)

        layout.addSpacing(10)

        # 2. KHUNG NHẬP NỘI DUNG CHI TIẾT
        lbl_noi_dung = QLabel("2. Mô tả chi tiết:")
        lbl_noi_dung.setStyleSheet("font-weight: bold; color: #1E3A8A; font-size: 13px;")
        layout.addWidget(lbl_noi_dung)

        self.txt_noi_dung = QTextEdit()
        self.txt_noi_dung.setPlaceholderText("Vui lòng mô tả chi tiết lỗi hoặc ý tưởng của bạn...")
        self.txt_noi_dung.setStyleSheet(
            "padding: 10px; border: 1px solid #D1D5DB; border-radius: 4px; font-size: 13px;")
        layout.addWidget(self.txt_noi_dung)

        layout.addSpacing(10)

        # 3. HÀNG NÚT BẤM
        khung_btn = QHBoxLayout()
        btn_huy = QPushButton("Hủy")
        btn_huy.setStyleSheet("padding: 8px 20px;")
        btn_huy.clicked.connect(self.reject)

        self.btn_gui = QPushButton(" Gửi Góp ý")
        self.btn_gui.setIcon(qta.icon('fa5s.paper-plane', color='white'))
        self.btn_gui.setStyleSheet(
            "background-color: #2563EB; color: white; font-weight: bold; padding: 8px 20px; border-radius: 4px;")
        self.btn_gui.clicked.connect(self.gui_du_lieu_ngam)

        khung_btn.addStretch()
        khung_btn.addWidget(btn_huy)
        khung_btn.addWidget(self.btn_gui)

        layout.addLayout(khung_btn)

    def gui_du_lieu_ngam(self):
        loai = self.cb_phan_loai.currentText()
        noi_dung = self.txt_noi_dung.toPlainText().strip()

        if not noi_dung:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập nội dung chi tiết trước khi gửi!")
            self.txt_noi_dung.setFocus()
            return

        # ==============================================================
        # CẤU HÌNH API GOOGLE FORM
        # Nhớ đổi đuôi link thành /formResponse và lấy ID câu hỏi chính xác
        # ==============================================================
        url_post = "https://docs.google.com/forms/d/e/1FAIpQLSeg5WYwiHvtsj8jKiR1F52UB29mTucfGxWGtC2ip0J-COA4LA/formResponse"

        payload = {
            "entry.166203927": loai,  # Thay ID tương ứng với câu hỏi Phân loại
            "entry.1208526999": noi_dung  # Thay ID tương ứng với câu hỏi Nội dung
        }

        self.btn_gui.setEnabled(False)
        self.btn_gui.setText(" Đang gửi...")
        self.btn_gui.setIcon(qta.icon('fa5s.spinner', color='white', animation=qta.Spin(self.btn_gui)))

        try:
            response = requests.post(url_post, data=payload, timeout=5)
            if response.status_code == 200:
                QMessageBox.information(self, "Thành công",
                                        "Cảm ơn bạn! Dữ liệu đã được gửi trực tiếp đến nhóm phát triển.")
                self.accept()
            else:
                QMessageBox.critical(self, "Lỗi hệ thống", f"Không thể gửi. Mã lỗi: {response.status_code}")
                self.khoi_phuc_nut()
        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "Lỗi mạng", "Không có kết nối Internet hoặc mạng bị chặn. Vui lòng thử lại sau!")
            self.khoi_phuc_nut()

    def khoi_phuc_nut(self):
        self.btn_gui.setEnabled(True)
        self.btn_gui.setText(" Gửi Góp ý")
        self.btn_gui.setIcon(qta.icon('fa5s.paper-plane', color='white'))