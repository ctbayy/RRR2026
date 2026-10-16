import re
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from module_ho_tro.dinh_dang_so import dinh_dang_so_vn

try:
    from module_doc_xml.tu_dien_chi_tieu import TU_DIEN_TO_KHAI
except ImportError:
    TU_DIEN_TO_KHAI = {}


class WidgetDoiChieuCheo(QWidget):
    def __init__(self, tieu_de="III. Báo cáo đối chiếu chéo dữ liệu", parent=None):
        super().__init__(parent)
        self.tieu_de = tieu_de
        self.danh_sach_bang = []
        self.thiet_lap_giao_dien()

    def thiet_lap_giao_dien(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        if self.tieu_de:
            self.lbl_title = QLabel(self.tieu_de)
            self.lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #000000; margin-bottom: 5px;")
            layout.addWidget(self.lbl_title)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.layout_container = QVBoxLayout(self.container)
        self.layout_container.setContentsMargins(0, 0, 0, 0)
        self.layout_container.setSpacing(25)
        self.layout_container.addStretch()

        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)

    def nap_du_lieu(self, danh_sach_du_lieu):
        self.danh_sach_bang.clear()
        while self.layout_container.count() > 1:
            item = self.layout_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not danh_sach_du_lieu: return

        # -------------------------------------------------------------
        # CỖ MÁY BÓC TÁCH STRING BẰNG REGEX (ĐÃ FIX LỖI TỜ KHAI)
        # -------------------------------------------------------------
        def _lay_ma_form(chuoi_goc):
            if not chuoi_goc: return "Dữ liệu"
            chuoi_str = str(chuoi_goc)

            # Quét tìm các định dạng mã chuẩn (hỗ trợ cả gạch nối và gạch dưới)
            match = re.search(
                r'(01/GTGT|02/GTGT|03/TNDN|04/TNDN|05/QTT[-_]TNCN|05/KK[-_]TNCN|BCTC[-_]TT133|BCTC[-_]TT200|01/TAIN|02/TAIN|TAIN)',
                chuoi_str)
            if match:
                return match.group(1).replace('_', '-')

            if "HD_BAN_RA" in chuoi_str or "bán ra" in chuoi_str.lower(): return "Hóa đơn Bán ra"
            if "HD_MUA_VAO" in chuoi_str or "mua vào" in chuoi_str.lower(): return "Hóa đơn Mua vào"
            if "TK" in chuoi_str or "Sổ cái" in chuoi_str or "Phát sinh" in chuoi_str: return "Sổ cái Tài khoản"

            # Fallback nếu Engine ném ra dạng tag nguyên thủy [Mã | ...]
            if "[" in chuoi_str and "|" in chuoi_str:
                return chuoi_str.split("|")[0].replace("[", "").strip().replace('_', '-')

            return "Dữ liệu"

        def _dich_ten_chi_tieu(chuoi_goc):
            if not chuoi_goc: return ""
            chuoi_str = str(chuoi_goc)
            if "Chỉ tiêu" in chuoi_str or "=" in chuoi_str:
                return chuoi_str  # Trả thẳng nếu Engine đã dịch sẵn

            if "|" in chuoi_str:
                ma_ct = chuoi_str.split("|")[-1].replace("]", "").strip()
            else:
                ma_ct = chuoi_str.replace("[", "").replace("]", "").strip()

            for form, form_data in TU_DIEN_TO_KHAI.items():
                if isinstance(form_data, dict):
                    for phan_he, phan_he_data in form_data.items():
                        if isinstance(phan_he_data, dict) and ma_ct in phan_he_data:
                            return f"[{ma_ct}] {phan_he_data[ma_ct]}"
                        elif isinstance(phan_he_data, str) and phan_he == ma_ct:
                            return f"[{ma_ct}] {phan_he_data}"
            return f"Chỉ tiêu {ma_ct}"

        def _format_so(val):
            try:
                return dinh_dang_so_vn(round(float(val), 2), 2 if not round(float(val), 2).is_integer() else 0)
            except:
                return str(val)

        # -------------------------------------------------------------
        # GOM NHÓM ĐỘNG THEO CẶP
        # -------------------------------------------------------------
        dict_nhom = {}
        for r in danh_sach_du_lieu:
            ve_a = r.get('ve_a_goc', '')
            ve_b = r.get('ve_b_goc', '')

            form_a = _lay_ma_form(ve_a)
            form_b = _lay_ma_form(ve_b)

            ten_cap = f"{form_a} VÀ {form_b}" if r.get('is_ab') else f"{form_a}"
            if ten_cap not in dict_nhom: dict_nhom[ten_cap] = []
            dict_nhom[ten_cap].append(r)

        # -------------------------------------------------------------
        # RẢI DỮ LIỆU LÊN GIAO DIỆN (BẢN FLAT UX - 1 BẢNG LIỀN MẠCH)
        # -------------------------------------------------------------
        # 1. Khởi tạo 1 Siêu Bảng duy nhất
        bang = QTableWidget(0, 7)
        bang.horizontalHeader().setVisible(False) # Ẩn Header mặc định để dùng Header fake
        bang.verticalHeader().setVisible(False)
        bang.setEditTriggers(QTableWidget.NoEditTriggers)

        bang.setWordWrap(True)
        bang.setTextElideMode(Qt.TextElideMode.ElideNone)
        bang.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        bang.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        bang.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        bang.wheelEvent = lambda event: event.ignore()

        # Style cho toàn bộ bảng (Sạch sẽ, kẻ viền nét mảnh)
        bang.setStyleSheet("QTableWidget { gridline-color: #e2e8f0; background-color: #ffffff; border: 1px solid #cbd5e1; }")

        # =========================================================
        # CẤU HÌNH ĐỘ RỘNG CỘT THÔNG MINH (TRỊ DỨT ĐIỂM LỖI CẮT CHỮ)
        # =========================================================
        header = bang.horizontalHeader()

        # 1. Cột STT: Tự ôm sát số thứ tự
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        # 2. Cột Nội dung: Giãn nở tự do (Stretch) để chứa câu dài
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # 3. Cột Vế A, Vế B, Chênh lệch: Tự đo độ dài của tên Tờ khai và phình ra vừa KHÍT
        # Đảm bảo 100% không bao giờ xuất hiện dấu "..."
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # 4. Cột Trạng thái: Bắt buộc chốt cứng 130px để bảo vệ form của thẻ HTML Badge
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        bang.setColumnWidth(5, 130)

        # 5. Cột Khuyến nghị: Giãn nở tự do, chia sẻ không gian thừa với cột Nội dung
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        # =========================================================

        # Hàm helper tạo ô đa năng
        def _tao_o(r_idx, c_idx, text, align_right=False, align_center=False, tooltip=None, bg_color=None, fg_color=None, is_bold=False):
            item = QTableWidgetItem(str(text))
            if align_right: item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            elif align_center: item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            else: item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            if bg_color: item.setBackground(QColor(bg_color))
            if fg_color: item.setForeground(QColor(fg_color))
            if is_bold:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            if tooltip: item.setToolTip(tooltip)
            bang.setItem(r_idx, c_idx, item)

        # 2. Bơm dữ liệu nối đuôi nhau
        for ten_cap, ds_loi in dict_nhom.items():

            def format_header(ma_form):
                if "hóa đơn" in ma_form.lower() or "sổ cái" in ma_form.lower() or "dữ liệu" in ma_form.lower(): return ma_form
                return f"Tờ khai {ma_form}"

            tk_a = format_header(_lay_ma_form(ds_loi[0].get('ve_a_goc', '')))
            tk_b = format_header(_lay_ma_form(ds_loi[0].get('ve_b_goc', ''))) if ds_loi[0].get('is_ab') else "Dữ liệu Vế Phải (B)"

            # --- VẼ DÒNG HEADER ĐỘNG (Đóng vai trò vách ngăn) ---
            r_head = bang.rowCount()
            bang.insertRow(r_head)
            cols_head = ["STT", "Nội dung đối chiếu", tk_a, tk_b, "Chênh lệch (A-B)", "Đánh giá", "Gợi ý"]
            
            for c, text in enumerate(cols_head):
                # Sửa bg_color từ "#f1f5f9" thành "#cbd5e1" (xám đậm) để tách biệt hoàn toàn với dữ liệu
                _tao_o(r_head, c, text, align_center=True, bg_color="#cbd5e1", fg_color="#0f172a", is_bold=True)

            # --- VẼ CÁC DÒNG DỮ LIỆU BÊN DƯỚI HEADER ---
            for i, r in enumerate(ds_loi):
                r_idx = bang.rowCount()
                bang.insertRow(r_idx)

                is_rui_ro = r.get('is_rui_ro', False)
                trang_thai_text = r.get('trang_thai', '')
                so_chenh_lech = r.get('ket_qua_so', 0)

                # Tự chế Sọc ngựa vằn
                bg_dong = "#f8fafc" if i % 2 == 0 else "#ffffff"

                _tao_o(r_idx, 0, str(i + 1), align_center=True, bg_color=bg_dong)
                _tao_o(r_idx, 1, r.get('ten_phan_tich', ''), bg_color=bg_dong)

                chi_tiet_bien_dict = r.get('chi_tiet_bien', {})
                str_bien = ""
                if isinstance(chi_tiet_bien_dict, dict) and len(chi_tiet_bien_dict) > 2:
                    str_bien = "\n[Chi tiết biến: " + "; ".join([f"{k} = {dinh_dang_so_vn(v)}" for k, v in chi_tiet_bien_dict.items()]) + "]"

                v_a = r.get('ve_a_goc', '')
                so_a = _format_so(r.get('gia_tri_a', 0)) if r.get('gia_tri_a', '') != '' and r.get('gia_tri_a') is not None else '---'
                _tao_o(r_idx, 2, so_a, align_right=True, tooltip=(_dich_ten_chi_tieu(v_a) + str_bien).strip(), bg_color=bg_dong)

                if r.get('is_ab'):
                    v_b = r.get('ve_b_goc', '')
                    so_b = _format_so(r.get('gia_tri_b', 0)) if r.get('gia_tri_b', '') != '' and r.get('gia_tri_b') is not None else '---'
                    tooltip_b = _dich_ten_chi_tieu(v_b)
                else:
                    so_b, tooltip_b = "---", "Không áp dụng đối chiếu vế B"
                _tao_o(r_idx, 3, so_b, align_right=True, tooltip=tooltip_b, bg_color=bg_dong)

                # ĐÃ XÓA is_bold=True
                _tao_o(r_idx, 4, _format_so(so_chenh_lech), align_right=True, bg_color=bg_dong)

                # Vũ khí thẻ Badge + Chữ tàng hình ép dòng
                if is_rui_ro: bg_badge, text_badge = "#ef4444", "❌ CẢNH BÁO"
                elif "Thiếu" in str(so_chenh_lech) or "Không đủ" in trang_thai_text: bg_badge, text_badge = "#f59e0b", "⚠️ THIẾU DỮ LIỆU"
                else: bg_badge, text_badge = "#10b981", "✅ AN TOÀN"

                hien_thi = trang_thai_text if trang_thai_text.strip() else text_badge
                html_badge = f"<div style='background-color: {bg_badge}; color: white; padding: 4px 2px; border-radius: 4px; font-weight: bold; text-align: center; font-size: 11px; white-space: normal; word-wrap: break-word;'>{hien_thi}</div>"

                lbl_badge = QLabel(html_badge)
                lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl_badge.setContentsMargins(2, 2, 2, 2)
                lbl_badge.setWordWrap(True)

                item_an = QTableWidgetItem(hien_thi + "\n\n")
                item_an.setForeground(QColor("transparent"))
                item_an.setBackground(QColor(bg_dong))
                bang.setItem(r_idx, 5, item_an)
                bang.setCellWidget(r_idx, 5, lbl_badge)

                _tao_o(r_idx, 6, r.get('thong_diep', ''), bg_color=bg_dong)

        bang.resizeRowsToContents()
        self.layout_container.insertWidget(self.layout_container.count() - 1, bang)
        self.danh_sach_bang.append(bang)
        self.cap_nhat_chieu_cao_cac_bang()

    def cap_nhat_chieu_cao_cac_bang(self):
        tong_chieu_cao = self.layout_container.contentsMargins().top() + self.layout_container.contentsMargins().bottom()

        for i in range(self.layout_container.count()):
            widget = self.layout_container.itemAt(i).widget()
            if isinstance(widget, QTableWidget):
                h = widget.horizontalHeader().height()
                for r in range(widget.rowCount()):
                    if not widget.isRowHidden(r): h += widget.rowHeight(r)
                widget.setFixedHeight(h + 2)
                tong_chieu_cao += (h + 2)
            elif isinstance(widget, QLabel):
                tong_chieu_cao += widget.sizeHint().height()
            tong_chieu_cao += self.layout_container.spacing()

        self.container.setFixedHeight(tong_chieu_cao)

    def loc_du_lieu(self, text):
        text = text.lower()
        for bang in self.danh_sach_bang:
            for row in range(bang.rowCount()):
                match = False
                for col in range(bang.columnCount()):
                    item = bang.item(row, col)
                    if item and text in item.text().lower():
                        match = True
                        break
                bang.setRowHidden(row, not match)
        self.cap_nhat_chieu_cao_cac_bang()