import ast
import json
import re
import qtawesome as qta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
                               QPushButton, QTextEdit, QLineEdit, QLabel, QFormLayout, QMessageBox,
                               QHeaderView, QComboBox, QGroupBox, QTableWidget, QTableWidgetItem,
                               QRadioButton, QStackedWidget, QSizePolicy, QScrollArea, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QTextCursor
from module_ho_tro.tu_dien_tt200 import TU_DIEN_TK_TT200
from module_doc_hoadon.tu_dien_hoa_don import MAU_HOA_DON
from module_doc_xml.tu_dien_chi_tieu import MAP_TEN_TO_KHAI, TU_DIEN_TO_KHAI
from module_ho_tro.quan_ly_cong_thuc import QuanLyCongThuc
from module_ho_tro.dinh_dang_so import dinh_dang_so_vn
from module_phan_tich.engine_tinh_toan import safe_eval, _chuan_hoa_bieu_thuc, _safe_div


class GiaoDienTaoCongThuc(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.o_nhap_hien_tai = None
        self.ma_dang_sua = None

        self.setStyleSheet("""
            QWidget { background-color: #f4f7f6; }
            QLabel { font-weight: bold; color: #003a99; margin-top: 5px; }
            QTreeWidget { background-color: white; border: 1px solid #ccc; border-radius: 5px; font-size: 13px; }
            QLineEdit#SearchBox { padding: 8px; border: 1px solid #0052D4; border-radius: 5px; margin-bottom: 5px;}
            QPushButton.ToanTu { background-color: #e2e8f0; border-radius: 4px; padding: 10px; font-weight: bold; font-size: 14px; color: #0f172a;}
            QPushButton.ToanTu:hover { background-color: #cbd5e1; }
            QPushButton#BtnLuu { background-color: #059669; color: white; font-weight: bold; padding: 12px; border-radius: 5px; font-size: 14px;}
            QPushButton#BtnLuu:hover { background-color: #047857; }
            QPushButton.BtnDieuHuong { background-color: #2563eb; color: white; font-weight: bold; padding: 8px 15px; border-radius: 4px; font-size: 13px;}
            QPushButton.BtnDieuHuong:hover { background-color: #1d4ed8; }
            QPushButton#BtnThemMoi { background-color: #059669; color: white; font-weight: bold; padding: 8px 15px; border-radius: 4px; font-size: 13px;}
            QPushButton#BtnThemMoi:hover { background-color: #047857; }
            QGroupBox { font-weight: bold; color: #1e3a8a; border: 1px solid #93c5fd; border-radius: 5px; margin-top: 10px; padding-top: 15px;}
            QTableWidget { background-color: white; alternate-background-color: #f1f5f9; }
            QRadioButton { font-size: 14px; font-weight: bold; color: #333; padding: 5px;}
        """)

        layout_tong = QVBoxLayout(self)
        layout_tong.setContentsMargins(10, 10, 10, 10)

        self.stack_chinh = QStackedWidget()
        layout_tong.addWidget(self.stack_chinh)

        self.trang_danh_sach = QWidget()
        self.trang_tao_moi = QWidget()

        self.stack_chinh.addWidget(self.trang_danh_sach)
        self.stack_chinh.addWidget(self.trang_tao_moi)

        self.thiet_lap_trang_danh_sach()
        self.thiet_lap_trang_tao_moi()

        self.chuyen_trang_danh_sach()
        self.tai_du_lieu_tu_dien_len_cay()

    def _dich_cong_thuc_sang_html(self, cong_thuc_goc):
        if not cong_thuc_goc: return ""

        def replacer(match):
            tag_full = match.group(0)
            loi_ngoac = re.search(r'\[(.*?)\]', tag_full)
            if not loi_ngoac: return tag_full
            noi_dung_tag = loi_ngoac.group(1)
            parts = [p.strip() for p in noi_dung_tag.split("|")]

            bg_col, txt_col = "#e0f2fe", "#0369a1"
            label_text = tag_full

            # 1. HÓA ĐƠN
            if len(parts) == 2 and "HD_" in parts[0]:
                bg_col, txt_col = "#d1fae5", "#065f46"
                loai_hd = "Bán ra" if "BAN_RA" in parts[0] else "Mua vào"
                prefix = "TỔNG HĐ" if "SUM" in tag_full else "HĐ"
                label_text = f"{prefix} {loai_hd}: {parts[1]}"

            # 2. BÁO CÁO TÀI CHÍNH & SỔ CÁI
            elif len(parts) == 3 and parts[0].startswith("BCTC_"):
                bg_col, txt_col = "#ffedd5", "#9a3412"
                ma_form, phan_he, ma_ct = parts[0].replace('BCTC_', ''), parts[1], parts[2]

                ph_nice = phan_he
                if "CDKT" in phan_he:
                    ph_nice = ph_nice.replace("CDKT_", "CĐKT ")
                elif "KQKD" in phan_he:
                    ph_nice = ph_nice.replace("KQKD_", "KQKD ")
                elif "LCTT" in phan_he:
                    ph_nice = ph_nice.replace("LCTT_", "LCTT ")
                if "CDTK" in phan_he: ph_nice = ph_nice.replace("CDTK_", "CĐSPS " if "200" in ma_form else "Sổ cái ")

                ph_nice = ph_nice.replace("SoCuoiNam", "Cuối năm").replace("SoDauNam", "Đầu năm")
                ph_nice = ph_nice.replace("NamNay", "Năm nay").replace("NamTruoc", "Năm trước")
                ph_nice = ph_nice.replace("NoDauKy", "Nợ ĐK").replace("CoDauKy", "Có ĐK")
                ph_nice = ph_nice.replace("NoCuoiKy", "Nợ CK").replace("CoCuoiKy", "Có CK")
                ph_nice = ph_nice.replace("DuNo", "Dư Nợ ").replace("DuCo", "Dư Có ")
                ph_nice = ph_nice.replace("PhatSinhNo", "Nợ PS").replace("PhatSinhCo", "Có PS")
                ph_nice = ph_nice.replace("NoPhatSinh", "Nợ PS").replace("CoPhatSinh", "Có PS")

                if "CDTK" in phan_he and "200" in ma_form:
                    tk_ma = ma_ct.replace('ct', '')
                    ten_ct = TU_DIEN_TK_TT200.get(tk_ma, tk_ma)
                else:
                    ten_ct = ma_ct.replace('ct', '') if "CDTK" in phan_he else ma_ct
                    try:
                        dict_form = "BCTC_TT133" if "133" in ma_form else "BCTC_TT200"
                        dict_data = TU_DIEN_TO_KHAI.get(dict_form, {})
                        nhom_tu_dien = None
                        if "CDKT" in phan_he:
                            nhom_tu_dien = "B01_CDKT"
                        elif "KQKD" in phan_he:
                            nhom_tu_dien = "B02_KQKD"
                        elif "LCTT" in phan_he:
                            nhom_tu_dien = "B03_LCTT_TT"
                        elif "CDTK" in phan_he:
                            nhom_tu_dien = "B04_CDTK"

                        if nhom_tu_dien and nhom_tu_dien in dict_data and ma_ct in dict_data[nhom_tu_dien]:
                            ten_ct = dict_data[nhom_tu_dien][
                                ma_ct] if "CDTK" in phan_he else f"{ma_ct.replace('ct', '')} - {dict_data[nhom_tu_dien][ma_ct]}"
                    except:
                        pass
                label_text = f"[{ma_form} - {ph_nice}] {ten_ct}"

            # 3. TỜ KHAI THUẾ
            elif len(parts) == 3:
                ma_form, phan_he, ma_ct = parts
                ten_ct = ma_ct
                bg_col, txt_col = "#e0f2fe", "#0369a1"
                try:
                    form_data = TU_DIEN_TO_KHAI.get(ma_form, {})
                    if phan_he == "ChiTieuChinh" and "ToKhaiChinh" in form_data:
                        ten_ct = form_data["ToKhaiChinh"].get(ma_ct, ma_ct)
                    elif phan_he in form_data and isinstance(form_data[phan_he], dict):
                        ten_ct = form_data[phan_he].get(ma_ct, ma_ct)
                except:
                    pass
                prefix = "TỔNG KỲ" if "SUM" in tag_full else "Tờ khai"
                label_text = f"[{prefix} {ma_form}] {ten_ct}"

            if "PREV" in tag_full:
                bg_col, txt_col = "#f3e8ff", "#6b21a8"
                label_text = f"⏳ KỲ TRƯỚC: {label_text.replace('Tờ khai ', '').replace('TỔNG KỲ ', '')}"

            style = f"background-color: {bg_col}; color: {txt_col}; text-decoration: none;"
            return f"&nbsp;<a href='{tag_full}' style='{style}'>&nbsp;<b>{label_text}</b>&nbsp;</a>&nbsp;"

        html_text = re.sub(r'(?:PREV|SUM_TK|SUM|TK)?\[.*?\]', replacer, cong_thuc_goc)
        return f"<div style='line-height: 2.0;'>{html_text}</div>"

    def _extract_raw_formula(self, text_edit):
        doc = text_edit.document()
        raw = ""
        block = doc.begin()
        last_anchor = None
        while block.isValid():
            it = block.begin()
            while not it.atEnd():
                fragment = it.fragment()
                if fragment.isValid():
                    fmt = fragment.charFormat()
                    if fmt.isAnchor():
                        href = fmt.anchorHref()
                        if href != last_anchor:
                            raw += f" {href} "
                            last_anchor = href
                    else:
                        text = fragment.text().replace('\xa0', ' ')
                        raw += text
                        last_anchor = None
                it += 1
            block = block.next()
            if block.isValid(): raw += " "
        return re.sub(r'\s+', ' ', raw).strip()

    def thiet_lap_trang_danh_sach(self):
        layout = QVBoxLayout(self.trang_danh_sach)
        layout.setContentsMargins(0, 0, 0, 0)

        khung_header = QHBoxLayout()
        lbl_info = QLabel("DANH SÁCH CÁC QUY TẮC PHÂN TÍCH ĐANG CÓ TRONG HỆ THỐNG")
        lbl_info.setStyleSheet("font-size: 15px; font-weight: bold; color: #333;")

        btn_them_moi = QPushButton(" Thêm Quy tắc mới")
        btn_them_moi.setIcon(qta.icon('fa5s.plus', color='white'))
        btn_them_moi.setObjectName("BtnThemMoi")
        btn_them_moi.clicked.connect(self.chuyen_trang_tao_moi)

        self.btn_khoi_phuc = QPushButton(" Khôi phục Mặc định")
        self.btn_khoi_phuc.setIcon(qta.icon('fa5s.sync', color='white'))
        self.btn_khoi_phuc.setStyleSheet(
            "background-color: #F59E0B; color: white; font-weight: bold; padding: 8px 15px; border-radius: 4px; font-size: 13px;")
        self.btn_khoi_phuc.clicked.connect(self.khoi_phuc_cong_thuc)

        khung_header.addWidget(lbl_info)
        khung_header.addStretch()
        khung_header.addWidget(self.btn_khoi_phuc)
        khung_header.addWidget(btn_them_moi)
        layout.addLayout(khung_header)

        self.txt_tim_kiem = QLineEdit()
        self.txt_tim_kiem.setObjectName("SearchBox")
        self.txt_tim_kiem.setPlaceholderText("Nhập mã, tên công thức, nhóm hoặc điều kiện để tìm nhanh...")
        self.txt_tim_kiem.addAction(qta.icon('fa5s.search', color='#94a3b8'), QLineEdit.ActionPosition.LeadingPosition)
        self.txt_tim_kiem.textChanged.connect(self.loc_cong_thuc_nhanh)
        layout.addWidget(self.txt_tim_kiem)

        self.bang_cong_thuc = QTableWidget()
        self.bang_cong_thuc.setColumnCount(5)
        self.bang_cong_thuc.setHorizontalHeaderLabels(
            ["Mã", "Nhóm", "Tên Phép Đối Chiếu", "Biểu thức Logic (Boolean)", "Thao tác"])
        self.bang_cong_thuc.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.bang_cong_thuc.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.bang_cong_thuc.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.bang_cong_thuc.setAlternatingRowColors(True)
        self.bang_cong_thuc.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.bang_cong_thuc)

    def thiet_lap_trang_tao_moi(self):
        layout_trang = QVBoxLayout(self.trang_tao_moi)
        layout_trang.setContentsMargins(0, 0, 0, 0)

        khung_header = QHBoxLayout()
        btn_quay_lai = QPushButton(" Quay lại danh sách")
        btn_quay_lai.setIcon(qta.icon('fa5s.arrow-left', color='white'))
        btn_quay_lai.setProperty("class", "BtnDieuHuong")
        btn_quay_lai.clicked.connect(self.chuyen_trang_danh_sach)

        self.lbl_tieude_form = QLabel("XÂY DỰNG QUY TẮC KIỂM TRA (V2)")
        self.lbl_tieude_form.setStyleSheet("font-size: 15px; font-weight: bold; color: #333;")

        khung_header.addWidget(btn_quay_lai)
        khung_header.addSpacing(20)
        khung_header.addWidget(self.lbl_tieude_form)
        khung_header.addStretch()
        layout_trang.addLayout(khung_header)

        layout_chinh = QHBoxLayout()
        layout_trang.addLayout(layout_chinh)

        # CỘT TRÁI: CÂY TỪ ĐIỂN
        khung_trai = QVBoxLayout()
        khung_trai.addWidget(QLabel("TỪ ĐIỂN DỮ LIỆU (Nhấp đúp để chèn):"))
        khung_ky = QHBoxLayout()
        self.rdo_ky_nay = QRadioButton("Kỳ hiện tại")
        self.rdo_ky_truoc = QRadioButton("Kỳ TRƯỚC (PREV)")
        self.rdo_ky_nay.setChecked(True)
        self.rdo_ky_truoc.setStyleSheet("color: #6b21a8; font-weight: bold;")
        khung_ky.addWidget(self.rdo_ky_nay)
        khung_ky.addWidget(self.rdo_ky_truoc)
        khung_trai.addLayout(khung_ky)

        self.o_tim_kiem = QLineEdit()
        self.o_tim_kiem.setObjectName("SearchBox")
        self.o_tim_kiem.setPlaceholderText("Gõ tên hoặc mã để tìm...")
        self.o_tim_kiem.textChanged.connect(self.loi_tim_kiem)
        khung_trai.addWidget(self.o_tim_kiem)

        self.cay_du_lieu = QTreeWidget()
        self.cay_du_lieu.setHeaderLabels(["Danh mục Cấu trúc Dữ liệu", "Tag Công thức"])
        self.cay_du_lieu.setColumnHidden(1, True)
        self.cay_du_lieu.itemDoubleClicked.connect(self.chen_tag_vao_cong_thuc)
        khung_trai.addWidget(self.cay_du_lieu)
        layout_chinh.addLayout(khung_trai, 3)  # Stretch = 3

        # CỘT GIỮA: NÚT TOÁN TỬ
        khung_giua = QVBoxLayout()
        khung_giua.setAlignment(Qt.AlignmentFlag.AlignTop)
        khung_giua.addWidget(QLabel("Phép tính:"))
        for nhan, gia_tri in [("+", " + "), ("-", " - "), ("*", " * "), ("/", " / "), ("(", " ( "), (")", " ) "),
                              ("AND", " and "), ("OR", " or ")]:
            btn = QPushButton(nhan)
            btn.setProperty("class", "ToanTu")
            btn.clicked.connect(lambda checked=False, val=gia_tri: self.chen_text(val, is_tag=False))
            khung_giua.addWidget(btn)
        layout_chinh.addLayout(khung_giua)  # Stretch = 1

        # CỘT PHẢI: FORM NHẬP LIỆU (BỌC TRONG QSCROLLAREA)
        khung_phai_widget = QWidget()
        khung_phai = QVBoxLayout(khung_phai_widget)
        khung_phai.setContentsMargins(5, 0, 0, 0)

        # MỤC 1: THÔNG TIN CHUNG
        box_thong_tin = QGroupBox("1. Thông tin Quy tắc kiểm tra")
        form_layout = QFormLayout(box_thong_tin)
        self.nhap_ten_pt = QLineEdit()
        self.nhap_ten_pt.setPlaceholderText("VD: Rủi ro tài khoản 331...")
        form_layout.addRow("Tên phép kiểm tra:", self.nhap_ten_pt)
        self.nhap_nhom = QComboBox()
        self.nhap_nhom.addItems(
            ["Báo cáo Đối chiếu chéo dữ liệu", "Phân tích Báo cáo tài chính", "Phân tích tỷ lệ", "Khác"])
        form_layout.addRow("Nhóm báo cáo:", self.nhap_nhom)
        khung_phai.addWidget(box_thong_tin)

        # MỤC 2: KHAI BÁO BIẾN SỐ (BẢNG QUẢN LÝ TẬP TRUNG)
        box_bien_so = QGroupBox("2. Khai báo Biến số (Nguyên liệu tính toán)")
        layout_bien = QVBoxLayout(box_bien_so)
        khung_nut_bien = QHBoxLayout()
        self.btn_them_bien = QPushButton(" + Thêm Biến mới")
        self.btn_them_bien.setStyleSheet(
            "background-color: #0284c7; color: white; font-weight: bold; padding: 5px 10px; border-radius: 4px;")
        self.btn_them_bien.clicked.connect(lambda: self.them_dong_bien("", ""))
        khung_nut_bien.addWidget(self.btn_them_bien)
        khung_nut_bien.addStretch()
        layout_bien.addLayout(khung_nut_bien)

        self.bang_bien = QTableWidget(0, 3)
        self.bang_bien.setHorizontalHeaderLabels(
            ["Tên Biến (VD: A, DOANH_THU)", "Giá trị / Tag Từ điển (Nhấp đúp cây để chèn)", "Xóa"])
        self.bang_bien.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.bang_bien.setColumnWidth(0, 180)
        self.bang_bien.setColumnWidth(2, 50)
        self.bang_bien.setMinimumHeight(150)
        layout_bien.addWidget(self.bang_bien)
        khung_phai.addWidget(box_bien_so)
        # =====================================================================
        # MỤC 2.5: CHỈ ĐỊNH DỮ LIỆU HIỂN THỊ LÊN BÁO CÁO (HYBRID V2)
        # =====================================================================
        box_hien_thi = QGroupBox("Chỉ định dữ liệu in ra Báo cáo (Vế A / Vế B)")
        layout_ht = QFormLayout(box_hien_thi)

        self.txt_hien_thi_a = QLineEdit()
        self.txt_hien_thi_a.setPlaceholderText("Gõ tên biến. VD: A, DOANH_THU...")
        self.txt_hien_thi_b = QLineEdit()
        self.txt_hien_thi_b.setPlaceholderText("Gõ tên biến. VD: B (Bỏ trống nếu không so sánh 2 vế)")

        layout_ht.addRow("Hiển thị Vế Trái (A) lấy từ Biến:", self.txt_hien_thi_a)
        layout_ht.addRow("Hiển thị Vế Phải (B) lấy từ Biến:", self.txt_hien_thi_b)
        khung_phai.addWidget(box_hien_thi)
        # MỤC 3: BIỂU THỨC LOGIC BOOLEAN CHỐT HẠ
        box_logic = QGroupBox("3. Biểu thức Logic Rủi ro (Đúng/Sai)")
        layout_logic = QVBoxLayout(box_logic)
        lbl_hd = QLabel(
            "Gõ công thức Toán & Logic (Hỗ trợ: +, -, *, /, >, <, ==, and, or, abs). VD: (A > B) and (abs(A - B) < 0.05)")
        lbl_hd.setStyleSheet("color: #64748b; font-style: italic;")
        layout_logic.addWidget(lbl_hd)

        self.nhap_logic_rui_ro = QTextEdit()
        self.nhap_logic_rui_ro.setMinimumHeight(70)
        self.nhap_logic_rui_ro.setStyleSheet(
            "font-family: Consolas; font-size: 14px; background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 4px;")

        def focus_logic(event):
            self.set_o_nhap(self.nhap_logic_rui_ro)
            QTextEdit.focusInEvent(self.nhap_logic_rui_ro, event)

        self.nhap_logic_rui_ro.focusInEvent = focus_logic
        layout_logic.addWidget(self.nhap_logic_rui_ro)
        khung_phai.addWidget(box_logic)

        # MỤC 4: KẾT LUẬN ĐƯA RA BÁO CÁO
        box_ket_luan = QGroupBox("4. Kết luận đưa ra báo cáo (Mở rộng)")
        layout_ket_luan = QVBoxLayout(box_ket_luan)
        lbl_rui_ro = QLabel("❌ Nếu VI PHẠM (Cảnh báo rủi ro):")
        lbl_rui_ro.setStyleSheet("color: #dc2626; font-weight: bold;")
        self.nhap_msg_rui_ro = QTextEdit()
        self.nhap_msg_rui_ro.setMinimumHeight(70)
        self.nhap_msg_rui_ro.setStyleSheet(
            "QTextEdit { background-color: #fef2f2; border: 1px solid #fca5a5; border-radius: 5px; padding: 5px; }")

        lbl_an_toan = QLabel("✅ Nếu KHỚP (An toàn):")
        lbl_an_toan.setStyleSheet("color: #059669; font-weight: bold;")
        self.nhap_msg_an_toan = QTextEdit()
        self.nhap_msg_an_toan.setMinimumHeight(45)
        self.nhap_msg_an_toan.setStyleSheet(
            "QTextEdit { background-color: #f0fdf4; border: 1px solid #86efac; border-radius: 5px; padding: 5px; }")

        layout_ket_luan.addWidget(lbl_rui_ro)
        layout_ket_luan.addWidget(self.nhap_msg_rui_ro)
        layout_ket_luan.addWidget(lbl_an_toan)
        layout_ket_luan.addWidget(self.nhap_msg_an_toan)
        khung_phai.addWidget(box_ket_luan, 1)

        # MỤC 5: CHẠY THỬ NGHIỆM CÔNG THỨC (SANDBOX DRY-RUN)
        box_test = QGroupBox("5. 🧪 Chạy thử nghiệm công thức (Sandbox)")
        layout_test = QVBoxLayout(box_test)

        lbl_hd_test = QLabel("Nhập giá trị giả lập cho các biến số để kiểm tra biểu thức trước khi lưu:")
        lbl_hd_test.setStyleSheet("color: #475569; font-style: italic; font-size: 12px;")
        layout_test.addWidget(lbl_hd_test)

        self.bang_test_bien = QTableWidget(0, 2)
        self.bang_test_bien.setHorizontalHeaderLabels(["Tên biến", "Giá trị giả lập (Số thực)"])
        self.bang_test_bien.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.bang_test_bien.setColumnWidth(0, 160)
        self.bang_test_bien.setMinimumHeight(110)
        layout_test.addWidget(self.bang_test_bien)

        khung_btn_test = QHBoxLayout()
        self.btn_nap_bien_test = QPushButton(" Đồng bộ biến số")
        self.btn_nap_bien_test.setIcon(qta.icon('fa5s.sync-alt', color='#0284c7'))
        self.btn_nap_bien_test.clicked.connect(self.nap_bien_vao_bang_test)
        khung_btn_test.addWidget(self.btn_nap_bien_test)

        self.btn_chay_thu = QPushButton("▶ Chạy thử nghiệm ngay")
        self.btn_chay_thu.setIcon(qta.icon('fa5s.play', color='white'))
        self.btn_chay_thu.setStyleSheet("background-color: #7c3aed; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px;")
        self.btn_chay_thu.clicked.connect(self.thuc_thi_chay_thu)
        khung_btn_test.addWidget(self.btn_chay_thu)
        layout_test.addLayout(khung_btn_test)

        self.lbl_ket_qua_test = QLabel("Chưa chạy thử nghiệm.")
        self.lbl_ket_qua_test.setWordWrap(True)
        self.lbl_ket_qua_test.setStyleSheet("background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 4px; padding: 8px; font-family: Segoe UI, sans-serif; font-size: 13px; color: #334155;")
        layout_test.addWidget(self.lbl_ket_qua_test)

        khung_phai.addWidget(box_test)

        # MỤC 6: TÙY CHỌN NƠI LƯU TRỮ
        box_tuy_chon_luu = QGroupBox("6. Tùy chọn nơi lưu trữ")
        layout_tuy_chon = QHBoxLayout(box_tuy_chon_luu)
        self.radio_luu_core = QRadioButton("Lưu vào công thức chung")
        self.radio_luu_core.setChecked(True)
        self.radio_luu_core.setStyleSheet("color: #DC2626; font-weight: bold;")
        self.radio_luu_user = QRadioButton("Lưu thành Rule Cá nhân (User)")
        self.radio_luu_user.setStyleSheet("color: #059669; font-weight: bold;")
        layout_tuy_chon.addWidget(self.radio_luu_core)
        layout_tuy_chon.addWidget(self.radio_luu_user)
        box_tuy_chon_luu.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        khung_phai.addWidget(box_tuy_chon_luu)

        self.btn_luu = QPushButton(" LƯU QUY TẮC")
        self.btn_luu.setIcon(qta.icon('fa5s.save', color='white'))
        self.btn_luu.setObjectName("BtnLuu")
        self.btn_luu.clicked.connect(self.luu_cong_thuc)
        khung_phai.addWidget(self.btn_luu)

        # BỌC SCROLLAREA CHO KHUNG PHẢI
        scroll_phai = QScrollArea()
        scroll_phai.setWidgetResizable(True)
        scroll_phai.setFrameShape(QFrame.Shape.NoFrame)
        scroll_phai.setStyleSheet("QScrollArea { background-color: transparent; }")
        scroll_phai.setWidget(khung_phai_widget)

        layout_chinh.addWidget(scroll_phai, stretch=8)  # Stretch = 6

    def them_dong_bien(self, ten_bien="", gia_tri=""):
        row_idx = self.bang_bien.rowCount()
        self.bang_bien.insertRow(row_idx)

        txt_ten = QLineEdit(ten_bien)
        txt_ten.setPlaceholderText("VD: VE_A")
        txt_ten.setStyleSheet("border: none; background: transparent; font-weight: bold; color: #b91c1c;")
        self.bang_bien.setCellWidget(row_idx, 0, txt_ten)

        # Đổi thành QTextEdit để chứa được HTML, ép chiều cao 35px để giả dạng ô input 1 dòng
        txt_gia_tri = QTextEdit()
        txt_gia_tri.setFixedHeight(35)
        txt_gia_tri.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        txt_gia_tri.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        txt_gia_tri.setPlaceholderText("Gõ số hoặc nhấp đúp cây bên trái...")
        txt_gia_tri.setStyleSheet("border: none; background: transparent; font-family: Consolas;")

        if gia_tri:
            txt_gia_tri.setHtml(self._dich_cong_thuc_sang_html(gia_tri))

        def focus_gia_tri(event, widget=txt_gia_tri):
            self.set_o_nhap(widget)
            QTextEdit.focusInEvent(widget, event)

        txt_gia_tri.focusInEvent = focus_gia_tri
        self.bang_bien.setCellWidget(row_idx, 1, txt_gia_tri)

        btn_xoa = QPushButton(qta.icon('fa5s.times'), "")
        btn_xoa.setStyleSheet("background-color: #fee2e2; color: #dc2626; border: none; border-radius: 4px;")
        btn_xoa.clicked.connect(lambda _, w=txt_ten: self._xoa_dong_bien(w))
        self.bang_bien.setCellWidget(row_idx, 2, btn_xoa)

    def _xoa_dong_bien(self, widget_ten):
        for i in range(self.bang_bien.rowCount()):
            if self.bang_bien.cellWidget(i, 0) == widget_ten:
                self.bang_bien.removeRow(i)
                break

    def chuyen_trang_danh_sach(self):
        self.load_danh_sach()
        self.huy_che_do_sua()
        self.stack_chinh.setCurrentIndex(0)

    def chuyen_trang_tao_moi(self):
        self.huy_che_do_sua()
        self.lbl_tieude_form.setText(" TẠO QUY TẮC KIỂM TRA MỚI (V2)")
        self.stack_chinh.setCurrentIndex(1)

    def huy_che_do_sua(self):
        self.nhap_ten_pt.clear()
        self.nhap_nhom.setCurrentIndex(0)
        self.bang_bien.setRowCount(0)
        self.txt_hien_thi_a.clear()
        self.txt_hien_thi_b.clear()
        self.nhap_logic_rui_ro.clear()
        self.nhap_msg_rui_ro.clear()
        self.nhap_msg_an_toan.clear()
        self.bang_test_bien.setRowCount(0)
        self.lbl_ket_qua_test.setText("Chưa chạy thử nghiệm.")
        self.lbl_ket_qua_test.setStyleSheet("background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 4px; padding: 8px; font-family: Segoe UI, sans-serif; font-size: 13px; color: #334155;")

        self.ma_dang_sua = None
        self.btn_luu.setText(" LƯU QUY TẮC")
        self.btn_luu.setIcon(qta.icon('fa5s.save', color='white'))
        self.btn_luu.setStyleSheet("")

    def set_o_nhap(self, text_edit):
        self.o_nhap_hien_tai = text_edit

    def chen_tag_vao_cong_thuc(self, item, column):
        tag = item.text(1)
        if tag:
            if hasattr(self, 'rdo_ky_truoc') and self.rdo_ky_truoc.isChecked():
                if "SUM" not in tag: tag = f"PREV{tag}"
            self.chen_text(tag, is_tag=True)

    def chen_text(self, text, is_tag=False):
        if self.o_nhap_hien_tai is None or not self.o_nhap_hien_tai.isVisible():
            self.o_nhap_hien_tai = self.nhap_logic_rui_ro

        if isinstance(self.o_nhap_hien_tai, QTextEdit):
            cursor = self.o_nhap_hien_tai.textCursor()
            if is_tag:
                html = self._dich_cong_thuc_sang_html(text)
                cursor.insertHtml(html)
            else:
                cursor.insertText(text)
        elif isinstance(self.o_nhap_hien_tai, QLineEdit):
            self.o_nhap_hien_tai.insert(text)

        self.o_nhap_hien_tai.setFocus()

    @staticmethod
    def _chuyen_chuoi_sang_so_thuc(chuoi_so):
        """Chuyển đổi chuỗi số nhập tay sang float, hỗ trợ cả định dạng VN (1.000,5) và QT (1,000.5)"""
        if not chuoi_so:
            return 0.0
        s = str(chuoi_so).strip()
        if '.' in s and ',' in s:
            if s.rfind(',') > s.rfind('.'):
                s = s.replace('.', '').replace(',', '.')
            else:
                s = s.replace(',', '')
        elif ',' in s and '.' not in s:
            parts = s.split(',')
            if len(parts) == 2 and len(parts[1]) != 3:
                s = s.replace(',', '.')
            else:
                s = s.replace(',', '')
        try:
            return float(s)
        except Exception:
            return 0.0

    def kiem_tra_tinh_hop_le_cong_thuc(self):
        """
        Bộ kiểm tra cú pháp và biến số (Syntax & Variable Validator):
        1. Kiểm tra Tên quy tắc kiểm tra (không được để trống).
        2. Kiểm tra danh mục biến số:
           - Tên biến phải hợp lệ (bắt đầu bằng chữ cái/gạch dưới, không khoảng trắng hay dấu TV).
           - Không trùng tên biến, không rỗng, giá trị biến không rỗng và cân đối dấu ngoặc.
           - Không trùng với từ khóa Python.
        3. Kiểm tra Biểu thức Logic Rủi ro:
           - Chuẩn hóa bằng _chuan_hoa_bieu_thuc.
           - Kiểm tra cú pháp thông qua ast.parse(mode='eval').
           - Kiểm tra toàn bộ biến số trong AST: tất cả phải tồn tại trong bảng biến số.
        4. Kiểm tra Dữ liệu hiển thị Vế A và Vế B:
           - Tự động gợi ý/điền nếu người dùng để trống.
           - Kiểm tra cú pháp AST và tính tồn tại của biến số.

        Trả về: (hop_le: bool, thong_diep_loi: str, data_chuan_hoa: dict)
        """
        ten = self.nhap_ten_pt.text().strip()
        nhom = self.nhap_nhom.currentText().strip() or "Khác"

        if not ten:
            return False, "Vui lòng nhập Tên quy tắc kiểm tra!", {}

        # 1. Thu thập và kiểm tra danh mục biến số
        dict_bien_so = {}
        bien_pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
        python_keywords = {
            'and', 'or', 'not', 'is', 'in', 'if', 'else', 'elif', 'for', 'while',
            'def', 'class', 'import', 'from', 'as', 'return', 'pass', 'break',
            'continue', 'lambda', 'try', 'except', 'finally', 'raise', 'with',
            'yield', 'global', 'nonlocal', 'assert', 'del', 'async', 'await'
        }

        so_dong = self.bang_bien.rowCount()
        for row in range(so_dong):
            txt_ten = self.bang_bien.cellWidget(row, 0)
            txt_val = self.bang_bien.cellWidget(row, 1)
            t = txt_ten.text().strip() if txt_ten else ""
            v = self._extract_raw_formula(txt_val).strip() if txt_val else ""

            if not t and not v:
                continue

            if not t and v:
                return False, f"Dòng {row + 1} trong '1. Khai báo danh mục biến số' chưa đặt tên biến!", {}

            if t and not v:
                return False, f"Biến số '{t}' (dòng {row + 1}) chưa có công thức/chỉ tiêu tính toán!", {}

            if not bien_pattern.match(t):
                return False, (
                    f"Tên biến '{t}' không hợp lệ!\n"
                    "Tên biến phải bắt đầu bằng chữ cái hoặc gạch dưới, chỉ gồm chữ, số và dấu gạch dưới, "
                    "không chứa khoảng trắng hay dấu tiếng Việt (VD: VE_A, DOANH_THU, THUE_GTGT)."
                ), {}

            if t.lower() in python_keywords or t in {'abs', 'round', 'min', 'max'}:
                return False, f"Tên biến '{t}' trùng với từ khóa hệ thống của Python! Vui lòng đặt tên khác (VD: BIEN_{t}).", {}

            if t in dict_bien_so:
                return False, f"Tên biến '{t}' bị trùng lặp nhiều lần trong bảng biến số!", {}

            if v.count('[') != v.count(']'):
                return False, f"Công thức của biến '{t}' bị lệch dấu ngoặc vuông '[' và ']'!", {}

            dict_bien_so[t] = v

        if not dict_bien_so:
            return False, "Vui lòng khai báo ít nhất 1 biến số trong bảng '1. Khai báo danh mục biến số'!", {}

        # 2. Kiểm tra Biểu thức Logic Rủi ro
        logic_raw = self._extract_raw_formula(self.nhap_logic_rui_ro) if isinstance(
            self.nhap_logic_rui_ro, QTextEdit
        ) else self.nhap_logic_rui_ro.toPlainText().strip()

        if not logic_raw:
            return False, "Vui lòng nhập Biểu thức Logic Rủi ro (Mục 2)!", {}

        logic_clean = _chuan_hoa_bieu_thuc(logic_raw)

        try:
            tree_logic = ast.parse(logic_clean, mode='eval')
        except SyntaxError as e:
            pos_info = f" (tại vị trí ký tự {e.offset})" if e.offset else ""
            return False, f"Biểu thức Logic Rủi ro bị lỗi cú pháp:\n'{e.msg}'{pos_info}\nBiểu thức: {logic_clean}", {}
        except Exception as e:
            return False, f"Biểu thức Logic Rủi ro không hợp lệ: {e}", {}

        builtins_allowed = {'abs', 'round', 'min', 'max', '_safe_div', 'True', 'False', 'None'}
        vars_in_logic = {
            node.id for node in ast.walk(tree_logic)
            if isinstance(node, ast.Name) and node.id not in builtins_allowed
        }

        missing_logic = vars_in_logic - set(dict_bien_so.keys())
        if missing_logic:
            ds_str = ", ".join(f"'{k}'" for k in sorted(missing_logic))
            return False, (
                f"Biểu thức Logic Rủi ro sử dụng biến số chưa được khai báo:\n{ds_str}\n"
                "Vui lòng thêm các biến này vào bảng '1. Khai báo danh mục biến số' trước."
            ), {}

        # 3. Kiểm tra và đồng bộ Hiển thị Vế A và Vế B
        ht_a = self.txt_hien_thi_a.text().strip()
        ht_b = self.txt_hien_thi_b.text().strip()
        danh_sach_keys = list(dict_bien_so.keys())

        if not ht_a and len(danh_sach_keys) >= 1:
            ht_a = danh_sach_keys[0]
            self.txt_hien_thi_a.setText(ht_a)
            if not ht_b and len(danh_sach_keys) >= 2:
                ht_b = danh_sach_keys[1]
                self.txt_hien_thi_b.setText(ht_b)

        if ht_a:
            ht_a_clean = _chuan_hoa_bieu_thuc(ht_a)
            try:
                tree_a = ast.parse(ht_a_clean, mode='eval')
            except SyntaxError as e:
                return False, f"Biểu thức 'Dữ liệu hiển thị Vế Trái (A)' bị lỗi cú pháp:\n{e.msg}", {}

            vars_a = {
                node.id for node in ast.walk(tree_a)
                if isinstance(node, ast.Name) and node.id not in builtins_allowed
            }
            missing_a = vars_a - set(dict_bien_so.keys())
            if missing_a:
                ds_str = ", ".join(f"'{k}'" for k in sorted(missing_a))
                return False, f"Biểu thức Vế Trái (A) sử dụng biến chưa khai báo: {ds_str}", {}

        if ht_b:
            ht_b_clean = _chuan_hoa_bieu_thuc(ht_b)
            try:
                tree_b = ast.parse(ht_b_clean, mode='eval')
            except SyntaxError as e:
                return False, f"Biểu thức 'Dữ liệu hiển thị Vế Phải (B)' bị lỗi cú pháp:\n{e.msg}", {}

            vars_b = {
                node.id for node in ast.walk(tree_b)
                if isinstance(node, ast.Name) and node.id not in builtins_allowed
            }
            missing_b = vars_b - set(dict_bien_so.keys())
            if missing_b:
                ds_str = ", ".join(f"'{k}'" for k in sorted(missing_b))
                return False, f"Biểu thức Vế Phải (B) sử dụng biến chưa khai báo: {ds_str}", {}

        # 4. Trả về dữ liệu hợp lệ đã chuẩn hóa
        msg_rr = self.nhap_msg_rui_ro.toPlainText().strip()
        msg_at = self.nhap_msg_an_toan.toPlainText().strip()

        data_chuan_hoa = {
            "ten_phan_tich": ten,
            "nhom": nhom,
            "bien_so": dict_bien_so,
            "hien_thi_ve_a": ht_a,
            "hien_thi_ve_b": ht_b,
            "bieu_thuc_rui_ro": logic_clean,
            "thong_diep_rui_ro": msg_rr,
            "thong_diep_an_toan": msg_at
        }
        return True, "", data_chuan_hoa

    def nap_bien_vao_bang_test(self):
        """Đồng bộ danh sách biến số từ bảng 1 sang bảng chạy thử nghiệm (Sandbox)"""
        gia_tri_cu = {}
        for r in range(self.bang_test_bien.rowCount()):
            it = self.bang_test_bien.item(r, 0)
            w = self.bang_test_bien.cellWidget(r, 1)
            if it and w and isinstance(w, QLineEdit):
                gia_tri_cu[it.text().strip()] = w.text().strip()

        ds_bien = []
        for r in range(self.bang_bien.rowCount()):
            w_ten = self.bang_bien.cellWidget(r, 0)
            if w_ten and isinstance(w_ten, QLineEdit):
                t = w_ten.text().strip()
                if t and t not in ds_bien:
                    ds_bien.append(t)

        self.bang_test_bien.setRowCount(len(ds_bien))
        for r, ten_bien in enumerate(ds_bien):
            item_ten = QTableWidgetItem(f" {ten_bien}")
            item_ten.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_ten.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
            self.bang_test_bien.setItem(r, 0, item_ten)

            val_mac_dinh = gia_tri_cu.get(ten_bien)
            if val_mac_dinh is None:
                if r == 0:
                    val_mac_dinh = "1000000000"
                elif r == 1:
                    val_mac_dinh = "800000000"
                else:
                    val_mac_dinh = "1000000"

            txt_val = QLineEdit(str(val_mac_dinh))
            txt_val.setPlaceholderText("VD: 1000000 hoặc 0.8")
            txt_val.setStyleSheet("padding: 4px; font-family: Consolas; font-size: 13px; border: 1px solid #cbd5e1; border-radius: 3px;")
            self.bang_test_bien.setCellWidget(r, 1, txt_val)

    def thuc_thi_chay_thu(self):
        """Chạy thử nghiệm công thức giả lập (Sandbox Dry-Run)"""
        hop_le, loi_msg, data_clean = self.kiem_tra_tinh_hop_le_cong_thuc()
        if not hop_le:
            self.lbl_ket_qua_test.setStyleSheet(
                "background-color: #fef2f2; border: 1px solid #ef4444; border-radius: 6px; padding: 10px; color: #991b1b; font-size: 13px;"
            )
            self.lbl_ket_qua_test.setText(f"❌ <b>Lỗi kiểm tra cú pháp / biến số:</b><br>{loi_msg.replace(chr(10), '<br>')}")
            QMessageBox.warning(self, "Chưa đủ điều kiện thử nghiệm", loi_msg)
            return

        # Đồng bộ biến vào bảng test nếu bảng test chưa đủ hoặc trống
        bien_trong_test = set()
        for r in range(self.bang_test_bien.rowCount()):
            it = self.bang_test_bien.item(r, 0)
            if it:
                bien_trong_test.add(it.text().strip())
        if set(data_clean["bien_so"].keys()) != bien_trong_test:
            self.nap_bien_vao_bang_test()

        # Thu thập giá trị giả lập từ bảng test
        mock_dict = {}
        for r in range(self.bang_test_bien.rowCount()):
            it = self.bang_test_bien.item(r, 0)
            w_val = self.bang_test_bien.cellWidget(r, 1)
            if it and w_val and isinstance(w_val, QLineEdit):
                ten_b = it.text().strip()
                mock_dict[ten_b] = self._chuyen_chuoi_sang_so_thuc(w_val.text().strip())

        for k in data_clean["bien_so"]:
            if k not in mock_dict:
                mock_dict[k] = 0.0

        safe_dict = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "True": True,
            "False": False,
            "None": None
        }

        try:
            is_rui_ro = bool(safe_eval(data_clean["bieu_thuc_rui_ro"], safe_dict, mock_dict))
            ht_a = data_clean["hien_thi_ve_a"]
            ht_b = data_clean["hien_thi_ve_b"]
            val_a = float(safe_eval(ht_a, safe_dict, mock_dict)) if ht_a else 0.0
            co_ve_b = bool(ht_b)
            val_b = float(safe_eval(ht_b, safe_dict, mock_dict)) if co_ve_b else 0.0
            chenh_lech = val_a - val_b if co_ve_b else val_a
        except Exception as e_run:
            self.lbl_ket_qua_test.setStyleSheet(
                "background-color: #fef2f2; border: 1px solid #ef4444; border-radius: 6px; padding: 10px; color: #991b1b; font-size: 13px;"
            )
            self.lbl_ket_qua_test.setText(f"❌ <b>Lỗi thực thi trong sandbox:</b> {e_run}")
            return

        if is_rui_ro:
            thong_diep = data_clean["thong_diep_rui_ro"] or "Phát hiện rủi ro (Kích hoạt điều kiện)"
            badge_html = '<span style="background-color: #dc2626; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 12px;">🚨 KÍCH HOẠT CẢNH BÁO RỦI RO (TRUE)</span>'
            border_color = "#f87171"
            bg_color = "#fef2f2"
            text_color = "#991b1b"
        else:
            thong_diep = data_clean["thong_diep_an_toan"] or "An toàn / Bình thường (Không thỏa điều kiện rủi ro)"
            badge_html = '<span style="background-color: #059669; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 12px;">✅ AN TOÀN / BÌNH THƯỜNG (FALSE)</span>'
            border_color = "#86efac"
            bg_color = "#f0fdf4"
            text_color = "#065f46"

        val_a_str = dinh_dang_so_vn(val_a)
        val_b_str = dinh_dang_so_vn(val_b) if co_ve_b else "—"
        diff_str = dinh_dang_so_vn(chenh_lech)

        ve_b_rows = f"""
            <tr>
                <td style="padding: 5px 8px; color: #475569; border-bottom: 1px solid #f1f5f9;"><b>Vế Phải (B) [{ht_b}]:</b></td>
                <td style="padding: 5px 8px; font-weight: bold; color: #0284c7; text-align: right; font-family: Consolas; border-bottom: 1px solid #f1f5f9;">{val_b_str}</td>
            </tr>
            <tr>
                <td style="padding: 5px 8px; color: #475569;"><b>Chênh lệch (A - B):</b></td>
                <td style="padding: 5px 8px; font-weight: bold; color: #d97706; text-align: right; font-family: Consolas;">{diff_str}</td>
            </tr>
        """ if co_ve_b else ""

        html_card = f"""
        <div style="font-family: Segoe UI, sans-serif; line-height: 1.5;">
            <div style="margin-bottom: 8px;">{badge_html}</div>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 8px; background: white; border-radius: 4px; border: 1px solid #e2e8f0; font-size: 13px;">
                <tr>
                    <td style="padding: 5px 8px; color: #475569; width: 55%; border-bottom: 1px solid #f1f5f9;"><b>Vế Trái (A) [{ht_a}]:</b></td>
                    <td style="padding: 5px 8px; font-weight: bold; color: #dc2626; text-align: right; font-family: Consolas; border-bottom: 1px solid #f1f5f9;">{val_a_str}</td>
                </tr>
                {ve_b_rows}
            </table>
            <div style="margin-bottom: 6px; color: {text_color}; font-size: 13px;">
                <b>Thông điệp hiển thị:</b> <i>{thong_diep}</i>
            </div>
            <div style="font-size: 11px; color: #64748b; font-family: Consolas;">
                <b>Logic thực thi:</b> {data_clean['bieu_thuc_rui_ro']}
            </div>
        </div>
        """
        self.lbl_ket_qua_test.setStyleSheet(
            f"background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 6px; padding: 10px;"
        )
        self.lbl_ket_qua_test.setText(html_card)

    def luu_cong_thuc(self):
        # 1. BỘ KIỂM TRA CÚ PHÁP VÀ BIẾN SỐ (SYNTAX & VARIABLE VALIDATOR)
        hop_le, thong_bao_loi, data_rule_moi = self.kiem_tra_tinh_hop_le_cong_thuc()
        if not hop_le:
            QMessageBox.critical(self, "Không thể lưu - Cú pháp / Biến số không hợp lệ", thong_bao_loi)
            return

        data_tong = QuanLyCongThuc.tai_du_lieu_tong_hop()
        if self.ma_dang_sua:
            ma_moi = self.ma_dang_sua
        else:
            ma_moi = f"PT_{len(data_tong) + 1:02d}"
            while ma_moi in data_tong:
                ma_moi = f"PT_{int(ma_moi.split('_')[1]) + 1:02d}"

        is_luu_core = getattr(self, 'radio_luu_core', None) and self.radio_luu_core.isChecked()
        if is_luu_core:
            hoi = QMessageBox.question(self, "Xác nhận ghi vào Core",
                                       "Lưu vào Hệ thống Lõi có thể bị mất nếu Cập nhật phần mềm mới.\nTiếp tục lưu?",
                                       QMessageBox.Yes | QMessageBox.No)
            if hoi == QMessageBox.No:
                return

        thanh_cong, msg = QuanLyCongThuc.them_hoac_sua_1_rule(ma_moi, data_rule_moi, is_luu_core)
        if thanh_cong:
            QMessageBox.information(self, "Thành công", msg)
            self.chuyen_trang_danh_sach()
        else:
            QMessageBox.critical(self, "Lỗi", msg)

    def sua_cong_thuc(self, ma_pt):
        try:
            data = QuanLyCongThuc.tai_du_lieu_tong_hop()
            if ma_pt not in data: return
            cfg = data[ma_pt]
            self.ma_dang_sua = ma_pt

            self.nhap_ten_pt.setText(cfg.get("ten_phan_tich", ""))
            self.nhap_nhom.setCurrentText(cfg.get("nhom", "Khác"))
            self.nhap_msg_rui_ro.setPlainText(cfg.get("thong_diep_rui_ro", ""))
            self.nhap_msg_an_toan.setPlainText(cfg.get("thong_diep_an_toan", ""))
            self.bang_bien.setRowCount(0)

            # ========================================================
            # AUTO-MIGRATION V1 -> V2 VÀ NẠP CẤU HÌNH HIỂN THỊ
            # ========================================================
            if "bien_so" in cfg:
                # 🟢 ĐÂY LÀ RULE V2 MỚI
                for ten_b, val_b in cfg.get("bien_so", {}).items():
                    self.them_dong_bien(ten_b, val_b)
                self.nhap_logic_rui_ro.setPlainText(cfg.get("bieu_thuc_rui_ro", ""))

                # <--- MỚI BỔ SUNG: Nạp cấu hình hiển thị V2 đã lưu
                self.txt_hien_thi_a.setText(cfg.get("hien_thi_ve_a", ""))
                self.txt_hien_thi_b.setText(cfg.get("hien_thi_ve_b", ""))
            else:
                # 🟠 ĐÂY LÀ RULE V1 CŨ -> ÉP SANG UI V2 VÀ CHỈ ĐỊNH LUÔN HIỂN THỊ
                cong_thuc_cu = cfg.get("cong_thuc", "")
                dieu_kien_cu = cfg.get("dieu_kien_rui_ro", "")
                tien_de_cu = cfg.get("dieu_kien_tien_de", "")

                bieu_thuc_chot = ""
                if cong_thuc_cu.startswith("(") and ") - (" in cong_thuc_cu and cong_thuc_cu.endswith(")"):
                    # Case V1 có đủ 2 vế đối chiếu
                    loi = cong_thuc_cu[1:-1]
                    parts = loi.split(") - (")
                    if len(parts) == 2:
                        self.them_dong_bien("VE_A", parts[0].strip())
                        self.them_dong_bien("VE_B", parts[1].strip())
                        bieu_thuc_chot = f"(VE_A - VE_B) {dieu_kien_cu}"

                        # <--- MỚI BỔ SUNG: Tự động điền cấu hình báo cáo
                        self.txt_hien_thi_a.setText("VE_A")
                        self.txt_hien_thi_b.setText("VE_B")
                else:
                    # Case V1 chỉ có 1 vế tự so sánh
                    self.them_dong_bien("VE_A", cong_thuc_cu)
                    bieu_thuc_chot = f"VE_A {dieu_kien_cu}"

                    # <--- MỚI BỔ SUNG: Tự điền Vế A, bỏ trống Vế B
                    self.txt_hien_thi_a.setText("VE_A")
                    self.txt_hien_thi_b.clear()

                    # Lồng ghép điều kiện tiền đề
                if tien_de_cu:
                    bieu_thuc_chot = f"({tien_de_cu}) and ({bieu_thuc_chot})"

                self.nhap_logic_rui_ro.setPlainText(bieu_thuc_chot)
                QMessageBox.information(self, "Chuyển đổi V2",
                                        f"Công thức [{ma_pt}] (V1 cũ) đã được tự động định dạng sang V2 mới.\nHệ thống đã tự gán 'VE_A' và 'VE_B' làm dữ liệu in ra báo cáo.")

            # ========================================================
            self.lbl_tieude_form.setText(f" ĐANG SỬA QUY TẮC: {ma_pt}")
            self.btn_luu.setText(" CẬP NHẬT QUY TẮC")
            self.btn_luu.setIcon(qta.icon('fa5s.edit', color='black'))
            self.btn_luu.setStyleSheet("background-color: #f59e0b; color: black; font-weight: bold;")
            self.nap_bien_vao_bang_test()
            self.lbl_ket_qua_test.setText("Chưa chạy thử nghiệm.")
            self.lbl_ket_qua_test.setStyleSheet("background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 4px; padding: 8px; font-family: Segoe UI, sans-serif; font-size: 13px; color: #334155;")
            self.stack_chinh.setCurrentIndex(1)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không tải được dữ liệu: {e}")

    def xoa_cong_thuc(self, ma_pt):
        if QMessageBox.question(self, "Xác nhận", f"Xóa quy tắc [{ma_pt}]?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            if QuanLyCongThuc.xoa_rule(ma_pt):
                self.load_danh_sach()
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể xóa Rule này. File có thể đang bị khóa.")

    def load_danh_sach(self):
        data = QuanLyCongThuc.tai_du_lieu_tong_hop()
        self.bang_cong_thuc.setRowCount(len(data))
        for row_idx, (ma_pt, cfg) in enumerate(data.items()):
            self.bang_cong_thuc.setItem(row_idx, 0, QTableWidgetItem(ma_pt))
            self.bang_cong_thuc.setItem(row_idx, 1, QTableWidgetItem(cfg.get("nhom", "")))
            self.bang_cong_thuc.setItem(row_idx, 2, QTableWidgetItem(cfg.get("ten_phan_tich", "")))

            # Hỗ trợ hiển thị cho cả V1 và V2
            ct_ht = cfg.get("bieu_thuc_rui_ro", cfg.get("cong_thuc", ""))
            html_cong_thuc = self._dich_cong_thuc_sang_html(ct_ht)
            lbl_ct = QLabel(html_cong_thuc)
            lbl_ct.setWordWrap(True)
            lbl_ct.setStyleSheet("padding: 2px;")
            self.bang_cong_thuc.setCellWidget(row_idx, 3, lbl_ct)

            widget_thao_tac = QWidget()
            layout_thao_tac = QHBoxLayout(widget_thao_tac)
            layout_thao_tac.setContentsMargins(2, 2, 2, 2)
            layout_thao_tac.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_sua = QPushButton("")
            btn_sua.setIcon(qta.icon('fa5s.edit', color='black'))
            btn_sua.setStyleSheet("background-color: #fcd34d; border-radius: 4px; padding: 6px;")
            btn_sua.setFixedSize(32, 32)
            btn_sua.clicked.connect(lambda checked=False, ma=ma_pt: self.sua_cong_thuc(ma))

            btn_xoa = QPushButton("")
            btn_xoa.setIcon(qta.icon('fa5s.trash-alt', color='white'))
            btn_xoa.setStyleSheet("background-color: #ef4444; border-radius: 4px; padding: 6px;")
            btn_xoa.setFixedSize(32, 32)
            btn_xoa.clicked.connect(lambda checked=False, ma=ma_pt: self.xoa_cong_thuc(ma))

            layout_thao_tac.addWidget(btn_sua)
            layout_thao_tac.addWidget(btn_xoa)
            self.bang_cong_thuc.setCellWidget(row_idx, 4, widget_thao_tac)

        self.bang_cong_thuc.resizeRowsToContents()

    def loc_cong_thuc_nhanh(self, tu_khoa):
        tu_khoa = tu_khoa.strip().lower()
        so_dong = self.bang_cong_thuc.rowCount()
        for row in range(so_dong):
            co_chua_tu_khoa = False
            for col in range(4):
                item = self.bang_cong_thuc.item(row, col)
                if item and tu_khoa in item.text().lower():
                    co_chua_tu_khoa = True
                elif col == 3:
                    widget = self.bang_cong_thuc.cellWidget(row, col)
                    if widget and tu_khoa in widget.text().lower(): co_chua_tu_khoa = True
            self.bang_cong_thuc.setRowHidden(row, not co_chua_tu_khoa)

    def tai_du_lieu_tu_dien_len_cay(self):
        node_hoa_don = QTreeWidgetItem(self.cay_du_lieu, ["1. DỮ LIỆU BẢNG KÊ HÓA ĐƠN"])
        node_hoa_don.setIcon(0, qta.icon('fa5s.file-excel', color='#10b981'))
        cac_cot_hd = set()
        try:
            with open("Data/master_data_map.json", 'r', encoding='utf-8') as f:
                for config_list in json.load(f).values():
                    for item in config_list:
                        if std_name := item.get("Standard_Column_Name"): cac_cot_hd.add(std_name)
        except Exception:
            cac_cot_hd = {"ThanhTien", "TongTienChuaThue", "TongTienThue"}

        node_ban_ra = QTreeWidgetItem(node_hoa_don, ["Hóa đơn Bán ra"])
        node_ban_ra.setIcon(0, qta.icon('fa5s.file-export', color='#059669'))
        node_mua_vao = QTreeWidgetItem(node_hoa_don, ["Hóa đơn Mua vào"])
        node_mua_vao.setIcon(0, qta.icon('fa5s.file-import', color='#059669'))

        for cot in sorted(cac_cot_hd):
            item_br = QTreeWidgetItem(node_ban_ra, [f"Cộng cột: {cot}", f"SUM[HD_BAN_RA | {cot}]"])
            item_br.setIcon(0, qta.icon('fa5s.plus-circle', color='#64748b'))
            item_mv = QTreeWidgetItem(node_mua_vao, [f"Cộng cột: {cot}", f"SUM[HD_MUA_VAO | {cot}]"])
            item_mv.setIcon(0, qta.icon('fa5s.plus-circle', color='#64748b'))

        node_to_khai = QTreeWidgetItem(self.cay_du_lieu, ["2. TỜ KHAI THUẾ KỲ (XML)"])
        node_to_khai.setIcon(0, qta.icon('fa5s.file-code', color='#3b82f6'))

        for ma_form, data_form in TU_DIEN_TO_KHAI.items():
            if "BCTC" in ma_form or "CDTK" in ma_form: continue
            node_tk_chi_tiet = QTreeWidgetItem(node_to_khai, [f"[{ma_form}] {MAP_TEN_TO_KHAI.get(ma_form, ma_form)}"])
            node_tk_chi_tiet.setIcon(0, qta.icon('fa5s.file-alt', color='#2563eb'))

            for key_cap_2, val_cap_2 in data_form.items():
                if isinstance(val_cap_2, dict):
                    node_pl = QTreeWidgetItem(node_tk_chi_tiet, [f"Phân hệ: {key_cap_2}"])
                    node_pl.setIcon(0, qta.icon('fa5s.folder-open', color='#3b82f6'))
                    nhom_hien_thi = "ChiTieuChinh" if key_cap_2 == "ToKhaiChinh" else key_cap_2
                    for ma_ct, ten_ct in val_cap_2.items():
                        item_ct = QTreeWidgetItem(node_pl,
                                                  [f"[{ma_ct}] - {ten_ct}", f"[{ma_form} | {nhom_hien_thi} | {ma_ct}]"])
                        item_ct.setIcon(0, qta.icon('fa5s.tag', color='#64748b'))
                elif isinstance(val_cap_2, str):
                    item_ct_phang = QTreeWidgetItem(node_tk_chi_tiet, [f"[{key_cap_2}] - {val_cap_2}",
                                                                       f"[{ma_form} | ChiTieuChinh | {key_cap_2}]"])
                    item_ct_phang.setIcon(0, qta.icon('fa5s.tag', color='#64748b'))

        node_bctc = QTreeWidgetItem(self.cay_du_lieu, ["3. BÁO CÁO TÀI CHÍNH"])
        node_bctc.setIcon(0, qta.icon('fa5s.chart-pie', color='#f59e0b'))

        tt133_cdkt = ["110", "120", "121", "122", "123", "124", "130", "131", "132", "133", "134", "135", "136", "140",
                      "141", "142", "150", "151", "152", "160", "161", "162", "170", "180", "181", "182", "200", "300",
                      "311", "312", "313", "314", "315", "316", "317", "318", "319", "320", "400", "411", "412", "413",
                      "414", "415", "416", "417", "500"]
        tt133_kqkd = ["01", "02", "10", "11", "20", "21", "22", "23", "24", "30", "31", "32", "40", "50", "51", "60"]
        tt133_lctt = ["01", "02", "03", "04", "05", "06", "07", "20", "21", "22", "23", "24", "25", "30", "31", "32",
                      "33", "34", "35", "40", "50", "60", "61", "70"]
        tt133_cdtk = ["111", "1111", "1112", "112", "1121", "1122", "121", "128", "1281", "1288", "131", "133", "1331",
                      "1332", "136", "1361", "1368", "138", "1381", "1386", "1388", "141", "151", "152", "153", "154",
                      "155", "156", "157", "211", "2111", "2112", "2113", "214", "2141", "2142", "2143", "2147", "217",
                      "228", "2281", "2288", "229", "2291", "2292", "2293", "2294", "241", "2411", "2412", "2413",
                      "242", "331", "333", "3331", "33311", "33312", "3332", "3333", "3334", "3335", "3336", "3337",
                      "3338", "33381", "33382", "3339", "334", "335", "336", "3361", "3368", "338", "3381", "3382",
                      "3383", "3384", "3385", "3386", "3387", "3388", "341", "3411", "3412", "352", "3521", "3522",
                      "3524", "353", "3531", "3532", "3533", "3534", "356", "3561", "3562", "411", "4111", "4112",
                      "4118", "413", "418", "419", "421", "4211", "4212", "511", "5111", "5112", "5113", "5118", "515",
                      "611", "631", "632", "635", "642", "6421", "6422", "711", "811", "821", "911"]

        tt200_cdkt = ["100", "110", "111", "112", "120", "121", "122", "123", "130", "131", "132", "133", "134", "135",
                      "136", "137", "139", "140", "141", "149", "150", "151", "152", "153", "154", "155", "200", "210",
                      "211", "212", "213", "214", "215", "216", "219", "220", "221", "222", "223", "224", "225", "226",
                      "227", "228", "229", "230", "231", "232", "240", "241", "242", "250", "251", "252", "253", "254",
                      "255", "260", "261", "262", "263", "268", "270", "300", "310", "311", "312", "313", "314", "315",
                      "316", "317", "318", "319", "320", "321", "322", "323", "324", "330", "331", "332", "333", "334",
                      "335", "336", "337", "338", "339", "340", "341", "342", "343", "400", "410", "411", "411a",
                      "411b", "412", "413", "414", "415", "416", "417", "418", "419", "420", "421", "421a", "421b",
                      "422", "430", "431", "432", "440"]
        tt200_kqkd = ["01", "02", "10", "11", "20", "21", "22", "23", "25", "26", "30", "31", "32", "40", "50", "51",
                      "52", "60", "70", "71"]
        tt200_lctt = ["01", "02", "03", "04", "05", "06", "07", "20", "21", "22", "23", "24", "25", "26", "27", "30",
                      "31", "32", "33", "34", "35", "36", "40", "50", "60", "61", "70"]

        def add_ph(parent, icon, title):
            n = QTreeWidgetItem(parent, [title])
            n.setIcon(0, qta.icon(icon, color='#0284c7'))
            return n

        def add_ct(parent, txt, tag):
            n = QTreeWidgetItem(parent, [txt, tag])
            n.setIcon(0, qta.icon('fa5s.tag', color='#64748b'))

        def lay_ten_bctc(tt_key, ph_key, ma_ct):
            ten = TU_DIEN_TO_KHAI.get(tt_key, {}).get(ph_key, {}).get(f"ct{ma_ct}", f"[ct{ma_ct}]")
            if len(ten) > 60: ten = ten[:60] + "..."
            return f"[{ma_ct}] - {ten}"

        node_133 = QTreeWidgetItem(node_bctc, ["Báo cáo tài chính (TT133/2016/TT-BTC)"])
        node_133.setIcon(0, qta.icon('fa5s.folder', color='#d97706'))

        n_cdkt = add_ph(node_133, 'fa5s.balance-scale', "Bảng Cân đối kế toán (B01a-DNN)")
        n_cdkt_c = add_ph(n_cdkt, 'fa5s.calendar-check', "Số Cuối Năm")
        n_cdkt_d = add_ph(n_cdkt, 'fa5s.calendar-minus', "Số Đầu Năm")
        for ct in tt133_cdkt:
            ten_ct = lay_ten_bctc("BCTC_TT133", "B01_CDKT", ct)
            add_ct(n_cdkt_c, ten_ct, f"[BCTC_TT133 | CDKT_SoCuoiNam | ct{ct}]")
            add_ct(n_cdkt_d, ten_ct, f"[BCTC_TT133 | CDKT_SoDauNam | ct{ct}]")

        n_kqkd = add_ph(node_133, 'fa5s.chart-line', "Kết quả Hoạt động SXKD (B02-DNN)")
        n_kqkd_n = add_ph(n_kqkd, 'fa5s.calendar-check', "Năm Nay")
        n_kqkd_t = add_ph(n_kqkd, 'fa5s.calendar-minus', "Năm Trước")
        for ct in tt133_kqkd:
            ten_ct = lay_ten_bctc("BCTC_TT133", "B02_KQKD", ct)
            add_ct(n_kqkd_n, ten_ct, f"[BCTC_TT133 | KQKD_NamNay | ct{ct}]")
            add_ct(n_kqkd_t, ten_ct, f"[BCTC_TT133 | KQKD_NamTruoc | ct{ct}]")

        n_lctt = add_ph(node_133, 'fa5s.exchange-alt', "Lưu chuyển tiền tệ (B03-DNN)")
        n_lctt_n = add_ph(n_lctt, 'fa5s.calendar-check', "Năm Nay")
        n_lctt_t = add_ph(n_lctt, 'fa5s.calendar-minus', "Năm Trước")
        for ct in tt133_lctt:
            ten_ct = lay_ten_bctc("BCTC_TT133", "B03_LCTT_TT", ct)
            add_ct(n_lctt_n, ten_ct, f"[BCTC_TT133 | LCTT_NamNay | ct{ct}]")
            add_ct(n_lctt_t, ten_ct, f"[BCTC_TT133 | LCTT_NamTruoc | ct{ct}]")

        n_cdtk = add_ph(node_133, 'fa5s.book', "Bảng Cân đối tài khoản - (F01-DNN)")
        for tk in tt133_cdtk:
            tk_name = f"Tài khoản {tk}"
            try:
                tk_name = TU_DIEN_TO_KHAI.get("BCTC_TT133", {}).get("B04_CDTK", {}).get(f"ct{tk}", tk_name)
            except:
                pass
            n_tk = add_ph(n_cdtk, 'fa5s.bookmark', tk_name)
            n_tk.setIcon(0, qta.icon('fa5s.bookmark', color='#64748b'))
            add_ct(n_tk, "Dư Nợ Đầu Kỳ", f"[BCTC_TT133 | CDTK_NoDauKy | ct{tk}]")
            add_ct(n_tk, "Dư Có Đầu Kỳ", f"[BCTC_TT133 | CDTK_CoDauKy | ct{tk}]")
            add_ct(n_tk, "Phát sinh Nợ Trong Kỳ", f"[BCTC_TT133 | CDTK_NoPhatSinh | ct{tk}]")
            add_ct(n_tk, "Phát sinh Có Trong Kỳ", f"[BCTC_TT133 | CDTK_CoPhatSinh | ct{tk}]")
            add_ct(n_tk, "Dư Nợ Cuối Kỳ", f"[BCTC_TT133 | CDTK_NoCuoiKy | ct{tk}]")
            add_ct(n_tk, "Dư Có Cuối Kỳ", f"[BCTC_TT133 | CDTK_CoCuoiKy | ct{tk}]")

        node_200 = QTreeWidgetItem(node_bctc, ["Báo cáo tài chính (TT200/2014/TT-BTC)"])
        node_200.setIcon(0, qta.icon('fa5s.folder', color='#d97706'))

        n2_cdkt = add_ph(node_200, 'fa5s.balance-scale', "Bảng Cân đối kế toán")
        n2_cdkt_c = add_ph(n2_cdkt, 'fa5s.calendar-check', "Số Cuối Năm")
        n2_cdkt_d = add_ph(n2_cdkt, 'fa5s.calendar-minus', "Số Đầu Năm")
        for ct in tt200_cdkt:
            ten_ct = lay_ten_bctc("BCTC_TT200", "B01_CDKT", ct)
            add_ct(n2_cdkt_c, ten_ct, f"[BCTC_TT200 | CDKT_SoCuoiNam | ct{ct}]")
            add_ct(n2_cdkt_d, ten_ct, f"[BCTC_TT200 | CDKT_SoDauNam | ct{ct}]")

        n2_kqkd = add_ph(node_200, 'fa5s.chart-line', "Kết quả Hoạt động SXKD")
        n2_kqkd_n = add_ph(n2_kqkd, 'fa5s.calendar-check', "Năm Nay")
        n2_kqkd_t = add_ph(n2_kqkd, 'fa5s.calendar-minus', "Năm Trước")
        for ct in tt200_kqkd:
            ten_ct = lay_ten_bctc("BCTC_TT200", "B02_KQKD", ct)
            add_ct(n2_kqkd_n, ten_ct, f"[BCTC_TT200 | KQKD_NamNay | ct{ct}]")
            add_ct(n2_kqkd_t, ten_ct, f"[BCTC_TT200 | KQKD_NamTruoc | ct{ct}]")

        n2_lctt = add_ph(node_200, 'fa5s.exchange-alt', "Lưu chuyển tiền tệ")
        n2_lctt_n = add_ph(n2_lctt, 'fa5s.calendar-check', "Năm Nay")
        n2_lctt_t = add_ph(n2_lctt, 'fa5s.calendar-minus', "Năm Trước")
        for ct in tt200_lctt:
            ten_ct = lay_ten_bctc("BCTC_TT200", "B03_LCTT_TT", ct)
            add_ct(n2_lctt_n, ten_ct, f"[BCTC_TT200 | LCTT_NamNay | ct{ct}]")
            add_ct(n2_lctt_t, ten_ct, f"[BCTC_TT200 | LCTT_NamTruoc | ct{ct}]")

        n2_cdtk = add_ph(node_200, 'fa5s.book', "Bảng Cân đối Số phát sinh")
        for tk, tk_name_goc in TU_DIEN_TK_TT200.items():
            tk_name = f"Tài khoản {tk} - {tk_name_goc}"
            n_tk = add_ph(n2_cdtk, 'fa5s.bookmark', tk_name)
            n_tk.setIcon(0, qta.icon('fa5s.bookmark', color='#64748b'))
            add_ct(n_tk, "Dư Nợ Đầu Kỳ", f"[BCTC_TT200 | CDTK_DuNoDauKy | ct{tk}]")
            add_ct(n_tk, "Dư Có Đầu Kỳ", f"[BCTC_TT200 | CDTK_DuCoDauKy | ct{tk}]")
            add_ct(n_tk, "Phát sinh Nợ Trong Kỳ", f"[BCTC_TT200 | CDTK_PhatSinhNo | ct{tk}]")
            add_ct(n_tk, "Phát sinh Có Trong Kỳ", f"[BCTC_TT200 | CDTK_PhatSinhCo | ct{tk}]")
            add_ct(n_tk, "Dư Nợ Cuối Kỳ", f"[BCTC_TT200 | CDTK_DuNoCuoiKy | ct{tk}]")
            add_ct(n_tk, "Dư Có Cuối Kỳ", f"[BCTC_TT200 | CDTK_DuCoCuoiKy | ct{tk}]")

    def loi_tim_kiem(self, text):
        text = text.lower()

        def duyet_node(node):
            match = text in node.text(0).lower() or text in node.text(1).lower()
            for i in range(node.childCount()):
                if duyet_node(node.child(i)): match = True
            node.setHidden(not match and text != "")
            if text != "": node.setExpanded(True)
            return match

        for i in range(self.cay_du_lieu.topLevelItemCount()): duyet_node(self.cay_du_lieu.topLevelItem(i))

    def khoi_phuc_cong_thuc(self):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QPushButton, QLabel, QHBoxLayout, QMessageBox
        dialog = QDialog(self)
        dialog.setWindowTitle("Tùy chọn Khôi phục")
        dialog.resize(500, 240)
        dialog.setStyleSheet("QDialog { background-color: #FFFFFF; }")

        layout = QVBoxLayout(dialog)
        lbl_cau_hoi = QLabel("Bạn muốn khôi phục hệ thống theo mức độ nào?")
        lbl_cau_hoi.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px;")
        layout.addWidget(lbl_cau_hoi)

        style_the_an_toan = """
            QRadioButton { background-color: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px 15px; font-size: 14px; font-weight: bold; color: #1E3A8A; }
            QRadioButton:hover { background-color: #EFF6FF; border: 1px solid #93C5FD; }
            QRadioButton:checked { background-color: #EFF6FF; border: 2px solid #2563EB; }
            QRadioButton::indicator { width: 14px; height: 14px; border-radius: 8px; border: 2px solid #94A3B8; background-color: white; margin-right: 8px; }
            QRadioButton::indicator:checked { border: 4px solid #2563EB; background-color: white; }
        """
        style_the_nguy_hiem = """
            QRadioButton { background-color: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; padding: 12px 15px; font-size: 14px; font-weight: bold; color: #DC2626; }
            QRadioButton:hover { background-color: #FEE2E2; border: 1px solid #FCA5A5; }
            QRadioButton:checked { background-color: #FEF2F2; border: 2px solid #DC2626; }
            QRadioButton::indicator { width: 14px; height: 14px; border-radius: 8px; border: 2px solid #FCA5A5; background-color: white; margin-right: 8px; }
            QRadioButton::indicator:checked { border: 4px solid #DC2626; background-color: white; }
        """
        rdo_chi_khoi_phuc_goc = QRadioButton(" 1. Chỉ khôi phục Rule mặc định (Khuyên dùng)")
        rdo_chi_khoi_phuc_goc.setChecked(True)
        rdo_chi_khoi_phuc_goc.setStyleSheet(style_the_an_toan)

        rdo_xoa_sach = QRadioButton(" 2. Xóa sạch toàn bộ (Khôi phục cài đặt gốc)")
        rdo_xoa_sach.setStyleSheet(style_the_nguy_hiem)

        layout.addWidget(rdo_chi_khoi_phuc_goc)
        layout.addWidget(rdo_xoa_sach)
        layout.addSpacing(15)

        khung_btn = QHBoxLayout()
        btn_huy = QPushButton("Hủy bỏ")
        btn_huy.setStyleSheet("padding: 8px 20px; font-size: 13px; font-weight: bold;")
        btn_huy.clicked.connect(dialog.reject)

        btn_xac_nhan = QPushButton(" Thực hiện Khôi phục")
        btn_xac_nhan.setIcon(qta.icon('fa5s.sync', color='white'))
        btn_xac_nhan.setStyleSheet(
            "background-color: #F59E0B; color: white; font-weight: bold; padding: 8px 20px; font-size: 13px; border-radius: 4px;")

        def xac_nhan_khoi_phuc():
            xoa_sach = rdo_xoa_sach.isChecked()
            thanh_cong, msg = QuanLyCongThuc.khoi_phuc_mac_dinh(xoa_sach_toan_bo=xoa_sach)
            dialog.accept()
            if thanh_cong:
                QMessageBox.information(self, "Thành công", msg)
                self.load_danh_sach()
            else:
                QMessageBox.critical(self, "Lỗi", msg)

        btn_xac_nhan.clicked.connect(xac_nhan_khoi_phuc)
        khung_btn.addStretch()
        khung_btn.addWidget(btn_huy)
        khung_btn.addWidget(btn_xac_nhan)
        layout.addLayout(khung_btn)
        dialog.exec()