import sys
from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFileDialog, QTableWidget, QTabWidget, QVBoxLayout, QWidget, QMessageBox
from giao_dien_chinh import GiaoDienChinh
from luong_xu_ly_nen import LuongXuLy
from module_doc_xml.quan_ly_doc_to_khai import QuanLyDocToKhaiXML
from module_doc_xml.tu_dien_chi_tieu import MAP_TEN_TO_KHAI
from module_giao_dien.quan_ly_bang_bieu import QuanLyBangBieu
from module_doc_hoadon.quan_ly_hoa_don_ui import QuanLyHoaDonUI
from module_phan_tich.giao_dien_tao_cong_thuc import GiaoDienTaoCongThuc

from module_xu_ly_office.module_xuat_excel import DialogXuatExcel
from module_giao_dien.khbs_widget import KHBSReviewWidget
import qtawesome as qta
from module_ho_tro.module_cau_hinh_tms import DialogCauHinhTMS, TMSConfig
from module_ho_tro.dialog_file_mau import DialogKhoFileMau
from module_ho_tro.quan_ly_cong_thuc import QuanLyCongThuc
from module_giao_dien.huong_dan_tour import HuongDanTour

import sys
import os
import ctypes
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

class UngDungRRR:
            def __init__(self):
                self.app = QApplication(sys.argv)

                # ==============================================================
                # KÍCH HOẠT LOGO TOÀN HỆ THỐNG & TASKBAR
                # ==============================================================
                # 1. Ép Windows tách biệt app này khỏi icon Python mặc định
                try:
                    myappid = 'ban_quyen.phan_mem_rrr.phan_tich_thue.v1'
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                except:
                    pass

                # 2. Gắn logo vào Application
                duong_dan_logo = os.path.join(os.getcwd(), "Data", "Images", "logo.ico")
                if os.path.exists(duong_dan_logo):
                    icon_app = QIcon(duong_dan_logo)
                    self.app.setWindowIcon(icon_app)
                # ==============================================================

                self.giao_dien = GiaoDienChinh()

                # 3. Gắn logo trực tiếp vào Cửa sổ chính
                if os.path.exists(duong_dan_logo):
                    self.giao_dien.setWindowIcon(icon_app)

                
                self.quan_ly_xml = QuanLyDocToKhaiXML()

                # Khởi tạo data lưu trữ
                self.dict_hd_ban_ra = {}
                self.dict_hd_mua_vao = {}
                self.du_lieu_he_thong_to_khai = {}
                # Mảng chờ chứa các file XML được chọn (Chưa xử lý ngay)
                self.du_lieu_bcdsps_tt200 = {}
                self.danh_sach_file_xml_cho = []
                self.danh_sach_luong = []
                self.so_luong_xml_dang_chay = 0
                self.quan_ly_hoa_don = QuanLyHoaDonUI(self)
                self.ket_qua_cuoi_cung = []  # Biến lưu trữ kết quả để xuất Excel
                self.danh_sach_rule_duoc_chon = None
                # --- THÊM 2 BIẾN NÀY ---
                self.toan_bo_file_xml = set()  # Lưu vết vĩnh viễn đường dẫn file XML để nạp cho widget KHBS
                self.dict_khbs_widgets = {}  # Quản lý các Widget KHBS theo từng loại tờ khai
                # =========================================================
                # TỰ ĐỘNG ĐỌC CẤU HÌNH RULE TỪ LẦN TRƯỚC (NẾU CÓ)
                # =========================================================
                self.file_cau_hinh_rule = "Data/config_rules.json"
                self.danh_sach_rule_duoc_chon = self._doc_cau_hinh_rule_luu_tru()
                self.giao_dien.btn_xuat_excel.clicked.connect(self.hien_thi_form_xuat_excel)
                self.ket_noi_su_kien()
                # Cập nhật chữ trên Nút bấm ngay lập tức nếu có cấu hình cũ
                if self.danh_sach_rule_duoc_chon is not None:
                    self.giao_dien.btn_chon_rule.setText(f" Đã chọn ({len(self.danh_sach_rule_duoc_chon)} Rule)")
                    self.giao_dien.btn_chon_rule.setStyleSheet(
                        "QPushButton { background-color: #DBEAFE; color: #1E3A8A; border: 1px solid #93C5FD; font-weight: bold; font-size: 13px; border-radius: 6px; padding: 10px; margin-top: 5px; }")

            def mo_cau_hinh_tms(self):
                dialog = DialogCauHinhTMS(self.giao_dien)
                dialog.exec()
            def _doc_cau_hinh_rule_luu_tru(self):
                """Đọc file json chứa danh sách các rule đã lưu mặc định"""
                import os, json
                if os.path.exists(self.file_cau_hinh_rule):
                    try:
                        with open(self.file_cau_hinh_rule, 'r', encoding='utf-8') as f:
                            return json.load(f)
                    except:
                        pass
                return None
            def ket_noi_su_kien(self):
                self.giao_dien.btn_tab_chuan_bi.clicked.connect(lambda: self.chuyen_tab(0))
                self.giao_dien.btn_tab_kq_to_khai.clicked.connect(lambda: self.chuyen_tab(1))
                self.giao_dien.btn_tab_kq_hoa_don.clicked.connect(lambda: self.chuyen_tab(2))
                self.giao_dien.btn_tab_rui_ro.clicked.connect(lambda: self.chuyen_tab(3))
                self.giao_dien.btn_tab_kq_phan_tich.clicked.connect(lambda: self.chuyen_tab(4))
                self.giao_dien.btn_tab_huong_dan.clicked.connect(lambda: self.chuyen_tab(5))  # Dòng mới
                self.giao_dien.btn_chuoi_cung_ung.clicked.connect(self.mo_cau_hinh_chuoi_cung_ung)
                self.giao_dien.btn_chon_file_xml.clicked.connect(self.chon_nhieu_file_xml)
                self.giao_dien.btn_phan_tich.clicked.connect(self.thuc_thi_phan_tich)
                self.giao_dien.btn_tao_cong_thuc.clicked.connect(self.mo_trinh_tao_cong_thuc)
                self.giao_dien.btn_lam_moi_du_lieu.clicked.connect(self.lam_moi_phien_lam_viec)
                # Thêm dòng này vào cuối hàm ket_noi_su_kien
                self.giao_dien.btn_tao_phieu.clicked.connect(self.mo_trinh_soan_thao_phieu)
                # ---> BỔ SUNG DÒNG NÀY ĐỂ BẮT SỰ KIỆN TÍCH CHỌN CHECKBOX TMS <---
                self.giao_dien.chk_tms.toggled.connect(self.hien_thi_canh_bao_tms)
                # ---> BỔ SUNG 2 SỰ KIỆN CHO NÚT TẢI/NẠP EXCEL TT200 <---
                self.giao_dien.btn_tai_mau_tt200.clicked.connect(self.tai_template_tt200)
                self.giao_dien.btn_nap_tt200.clicked.connect(self.nap_du_lieu_tt200)
                self.giao_dien.btn_chon_rule.clicked.connect(self.mo_dialog_chon_rule)
                #self.giao_dien.btn_dong_bo_tms.clicked.connect(self.hien_thi_popup_dong_bo)
                self.giao_dien.btn_cau_hinh_tms.clicked.connect(self.mo_cau_hinh_tms)
                self.giao_dien.btn_kho_file_mau.clicked.connect(self.mo_kho_file_mau)
                self.giao_dien.btn_mo_auto_bot.clicked.connect(self.mo_popup_auto_bot)
                self.giao_dien.cb_nam_kq.currentTextChanged.connect(self.chuyen_view_ket_qua_nam)
                if hasattr(self.giao_dien, 'drop_zone'):
                    self.giao_dien.drop_zone.files_dropped.connect(self.xu_ly_keo_tha_files)
            def mo_kho_file_mau(self):
                dialog = DialogKhoFileMau(self.giao_dien)
                dialog.exec()

            def mo_popup_auto_bot(self):
                # Gọi Popup đã được đóng gói từ module mới
                from module_giao_dien.giao_dien_auto_bot import DialogAutoBot
                dialog = DialogAutoBot(main_app=self, parent=self.giao_dien)
                dialog.exec()
            def hien_thi_canh_bao_tms(self, is_checked):
                """Bung thông báo nhắc nhở khi NSD bật tính năng tra cứu SAP/TMS"""
                if is_checked:
                    from PySide6.QtWidgets import QMessageBox

                    msg = QMessageBox(self.giao_dien)
                    msg.setWindowTitle("Lưu ý kết nối hệ thống TMS")
                    msg.setText(
                        "ĐỂ TÍNH NĂNG TRA CỨU TÌNH TRẠNG HOẠT ĐỘNG, VUI LÒNG:\n\n"
                        "1. Tự đăng nhập vào ứng dụng SAP/TMS.\n"
                        "2. Tài khoản TMS có quyền truy cập chức năng Tra cứu danh bạ 2.9.1.\n\n"

                    )
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.exec()

            def hien_thi_popup_dong_bo(self):
                from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox
                from datetime import datetime
                import os
                from module_ho_tro.module_dong_bo_tms import chay_tu_dong_3233, dong_bo_ngay_nop_tu_excel

                if not self.dict_he_thong_to_khai:
                    QMessageBox.warning(self.giao_dien, "Cảnh báo",
                                        "Bạn chưa tải Tờ khai XML nào. Vui lòng tải XML trước khi đồng bộ!")
                    return

                # TỰ ĐỘNG NẶN NGÀY (Từ 01.01 của năm nhỏ nhất đến ngày hôm nay)
                cac_nam = []
                for ma_form, dict_ky in self.dict_he_thong_to_khai.items():
                    for ky in dict_ky.keys():
                        try:
                            cac_nam.append(int(str(ky)[-4:]))
                        except:
                            pass

                nam_nho_nhat = min(cac_nam) if cac_nam else datetime.now().year
                ngay_bat_dau = f"01.01.{nam_nho_nhat}"
                ngay_ket_thuc = datetime.now().strftime("%d.%m.%Y")

                # VẼ CỬA SỔ POPUP NHANH
                dialog = QDialog(self.giao_dien)
                dialog.setWindowTitle("Tham số tải TMS")
                dialog.resize(300, 150)
                layout = QVBoxLayout(dialog)

                form_layout = QFormLayout()
                txt_cqt = QLineEdit("50500")  # CQT Mặc định của mày
                txt_tu_ngay = QLineEdit(ngay_bat_dau)
                txt_den_ngay = QLineEdit(ngay_ket_thuc)

                form_layout.addRow("Mã CQT:", txt_cqt)
                form_layout.addRow("Từ ngày (dd.mm.yyyy):", txt_tu_ngay)
                form_layout.addRow("Đến ngày (dd.mm.yyyy):", txt_den_ngay)
                layout.addLayout(form_layout)

                btn_chay = QPushButton("Khởi động Bot SAP")
                btn_chay.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 8px;")
                layout.addWidget(btn_chay)

                def chay_bot_ngay():
                    cqt = txt_cqt.text().strip()
                    tu = txt_tu_ngay.text().strip()
                    den = txt_den_ngay.text().strip()
                    # Mặc định lưu file tải về ở thư mục chứa phần mềm luôn cho tiện
                    thu_muc_luu = os.getcwd()

                    btn_chay.setText("Đang chạy SAP... Vui lòng không đụng chuột")
                    btn_chay.setEnabled(False)
                    self.giao_dien.repaint()  # Ép giao diện update chữ

                    # 1. Gọi RPA tải file
                    thanh_cong, ket_qua = chay_tu_dong_3233(tu, den, cqt, thu_muc_luu)
                    if not thanh_cong:
                        QMessageBox.critical(dialog, "Lỗi RPA", ket_qua)
                        dialog.reject()
                        return

                    # 2. Bắn file excel vào hàm Đồng bộ
                    so_luong, msg = dong_bo_ngay_nop_tu_excel(ket_qua, self.dict_he_thong_to_khai)
                    if so_luong >= 0:
                        self.ghi_log(f"✅ Đã đồng bộ thành công ngày nộp thực tế cho {so_luong} Tờ khai XML!")
                        QMessageBox.information(dialog, "Thành công",
                                                f"RPA hoàn tất. Đã chốt ngày nộp cho {so_luong} tờ khai.")
                    else:
                        QMessageBox.warning(dialog, "Lỗi Mapping", f"Tải file thành công nhưng lỗi đồng bộ: {msg}")

                    dialog.accept()

                btn_chay.clicked.connect(chay_bot_ngay)
                dialog.exec()
            def mo_cau_hinh_chuoi_cung_ung(self):
                from module_giao_dien.dialog_chuoi_cung_ung import DialogCauHinhChuoiCungUng
                dialog = DialogCauHinhChuoiCungUng(self.giao_dien)
                dialog.exec()
                
            def mo_trinh_tao_cong_thuc(self):
                # Kiểm tra xem Tab "Quản lý Công thức" đã mở chưa. Nếu mở rồi thì chỉ focus tới nó thôi (chống spam tab)
                for i in range(self.giao_dien.tabs_chuan_bi.count()):
                    if self.giao_dien.tabs_chuan_bi.tabText(i) == "⚙️ Quản lý Công thức":
                        self.giao_dien.tabs_chuan_bi.setCurrentIndex(i)
                        return

                # Nạp widget công thức
                widget_cong_thuc = GiaoDienTaoCongThuc(parent=self.giao_dien)

                # Đẩy nó vào làm 1 tab mới cạnh cái "Bảng điều khiển"
                index = self.giao_dien.tabs_chuan_bi.addTab(widget_cong_thuc, "⚙️ Quản lý Công thức")

                # Tự động nhảy sang tab vừa tạo
                self.giao_dien.tabs_chuan_bi.setCurrentIndex(index)

            def mo_dialog_chon_rule(self):
                from module_giao_dien.dialog_chon_quy_tac import DialogChonQuyTac
                from PySide6.QtWidgets import QDialog
                import json, os

                dialog = DialogChonQuyTac(parent=self.giao_dien)

                # Tick lại trên giao diện những rule đã chọn ở phiên trước/cấu hình cũ
                if self.danh_sach_rule_duoc_chon is not None:
                    dialog.cay_rule.blockSignals(True)
                    for i in range(dialog.cay_rule.topLevelItemCount()):
                        cha = dialog.cay_rule.topLevelItem(i)
                        co_checked = False
                        for j in range(cha.childCount()):
                            con = cha.child(j)
                            is_chk = con.text(1) in self.danh_sach_rule_duoc_chon
                            con.setCheckState(0, Qt.CheckState.Checked if is_chk else Qt.CheckState.Unchecked)
                            if is_chk: co_checked = True
                        cha.setCheckState(0, Qt.CheckState.Checked if co_checked else Qt.CheckState.Unchecked)
                    dialog.cay_rule.blockSignals(False)

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    # Lưu vào RAM để Engine chạy ngay trong phiên này
                    self.danh_sach_rule_duoc_chon = dialog.danh_sach_chon
                    so_luong = len(self.danh_sach_rule_duoc_chon)

                    # Nếu NSD tích chọn "Lưu cấu hình", thì xuất ra file JSON
                    if dialog.luu_vinh_vien:
                        try:
                            os.makedirs("Data", exist_ok=True)
                            with open(self.file_cau_hinh_rule, 'w', encoding='utf-8') as f:
                                json.dump(self.danh_sach_rule_duoc_chon, f, ensure_ascii=False)
                            self.ghi_log("💾 Đã lưu cấu hình bộ lọc Rule làm mặc định cho các lần mở app sau.")
                        except Exception as e:
                            self.ghi_log(f"❌ Không thể lưu cấu hình Rule: {e}")
                    else:
                        self.ghi_log("🔄 Chế độ: Chỉ áp dụng lọc Rule cho phiên làm việc hiện tại.")

                    self.ghi_log(f"⚙️ Đã thiết lập chỉ chạy {so_luong} quy tắc phân tích.")
                    self.giao_dien.btn_chon_rule.setText(f" Đã chọn ({so_luong} Rule)")
                    self.giao_dien.btn_chon_rule.setStyleSheet(
                        "QPushButton { background-color: #DBEAFE; color: #1E3A8A; border: 1px solid #93C5FD; font-weight: bold; font-size: 13px; border-radius: 6px; padding: 10px; margin-top: 5px; }")
            def chuyen_tab(self, index):
                self.giao_dien.khung_phai.setCurrentIndex(index)
                self.giao_dien.btn_tab_chuan_bi.setChecked(index == 0)
                self.giao_dien.btn_tab_kq_to_khai.setChecked(index == 1)
                self.giao_dien.btn_tab_kq_hoa_don.setChecked(index == 2)

                # --- BỔ SUNG & SỬA LẠI INDEX Ở 2 DÒNG NÀY ---
                self.giao_dien.btn_tab_rui_ro.setChecked(index == 3)
                self.giao_dien.btn_tab_kq_phan_tich.setChecked(index == 4)
                self.giao_dien.btn_tab_huong_dan.setChecked(index == 5)  # Dòng mới

            def ghi_log(self, thong_diep):
                """Hàm in thông báo ra màn hình Console UI"""
                thoi_gian = datetime.now().strftime("%H:%M:%S")
                self.giao_dien.text_log_xu_ly.append(f"[{thoi_gian}] {thong_diep}")

                # BÍ KÍP CHỐNG ĐƠ: Ép Giao diện (UI) cập nhật và vẽ lại ngay lập tức
                QApplication.processEvents()

            def cap_nhat_kpi_chuan_bi(self):
                """Cập nhật các số liệu trên 4 thẻ KPI của màn hình Chuẩn bị Dữ liệu"""
                try:
                    sl_xml = len(self.toan_bo_file_xml) if hasattr(self, 'toan_bo_file_xml') else 0
                    if hasattr(self.giao_dien, 'kpi_to_khai'):
                        self.giao_dien.kpi_to_khai.cap_nhat(
                            gia_tri=str(sl_xml),
                            subtext=f"{sl_xml} file XML sẵn sàng" if sl_xml > 0 else "Chưa có file XML"
                        )

                    sl_br = 0
                    if hasattr(self, 'dict_hd_ban_ra') and hasattr(self.dict_hd_ban_ra, '__len__'):
                        sl_br = len(self.dict_hd_ban_ra)
                    if hasattr(self.giao_dien, 'kpi_hd_ban'):
                        self.giao_dien.kpi_hd_ban.cap_nhat(
                            gia_tri=f"{sl_br:,}".replace(',', '.') if sl_br > 0 else "0",
                            subtext=f"{sl_br} dòng hóa đơn" if sl_br > 0 else "Chưa nạp hóa đơn"
                        )

                    sl_mv = 0
                    if hasattr(self, 'dict_hd_mua_vao') and hasattr(self.dict_hd_mua_vao, '__len__'):
                        sl_mv = len(self.dict_hd_mua_vao)
                    if hasattr(self.giao_dien, 'kpi_hd_mua'):
                        self.giao_dien.kpi_hd_mua.cap_nhat(
                            gia_tri=f"{sl_mv:,}".replace(',', '.') if sl_mv > 0 else "0",
                            subtext=f"{sl_mv} dòng hóa đơn" if sl_mv > 0 else "Chưa nạp hóa đơn"
                        )
                except Exception:
                    pass

            def chon_nhieu_file_xml(self):
                duong_dan_files, _ = QFileDialog.getOpenFileNames(
                    self.giao_dien, "Chọn file XML tờ khai", "", "XML Files (*.xml)"
                )
                if not duong_dan_files: return

                for file in duong_dan_files:
                    if file not in self.danh_sach_file_xml_cho:
                        self.danh_sach_file_xml_cho.append(file)
                        self.toan_bo_file_xml.add(file)
                        ten_file = file.split('/')[-1]
                        self.giao_dien.danh_sach_file.addItem(f"[XML] {ten_file}")

                self.ghi_log(f"Đã nạp {len(duong_dan_files)} file XML vào hàng đợi.")
                self.cap_nhat_kpi_chuan_bi()

            def xu_ly_keo_tha_files(self, danh_sach_file_keo):
                """Tự động phân loại và nạp các file được kéo thả vào khu vực Drop-zone"""
                import os
                import pandas as pd
                from module_doc_hoadon.xu_ly_hoa_don_hub import doc_file_hoa_don_v2
                from module_giao_dien.quan_ly_bang_bieu import QuanLyBangBieu

                so_xml = 0
                so_br = 0
                so_mv = 0
                so_tt200 = 0

                for file_path in danh_sach_file_keo:
                    file_path = os.path.normpath(file_path)
                    ext = os.path.splitext(file_path)[1].lower()
                    ten_file = os.path.basename(file_path)

                    if ext == '.xml':
                        if file_path not in self.danh_sach_file_xml_cho:
                            self.danh_sach_file_xml_cho.append(file_path)
                            self.toan_bo_file_xml.add(file_path)
                            self.giao_dien.danh_sach_file.addItem(f"[XML] {ten_file}")
                            so_xml += 1
                    elif ext in ['.xlsx', '.xls', '.csv']:
                        ten_lower = ten_file.lower()
                        # Nhận diện Bảng cân đối số phát sinh TT200
                        if any(k in ten_lower for k in ['cdsps', 'cdps', 'tt200', 'cân đối']):
                            try:
                                from module_ho_tro.kiem_tra_excel import kiem_tra_file_upload
                                from module_ho_tro.tu_dien_tt200 import TU_DIEN_TK_TT200

                                is_valid, danh_sach_msg, df_sach, nam_phat_hien = kiem_tra_file_upload(file_path, TU_DIEN_TK_TT200)
                                if is_valid and df_sach is not None and not df_sach.empty:
                                    nam_nhap = str(nam_phat_hien) if nam_phat_hien else ""
                                    if not nam_nhap:
                                        if hasattr(self.giao_dien, 'cb_nam_kq') and self.giao_dien.cb_nam_kq.currentText():
                                            nam_nhap = self.giao_dien.cb_nam_kq.currentText()
                                        elif self.du_lieu_he_thong_to_khai:
                                            cac_nam_tk = []
                                            for m_f, d_k in self.du_lieu_he_thong_to_khai.items():
                                                for k in d_k.keys():
                                                    try:
                                                        cac_nam_tk.append(int(str(k)[-4:]))
                                                    except Exception:
                                                        pass
                                            nam_nhap = str(max(cac_nam_tk)) if cac_nam_tk else "2024"
                                        else:
                                            nam_nhap = "2024"

                                    if not isinstance(self.du_lieu_bcdsps_tt200, dict):
                                        self.du_lieu_bcdsps_tt200 = {}

                                    self.du_lieu_bcdsps_tt200[nam_nhap] = df_sach
                                    self.giao_dien.cb_bctc.setCurrentIndex(1)  # Chọn TT200
                                    self.giao_dien.btn_nap_tt200.setStyleSheet("background-color: #D1FAE5; border: 1px solid #10B981;")

                                    item_label = f"[Excel] CĐSPS TT200 - Năm {nam_nhap} ({len(df_sach)} TK) - Sẵn sàng"
                                    for idx_f in range(self.giao_dien.danh_sach_file.count()):
                                        it = self.giao_dien.danh_sach_file.item(idx_f)
                                        if it and f"CĐSPS TT200 - Năm {nam_nhap}" in it.text():
                                            self.giao_dien.danh_sach_file.takeItem(idx_f)
                                            break
                                    self.giao_dien.danh_sach_file.addItem(item_label)

                                    self._ve_bang_cdsps_len_ui(df_sach, nam=nam_nhap)
                                    self.ghi_log(f"✅ Đã nạp thành công Bảng CĐSPS năm {nam_nhap} ({len(df_sach)} tài khoản) từ file {ten_file}")
                                    so_tt200 += 1
                                else:
                                    loi_str = "; ".join(danh_sach_msg[:3]) if danh_sach_msg else "Dữ liệu không hợp lệ"
                                    self.ghi_log(f"❌ File CĐSPS {ten_file} không hợp lệ: {loi_str}")
                            except Exception as e:
                                self.ghi_log(f"❌ Lỗi nạp CĐSPS TT200 từ {ten_file}: {e}")
                        # Nhận diện HĐ Mua vào
                        elif any(k in ten_lower for k in ['mua_vao', 'muavao', 'mua vào', '_in', 'input', 'đầu vào']):
                            try:
                                df = doc_file_hoa_don_v2(file_path, is_mua_vao=True)
                                if df is not None and not df.empty:
                                    if hasattr(self, 'dict_hd_mua_vao') and isinstance(self.dict_hd_mua_vao, pd.DataFrame) and not self.dict_hd_mua_vao.empty:
                                        self.dict_hd_mua_vao = pd.concat([self.dict_hd_mua_vao, df], ignore_index=True)
                                    else:
                                        self.dict_hd_mua_vao = df
                                    QuanLyBangBieu.xu_ly_bang_ke(self.giao_dien.bang_hd_mua_vao, self.dict_hd_mua_vao)
                                    QuanLyBangBieu.cau_hinh_bang_du_lieu(self.giao_dien.bang_hd_mua_vao)
                                    QuanLyBangBieu.can_bang_kich_thuoc_bang(self.giao_dien.bang_hd_mua_vao)
                                    self.giao_dien.danh_sach_file.addItem(f"[HĐ MUA VÀO] {ten_file}")
                                    so_mv += 1
                            except Exception as e:
                                self.ghi_log(f"Lỗi đọc HĐ mua vào {ten_file}: {e}")
                        # Mặc định còn lại ưu tiên HĐ Bán ra
                        else:
                            is_mua = any(k in ten_lower for k in ['mua', 'cost', 'expense'])
                            try:
                                df = doc_file_hoa_don_v2(file_path, is_mua_vao=is_mua)
                                if df is not None and not df.empty:
                                    if is_mua:
                                        if hasattr(self, 'dict_hd_mua_vao') and isinstance(self.dict_hd_mua_vao, pd.DataFrame) and not self.dict_hd_mua_vao.empty:
                                            self.dict_hd_mua_vao = pd.concat([self.dict_hd_mua_vao, df], ignore_index=True)
                                        else:
                                            self.dict_hd_mua_vao = df
                                        QuanLyBangBieu.xu_ly_bang_ke(self.giao_dien.bang_hd_mua_vao, self.dict_hd_mua_vao)
                                        self.giao_dien.danh_sach_file.addItem(f"[HĐ MUA VÀO] {ten_file}")
                                        so_mv += 1
                                    else:
                                        if hasattr(self, 'dict_hd_ban_ra') and isinstance(self.dict_hd_ban_ra, pd.DataFrame) and not self.dict_hd_ban_ra.empty:
                                            self.dict_hd_ban_ra = pd.concat([self.dict_hd_ban_ra, df], ignore_index=True)
                                        else:
                                            self.dict_hd_ban_ra = df
                                        QuanLyBangBieu.xu_ly_bang_ke(self.giao_dien.bang_hd_ban_ra, self.dict_hd_ban_ra)
                                        self.giao_dien.danh_sach_file.addItem(f"[HĐ BÁN RA] {ten_file}")
                                        so_br += 1
                            except Exception as e:
                                self.ghi_log(f"Lỗi đọc file hóa đơn {ten_file}: {e}")

                thong_bao = []
                if so_xml: thong_bao.append(f"{so_xml} file XML")
                if so_br: thong_bao.append(f"{so_br} file HĐ Bán ra")
                if so_mv: thong_bao.append(f"{so_mv} file HĐ Mua vào")
                if so_tt200: thong_bao.append(f"{so_tt200} file Bảng CĐSPS")

                if thong_bao:
                    self.ghi_log(f"⚡ Đã kéo thả thành công: {', '.join(thong_bao)}")
                self.cap_nhat_kpi_chuan_bi()

            def thuc_thi_phan_tich(self):
                """Hàm kích hoạt khi bấm nút Phân tích"""
                loai_bctc = self.giao_dien.cb_bctc.currentText()
                nam_pt = self.giao_dien.cb_nam.currentText()
                check_tms = "Có" if self.giao_dien.chk_tms.isChecked() else "Không"

                self.ghi_log("-" * 50)
                self.ghi_log(f"BẮT ĐẦU PHIÊN PHÂN TÍCH | BCTC: {loai_bctc} | Năm: {nam_pt} | Ktra TMS: {check_tms}")
                if hasattr(self.giao_dien, 'kpi_trang_thai'):
                    self.giao_dien.kpi_trang_thai.cap_nhat(gia_tri="Đang chạy", subtext="Đang phân tích...")

                if not self.danh_sach_file_xml_cho:
                    self.ghi_log("Đang tải lại giao diện Tờ khai từ bộ nhớ RAM...")

                    # 1. Quét sạch các Tab Tờ khai trên giao diện
                    while self.giao_dien.tab_tong_hop_chi_tiet.count() > 0:
                        self.giao_dien.tab_tong_hop_chi_tiet.removeTab(0)

                    # 2. Xóa widget KHBS cũ để khởi tạo lại sạch sẽ
                    self.dict_khbs_widgets.clear()

                    # 3. Lôi dữ liệu tờ khai từ RAM ra, nhồi lại vào hàm vẽ bảng
                    for form, dict_ky in self.du_lieu_he_thong_to_khai.items():
                        for ky, ket_qua in dict_ky.items():
                            # Hàm này sẽ tự động check cb_nam trên giao diện để quyết định vẽ hay không vẽ
                            self.cap_nhat_bang_tong_hop(ket_qua)

                    # 4. Nạp lại cấu hình cho Widget KHBS
                    tu_ky = f"01/{nam_pt}" if nam_pt != "Tất cả các năm" else ""
                    den_ky = f"12/{nam_pt}" if nam_pt != "Tất cả các năm" else ""
                    for tk_loai, w_khbs in self.dict_khbs_widgets.items():
                        w_khbs.set_data(list(self.toan_bo_file_xml))
                        idx = w_khbs.cbo_type.findText(tk_loai)
                        if idx >= 0: w_khbs.cbo_type.setCurrentIndex(idx)
                        w_khbs.set_refund_period(tu_ky, den_ky)

                    # Nhảy sang chạy Engine phân tích
                    self.chay_engine_phan_tich()
                    return

                # ... (Phần code bên dưới giữ nguyên) ...
                self.ghi_log("Đang phân tích cấu trúc Tờ khai XML...")
                # Lấy số lượng file chờ gán cho biến đếm
                self.so_luong_xml_dang_chay = len(self.danh_sach_file_xml_cho)

                # Vòng lặp kích hoạt luồng đọc từng file
                for file in self.danh_sach_file_xml_cho:
                    self.xu_ly_doc_xml(file)

                # Làm sạch danh sách để chuẩn bị cho lần nạp dữ liệu ở phiên làm việc sau
                self.danh_sach_file_xml_cho = []

            def xu_ly_doc_xml(self, duong_dan_file):
                luong_xml = LuongXuLy(self.quan_ly_xml.xu_ly_file_xml, duong_dan_file)
                luong_xml.ket_qua_tra_ve.connect(self.hoan_thanh_doc_xml)
                luong_xml.bao_loi.connect(self.loi_doc_xml)

                self.danh_sach_luong.append(luong_xml)
                luong_xml.start()

            def hoan_thanh_doc_xml(self, ket_qua):
                try:
                    self._thuc_thi_hoan_thanh_doc_xml(ket_qua)
                except Exception as e:
                    self.ghi_log(f"❌ Lỗi xử lý kết quả đọc XML: {e}")
                finally:
                    self.so_luong_xml_dang_chay -= 1
                    if self.so_luong_xml_dang_chay <= 0:
                        nam_pt = self.giao_dien.cb_nam.currentText()
                        tu_ky = f"01/{nam_pt}" if nam_pt != "Tất cả các năm" else ""
                        den_ky = f"12/{nam_pt}" if nam_pt != "Tất cả các năm" else ""

                        for tk_loai, w_khbs in self.dict_khbs_widgets.items():
                            w_khbs.set_data(list(self.toan_bo_file_xml))
                            idx = w_khbs.cbo_type.findText(tk_loai)
                            if idx >= 0:
                                w_khbs.cbo_type.setCurrentIndex(idx)
                            w_khbs.set_refund_period(tu_ky, den_ky)

                        self.chay_engine_phan_tich()

            def _thuc_thi_hoan_thanh_doc_xml(self, ket_qua):
                ma_tk = ket_qua.get("ThongTinChung", {}).get("MaTKhai", "N/A")
                ky_ke_khai = ket_qua.get("ThongTinChung", {}).get("KyKeKhai", "N/A")

                # =====================================================================
                # TRẠM KIỂM SOÁT PHÂN QUYỀN CƠ QUAN THUẾ (CHỐNG XÀI CHÙA)
                # =====================================================================
                ma_cqt_ho_so = ket_qua.get("ThongTinChung", {}).get("maCQTNoiNop", "").strip()
                ds_cqt_duoc_phep = getattr(self, 'allowed_cqt', [])

                if "*" not in ds_cqt_duoc_phep:
                    if not ma_cqt_ho_so:
                        self.ghi_log(f"⚠️ CẢNH BÁO: Không tìm thấy Mã CQT trên tờ khai [{ma_tk}], kỳ {ky_ke_khai}.")
                    elif ma_cqt_ho_so not in ds_cqt_duoc_phep:
                        thong_diep_tu_choi = f"Hồ sơ không thuộc CQT đã đăng ký, tài khoản của bạn không được cấp quyền phân tích dữ liệu tại CQT này!"
                        self.ghi_log(thong_diep_tu_choi)
                        return
                # =====================================================================

                ten_form = MAP_TEN_TO_KHAI.get(ma_tk, ma_tk)
                thong_tin_chung = ket_qua.get("ThongTinChung", {})

                # --- BỔ SUNG HÀM HỖ TRỢ XỬ LÝ LỖI TRỐNG DỮ LIỆU ---
                def lay_so_lan(thong_tin_dict):
                    val = thong_tin_dict.get("LanBoSung")
                    if val is None or str(val).strip() == "":
                        val = thong_tin_dict.get("SoLan", 0)
                    try:
                        return int(val)
                    except (ValueError, TypeError):
                        return 0

                # Lấy số Lần bổ sung của file đang xử lý an toàn
                lan_bs_moi = lay_so_lan(thong_tin_chung)

                if ten_form not in self.du_lieu_he_thong_to_khai:
                    self.du_lieu_he_thong_to_khai[ten_form] = {}

                # =====================================================================
                # LOGIC MỚI: CHỈ LƯU VÀ VẼ PHIÊN BẢN CÓ LẦN BỔ SUNG LỚN NHẤT
                # =====================================================================
                ve_len_giao_dien = False

                if ky_ke_khai in self.du_lieu_he_thong_to_khai[ten_form]:
                    to_khai_cu = self.du_lieu_he_thong_to_khai[ten_form][ky_ke_khai]
                    # Ép kiểu an toàn cho tờ khai cũ để chống lỗi ValueError
                    lan_bs_cu = lay_so_lan(to_khai_cu.get("ThongTinChung", {}))

                    if lan_bs_moi > lan_bs_cu:
                        # Ghi đè bản mới nhất vào RAM
                        self.du_lieu_he_thong_to_khai[ten_form][ky_ke_khai] = ket_qua
                        ve_len_giao_dien = True
                else:
                    # Kỳ này chưa có trong RAM -> Lưu mới
                    self.du_lieu_he_thong_to_khai[ten_form][ky_ke_khai] = ket_qua
                    ve_len_giao_dien = True

                # Chỉ vẽ lên màn hình nếu thực sự nạp bản mới
                if ve_len_giao_dien:
                    self.ghi_log(
                        f"-> Phân tích thành công: Tờ khai mã [{ma_tk}], kỳ {ky_ke_khai} (Lần bổ sung: {lan_bs_moi}).")
                    self.cap_nhat_bang_tong_hop(ket_qua)
                else:
                    self.ghi_log(
                        f"-> Bỏ qua Tờ khai mã [{ma_tk}], kỳ {ky_ke_khai} (Lần {lan_bs_moi}) do đã nạp bản mới hơn.")

            def chay_engine_phan_tich(self):
                from module_ho_tro.module_cau_hinh_tms import TMSConfig, DialogCauHinhTMS
                from module_ho_tro.module_dong_bo_tms import BotSAPWorker
                from PySide6.QtWidgets import QMessageBox, QProgressDialog
                from PySide6.QtCore import Qt
                import os
                from datetime import datetime

                self.ghi_log("\n" + "=" * 40)
                self.ghi_log("🚀 KHỞI ĐỘNG PHÂN TÍCH RỦI RO")
                self.ghi_log("=" * 40)

                # ==============================================================
                # CỬA KHẨU 1: BOT ĐỒNG BỘ NGÀY NỘP KHBS TỪ SAP
                # ==============================================================
                if hasattr(self.giao_dien, 'chk_dong_bo_ngay') and self.giao_dien.chk_dong_bo_ngay.isChecked():
                    config = TMSConfig.load()

                    # RÀ SOÁT CẤU HÌNH: Nếu chưa có Tài khoản/Mật khẩu -> Ép nhập
                    if not config.get("user_tms") or not config.get("pass_tms"):
                        QMessageBox.warning(self.giao_dien, "Chưa cấu hình",
                                            "Vui lòng nhập Tài khoản và Mật khẩu SAP trước khi đồng bộ!")
                        dialog = DialogCauHinhTMS(self.giao_dien)
                        dialog.exec()
                        config = TMSConfig.load()
                        # Vẫn không chịu nhập thì hủy toàn bộ tiến trình
                        if not config.get("user_tms"):
                            self.ghi_log("⚠️ Hủy phân tích do chưa cấu hình SAP.")
                            return

                    self.ghi_log("⏳ Bắt đầu luồng kiểm tra dữ liệu từ TMS...")

                    # 1. TỰ ĐỘNG NỘI SUY NGÀY & MST TỪ DỮ LIỆU ĐÃ NẠP
                    cac_nam = []
                    mst_he_thong = "ChuaXacDinh"
                    for ma_form, dict_ky in self.du_lieu_he_thong_to_khai.items():
                        for ky, val in dict_ky.items():
                            try:
                                cac_nam.append(int(str(ky)[-4:]))
                            except:
                                pass
                            if mst_he_thong == "ChuaXacDinh":
                                mst_he_thong = val.get("ThongTinChung", {}).get("MST", "ChuaXacDinh")

                    nam_nho_nhat = min(cac_nam) if cac_nam else datetime.now().year
                    # Nếu trong config không ghim ngày -> Tự động nội suy
                    tu_ngay = config.get("tu_ngay") if config.get("tu_ngay") else f"01.01.{nam_nho_nhat}"
                    den_ngay = config.get("den_ngay") if config.get("den_ngay") else datetime.now().strftime("%d.%m.%Y")
                    cqt = config.get("cqt", "50500")

                    # 2. XÁC ĐỊNH CACHE FILE
                    ngay_tai = datetime.now().strftime("%d%m%Y")
                    ten_file = f"TMS_{mst_he_thong}_{ngay_tai}_{tu_ngay.replace('.', '')}_{den_ngay.replace('.', '')}.xlsx"

                    # File hệ thống trả về đường dẫn gốc, nếu biên dịch file exe nhớ xử lý path
                    thu_muc_data = os.path.join(os.getcwd(), "Data", "Dulieukekhai")
                    os.makedirs(thu_muc_data, exist_ok=True)
                    duong_dan_cache = os.path.join(thu_muc_data, ten_file)

                    # HỎI CACHE: Nếu đã có file thì hỏi xem có muốn chạy lại không
                    if os.path.exists(duong_dan_cache):
                        hoi = QMessageBox.question(
                            self.giao_dien, "Phát hiện Dữ liệu có sẵn",
                            f"Đã có file danh sách tờ khai của MST {mst_he_thong} tải trong hôm nay.\n\nChọn [YES] để dùng file cũ cho nhanh, hoặc [NO] để mở SAP tải mới hoàn toàn.",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if hoi == QMessageBox.StandardButton.No:
                            os.remove(duong_dan_cache)  # Bấm NO -> Xóa để Bot tải mới

                    # 3. MỞ SPINNER ANIMATION (KHÔNG LÀM ĐƠ GIAO DIỆN)
                    self.loading_dialog = QProgressDialog("Khởi động Bot SAP...", None, 0, 0, self.giao_dien)
                    self.loading_dialog.setWindowTitle("Đang đồng bộ TMS")
                    self.loading_dialog.setWindowModality(Qt.WindowModality.WindowModal)
                    self.loading_dialog.setStyleSheet(
                        "QProgressBar { border: 1px solid #D1D5DB; border-radius: 4px; text-align: center; } QProgressBar::chunk { background-color: #10B981; }")
                    self.loading_dialog.show()

                    # 4. BẮN VÀO QTHREAD ĐỂ CHẠY NGẦM
                    self.tms_thread = BotSAPWorker(cqt, tu_ngay, den_ngay, mst_he_thong, self.du_lieu_he_thong_to_khai,
                                                   config["user_tms"], config["pass_tms"], duong_dan_cache)

                    def on_tms_progress(msg):
                        self.loading_dialog.setLabelText(msg)

                    def on_tms_finished(thanh_cong, ket_qua, so_luong):
                        self.loading_dialog.close()
                        if thanh_cong:
                            self.ghi_log(
                                f"   ✅ Đã đồng bộ ngày nộp thực tế cho {so_luong} Tờ khai (Nguồn: {os.path.basename(ket_qua)})")
                        else:
                            self.ghi_log(f"   ❌ Lỗi đồng bộ TMS: {ket_qua}")
                            QMessageBox.warning(self.giao_dien, "Lỗi SAP", f"Tiến trình đồng bộ thất bại:\n{ket_qua}")

                        # ---> BOT CHẠY XONG THÌ MỚI GỌI HÀM PHÂN TÍCH TIẾP THEO <---
                        self._tiep_tuc_phan_tich_sau_dong_bo()

                    self.tms_thread.progress.connect(on_tms_progress)
                    self.tms_thread.finished.connect(on_tms_finished)
                    self.tms_thread.start()

                    # Bắt buộc RETURN ở đây để hàm tạm dừng, nhường UI cho QThread chạy
                    return

                    # ==============================================================
                # NẾU KHÔNG BẬT ĐỒNG BỘ TMS -> NHẢY THẲNG ĐẾN HÀM PHÂN TÍCH
                # ==============================================================
                self._tiep_tuc_phan_tich_sau_dong_bo()

            def _tiep_tuc_phan_tich_sau_dong_bo(self):
                """Hàm này chứa TẤT CẢ logic Phân tích (Tình trạng MST, Báo cáo rủi ro...)
                   Được gọi tự động sau khi quá trình tải TMS hoàn tất"""
                from module_phan_tich.engine_tinh_toan import EnginePhanTich
                from PySide6.QtGui import QColor
                from PySide6.QtWidgets import QTableWidgetItem, QMessageBox, QTableWidget, QWidget, QVBoxLayout
                from module_ho_tro.sap_worker import SAPWorker
                import pandas as pd

                nam_pt = self.giao_dien.cb_nam.currentText()
                loai_bctc = self.giao_dien.cb_bctc.currentText()

                # 1. KIỂM TRA TRẠNG THÁI DOANH NGHIỆP TRONG HÓA ĐƠN TỪ SAP
                if hasattr(self.giao_dien, 'chk_tms') and self.giao_dien.chk_tms.isChecked():
                    self.ghi_log("🔍 Đang tra cứu trạng thái TMS...")

                    mst_can_tra_cuu = set()
                    col_mua_vao = ""
                    col_ban_ra = ""

                    if isinstance(self.dict_hd_mua_vao, pd.DataFrame):
                        if 'Mã số thuế người bán' in self.dict_hd_mua_vao.columns:
                            col_mua_vao = 'Mã số thuế người bán'
                        elif 'MSTNguoiBan' in self.dict_hd_mua_vao.columns:
                            col_mua_vao = 'MSTNguoiBan'
                        if col_mua_vao:
                            mst_can_tra_cuu.update(self.dict_hd_mua_vao[col_mua_vao].dropna().astype(str).unique())

                    if isinstance(self.dict_hd_ban_ra, pd.DataFrame):
                        if 'MST người mua' in self.dict_hd_ban_ra.columns:
                            col_ban_ra = 'MST người mua'
                        elif 'MSTNguoiMua' in self.dict_hd_ban_ra.columns:
                            col_ban_ra = 'MSTNguoiMua'
                        if col_ban_ra:
                            mst_can_tra_cuu.update(self.dict_hd_ban_ra[col_ban_ra].dropna().astype(str).unique())

                    mst_can_tra_cuu = [mst.strip() for mst in mst_can_tra_cuu if mst.strip() != ""]

                    if mst_can_tra_cuu:
                        self.ghi_log(f"   Chuẩn bị quét {len(mst_can_tra_cuu)} Mã số thuế qua TMS...")

                        sap_robot = SAPWorker(mst_can_tra_cuu)
                        sap_robot.progress.connect(lambda step, msg: self.ghi_log(f"   [TMS] {msg}"))
                        sap_robot.error.connect(lambda msg: self.ghi_log(f"   ❌ [LỖI TMS] {msg}"))

                        ket_qua_tms = sap_robot.run_check()

                        if ket_qua_tms:
                            self.ghi_log(
                                f"   ✅ Nhận thành công {len(ket_qua_tms)} kết quả. Đang map vào bảng và tô màu cảnh báo...")

                            df_tms = pd.DataFrame(ket_qua_tms, columns=['MST_SAP', 'TenNNT', 'CQT_TMS', 'MaTrangThai',
                                                                        'TrangThaiTMS', 'NgayCapNhat'])
                            df_map = df_tms[['MST_SAP', 'TrangThaiTMS', 'CQT_TMS']].drop_duplicates(subset=['MST_SAP'])

                            def _xu_ly_map_va_to_mau(df_hd, bang_widget, col_mst):
                                if not isinstance(df_hd, pd.DataFrame) or df_hd.empty or not col_mst: return df_hd

                                for col in ['TrangThaiTMS', 'CQT_TMS']:
                                    if col in df_hd.columns: df_hd.drop(columns=[col], inplace=True)

                                df_new = pd.merge(df_hd, df_map, how='left', left_on=col_mst, right_on='MST_SAP')
                                df_new['TrangThaiTMS'] = df_new['TrangThaiTMS'].fillna('Chưa xác định')
                                df_new['CQT_TMS'] = df_new['CQT_TMS'].fillna('')
                                df_new.drop(columns=['MST_SAP'], inplace=True, errors='ignore')

                                from module_giao_dien.quan_ly_bang_bieu import QuanLyBangBieu
                                QuanLyBangBieu.xu_ly_bang_ke(bang_widget, df_new)
                                QuanLyBangBieu.cau_hinh_bang_du_lieu(bang_widget)

                                tu_khoa_do = ["không hoạt động tại địa chỉ", "chờ xác minh"]
                                tu_khoa_vang = ["ngừng hoạt động nhưng chưa hoàn thành", "tạm nghỉ kinh doanh"]

                                idx_tms = df_new.columns.get_loc('TrangThaiTMS')
                                idx_hd_goc = df_new.columns.get_loc(
                                    'Trạng thái hóa đơn') if 'Trạng thái hóa đơn' in df_new.columns else -1

                                for row in range(bang_widget.rowCount()):
                                    tt_tms = str(df_new.iloc[row, idx_tms]).lower()
                                    tt_hd_goc = str(df_new.iloc[row, idx_hd_goc]).lower() if idx_hd_goc != -1 else ""

                                    is_do = any(k in tt_tms for k in tu_khoa_do) or "hủy" in tt_hd_goc
                                    is_vang = any(k in tt_tms for k in tu_khoa_vang)

                                    if is_do or is_vang:
                                        bg_color = QColor("#fee2e2") if is_do else QColor("#fef08a")
                                        for col in range(bang_widget.columnCount()):
                                            item = bang_widget.item(row, col)
                                            if item: item.setBackground(bg_color)
                                return df_new

                            self.dict_hd_mua_vao = _xu_ly_map_va_to_mau(self.dict_hd_mua_vao,
                                                                        self.giao_dien.bang_hd_mua_vao, col_mua_vao)
                            self.dict_hd_ban_ra = _xu_ly_map_va_to_mau(self.dict_hd_ban_ra,
                                                                       self.giao_dien.bang_hd_ban_ra, col_ban_ra)

                            # TẠO BẢNG TỔNG HỢP NNT CÓ TRẠNG THÁI BẤT THƯỜNG
                            trang_thai_an_toan = ['00', '01', '04']
                            df_bat_thuong = df_tms[
                                ~df_tms['MaTrangThai'].astype(str).str.strip().isin(trang_thai_an_toan)].copy()

                            if not df_bat_thuong.empty:
                                df_bat_thuong.rename(columns={'MST_SAP': 'Mã số thuế', 'TenNNT': 'Tên người nộp thuế',
                                                              'CQT_TMS': 'Cơ quan thuế quản lý', 'MaTrangThai': 'Mã TT',
                                                              'TrangThaiTMS': 'Trạng thái hoạt động',
                                                              'NgayCapNhat': 'Ngày cập nhật'}, inplace=True)
                                tab_idx = -1
                                for i in range(self.giao_dien.tabs_hoa_don.count()):
                                    if self.giao_dien.tabs_hoa_don.tabText(i) == "NNT Bất thường (TMS)":
                                        tab_idx = i
                                        break

                                if tab_idx != -1:
                                    widget_th = self.giao_dien.tabs_hoa_don.widget(tab_idx)
                                    bang_th = widget_th.findChild(QTableWidget)
                                else:
                                    widget_th = QWidget()
                                    layout_th = QVBoxLayout(widget_th)
                                    layout_th.setContentsMargins(0, 0, 0, 0)
                                    bang_th = QTableWidget()
                                    layout_th.addWidget(bang_th)
                                    import qtawesome as qta
                                    self.giao_dien.tabs_hoa_don.addTab(widget_th, qta.icon('fa5s.exclamation-circle',
                                                                                           color='#DC2626'),
                                                                       "NNT Bất thường (TMS)")

                                from module_giao_dien.quan_ly_bang_bieu import QuanLyBangBieu
                                QuanLyBangBieu.xu_ly_bang_ke(bang_th, df_bat_thuong)
                                QuanLyBangBieu.cau_hinh_bang_du_lieu(bang_th)
                                QuanLyBangBieu.can_bang_kich_thuoc_bang(bang_th)

                                bg_color = QColor("#fee2e2")
                                for r in range(bang_th.rowCount()):
                                    for c in range(bang_th.columnCount()):
                                        item = bang_th.item(r, c)
                                        if item: item.setBackground(bg_color)
                                self.ghi_log(f"   🚨 Đã tổng hợp {len(df_bat_thuong)} NNT bất thường sang Tab riêng!")
                            else:
                                self.ghi_log("   ✅ 100% NNT tra cứu đều có trạng thái an toàn (00, 01, 04).")
                        else:
                            self.ghi_log("   ⚠️ Tiến trình chạy xong nhưng không thu thập được dữ liệu từ TMS.")
                    else:
                        self.ghi_log("   ⚠️ Không tìm thấy Mã số thuế hợp lệ trong dữ liệu Hóa đơn để tra cứu.")
                else:
                    self.ghi_log("⏭️ Bỏ qua bước tra cứu TMS (Người dùng không tích chọn).")

                # =================================================================
                # 2. CHẠY ENGINE PHÂN TÍCH RỦI RO (PHÂN TÁCH ĐỘC LẬP TỪNG NĂM)
                # =================================================================
                self.ghi_log("⚙️ Đang phân tích rủi ro tài chính...")

                # Tạo danh sách các năm cần phân tích
                danh_sach_nam = []
                if nam_pt != "Tất cả các năm":
                    danh_sach_nam = [nam_pt]
                else:
                    cac_nam = set()
                    for form, dict_ky in self.du_lieu_he_thong_to_khai.items():
                        for ky in dict_ky.keys():
                            try:
                                cac_nam.add(str(ky)[-4:])
                            except:
                                pass
                    danh_sach_nam = sorted(list(cac_nam)) if cac_nam else [str(datetime.now().year)]

                self.kho_ket_qua_nam = {}
                dict_tong = QuanLyCongThuc.tai_du_lieu_tong_hop()

                # Tối ưu: Lọc hóa đơn rác 1 lần duy nhất ở bên ngoài vòng lặp
                from module_phan_tich.bao_cao_doanh_so import BaoCaoDoanhSoEngine
                from module_doc_hoadon.invoice_processor import InvoiceProcessor
                df_br_sach_all = InvoiceProcessor.loc_hoa_don_tinh_toan(self.dict_hd_ban_ra)
                df_mv_sach_all = InvoiceProcessor.loc_hoa_don_tinh_toan(self.dict_hd_mua_vao)

                for nam in danh_sach_nam:
                    self.ghi_log(f"⚙️ Phân tích dữ liệu năm {nam}...")

                    # A. Chạy Engine Rủi ro cho riêng năm này
                    engine = EnginePhanTich(dict_cong_thuc=dict_tong, log_callback=self.ghi_log)
                    ket_qua_list = engine.thuc_thi_phan_tich(
                        self.du_lieu_he_thong_to_khai, self.dict_hd_ban_ra, self.dict_hd_mua_vao,
                        nam_phan_tich=nam, df_cdsps_tt200=self.du_lieu_bcdsps_tt200,
                        loai_bctc=loai_bctc, danh_sach_rule_chon=self.danh_sach_rule_duoc_chon
                    )

                    # B. Tính Doanh số cho riêng năm này
                    du_lieu_br = BaoCaoDoanhSoEngine.xuat_du_lieu_bao_cao(df_br_sach_all, self.du_lieu_he_thong_to_khai,
                                                                          nam, False, self.ghi_log)
                    du_lieu_mv = BaoCaoDoanhSoEngine.xuat_du_lieu_bao_cao(df_mv_sach_all, self.du_lieu_he_thong_to_khai,
                                                                          nam, True, self.ghi_log)

                    # C. Đóng gói cất vào Kho RAM
                    self.kho_ket_qua_nam[nam] = {
                        "ket_qua_list": ket_qua_list,
                        "du_lieu_ban_ra": du_lieu_br,
                        "du_lieu_mua_vao": du_lieu_mv,
                        "df_br_sach": df_br_sach_all,
                        "df_mv_sach": df_mv_sach_all
                    }

                # Bơm các năm vào Combobox để giao diện hiển thị
                if hasattr(self.giao_dien, 'cb_nam_kq'):
                    self.giao_dien.cb_nam_kq.blockSignals(True)
                    self.giao_dien.cb_nam_kq.clear()
                    self.giao_dien.cb_nam_kq.addItems(danh_sach_nam)
                    self.giao_dien.cb_nam_kq.blockSignals(False)

                # Ra lệnh cho Giao diện tự động móc RAM ra vẽ cho năm đầu tiên
                self.chuyen_view_ket_qua_nam(danh_sach_nam[0])

                # ==============================================================
                # 3. BƠM DỮ LIỆU ĐỐI CHIẾU TỒN KHO
                # (Phần này liên quan đến kho chung toàn kỳ, giữ nguyên không chuyển)
                # ==============================================================
                if hasattr(self.giao_dien, 'tabs_hoa_don'):
                    try:
                        if isinstance(self.dict_hd_mua_vao, pd.DataFrame) and isinstance(self.dict_hd_ban_ra,
                                                                                         pd.DataFrame):
                            if not self.dict_hd_mua_vao.empty or not self.dict_hd_ban_ra.empty:

                                # TỒN KHO CƠ BẢN
                                self.ghi_log("📦 Đang rà soát đối chiếu Tồn kho...")
                                from module_phan_tich.inventory_matcher import InventoryReconcilerLight
                                from module_giao_dien.builder_phan_tich_ton_kho import BuilderPhanTichTonKho
                                import qtawesome as qta

                                reconciler_old = InventoryReconcilerLight(self.dict_hd_mua_vao, self.dict_hd_ban_ra)
                                kq_ton_kho = reconciler_old.analyze_inventory()

                                if kq_ton_kho:
                                    tab_idx_old = -1
                                    for i in range(self.giao_dien.tabs_hoa_don.count()):
                                        if self.giao_dien.tabs_hoa_don.tabText(i) == "Rà soát Tồn kho":
                                            tab_idx_old = i
                                            break

                                    if tab_idx_old != -1:
                                        widget_ton_kho_old = self.giao_dien.tabs_hoa_don.widget(tab_idx_old)
                                        widget_ton_kho_old.nap_du_lieu(kq_ton_kho)
                                    else:
                                        widget_ton_kho_old = BuilderPhanTichTonKho(kq_ton_kho)
                                        self.giao_dien.tabs_hoa_don.addTab(widget_ton_kho_old,
                                                                           qta.icon('fa5s.boxes', color='#059669'),
                                                                           "Rà soát Tồn kho")
                                    self.ghi_log("   ✅ Đã tổng hợp thành công báo cáo Tồn kho.")

                                # TỒN KHO AI
                                self.ghi_log("🤖 Đang khởi động rà soát đối chiếu tên mặt hàng...")
                                from module_giao_dien.inventory_widget import InventoryAnalysisWidget
                                from module_phan_tich.inventory_worker import InventoryAnalysisWorker
                                from PySide6.QtCore import QThread

                                tab_idx_ai = -1
                                for i in range(self.giao_dien.tabs_hoa_don.count()):
                                    if self.giao_dien.tabs_hoa_don.tabText(i) == "Đối chiếu tên mặt hàng":
                                        tab_idx_ai = i
                                        break

                                if tab_idx_ai != -1:
                                    widget_ton_kho_ai = self.giao_dien.tabs_hoa_don.widget(tab_idx_ai)
                                else:
                                    widget_ton_kho_ai = InventoryAnalysisWidget()
                                    self.giao_dien.tabs_hoa_don.addTab(widget_ton_kho_ai,
                                                                       qta.icon('fa5s.robot', color='#059669'),
                                                                       "Đối chiếu tên mặt hàng")

                                widget_ton_kho_ai.update_status_label("Đang khởi động...")

                                self.inv_thread = QThread()
                                self.inv_worker = InventoryAnalysisWorker(self.dict_hd_mua_vao, self.dict_hd_ban_ra)
                                self.inv_worker.moveToThread(self.inv_thread)

                                self.inv_thread.started.connect(self.inv_worker.run_analysis)
                                self.inv_worker.progress_text.connect(widget_ton_kho_ai.update_status_label)
                                self.inv_worker.progress_text.connect(lambda msg: self.ghi_log(f"  {msg}"))

                                def _on_inventory_finished(matcher, df_result):
                                    widget_ton_kho_ai.load_precalculated_data(matcher, self.dict_hd_mua_vao,
                                                                              self.dict_hd_ban_ra)
                                    self.inv_thread.quit()
                                    self.ghi_log("   ✅ Đã phân tích đối chiếu bằng AI thành công.")

                                self.inv_worker.finished.connect(_on_inventory_finished)
                                self.inv_worker.error.connect(lambda e: self.ghi_log(f"   ❌ [LỖI] {e}"))
                                self.inv_thread.start()

                    except Exception as e:
                        self.ghi_log(f"   ❌ [LỖI KHỞI TẠO TỒN KHO] Quá trình rà soát bị lỗi: {e}")

                self.ghi_log("✅ Phân tích tổng thể hoàn tất. Đang trích xuất báo cáo...")
                QMessageBox.information(self.giao_dien, "Hoàn tất",
                                        "Quá trình rà soát và đối chiếu đã thành công!\n\nHệ thống đã sẵn sàng. Nhấn 'OK' để xem chi tiết Bảng kết quả phân tích.")
                self.chuyen_tab(4)

            def loi_doc_xml(self, thong_bao_loi):
                self.ghi_log(f"[LỖI] Lỗi phân tích XML: {thong_bao_loi}")

                # Nếu lỗi cũng phải trừ đi 1 để tránh hệ thống bị treo đơ
                self.so_luong_xml_dang_chay -= 1
                if self.so_luong_xml_dang_chay <= 0:
                    self.chay_engine_phan_tich()
            def tai_template_tt200(self):
                """Hành động khi bấm nút tải file Excel mẫu"""
                from module_ho_tro.tao_template_excel import tao_file_mau_cdsps
                duong_dan, _ = QFileDialog.getSaveFileName(
                    self.giao_dien, "Lưu file Mẫu Bảng CĐSPS", "Bang_CDSPS_TT200_Template.xlsx", "Excel Files (*.xlsx)"
                )
                if duong_dan:
                    try:
                        tao_file_mau_cdsps(duong_dan)
                        self.ghi_log(f"✅ Đã tải file mẫu thành công: {duong_dan}")
                        QMessageBox.information(self.giao_dien, "Thành công", f"Đã lưu file mẫu tại:\n{duong_dan}")
                    except Exception as e:
                        self.ghi_log(f"❌ Lỗi khi tạo file mẫu: {e}")
                        QMessageBox.critical(self.giao_dien, "Lỗi", f"Không thể tạo file mẫu: {e}")

            def nap_du_lieu_tt200(self):
                """Hành động khi NSD nạp file CĐSPS (TT200) đã điền số liệu"""
                from module_ho_tro.kiem_tra_excel import kiem_tra_file_upload
                from module_ho_tro.tu_dien_tt200 import TU_DIEN_TK_TT200
                from PySide6.QtWidgets import QInputDialog

                file_path, _ = QFileDialog.getOpenFileName(
                    self.giao_dien, "Chọn file Bảng CĐSPS (Thông tư 200)", "", "Excel Files (*.xlsx *.xls)"
                )
                if not file_path: return

                self.ghi_log(f"⏳ Đang kiểm tra cấu trúc dữ liệu file: {file_path.split('/')[-1]}...")

                # Gọi cỗ máy Validation để quét lỗi và nhận diện năm tự động
                is_valid, danh_sach_msg, df_sach, nam_phat_hien = kiem_tra_file_upload(file_path, TU_DIEN_TK_TT200)

                if not is_valid:
                    loi_str = "\n".join(danh_sach_msg[:10])
                    if len(danh_sach_msg) > 10: loi_str += f"\n... và {len(danh_sach_msg)-10} lỗi khác."

                    self.ghi_log("❌ File chứa dữ liệu lỗi. Từ chối nạp vào hệ thống!")
                    QMessageBox.warning(self.giao_dien, "Lỗi Dữ Liệu Kế Toán", f"Phát hiện lỗi trong file Excel:\n\n{loi_str}")
                    self.giao_dien.btn_nap_tt200.setStyleSheet("background-color: #FEE2E2; border: 1px solid #EF4444;")
                    return

                # Xác định Năm tài chính của CĐSPS
                nam_goi_y = nam_phat_hien
                if not nam_goi_y:
                    if hasattr(self.giao_dien, 'cb_nam_kq') and self.giao_dien.cb_nam_kq.currentText():
                        nam_goi_y = self.giao_dien.cb_nam_kq.currentText()
                    elif self.du_lieu_he_thong_to_khai:
                        cac_nam_tk = []
                        for m_f, d_k in self.du_lieu_he_thong_to_khai.items():
                            for k in d_k.keys():
                                try: cac_nam_tk.append(int(str(k)[-4:]))
                                except: pass
                        nam_goi_y = str(max(cac_nam_tk)) if cac_nam_tk else "2024"
                    else:
                        from datetime import datetime
                        nam_goi_y = str(datetime.now().year)

                nam_nhap, ok_nam = QInputDialog.getText(
                    self.giao_dien, "Xác nhận Năm tài chính",
                    f"Xác nhận Năm tài chính của Bảng CĐSPS vừa nạp:",
                    text=str(nam_goi_y)
                )
                if not ok_nam or not nam_nhap.strip():
                    nam_nhap = str(nam_goi_y)
                nam_nhap = nam_nhap.strip()

                if not isinstance(self.du_lieu_bcdsps_tt200, dict):
                    self.du_lieu_bcdsps_tt200 = {}

                self.du_lieu_bcdsps_tt200[nam_nhap] = df_sach
                self.ghi_log(f"✅ Đã nạp thành công Bảng CĐSPS năm {nam_nhap} ({len(df_sach)} tài khoản)")

                # Gắn cờ hiệu lên UI
                self.giao_dien.btn_nap_tt200.setStyleSheet("background-color: #D1FAE5; border: 1px solid #10B981;")

                # Thêm vào danh sách file
                item_label = f"[Excel] CĐSPS TT200 - Năm {nam_nhap} ({len(df_sach)} TK) - Sẵn sàng"
                for idx_f in range(self.giao_dien.danh_sach_file.count()):
                    it = self.giao_dien.danh_sach_file.item(idx_f)
                    if it and f"CĐSPS TT200 - Năm {nam_nhap}" in it.text():
                        self.giao_dien.danh_sach_file.takeItem(idx_f)
                        break
                self.giao_dien.danh_sach_file.addItem(item_label)

                # Vẽ bảng ra Tab Tổng hợp
                self._ve_bang_cdsps_len_ui(df_sach, nam=nam_nhap)

                # Hiển thị thông báo hoặc cảnh báo kế toán
                thong_bao_str = "\n".join(danh_sach_msg)
                if any("⚠️" in m for m in danh_sach_msg):
                    QMessageBox.warning(self.giao_dien, f"Lưu ý Cân đối Kế toán - Năm {nam_nhap}", thong_bao_str)
                else:
                    QMessageBox.information(self.giao_dien, f"Thành công - Năm {nam_nhap}", thong_bao_str)

            def _ve_bang_cdsps_len_ui(self, df, nam=None):
                """Hàm vẽ DataFrame Bảng CĐSPS ra Tab Tổng hợp tờ khai để NSD xem lại (có tìm kiếm & phân cấp)"""
                from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
                                               QWidget, QHeaderView, QLineEdit, QLabel, QPushButton, QComboBox)
                from PySide6.QtCore import Qt
                from PySide6.QtGui import QColor, QFont
                from module_ho_tro.dinh_dang_so import dinh_dang_so_vn
                import pandas as pd

                tab_idx = -1
                for i in range(self.giao_dien.tab_tong_hop_chi_tiet.count()):
                    if "CĐSPS (TT200)" in self.giao_dien.tab_tong_hop_chi_tiet.tabText(i):
                        tab_idx = i
                        break

                nam_hien_thi = str(nam) if nam else "Dữ liệu"

                if tab_idx == -1:
                    tab_moi = QWidget()
                    layout_tab = QVBoxLayout(tab_moi)
                    layout_tab.setContentsMargins(5, 5, 5, 5)

                    # Thanh điều khiển: Tìm kiếm & Thông tin
                    thanh_cong_cu = QHBoxLayout()
                    lbl_nam = QLabel("<b>NĂM:</b>")
                    lbl_nam.setObjectName("lbl_cdsps_nam")
                    thanh_cong_cu.addWidget(lbl_nam)

                    cb_nam_cdsps = QComboBox()
                    cb_nam_cdsps.setObjectName("cb_nam_cdsps")
                    cb_nam_cdsps.setMinimumWidth(90)
                    thanh_cong_cu.addWidget(cb_nam_cdsps)

                    txt_tim_kiem = QLineEdit()
                    txt_tim_kiem.setObjectName("txt_tim_cdsps")
                    txt_tim_kiem.setPlaceholderText("🔍 Tìm nhanh theo Mã TK hoặc Tên tài khoản...")
                    txt_tim_kiem.setStyleSheet("padding: 5px; font-size: 13px; border: 1px solid #cbd5e1; border-radius: 4px;")
                    thanh_cong_cu.addWidget(txt_tim_kiem, stretch=1)

                    lbl_thong_tin = QLabel("")
                    lbl_thong_tin.setObjectName("lbl_thong_tin_cdsps")
                    lbl_thong_tin.setStyleSheet("color: #0284c7; font-weight: bold; font-size: 12px;")
                    thanh_cong_cu.addWidget(lbl_thong_tin)

                    layout_tab.addLayout(thanh_cong_cu)

                    bang_du_lieu = QTableWidget()
                    bang_du_lieu.setObjectName("bang_du_lieu_cdsps")
                    bang_du_lieu.setEditTriggers(QTableWidget.NoEditTriggers)
                    bang_du_lieu.setAlternatingRowColors(True)
                    bang_du_lieu.setStyleSheet("QTableWidget { alternate-background-color: #f8fafc; gridline-color: #e2e8f0; font-size: 13px; }")
                    bang_du_lieu.verticalHeader().setVisible(False)
                    layout_tab.addWidget(bang_du_lieu)

                    # Kết nối bộ lọc tìm kiếm
                    def loc_bang(text, tbl=bang_du_lieu):
                        t_l = text.strip().lower()
                        for r_i in range(tbl.rowCount()):
                            it_ma = tbl.item(r_i, 1)
                            it_ten = tbl.item(r_i, 2)
                            ma_txt = it_ma.text().lower() if it_ma else ""
                            ten_txt = it_ten.text().lower() if it_ten else ""
                            tbl.setRowHidden(r_i, not (t_l in ma_txt or t_l in ten_txt))

                    txt_tim_kiem.textChanged.connect(loc_bang)

                    # Kết nối chuyển năm
                    def doi_nam(nam_str):
                        if isinstance(self.du_lieu_bcdsps_tt200, dict) and nam_str in self.du_lieu_bcdsps_tt200:
                            self._ve_bang_cdsps_len_ui(self.du_lieu_bcdsps_tt200[nam_str], nam=nam_str)

                    cb_nam_cdsps.currentTextChanged.connect(doi_nam)

                    self.giao_dien.tab_tong_hop_chi_tiet.addTab(tab_moi, "CĐSPS (TT200)")
                    tab_idx = self.giao_dien.tab_tong_hop_chi_tiet.count() - 1

                # Lấy widget và cập nhật
                tab_widget = self.giao_dien.tab_tong_hop_chi_tiet.widget(tab_idx)
                bang_du_lieu = tab_widget.findChild(QTableWidget, "bang_du_lieu_cdsps")
                cb_nam_cdsps = tab_widget.findChild(QComboBox, "cb_nam_cdsps")
                lbl_thong_tin = tab_widget.findChild(QLabel, "lbl_thong_tin_cdsps")

                # Cập nhật danh sách năm trong combobox
                if cb_nam_cdsps and isinstance(self.du_lieu_bcdsps_tt200, dict):
                    cb_nam_cdsps.blockSignals(True)
                    cb_nam_cdsps.clear()
                    cac_nam = sorted(list(self.du_lieu_bcdsps_tt200.keys()), reverse=True)
                    cb_nam_cdsps.addItems(cac_nam)
                    if nam_hien_thi in cac_nam:
                        cb_nam_cdsps.setCurrentText(nam_hien_thi)
                    cb_nam_cdsps.blockSignals(False)

                # Cập nhật nhãn thông tin
                df_leaf = df[df["IsLeaf"] == True] if "IsLeaf" in df.columns else df
                sum_ps_no = df_leaf["PhatSinhNo"].sum()
                sum_ps_co = df_leaf["PhatSinhCo"].sum()
                if lbl_thong_tin:
                    lbl_thong_tin.setText(f"Số TK: {len(df)} | PS Nợ: {sum_ps_no:,.0f} đ | PS Có: {sum_ps_co:,.0f} đ")

                # Chuẩn bị cột dữ liệu hiển thị (chỉ lấy 8 cột kinh doanh chuẩn)
                cot_hien_thi = ["MaTK", "TenTK", "DuNoDauKy", "DuCoDauKy", "PhatSinhNo", "PhatSinhCo", "DuNoCuoiKy", "DuCoCuoiKy"]
                map_cot = {
                    "MaTK": "Mã TK", "TenTK": "Tên Tài Khoản",
                    "DuNoDauKy": "Dư Nợ ĐK", "DuCoDauKy": "Dư Có ĐK",
                    "PhatSinhNo": "PS Nợ", "PhatSinhCo": "PS Có",
                    "DuNoCuoiKy": "Dư Nợ CK", "DuCoCuoiKy": "Dư Có CK"
                }

                bang_du_lieu.clear()
                bang_du_lieu.setRowCount(len(df))
                bang_du_lieu.setColumnCount(len(cot_hien_thi) + 1)

                headers_vn = ["STT"] + [map_cot.get(c, c) for c in cot_hien_thi]
                bang_du_lieu.setHorizontalHeaderLabels(headers_vn)
                bang_du_lieu.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                bang_du_lieu.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

                for r in range(len(df)):
                    row_data = df.iloc[r]
                    is_leaf = row_data.get("IsLeaf", True)
                    cap_tk = row_data.get("CapTK", 1)
                    is_parent = not is_leaf or (len(str(row_data["MaTK"])) == 3)

                    # Cột STT
                    item_stt = QTableWidgetItem(str(r + 1))
                    item_stt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if is_parent:
                        font_stt = item_stt.font()
                        font_stt.setBold(True)
                        item_stt.setFont(font_stt)
                    bang_du_lieu.setItem(r, 0, item_stt)

                    # Các cột dữ liệu
                    for c, col_name in enumerate(cot_hien_thi):
                        val = row_data[col_name]
                        if col_name in ["DuNoDauKy", "DuCoDauKy", "PhatSinhNo", "PhatSinhCo", "DuNoCuoiKy", "DuCoCuoiKy"]:
                            val_f = float(val) if pd.notna(val) else 0.0
                            item = QTableWidgetItem(dinh_dang_so_vn(val_f))
                            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                        else:
                            val_str = str(val) if pd.notna(val) else ""
                            # Thụt lề nhẹ cho tài khoản con
                            if col_name == "TenTK" and is_leaf and cap_tk > 1:
                                val_str = "    " + val_str
                            item = QTableWidgetItem(val_str)
                            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

                        # Định dạng nổi bật cho Tài khoản Mẹ
                        if is_parent:
                            font = item.font()
                            font.setBold(True)
                            item.setFont(font)
                            item.setBackground(QColor("#f1f5f9"))

                        bang_du_lieu.setItem(r, c + 1, item)
            # (GIỮ NGUYÊN HÀM cap_nhat_bang_tong_hop Ở ĐÂY, KHÔNG SỬA GÌ)
            def cap_nhat_bang_tong_hop(self, ket_qua):
                thong_tin = ket_qua.get("ThongTinChung", {})
                ma_tk = thong_tin.get("MaTKhai", "")
                ky_ke_khai = thong_tin.get("KyKeKhai", "Không xác định")

                # =========================================================
                # [MÀNG LỌC TÀNG HÌNH]: CHỈ VẼ CÁC KỲ THUỘC NĂM ĐƯỢC CHỌN
                # =========================================================
                nam_pt = self.giao_dien.cb_nam.currentText()
                if nam_pt != "Tất cả các năm" and str(nam_pt) not in str(ky_ke_khai):
                    # Data đã được nạp an toàn vào RAM ở bước trước.
                    # Lệnh return này chỉ ngắt luồng không cho vẽ cột ra Bảng UI.
                    return
                # =========================================================

                if ma_tk in MAP_TEN_TO_KHAI:
                    loai_tk = MAP_TEN_TO_KHAI[ma_tk]
                else:
                    ten_day_du = thong_tin.get("TenTKhai", "")
                    loai_tk = ten_day_du.split("Mẫu số ")[-1].replace(")", "").strip() if "Mẫu số " in ten_day_du else ma_tk

                tab_index = -1
                for i in range(self.giao_dien.tab_tong_hop_chi_tiet.count()):
                    if self.giao_dien.tab_tong_hop_chi_tiet.tabText(i) == loai_tk:
                        tab_index = i
                        break

                if tab_index == -1:
                    tab_moi = QWidget()
                    layout_tab = QVBoxLayout(tab_moi)
                    layout_tab.setContentsMargins(5, 5, 5, 5)

                    inner_tab = QTabWidget()
                    inner_tab.setObjectName("InnerTab")
                    layout_tab.addWidget(inner_tab)

                    self.giao_dien.tab_tong_hop_chi_tiet.addTab(tab_moi, loai_tk)
                    tab_index = self.giao_dien.tab_tong_hop_chi_tiet.count() - 1

                tab_hien_tai = self.giao_dien.tab_tong_hop_chi_tiet.widget(tab_index)
                inner_tab = tab_hien_tai.findChild(QTabWidget, "InnerTab")
                is_thang_quy = "/" in ky_ke_khai

                # ================================================================
                # BỔ SUNG: NHÚNG WIDGET KHBS VÀO ĐÚNG TAB 01/GTGT VÀ 02/GTGT
                # ================================================================
                if loai_tk in ["01/GTGT", "02/GTGT"]:
                    khbs_idx = -1
                    for i in range(inner_tab.count()):
                        if inner_tab.tabText(i) == "Lịch sử KHBS":
                            khbs_idx = i
                            break

                    if khbs_idx == -1:
                        widget_khbs = KHBSReviewWidget(parent=inner_tab)
                        # Khóa cứng dropdown để giao diện không bị nhảy loại tờ khai
                        if widget_khbs.cbo_type.findText(loai_tk) == -1:
                            widget_khbs.cbo_type.addItem(loai_tk)
                        widget_khbs.cbo_type.setCurrentText(loai_tk)
                        widget_khbs.cbo_type.setEnabled(False)

                        inner_tab.addTab(widget_khbs, "Lịch sử KHBS")
                        self.dict_khbs_widgets[loai_tk] = widget_khbs
                # ================================================================

                def xu_ly_sub_tab(ten_sub_tab, du_lieu):
                    if not du_lieu: return

                    sub_tab_idx = -1
                    for i in range(inner_tab.count()):
                        if inner_tab.tabText(i) == ten_sub_tab:
                            sub_tab_idx = i
                            break

                    if sub_tab_idx == -1:
                        sub_widget = QWidget()
                        sub_layout = QVBoxLayout(sub_widget)
                        sub_layout.setContentsMargins(0, 0, 0, 0)

                        bang_du_lieu = QTableWidget()

                        QuanLyBangBieu.cau_hinh_bang_du_lieu(bang_du_lieu)
                        sub_layout.addWidget(bang_du_lieu)

                        inner_tab.addTab(sub_widget, ten_sub_tab)
                        sub_tab_idx = inner_tab.count() - 1

                    sub_widget = inner_tab.widget(sub_tab_idx)
                    bang_du_lieu = sub_widget.findChild(QTableWidget)

                    if ma_tk in ["402", "683","684","685","686","699"]:
                        QuanLyBangBieu.xu_ly_bang_bctc(bang_du_lieu, du_lieu)

                    elif isinstance(du_lieu, dict) and "IsBangKe" in du_lieu:
                        if du_lieu["IsBangKe"]:
                            QuanLyBangBieu.xu_ly_bang_ke(bang_du_lieu, du_lieu["DuLieu"])
                        else:
                            if is_thang_quy:
                                QuanLyBangBieu.xu_ly_bang_thang_quy(bang_du_lieu, du_lieu["DuLieu"], ky_ke_khai)
                            else:
                                QuanLyBangBieu.xu_ly_bang_nam(bang_du_lieu, du_lieu["DuLieu"], ky_ke_khai)
                    else:
                        if is_thang_quy:
                            QuanLyBangBieu.xu_ly_bang_thang_quy(bang_du_lieu, du_lieu, ky_ke_khai)
                        else:
                            QuanLyBangBieu.xu_ly_bang_nam(bang_du_lieu, du_lieu, ky_ke_khai)

                    QuanLyBangBieu.can_bang_kich_thuoc_bang(bang_du_lieu)

                if ma_tk == "402":
                    xu_ly_sub_tab("Bảng CĐKT", ket_qua.get("B01_CDKT", {}))
                    xu_ly_sub_tab("KQ HĐKD", ket_qua.get("B02_KQKD", {}))
                    xu_ly_sub_tab("Lưu chuyển TT", ket_qua.get("B03_LCTT", {}))
                elif ma_tk in ["683", "684", "685", "686", "699"]:
                    xu_ly_sub_tab("Bảng CĐKT", ket_qua.get("B01_CDKT", {}))
                    xu_ly_sub_tab("KQ HĐKD", ket_qua.get("B02_KQKD", {}))
                    xu_ly_sub_tab("Lưu chuyển TT", ket_qua.get("B03_LCTT", {}))
                    xu_ly_sub_tab("Cân đối Tài khoản", ket_qua.get("B04_CDTK", {}))
                else:
                    chi_tieu_chinh = ket_qua.get("ChiTieuChinh", {})
                    phu_luc = ket_qua.get("PhuLuc", {})

                    xu_ly_sub_tab("Tờ khai chính", chi_tieu_chinh)
                    for ten_pl, du_lieu_pl in phu_luc.items():
                        xu_ly_sub_tab(ten_pl, du_lieu_pl)

            def chay(self):
                """Luồng khởi động thực tế: Bắt buộc đăng nhập trước khi vào hệ thống"""
                from module_giao_dien.dang_nhap import LoginDialog
                from PySide6.QtWidgets import QDialog
                from PySide6.QtCore import QTimer
                import os, json

                dialog_dang_nhap = LoginDialog()

                if dialog_dang_nhap.exec() == QDialog.DialogCode.Accepted:
                    self.allowed_cqt = dialog_dang_nhap.allowed_cqt
                    self.username = dialog_dang_nhap.username
                    self.role = dialog_dang_nhap.role

                    self.giao_dien.show()
                    QTimer.singleShot(1500, self.kiem_tra_update_ngam)

                    # ==============================================================
                    # KÍCH HOẠT TOUR HƯỚNG DẪN TÂN THỦ
                    # ==============================================================
                    can_chay_tour = True
                    if os.path.exists("Data/tour_config.json"):
                        try:
                            with open("Data/tour_config.json", "r") as f:
                                can_chay_tour = json.load(f).get("show_tour", True)
                        except: pass

                    if can_chay_tour:
                        # Đợi nửa giây cho app vẽ xong nút bấm rồi mới phủ mờ
                        QTimer.singleShot(500, self.khoi_dong_tour_huong_dan)
                    # ==============================================================

                    sys.exit(self.app.exec())
                else:
                    sys.exit(0)

            def khoi_dong_tour_huong_dan(self):
                kich_ban = [
                    # ==========================================================
                    # CỤM 1: CÁC BƯỚC TẠI TAB 0 (CHUẨN BỊ DỮ LIỆU)
                    # ==========================================================
                    {
                        "tab_index": 0,
                        "widget": self.giao_dien.btn_chon_file_xml,
                        "tieu_de": "1. Upload Tờ khai XML",
                        "noi_dung": "Bắt đầu bằng việc upload hàng loạt Tờ khai Thuế (XML) vào hệ thống tại đây."
                    },
                    {
                        "tab_index": 0,  # Vẫn giữ nguyên tab_index = 0, ứng dụng sẽ không bị giật màn hình
                        "widget": self.giao_dien.btn_kho_file_mau,
                        "tieu_de": "2. Kho Biểu mẫu",
                        "noi_dung": "Sử dụng nút này để tải Template Excel chuẩn, sau đó copy dữ liệu Hóa đơn hoặc CĐSPS (TT200/TT99) vào để tải lên."
                    },
                    {
                        "tab_index": 0,
                        "widget": self.giao_dien.btn_cau_hinh_tms,
                        "tieu_de": "3. Kết nối TMS",
                        "noi_dung": "Cài đặt tài khoản TMS để Bot tự động tra cứu tình trạng Doanh nghiệp, thời điểm nộp tờ khai"
                    },
                    {
                        "tab_index": 0,
                        "widget": self.giao_dien.btn_chon_rule,
                        "tieu_de": "4. Bộ lọc Phân tích",
                        "noi_dung": "Bật/Tắt các quy tắc đối chiếu không cần thiết để tối ưu hóa tốc độ chạy của hệ thống."
                    },
                    {
                        "tab_index": 0,
                        "widget": self.giao_dien.btn_phan_tich,
                        "tieu_de": "5. Khởi động Phân tích",
                        "noi_dung": "Sau khi chuẩn bị đủ dữ liệu, bấm nút này để ứng dụng bắt đầu phân tích."
                    },

                    # ==========================================================
                    # CỤM 2: NHẢY SANG CÁC TAB KẾT QUẢ ĐỂ GIỚI THIỆU
                    # ==========================================================
                    {
                        "tab_index": 2,  # Hệ thống nhận diện Tab thay đổi -> Tự động đổi Tab
                        "widget": self.giao_dien.btn_tab_kq_hoa_don,
                        "tieu_de": "6. Đối chiếu Chuỗi cung ứng",
                        "noi_dung": "Hệ thống sẽ chuyển dữ liệu sang Tab này để báo cáo chênh lệch Tồn kho và phân tích tên hàng hóa bằng AI."
                    },
                    {
                        "tab_index": 3,
                        "widget": self.giao_dien.btn_tab_rui_ro,
                        "tieu_de": "7. Hóa đơn Rủi ro",
                        "noi_dung": "Tất cả các Hóa đơn mua của Doanh nghiệp có cảnh báo rủi ro sẽ bị bôi đỏ tại đây."
                    },
                    {
                        "tab_index": 4,
                        "widget": self.giao_dien.btn_tab_kq_phan_tich,
                        "tieu_de": "8. Báo cáo Tổng hợp",
                        "noi_dung": "Mọi kết quả chênh lệch số liệu tờ khai, sai sót tài chính đều được gom chung vào Tab này."
                    },

                    # ==========================================================
                    # CỤM 3: HƯỚNG DẪN CÁC NÚT BÊN TRONG TAB 4
                    # ==========================================================
                    {
                        "tab_index": 4,
                        "widget": self.giao_dien.btn_tao_phieu,
                        "tieu_de": "9. Tự động Soạn thảo",
                        "noi_dung": "Nhấn nút này để máy tự động tổng hợp lỗi và sinh ra Phiếu Nhận xét dạng Word."
                    },
                    {
                        "tab_index": 4,  # Vẫn là Tab 4, mượt mà di chuyển sang nút Excel
                        "widget": self.giao_dien.btn_xuat_excel,
                        "tieu_de": "10. Kết xuất Excel",
                        "noi_dung": "Hoặc xuất toàn bộ bảng kê chi tiết dữ liệu, đối chiếu doanh số ra file Excel chuyên nghiệp."
                    }
                ]

                self.tour_overlay = HuongDanTour(
                    parent=self.giao_dien,
                    danh_sach_buoc=kich_ban,
                    ham_chuyen_tab=self.chuyen_tab
                )
                self.tour_overlay.bat_dau()
            def kiem_tra_update_ngam(self):
                """Hàm chạy ngầm kiểm tra phiên bản mới bằng file JSON đọc trực tiếp từ Google Drive"""
                try:
                    import requests

                    # =============================================================
                    # CẤU HÌNH PRODUCTION CỦA MÀY Ở ĐÂY
                    # =============================================================
                    VERSION_HIEN_TAI = "v5"

                    # Điền lại đúng cái ID file JSON trên Google Drive của mày vào đây
                    FILE_ID_JSON = "1XCqx0m7C79G_8UGbBZvVXYCzR9ZPCFdG"

                    url_api = f"https://drive.google.com/uc?export=download&id={FILE_ID_JSON}"

                    # Bắn request kéo file JSON về
                    response = requests.get(url_api, timeout=10, allow_redirects=True)

                    if response.status_code == 200:
                        try:
                            thong_tin_update = response.json()
                            version_tren_mang = thong_tin_update.get("latest_version", "")

                            # =======================================================
                            # [ĐÃ SỬA] THUẬT TOÁN SO SÁNH VERSION CHUẨN XÁC
                            # =======================================================
                            def check_is_newer(v_mang, v_local):
                                try:
                                    # Lọc bỏ chữ 'v', tách số theo dấu chấm (VD: 'v3.1' -> [3, 1])
                                    v1 = [int(x) for x in v_mang.lower().replace('v', '').split('.')]
                                    v2 = [int(x) for x in v_local.lower().replace('v', '').split('.')]

                                    # Cân bằng độ dài mảng (VD: v4 là [4], v3.1 là [3, 1] -> Ép thành [4, 0] và [3, 1])
                                    max_len = max(len(v1), len(v2))
                                    v1.extend([0] * (max_len - len(v1)))
                                    v2.extend([0] * (max_len - len(v2)))

                                    return v1 > v2 # Trả về True nếu Mạng > Local
                                except:
                                    return False # Lỗi mạng hoặc JSON rác thì khóa luôn không update

                            # So sánh: Chỉ update khi version trên mạng CAO HƠN version đang chạy
                            if version_tren_mang and check_is_newer(version_tren_mang, VERSION_HIEN_TAI):
                                self.ghi_log(f"🌟 Phát hiện phiên bản cập nhật mới: {version_tren_mang}")
                                from module_ho_tro.updater import AutoUpdater
                                self.trinh_cap_nhat = AutoUpdater(self.giao_dien)
                                self.trinh_cap_nhat.prompt_and_update(thong_tin_update)

                        except Exception as err:
                            self.ghi_log(f"⚠️ Lỗi khởi động trình cập nhật: {err}")
                    else:
                        self.ghi_log(f"⚠️ Máy chủ cập nhật từ chối kết nối (HTTP {response.status_code}).")

                except Exception:
                    self.ghi_log("⚠️ Không thể kết nối đến máy chủ kiểm tra cập nhật (Kiểm tra lại mạng).")

            def hien_thi_form_xuat_excel(self):
                # ---> BẪY KHÓA TÀI KHOẢN DÙNG THỬ <---
                if getattr(self, 'role', '') == 'Dùng thử':
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(self.giao_dien, "Giới hạn tính năng",
                                        "Tính năng Kết xuất Báo cáo Excel bị khóa đối với tài khoản Dùng thử.\n\nVui lòng đăng ký tài khoản chính thức để sử dụng!")
                    return
                # ĐÃ SỬA: Bổ sung thêm self.du_lieu_he_thong_to_khai vào chốt kiểm tra
                if not self.ket_qua_cuoi_cung and not self.dict_hd_ban_ra and not self.dict_hd_mua_vao and not self.du_lieu_he_thong_to_khai:
                    self.ghi_log("Chưa có dữ liệu nào trong hệ thống để xuất Excel!")
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(self.giao_dien, "Cảnh báo", "Bạn chưa nạp bất kỳ dữ liệu Tờ khai hay Hóa đơn nào vào hệ thống!")
                    return

                # Trả lại lệnh gọi Dialog Excel về đúng chỗ của nó
                dialog = DialogXuatExcel(main_app=self)
                dialog.exec()

            def mo_trinh_soan_thao_phieu(self):
                # ---> CHÈN ĐOẠN KHÓA TẠM THỜI VÀO NGAY ĐÂY <---
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self.giao_dien, "Thông báo",
                                        "Chức năng này đang được nâng cấp theo biểu mẫu của quy trình mới.")
                return  # Lệnh return sẽ chặn đứng, không cho code chạy tiếp xuống dưới
                # ------------------------------------------------
                # ---> BẪY KHÓA TÀI KHOẢN DÙNG THỬ <---
                if getattr(self, 'role', '') == 'Dùng thử':

                    QMessageBox.warning(self.giao_dien, "Giới hạn tính năng",
                                        "Tính năng Soạn thảo Phiếu nhận xét tự động bị khóa đối với tài khoản Dùng thử.\n\nVui lòng nâng cấp tài khoản!")
                    return
                """Khởi chạy trình soạn thảo Phiếu nhận xét và đắp nó làm 1 sub-tab bên trong Tab Kết quả Phân tích"""
                if not self.ket_qua_cuoi_cung:
                    QMessageBox.warning(self.giao_dien, "Cảnh báo", "Bạn chưa chạy phân tích hồ sơ, không có dữ liệu để tạo phiếu!")
                    return

                # Xác định đúng cụm Tab con của Màn hình Kết quả phân tích (Tab 4)
                tabs_kq = self.giao_dien.widget_kq_phan_tich.tabs_kq

                # Chống mở trùng Tab (Nếu đang mở rồi thì Focus tới nó)
                for i in range(tabs_kq.count()):
                    if tabs_kq.tabText(i) == "📝 Soạn thảo Phiếu nhận xét":
                        tabs_kq.setCurrentIndex(i)
                        return

                # Gọi View soạn thảo ra
                #from module_giao_dien.giao_dien_soan_thao import GiaoDienSoanThaoPhieu
                #widget_soan_thao = GiaoDienSoanThaoPhieu(self.ket_qua_cuoi_cung, parent=self.giao_dien)
                # ==============================================================
                # TRÍCH XUẤT TOÀN BỘ DỮ LIỆU ĐỂ BƠM CHO PHIẾU NHẬN XÉT
                # ==============================================================
                import re
                ten_cong_ty, mst_cong_ty, dia_chi_cong_ty, nnkd_cong_ty = "", "", "", ""

                nam_pt = self.giao_dien.cb_nam.currentText()

                def gach_bo_ma_ct(dien_giai):
                    return re.sub(r'^\[.*?\]\s*', '', str(dien_giai)).strip()

                def co_so_lieu(gia_tri_str):
                    try:
                        val = float(str(gia_tri_str).replace(',', ''))
                        return val != 0
                    except:
                        return False

                # TẠO TỪ ĐIỂN PHÂN LỌC THEO TỪNG NĂM CHUYÊN BIỆT
                du_lieu_theo_nam = {}

                for form, dict_ky in self.du_lieu_he_thong_to_khai.items():
                    for ky, data in dict_ky.items():
                        # Cắt lấy 4 số cuối của kỳ để lấy đích danh Năm
                        nam_cua_ky = str(ky).split('/')[-1]

                        if nam_pt != "Tất cả các năm" and nam_pt != nam_cua_ky:
                            continue

                        # Nếu năm này chưa có trong từ điển, tạo mới ngăn kéo cho nó
                        if nam_cua_ky not in du_lieu_theo_nam:
                            du_lieu_theo_nam[nam_cua_ky] = {"gtgt": [], "tndn": [], "tncn": [], "tong_gtgt_tam": {}}

                        thong_tin = data.get("ThongTinChung", {})
                        chi_tieu = data.get("ChiTieuChinh", {})

                        if thong_tin.get("TenNNT"): ten_cong_ty = thong_tin.get("TenNNT")
                        if thong_tin.get("MST"): mst_cong_ty = thong_tin.get("MST")
                        if thong_tin.get("DiaChi"): dia_chi_cong_ty = thong_tin.get("DiaChi")
                        if thong_tin.get("TenNganhNgheKD"): nnkd_cong_ty = thong_tin.get("TenNganhNgheKD")
                        elif thong_tin.get("NganhNgheKD"): nnkd_cong_ty = thong_tin.get("NganhNgheKD")

                        # 1. Rút trích TNDN (Đẩy vào đúng năm)
                        if "03/TNDN" in form:
                            for ma_ct, info in chi_tieu.items():
                                dien_giai = info.get('DienGiai','')
                                so_tien = info.get('GiaTri', '0')

                                if not nnkd_cong_ty and "ngành nghề" in str(dien_giai).lower():
                                    nnkd_cong_ty = so_tien

                                if co_so_lieu(so_tien):
                                    du_lieu_theo_nam[nam_cua_ky]["tndn"].append({
                                        "ten_chi_tieu": gach_bo_ma_ct(dien_giai),
                                        "so_lieu": so_tien
                                    })

                        # 2. Rút trích TNCN (Đẩy vào đúng năm)
                        elif "05/KK" in form or "05/QTT" in form:
                            for ma_ct, info in chi_tieu.items():
                                so_tien = info.get('GiaTri', '0')
                                if co_so_lieu(so_tien):
                                    du_lieu_theo_nam[nam_cua_ky]["tncn"].append({
                                        "ten_chi_tieu": gach_bo_ma_ct(info.get('DienGiai','')),
                                        "so_lieu": so_tien
                                    })

                        # 3. Rút trích GTGT (Cộng dồn nội bộ trong năm đó)
                        elif "01/GTGT" in form:
                            for ma_ct, info in chi_tieu.items():
                                if ma_ct not in du_lieu_theo_nam[nam_cua_ky]["tong_gtgt_tam"]:
                                    du_lieu_theo_nam[nam_cua_ky]["tong_gtgt_tam"][ma_ct] = {"dien_giai": gach_bo_ma_ct(info.get('DienGiai','')), "tong_tien": 0}
                                try:
                                    du_lieu_theo_nam[nam_cua_ky]["tong_gtgt_tam"][ma_ct]["tong_tien"] += float(str(info.get('GiaTri', '0')).replace(',', ''))
                                except:
                                    pass

                # Chốt sổ GTGT: Ép kiểu dữ liệu GTGT cho từng năm
                danh_sach_nam = sorted(list(du_lieu_theo_nam.keys()))
                for nam in danh_sach_nam:
                    for ma_ct, data in du_lieu_theo_nam[nam]["tong_gtgt_tam"].items():
                        if data["tong_tien"] != 0:
                            du_lieu_theo_nam[nam]["gtgt"].append({"ten_chi_tieu": data['dien_giai'], "so_lieu": data["tong_tien"]})

                from module_phan_tich.bao_cao_doanh_so import BaoCaoDoanhSoEngine
                from module_doc_hoadon.invoice_processor import InvoiceProcessor

                # BỌC LƯỚI LỌC: Bóp chết HĐ rác trước khi xuất Phiếu Word
                df_br_sach = InvoiceProcessor.loc_hoa_don_tinh_toan(self.dict_hd_ban_ra)
                df_mv_sach = InvoiceProcessor.loc_hoa_don_tinh_toan(self.dict_hd_mua_vao)

                du_lieu_br = BaoCaoDoanhSoEngine.xuat_du_lieu_bao_cao(df_br_sach, self.du_lieu_he_thong_to_khai, nam_pt,
                                                                      False, self.ghi_log)
                du_lieu_mv = BaoCaoDoanhSoEngine.xuat_du_lieu_bao_cao(df_mv_sach, self.du_lieu_he_thong_to_khai, nam_pt,
                                                                      True, self.ghi_log)

                # --- ĐÓNG GÓI CHUẨN FORM MỚI ---
                du_lieu_tong_hop = {
                    "ten_nnt": ten_cong_ty,
                    "mst": mst_cong_ty,
                    "dia_chi": dia_chi_cong_ty,
                    "nnkd": nnkd_cong_ty,
                    "ky_pt": nam_pt,
                    "danh_sach_nam": danh_sach_nam,      # VD: ['2023', '2024']
                    "du_lieu_theo_nam": du_lieu_theo_nam, # Chứa data đã chia sẵn
                    "bang_hoa_don_br": du_lieu_br if du_lieu_br else [],
                    "bang_hoa_don_mv": du_lieu_mv if du_lieu_mv else []
                }

                # Gọi View xuất phiếu nhận xét ra
                from module_giao_dien.giao_dien_soan_thao import GiaoDienXuatPhieuNhanXet
                widget_soan_thao = GiaoDienXuatPhieuNhanXet(
                    ds_rui_ro=self.ket_qua_cuoi_cung,
                    du_lieu_tong_hop=du_lieu_tong_hop,
                    parent=self.giao_dien
                )
                # Cắm nó vào làm Tab con cuối cùng của dãy Tab Phân tích
                index = tabs_kq.addTab(widget_soan_thao, "📝 Soạn thảo Phiếu nhận xét")
                tabs_kq.setCurrentIndex(index)

            def lam_moi_phien_lam_viec(self):
                """Xóa toàn bộ Cache trong RAM và làm sạch Giao diện để bắt đầu công ty mới"""
                hoi = QMessageBox.question(
                    self.giao_dien,
                    "Xác nhận dọn dẹp",
                    "Bạn có chắc chắn muốn xóa toàn bộ dữ liệu của phiên làm việc hiện tại để bắt đầu công ty mới không?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )

                if hoi == QMessageBox.StandardButton.Yes:
                    # 1. XÓA BỘ NHỚ TRONG RAM (Controller)
                    self.dict_hd_ban_ra = {}
                    self.dict_hd_mua_vao = {}
                    self.du_lieu_he_thong_to_khai = {}
                    self.danh_sach_file_xml_cho = []
                    self.toan_bo_file_xml = set()
                    self.ket_qua_cuoi_cung = []
                    self.dict_khbs_widgets.clear()
                    self.so_luong_xml_dang_chay = 0
                    self.du_lieu_bcdsps_tt200 = {}  # ---> XÓA DATA EXCEL TT200 TRONG RAM <---
                    # 2. XÓA GIAO DIỆN (View)
                    # Xóa list file và log
                    self.giao_dien.danh_sach_file.clear()
                    self.giao_dien.text_log_xu_ly.clear()
                    self.giao_dien.btn_nap_tt200.setStyleSheet(
                        "QPushButton:disabled { background-color: #F3F4F6; border: 1px solid #E5E7EB; }")
                    # Xóa trắng dữ liệu các bảng hóa đơn, phân tích
                    self.giao_dien.bang_hd_ban_ra.setRowCount(0)
                    self.giao_dien.bang_hd_mua_vao.setRowCount(0)
                    self.giao_dien.bang_hd_rui_ro.setRowCount(0)
                    #self.giao_dien.bang_phan_tich.setRowCount(0)

                    # Đóng tất cả các Tab Tờ khai đã sinh ra trước đó
                    while self.giao_dien.tab_tong_hop_chi_tiet.count() > 0:
                        self.giao_dien.tab_tong_hop_chi_tiet.removeTab(0)
                    # ---> BỔ SUNG LỆNH QUÉT DỌN TAB KẾT QUẢ MỚI Ở ĐÂY <---
                    if hasattr(self.giao_dien, 'widget_kq_phan_tich'):
                        self.giao_dien.widget_kq_phan_tich.lam_moi_giao_dien()
                    # ---> BỔ SUNG LỆNH QUÉT DỌN TAB TỒN KHO TRONG TABS HÓA ĐƠN <---
                    for i in range(self.giao_dien.tabs_hoa_don.count() - 1, -1, -1):
                        ten_tab = self.giao_dien.tabs_hoa_don.tabText(i)
                        # Quét trúng tên 1 trong 2 Tab thì sút nó đi
                        if ten_tab in ["Rà soát Tồn kho", "Đối chiếu tên mặt hàng"]:
                            w = self.giao_dien.tabs_hoa_don.widget(i)
                            self.giao_dien.tabs_hoa_don.removeTab(i)
                            w.deleteLater()
                    # In thông báo thành công
                    self.ghi_log("♻️ Đã dọn dẹp toàn bộ dữ liệu. Hệ thống sẵn sàng cho phiên làm việc mới!")
                    self.cap_nhat_kpi_chuan_bi()
                    if hasattr(self.giao_dien, 'kpi_trang_thai'):
                        self.giao_dien.kpi_trang_thai.cap_nhat(gia_tri="Sẵn sàng", subtext="Chờ lệnh khởi chạy")

            def chuyen_view_ket_qua_nam(self, nam):
                """Hàm 1: Bật hiệu ứng Loading và ép UI nín thở"""
                if not hasattr(self, 'kho_ket_qua_nam') or nam not in self.kho_ket_qua_nam: return

                # 1. Bật nhãn Loading và khóa Combobox để tránh user bấm spam
                if hasattr(self.giao_dien, 'lbl_loading_nam'):
                    self.giao_dien.lbl_loading_nam.setVisible(True)
                    self.giao_dien.cb_nam_kq.setEnabled(False)

                self.ghi_log(f"🔄 Đang kết xuất giao diện báo cáo cho Năm {nam}...")

                # 2. BÍ KÍP: Ép Giao diện vẽ chữ Loading ra màn hình NGAY LẬP TỨC
                QApplication.processEvents()

                # 3. Hẹn giờ 50ms sau mới chạy code nặng để UI kịp render
                from PySide6.QtCore import QTimer
                QTimer.singleShot(50, lambda: self._thuc_thi_chuyen_view_nam(nam))

            def _thuc_thi_chuyen_view_nam(self, nam):
                """Hàm 2: Thực thi việc vẽ UI nặng nhọc ngầm bên dưới"""
                try:
                    data_nam = self.kho_ket_qua_nam[nam]
                    self.ket_qua_cuoi_cung = data_nam["ket_qua_list"]

                    if hasattr(self.giao_dien, 'widget_kq_phan_tich'):
                        # Quét sạch View cũ và nhồi data mới
                        self.giao_dien.widget_kq_phan_tich.lam_moi_giao_dien()
                        self.giao_dien.widget_kq_phan_tich.nap_du_lieu_tong_the(
                            data_nam["ket_qua_list"], data_nam["du_lieu_ban_ra"], data_nam["du_lieu_mua_vao"],
                            data_nam["df_br_sach"], data_nam["df_mv_sach"]
                        )

                        # Bơm lại Module KHBS
                        from module_giao_dien.builder_phan_tich_khbs import BuilderPhanTichKHBS
                        for tk_loai, w_khbs in self.dict_khbs_widgets.items():
                            if w_khbs.grouped_data:
                                danh_sach_canh_bao = w_khbs.get_khbs_warnings(tk_loai)
                                if danh_sach_canh_bao:
                                    module_khbs = BuilderPhanTichKHBS()
                                    module_khbs.nap_du_lieu(danh_sach_canh_bao)
                                    self.giao_dien.widget_kq_phan_tich.them_module_phan_tich_khac(
                                        f"RÀ SOÁT KHBS ({tk_loai})", module_khbs)

                        # Bơm lại Chuỗi cung ứng
                        try:
                            from module_phan_tich.supply_chain_analyzer import SupplyChainAnalyzer
                            from module_giao_dien.builder_phan_tich_chuoi_cung_ung import BuilderPhanTichChuoiCungUng
                            import pandas as pd
                            df_mv = data_nam["df_mv_sach"]
                            df_br = data_nam["df_br_sach"]
                            if isinstance(df_mv, pd.DataFrame) and not df_mv.empty: df_mv = df_mv[df_mv['_Nam'] == nam]
                            if isinstance(df_br, pd.DataFrame) and not df_br.empty: df_br = df_br[df_br['_Nam'] == nam]

                            if (isinstance(df_mv, pd.DataFrame) and not df_mv.empty) or (
                                    isinstance(df_br, pd.DataFrame) and not df_br.empty):
                                sc_analyzer = SupplyChainAnalyzer(df_mv, df_br)
                                sc_result = sc_analyzer.run_analysis()
                                if sc_result:
                                    module_sc = BuilderPhanTichChuoiCungUng()
                                    module_sc.nap_du_lieu(sc_result)
                                    self.giao_dien.widget_kq_phan_tich.them_module_phan_tich_khac(
                                        "RÀ SOÁT CHUỖI GIÁ TRỊ", module_sc)
                        except Exception:
                            pass
                finally:
                    # 4. CHỐT HẠ: Chạy xong (hoặc lỗi) thì giấu nút Loading đi và mở khóa Combobox
                    if hasattr(self.giao_dien, 'lbl_loading_nam'):
                        self.giao_dien.lbl_loading_nam.setVisible(False)
                        self.giao_dien.cb_nam_kq.setEnabled(True)
                    self.ghi_log(f"✅ Đã hiển thị báo cáo Năm {nam}.")
                    if hasattr(self.giao_dien, 'kpi_trang_thai'):
                        self.giao_dien.kpi_trang_thai.cap_nhat(gia_tri="Hoàn tất", subtext="Đã phân tích xong")
if __name__ == "__main__":
    ung_dung = UngDungRRR()
    ung_dung.chay()