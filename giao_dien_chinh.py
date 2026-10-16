from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QStackedWidget, QLabel, QSplitter, QFrame,
                               QListWidget, QTabWidget, QTableWidget, QTableWidgetItem, QComboBox, QCheckBox, QTextEdit,
                               QHeaderView,
                               QTabBar, QFileDialog, QMessageBox,QSplitter)
from PySide6.QtCore import Qt, QSize, QThread, Signal
import qtawesome as qta

from cau_hinh_giao_dien import lay_style_xanh_nuoc_bien
from module_giao_dien.giao_dien_bao_cao import WidgetBaoCaoDoanhSo
from PySide6.QtCore import Qt, QSize, QThread, Signal, QTimer
# NHỚ IMPORT CỖ MÁY RỦI RO VÀO ĐÂY
from module_doc_hoadon.hoadon_ruiro import HoaDonRuiRoManager
import os
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from module_giao_dien.giao_dien_gop_y import DialogGopY
from PySide6.QtGui import QMovie
from module_giao_dien.ui_web_effects import tao_bong_do_web, TheKPIWeb, VungKeoThaWeb

class GiaoDienChinh(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ứng Dụng Phân Tích Hồ Sơ Khai Thuế")
        self.resize(1250, 850)
        self.setStyleSheet(lay_style_xanh_nuoc_bien())

        # Khởi động cỗ máy rủi ro ngầm
        self.ruiro_mgr = HoaDonRuiRoManager()

        self.thiet_lap_giao_dien()

    def thiet_lap_giao_dien(self):
        widget_trung_tam = QWidget()
        self.setCentralWidget(widget_trung_tam)
        layout_chinh = QVBoxLayout(widget_trung_tam)
        layout_chinh.setContentsMargins(0, 0, 0, 0)

        bo_chia = QSplitter(Qt.Horizontal)
        bo_chia.setStyleSheet("QSplitter::handle { background-color: transparent; }")
        layout_chinh.addWidget(bo_chia)

        # =========================================================
        # --- KHỐI BÊN TRÁI: MENU ĐIỀU HƯỚNG DỌC ---
        # =========================================================
        self.khung_trai = QFrame()
        self.khung_trai.setObjectName("KhungTrai")
        layout_trai = QVBoxLayout(self.khung_trai)
        layout_trai.setContentsMargins(0, 16, 0, 16)
        layout_trai.setSpacing(4)

        # 1. LOGO / BRANDING Ở ĐỈNH MENU
        self.khung_brand = QFrame()
        self.khung_brand.setStyleSheet("background: transparent; border: none; padding: 0 16px 12px 16px; border-bottom: 1px solid #E2E8F0;")
        layout_brand = QVBoxLayout(self.khung_brand)
        layout_brand.setContentsMargins(0, 0, 0, 0)
        layout_brand.setSpacing(2)

        lbl_brand = QLabel("RRR TAX PRO")
        lbl_brand.setStyleSheet("font-size: 15px; font-weight: 800; color: #1E3A8A; letter-spacing: 0.5px;")

        lbl_brand_sub = QLabel("Phân tích Rủi ro Thuế")
        lbl_brand_sub.setStyleSheet("font-size: 11px; font-weight: 600; color: #64748B;")

        layout_brand.addWidget(lbl_brand)
        layout_brand.addWidget(lbl_brand_sub)
        layout_trai.addWidget(self.khung_brand)

        # 2. CÁC NÚT QUY TRÌNH PHÂN TÍCH CHÍNH (MAIN WORKFLOW)
        self.btn_tab_chuan_bi = QPushButton("  Chuẩn bị Dữ liệu")
        self.btn_tab_chuan_bi.setIcon(qta.icon('fa5s.folder-open', color='#2563EB'))

        self.btn_tab_kq_to_khai = QPushButton("  Tổng hợp Tờ khai")
        self.btn_tab_kq_to_khai.setIcon(qta.icon('fa5s.file-invoice', color='#059669'))

        self.btn_tab_kq_hoa_don = QPushButton("  Kết quả Hóa đơn")
        self.btn_tab_kq_hoa_don.setIcon(qta.icon('fa5s.receipt', color='#D97706'))

        self.btn_tab_rui_ro = QPushButton("  Quản lý Rủi ro")
        self.btn_tab_rui_ro.setIcon(qta.icon('fa5s.shield-alt', color='#DC2626'))

        self.btn_tab_kq_phan_tich = QPushButton("  Kết quả Phân tích")
        self.btn_tab_kq_phan_tich.setIcon(qta.icon('fa5s.chart-line', color='#7C3AED'))

        self.danh_sach_btn = [
            self.btn_tab_chuan_bi,
            self.btn_tab_kq_to_khai,
            self.btn_tab_kq_hoa_don,
            self.btn_tab_rui_ro,
            self.btn_tab_kq_phan_tich
        ]

        for btn in self.danh_sach_btn:
            btn.setProperty("class", "TabButton")
            btn.setCheckable(True)
            layout_trai.addWidget(btn)

        # 3. PHÂN VÙNG TỰ ĐỘNG HÓA & TRỢ GIÚP
        self.lbl_section_tools = QLabel("CÔNG CỤ NÂNG CAO")
        self.lbl_section_tools.setStyleSheet("font-size: 10px; font-weight: bold; color: #94A3B8; padding: 12px 0 4px 16px; letter-spacing: 0.5px;")
        layout_trai.addWidget(self.lbl_section_tools)

        self.btn_mo_auto_bot = QPushButton("  Phân tích tự động")
        self.btn_mo_auto_bot.setIcon(qta.icon('fa5s.robot', color='#7C3AED'))
        self.btn_mo_auto_bot.setStyleSheet("""
            QPushButton {
                text-align: left; padding: 10px 14px; font-weight: 700; color: #6D28D9;
                background-color: #F5F3FF; border: 1px solid #DDD6FE; border-radius: 8px;
                margin: 2px 10px; font-size: 13px;
            }
            QPushButton:hover { background-color: #EDE9FE; border-color: #C4B5FD; color: #5B21B6; }
        """)
        layout_trai.addWidget(self.btn_mo_auto_bot)

        self.btn_tab_huong_dan = QPushButton("  Hướng dẫn sử dụng")
        self.btn_tab_huong_dan.setIcon(qta.icon('fa5s.book-open', color='#0284C7'))
        self.btn_tab_huong_dan.setProperty("class", "TabButton")
        self.btn_tab_huong_dan.setCheckable(True)
        self.danh_sach_btn.append(self.btn_tab_huong_dan)
        layout_trai.addWidget(self.btn_tab_huong_dan)

        # 4. GẮN TÍN HIỆU ĐIỀU HƯỚNG
        self.btn_tab_chuan_bi.clicked.connect(lambda: self.chuyen_trang(self.btn_tab_chuan_bi, self.tabs_chuan_bi))
        self.btn_tab_kq_to_khai.clicked.connect(lambda: self.chuyen_trang(self.btn_tab_kq_to_khai, self.trang_tong_hop_tk))
        self.btn_tab_kq_hoa_don.clicked.connect(lambda: self.chuyen_trang(self.btn_tab_kq_hoa_don, self.trang_kq_hd))
        self.btn_tab_rui_ro.clicked.connect(lambda: self.chuyen_trang(self.btn_tab_rui_ro, self.trang_quan_ly_rui_ro))
        self.btn_tab_kq_phan_tich.clicked.connect(lambda: self.chuyen_trang(self.btn_tab_kq_phan_tich, self.trang_kq_phan_tich))
        self.btn_tab_huong_dan.clicked.connect(lambda: self.chuyen_trang(self.btn_tab_huong_dan, self.trang_huong_dan))
        self.btn_tab_chuan_bi.setChecked(True)

        layout_trai.addStretch()

        # 5. KHU VỰC CHÂN SIDEBAR (STATUS & ACTION)
        self.khung_user_status = QFrame()
        self.khung_user_status.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC; 
                border: 1px solid #E2E8F0; 
                border-radius: 8px; 
                margin: 4px 10px; 
                padding: 6px 10px;
            }
        """)
        layout_us = QHBoxLayout(self.khung_user_status)
        layout_us.setContentsMargins(0, 0, 0, 0)
        layout_us.setSpacing(8)

        lbl_avt = QLabel()
        lbl_avt.setPixmap(qta.icon('fa5s.user-shield', color='#2563EB').pixmap(14, 14))
        lbl_avt.setStyleSheet("background: transparent; border: none;")

        lbl_user_txt = QLabel("Chuyên viên Thuế")
        lbl_user_txt.setStyleSheet("color: #334155; font-size: 11px; font-weight: 700; background: transparent; border: none;")

        lbl_dot = QLabel("●")
        lbl_dot.setStyleSheet("color: #10B981; font-size: 10px; background: transparent; border: none;")

        layout_us.addWidget(lbl_avt)
        layout_us.addWidget(lbl_user_txt)
        layout_us.addWidget(lbl_dot)
        layout_us.addStretch()
        layout_trai.addWidget(self.khung_user_status)

        self.btn_gop_y = QPushButton("  Góp ý / Báo lỗi")
        self.btn_gop_y.setIcon(qta.icon('fa5s.comment-dots', color='#D97706'))
        self.btn_gop_y.setStyleSheet("""
            QPushButton {
                text-align: left; padding: 9px 14px; font-weight: 600; color: #475569;
                background-color: transparent; border: none; border-radius: 6px; margin: 2px 10px; font-size: 12px;
            }
            QPushButton:hover { background-color: #FEF3C7; color: #B45309; }
        """)
        self.btn_gop_y.clicked.connect(self.mo_dialog_gop_y)
        layout_trai.addWidget(self.btn_gop_y)

        self.btn_thu_gon = QPushButton("  Thu gọn menu")
        self.btn_thu_gon.setIcon(qta.icon('fa5s.angle-double-left', color='#64748B'))
        self.btn_thu_gon.setIconSize(QSize(16, 16))
        self.btn_thu_gon.setObjectName("BtnThuGon")
        self.btn_thu_gon.clicked.connect(self.thu_gon_menu)
        layout_trai.addWidget(self.btn_thu_gon)

        # =========================================================
        # --- KHỐI BÊN PHẢI: NGĂN XẾP HIỂN THỊ (STACK) ---
        # =========================================================
        self.khung_phai = QStackedWidget()

        # TAB 0: CHUẨN BỊ DỮ LIỆU
        self.tabs_chuan_bi = QTabWidget()
        self.tabs_chuan_bi.setTabsClosable(True)
        self.tabs_chuan_bi.tabCloseRequested.connect(self.dong_tab_chuan_bi)

        trang_chuan_bi = QWidget()
        layout_chuan_bi = QVBoxLayout(trang_chuan_bi)
        layout_chuan_bi.setContentsMargins(18, 16, 18, 16)
        layout_chuan_bi.setSpacing(16)

        # =========================================================
        # 1. HERO BANNER WEB SAAS (DEEP SLATE GRADIENT & GLOW ACCENTS)
        # =========================================================
        header_frame = QFrame()
        header_frame.setFixedHeight(68)
        header_frame.setStyleSheet("""
            QFrame { 
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #0F172A, stop:0.65 #1E3A8A, stop:1 #2563EB); 
                border: 1px solid #1E293B; 
                border-radius: 12px; 
            }
        """)
        tao_bong_do_web(header_frame, blur_radius=20, offset_y=4, alpha=22)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(14)

        icon_hero_box = QFrame()
        icon_hero_box.setFixedSize(40, 40)
        icon_hero_box.setStyleSheet("background-color: rgba(255, 255, 255, 0.12); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2);")
        layout_hero_ic = QVBoxLayout(icon_hero_box)
        layout_hero_ic.setContentsMargins(0, 0, 0, 0)
        lbl_icon_head = QLabel()
        lbl_icon_head.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon_head.setPixmap(qta.icon('fa5s.chart-line', color='#60A5FA').pixmap(20, 20))
        lbl_icon_head.setStyleSheet("background: transparent; border: none;")
        layout_hero_ic.addWidget(lbl_icon_head)
        header_layout.addWidget(icon_hero_box)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_title = QLabel("HỆ THỐNG PHÂN TÍCH RỦI RO HỒ SƠ KHAI THUẾ")
        lbl_title.setStyleSheet("""
            background: transparent; 
            border: none; 
            color: #FFFFFF; 
            font-weight: 800; 
            font-size: 15px; 
            letter-spacing: 0.5px;
        """)
        lbl_subhead = QLabel("Kiểm tra chéo tờ khai, hóa đơn điện tử & Báo cáo tài chính theo chuẩn ngành Thuế")
        lbl_subhead.setStyleSheet("""
            background: transparent; 
            border: none; 
            color: #93C5FD; 
            font-size: 11px; 
            font-weight: 500;
        """)
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_subhead)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        pill_status = QLabel("● Sẵn sàng phân tích")
        pill_status.setStyleSheet("""
            background-color: rgba(16, 185, 129, 0.15); 
            color: #34D399; 
            font-size: 11px; 
            font-weight: 700;
            padding: 5px 12px;
            border-radius: 12px;
            border: 1px solid rgba(52, 211, 153, 0.3);
        """)
        header_layout.addWidget(pill_status)

        lbl_version = QLabel("PRO 4.2")
        lbl_version.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.18); 
            color: #FFFFFF; 
            font-size: 11px; 
            font-weight: 800;
            padding: 5px 12px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.25);
            letter-spacing: 0.5px;
        """)
        header_layout.addWidget(lbl_version)
        layout_chuan_bi.addWidget(header_frame)

        # =========================================================
        # 1.1 HÀNG THẺ KPI METRIC TRẠNG THÁI (WEB SAAS STATS)
        # =========================================================
        khung_kpi_chuan_bi = QHBoxLayout()
        khung_kpi_chuan_bi.setSpacing(14)

        self.kpi_to_khai = TheKPIWeb(
            tieu_de="Tờ khai đã nạp", 
            gia_tri="0", 
            subtext="Chưa có file XML", 
            icon_name="fa5s.file-code", 
            icon_color="#2563EB", 
            bg_icon="#EFF6FF", 
            badge_text="XML"
        )
        self.kpi_hd_ban = TheKPIWeb(
            tieu_de="HĐ Bán ra", 
            gia_tri="0", 
            subtext="Chưa nạp hóa đơn", 
            icon_name="fa5s.file-invoice-dollar", 
            icon_color="#059669", 
            bg_icon="#ECFDF5", 
            badge_text="Doanh thu",
            badge_color="#ECFDF5",
            badge_text_color="#047857"
        )
        self.kpi_hd_mua = TheKPIWeb(
            tieu_de="HĐ Mua vào", 
            gia_tri="0", 
            subtext="Chưa nạp hóa đơn", 
            icon_name="fa5s.shopping-cart", 
            icon_color="#D97706", 
            bg_icon="#FEF3C7", 
            badge_text="Chi phí",
            badge_color="#FEF3C7",
            badge_text_color="#B45309"
        )
        self.kpi_trang_thai = TheKPIWeb(
            tieu_de="Trạng thái", 
            gia_tri="Sẵn sàng", 
            subtext="Chờ lệnh khởi chạy", 
            icon_name="fa5s.shield-alt", 
            icon_color="#7C3AED", 
            bg_icon="#F5F3FF", 
            badge_text="Hệ thống",
            badge_color="#F5F3FF",
            badge_text_color="#6D28D9"
        )

        khung_kpi_chuan_bi.addWidget(self.kpi_to_khai)
        khung_kpi_chuan_bi.addWidget(self.kpi_hd_ban)
        khung_kpi_chuan_bi.addWidget(self.kpi_hd_mua)
        khung_kpi_chuan_bi.addWidget(self.kpi_trang_thai)
        layout_chuan_bi.addLayout(khung_kpi_chuan_bi)

        # =========================================================
        # 2. KHU VỰC THAO TÁC CHÍNH (TOP CARDS)
        # =========================================================
        vung_thao_tac_top = QHBoxLayout()
        vung_thao_tac_top.setSpacing(16)

        # --- CARD 1: NẠP DỮ LIỆU ĐẦU VÀO VỚI DROP-ZONE HIỆN ĐẠI ---
        card_nap_du_lieu = QFrame()
        card_nap_du_lieu.setProperty("class", "CardWidget")
        tao_bong_do_web(card_nap_du_lieu, blur_radius=16, offset_y=3, alpha=14)
        layout_nap = QVBoxLayout(card_nap_du_lieu)
        layout_nap.setContentsMargins(16, 16, 16, 16)
        layout_nap.setSpacing(10)

        lbl_nap = QLabel("1. Tải lên Tờ khai thuế & Hóa đơn")
        lbl_nap.setProperty("class", "SubtitleLabel")
        layout_nap.addWidget(lbl_nap)

        # Vùng Kéo & Thả Chuẩn Web
        self.drop_zone = VungKeoThaWeb()
        layout_drop = QVBoxLayout(self.drop_zone)
        layout_drop.setContentsMargins(14, 12, 14, 12)
        layout_drop.setSpacing(8)
        layout_drop.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_upload = QLabel()
        icon_upload.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_upload.setPixmap(qta.icon('fa5s.cloud-upload-alt', color='#3B82F6').pixmap(28, 28))
        icon_upload.setStyleSheet("background: transparent; border: none;")
        layout_drop.addWidget(icon_upload)

        lbl_drop_title = QLabel("Kéo & thả file XML / Excel vào đây để nạp nhanh")
        lbl_drop_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_drop_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #1E293B; background: transparent; border: none;")
        layout_drop.addWidget(lbl_drop_title)

        lbl_drop_sub = QLabel("hoặc bấm các nút bên dưới để chọn file từ máy tính")
        lbl_drop_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_drop_sub.setStyleSheet("font-size: 11px; color: #64748B; background: transparent; border: none;")
        layout_drop.addWidget(lbl_drop_sub)

        khung_btn_nap = QHBoxLayout()
        khung_btn_nap.setSpacing(8)

        self.btn_chon_file_xml = QPushButton(" Tờ khai XML")
        self.btn_chon_file_xml.setIcon(qta.icon('fa5s.upload', color='white'))
        self.btn_chon_file_xml.setStyleSheet("""
            QPushButton {
                background-color: #2563EB; color: white; 
                font-weight: bold; font-size: 12px; 
                padding: 7px 12px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #1D4ED8; }
        """)

        self.btn_tai_hd_ban_ra = QPushButton(" HĐ Bán ra")
        self.btn_tai_hd_ban_ra.setIcon(qta.icon('fa5s.file-excel', color='white'))
        self.btn_tai_hd_ban_ra.setStyleSheet("""
            QPushButton {
                background-color: #059669; color: white; 
                font-weight: bold; font-size: 12px; 
                padding: 7px 12px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #047857; }
        """)

        self.btn_tai_hd_mua_vao = QPushButton(" HĐ Mua vào")
        self.btn_tai_hd_mua_vao.setIcon(qta.icon('fa5s.file-excel', color='white'))
        self.btn_tai_hd_mua_vao.setStyleSheet("""
            QPushButton {
                background-color: #D97706; color: white; 
                font-weight: bold; font-size: 12px; 
                padding: 7px 12px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #B45309; }
        """)

        self.btn_lam_moi_du_lieu = QPushButton(" Xóa")
        self.btn_lam_moi_du_lieu.setIcon(qta.icon('fa5s.trash-alt', color='#DC2626'))
        self.btn_lam_moi_du_lieu.setStyleSheet("""
            QPushButton {
                background-color: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; 
                font-weight: bold; font-size: 12px; padding: 7px 10px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #FEE2E2; }
        """)

        khung_btn_nap.addWidget(self.btn_chon_file_xml)
        khung_btn_nap.addWidget(self.btn_tai_hd_ban_ra)
        khung_btn_nap.addWidget(self.btn_tai_hd_mua_vao)
        khung_btn_nap.addWidget(self.btn_lam_moi_du_lieu)
        layout_drop.addLayout(khung_btn_nap)

        layout_nap.addWidget(self.drop_zone)

        lbl_ds_file = QLabel("Danh sách hồ sơ đã nạp:")
        lbl_ds_file.setStyleSheet("font-size: 11px; font-weight: 600; color: #64748B; margin-top: 2px;")
        layout_nap.addWidget(lbl_ds_file)

        self.danh_sach_file = QListWidget()
        self.danh_sach_file.setStyleSheet("""
            QListWidget {
                border: 1px solid #E2E8F0; 
                background-color: #F8FAFC; 
                border-radius: 8px; 
                padding: 6px;
                font-size: 12px;
                color: #334155;
            }
            QListWidget::item {
                padding: 5px 8px;
                border-bottom: 1px solid #F1F5F9;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #EFF6FF;
                color: #1D4ED8;
            }
        """)
        layout_nap.addWidget(self.danh_sach_file)
        vung_thao_tac_top.addWidget(card_nap_du_lieu, 6)

        # --- CARD 2: CẤU HÌNH PHÂN TÍCH ---
        card_cau_hinh = QFrame()
        card_cau_hinh.setProperty("class", "CardWidget")
        tao_bong_do_web(card_cau_hinh, blur_radius=16, offset_y=3, alpha=14)
        layout_cau_hinh = QVBoxLayout(card_cau_hinh)
        layout_cau_hinh.setContentsMargins(16, 16, 16, 16)
        layout_cau_hinh.setSpacing(10)

        lbl_cau_hinh = QLabel("2. Cấu hình Phân tích")
        lbl_cau_hinh.setProperty("class", "SubtitleLabel")
        layout_cau_hinh.addWidget(lbl_cau_hinh)

        # Dòng chọn Loại BCTC
        lbl_lbl_bctc = QLabel("Loại Báo cáo tài chính:")
        lbl_lbl_bctc.setStyleSheet("font-weight: 600; color: #475569; font-size: 12px;")
        layout_cau_hinh.addWidget(lbl_lbl_bctc)

        self.cb_bctc = QComboBox()
        self.cb_bctc.addItems(["Tự động nhận diện", "Theo Thông tư 200", "Theo Thông tư 133"])
        layout_cau_hinh.addWidget(self.cb_bctc)

        # Dòng Bảng CĐSPS TT200
        khung_tt200 = QHBoxLayout()
        khung_tt200.setContentsMargins(0, 2, 0, 4)

        self.lbl_tt200_note = QLabel(" Upload Bảng CĐSPS (nếu có)")
        self.lbl_tt200_note.setStyleSheet("font-size: 11px; color: #94A3B8; font-style: italic;")
        khung_tt200.addWidget(self.lbl_tt200_note)
        khung_tt200.addStretch()

        self.btn_tai_mau_tt200 = QPushButton(" Mẫu")
        self.btn_tai_mau_tt200.setIcon(qta.icon('fa5s.download', color='#94A3B8'))
        self.btn_tai_mau_tt200.setToolTip("Tải file Excel mẫu Bảng CĐSPS")
        self.btn_tai_mau_tt200.setFixedHeight(28)
        self.btn_tai_mau_tt200.setEnabled(False)
        self.btn_tai_mau_tt200.setStyleSheet("""
            QPushButton { padding: 4px 10px; font-size: 11px; border-radius: 4px; font-weight: bold; }
            QPushButton:disabled { background-color: #F1F5F9; color: #94A3B8; border: 1px solid #E2E8F0; }
        """)
        khung_tt200.addWidget(self.btn_tai_mau_tt200)

        self.btn_nap_tt200 = QPushButton(" Tải lên File")
        self.btn_nap_tt200.setIcon(qta.icon('fa5s.upload', color='#94A3B8'))
        self.btn_nap_tt200.setToolTip("Tải lên dữ liệu Bảng CĐSPS đã điền")
        self.btn_nap_tt200.setFixedHeight(28)
        self.btn_nap_tt200.setEnabled(False)
        self.btn_nap_tt200.setStyleSheet("""
            QPushButton { padding: 4px 10px; font-size: 11px; border-radius: 4px; font-weight: bold; }
            QPushButton:disabled { background-color: #F1F5F9; color: #94A3B8; border: 1px solid #E2E8F0; }
        """)
        khung_tt200.addWidget(self.btn_nap_tt200)
        layout_cau_hinh.addLayout(khung_tt200)

        self.cb_bctc.currentIndexChanged.connect(self.kiem_tra_trang_thai_nut_tt200)

        # Dòng chọn Năm
        lbl_lbl_nam = QLabel("Năm phân tích:")
        lbl_lbl_nam.setStyleSheet("font-weight: 600; color: #475569; font-size: 12px;")
        layout_cau_hinh.addWidget(lbl_lbl_nam)

        self.cb_nam = QComboBox()
        self.cb_nam.addItems(["Tất cả các năm", "2026", "2025", "2024", "2023", "2022"])
        layout_cau_hinh.addWidget(self.cb_nam)

        # Khu vực TMS
        khung_tms = QHBoxLayout()
        khung_tms.setContentsMargins(0, 6, 0, 4)

        khung_checkbox = QVBoxLayout()
        khung_checkbox.setSpacing(4)
        self.chk_tms = QCheckBox("Tra cứu trạng thái HĐ từ TMS")
        self.chk_dong_bo_ngay = QCheckBox("Tra cứu ngày nộp Tờ khai TMS")
        khung_checkbox.addWidget(self.chk_tms)
        khung_checkbox.addWidget(self.chk_dong_bo_ngay)
        khung_tms.addLayout(khung_checkbox)
        khung_tms.addStretch()

        self.btn_cau_hinh_tms = QPushButton(" Cấu hình TMS")
        self.btn_cau_hinh_tms.setIcon(qta.icon('fa5s.cog', color='#475569'))
        self.btn_cau_hinh_tms.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9; color: #475569; 
                font-weight: bold; font-size: 11px;
                padding: 8px 12px; border-radius: 6px; border: 1px solid #CBD5E1;
            }
            QPushButton:hover { background-color: #E2E8F0; color: #0F172A; }
        """)
        khung_tms.addWidget(self.btn_cau_hinh_tms)
        layout_cau_hinh.addLayout(khung_tms)

        layout_cau_hinh.addSpacing(4)

        # NÚT BẮT ĐẦU PHÂN TÍCH (CALL TO ACTION CHÍNH)
        self.btn_phan_tich = QPushButton(" 🚀 PHÂN TÍCH HỒ SƠ TOÀN DIỆN")
        self.btn_phan_tich.setIcon(qta.icon('fa5s.rocket', color='white'))
        self.btn_phan_tich.setFixedHeight(44)
        self.btn_phan_tich.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_phan_tich.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #2563EB, stop:1 #1D4ED8);
                color: white; font-weight: 800; font-size: 14px; 
                border-radius: 8px; border: none; letter-spacing: 0.5px;
            }
            QPushButton:hover { 
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1D4ED8, stop:1 #1E40AF); 
            }
        """)
        layout_cau_hinh.addWidget(self.btn_phan_tich)

        # HÀNG CÔNG CỤ PHỤ (TIỆN ÍCH)
        khung_btn_phu = QHBoxLayout()
        khung_btn_phu.setSpacing(6)

        style_btn_phu = """
            QPushButton {
                background-color: #F8FAFC; color: #475569; font-weight: 600; 
                font-size: 12px; border-radius: 6px; padding: 7px 8px; border: 1px solid #CBD5E1;
            }
            QPushButton:hover { background-color: #EFF6FF; color: #1D4ED8; border-color: #93C5FD; }
        """

        self.btn_chon_rule = QPushButton(" Chọn Công thức")
        self.btn_chon_rule.setIcon(qta.icon('fa5s.filter', color='#475569'))
        self.btn_chon_rule.setStyleSheet(style_btn_phu)

        self.btn_tao_cong_thuc = QPushButton(" Quản lý Công thức")
        self.btn_tao_cong_thuc.setIcon(qta.icon('fa5s.cog', color='#475569'))
        self.btn_tao_cong_thuc.setStyleSheet(style_btn_phu)

        self.btn_chuoi_cung_ung = QPushButton(" Cấu hình Chuỗi")
        self.btn_chuoi_cung_ung.setIcon(qta.icon('fa5s.project-diagram', color='#475569'))
        self.btn_chuoi_cung_ung.setStyleSheet(style_btn_phu)

        self.btn_kho_file_mau = QPushButton(" Tải Mẫu")
        self.btn_kho_file_mau.setIcon(qta.icon('fa5s.file-download', color='#059669'))
        self.btn_kho_file_mau.setStyleSheet("""
            QPushButton {
                background-color: #ECFDF5; color: #065F46; font-weight: 600; 
                font-size: 12px; border-radius: 6px; padding: 7px 8px; border: 1px solid #A7F3D0;
            }
            QPushButton:hover { background-color: #D1FAE5; }
        """)

        khung_btn_phu.addWidget(self.btn_chon_rule)
        khung_btn_phu.addWidget(self.btn_tao_cong_thuc)
        khung_btn_phu.addWidget(self.btn_chuoi_cung_ung)
        khung_btn_phu.addWidget(self.btn_kho_file_mau)
        layout_cau_hinh.addLayout(khung_btn_phu)

        vung_thao_tac_top.addWidget(card_cau_hinh, 4)
        layout_chuan_bi.addLayout(vung_thao_tac_top, 5)

        # --- CARD 3: NHẬT KÝ HỆ THỐNG ---
        card_log = QFrame()
        card_log.setProperty("class", "CardWidget")
        tao_bong_do_web(card_log, blur_radius=16, offset_y=3, alpha=14)
        layout_log = QVBoxLayout(card_log)
        layout_log.setContentsMargins(16, 12, 16, 12)
        layout_log.setSpacing(8)

        lbl_log = QLabel("📋 Nhật ký xử lý hệ thống")
        lbl_log.setStyleSheet("font-weight: 700; color: #475569; font-size: 13px;")
        layout_log.addWidget(lbl_log)

        self.text_log_xu_ly = QTextEdit()
        self.text_log_xu_ly.setReadOnly(True)
        self.text_log_xu_ly.setStyleSheet("""
            QTextEdit {
                background-color: #F8FAFC; color: #1E293B; 
                font-family: Consolas, 'Cascadia Code', monospace; 
                font-size: 12px; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px;
            }
        """)
        layout_log.addWidget(self.text_log_xu_ly)
        layout_chuan_bi.addWidget(card_log, 4)

        self.tabs_chuan_bi.addTab(trang_chuan_bi, "Bảng Điều khiển")
        self.tabs_chuan_bi.tabBar().setTabButton(0, QTabBar.ButtonPosition.RightSide, None)
        self.tabs_chuan_bi.tabBar().setTabButton(0, QTabBar.ButtonPosition.LeftSide, None)
        self.khung_phai.addWidget(self.tabs_chuan_bi)

        # TAB 1: TỔNG HỢP TỜ KHAI
        self.trang_tong_hop_tk = QWidget()
        layout_thtk = QVBoxLayout(self.trang_tong_hop_tk)
        layout_thtk.setContentsMargins(10, 10, 10, 10)
        self.tab_tong_hop_chi_tiet = QTabWidget()
        layout_thtk.addWidget(self.tab_tong_hop_chi_tiet)
        self.khung_phai.addWidget(self.trang_tong_hop_tk)

        # TAB 2: KẾT QUẢ HÓA ĐƠN
        self.trang_kq_hd = QWidget()
        layout_kq_hd = QVBoxLayout(self.trang_kq_hd)
        layout_kq_hd.setContentsMargins(10, 10, 10, 10)
        self.tabs_hoa_don = QTabWidget()
        layout_kq_hd.addWidget(self.tabs_hoa_don)

        self.tab_hd_ban_ra = QWidget()
        layout_ban_ra = QVBoxLayout(self.tab_hd_ban_ra)
        layout_ban_ra.setContentsMargins(0, 0, 0, 0)
        self.bang_hd_ban_ra = QTableWidget()
        layout_ban_ra.addWidget(self.bang_hd_ban_ra)
        self.tabs_hoa_don.addTab(self.tab_hd_ban_ra, "Hóa đơn Bán ra")

        self.tab_hd_mua_vao = QWidget()
        layout_mua_vao = QVBoxLayout(self.tab_hd_mua_vao)
        layout_mua_vao.setContentsMargins(0, 0, 0, 0)
        self.bang_hd_mua_vao = QTableWidget()
        layout_mua_vao.addWidget(self.bang_hd_mua_vao)
        self.tabs_hoa_don.addTab(self.tab_hd_mua_vao, "Hóa đơn Mua vào")

        self.tab_hd_rui_ro = QWidget()
        layout_hd_rr = QVBoxLayout(self.tab_hd_rui_ro)
        layout_hd_rr.setContentsMargins(0, 0, 0, 0)
        self.bang_hd_rui_ro = QTableWidget()
        #self.bang_hd_rui_ro.setStyleSheet(
            #"QTableWidget { background-color: #FFF0F0; } QTableWidget::item:hover { background-color: #FFE5E5; }")
        layout_hd_rr.addWidget(self.bang_hd_rui_ro)
        self.tabs_hoa_don.addTab(self.tab_hd_rui_ro, qta.icon('fa5s.exclamation-triangle', color='#DC2626'),
                                 "Hóa đơn Rủi ro")
        self.khung_phai.addWidget(self.trang_kq_hd)

        # TAB 3: QUẢN LÝ RỦI RO (Đã tách thành Component độc lập)
        from module_giao_dien.quan_ly_rui_ro_ui import WidgetQuanLyRuiRo
        self.trang_quan_ly_rui_ro = WidgetQuanLyRuiRo(self.ruiro_mgr, parent=self)
        self.khung_phai.addWidget(self.trang_quan_ly_rui_ro)

        # TAB 4: KẾT QUẢ PHÂN TÍCH (ĐẶT Ở DƯỚI CÙNG)
        self.trang_kq_phan_tich = QWidget()
        layout_kq_pt = QVBoxLayout(self.trang_kq_phan_tich)
        layout_kq_pt.setContentsMargins(10, 10, 10, 10)

        # --- Nút Kết xuất Excel và Phiếu ---
        khung_tool_bar = QHBoxLayout()
        khung_tool_bar.addStretch()

        # ==============================================================
        # 1. NÚT LOADING (Mặc định sẽ bị ẩn, chỉ hiện khi đang tải)
        # ==============================================================
        self.lbl_loading_nam = QLabel("⏳ Đang tải dữ liệu...")
        self.lbl_loading_nam.setStyleSheet("""
                    QLabel {
                        color: #D97706; 
                        font-weight: bold; 
                        font-size: 13px; 
                        background-color: #FEF3C7; 
                        padding: 4px 10px; /* <--- Bóp chiều cao xuống bằng chuẩn với Combobox */
                        border-radius: 4px; /* <--- Đồng bộ độ bo góc */
                        border: 1px solid #FCD34D;
                        margin-right: 15px;
                    }
                """)
        self.lbl_loading_nam.setVisible(False)
        khung_tool_bar.addWidget(self.lbl_loading_nam)

        # ==============================================================
        # 2. COMBOBOX CHỌN NĂM (Thiết kế nhỏ gọn, liền khối)
        # ==============================================================
        lbl_chon_nam = QLabel("📅 Lọc theo năm:")
        lbl_chon_nam.setStyleSheet("font-size: 13px; font-weight: bold; color: #475569;")
        khung_tool_bar.addWidget(lbl_chon_nam)

        self.cb_nam_kq = QComboBox()
        self.cb_nam_kq.setStyleSheet("""
                    QComboBox {
                        padding: 4px 10px; /* Bóp trên dưới sát vào chữ */
                        border: 1px solid #CBD5E1; /* Viền mỏng 1px tinh tế */
                        border-radius: 4px; /* Bo góc nhẹ nhàng */
                        font-weight: bold; 
                        font-size: 13px;
                        color: #0F172A; 
                        background-color: #FFFFFF; 
                        margin-right: 15px;
                        min-width: 70px; /* Bóp chiều ngang vừa đủ chứa 4 số */
                    }
                    QComboBox:hover { 
                        border: 1px solid #3B82F6; 
                    }
                    QComboBox::drop-down {
                        subcontrol-origin: padding;
                        subcontrol-position: top right;
                        width: 20px; /* Nút bấm nhỏ lại */
                        border-left: none; /* XÓA ĐƯỜNG KẺ DỌC CHIA CẮT */
                        background-color: transparent; /* Nút thả xuống tiệp hoàn toàn màu nền */
                    }
                """)
        khung_tool_bar.addWidget(self.cb_nam_kq)


        # ==============================================================
        # ---> BỔ SUNG NÚT NÀY VÀO <---
        self.btn_tao_phieu = QPushButton(" Tạo Phiếu Nhận Xét (Word)")
        self.btn_tao_phieu.setIcon(qta.icon('fa5s.file-word', color='white'))
        self.btn_tao_phieu.setStyleSheet(
            "background-color: #2563EB; color: white; font-weight: bold; padding: 8px 18px; border-radius: 6px; font-size: 13px; margin-right: 10px;")
        khung_tool_bar.addWidget(self.btn_tao_phieu)
        self.btn_xuat_excel = QPushButton(" Kết xuất Excel")
        self.btn_xuat_excel.setIcon(qta.icon('fa5s.file-excel', color='white'))
        self.btn_xuat_excel.setStyleSheet(
            "background-color: #107C41; color: white; font-weight: bold; padding: 8px 18px; border-radius: 6px; font-size: 13px;")
        khung_tool_bar.addWidget(self.btn_xuat_excel)
        layout_kq_pt.addLayout(khung_tool_bar)

        # --- NHÚNG WIDGET VIEW ĐỘC LẬP VÀO ĐÂY ---
        from module_giao_dien.giao_dien_ket_qua_phan_tich import WidgetKetQuaPhanTich
        self.widget_kq_phan_tich = WidgetKetQuaPhanTich()
        layout_kq_pt.addWidget(self.widget_kq_phan_tich)

        self.khung_phai.addWidget(self.trang_kq_phan_tich)
        # TAB 5: HƯỚNG DẪN SỬ DỤNG (ĐẶT CUỐI CÙNG TRONG KHUNG PHẢI)
        from module_giao_dien.huong_dan_su_dung import WidgetHuongDanSuDung
        self.trang_huong_dan = WidgetHuongDanSuDung(self)
        self.khung_phai.addWidget(self.trang_huong_dan)
        # Chốt layout
        bo_chia.addWidget(self.khung_trai)
        bo_chia.addWidget(self.khung_phai)

        self.khung_trai.setMinimumWidth(210)
        self.khung_trai.setMaximumWidth(210)
        bo_chia.setSizes([210, 1040])

    def xu_ly_lap_video_muot(self, status):
        from PySide6.QtMultimedia import QMediaPlayer
        # Nếu video vừa chạm mốc kết thúc, ép tua về mốc 0ms và phát lại ngay lập tức
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()


    # =========================================================================
    # CÁC HÀM XỬ LÝ SỰ KIỆN GIAO DIỆN
    # =========================================================================
    def chuyen_trang(self, btn_active, trang_dich):
        """Hàm bẻ ghi chuyển đổi màn hình - Trỏ đích danh Widget, không dùng số Index lôm côm"""
        for btn in self.danh_sach_btn:
            btn.setChecked(btn == btn_active)
        self.khung_phai.setCurrentWidget(trang_dich)

    def mo_dialog_gop_y(self):
        dialog = DialogGopY(self)
        dialog.exec()

    def thu_gon_menu(self):
        if self.btn_tab_chuan_bi.text() != "":
            for btn in self.danh_sach_btn:
                btn.setText("")
            self.btn_mo_auto_bot.setText("")
            self.btn_gop_y.setText("")
            self.btn_thu_gon.setText("")
            self.btn_thu_gon.setIcon(qta.icon('fa5s.angle-double-right', color='#64748B'))
            if hasattr(self, 'khung_brand'):
                self.khung_brand.setVisible(False)
            if hasattr(self, 'khung_user_status'):
                self.khung_user_status.setVisible(False)
            if hasattr(self, 'lbl_section_tools'):
                self.lbl_section_tools.setVisible(False)
            self.khung_trai.setMinimumWidth(64)
            self.khung_trai.setMaximumWidth(64)
        else:
            self.btn_tab_chuan_bi.setText("  Chuẩn bị Dữ liệu")
            self.btn_tab_kq_to_khai.setText("  Tổng hợp Tờ khai")
            self.btn_tab_kq_hoa_don.setText("  Kết quả Hóa đơn")
            self.btn_tab_rui_ro.setText("  Quản lý Rủi ro")
            self.btn_tab_kq_phan_tich.setText("  Kết quả Phân tích")
            self.btn_tab_huong_dan.setText("  Hướng dẫn sử dụng")
            self.btn_mo_auto_bot.setText("  Phân tích tự động")
            self.btn_gop_y.setText("  Góp ý / Báo lỗi")
            self.btn_thu_gon.setText("  Thu gọn menu")
            self.btn_thu_gon.setIcon(qta.icon('fa5s.angle-double-left', color='#64748B'))
            if hasattr(self, 'khung_brand'):
                self.khung_brand.setVisible(True)
            if hasattr(self, 'khung_user_status'):
                self.khung_user_status.setVisible(True)
            if hasattr(self, 'lbl_section_tools'):
                self.lbl_section_tools.setVisible(True)
            self.khung_trai.setMinimumWidth(210)
            self.khung_trai.setMaximumWidth(210)

    def dong_tab_chuan_bi(self, index):
        if index > 0:
            widget = self.tabs_chuan_bi.widget(index)
            self.tabs_chuan_bi.removeTab(index)
            widget.deleteLater()

    def kiem_tra_trang_thai_nut_tt200(self, index):
        """Đổi màu sắc và trạng thái UI khi chọn TT200"""
        is_tt200 = (index == 1)

        # Mở/khóa nút
        self.btn_tai_mau_tt200.setEnabled(is_tt200)
        self.btn_nap_tt200.setEnabled(is_tt200)

        # Đổi màu Icon
        mau_tai = '#2563EB' if is_tt200 else '#9CA3AF'
        mau_nap = '#10B981' if is_tt200 else '#9CA3AF'
        self.btn_tai_mau_tt200.setIcon(qta.icon('fa5s.download', color=mau_tai))
        self.btn_nap_tt200.setIcon(qta.icon('fa5s.upload', color=mau_nap))

        # Ép CSS đổi màu chữ cho 2 nút khi được bật
        if is_tt200:
            self.btn_tai_mau_tt200.setStyleSheet(
                "QPushButton { background-color: #EFF6FF; color: #1E3A8A; border: 1px solid #BFDBFE; padding: 4px 10px; font-size: 12px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #DBEAFE; }")
            self.btn_nap_tt200.setStyleSheet(
                "QPushButton { background-color: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; padding: 4px 10px; font-size: 12px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #D1FAE5; }")

            # Cảnh báo rực sáng lên
            self.lbl_tt200_note.setStyleSheet("font-size: 11px; color: #D97706; font-weight: bold; font-style: italic;")
            self.lbl_tt200_note.setText("Tải lên Bảng CĐSPS (nếu có)")
        else:
            self.btn_tai_mau_tt200.setStyleSheet(
                "QPushButton:disabled { background-color: #F3F4F6; color: #9CA3AF; border: 1px solid #E5E7EB; padding: 4px 10px; font-size: 12px; border-radius: 4px; font-weight: bold; }")
            self.btn_nap_tt200.setStyleSheet(
                "QPushButton:disabled { background-color: #F3F4F6; color: #9CA3AF; border: 1px solid #E5E7EB; padding: 4px 10px; font-size: 12px; border-radius: 4px; font-weight: bold; }")

            # Cảnh báo mờ đi
            self.lbl_tt200_note.setStyleSheet("font-size: 11px; color: #9CA3AF; font-style: italic;")
            self.lbl_tt200_note.setText("Tải lên Bảng CĐSPS (nếu có)")