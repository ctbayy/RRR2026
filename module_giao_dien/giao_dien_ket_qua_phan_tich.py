from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QTableWidget,
                               QTableWidgetItem, QHeaderView, QHBoxLayout, QLineEdit,
                               QLabel, QSplitter, QScrollArea, QSizePolicy, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
from module_ho_tro.dinh_dang_so import dinh_dang_so_vn
from module_giao_dien.giao_dien_bao_cao import WidgetBaoCaoDoanhSo
from module_giao_dien.giao_dien_doi_chieu_cheo import WidgetDoiChieuCheo
from module_giao_dien.builder_phan_tich_ngang import BuilderPhanTichNgang
from module_giao_dien.ui_web_effects import TheKPIWeb, tao_bong_do_web

class WidgetKetQuaPhanTich(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thiet_lap_giao_dien()

    def _tao_tieu_de_html(self, text):
        """Tạo tiêu đề phân cách các mảng báo cáo (Bản tối giản Clean UX)"""
        lbl = QLabel(text.upper())
        lbl.setStyleSheet("""
            font-size: 15px; 
            font-weight: bold; 
            color: #1e3a8a; 
            border-bottom: 2px solid #cbd5e1; 
            padding-bottom: 5px; 
            margin-top: 25px;
            margin-bottom: 5px;
        """)
        # Căn trái để form báo cáo liền mạch, hiện đại hơn
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return lbl

    def thiet_lap_giao_dien(self):
        layout_chinh = QVBoxLayout(self)
        layout_chinh.setContentsMargins(0, 0, 0, 0)

        self.tabs_kq = QTabWidget()
        # --- BẬT NÚT ĐÓNG TAB ---
        self.tabs_kq.setTabsClosable(True)
        self.tabs_kq.tabCloseRequested.connect(self.dong_tab_soan_thao)
        layout_chinh.addWidget(self.tabs_kq)

        # ==========================================
        # TAB 0: TỔNG HỢP KẾT QUẢ (TRANG HTML SCROLL)
        # ==========================================
        self.tab_tong = QWidget()
        layout_tong = QVBoxLayout(self.tab_tong)
        layout_tong.setContentsMargins(5, 10, 5, 5)

        # 1. Khung Search
        khung_search = QHBoxLayout()
        lbl_search = QLabel("🔍 Tìm kiếm nhanh toàn trang:")
        lbl_search.setStyleSheet("font-weight: bold; color: #334155;")
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Nhập từ khóa để lọc các dòng dữ liệu bên dưới...")
        self.txt_search.setStyleSheet("padding: 8px; border: 1px solid #cbd5e1; border-radius: 5px;")
        self.txt_search.textChanged.connect(self.loc_du_lieu_tong)

        khung_search.addWidget(lbl_search)
        khung_search.addWidget(self.txt_search)
        layout_tong.addLayout(khung_search)

        # 2. Vùng Cuộn (ScrollArea)
        self.scroll_tong = QScrollArea()
        self.scroll_tong.setWidgetResizable(True)
        self.scroll_tong.setStyleSheet("QScrollArea { border: none; background-color: #ffffff; }")

        self.trang_html = QWidget()
        self.trang_html.setStyleSheet("background-color: #ffffff;")
        self.layout_html = QVBoxLayout(self.trang_html)
        self.layout_html.setContentsMargins(10, 0, 10, 20)
        self.layout_html.setSpacing(10)

        # 3. Khởi tạo các Component
        self.tong_bcao_ban_ra = WidgetBaoCaoDoanhSo(is_mua_vao=False)
        self.tong_bcao_mua_vao = WidgetBaoCaoDoanhSo(is_mua_vao=True)
        self.tong_bang_cheo = WidgetDoiChieuCheo(tieu_de="")
        self.tong_bang_bctc = self._tao_bang_mau()
        self.tong_bang_ngang = BuilderPhanTichNgang() # Dùng cỗ máy mới

        # Tắt thanh cuộn cục bộ
        self.tong_bang_bctc.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tong_bang_bctc.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.tong_bang_ngang.bang_data.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tong_bang_ngang.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        for w_bc in [self.tong_bcao_ban_ra, self.tong_bcao_mua_vao]:
            w_bc.bang_data.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.tong_bang_cheo.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 3.1 Khung KPI Tổng quan Rủi ro (Executive Risk Dashboard)
        self.khung_kpi_rui_ro = QFrame()
        self.khung_kpi_rui_ro.setStyleSheet("background: transparent; border: none;")
        layout_kpi_rr = QHBoxLayout(self.khung_kpi_rui_ro)
        layout_kpi_rr.setContentsMargins(0, 4, 0, 10)
        layout_kpi_rr.setSpacing(12)

        self.kpi_rr_cao = TheKPIWeb(
            tieu_de="Rủi ro mức Cao", 
            gia_tri="0", 
            subtext="Chưa có dữ liệu", 
            icon_name="fa5s.exclamation-circle", 
            icon_color="#DC2626", 
            bg_icon="#FEF2F2", 
            badge_text="Nghiêm trọng",
            badge_color="#FEF2F2",
            badge_text_color="#B91C1C"
        )
        self.kpi_rr_canh_bao = TheKPIWeb(
            tieu_de="Cảnh báo chênh lệch", 
            gia_tri="0", 
            subtext="Chưa có dữ liệu", 
            icon_name="fa5s.exclamation-triangle", 
            icon_color="#D97706", 
            bg_icon="#FEF3C7", 
            badge_text="Cần lưu ý",
            badge_color="#FEF3C7",
            badge_text_color="#B45309"
        )
        self.kpi_rr_lech_hd = TheKPIWeb(
            tieu_de="Lệch Hóa đơn & TK", 
            gia_tri="0", 
            subtext="Chưa có dữ liệu", 
            icon_name="fa5s.balance-scale", 
            icon_color="#2563EB", 
            bg_icon="#EFF6FF", 
            badge_text="Đối chiếu",
            badge_color="#EFF6FF",
            badge_text_color="#1D4ED8"
        )
        self.kpi_rr_tong_rule = TheKPIWeb(
            tieu_de="Tổng tiêu chí đã chạy", 
            gia_tri="0", 
            subtext="Chưa có dữ liệu", 
            icon_name="fa5s.clipboard-check", 
            icon_color="#059669", 
            bg_icon="#ECFDF5", 
            badge_text="Hoàn tất",
            badge_color="#ECFDF5",
            badge_text_color="#047857"
        )

        layout_kpi_rr.addWidget(self.kpi_rr_cao)
        layout_kpi_rr.addWidget(self.kpi_rr_canh_bao)
        layout_kpi_rr.addWidget(self.kpi_rr_lech_hd)
        layout_kpi_rr.addWidget(self.kpi_rr_tong_rule)
        self.layout_html.addWidget(self.khung_kpi_rui_ro)

        # 4. Trình bày bố cục HTML
        self.layout_html.addWidget(self._tao_tieu_de_html("BÁO CÁO ĐỐI CHIẾU DOANH SỐ HÓA ĐƠN"))
        self.layout_html.addWidget(self.tong_bcao_ban_ra)
        self.layout_html.addWidget(self.tong_bcao_mua_vao)

        self.layout_html.addWidget(self._tao_tieu_de_html("BÁO CÁO ĐỐI CHIẾU CHÉO DỮ LIỆU TỜ KHAI"))
        self.layout_html.addWidget(self.tong_bang_cheo)

        self.layout_html.addWidget(self._tao_tieu_de_html("KẾT QUẢ PHÂN TÍCH BÁO CÁO TÀI CHÍNH"))
        self.layout_html.addWidget(self.tong_bang_bctc)

        self.layout_html.addWidget(self._tao_tieu_de_html("KẾT QUẢ PHÂN TÍCH TỶ LỆ"))
        self.layout_html.addWidget(self.tong_bang_ngang)

        self.layout_html.addStretch()
        self.scroll_tong.setWidget(self.trang_html)
        layout_tong.addWidget(self.scroll_tong)
        self.tabs_kq.addTab(self.tab_tong, "Tổng hợp Kết quả")

        # ==========================================
        # TAB 1: ĐỐI CHIẾU HÓA ĐƠN
        # ==========================================
        self.tab_doi_chieu_hd = QWidget()
        layout_hd = QVBoxLayout(self.tab_doi_chieu_hd)
        bo_chia_doc = QSplitter(Qt.Orientation.Vertical)
        bo_chia_doc.setStyleSheet("QSplitter::handle { background-color: #cbd5e1; height: 3px; }")

        self.widget_bcao_ban_ra = WidgetBaoCaoDoanhSo(is_mua_vao=False)
        self.widget_bcao_mua_vao = WidgetBaoCaoDoanhSo(is_mua_vao=True)
        bo_chia_doc.addWidget(self.widget_bcao_ban_ra)
        bo_chia_doc.addWidget(self.widget_bcao_mua_vao)
        bo_chia_doc.setSizes([400, 400])

        layout_hd.addWidget(bo_chia_doc)
        self.tabs_kq.addTab(self.tab_doi_chieu_hd, "BC Đối chiếu Hóa đơn")

        # ==========================================
        # TAB 2, 3, 4: CÁC NHÓM PHÂN TÍCH CHUYÊN SÂU
        # ==========================================
        self.bang_doi_chieu_cheo = WidgetDoiChieuCheo(tieu_de="Báo cáo đối chiếu chéo dữ liệu")
        self.tabs_kq.addTab(self.bang_doi_chieu_cheo, "BC Đối chiếu chéo dữ liệu")

        self.bang_bctc = self._tao_bang_mau()
        self.tabs_kq.addTab(self.bang_bctc, "Phân tích BCTC")

        self.bang_pt_ngang = BuilderPhanTichNgang()
        self.tabs_kq.addTab(self.bang_pt_ngang, "Phân tích tỷ lệ")

        # ==========================================
        # TAB 5: PHÂN TÍCH KHÁC (HUB CHỨA CÁC MODULE CUSTOM)
        # ==========================================
        self.tab_phan_tich_khac = QWidget()
        layout_khac = QVBoxLayout(self.tab_phan_tich_khac)
        layout_khac.setContentsMargins(5, 5, 5, 5)

        self.scroll_khac = QScrollArea()
        self.scroll_khac.setWidgetResizable(True)
        self.scroll_khac.setStyleSheet("QScrollArea { border: none; background-color: #ffffff; }")

        self.trang_html_khac = QWidget()
        self.trang_html_khac.setStyleSheet("background-color: #ffffff;")
        self.layout_html_khac = QVBoxLayout(self.trang_html_khac)
        self.layout_html_khac.setContentsMargins(10, 10, 10, 20)
        self.layout_html_khac.setSpacing(15)

        # Băng rôn chào mừng mặc định nếu chưa có module nào
        self.lbl_empty_khac = QLabel("Đang chờ nạp các Module phân tích chuyên sâu...")
        self.lbl_empty_khac.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 14px;")
        self.lbl_empty_khac.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_html_khac.addWidget(self.lbl_empty_khac)

        self.layout_html_khac.addStretch()  # Lò xo đẩy mọi thứ lên trên
        self.scroll_khac.setWidget(self.trang_html_khac)
        layout_khac.addWidget(self.scroll_khac)

        self.tabs_kq.addTab(self.tab_phan_tich_khac, "Phân tích chuyên sâu")

        # Ẩn nút X cho 6 tab gốc (Tính cả tab Phân tích khác)
        from PySide6.QtWidgets import QTabBar
        for i in range(6):
            self.tabs_kq.tabBar().setTabButton(i, QTabBar.ButtonPosition.RightSide, None)
            self.tabs_kq.tabBar().setTabButton(i, QTabBar.ButtonPosition.LeftSide, None)

    def them_module_phan_tich_khac(self, tieu_de, widget_module):
        """
        Hàm API dùng để bơm các module custom do mày tự code vào Tab Phân tích khác.
        Tự động xử lý ẩn text mặc định, vẽ băng rôn và nhét widget vào.
        """
        # Ẩn dòng chữ mặc định nếu nó đang hiện
        if self.lbl_empty_khac.isVisible():
            self.lbl_empty_khac.setVisible(False)

        # Tháo lò xo ở cuối ra để nhét đồ mới vào, sau đó lắp lò xo lại
        item = self.layout_html_khac.takeAt(self.layout_html_khac.count() - 1)

        # Bơm Băng rôn Tiêu đề và Widget
        if tieu_de:
            self.layout_html_khac.addWidget(self._tao_tieu_de_html(tieu_de))
        self.layout_html_khac.addWidget(widget_module)

        # Lắp lại lò xo
        if item:
            self.layout_html_khac.addItem(item)

    def dong_tab_soan_thao(self, index):
        """Chỉ cho phép đóng các tab sinh ra sau này (Index > 5)"""
        if index > 5:
            widget = self.tabs_kq.widget(index)
            self.tabs_kq.removeTab(index)
            widget.deleteLater()

    def _tao_bang_mau(self):
        bang = QTableWidget(0, 7)
        bang.setHorizontalHeaderLabels([
            "Nhóm Phân Tích", "Tên Phép Kiểm Tra (Logic)", "Số liệu Vế Trái (A)",
            "Số liệu Vế Phải (B)", "Chênh lệch (A - B)", "Trạng thái", "Khuyến nghị / Thông điệp"
        ])
        header = bang.horizontalHeader()

        # Đồng bộ giao diện sọc ngựa vằn
        header.setStyleSheet("QHeaderView::section { background-color: #f8fafc; font-weight: bold; color: #1e293b; border: 1px solid #e2e8f0; padding: 4px; }")
        bang.setStyleSheet("QTableWidget { gridline-color: #e2e8f0; alternate-background-color: #f8fafc; }")

        # =========================================================
        # CẤU HÌNH ĐỘ RỘNG CỘT THÔNG MINH (TRỊ DỨT ĐIỂM LỖI CẮT CHỮ CHO BCTC)
        # =========================================================
        # 1. Cột Nhóm Phân Tích: Tự đo chữ và ôm sát
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        # 2. Cột Tên Phép Kiểm Tra: Giãn nở tự do để không bao giờ xuất hiện "..."
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # 3. Cột Số liệu A, B, Chênh lệch: Ôm sát độ dài con số
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # 4. Cột Trạng thái: Chốt cứng 130px để bảo toàn form thẻ HTML (Badge)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        bang.setColumnWidth(5, 130)

        # 5. Cột Khuyến nghị: Bung xõa tự do chiếm nốt phần không gian trống
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        # =========================================================

        bang.setWordWrap(True)
        bang.setTextElideMode(Qt.TextElideMode.ElideNone)
        bang.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        bang.setAlternatingRowColors(True)
        bang.setEditTriggers(QTableWidget.NoEditTriggers)

        # Ép phẳng cuộn (Flat UX)
        #bang.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        #bang.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        #bang.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        #bang.wheelEvent = lambda event: event.ignore()
        # KHÔI PHỤC THANH CUỘN CHO BẢNG Ở TAB ĐỘC LẬP
        bang.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        bang.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        bang.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # TUYỆT ĐỐI XÓA DÒNG bang.wheelEvent = lambda event: event.ignore()
        # ĐỂ CHUỘT CÓ THỂ LĂN ĐƯỢC
        return bang

    # ========================================================
    # LOGIC SEARCH & ĐIỀU CHỈNH CHIỀU CAO
    # ========================================================
    def _cap_nhat_chieu_cao(self, bang):
        h = bang.horizontalHeader().height()
        for r in range(bang.rowCount()):
            if not bang.isRowHidden(r): h += bang.rowHeight(r)

        # Sửa từ (h + 2) thành (h + 5) để có biên độ an toàn cho khung viền
        bang.setFixedHeight(h + 5)

    def _cap_nhat_chieu_cao_widget_bc(self, widget_bc):
        h = 0
        for r in range(widget_bc.bang_data.rowCount()):
            if not widget_bc.bang_data.isRowHidden(r): h += widget_bc.bang_data.rowHeight(r)
        widget_bc.bang_data.setFixedHeight(h + 2)

    def loc_du_lieu_tong(self, text):
        text = text.lower()

        # 1. Lọc BCTC và Ngang
        for bang in [self.tong_bang_bctc]:
            for row in range(bang.rowCount()):
                match = False
                for col in range(bang.columnCount()):
                    item = bang.item(row, col)
                    if item and text in item.text().lower():
                        match = True
                        break
                bang.setRowHidden(row, not match)
            self._cap_nhat_chieu_cao(bang)


        # 2. Lọc Hóa đơn & Phân tích Ngang (Dùng chung cấu trúc widget.bang_data)
        for w_bc in [self.tong_bcao_ban_ra, self.tong_bcao_mua_vao, self.tong_bang_ngang]:
            bang = w_bc.bang_data
            for row in range(bang.rowCount()):
                if row == bang.rowCount() - 1:
                    bang.setRowHidden(row, False)
                    continue
                match = False
                for col in range(bang.columnCount()):
                    item = bang.item(row, col)
                    if item and text in item.text().lower():
                        match = True
                        break
                bang.setRowHidden(row, not match)
            self._cap_nhat_chieu_cao_widget_bc(w_bc)

        # 3. Lọc Đối chiếu chéo
        self.tong_bang_cheo.loc_du_lieu(text)
        self.tong_bang_cheo.setFixedHeight(self.tong_bang_cheo.container.height() + 20)

    # ========================================================
    # BƠM DỮ LIỆU ĐỒNG BỘ
    # ========================================================
    def nap_du_lieu_tong_the(self, ket_qua_list, du_lieu_ban_ra, du_lieu_mua_vao, df_ban_ra_goc=None, df_mua_vao_goc=None):
        # 0. Cập nhật Thống kê KPI Rủi ro (Executive Risk Dashboard)
        count_cao = 0
        count_canh_bao = 0
        count_lech_hd = 0

        # Import bộ lọc rác chuẩn
        try:
            from module_ho_tro.thu_vien_mau_cau import la_canh_bao_rac
        except ImportError:
            def la_canh_bao_rac(item): return False

        # Kiểm tra chênh lệch Hóa đơn và Tờ khai thực tế
        if du_lieu_ban_ra:
            for row in du_lieu_ban_ra:
                try:
                    c_dt = abs(float(row.get('hd_truoc', 0) or 0) - float(row.get('tk_truoc', 0) or 0))
                    c_th = abs(float(row.get('hd_thue', 0) or 0) - float(row.get('tk_thue', 0) or 0))
                    if 'chenh_lech_dt' in row and row.get('chenh_lech_dt') is not None:
                        c_dt = max(c_dt, abs(float(row.get('chenh_lech_dt', 0) or 0)))
                    if 'chenh_lech_thue' in row and row.get('chenh_lech_thue') is not None:
                        c_th = max(c_th, abs(float(row.get('chenh_lech_thue', 0) or 0)))
                    if c_dt > 1000 or c_th > 1000:
                        count_lech_hd += 1
                except Exception:
                    pass

        if du_lieu_mua_vao:
            for row in du_lieu_mua_vao:
                try:
                    c_gt = abs(float(row.get('hd_truoc', 0) or 0) - float(row.get('tk_truoc', 0) or 0))
                    c_th = abs(float(row.get('hd_thue', 0) or 0) - float(row.get('tk_thue', 0) or 0))
                    if 'chenh_lech_gt' in row and row.get('chenh_lech_gt') is not None:
                        c_gt = max(c_gt, abs(float(row.get('chenh_lech_gt', 0) or 0)))
                    if 'chenh_lech_thue' in row and row.get('chenh_lech_thue') is not None:
                        c_th = max(c_th, abs(float(row.get('chenh_lech_thue', 0) or 0)))
                    if c_gt > 1000 or c_th > 1000:
                        count_lech_hd += 1
                except Exception:
                    pass

        # Quét và phân loại rủi ro từ ket_qua_list
        tu_khoa_nghiem_trong = [
            'bỏ trốn', 'ngừng hoạt động', 'không hoạt động tại địa chỉ',
            'giấu doanh thu', 'chênh lệch doanh thu', '131', '511', '3331',
            'tồn kho âm', 'tồn kho ảo', 'không hợp pháp', 'sai lệch nghiêm trọng',
            'không khớp'
        ]

        for r in ket_qua_list:
            if not r.get('is_rui_ro', False):
                continue
            # Lọc cảnh báo rác, thiếu dữ liệu, lệch = 0
            if la_canh_bao_rac(r):
                continue

            val_so = 0.0
            try:
                raw_val = r.get('ket_qua_so', 0)
                val_so = abs(float(str(raw_val).replace(',', '').strip()))
            except Exception:
                pass

            ten_pt = str(r.get('ten_phan_tich', '')).lower()
            thong_diep = str(r.get('thong_diep', '')).lower()
            muc_do = str(r.get('muc_do', '')).lower()

            # Tiêu chí rủi ro cao: Chênh lệch >= 50 triệu VNĐ hoặc thuộc nhóm rủi ro trọng điểm
            is_cao = (
                val_so >= 50_000_000 or
                'cao' in muc_do or
                any(kw in ten_pt or kw in thong_diep for kw in tu_khoa_nghiem_trong)
            )

            if is_cao:
                count_cao += 1
            else:
                count_canh_bao += 1

        tong_tieu_chi = len(ket_qua_list)
        if du_lieu_ban_ra: tong_tieu_chi += len(du_lieu_ban_ra)
        if du_lieu_mua_vao: tong_tieu_chi += len(du_lieu_mua_vao)

        self.kpi_rr_cao.cap_nhat(
            gia_tri=str(count_cao),
            subtext=f"{count_cao} chỉ tiêu rủi ro cao" if count_cao > 0 else "Không phát hiện rủi ro cao",
            badge_text="Cần xử lý" if count_cao > 0 else "An toàn"
        )
        self.kpi_rr_canh_bao.cap_nhat(
            gia_tri=str(count_canh_bao),
            subtext=f"{count_canh_bao} chỉ tiêu cần lưu ý" if count_canh_bao > 0 else "Chỉ số bình thường",
            badge_text="Lưu ý" if count_canh_bao > 0 else "Bình thường"
        )
        self.kpi_rr_lech_hd.cap_nhat(
            gia_tri=str(count_lech_hd),
            subtext=f"{count_lech_hd} kỳ có lệch doanh thu/thuế" if count_lech_hd > 0 else "Khớp 100% dữ liệu",
            badge_text="Lệch số" if count_lech_hd > 0 else "Khớp chuẩn"
        )
        self.kpi_rr_tong_rule.cap_nhat(
            gia_tri=str(tong_tieu_chi),
            subtext="Tờ khai, Hóa đơn & BCTC",
            badge_text="Đã hoàn tất"
        )

        # 1. Bơm Hóa đơn
        for w in [self.widget_bcao_ban_ra, self.tong_bcao_ban_ra]: w.nap_du_lieu(du_lieu_ban_ra, df_ban_ra_goc)
        for w in [self.widget_bcao_mua_vao, self.tong_bcao_mua_vao]: w.nap_du_lieu(du_lieu_mua_vao, df_mua_vao_goc)

        # 2. Xóa data cũ
        for bang in [self.tong_bang_bctc, self.bang_bctc]:
            bang.setRowCount(0)
        self.tong_bang_ngang.bang_data.setRowCount(0)
        self.bang_pt_ngang.bang_data.setRowCount(0)

        # 3. Rút riêng data "Đối chiếu chéo" nạp vào Custom Widget
        ds_cheo = [r for r in ket_qua_list if "chéo" in str(r.get('nhom', '')).lower()]
        self.bang_doi_chieu_cheo.nap_du_lieu(ds_cheo)
        self.tong_bang_cheo.nap_du_lieu(ds_cheo)

        # 4. Phân luồng dữ liệu BCTC và Ngang
        self.ds_bctc_cho_xu_ly = []  # Biến toàn cục để lưu danh sách BCTC
        ds_ngang = []

        for r in ket_qua_list:
            nhom = r.get('nhom', 'Khác')
            if "chéo" not in nhom.lower():
                if "tỷ lệ" in nhom.lower():
                    ds_ngang.append(r)
                elif "tài chính" in nhom.lower() or "bctc" in nhom.lower():
                    self.ds_bctc_cho_xu_ly.append(r)

        # =======================================================================
        # HÀM VẼ 1 DÒNG DỮ LIỆU (Tách ra để dùng chung)
        # =======================================================================
        def _format_so(val):
            try:
                return dinh_dang_so_vn(round(float(val), 2), 2 if not round(float(val), 2).is_integer() else 0)
            except:
                return str(val)

        def _ve_dong_du_lieu(bang_dich, data):
            row_idx = bang_dich.rowCount()
            bang_dich.insertRow(row_idx)
            is_rui_ro = data.get('is_rui_ro', False)
            trang_thai_text = data.get('trang_thai', '')
            so_chenh_lech = data.get('ket_qua_so', 0)

            def _tao_o(c, text, align_right=False, align_center=False, tooltip=None, is_bold=False):
                item = QTableWidgetItem(str(text))
                if align_right: item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                elif align_center: item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else: item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if tooltip: item.setToolTip(tooltip)
                bang_dich.setItem(row_idx, c, item)

            _tao_o(0, data.get('nhom', ''))
            _tao_o(1, data.get('ten_phan_tich', ''))

            chi_tiet_bien_dict = data.get('chi_tiet_bien', {})
            str_bien = ""
            if isinstance(chi_tiet_bien_dict, dict) and len(chi_tiet_bien_dict) > 2:
                str_bien = "\n[Chi tiết biến: " + "; ".join([f"{k} = {dinh_dang_so_vn(v)}" for k, v in chi_tiet_bien_dict.items()]) + "]"

            gt_a = data.get('gia_tri_a', 0)
            so_a = _format_so(gt_a) if gt_a != '' and gt_a is not None else '---'
            tooltip_a = (str(data.get('ve_a_goc', '') or '') + str_bien).strip()
            _tao_o(2, so_a, align_right=True, tooltip=tooltip_a)

            if data.get('is_ab'):
                gt_b = data.get('gia_tri_b', 0)
                so_b = _format_so(gt_b) if gt_b != '' and gt_b is not None else '---'
                _tao_o(3, so_b, align_right=True, tooltip=data.get('ve_b_goc', ''))
            else:
                _tao_o(3, "---", align_right=True, tooltip="Không áp dụng đối chiếu vế B")

            _tao_o(4, _format_so(so_chenh_lech), align_right=True)

            if is_rui_ro:
                bg_badge, text_badge = "#ef4444", "❌ CẢNH BÁO"
            elif "Thiếu" in str(so_chenh_lech) or "Không đủ" in trang_thai_text:
                bg_badge, text_badge = "#f59e0b", "⚠️ THIẾU DỮ LIỆU"
            else:
                bg_badge, text_badge = "#10b981", "✅ AN TOÀN"

            hien_thi = trang_thai_text if trang_thai_text.strip() else text_badge
            html_badge = f"""
                <div style='background-color: {bg_badge}; color: white; 
                            padding: 4px 2px; border-radius: 4px; font-weight: bold; 
                            text-align: center; font-size: 11px; 
                            white-space: normal; word-wrap: break-word;'>
                    {hien_thi}
                </div>
            """
            lbl_badge = QLabel(html_badge)
            lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_badge.setContentsMargins(2, 2, 2, 2)
            lbl_badge.setWordWrap(True)

            item_an = QTableWidgetItem(hien_thi + "\n\n")
            item_an.setForeground(QColor("transparent"))
            item_an.setBackground(QColor("transparent"))
            bang_dich.setItem(row_idx, 5, item_an)
            bang_dich.setCellWidget(row_idx, 5, lbl_badge)

            _tao_o(6, data.get('thong_diep', ''))

        # =======================================================================
        # 5. KÍCH HOẠT CÁC CỖ MÁY (Phân tích ngang vẽ ngay, BCTC vẽ theo mẻ)
        # =======================================================================
        self.bang_pt_ngang.nap_du_lieu_chuoi_thoi_gian(ds_ngang)
        self.tong_bang_ngang.nap_du_lieu_chuoi_thoi_gian(ds_ngang)

        # Chuyển tab về trang Tổng hợp ngay lập tức để User nhìn thấy UI
        self.tabs_kq.setCurrentIndex(0)

        # Cài đặt biến cho cỗ máy bơm dữ liệu BCTC
        self.chi_so_hien_tai = 0
        self.kich_thuoc_me = 30 # Bơm 30 dòng mỗi lần
        self.tabs_kq.setTabText(self.tabs_kq.indexOf(self.bang_bctc), "Phân tích BCTC (Đang tải...)")

        def _bom_du_lieu_bctc():
            """Cỗ máy đệ quy bơm nhỏ giọt chống đơ giao diện"""
            if self.chi_so_hien_tai >= len(self.ds_bctc_cho_xu_ly):
                # ĐÃ BƠM XONG TẤT CẢ
                self.tabs_kq.setTabText(self.tabs_kq.indexOf(self.bang_bctc), "Phân tích BCTC")
                # Bật lại tính năng tính chiều cao tự động vào phút chót
                for bang in [self.tong_bang_bctc, self.bang_bctc]:
                    bang.resizeRowsToContents()
                self._cap_nhat_chieu_cao(self.tong_bang_bctc)

                # Cập nhật chiều cao các thành phần khác
                self._cap_nhat_chieu_cao_widget_bc(self.tong_bang_ngang)
                self._cap_nhat_chieu_cao_widget_bc(self.tong_bcao_ban_ra)
                self._cap_nhat_chieu_cao_widget_bc(self.tong_bcao_mua_vao)
                self.tong_bang_cheo.setFixedHeight(self.tong_bang_cheo.container.height() + 20)
                return

            # Khóa vẽ UI tạm thời để nhồi 30 dòng tốc độ cao
            self.tong_bang_bctc.setUpdatesEnabled(False)
            self.bang_bctc.setUpdatesEnabled(False)

            # Bơm 1 mẻ (30 dòng)
            gioi_han = min(self.chi_so_hien_tai + self.kich_thuoc_me, len(self.ds_bctc_cho_xu_ly))
            for i in range(self.chi_so_hien_tai, gioi_han):
                r = self.ds_bctc_cho_xu_ly[i]
                _ve_dong_du_lieu(self.bang_bctc, r)
                _ve_dong_du_lieu(self.tong_bang_bctc, r)

            self.chi_so_hien_tai = gioi_han

            # Mở lại UI cho khung hình được render
            self.tong_bang_bctc.setUpdatesEnabled(True)
            self.bang_bctc.setUpdatesEnabled(True)

            # Đặt báo thức 10ms sau gọi lại chính hàm này để bơm mẻ tiếp theo
            QTimer.singleShot(10, _bom_du_lieu_bctc)

        # Phát súng khởi động cỗ máy bơm dữ liệu BCTC
        _bom_du_lieu_bctc()

    def lam_moi_giao_dien(self):
        """Hàm dọn dẹp sạch sẽ dữ liệu trên tất cả các tab khi tạo phiên làm việc mới"""

        # Xóa dữ liệu các bảng cơ bản
        for bang in [self.tong_bang_bctc, self.bang_bctc]:
            bang.setRowCount(0)
        self.tong_bang_ngang.bang_data.setRowCount(0)
        self.bang_pt_ngang.bang_data.setRowCount(0)

        # Xóa dữ liệu Đối chiếu chéo
        self.tong_bang_cheo.nap_du_lieu([])
        self.bang_doi_chieu_cheo.nap_du_lieu([])

        # Xóa dữ liệu Hóa đơn
        self.tong_bcao_ban_ra.bang_data.setRowCount(0)
        self.tong_bcao_mua_vao.bang_data.setRowCount(0)
        self.widget_bcao_ban_ra.bang_data.setRowCount(0)
        self.widget_bcao_mua_vao.bang_data.setRowCount(0)

        # ========================================================
        # [MỚI BỔ SUNG]: Dọn dẹp sạch sẽ Tab Phân tích Chuyên sâu
        # ========================================================
        for i in reversed(range(self.layout_html_khac.count())):
            item = self.layout_html_khac.itemAt(i)
            # Xóa tất cả các Module đã bơm vào, ngoại trừ Nhãn Trống và Lò xo (Spacer)
            if item.widget() and item.widget() != self.lbl_empty_khac:
                item.widget().deleteLater()
                self.layout_html_khac.takeAt(i)

        # Bật lại dòng chữ "Đang chờ nạp..."
        self.lbl_empty_khac.setVisible(True)
