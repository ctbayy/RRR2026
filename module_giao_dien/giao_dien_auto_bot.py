import os
import time
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QLineEdit, QFileDialog, QListWidget, QListWidgetItem,
                               QProgressBar, QTextEdit, QComboBox, QCheckBox, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal
import qtawesome as qta
import pandas as pd
from datetime import datetime
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

from module_doc_xml.quan_ly_doc_to_khai import QuanLyDocToKhaiXML
from module_doc_xml.tu_dien_chi_tieu import MAP_TEN_TO_KHAI
from module_ho_tro.quan_ly_cong_thuc import QuanLyCongThuc
from module_phan_tich.engine_tinh_toan import EnginePhanTich
from module_phan_tich.bao_cao_doanh_so import BaoCaoDoanhSoEngine
from module_doc_hoadon.invoice_processor import InvoiceProcessor


# =========================================================================
# LUỒNG CHẠY NGẦM (WORKER): AUTO BOT TÍCH HỢP TMS VÀ RICH LOGGING
# =========================================================================
class AutoBotWorker(QThread):
    log_msg = Signal(str)
    progress_tong = Signal(int, int)
    progress_ct = Signal(str)
    finished_batch = Signal(int, int)

    def __init__(self, thu_muc_goc, thu_muc_xuat, ds_mst, cau_hinh, parent=None):
        super().__init__(parent)
        self.thu_muc_goc = thu_muc_goc
        self.thu_muc_xuat = thu_muc_xuat
        self.ds_mst = ds_mst
        self.cau_hinh = cau_hinh
        self.is_running = True

    def run(self):
        import pythoncom
        pythoncom.CoInitialize()  # <--- GIẤY PHÉP ĐỂ QTHREAD ĐƯỢC CHẠM VÀO SAP
        thanh_cong, that_bai = 0, 0
        tong_so = len(self.ds_mst)

        self.log_msg.emit(f"🚀 BẮT ĐẦU CHẠY PHÂN TÍCH CHO {tong_so} DOANH NGHIỆP...")
        dict_tong = QuanLyCongThuc.tai_du_lieu_tong_hop()

        # MÓC CẤU HÌNH TMS TỪ MAIN THREAD RA DÙNG (Không import động nữa)
        config_tms = self.cau_hinh.get("config_tms", {})

        for idx, mst in enumerate(self.ds_mst, 1):
            if not self.is_running:
                self.log_msg.emit("🛑 ĐÃ DỪNG TIẾN TRÌNH AUTO BOT BỞI NGƯỜI DÙNG!")
                break

            self.progress_tong.emit(idx, tong_so)
            self.log_msg.emit(f"\n{'=' * 60}\n🏢 ĐANG XỬ LÝ MST: {mst} ({idx}/{tong_so})\n{'=' * 60}")

            du_lieu_to_khai = {}
            df_hdmv = pd.DataFrame()
            df_hdbr = pd.DataFrame()

            try:
                path_mst = os.path.join(self.thu_muc_goc, mst)
                path_tk = os.path.join(path_mst, "TK")
                path_hdmv = os.path.join(path_mst, "HDMV")
                path_hdbr = os.path.join(path_mst, "HDBR")

                # ===============================================================
                # 1. ĐỌC VÀ BÓC TÁCH XML
                # ===============================================================
                self.progress_ct.emit("Đang nạp Tờ khai XML...")
                quan_ly_xml = QuanLyDocToKhaiXML()

                so_luong_xml = 0
                if os.path.exists(path_tk):
                    for f in os.listdir(path_tk):
                        if f.lower().endswith('.xml'):
                            kq = quan_ly_xml.xu_ly_file_xml(os.path.join(path_tk, f))
                            ma_tk = kq.get("ThongTinChung", {}).get("MaTKhai", "N/A")
                            ky = kq.get("ThongTinChung", {}).get("KyKeKhai", "N/A")
                            ten_form = MAP_TEN_TO_KHAI.get(ma_tk, ma_tk)
                            lan_bs_moi = int(kq.get("ThongTinChung", {}).get("LanBoSung", kq.get("ThongTinChung", {}).get("SoLan", 0)))

                            if ten_form not in du_lieu_to_khai: du_lieu_to_khai[ten_form] = {}
                            if ky in du_lieu_to_khai[ten_form]:
                                tk_cu = du_lieu_to_khai[ten_form][ky]
                                lan_bs_cu = int(tk_cu.get("ThongTinChung", {}).get("LanBoSung", tk_cu.get("ThongTinChung", {}).get("SoLan", 0)))
                                if lan_bs_moi > lan_bs_cu: du_lieu_to_khai[ten_form][ky] = kq
                            else:
                                du_lieu_to_khai[ten_form][ky] = kq
                            so_luong_xml += 1

                if so_luong_xml > 0: self.log_msg.emit(f"   ✅ Đã nạp {so_luong_xml} Tờ khai XML.")
                else: self.log_msg.emit(f"   ⚠️ Thư mục TK không có Tờ khai XML nào.")

                # ===============================================================
                # 2. ĐỌC HÓA ĐƠN EXCEL
                # ===============================================================
                self.progress_ct.emit("Đang nạp Hóa đơn Mua vào/Bán ra...")

                def _doc_thu_muc_excel(thu_muc, loai):
                    dfs = []
                    so_file = 0
                    if os.path.exists(thu_muc):
                        for f in os.listdir(thu_muc):
                            if f.lower().endswith(('.xlsx', '.xls', '.csv')):
                                try:
                                    dfs.append(pd.read_excel(os.path.join(thu_muc, f)))
                                    so_file += 1
                                except Exception as e:
                                    self.log_msg.emit(f"   ❌ Lỗi đọc file {f}: {e}")

                    if so_file > 0: self.log_msg.emit(f"   ✅ Đã nạp {so_file} file {loai}.")
                    else: self.log_msg.emit(f"   ⚠️ Thư mục {loai} trống.")
                    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

                df_hdmv = _doc_thu_muc_excel(path_hdmv, "Mua vào (HDMV)")
                df_hdbr = _doc_thu_muc_excel(path_hdbr, "Bán ra (HDBR)")

                # ===============================================================
                # 2.5 TRẠM TÍCH HỢP TMS (MÓC CHUẨN 100% LUỒNG GỐC CỦA APP)
                # ===============================================================
                from PySide6.QtCore import QEventLoop

                # A. ĐỒNG BỘ NGÀY NỘP TỜ KHAI (SỬ DỤNG BotSAPWorker NGUYÊN BẢN)
                if self.cau_hinh.get('dong_bo_ngay'):
                    if not config_tms.get("user_tms"):
                        self.log_msg.emit("   ⏭️ [TMS] Bỏ qua bước tra Ngày nộp do chưa cấu hình Tài khoản SAP.")
                    else:
                        self.progress_ct.emit("Đang chạy BotSAPWorker đồng bộ ngày nộp...")
                        self.log_msg.emit("   🔍 [TMS] Khởi động luồng BotSAPWorker gốc...")
                        try:
                            from module_ho_tro.module_dong_bo_tms import BotSAPWorker

                            # Nội suy ngày y như app gốc
                            cac_nam_tms = [int(str(ky)[-4:]) for form, dict_ky in du_lieu_to_khai.items() for ky in
                                           dict_ky.keys() if str(ky)[-4:].isdigit()]
                            nam_nho_nhat = min(cac_nam_tms) if cac_nam_tms else datetime.now().year
                            tu_ngay = config_tms.get("tu_ngay") if config_tms.get(
                                "tu_ngay") else f"01.01.{nam_nho_nhat}"
                            den_ngay = config_tms.get("den_ngay") if config_tms.get(
                                "den_ngay") else datetime.now().strftime("%d.%m.%Y")
                            cqt = config_tms.get("cqt", "50500")

                            # Tạo đường dẫn cache file
                            ngay_tai = datetime.now().strftime("%d%m%Y")
                            ten_file = f"TMS_AUTO_{mst}_{ngay_tai}_{tu_ngay.replace('.', '')}_{den_ngay.replace('.', '')}.xlsx"
                            duong_dan_cache = os.path.join(self.thu_muc_xuat, ten_file)

                            # Khởi tạo Worker gốc y hệt hàm chay_engine_phan_tich
                            bot_sap = BotSAPWorker(
                                cqt, tu_ngay, den_ngay, mst, du_lieu_to_khai,
                                config_tms["user_tms"], config_tms["pass_tms"], duong_dan_cache
                            )

                            # KỸ THUẬT: Ép AutoBot chờ BotSAPWorker chạy xong
                            loop = QEventLoop()
                            ket_qua_bot = {}

                            def on_bot_sap_finished(thanh_cong, ket_qua, so_luong):
                                ket_qua_bot['thanh_cong'] = thanh_cong
                                ket_qua_bot['ket_qua'] = ket_qua
                                ket_qua_bot['so_luong'] = so_luong
                                loop.quit()  # Tháo chốt chờ

                            bot_sap.progress.connect(lambda msg: self.log_msg.emit(f"      [BotSAP] {msg}"))
                            bot_sap.finished.connect(on_bot_sap_finished)

                            bot_sap.start()
                            loop.exec()  # Dừng luồng Auto lại chờ Bot gốc cày xong

                            # Nhận kết quả từ Bot gốc
                            if ket_qua_bot.get('thanh_cong'):
                                self.log_msg.emit(
                                    f"   ✅ [TMS] Đã đồng bộ ngày nộp thực tế cho {ket_qua_bot.get('so_luong')} Tờ khai.")
                            else:
                                self.log_msg.emit(f"   ❌ [TMS] Lỗi BotSAPWorker: {ket_qua_bot.get('ket_qua')}")
                        except Exception as e:
                            import traceback
                            self.log_msg.emit(f"   💥 [FATAL] Lỗi cấu trúc gọi BotSAPWorker:\n{traceback.format_exc()}")

                # B. TRA CỨU TRẠNG THÁI HÓA ĐƠN (SỬ DỤNG SAPWorker NGUYÊN BẢN)
                if self.cau_hinh.get('check_tms'):
                    if not config_tms.get("user_tms"):
                        self.log_msg.emit("   ⏭️ [TMS] Bỏ qua tra cứu Hóa đơn do Tài khoản SAP rỗng.")
                    else:
                        self.progress_ct.emit("Đang tra cứu tình trạng Mã số thuế trên Hóa đơn...")
                        self.log_msg.emit("   🔍 [TMS] Bóc tách MST để gọi SAPWorker gốc...")
                        try:
                            mst_can_tra_cuu = set()
                            c_mv, c_br = "", ""

                            if not df_hdmv.empty:
                                if 'Mã số thuế người bán' in df_hdmv.columns:
                                    c_mv = 'Mã số thuế người bán'
                                elif 'MSTNguoiBan' in df_hdmv.columns:
                                    c_mv = 'MSTNguoiBan'
                                if c_mv: mst_can_tra_cuu.update(df_hdmv[c_mv].dropna().astype(str).unique())

                            if not df_hdbr.empty:
                                if 'MST người mua' in df_hdbr.columns:
                                    c_br = 'MST người mua'
                                elif 'MSTNguoiMua' in df_hdbr.columns:
                                    c_br = 'MSTNguoiMua'
                                if c_br: mst_can_tra_cuu.update(df_hdbr[c_br].dropna().astype(str).unique())

                            mst_can_tra_cuu = [m.strip() for m in mst_can_tra_cuu if m.strip() != ""]

                            if mst_can_tra_cuu:
                                self.log_msg.emit(f"   -> Đang đẩy {len(mst_can_tra_cuu)} MST lên SAPWorker...")
                                from module_ho_tro.sap_worker import SAPWorker

                                # Khởi tạo chuẩn xác y hệt luồng gốc
                                sap_robot = SAPWorker(list(mst_can_tra_cuu))
                                sap_robot.progress.connect(
                                    lambda step, msg: self.log_msg.emit(f"      [SAPWorker] {msg}"))
                                sap_robot.error.connect(lambda msg: self.log_msg.emit(f"      ❌ [SAPWorker LỖI] {msg}"))

                                ket_qua_tms = sap_robot.run_check()

                                if ket_qua_tms:
                                    df_tms = pd.DataFrame(ket_qua_tms,
                                                          columns=['MST_SAP', 'TenNNT', 'CQT_TMS', 'MaTrangThai',
                                                                   'TrangThaiTMS', 'NgayCapNhat'])
                                    df_map = df_tms[['MST_SAP', 'TrangThaiTMS', 'CQT_TMS']].drop_duplicates(
                                        subset=['MST_SAP'])

                                    def _map_tms(df_hd, col_mst):
                                        if df_hd.empty or not col_mst: return df_hd
                                        df_new = pd.merge(df_hd, df_map, how='left', left_on=col_mst,
                                                          right_on='MST_SAP')
                                        df_new['TrangThaiTMS'] = df_new['TrangThaiTMS'].fillna('Chưa xác định')
                                        df_new.drop(columns=['MST_SAP'], inplace=True, errors='ignore')
                                        return df_new

                                    df_hdmv = _map_tms(df_hdmv, c_mv)
                                    df_hdbr = _map_tms(df_hdbr, c_br)
                                    self.log_msg.emit("   ✅ [TMS] Map dữ liệu SAP vào Hóa đơn thành công.")
                                else:
                                    self.log_msg.emit("   ⚠️ [TMS] SAPWorker trả về kết quả rỗng.")
                            else:
                                self.log_msg.emit("   ⚠️ [TMS] Không có MST đối tác hợp lệ.")
                        except Exception as e:
                            import traceback
                            self.log_msg.emit(f"   💥 [FATAL] Lỗi cấu trúc gọi SAPWorker:\n{traceback.format_exc()}")
                # ===============================================================
                # 3. CHẠY ENGINE PHÂN TÍCH RỦI RO (MỞ KHÓA LOG)
                # ===============================================================
                self.progress_ct.emit("Đang chạy Engine Đối chiếu & Phân tích...")

                # MỞ KHÓA LOG: Truyền self.log_msg.emit để thấy Engine đang làm gì
                engine = EnginePhanTich(dict_cong_thuc=dict_tong, log_callback=self.log_msg.emit)

                nam_pt = self.cau_hinh['nam_pt']
                danh_sach_nam = [nam_pt] if nam_pt != "Tất cả các năm" else sorted(
                    list({str(k)[-4:] for d in du_lieu_to_khai.values() for k in d.keys()}))
                if not danh_sach_nam: danh_sach_nam = [str(datetime.now().year)]

                # Làm sạch hóa đơn (Bỏ xóa bỏ, hủy...)
                df_br_sach = InvoiceProcessor.loc_hoa_don_tinh_toan(df_hdbr)
                df_mv_sach = InvoiceProcessor.loc_hoa_don_tinh_toan(df_hdmv)

                for nam in danh_sach_nam:
                    self.log_msg.emit(f"\n   ⚙️ --- ĐANG TÍNH TOÁN RỦI RO NĂM {nam} ---")
                    ket_qua_list = engine.thuc_thi_phan_tich(
                        du_lieu_to_khai, df_hdbr, df_hdmv, nam_phan_tich=nam, df_cdsps_tt200=None,
                        loai_bctc=self.cau_hinh['loai_bctc'], danh_sach_rule_chon=None
                    )

                    du_lieu_br = BaoCaoDoanhSoEngine.xuat_du_lieu_bao_cao(df_br_sach, du_lieu_to_khai, nam, False,
                                                                          self.log_msg.emit)
                    du_lieu_mv = BaoCaoDoanhSoEngine.xuat_du_lieu_bao_cao(df_mv_sach, du_lieu_to_khai, nam, True,
                                                                          self.log_msg.emit)

                    # ===============================================================
                    # 4. KẾT XUẤT FULL EXCEL TỰ ĐỘNG
                    # ===============================================================
                    self.progress_ct.emit(f"Đang kết xuất TOÀN BỘ dữ liệu năm {nam}...")
                    file_name = f"BaoCaoAuto_{mst}_Nam_{nam}.xlsx"
                    path_save = os.path.join(self.thu_muc_xuat, file_name)

                    self._ghi_full_excel_bot(path_save, ket_qua_list, du_lieu_br, du_lieu_mv, du_lieu_to_khai, df_hdbr,
                                             df_hdmv, nam)
                    self.log_msg.emit(f"   💾 Đã lưu File Báo cáo: {file_name}")

                self.log_msg.emit(f"HOÀN THÀNH MST: {mst}")
                thanh_cong += 1

            except Exception as e:
                # BỌC LỖI TỔNG: Nếu code gãy giữa chừng (như lỗi thư viện, lỗi format lạ),
                # Bot sẽ ghi nhận Thất bại và bỏ qua Cty này chứ tuyệt đối không Crash app.
                self.log_msg.emit(f"❌ THẤT BẠI tại MST {mst}.\n   Chi tiết mã lỗi: {str(e)}")
                that_bai += 1
            finally:
                self.progress_ct.emit("Đang dọn dẹp bộ nhớ RAM...")
                du_lieu_to_khai.clear();
                del df_hdmv, df_hdbr
                import gc;
                gc.collect()

        self.progress_ct.emit("Đã chạy xong toàn bộ danh sách!")
        self.finished_batch.emit(thanh_cong, that_bai)



    # =========================================================================
    # BỘ CÔNG CỤ XUẤT EXCEL FULL OPTION (SAO CHÉP TỪ MODULE_XUAT_EXCEL)
    # =========================================================================
    def _dinh_dang_tieu_de(self, sheet, danh_sach_cot):
        fill_header = PatternFill(start_color="0052D4", end_color="0052D4", fill_type="solid")
        font_header = Font(color="FFFFFF", bold=True)
        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        border_thin = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                             bottom=Side(style='thin'))

        sheet.append(danh_sach_cot)
        for col_idx in range(1, len(danh_sach_cot) + 1):
            cell = sheet.cell(row=1, column=col_idx)
            cell.fill = fill_header;
            cell.font = font_header;
            cell.alignment = align_center;
            cell.border = border_thin

    def _ghi_so_excel(self, sheet, row, col, gia_tri):
        import re
        cell = sheet.cell(row=row, column=col)
        cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                             bottom=Side(style='thin'))
        try:
            if pd.isna(gia_tri) or gia_tri == "":
                val_num = 0.0
            elif isinstance(gia_tri, (int, float)):
                val_num = float(gia_tri)
            else:
                str_val = re.sub(r'[^\d.,-]', '', str(gia_tri).strip())
                if not str_val:
                    val_num = 0.0
                elif str_val.count(',') > 1:
                    val_num = float(str_val.replace(',', ''))
                elif ',' in str_val and '.' in str_val:
                    val_num = float(str_val.replace('.', '').replace(',', '.')) if str_val.rfind(',') > str_val.rfind(
                        '.') else float(str_val.replace(',', ''))
                elif ',' in str_val:
                    val_num = float(str_val.replace(',', '')) if len(str_val.split(',')[-1]) == 3 else float(
                        str_val.replace(',', '.'))
                elif '.' in str_val and str_val.count('.') > 1:
                    val_num = float(str_val.replace('.', ''))
                else:
                    val_num = float(str_val)
            cell.value = val_num
            cell.number_format = '#,##0' if val_num.is_integer() else '#,##0.00'
            cell.alignment = Alignment(horizontal="right", vertical="center")
        except:
            cell.value = str(gia_tri)
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    def _ghi_du_lieu_thong_minh(self, sheet, row, col, ten_cot, gia_tri):
        import re
        cell = sheet.cell(row=row, column=col)
        cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                             bottom=Side(style='thin'))
        val_str = str(gia_tri).strip() if pd.notna(gia_tri) else ""
        ten_cot_lower = str(ten_cot).lower()

        nhom_text = ["mst", "mã số thuế", "cmnd", "cccd", "hộ chiếu", "số giấy tờ", "điện thoại", "tài khoản"]
        if any(k in ten_cot_lower for k in nhom_text):
            cell.value = val_str;
            cell.number_format = '@'
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            return

        if "ngày" in ten_cot_lower or "ngay" in ten_cot_lower:
            if re.match(r'^\d{4}-\d{2}-\d{2}', val_str):
                try:
                    cell.value = datetime.strptime(val_str[:10], '%Y-%m-%d')
                    cell.number_format = 'dd/mm/yyyy';
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    return
                except:
                    pass
            elif re.match(r'^\d{2}/\d{2}/\d{4}', val_str):
                cell.value = val_str;
                cell.number_format = 'dd/mm/yyyy';
                cell.alignment = Alignment(horizontal="center", vertical="center")
                return
        self._ghi_so_excel(sheet, row, col, gia_tri)

    def _can_chinh_kich_thuoc_cot(self, sheet):
        font_chuan = Font(name="Times New Roman", size=11)
        for col_idx in range(1, sheet.max_column + 1):
            max_length = 0
            col_letter = openpyxl.utils.get_column_letter(col_idx)
            for row_idx in range(1, sheet.max_row + 1):
                cell = sheet.cell(row=row_idx, column=col_idx)
                if type(cell).__name__ == 'MergedCell': continue
                if getattr(cell, 'font', None):
                    cell.font = Font(name="Times New Roman", size=11, bold=cell.font.bold, italic=cell.font.italic,
                                     color=cell.font.color)
                else:
                    cell.font = font_chuan
                if col_idx == 1 and getattr(cell, 'font', None) and cell.font.bold and cell.value and len(
                    str(cell.value)) > 35: continue
                try:
                    if cell.value is not None:
                        lines = str(cell.value).split('\n')
                        for line in lines:
                            if len(line) > max_length: max_length = len(line)
                except:
                    pass
            adjusted_width = max_length + 2.0 if max_length > 0 else 12
            if adjusted_width < 5:
                adjusted_width = 5
            elif adjusted_width > 55:
                adjusted_width = 55
            sheet.column_dimensions[col_letter].width = adjusted_width

    def _ghi_full_excel_bot(self, duong_dan_luu, ds_kq, du_lieu_br, du_lieu_mv, dict_to_khai, df_hdbr, df_hdmv, nam):
        wb = openpyxl.Workbook()
        wb.remove(wb.active)
        border_thin = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        from openpyxl.comments import Comment

        # =========================================================
        # 1. VẼ KẾT QUẢ PHÂN TÍCH (BẢN FULL 7 CỘT CHUẨN GỐC)
        # =========================================================
        if ds_kq:
            def _dich_ten_chi_tieu(chuoi_goc):
                try: from module_doc_xml.tu_dien_chi_tieu import TU_DIEN_TO_KHAI
                except: TU_DIEN_TO_KHAI = {}
                if not chuoi_goc: return ""
                chuoi_str = str(chuoi_goc)
                if "Chỉ tiêu" in chuoi_str or "=" in chuoi_str: return chuoi_str
                if "|" in chuoi_str: ma_ct = chuoi_str.split("|")[-1].replace("]", "").strip()
                else: ma_ct = chuoi_str.replace("[", "").replace("]", "").strip()
                for form, form_data in TU_DIEN_TO_KHAI.items():
                    if isinstance(form_data, dict):
                        for phan_he, phan_he_data in form_data.items():
                            if isinstance(phan_he_data, dict) and ma_ct in phan_he_data: return f"[{ma_ct}] {phan_he_data[ma_ct]}"
                            elif isinstance(phan_he_data, str) and phan_he == ma_ct: return f"[{ma_ct}] {phan_he_data}"
                return f"Chỉ tiêu {ma_ct}"

            ds_cheo, ds_bctc, ds_ngang = [], [], []
            for r in ds_kq:
                nhom = str(r.get('nhom', '')).lower()
                if "chéo" in nhom: ds_cheo.append(r)
                elif "tài chính" in nhom or "bctc" in nhom: ds_bctc.append(r)
                elif "ngang" in nhom: ds_ngang.append(r)
                else: ds_bctc.append(r)

            def _ve_bang_7_cot(ten_sheet, data_list):
                if not data_list: return
                ws = wb.create_sheet(ten_sheet)
                cols = ["Nhóm Phân Tích", "Tên Phép Kiểm Tra (Logic)", "Số liệu Vế Trái (A)", "Số liệu Vế Phải (B)", "Chênh lệch (A - B)", "Đánh giá", "Khuyến nghị / Thông điệp"]
                self._dinh_dang_tieu_de(ws, cols)

                ws.column_dimensions['A'].width = 15; ws.column_dimensions['B'].width = 35; ws.column_dimensions['C'].width = 25
                ws.column_dimensions['D'].width = 25; ws.column_dimensions['E'].width = 20; ws.column_dimensions['F'].width = 18; ws.column_dimensions['G'].width = 40
                align_wrap = Alignment(vertical="center", wrap_text=True)

                for r_idx, r in enumerate(data_list, start=2):
                    is_rui_ro = r.get('is_rui_ro', False)
                    mau_nen = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid") if r_idx % 2 == 0 else PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

                    ws.cell(row=r_idx, column=1, value=r.get('nhom', '')).alignment = align_wrap
                    ws.cell(row=r_idx, column=2, value=r.get('ten_phan_tich', '')).alignment = align_wrap

                    self._ghi_so_excel(ws, r_idx, 3, r.get('gia_tri_a', 0))
                    ws.cell(row=r_idx, column=3).comment = Comment(_dich_ten_chi_tieu(r.get('ve_a_goc', '')), "Chi tiết")
                    ws.cell(row=r_idx, column=3).font = Font(bold=True)

                    if r.get('is_ab'):
                        self._ghi_so_excel(ws, r_idx, 4, r.get('gia_tri_b', 0))
                        ws.cell(row=r_idx, column=4).comment = Comment(_dich_ten_chi_tieu(r.get('ve_b_goc', '')), "Chi tiết")
                    else: ws.cell(row=r_idx, column=4, value="---").alignment = align_center
                    ws.cell(row=r_idx, column=4).font = Font(bold=True)

                    so_chenh_lech = r.get('ket_qua_so', 0)
                    self._ghi_so_excel(ws, r_idx, 5, so_chenh_lech)
                    if is_rui_ro: ws.cell(row=r_idx, column=5).font = Font(color="DC2626", bold=True)
                    else: ws.cell(row=r_idx, column=5).font = Font(bold=True)

                    tt_text = r.get('trang_thai', '')
                    c_tt = ws.cell(row=r_idx, column=6, value=tt_text)
                    c_tt.alignment = align_center
                    if is_rui_ro: c_tt.fill = PatternFill(start_color="EF4444", end_color="EF4444", fill_type="solid"); c_tt.font = Font(color="FFFFFF", bold=True)
                    elif "Thiếu" in str(so_chenh_lech) or "Không đủ" in tt_text: c_tt.fill = PatternFill(start_color="F59E0B", end_color="F59E0B", fill_type="solid"); c_tt.font = Font(color="FFFFFF", bold=True)
                    else: c_tt.fill = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid"); c_tt.font = Font(color="FFFFFF", bold=True)

                    ws.cell(row=r_idx, column=7, value=r.get('thong_diep', '')).alignment = align_wrap
                    for c_idx in range(1, 8):
                        c = ws.cell(row=r_idx, column=c_idx)
                        if c_idx != 6: c.fill = mau_nen
                        c.border = border_thin

            _ve_bang_7_cot("PT Báo cáo Tài chính", ds_bctc)
            _ve_bang_7_cot("Phân tích Ngang", ds_ngang)

            # VẼ MA TRẬN ĐỐI CHIẾU CHÉO (Full format)
            if ds_cheo:
                import re
                ws_cheo = wb.create_sheet("Đối chiếu chéo Tờ khai")
                def _lay_ma_form_excel(chuoi_goc):
                    if not chuoi_goc: return "Dữ liệu"
                    match = re.search(r'(01/GTGT|02/GTGT|03/TNDN|04/TNDN|05/QTT-TNCN|05/KK-TNCN|BCTC_TT133|BCTC_TT200|01/TAIN|02/TAIN)', str(chuoi_goc))
                    if match: return match.group(1)
                    if "HD_" in str(chuoi_goc) or "bán ra" in str(chuoi_goc).lower(): return "Hóa đơn Bán ra"
                    if "HD_MUA_VAO" in str(chuoi_goc) or "mua vào" in str(chuoi_goc).lower(): return "Hóa đơn Mua vào"
                    return "Dữ liệu"

                dict_nhom = {}
                for r in ds_cheo:
                    form_a = _lay_ma_form_excel(r.get('ve_a_goc', ''))
                    form_b = _lay_ma_form_excel(r.get('ve_b_goc', ''))
                    ten_cap = f"{form_a} VÀ {form_b}" if r.get('is_ab') else f"{form_a}"
                    if ten_cap not in dict_nhom: dict_nhom[ten_cap] = []
                    dict_nhom[ten_cap].append(r)

                r_idx = 1
                align_wrap = Alignment(vertical="center", wrap_text=True)
                ws_cheo.column_dimensions['A'].width = 8; ws_cheo.column_dimensions['B'].width = 35; ws_cheo.column_dimensions['C'].width = 25
                ws_cheo.column_dimensions['D'].width = 25; ws_cheo.column_dimensions['E'].width = 20; ws_cheo.column_dimensions['F'].width = 18; ws_cheo.column_dimensions['G'].width = 40

                for ten_cap, ds_loi in dict_nhom.items():
                    tk_a = f"Tờ khai {_lay_ma_form_excel(ds_loi[0].get('ve_a_goc', ''))}" if "hóa đơn" not in _lay_ma_form_excel(ds_loi[0].get('ve_a_goc', '')).lower() else _lay_ma_form_excel(ds_loi[0].get('ve_a_goc', ''))
                    tk_b = f"Tờ khai {_lay_ma_form_excel(ds_loi[0].get('ve_b_goc', ''))}" if ds_loi[0].get('is_ab') and "hóa đơn" not in _lay_ma_form_excel(ds_loi[0].get('ve_b_goc', '')).lower() else (_lay_ma_form_excel(ds_loi[0].get('ve_b_goc', '')) if ds_loi[0].get('is_ab') else "Dữ liệu Vế Phải (B)")
                    cols = ["STT", "Nội dung đối chiếu", tk_a, tk_b, "Chênh lệch (A-B)", "Đánh giá", "Khuyến nghị / Thông điệp"]

                    fill_header = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
                    for c_i, c_name in enumerate(cols, start=1):
                        c = ws_cheo.cell(row=r_idx, column=c_i, value=c_name)
                        c.fill = fill_header; c.font = Font(color="0F172A", bold=True); c.alignment = align_center; c.border = border_thin
                    r_idx += 1

                    for stt, r in enumerate(ds_loi, start=1):
                        is_rui_ro = r.get('is_rui_ro', False)
                        mau_nen = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid") if stt % 2 != 0 else PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

                        ws_cheo.cell(row=r_idx, column=1, value=stt).alignment = align_center
                        ws_cheo.cell(row=r_idx, column=2, value=r.get('ten_phan_tich', '')).alignment = align_wrap

                        self._ghi_so_excel(ws_cheo, r_idx, 3, r.get('gia_tri_a', 0))
                        ws_cheo.cell(row=r_idx, column=3).comment = Comment(_dich_ten_chi_tieu(r.get('ve_a_goc', '')), "Chi tiết")
                        ws_cheo.cell(row=r_idx, column=3).font = Font(bold=True)

                        if r.get('is_ab'):
                            self._ghi_so_excel(ws_cheo, r_idx, 4, r.get('gia_tri_b', 0))
                            ws_cheo.cell(row=r_idx, column=4).comment = Comment(_dich_ten_chi_tieu(r.get('ve_b_goc', '')), "Chi tiết")
                        else: ws_cheo.cell(row=r_idx, column=4, value="---").alignment = align_center
                        ws_cheo.cell(row=r_idx, column=4).font = Font(bold=True)

                        so_chenh_lech = r.get('ket_qua_so', 0)
                        self._ghi_so_excel(ws_cheo, r_idx, 5, so_chenh_lech)
                        if is_rui_ro: ws_cheo.cell(row=r_idx, column=5).font = Font(color="DC2626", bold=True)
                        else: ws_cheo.cell(row=r_idx, column=5).font = Font(bold=True)

                        tt_text = r.get('trang_thai', '')
                        c_tt = ws_cheo.cell(row=r_idx, column=6, value=tt_text)
                        c_tt.alignment = align_center
                        if is_rui_ro: c_tt.fill = PatternFill(start_color="EF4444", end_color="EF4444", fill_type="solid"); c_tt.font = Font(color="FFFFFF", bold=True)
                        elif "Thiếu" in str(so_chenh_lech) or "Không đủ" in tt_text: c_tt.fill = PatternFill(start_color="F59E0B", end_color="F59E0B", fill_type="solid"); c_tt.font = Font(color="FFFFFF", bold=True)
                        else: c_tt.fill = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid"); c_tt.font = Font(color="FFFFFF", bold=True)

                        ws_cheo.cell(row=r_idx, column=7, value=r.get('thong_diep', '')).alignment = align_wrap
                        for c_idx in range(1, 8):
                            c = ws_cheo.cell(row=r_idx, column=c_idx)
                            if c_idx != 6: c.fill = mau_nen
                            c.border = border_thin
                        r_idx += 1

        # --- 2. VẼ BÁO CÁO ĐỐI CHIẾU DOANH SỐ (CHUẨN 100% BẢN GỐC) ---
        if du_lieu_br or du_lieu_mv:
            ws_bc = wb.create_sheet("Đối chiếu Hóa đơn")
            dong_ht = 1

            def _ve_bang_bao_cao_excel(ws, start_row, tieu_de, data):
                if not data: return start_row
                ws.cell(row=start_row, column=1, value=tieu_de).font = Font(bold=True, size=11, color="000000"); start_row += 1
                fill_header = PatternFill(start_color="F0F0F0", end_color="F0F0F0", fill_type="solid")
                for r_offset, h_list in enumerate([["STT", "Kỳ", "Hóa đơn điện tử", "", "Hồ sơ khai thuế", "", "Chênh lệch (KK-Hóa đơn)", ""], ["", "", "Giá trị chưa thuế", "Thuế GTGT", "Giá trị chưa thuế", "Thuế GTGT", "Giá trị chưa thuế", "Thuế GTGT"]]):
                    for i, text in enumerate(h_list, 1):
                        c = ws.cell(row=start_row + r_offset, column=i, value=text)
                        c.fill = fill_header; c.font = Font(bold=True); c.alignment = align_center; c.border = border_thin

                ws.merge_cells(start_row=start_row, start_column=1, end_row=start_row+1, end_column=1); ws.merge_cells(start_row=start_row, start_column=2, end_row=start_row+1, end_column=2)
                ws.merge_cells(start_row=start_row, start_column=3, end_row=start_row, end_column=4); ws.merge_cells(start_row=start_row, start_column=5, end_row=start_row, end_column=6); ws.merge_cells(start_row=start_row, start_column=7, end_row=start_row, end_column=8)
                row_idx = start_row + 2
                tong_hd_truoc = tong_hd_thue = tong_tk_truoc = tong_tk_thue = 0

                for stt, r_data in enumerate(data, 1):
                    hd_truoc, hd_thue = r_data.get('hd_truoc', 0), r_data.get('hd_thue', 0)
                    tk_truoc, tk_thue = r_data.get('tk_truoc', 0), r_data.get('tk_thue', 0)
                    tong_hd_truoc += hd_truoc; tong_hd_thue += hd_thue; tong_tk_truoc += tk_truoc; tong_tk_thue += tk_thue

                    ws.cell(row=row_idx, column=1, value=stt).alignment = align_center; ws.cell(row=row_idx, column=2, value=r_data.get('ky', '')).alignment = align_center
                    self._ghi_so_excel(ws, row_idx, 3, hd_truoc if hd_truoc else "-"); self._ghi_so_excel(ws, row_idx, 4, hd_thue if hd_thue else "-")
                    self._ghi_so_excel(ws, row_idx, 5, tk_truoc if tk_truoc else "-"); self._ghi_so_excel(ws, row_idx, 6, tk_thue if tk_thue else "-")
                    self._ghi_so_excel(ws, row_idx, 7, (tk_truoc - hd_truoc) if (tk_truoc - hd_truoc) else "-"); self._ghi_so_excel(ws, row_idx, 8, (tk_thue - hd_thue) if (tk_thue - hd_thue) else "-")

                    for c_fix in range(3, 9):
                        if ws.cell(row=row_idx, column=c_fix).value == "-": ws.cell(row=row_idx, column=c_fix).alignment = Alignment(horizontal="right", vertical="center")
                    for c in range(1, 9): ws.cell(row=row_idx, column=c).border = border_thin
                    row_idx += 1

                ws.cell(row=row_idx, column=1, value="Tổng").alignment = align_center; ws.cell(row=row_idx, column=1).font = Font(bold=True)
                ws.merge_cells(start_row=row_idx, start_column=1, end_row=row_idx, end_column=2)
                self._ghi_so_excel(ws, row_idx, 3, tong_hd_truoc if tong_hd_truoc else "-"); self._ghi_so_excel(ws, row_idx, 4, tong_hd_thue if tong_hd_thue else "-")
                self._ghi_so_excel(ws, row_idx, 5, tong_tk_truoc if tong_tk_truoc else "-"); self._ghi_so_excel(ws, row_idx, 6, tong_tk_thue if tong_tk_thue else "-")
                self._ghi_so_excel(ws, row_idx, 7, (tong_tk_truoc - tong_hd_truoc) if (tong_tk_truoc - tong_hd_truoc) else "-"); self._ghi_so_excel(ws, row_idx, 8, (tong_tk_thue - tong_hd_thue) if (tong_tk_thue - tong_hd_thue) else "-")

                for c in range(1, 9):
                    ws.cell(row=row_idx, column=c).border = border_thin; ws.cell(row=row_idx, column=c).font = Font(bold=True)
                    if ws.cell(row=row_idx, column=c).value == "-": ws.cell(row=row_idx, column=c).alignment = Alignment(horizontal="right", vertical="center")
                return row_idx + 3

            dong_ht = _ve_bang_bao_cao_excel(ws_bc, dong_ht, "1.1.2. Chênh lệch doanh số bán ra trên hồ sơ khai thuế và dữ liệu hóa đơn điện tử:", du_lieu_br)
            dong_ht = _ve_bang_bao_cao_excel(ws_bc, dong_ht, "1.1.3. Chênh lệch giá trị HHDV mua vào, thuế GTGT đầu vào được khấu trừ trên hồ sơ khai thuế và dữ liệu hóa đơn điện tử:", du_lieu_mv)
            ws_bc.column_dimensions['A'].width = 8; ws_bc.column_dimensions['B'].width = 12
            for c in ['C', 'D', 'E', 'F', 'G', 'H']: ws_bc.column_dimensions[c].width = 20

        # --- 3. VẼ TỜ KHAI (XML) MA TRẬN & BCTC ---
        def _sort_ky(ky_str):
            try:
                t_q, y = ky_str.split('/')
                if 'Q' in t_q.upper() or 'q' in t_q.lower(): m = int(t_q.upper().replace('Q', '')) * 3 - 2
                else: m = int(t_q)
                return int(y) * 100 + m
            except: return 999999

        for ma_form, dict_ky in dict_to_khai.items():
            danh_sach_ky = [ky for ky in sorted(list(dict_ky.keys()), key=_sort_ky) if nam in str(ky)]
            if not danh_sach_ky: continue

            ws_tk = wb.create_sheet(f"TKhai {str(ma_form).replace('/', '_').replace(chr(92), '_')[:31]}")
            ma_tran, ds_bctc = {}, []

            for ky in danh_sach_ky:
                data = dict_ky[ky]
                for ma_ct, val_dict in data.get("ChiTieuChinh", {}).items():
                    if "Chỉ tiêu chính" not in ma_tran: ma_tran["Chỉ tiêu chính"] = {}
                    if ma_ct not in ma_tran["Chỉ tiêu chính"]: ma_tran["Chỉ tiêu chính"][ma_ct] = {"DienGiai": val_dict.get("DienGiai", ""), "GiaTri": {}}
                    ma_tran["Chỉ tiêu chính"][ma_ct]["GiaTri"][ky] = val_dict.get("GiaTri", 0)
                for ph in ["B01_CDKT", "B02_KQKD", "B03_LCTT", "B04_CDTK"]:
                    if ph in data and data[ph]: ds_bctc.append({"Ky": ky, "PhanHe": ph, "DuLieu": data[ph]})

            r_idx = 1
            if ma_tran:
                self._dinh_dang_tieu_de(ws_tk, ["Phân Hệ", "Mã CT", "Diễn Giải"] + danh_sach_ky)
                r_idx += 1
                for phan_he, dict_ct in ma_tran.items():
                    ws_tk.cell(row=r_idx, column=1, value=phan_he).font = Font(bold=True); r_idx += 1
                    for ma_ct, info in dict_ct.items():
                        ws_tk.cell(row=r_idx, column=2, value=ma_ct).border = border_thin
                        ws_tk.cell(row=r_idx, column=3, value=info["DienGiai"]).border = border_thin
                        for c_idx, ky in enumerate(danh_sach_ky): self._ghi_so_excel(ws_tk, r_idx, 4 + c_idx, info["GiaTri"].get(ky, 0))
                        r_idx += 1
            if ds_bctc:
                r_idx += 2
                for bctc in ds_bctc:
                    ws_tk.cell(row=r_idx, column=1, value=f"--- BÁO CÁO TÀI CHÍNH: {bctc['PhanHe']} (Kỳ: {bctc['Ky']}) ---").font = Font(bold=True, color="D83B01"); r_idx += 1
                    du_lieu_bctc = bctc['DuLieu']
                    if not du_lieu_bctc: continue
                    cot_gia_tri = [k for k in du_lieu_bctc[list(du_lieu_bctc.keys())[0]].keys() if k != "DienGiai"]
                    self._dinh_dang_tieu_de(ws_tk, ["Mã Chỉ Tiêu", "Nội Dung Diễn Giải"] + cot_gia_tri); r_idx += 1
                    for ma_ct, row_data in du_lieu_bctc.items():
                        ws_tk.cell(row=r_idx, column=1, value=ma_ct).border = border_thin
                        ws_tk.cell(row=r_idx, column=2, value=row_data.get("DienGiai", "")).border = border_thin
                        for i, ten_cot in enumerate(cot_gia_tri): self._ghi_so_excel(ws_tk, r_idx, 3 + i, row_data.get(ten_cot, "0"))
                        r_idx += 1
                    r_idx += 1

        # --- 4. VẼ HÓA ĐƠN RAW (THÔ) ĐẦY ĐỦ ---
        def _xuat_hoa_don_tho(ten_sheet, df_hd):
            if isinstance(df_hd, pd.DataFrame) and not df_hd.empty:
                if '_Nam' in df_hd.columns: df_hd = df_hd[df_hd['_Nam'] == nam].copy()
                if not df_hd.empty:
                    ws_hd = wb.create_sheet(ten_sheet)
                    cols = [col for col in df_hd.columns if not str(col).startswith("_")]
                    self._dinh_dang_tieu_de(ws_hd, cols)
                    tu_khoa_so = ["tiền", "thuế", "đơn giá", "số lượng", "giá trị", "tien", "thue", "dongia", "soluong", "giatri"]
                    for r_idx, row in enumerate(df_hd[cols].itertuples(index=False), start=2):
                        for c_idx, val in enumerate(row, start=1):
                            col_name = str(cols[c_idx - 1]).lower().replace(" ", "")
                            if any(k in col_name for k in tu_khoa_so): self._ghi_so_excel(ws_hd, r_idx, c_idx, val)
                            else: self._ghi_du_lieu_thong_minh(ws_hd, r_idx, c_idx, cols[c_idx - 1], val)

        _xuat_hoa_don_tho("HĐ Bán Ra", df_hdbr)
        _xuat_hoa_don_tho("HĐ Mua Vào", df_hdmv)

        # Chốt lưu file
        if not wb.sheetnames: wb.create_sheet("Không có dữ liệu")
        for sheet_name in wb.sheetnames: self._can_chinh_kich_thuoc_cot(wb[sheet_name])
        wb.save(duong_dan_luu)


# =========================================================================
# GIAO DIỆN CẤU HÌNH AUTO BOT (POPUP)
# =========================================================================
class DialogAutoBot(QDialog):
    def __init__(self, main_app, parent=None):
        super().__init__(parent)
        self.main_app = main_app
        self.setWindowTitle("🤖 Phân tích dữ liệu tự động")
        self.setFixedSize(850, 650)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        self.setStyleSheet("""
            QDialog { background-color: #f8fafc; }
            QGroupBox { font-weight: bold; color: #1e3a8a; border: 1px solid #cbd5e1; border-radius: 6px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
            QLineEdit { padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px; background: #ffffff; }
            QPushButton { font-weight: bold; border-radius: 5px; padding: 8px; }
        """)

        self._thiet_lap_ui()

    def _thiet_lap_ui(self):
        layout_chinh = QVBoxLayout(self)

        # ---------------------------------------------------------
        # KHỐI 1: CHỌN ĐƯỜNG DẪN & QUÉT TỰ ĐỘNG
        # ---------------------------------------------------------
        grp_duong_dan = QGroupBox("1. Thiết lập Thư mục")
        layout_dd = QVBoxLayout(grp_duong_dan)

        khung_chon_goc = QHBoxLayout()
        self.txt_thu_muc_goc = QLineEdit()
        self.txt_thu_muc_goc.setReadOnly(True)
        self.txt_thu_muc_goc.setPlaceholderText("Chưa chọn thư mục chứa các MST...")
        btn_chon_goc = QPushButton(" Chọn Thư mục Nguồn")
        btn_chon_goc.setIcon(qta.icon('fa5s.folder-open', color='#3b82f6'))
        btn_chon_goc.setStyleSheet("background-color: #e0f2fe; color: #0284c7; border: 1px solid #7dd3fc;")
        btn_chon_goc.clicked.connect(self.chon_thu_muc_goc)
        khung_chon_goc.addWidget(self.txt_thu_muc_goc)
        khung_chon_goc.addWidget(btn_chon_goc)

        khung_chon_xuat = QHBoxLayout()
        self.txt_thu_muc_xuat = QLineEdit()
        self.txt_thu_muc_xuat.setReadOnly(True)
        self.txt_thu_muc_xuat.setPlaceholderText("Chưa chọn thư mục lưu Báo cáo Excel...")
        btn_chon_xuat = QPushButton(" Chọn Thư mục Đích")
        btn_chon_xuat.setIcon(qta.icon('fa5s.save', color='#10b981'))
        btn_chon_xuat.setStyleSheet("background-color: #d1fae5; color: #059669; border: 1px solid #6ee7b7;")
        btn_chon_xuat.clicked.connect(self.chon_thu_muc_xuat)
        khung_chon_xuat.addWidget(self.txt_thu_muc_xuat)
        khung_chon_xuat.addWidget(btn_chon_xuat)

        layout_dd.addLayout(khung_chon_goc)
        layout_dd.addLayout(khung_chon_xuat)
        layout_chinh.addWidget(grp_duong_dan)

        # ---------------------------------------------------------
        # KHỐI 2: THÂN APP (LIST MST VÀ CẤU HÌNH DÙNG CHUNG)
        # ---------------------------------------------------------
        khung_giua = QHBoxLayout()

        # Cột trái: Danh sách MST quét được
        grp_mst = QGroupBox("2. Danh sách Mã Số Thuế")
        layout_mst = QVBoxLayout(grp_mst)

        self.chk_chon_tat_ca = QCheckBox("Chọn tất cả")
        self.chk_chon_tat_ca.setChecked(True)
        self.chk_chon_tat_ca.toggled.connect(self.xu_ly_chon_tat_ca_mst)
        layout_mst.addWidget(self.chk_chon_tat_ca)

        self.list_mst = QListWidget()
        self.list_mst.setStyleSheet("background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px;")
        layout_mst.addWidget(self.list_mst)
        khung_giua.addWidget(grp_mst, 5)

        # ... (Cột trái danh sách MST giữ nguyên) ...

        # ---------------------------------------------------------
        # CỘT PHẢI: CẤU HÌNH DÙNG CHUNG (COPY 100% TỪ GIAO DIỆN CHÍNH)
        # ---------------------------------------------------------
        # ---------------------------------------------------------
        # CỘT PHẢI: CẤU HÌNH DÙNG CHUNG
        # ---------------------------------------------------------
        grp_cau_hinh = QGroupBox("2. Cấu hình Phân tích Auto")
        grp_cau_hinh.setStyleSheet("""
                    QGroupBox { border: none; margin-top: 5px; }
                    QGroupBox::title { color: #1e3a8a; font-size: 15px; font-weight: bold; }
                    QLabel { color: #334155; margin-top: 5px; }
                    QComboBox { padding: 6px; border: 1px solid #cbd5e1; border-radius: 4px; background: white; min-height: 22px; }
                    QComboBox:focus { border: 1px solid #3b82f6; }
                    QCheckBox { color: #475569; font-size: 13px; }
                """)
        layout_ch = QVBoxLayout(grp_cau_hinh)
        layout_ch.setSpacing(8)

        # 1. Loại Báo cáo tài chính
        layout_ch.addWidget(QLabel("Loại Báo cáo tài chính:"))
        self.cb_bctc = QComboBox()
        self.cb_bctc.addItems(["Tự động nhận diện", "Theo Thông tư 200", "Theo Thông tư 133"])
        layout_ch.addWidget(self.cb_bctc)

        # 2. Năm phân tích
        layout_ch.addWidget(QLabel("Năm phân tích:"))
        self.cb_nam = QComboBox()
        self.cb_nam.addItems(["Tất cả các năm", "2026", "2025", "2024", "2023", "2022"])
        layout_ch.addWidget(self.cb_nam)

        # 3. Cụm TMS
        khung_tms = QHBoxLayout()
        khung_tms.setContentsMargins(0, 10, 0, 5)

        khung_checkbox_tms = QVBoxLayout()
        khung_checkbox_tms.setSpacing(5)
        self.chk_tms = QCheckBox("Tra cứu trạng thái HĐ doanh nghiệp từ TMS")
        self.chk_dong_bo_ngay = QCheckBox("Tra cứu ngày nộp Tờ khai từ TMS")
        khung_checkbox_tms.addWidget(self.chk_tms)
        khung_checkbox_tms.addWidget(self.chk_dong_bo_ngay)

        btn_cau_hinh_tms = QPushButton(" Cấu hình TMS")
        btn_cau_hinh_tms.setIcon(qta.icon('fa5s.cog', color='#475569'))
        btn_cau_hinh_tms.setStyleSheet("""
                    QPushButton { background-color: #e2e8f0; color: #334155; border: 1px solid #cbd5e1; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
                    QPushButton:hover { background-color: #cbd5e1; }
                """)
        btn_cau_hinh_tms.clicked.connect(self.main_app.mo_cau_hinh_tms)

        khung_tms.addLayout(khung_checkbox_tms)
        khung_tms.addStretch()
        khung_tms.addWidget(btn_cau_hinh_tms, alignment=Qt.AlignmentFlag.AlignBottom)
        layout_ch.addLayout(khung_tms)

        # Cắt đứt phần giao diện ở đây, không chèn thêm nút Start hay Lưu tùy chọn nữa!
        layout_ch.addStretch()

        khung_giua.addWidget(grp_cau_hinh, 4)
        layout_chinh.addLayout(khung_giua)


        # ---------------------------------------------------------
        # KHỐI 3: TIẾN ĐỘ & LOG XỬ LÝ
        # ---------------------------------------------------------
        grp_log = QGroupBox("4. Tiến độ xử lý")
        layout_log = QVBoxLayout(grp_log)

        self.lbl_trang_thai = QLabel("Sẵn sàng...")
        self.lbl_trang_thai.setStyleSheet("font-weight: bold; color: #0284c7;")
        layout_log.addWidget(self.lbl_trang_thai)

        self.prg_tong = QProgressBar()
        self.prg_tong.setStyleSheet(
            "QProgressBar { border: 1px solid #cbd5e1; border-radius: 4px; text-align: center; } QProgressBar::chunk { background-color: #10b981; }")
        layout_log.addWidget(self.prg_tong)

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        # ĐÃ SỬA: Đổi nền sang trắng, chữ xám đen, thêm viền bo góc mượt mà
        self.txt_log.setStyleSheet("""
                    QTextEdit {
                        background-color: #ffffff; 
                        color: #334155; 
                        font-family: Consolas, 'Courier New', monospace; 
                        font-size: 13px; 
                        border: 1px solid #cbd5e1;
                        border-radius: 4px;
                        padding: 5px;
                    }
                """)
        layout_log.addWidget(self.txt_log)
        layout_chinh.addWidget(grp_log)

        # ---------------------------------------------------------
        # KHỐI NÚT ĐIỀU KHIỂN
        # ---------------------------------------------------------
        khung_dieu_khien = QHBoxLayout()
        self.btn_dong = QPushButton(" Đóng cửa sổ")
        self.btn_dong.setIcon(qta.icon('fa5s.times', color='#64748b'))
        self.btn_dong.setStyleSheet("background-color: #f1f5f9; border: 1px solid #cbd5e1; color: #475569;")
        self.btn_dong.clicked.connect(self.reject)

        self.btn_chay_auto = QPushButton(" CHẠY PHÂN TÍCH ")
        self.btn_chay_auto.setIcon(qta.icon('fa5s.robot', color='white'))
        self.btn_chay_auto.setStyleSheet("background-color: #2563eb; color: white; padding: 12px; font-size: 14px;")
        self.btn_chay_auto.clicked.connect(self.thuc_thi_auto)

        khung_dieu_khien.addWidget(self.btn_dong)
        khung_dieu_khien.addWidget(self.btn_chay_auto)
        layout_chinh.addLayout(khung_dieu_khien)

    # =========================================================================
    # CÁC HÀM LOGIC GIAO DIỆN
    # =========================================================================
    def chon_thu_muc_goc(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Chọn Thư mục chứa các MST")
        if folder_path:
            self.txt_thu_muc_goc.setText(folder_path)
            self.quet_thu_muc_mst(folder_path)

    def chon_thu_muc_xuat(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Chọn Thư mục xuất Báo cáo")
        if folder_path:
            self.txt_thu_muc_xuat.setText(folder_path)

    def quet_thu_muc_mst(self, folder_path):
        """Hàm tự động quét và lọc ra các thư mục là MST hợp lệ"""
        self.list_mst.clear()
        so_luong = 0
        try:
            for ten_thu_muc in os.listdir(folder_path):
                full_path = os.path.join(folder_path, ten_thu_muc)
                if os.path.isdir(full_path):
                    # Kiểm tra xem có cấu trúc chuẩn bên trong không
                    subdirs = [d.upper() for d in os.listdir(full_path) if os.path.isdir(os.path.join(full_path, d))]
                    if "TK" in subdirs or "HDMV" in subdirs or "HDBR" in subdirs:
                        item = QListWidgetItem(ten_thu_muc)
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(Qt.CheckState.Checked)
                        self.list_mst.addItem(item)
                        so_luong += 1

            self.ghi_log(f"🔍 Quét thành công: Phát hiện {so_luong} công ty.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi quét thư mục", str(e))

    def xu_ly_chon_tat_ca_mst(self, checked):
        for i in range(self.list_mst.count()):
            item = self.list_mst.item(i)
            item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

    def ghi_log(self, text):
        self.txt_log.append(text)
        self.txt_log.verticalScrollBar().setValue(self.txt_log.verticalScrollBar().maximum())

    # =========================================================================
    # KÍCH HOẠT BOT VÀ THEO DÕI TIẾN ĐỘ
    # =========================================================================
    def thuc_thi_auto(self):
        tm_goc = self.txt_thu_muc_goc.text().strip()
        tm_xuat = self.txt_thu_muc_xuat.text().strip()

        if not tm_goc or not tm_xuat:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn đầy đủ Thư mục Nguồn và Thư mục Đích!")
            return

        ds_mst_chay = []
        for i in range(self.list_mst.count()):
            item = self.list_mst.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                ds_mst_chay.append(item.text())

        if not ds_mst_chay:
            QMessageBox.warning(self, "Lỗi", "Bạn chưa tích chọn Mã số thuế nào để chạy!")
            return

        # Khóa giao diện
        self.btn_chay_auto.setEnabled(False)
        self.btn_dong.setEnabled(False)
        self.prg_tong.setMaximum(len(ds_mst_chay))
        self.prg_tong.setValue(0)
        self.txt_log.clear()

        config_tms = {}
        try:
            from module_ho_tro.module_cau_hinh_tms import TMSConfig
            config_tms = TMSConfig.load()
        except:
            pass
        # Gom cấu hình
        cau_hinh = {
            "nam_pt": self.cb_nam.currentText(),
            "loai_bctc": self.cb_bctc.currentText(),
            "check_tms": self.chk_tms.isChecked(),
            "dong_bo_ngay": self.chk_dong_bo_ngay.isChecked(),  # <--- THÊM DÒNG NÀY
            "config_tms": config_tms  # <--- CHÍNH LÀ CHỖ NÀY BỊ THIẾU
        }

        # Khởi tạo và kết nối Worker
        self.worker = AutoBotWorker(tm_goc, tm_xuat, ds_mst_chay, cau_hinh)
        self.worker.log_msg.connect(self.ghi_log)
        self.worker.progress_tong.connect(self.cap_nhat_tien_do)
        self.worker.progress_ct.connect(lambda txt: self.lbl_trang_thai.setText(txt))
        self.worker.finished_batch.connect(self.hoan_thanh_batch)

        # CHẠY
        self.worker.start()

    def cap_nhat_tien_do(self, hien_tai, tong):
        self.prg_tong.setValue(hien_tai)

    def hoan_thanh_batch(self, thanh_cong, that_bai):
        self.lbl_trang_thai.setText("HOÀN TẤT!")
        self.btn_chay_auto.setEnabled(True)
        self.btn_dong.setEnabled(True)
        QMessageBox.information(self, "Hoàn thành",
                                f"Đã chạy Auto xong!\n- Thành công: {thanh_cong}\n- Thất bại: {that_bai}")