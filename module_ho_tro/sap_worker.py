from PySide6.QtCore import QObject, Signal
from datetime import datetime, date, timedelta
from pandas import Timestamp
import pandas as pd
import pythoncom
import xml.etree.ElementTree as ET
import os
import re
try:
    import win32com.client
except ImportError:
    win32com = None
import time
import pyperclip


class SAPWorker(QObject):
    # ĐỔI TOÀN BỘ 'pyqtSignal' THÀNH 'Signal'
    finished = Signal(object)
    progress = Signal(int, str)
    error = Signal(str)

    def __init__(self, tax_ids_to_check):
        super().__init__()
        self.tax_ids = [
            re.sub(r'\.0$', '', str(tid).strip())
            for tid in tax_ids_to_check
            if str(tid).strip() and str(tid).strip().lower() not in ['nan', 'none']
        ]
        self.is_cancelled = False

        self.CHUNK_SIZE = 1000
        self.TEMP_DIR = r"C:\Temp"
        self.BPKIN_LIST = [
            "0100", "0110", "0300", "0310", "0400", "0410", "0420", "0430",
            "0440", "0450", "0500", "0700", "0800", "0900", "1000", "1001",
            "3100", "3110", "9100", "9110"
        ]

    @staticmethod
    def _trich_xuat_ma_trang_thai(row, tt_name: str) -> str:
        """
        Trích xuất Mã trạng thái TMS chuẩn (00, 01, 02, 03, 04, 05, 06, 07):
        1. Bóc tách 2 chữ số đầu nếu nằm trong chuỗi tt_name (VD: '00 - NNT đang hoạt động').
        2. Kiểm tra cột liền kề (row[43]) nếu SAP xuất tách riêng cột Mã và Tên trạng thái.
        3. Nội suy từ nội dung chữ tiếng Việt của tt_name để bộ lọc MaTrangThai luôn chính xác.
        """
        if tt_name:
            m = re.match(r'^(\d{2})\b', tt_name.strip())
            if m:
                return m.group(1)

        if len(row) > 43:
            col_43 = str(row[43]).strip()
            if re.match(r'^\d{2}$', col_43):
                return col_43

        tt_lower = (tt_name or "").lower()
        if any(k in tt_lower for k in ["không hoạt động tại địa chỉ", "bỏ địa chỉ", "chờ xác minh"]):
            return "06"
        if any(k in tt_lower for k in ["tạm nghỉ", "tạm ngừng"]):
            return "05"
        if "ngừng hoạt động nhưng chưa hoàn thành" in tt_lower:
            return "03"
        if any(k in tt_lower for k in ["ngừng hoạt động", "đã chấm dứt", "chấm dứt hiệu lực"]):
            return "01"
        if "đang hoạt động" in tt_lower:
            if "tạm" in tt_lower or "gcn" in tt_lower:
                return "04"
            return "00"
        return ""

    def click_sap_button(self, session, relative_id, max_retries=10):
        for _ in range(max_retries):
            if self.is_cancelled:
                return False
            try:
                btn = session.findById(relative_id)
                btn.press()
                return True
            except Exception:
                time.sleep(0.5)
        raise Exception(f"Timeout: Không thể click ID: {relative_id}")

    def parse_sap_xml(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}
        all_rows = []

        for row in root.findall('.//ss:Worksheet[1]/ss:Table/ss:Row', ns):
            row_data = []
            for cell in row.findall('ss:Cell', ns):
                index_attr = cell.get('{urn:schemas-microsoft-com:office:spreadsheet}Index')
                if index_attr:
                    target_idx = int(index_attr) - 1
                    while len(row_data) < target_idx:
                        row_data.append("")

                data_tag = cell.find('ss:Data', ns)
                if data_tag is not None and data_tag.text is not None:
                    row_data.append(data_tag.text.strip())
                else:
                    row_data.append("")

            if any(row_data):
                all_rows.append(row_data)

        if not all_rows:
            return pd.DataFrame()

        max_cols = max(len(row) for row in all_rows)
        padded_rows = [row + [""] * (max_cols - len(row)) for row in all_rows]
        return pd.DataFrame(padded_rows)

    def run_check(self):
        pythoncom.CoInitialize()
        all_results_df = []
        session = None

        if not os.path.exists(self.TEMP_DIR):
            os.makedirs(self.TEMP_DIR)

        try:
            try:
                SapGuiAuto = win32com.client.GetObject("SAPGUI")
                application = SapGuiAuto.GetScriptingEngine
                session = application.Children(0).Children(0)
            except Exception:
                self.error.emit("Không tìm thấy SAP. Vui lòng đăng nhập SAP trước.")
                return []

            total_mst = len(self.tax_ids)
            if total_mst == 0:
                self.finished.emit([])
                return []

            total_chunks = (total_mst // self.CHUNK_SIZE) + (1 if total_mst % self.CHUNK_SIZE != 0 else 0)

            for i in range(total_chunks):
                if self.is_cancelled:
                    break

                chunk_mst = self.tax_ids[i * self.CHUNK_SIZE: (i + 1) * self.CHUNK_SIZE]
                self.progress.emit(i + 1, f"Đang tra cứu lô {i + 1}/{total_chunks} ({len(chunk_mst)} MST)...")

                try:
                    session.findById("wnd[0]/tbar[0]/okcd").text = "/nZTC_RPT_BP"
                    session.findById("wnd[0]").sendVKey(0)
                    time.sleep(1.5)
                    session.findById("wnd[0]/usr/ctxtS_BUKRS-LOW").text = "*"

                    pyperclip.copy("\r\n".join(chunk_mst))
                    time.sleep(0.3)
                    self.click_sap_button(session, "wnd[0]/usr/btn%_S_IDNUM_%_APP_%-VALU_PUSH")
                    time.sleep(0.5)
                    session.findById("wnd[1]/tbar[0]/btn[24]").press()
                    session.findById("wnd[1]/tbar[0]/btn[8]").press()

                    pyperclip.copy("\r\n".join(self.BPKIN_LIST))
                    time.sleep(0.3)
                    self.click_sap_button(session, "wnd[0]/usr/btn%_S_BPKIN_%_APP_%-VALU_PUSH")
                    time.sleep(0.5)
                    session.findById("wnd[1]/tbar[0]/btn[24]").press()
                    session.findById("wnd[1]/tbar[0]/btn[8]").press()

                    today_str = datetime.now().strftime("%d.%m.%Y")
                    session.findById("wnd[0]/usr/ctxtS_CRDAT-LOW").text = "01.01.1999"
                    session.findById("wnd[0]/usr/ctxtS_CRDAT-HIGH").text = today_str
                    session.findById("wnd[0]/tbar[1]/btn[27]").press()
                    time.sleep(1.5)

                    file_name = f"MST_Chunk_{i + 1}.xls"
                    file_path = os.path.join(self.TEMP_DIR, file_name)

                    if os.path.exists(file_path):
                        os.remove(file_path)

                    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = file_name
                    try:
                        session.findById("wnd[1]/usr/ctxtDY_PATH").text = self.TEMP_DIR
                    except Exception:
                        pass

                    session.findById("wnd[1]/tbar[0]/btn[0]").press()

                    wait_time = 0
                    while not os.path.exists(file_path) and wait_time < 20:
                        if self.is_cancelled:
                            break
                        time.sleep(1)
                        wait_time += 1

                    if os.path.exists(file_path):
                        # Chờ SAP nhả file ra (đã ghi xong)
                        time.sleep(1.5)

                        df = self.parse_sap_xml(file_path)
                        if not df.empty:
                            all_results_df.append(df)
                        os.remove(file_path)
                    else:
                        print(f"Lô {i + 1}: Không tạo được file báo cáo từ SAP.")

                except Exception as step_err:
                    print(f"Lỗi thao tác SAP lô {i + 1}: {step_err}")

            # =====================================================================
            # [VÁ LỖI THỤT LỀ]: ĐƯA KHỐI TỔNG HỢP RA NGOÀI VÒNG LẶP CHUNK
            # Đảm bảo quét đủ tất cả các lô khi danh sách > 1.000 MST
            # =====================================================================
            final_results = []
            if all_results_df and not self.is_cancelled:
                self.progress.emit(total_chunks, "Đang xử lý và làm sạch dữ liệu...")
                master_df = pd.concat(all_results_df, ignore_index=True)

                for index, row in master_df.iterrows():
                    if len(row) < 54:
                        continue

                    try:
                        # 1. Làm sạch khoảng trắng thừa
                        raw_mst = str(row[3]).strip().replace(" ", "")

                        # 2. Nắn định dạng về chuẩn có gạch ngang (XXXXXXXXXX-XXX)
                        if len(raw_mst) == 13 and raw_mst.isdigit():
                            clean_mst = f"{raw_mst[:10]}-{raw_mst[10:]}"
                        elif len(raw_mst) == 12 and raw_mst.isdigit():  # Thiếu số 0 ở đầu
                            clean_mst = f"0{raw_mst[:9]}-{raw_mst[9:]}"
                        else:
                            clean_mst = raw_mst

                        # 3. Validate định dạng MST (10 hoặc 13 chữ số)
                        mst_check = clean_mst.replace("-", "")
                        if len(mst_check) not in [10, 13] or not mst_check.isdigit():
                            continue

                        ten_nnt = str(row[4]).strip()
                        cqt = str(row[1]).strip()

                        # Lấy Tên trạng thái tại tọa độ 44 và trích xuất Mã trạng thái chuẩn
                        tt_name = str(row[44]).strip()
                        tt_code = self._trich_xuat_ma_trang_thai(row, tt_name)
                        ngay = str(row[53]).strip()

                        final_results.append((clean_mst, ten_nnt, cqt, tt_code, tt_name, ngay))
                        print(
                            f"👉 CHUẨN BỊ GỬI UI -> MST: {clean_mst} | MÃ TT: '{tt_code}' | TT_NAME: '{tt_name}'"
                        )

                    except Exception as e:
                        print(f"Lỗi dòng {index}: {e}")

            self.finished.emit(final_results)
            return final_results
        except Exception as e:
            self.error.emit(f"Lỗi hệ thống SAP Worker: {e}")
            return []
        finally:
            pythoncom.CoUninitialize()