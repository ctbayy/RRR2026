import pandas as pd
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QHBoxLayout, QPushButton, QLineEdit,
                               QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from module_ho_tro.dinh_dang_so import dinh_dang_so_vn


class WidgetBaoCaoDoanhSo(QWidget):
    def __init__(self, is_mua_vao=False, parent=None):
        super().__init__(parent)
        self.is_mua_vao = is_mua_vao
        self.thiet_lap_giao_dien()

    def thiet_lap_giao_dien(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 1. Tiêu đề
        if self.is_mua_vao:
            tieu_de = "Chênh lệch giá trị HHDV mua vào, thuế GTGT đầu vào được khấu trừ trên hồ sơ khai thuế và dữ liệu hóa đơn điện tử:"
        else:
            tieu_de = "Chênh lệch doanh thu HHDV, thuế GTGT bán ra trên tờ khai và trên dữ liệu hóa đơn điện tử:"

        self.lbl_title = QLabel(tieu_de)
        self.lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #000000; margin-bottom: 5px;")
        layout.addWidget(self.lbl_title)

        # =======================================================
        # 2. KHUNG CHỨA BẢNG (Dùng Spacing=0 để dán dính 2 bảng)
        # =======================================================
        khung_bang = QVBoxLayout()
        khung_bang.setSpacing(0)

        # --- A. BẢNG HEADER (Cố định 2 dòng ở trên cùng) ---
        self.bang_header = QTableWidget(2, 8)
        self.bang_header.horizontalHeader().setVisible(False)
        self.bang_header.verticalHeader().setVisible(False)
        self.bang_header.setEditTriggers(QTableWidget.NoEditTriggers)
        self.bang_header.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.bang_header.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.bang_header.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.bang_header.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical { background: transparent; }
            QScrollBar::handle:vertical { background: transparent; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background: transparent; border: none; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
        """)
        self.bang_header.setStyleSheet("QTableWidget { border-bottom: none; background-color: #f0f0f0; }")

        # --- B. BẢNG DỮ LIỆU (Có thể cuộn) ---
        self.bang_data = QTableWidget(0, 8)
        self.bang_data.horizontalHeader().setVisible(False)
        self.bang_data.verticalHeader().setVisible(False)
        self.bang_data.setEditTriggers(QTableWidget.NoEditTriggers)
        self.bang_data.setAlternatingRowColors(True)
        self.bang_data.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.bang_data.setStyleSheet("QTableWidget { border-top: none; }")

        for bang in [self.bang_header, self.bang_data]:
            header = bang.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            bang.setColumnWidth(0, 50)
            bang.setColumnWidth(1, 80)

        self.bang_data.horizontalScrollBar().valueChanged.connect(self.bang_header.horizontalScrollBar().setValue)

        khung_bang.addWidget(self.bang_header)
        khung_bang.addWidget(self.bang_data)
        layout.addLayout(khung_bang)

        self.ve_header_phuc_tap()
        self.bang_header.resizeRowsToContents()

        chieu_cao_hd = self.bang_header.rowHeight(0) + self.bang_header.rowHeight(1) + 2
        self.bang_header.setFixedHeight(chieu_cao_hd)

        # BẮT SỰ KIỆN CLICK ĐÚP Ở ĐÂY
        self.bang_data.cellDoubleClicked.connect(self.mo_popup_chi_tiet)

    def mo_popup_chi_tiet(self, row, col):
        if row == self.bang_data.rowCount() - 1 or not hasattr(self, 'df_raw') or self.df_raw is None:
            return

        item_ky = self.bang_data.item(row, 1)
        if not item_ky: return
        ky_str = item_ky.text().strip()

        if 'Q' in ky_str:
            df_loc = self.df_raw[self.df_raw['_Quy'] == ky_str].copy()
        else:
            df_loc = self.df_raw[self.df_raw['_Thang'] == ky_str].copy()

        if df_loc.empty: return

        dialog = DialogChiTietHoaDon(ky_str, df_loc, self.is_mua_vao, self)
        dialog.exec()

    def _tao_o_header(self, dong, cot, chuoi):
        item = QTableWidgetItem(str(chuoi))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setBackground(QColor("#f0f0f0"))
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        self.bang_header.setItem(dong, cot, item)

    def _tao_o_data(self, dong, cot, chuoi, can_giua=False, in_dam=False):
        item = QTableWidgetItem(str(chuoi))
        if can_giua:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        if in_dam:
            font = QFont()
            font.setBold(True)
            item.setFont(font)

        self.bang_data.setItem(dong, cot, item)

    def ve_header_phuc_tap(self):
        self.bang_header.setSpan(0, 0, 2, 1)
        self.bang_header.setSpan(0, 1, 2, 1)
        self.bang_header.setSpan(0, 2, 1, 2)
        self.bang_header.setSpan(0, 4, 1, 2)
        self.bang_header.setSpan(0, 6, 1, 2)

        self._tao_o_header(0, 0, "STT")
        self._tao_o_header(0, 1, "Kỳ")
        self._tao_o_header(0, 2, "Hóa đơn điện tử")
        self._tao_o_header(0, 4, "Tờ khai GTGT")
        self._tao_o_header(0, 6, "Chênh lệch (Tờ khai-Hóa đơn)")

        for cot in [2, 4, 6]:
            self._tao_o_header(1, cot, "Giá trị chưa thuế")
        for cot in [3, 5, 7]:
            self._tao_o_header(1, cot, "Thuế GTGT")

    def nap_du_lieu(self, danh_sach_du_lieu, df_raw=None):
        self.df_raw = df_raw
        self.bang_data.setRowCount(0)
        tong_hd_truoc = tong_hd_thue = tong_tk_truoc = tong_tk_thue = 0

        for stt, row_data in enumerate(danh_sach_du_lieu, 1):
            dong_hien_tai = self.bang_data.rowCount()
            self.bang_data.insertRow(dong_hien_tai)

            hd_truoc = float(row_data.get("hd_truoc", 0))
            hd_thue = float(row_data.get("hd_thue", 0))
            tk_truoc = float(row_data.get("tk_truoc", 0))
            tk_thue = float(row_data.get("tk_thue", 0))

            cl_truoc = tk_truoc - hd_truoc
            cl_thue = tk_thue - hd_thue

            tong_hd_truoc += hd_truoc
            tong_hd_thue += hd_thue
            tong_tk_truoc += tk_truoc
            tong_tk_thue += tk_thue

            self._tao_o_data(dong_hien_tai, 0, stt, can_giua=True)
            self._tao_o_data(dong_hien_tai, 1, row_data.get("ky", ""), can_giua=True)
            self._tao_o_data(dong_hien_tai, 2, dinh_dang_so_vn(hd_truoc) if hd_truoc else "-")
            self._tao_o_data(dong_hien_tai, 3, dinh_dang_so_vn(hd_thue) if hd_thue else "-")
            self._tao_o_data(dong_hien_tai, 4, dinh_dang_so_vn(tk_truoc) if tk_truoc else "-")
            self._tao_o_data(dong_hien_tai, 5, dinh_dang_so_vn(tk_thue) if tk_thue else "-")
            self._tao_o_data(dong_hien_tai, 6, dinh_dang_so_vn(cl_truoc) if cl_truoc else "-")
            self._tao_o_data(dong_hien_tai, 7, dinh_dang_so_vn(cl_thue) if cl_thue else "-")

        dong_tong = self.bang_data.rowCount()
        self.bang_data.insertRow(dong_tong)

        self._tao_o_data(dong_tong, 1, "Tổng", can_giua=True, in_dam=True)
        self.bang_data.setSpan(dong_tong, 0, 1, 2)

        tong_cl_truoc = tong_tk_truoc - tong_hd_truoc
        tong_cl_thue = tong_tk_thue - tong_hd_thue

        gia_tri_tong = [tong_hd_truoc, tong_hd_thue, tong_tk_truoc, tong_tk_thue, tong_cl_truoc, tong_cl_thue]
        for cot, gia_tri in zip(range(2, 8), gia_tri_tong):
            self._tao_o_data(dong_tong, cot, dinh_dang_so_vn(gia_tri) if gia_tri else "-", in_dam=True)


class DialogChiTietHoaDon(QDialog):
    def __init__(self, ky_bao_cao, df_chi_tiet, is_mua_vao, parent=None):
        super().__init__(parent)
        self.loai_hd = "MUA VÀO" if is_mua_vao else "BÁN RA"
        self.ky_bao_cao = ky_bao_cao

        # FIX VẤN ĐỀ 1: Cho phép phóng to, thu nhỏ, kéo giãn
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle(f"Chi tiết Hóa đơn {self.loai_hd} - Kỳ: {ky_bao_cao}")
        self.resize(1300, 750)
        self.setStyleSheet("QDialog { background-color: #f8fafc; }")

        # FIX VẤN ĐỀ 5: Đổi tên cột Code thành Tiếng Việt
        dict_doi_ten = {
            'Ký hiệu HD': 'Ký hiệu', 'Sohoadon': 'Số HĐ', 'Số HĐ': 'Số HĐ',
            'Ngaylap': 'Ngày lập', 'NgayLap': 'Ngày lập',
            'Tennguoiban': 'Tên người bán', 'MSTnguoiban': 'MST người bán',
            'Tennguoimua': 'Tên người mua', 'MSTnguoimua': 'MST người mua',
            'Tenhanghoa': 'Tên Hàng hóa/Dịch vụ', 'DonViTienTe': 'Loại tiền',
            'ThueSuat': 'Thuế suất', 'Thuế suất GTGT(%)': 'Thuế suất',
            'TongTienChuaThue': 'Giá trị chưa thuế', 'TongTienThue': 'Thuế GTGT',
            'ThanhTien': 'Tổng tiền thanh toán', 'Trạng thái hóa đơn': 'Trạng thái',
            'Đối chiếu HĐ rủi ro': 'Cảnh báo Rủi ro'
        }

        df_clean = df_chi_tiet.copy()
        cols_to_keep = [c for c in df_clean.columns if not str(c).startswith('_')]
        self.df_data = df_clean[cols_to_keep].rename(columns=dict_doi_ten)

        self._thiet_lap_ui()

    def _thiet_lap_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        khung_top = QHBoxLayout()

        lbl_title = QLabel(f"BẢNG KÊ CHI TIẾT HÓA ĐƠN {self.loai_hd} - KỲ: {self.ky_bao_cao}")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e3a8a;")
        khung_top.addWidget(lbl_title)

        khung_top.addStretch()

        # FIX VẤN ĐỀ 2: Thanh tìm kiếm (Filter)
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Gõ để tìm kiếm (Tên, Số HĐ, MST...)")
        self.txt_search.setFixedWidth(350)
        self.txt_search.setStyleSheet(
            "padding: 8px; border: 1px solid #cbd5e1; border-radius: 5px; font-size: 13px; background-color: white;")
        self.txt_search.textChanged.connect(self.loc_du_lieu)
        khung_top.addWidget(self.txt_search)

        # FIX VẤN ĐỀ 6: Nút xuất Excel riêng biệt
        btn_excel = QPushButton(" Xuất Excel bảng này")
        import qtawesome as qta
        btn_excel.setIcon(qta.icon('fa5s.file-excel', color='white'))
        btn_excel.setStyleSheet(
            "background-color: #10b981; color: white; padding: 8px 15px; font-weight: bold; border-radius: 5px;")
        btn_excel.clicked.connect(self.xuat_excel_nhanh)
        khung_top.addWidget(btn_excel)

        layout.addLayout(khung_top)

        self.bang_chi_tiet = QTableWidget()
        self.bang_chi_tiet.setStyleSheet("""
            QTableWidget { background-color: #ffffff; alternate-background-color: #f1f5f9; gridline-color: #cbd5e1; }
            QHeaderView::section { background-color: #e2e8f0; font-weight: bold; padding: 4px; border: 1px solid #cbd5e1;}
        """)
        self.bang_chi_tiet.setAlternatingRowColors(True)
        self.bang_chi_tiet.setEditTriggers(QTableWidget.NoEditTriggers)

        # FIX VẤN ĐỀ 3: Tắt cột STT mặc định
        self.bang_chi_tiet.verticalHeader().setVisible(False)

        # FIX VẤN ĐỀ 2: Bật Sort
        self.bang_chi_tiet.setSortingEnabled(False)
        layout.addWidget(self.bang_chi_tiet)

        self.do_du_lieu_vao_bang()

        btn_dong = QPushButton("Đóng cửa sổ (ESC)")
        btn_dong.setStyleSheet(
            "background-color: #64748b; color: white; padding: 10px 20px; font-weight: bold; border-radius: 5px;")
        btn_dong.clicked.connect(self.reject)
        layout.addWidget(btn_dong, alignment=Qt.AlignmentFlag.AlignCenter)

    def do_du_lieu_vao_bang(self):
        df = self.df_data
        self.bang_chi_tiet.setColumnCount(len(df.columns))
        self.bang_chi_tiet.setHorizontalHeaderLabels(df.columns.tolist())
        self.bang_chi_tiet.setRowCount(len(df))

        cot_tien_te = ['giá trị chưa thuế', 'thuế gtgt', 'tổng tiền thanh toán', 'đơn giá']
        # FIX VẤN ĐỀ 4: Số HĐ và Ký hiệu giữ nguyên
        cot_so_hd = ['số hđ', 'ký hiệu']

        for r_idx, row in enumerate(df.itertuples(index=False)):
            for c_idx, val in enumerate(row):
                val_str = "" if pd.isna(val) else str(val).strip()
                col_name = df.columns[c_idx].lower()

                if any(k in col_name for k in cot_so_hd):
                    val_str = val_str.replace('.0', '') if val_str.endswith('.0') else val_str
                    item = QTableWidgetItem(val_str)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                elif any(k in col_name for k in cot_tien_te):
                    try:
                        num_val = float(val_str.replace(',', ''))
                        val_format = dinh_dang_so_vn(num_val)
                    except:
                        val_format = val_str
                    item = QTableWidgetItem(val_format)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                else:
                    item = QTableWidgetItem(val_str)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

                self.bang_chi_tiet.setItem(r_idx, c_idx, item)

        self.bang_chi_tiet.setSortingEnabled(True)

        header = self.bang_chi_tiet.horizontalHeader()
        self.bang_chi_tiet.resizeColumnsToContents()
        for i, col in enumerate(df.columns):
            if "tên" in col.lower() or "hàng hóa" in col.lower() or "người" in col.lower():
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
                if self.bang_chi_tiet.columnWidth(i) > 400: self.bang_chi_tiet.setColumnWidth(i, 400)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

    def loc_du_lieu(self, text):
        text = text.lower().strip()
        for row in range(self.bang_chi_tiet.rowCount()):
            match = False
            for col in range(self.bang_chi_tiet.columnCount()):
                item = self.bang_chi_tiet.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.bang_chi_tiet.setRowHidden(row, not match)

    def xuat_excel_nhanh(self):
        import pandas as pd
        duong_dan, _ = QFileDialog.getSaveFileName(self, "Lưu file Excel Chi tiết",
                                                   f"Chi_Tiet_HD_{self.loai_hd}_{self.ky_bao_cao.replace('/', '_')}.xlsx",
                                                   "Excel Files (*.xlsx)")
        if not duong_dan: return

        try:
            data_xuat = []
            for row in range(self.bang_chi_tiet.rowCount()):
                if not self.bang_chi_tiet.isRowHidden(row):
                    row_data = []
                    for col in range(self.bang_chi_tiet.columnCount()):
                        item = self.bang_chi_tiet.item(row, col)
                        val = item.text() if item else ""
                        row_data.append(val)
                    data_xuat.append(row_data)

            df_export = pd.DataFrame(data_xuat, columns=self.df_data.columns)
            df_export.to_excel(duong_dan, index=False)
            QMessageBox.information(self, "Thành công", f"Đã xuất file Excel chi tiết tại:\n{duong_dan}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất file: {e}")