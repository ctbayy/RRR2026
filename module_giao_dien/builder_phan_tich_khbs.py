from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
import re


class BuilderPhanTichKHBS(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_chinh = QVBoxLayout(self)
        self.layout_chinh.setContentsMargins(0, 0, 0, 0)
        self.layout_chinh.setSpacing(12)

    def nap_du_lieu(self, danh_sach_canh_bao):
        # 1. Xóa sạch rác cũ nếu có chạy lại nhiều lần
        while self.layout_chinh.count():
            item = self.layout_chinh.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 2. Xử lý trường hợp trống
        if not danh_sach_canh_bao:
            lbl_empty = QLabel("Chưa có dữ liệu rà soát KHBS hoặc dữ liệu hoàn toàn khớp đúng.")
            lbl_empty.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 14px;")
            self.layout_chinh.addWidget(lbl_empty)
            return

        # 3. Quét từng dòng thông báo và Render ra Card HTML
        for msg in danh_sach_canh_bao:
            lbl = QLabel()
            lbl.setWordWrap(True)
            lbl.setTextFormat(Qt.TextFormat.RichText)

            # Phân loại màu sắc và Icon theo mức độ nghiêm trọng
            if "LƯU Ý" in msg or "THÔNG TIN" in msg:
                bg_col, border_col, text_col = "#f8fafc", "#94a3b8", "#475569"
                icon = "📌" if "LƯU Ý" in msg else "ℹ️"
            elif "TUÂN THỦ TỐT" in msg:
                bg_col, border_col, text_col = "#f0fdf4", "#22c55e", "#166534"
                icon = "✅"
            else:
                bg_col, border_col, text_col = "#fef2f2", "#ef4444", "#991b1b"
                icon = "⚠️"

            # Tự động tô đậm số tiền (VD: 10.000.000)
            msg_html = re.sub(r'(\d{1,3}(?:\.\d{3})+)', r'<b>\1</b>', msg)

            # Tự động kích hoạt màu Đỏ cho các Keyword báo động
            msg_html = re.sub(r'(TĂNG|GIẢM)', r'<b style="color:#dc2626;">\1</b>', msg_html)
            msg_html = re.sub(r'(Lệch:\s*[\d\.\,]+)', r'<b style="color:#dc2626;">\1</b>', msg_html)

            # Tô màu Xanh lam cho các Mã chỉ tiêu [xx]
            msg_html = re.sub(r'(\[\w+\])', r'<b style="color:#0284c7;">\1</b>', msg_html)

            # Đóng gói vào khuôn HTML Fluent Design
            html = f"""
            <div style='
                background-color: {bg_col};
                border-left: 5px solid {border_col};
                padding: 14px 16px;
                border-radius: 6px;
                border-top: 1px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
                border-bottom: 1px solid #e2e8f0;
            '>
                <div style='font-size: 14px; color: {text_col}; line-height: 1.6;'>
                    <b>{icon}</b> {msg_html}
                </div>
            </div>
            """
            lbl.setText(html)
            self.layout_chinh.addWidget(lbl)