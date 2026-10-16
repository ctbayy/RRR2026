from PySide6.QtWidgets import QFileDialog, QMessageBox
from module_doc_hoadon.xu_ly_hoa_don_hub import doc_file_hoa_don_v2
from module_giao_dien.quan_ly_bang_bieu import QuanLyBangBieu
import pandas as pd
from module_doc_hoadon.hoadon_ruiro import HoaDonRuiRoManager


class QuanLyHoaDonUI:
    def __init__(self, ung_dung_chinh):
        self.app = ung_dung_chinh
        self.ui = ung_dung_chinh.giao_dien

        self.ui.btn_tai_hd_ban_ra.clicked.connect(self.tai_hoa_don_ban_ra)
        self.ui.btn_tai_hd_mua_vao.clicked.connect(self.tai_hoa_don_mua_vao)
        # Đã xóa dòng lệnh tìm nút btn_cap_nhat_rui_ro gây lỗi ở đây

    def tai_hoa_don_ban_ra(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self.ui, "Chọn file Hóa đơn bán ra", "",
                                                     "Excel Files (*.xlsx *.xls);;XML Files (*.xml);;CSV Files (*.csv)")
        if file_paths:
            thanh_cong = 0
            danh_sach_df = []

            if hasattr(self.app, 'dict_hd_ban_ra') and isinstance(self.app.dict_hd_ban_ra,
                                                                  pd.DataFrame) and not self.app.dict_hd_ban_ra.empty:
                danh_sach_df.append(self.app.dict_hd_ban_ra)

            for file_path in file_paths:
                du_lieu = doc_file_hoa_don_v2(file_path, is_mua_vao=False)

                if du_lieu is not None and not du_lieu.empty:
                    ten_file = file_path.split('/')[-1]
                    self.ui.danh_sach_file.addItem(f"[HĐ BÁN RA] {ten_file}")
                    danh_sach_df.append(du_lieu)
                    thanh_cong += 1

            if thanh_cong > 0:
                self.app.dict_hd_ban_ra = pd.concat(danh_sach_df, ignore_index=True)
                QuanLyBangBieu.xu_ly_bang_ke(self.ui.bang_hd_ban_ra, self.app.dict_hd_ban_ra)
                QuanLyBangBieu.cau_hinh_bang_du_lieu(self.ui.bang_hd_ban_ra)
                QuanLyBangBieu.can_bang_kich_thuoc_bang(self.ui.bang_hd_ban_ra)
                self.app.ghi_log(f"Đã gộp thành công {thanh_cong} file Hóa đơn Bán ra vào hệ thống.")
                if hasattr(self.app, 'cap_nhat_kpi_chuan_bi'):
                    self.app.cap_nhat_kpi_chuan_bi()
            else:
                QMessageBox.warning(self.ui, "Lỗi", "Không thể đọc các file hóa đơn này. Kiểm tra lại cấu trúc.")

    def tai_hoa_don_mua_vao(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self.ui, "Chọn file Hóa đơn mua vào", "",
                                                     "Excel Files (*.xlsx *.xls);;XML Files (*.xml);;CSV Files (*.csv)")
        if file_paths:
            thanh_cong = 0
            danh_sach_df = []

            if hasattr(self.app, 'dict_hd_mua_vao') and isinstance(self.app.dict_hd_mua_vao,
                                                                   pd.DataFrame) and not self.app.dict_hd_mua_vao.empty:
                danh_sach_df.append(self.app.dict_hd_mua_vao)

            for file_path in file_paths:
                du_lieu = doc_file_hoa_don_v2(file_path, is_mua_vao=True)

                if du_lieu is not None and not du_lieu.empty:
                    ten_file = file_path.split('/')[-1]
                    self.ui.danh_sach_file.addItem(f"[HĐ MUA VÀO] {ten_file}")
                    danh_sach_df.append(du_lieu)
                    thanh_cong += 1

            if thanh_cong > 0:
                self.app.dict_hd_mua_vao = pd.concat(danh_sach_df, ignore_index=True)

                # ==========================================================
                # CHUYỂN LUỒNG: BẬT MÁY QUÉT HÓA ĐƠN RỦI RO TẠI ĐÂY
                # ==========================================================
                self.app.ghi_log("🔍 Đang kích hoạt Radar rà soát Danh sách Doanh nghiệp Rủi ro...")
                try:
                    rui_ro_mgr = getattr(self.ui, 'ruiro_mgr', None) or getattr(self.app, 'ruiro_mgr', None)
                    if rui_ro_mgr is None:
                        rui_ro_mgr = HoaDonRuiRoManager()
                        self.app.ruiro_mgr = rui_ro_mgr

                    self.app.dict_hd_mua_vao, warnings = rui_ro_mgr.check_bang_ke_01_1(self.app.dict_hd_mua_vao)

                    for w in warnings:
                        self.app.ghi_log(w)

                    # LỌC RA DANH SÁCH RIÊNG (Chỉ chứa HĐ bị đánh dấu Rủi ro)
                    if 'Đối chiếu HĐ rủi ro' in self.app.dict_hd_mua_vao.columns:
                        mask_rui_ro = self.app.dict_hd_mua_vao['Đối chiếu HĐ rủi ro'] == "Thuộc DS hóa đơn rủi ro"
                        df_rui_ro_rieng = self.app.dict_hd_mua_vao[mask_rui_ro].copy()
                    else:
                        df_rui_ro_rieng = pd.DataFrame()

                except Exception as e:
                    df_rui_ro_rieng = pd.DataFrame()
                    self.app.ghi_log(f"⚠️ Lỗi Radar rủi ro: {e}")

                # 1. Đổ dữ liệu GỐC (Đã găm thêm cột cảnh báo) lên Tab Mua Vào
                QuanLyBangBieu.xu_ly_bang_ke(self.ui.bang_hd_mua_vao, self.app.dict_hd_mua_vao)
                QuanLyBangBieu.cau_hinh_bang_du_lieu(self.ui.bang_hd_mua_vao)
                QuanLyBangBieu.can_bang_kich_thuoc_bang(self.ui.bang_hd_mua_vao)

                # 2. Đổ dữ liệu ĐỘC HẠI lên Tab Hóa Đơn Rủi Ro
                QuanLyBangBieu.xu_ly_bang_ke(self.ui.bang_hd_rui_ro, df_rui_ro_rieng)
                QuanLyBangBieu.cau_hinh_bang_du_lieu(self.ui.bang_hd_rui_ro)
                QuanLyBangBieu.can_bang_kich_thuoc_bang(self.ui.bang_hd_rui_ro)

                self.app.ghi_log(f"Đã gộp thành công {thanh_cong} file Hóa đơn Mua vào vào hệ thống.")
                if hasattr(self.app, 'cap_nhat_kpi_chuan_bi'):
                    self.app.cap_nhat_kpi_chuan_bi()

                # 3. Kích hoạt Popup nếu phát hiện có rác
                if not df_rui_ro_rieng.empty:
                    QMessageBox.critical(
                        self.ui,
                        "BÁO ĐỘNG ĐỎ",
                        f"Phát hiện {len(df_rui_ro_rieng)} hóa đơn đầu vào MUA CỦA DOANH NGHIỆP RỦI RO/BỎ TRỐN!\n\nHệ thống đã chuyển toàn bộ các hóa đơn này sang Tab 'Hóa đơn Rủi ro' để bạn kiểm tra."
                    )
                    # Tự động giật màn hình nhảy sang Tab Rủi Ro cho User xem ngay
                    self.ui.tabs_hoa_don.setCurrentIndex(2)
            else:
                QMessageBox.warning(self.ui, "Lỗi", "Không thể đọc các file hóa đơn này. Kiểm tra lại cấu trúc.")