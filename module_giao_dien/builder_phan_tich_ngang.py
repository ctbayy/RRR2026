from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView,
                               QLabel, QWidget, QVBoxLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from module_ho_tro.dinh_dang_so import dinh_dang_so_vn


class BuilderPhanTichNgang(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_chinh = QVBoxLayout(self)
        self.layout_chinh.setContentsMargins(0, 0, 0, 0)

        # Khởi tạo bảng chính
        self.bang_data = QTableWidget(0, 6)
        self.thiet_lap_bang()
        self.layout_chinh.addWidget(self.bang_data)

    def thiet_lap_bang(self):
        """Cấu hình form chuẩn của bảng chuỗi thời gian"""
        self.bang_data.setHorizontalHeaderLabels([
            "Tên Phép Kiểm Tra (Logic)", "Năm", "Chi tiết Số liệu (A/B)",
            "Chênh lệch", "Trạng thái", "Khuyến nghị / Thông điệp"
        ])

        header = self.bang_data.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.bang_data.setColumnWidth(0, 220)  # Cột tên kiểm tra (Gộp ô)
        self.bang_data.setColumnWidth(1, 70)  # Cột Năm
        self.bang_data.setColumnWidth(2, 250)  # Cột Chi tiết HTML
        self.bang_data.setColumnWidth(3, 130)  # Cột Chênh lệch
        self.bang_data.setColumnWidth(4, 120)  # Cột Trạng thái HTML
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Cột Thông điệp tự giãn

        self.bang_data.setWordWrap(True)
        self.bang_data.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.bang_data.setAlternatingRowColors(True)
        self.bang_data.setEditTriggers(QTableWidget.NoEditTriggers)
        self.bang_data.setStyleSheet("""
            QTableWidget { gridline-color: #cbd5e1; font-size: 13px; }
            QHeaderView::section { background-color: #f8fafc; font-weight: bold; border: 1px solid #cbd5e1; }
        """)

    def _tao_the_html(self, noi_dung, mau_chu, mau_nen, icon=""):
        """Nặn thẻ HTML (Badge) bo góc để cắm vào bảng"""
        return f"""
            <div style='
                background-color: {mau_nen}; 
                color: {mau_chu}; 
                padding: 4px 8px; 
                border-radius: 6px; 
                border: 1px solid {mau_chu};
                font-weight: bold;
                display: inline-block;
                margin: 2px 0px;
            '>
                {icon} {noi_dung}
            </div>
        """

    def _format_so(self, val):
        try:
            return dinh_dang_so_vn(round(float(val), 2), 2 if not round(float(val), 2).is_integer() else 0)
        except:
            return str(val)

    def nap_du_lieu_chuoi_thoi_gian(self, danh_sach_ket_qua):
        """Thuật toán gom nhóm (Groupby) và Trải rèm (RowSpan)"""
        self.bang_data.setRowCount(0)
        if not danh_sach_ket_qua: return

        # 1. Thuật toán Gom nhóm dữ liệu theo "Tên phép phân tích"
        dict_gom_nhom = {}
        for r in danh_sach_ket_qua:
            ten = r.get('ten_phan_tich', 'Không xác định')
            if ten not in dict_gom_nhom:
                dict_gom_nhom[ten] = []
            dict_gom_nhom[ten].append(r)

        # 2. Rải dữ liệu và Gộp ô
        row_idx = 0
        for ten_pt, cac_nam in dict_gom_nhom.items():
            start_row = row_idx
            so_luong_nam = len(cac_nam)

            for data in cac_nam:
                self.bang_data.insertRow(row_idx)

                # CỘT 0: Tên phép phân tích (Sẽ được gộp ô ở dưới)
                item_ten = QTableWidgetItem(ten_pt)
                item_ten.setFont(QFont("Segoe UI", 10, QFont.Bold))
                item_ten.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.bang_data.setItem(row_idx, 0, item_ten)

                # CỘT 1: Năm áp dụng (In đậm)
                nam = str(data.get('nam_ap_dung', 'N/A'))
                item_nam = QTableWidgetItem(nam)
                item_nam.setFont(QFont("Segoe UI", 10, QFont.Bold))
                item_nam.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.bang_data.setItem(row_idx, 1, item_nam)

                # CỘT 2: Chi tiết Vế A / Vế B (Hiển thị văn bản an toàn, phẳng)
                chuoi_chu = data.get("ve_a_goc", "")
                chuoi_so = data.get("cong_thuc_so", "")

                if data.get('is_ab'):
                    # Rule đối chiếu 2 vế thông thường (A - B)
                    str_a = f"[A] {chuoi_chu}: <b style='color:#0284c7'>{self._format_so(data.get('gia_tri_a', 0))}</b>"
                    str_b = f"<br>[B] {data.get('ve_b_goc', '')}: <b style='color:#d97706'>{self._format_so(data.get('gia_tri_b', 0))}</b>"
                    html_chi_tiet = f"<div style='line-height: 1.5;'>{str_a}{str_b}</div>"
                else:
                    # Rule biểu thức tự do (Hiển thị 1 dòng công thức, 1 dòng số liệu thật)
                    html_chi_tiet = f"<div style='line-height: 1.5;'>"
                    html_chi_tiet += f"<span style='color:#1e293b;'><b>Công thức:</b> {chuoi_chu}</span>"
                    if chuoi_so and chuoi_so != chuoi_chu:
                        html_chi_tiet += f"<br><span style='color:#0284c7;'><b>Số liệu:</b> {chuoi_so}</span>"
                    html_chi_tiet += f"</div>"

                lbl_chi_tiet = QLabel(html_chi_tiet)
                lbl_chi_tiet.setTextFormat(Qt.TextFormat.RichText)
                lbl_chi_tiet.setWordWrap(True)
                lbl_chi_tiet.setMargin(5)
                self.bang_data.setCellWidget(row_idx, 2, lbl_chi_tiet)

                # (KHÔNG CẦN ÉP CHIỀU CAO 80px NỮA, để QTableWidget tự động co giãn theo nội dung)

                # CỘT 3: Chênh lệch
                item_kq = QTableWidgetItem(self._format_so(data.get('ket_qua_so', 0)))
                item_kq.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                item_kq.setFont(QFont("Segoe UI", 10, QFont.Bold))
                self.bang_data.setItem(row_idx, 3, item_kq)

                # CỘT 4: Trạng thái (Cắm thẻ HTML Badge)
                is_rui_ro = data.get('is_rui_ro', False)
                if str(data.get('ket_qua_so')) == "Thiếu dữ liệu":
                    html_badge = self._tao_the_html("CHƯA ĐỦ DỮ LIỆU", "#64748b", "#f1f5f9", "⚠️")
                elif is_rui_ro:
                    html_badge = self._tao_the_html("CẢNH BÁO RỦI RO", "#b91c1c", "#fef2f2", "❌")
                else:
                    html_badge = self._tao_the_html("AN TOÀN", "#15803d", "#f0fdf4", "✅")

                lbl_trang_thai = QLabel(html_badge)
                lbl_trang_thai.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.bang_data.setCellWidget(row_idx, 4, lbl_trang_thai)

                # CỘT 5: Thông điệp
                self.bang_data.setItem(row_idx, 5, QTableWidgetItem(data.get('thong_diep', '')))

                row_idx += 1

            # 3. Kích hoạt hiệu ứng Gộp ô (Merge) cho Cột "Tên phép phân tích"
            if so_luong_nam > 1:
                self.bang_data.setSpan(start_row, 0, so_luong_nam, 1)

        self.bang_data.resizeRowsToContents()