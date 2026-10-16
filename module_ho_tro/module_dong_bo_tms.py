# module_dong_bo_tms.py
import os
import time
import pandas as pd
from datetime import datetime
import win32com.client
import pythoncom
import subprocess
from PySide6.QtCore import QThread, Signal


# =====================================================================
# 1. CÁC HÀM XỬ LÝ LÕI (NGHIỆP VỤ)
# =====================================================================

def chay_tu_dong_3233(tu_ngay, den_ngay, ma_cqt, thu_muc_luu, ten_file="DanhSachToKhai.xlsx"):
    duong_dan_day_du = os.path.join(thu_muc_luu, ten_file)
    if os.path.exists(duong_dan_day_du):
        try:
            os.remove(duong_dan_day_du)
        except:
            return False, "Vui lòng đóng file Excel DanhSachToKhai.xlsx trước khi chạy."

    try:
        SapGuiAuto = win32com.client.GetObject("SAPGUI")
        application = SapGuiAuto.GetScriptingEngine
        connection = application.Children(0)
        session = connection.Children(0)

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nZTC_SEARCH_FORM"
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]/usr/ctxtS_BUKRS-LOW").text = ma_cqt
        session.findById("wnd[0]/usr/ctxtS_DATE-LOW").text = tu_ngay
        session.findById("wnd[0]/usr/ctxtS_DATE-HIGH").text = den_ngay
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        session.findById("wnd[0]/tbar[1]/btn[13]").press()
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = thu_muc_luu
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = ten_file
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        time_wait = 0
        while not os.path.exists(duong_dan_day_du) and time_wait < 45:
            time.sleep(1)
            time_wait += 1

        if not os.path.exists(duong_dan_day_du): return False, "Time out! Không tải được file."
        return True, duong_dan_day_du
    except Exception as e:
        return False, f"Lỗi kết nối SAP TMS: {e}"


def convert_tms_period(tms_ky):
    tms_ky = str(tms_ky).strip().upper()
    if len(tms_ky) == 4:
        yy = "20" + tms_ky[:2]
        suffix = tms_ky[2:]
        if suffix.startswith('Q'):
            return f"{suffix}/{yy}"
        elif suffix == 'CN':
            return yy
        elif suffix.isdigit():
            return f"{suffix}/{yy}"
    return tms_ky


def dong_bo_ngay_nop_tu_excel(duong_dan_excel, dict_he_thong_to_khai):
    try:
        df = pd.read_excel(duong_dan_excel, dtype=str)
        df.columns = [str(c).replace('\n', '').strip() for c in df.columns]
        trang_thai_hop_le = ['13', '6B', '04', '4E']
        col_tt = 'Trạng thái chính' if 'Trạng thái chính' in df.columns else 'Trạng thái xử lý'

        if col_tt in df.columns: df = df[df[col_tt].isin(trang_thai_hop_le)]

        map_ngay_nop = {}
        for _, row in df.iterrows():
            ten_tk = str(row.get('Têntờ khai', row.get('Tên tờ khai', ''))).strip()
            ky_tms = str(row.get('Kỳ tính thuế', '')).strip()
            lan_bs = str(row.get('Lần bổ sung', '0')).strip()
            ngay_nhan_goc = str(row.get('Ngày nhận', '')).strip()

            if not ten_tk or not ky_tms or not ngay_nhan_goc or ngay_nhan_goc.lower() == 'nan': continue
            ky_chuan = convert_tms_period(ky_tms)
            try:
                ngay_nhan_chuan = datetime.strptime(ngay_nhan_goc.split()[0], '%Y-%m-%d').strftime('%d/%m/%Y')
            except:
                ngay_nhan_chuan = ngay_nhan_goc

            map_ngay_nop[(ten_tk, ky_chuan, lan_bs)] = ngay_nhan_chuan

        so_luong_dong_bo = 0
        for ma_form, dict_ky in dict_he_thong_to_khai.items():
            for ky, to_khai_data in dict_ky.items():
                lan_bs_xml = str(to_khai_data.get('SoLan', '0'))
                key_xml = (ma_form, ky, lan_bs_xml)
                if key_xml in map_ngay_nop:
                    if 'ThongTinChung' in to_khai_data:
                        to_khai_data['ThongTinChung']['ngayLapTKhai'] = map_ngay_nop[key_xml]
                    so_luong_dong_bo += 1
        return so_luong_dong_bo, "Thành công"
    except Exception as e:
        return -1, str(e)


# =====================================================================
# 2. CLASS ĐIỀU PHỐI ĐA LUỒNG VÀ TỰ ĐỘNG ĐĂNG NHẬP
# =====================================================================

class BotSAPWorker(QThread):
    finished = Signal(bool, str, int)  # (thanh_cong, ket_qua_hoac_loi, so_luong_dong_bo)
    progress = Signal(str)  # Cập nhật text cho Spinner Loading

    def __init__(self, cqt, tu_ngay, den_ngay, mst, dict_xml, user, pwd, file_cache):
        super().__init__()
        self.cqt = cqt
        self.tu_ngay = tu_ngay
        self.den_ngay = den_ngay
        self.mst = mst
        self.dict_xml = dict_xml
        self.user = user
        self.pwd = pwd
        self.file_cache = file_cache

    def an_tat_ca_cua_so_sap_excel(self):
        """Hệ thống quét ngầm: Ép các cửa sổ SAP/Excel thu nhỏ xuống Taskbar"""
        try:
            import ctypes
            EnumWindows = ctypes.windll.user32.EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

            def foreach_window(hwnd, lParam):
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value.lower()
                    if "sap" in title or "excel" in title or "tms" in title:
                        if ctypes.windll.user32.IsWindowVisible(hwnd):
                            ctypes.windll.user32.ShowWindow(hwnd, 6)  # Mã 6: Minimize
                return True

            EnumWindows(EnumWindowsProc(foreach_window), 0)
        except:
            pass

    def tu_dong_dang_nhap(self):
        """Mở SAP Logon, kết nối TMS và điền ID/Pass"""
        try:
            SapGuiAuto = win32com.client.GetObject("SAPGUI")
        except:
            self.progress.emit("Đang khởi chạy SAP Logon (Tàng hình)...")
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = 6
            subprocess.Popen(r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe", startupinfo=info)
            for _ in range(10):
                self.an_tat_ca_cua_so_sap_excel()
                time.sleep(0.3)
            SapGuiAuto = win32com.client.GetObject("SAPGUI")

        app = SapGuiAuto.GetScriptingEngine
        if app.Children.Count == 0:
            app.OpenConnection("TMS", True)
            time.sleep(2)

        self.an_tat_ca_cua_so_sap_excel()
        session = app.Children(0).Children(0)

        try:
            txt_user = session.findById("wnd[0]/usr/txtRSYST-BNAME")
            self.progress.emit("Đang tự động điền tài khoản SAP...")
            txt_user.text = self.user
            session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = self.pwd
            session.findById("wnd[0]").sendVKey(0)
            time.sleep(2)
            # Tắt popup cảnh báo đăng nhập nhiều nơi nếu có
            if session.ActiveWindow.Name == "wnd[1]":
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except:
            self.progress.emit("TMS đã đăng nhập sẵn. Bỏ qua nhập ID/Pass...")

        self.an_tat_ca_cua_so_sap_excel()
        return session

    def run(self):
        """Hàm thực thi ngầm của QThread"""
        # Bắt buộc khởi tạo COM trong luồng phụ khi dùng win32com
        pythoncom.CoInitialize()
        try:
            thu_muc_luu = os.path.dirname(self.file_cache)
            ten_file = os.path.basename(self.file_cache)

            # 1. KÉO DỮ LIỆU TỪ SAP (Nếu chưa có Cache)
            if not os.path.exists(self.file_cache):
                # Kích hoạt thủ tục Đăng nhập trước
                self.tu_dong_dang_nhap()

                self.progress.emit("Đang gọi T-Code ZTC_SEARCH_FORM trích xuất Danh sách tờ khai...")
                thanh_cong, ket_qua = chay_tu_dong_3233(self.tu_ngay, self.den_ngay, self.cqt, thu_muc_luu, ten_file)

                if not thanh_cong:
                    self.finished.emit(False, ket_qua, 0)
                    return
            else:
                self.progress.emit("Đã có dữ liệu Cache. Bỏ qua bước kéo SAP...")

            # 2. ĐỒNG BỘ VÀO BỘ NHỚ XML
            self.progress.emit("Đang đồng bộ ngày nộp vào hồ sơ XML...")
            so_luong, msg = dong_bo_ngay_nop_tu_excel(self.file_cache, self.dict_xml)

            if so_luong >= 0:
                self.finished.emit(True, self.file_cache, so_luong)
            else:
                self.finished.emit(False, msg, 0)

        except Exception as e:
            self.finished.emit(False, f"Lỗi Bot RPA: {e}", 0)
        finally:
            pythoncom.CoUninitialize()