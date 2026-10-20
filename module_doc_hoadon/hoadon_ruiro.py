# core/hoadon_ruiro.py
import pandas as pd
import json
import os
import re
import requests
from datetime import datetime


class HoaDonRuiRoManager:
    # Thay firebase_url bằng gas_url (Google Apps Script URL)
    def __init__(self,
                 gas_url="https://script.google.com/macros/s/AKfycbx-DnII54t-msdYcXdLXmSwMjHnARIM6GK0ZQzB58ILBdheJYYJgGvvME_5NTmASPEeeQ/exec"):
        self.gas_url = gas_url

        # 1. Lấy tọa độ thư mục chứa file code này (thư mục 'core')
        core_dir = os.path.dirname(os.path.abspath(__file__))
        # 2. Đi lùi ra 1 cấp để về thư mục gốc của Project
        project_root = os.path.dirname(core_dir)
        # 3. Trỏ thẳng vào thư mục "Data" nằm ở gốc
        data_dir = os.path.join(project_root, "Data")
        os.makedirs(data_dir, exist_ok=True)

        # 4. Chốt hạ đường dẫn file
        self.local_cache_path = os.path.join(data_dir, "risk_cache.json")
        self.risk_data_cache = {}

        self._load_local_cache()
        # Ưu tiên dữ liệu local cache, sync cloud với timeout ngắn để tránh treo UI
        timeout_init = 3 if self.risk_data_cache else 5
        self.sync_from_cloud(timeout=timeout_init)

    def _get_machine_id(self):
        """Trích xuất mã định danh máy tính chuẩn Native Windows (winreg + volume serial)"""
        try:
            from module_bao_mat.device_manager import DeviceManager
            return DeviceManager.get_machine_id()
        except Exception:
            import uuid
            return str(uuid.getnode())

    def _load_local_cache(self):
        if os.path.exists(self.local_cache_path):
            try:
                with open(self.local_cache_path, 'r', encoding='utf-8') as f:
                    self.risk_data_cache = json.load(f)
            except Exception:
                pass

    def _save_local_cache(self):
        with open(self.local_cache_path, 'w', encoding='utf-8') as f:
            json.dump(self.risk_data_cache, f, ensure_ascii=False, indent=2)

    def sync_from_cloud(self, timeout=5):
        """ Kéo dữ liệu mới nhất từ Google Sheets về RAM """
        try:
            # GỌI GET TỚI GOOGLE APPS SCRIPT (ĐÃ BỌC USER-AGENT CHỐNG BOT)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(self.gas_url, headers=headers, allow_redirects=True, timeout=timeout)

            if response.status_code == 200:
                data = response.json()
                if data and "status" not in data:  # Phân biệt với JSON lỗi
                    self.risk_data_cache = data
                    self._save_local_cache()
                    return True, f"Đã đồng bộ {len(self.risk_data_cache)} MST rủi ro từ Cloud."
                return True, "Hệ thống Cloud hiện chưa có dữ liệu rủi ro."
            return False, f"Lỗi HTTP: {response.status_code}"
        except Exception as e:
            return False, f"Lỗi kết nối (Đang chạy Offline Mode): {str(e)}"

    def get_all_data_as_df(self):
        if not self.risk_data_cache:
            return pd.DataFrame(columns=["MST", "Dấu hiệu", "Nội dung", "Cập nhật lần cuối"])

        rows = []
        for mst, info in self.risk_data_cache.items():
            rows.append({
                "MST": mst,
                "Dấu hiệu": info.get("Dau_hieu", ""),
                "Nội dung": info.get("Noi_dung", ""),
                "Cập nhật lần cuối": info.get("Ngay_Cap_Nhat", "")
            })
        df = pd.DataFrame(rows)
        if not df.empty:
            df.sort_values(by="Cập nhật lần cuối", ascending=False, inplace=True)
        return df

    def upload_data_from_template(self, file_path: str):
        try:
            df_upload = pd.read_excel(file_path, dtype=str)
            df_upload.columns = [c.strip() for c in df_upload.columns]

            required_cols = ['MST', 'Dau_hieu', 'Noi_dung']
            missing_cols = [col for col in required_cols if col not in df_upload.columns]
            if missing_cols:
                return False, f"Từ chối cập nhật! Template thiếu các cột: {', '.join(missing_cols)}."

            df_upload['MST'] = df_upload['MST'].astype(str).str.strip()
            df_upload = df_upload[~df_upload['MST'].str.lower().isin(['nan', 'none', ''])]

            if df_upload.empty:
                return False, "Từ chối cập nhật! File Excel không có dữ liệu."

            valid_mask = df_upload['MST'].str.match(r'^\d{10}(-\d{3})?$')
            df_valid = df_upload[valid_mask]
            df_invalid = df_upload[~valid_mask]

            invalid_count = len(df_invalid)
            valid_count = len(df_valid)

            if valid_count == 0:
                return False, f"Từ chối cập nhật! Toàn bộ {invalid_count} Mã số thuế trong file đều sai định dạng."

            current_hwid = self._get_machine_id()
            payload = {}
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for _, row in df_valid.iterrows():
                mst = row['MST']
                payload[mst] = {
                    "Dau_hieu": str(row['Dau_hieu']).strip() if pd.notna(
                        row['Dau_hieu']) else "Cảnh báo rủi ro hóa đơn",
                    "Noi_dung": str(row['Noi_dung']).strip() if pd.notna(row['Noi_dung']) else "",
                    "Ngay_Cap_Nhat": now_str,
                    "NSD": current_hwid
                }

            # GỌI POST TỚI GOOGLE APPS SCRIPT (ĐÃ BỌC USER-AGENT CHỐNG BOT)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.post(self.gas_url, json=payload, headers=headers, allow_redirects=True, timeout=60)

            if response.status_code == 200:
                try:
                    res_data = response.json()
                    if res_data.get("status") != "success":
                        return False, "Google Sheets xử lý thất bại."
                except Exception:
                    pass

                self.sync_from_cloud()

                if invalid_count > 0:
                    msg = f"✅ Cập nhật thành công {valid_count} MST rủi ro lên hệ thống.\n\n⚠️ Đã tự động BỎ QUA {invalid_count} dòng do Mã số thuế sai định dạng."
                    return True, msg
                else:
                    return True, f"✅ Tuyệt vời! Đã cập nhật trọn vẹn {valid_count} MST rủi ro."
            else:
                return False, f"Lỗi máy chủ Cloud (HTTP {response.status_code})."

        except Exception as e:
            return False, f"Lỗi đọc file/kết nối: {str(e)}"

    @staticmethod
    def _tim_cot_mst_nguoi_ban(columns) -> str | None:
        """Ưu tiên dò chính xác cột MST người bán, tránh bắt nhầm MST người mua hoặc MST tổ chức giải pháp."""
        uu_tien = [
            'MSTNguoiBan', 'Mã số thuế người bán', 'MST người bán',
            'MST người bán/MST người xuất hàng', 'MST_NguoiBan'
        ]
        for col_std in uu_tien:
            if col_std in columns:
                return col_std

        tu_khoa_loai_tru = ['MUA', 'GIẢI PHÁP', 'GIAIPHAP', 'TRUYỀN NHẬN', 'TRUYENNHAN', 'CCGP']
        for c in columns:
            c_upper = str(c).upper()
            if ('MST' in c_upper or 'MÃ SỐ THUẾ' in c_upper or 'MA SO THUE' in c_upper):
                if not any(excl in c_upper for excl in tu_khoa_loai_tru):
                    return c

        return next((c for c in columns if 'MST' in str(c).upper() or 'MÃ SỐ THUẾ' in str(c).upper()), None)

    @staticmethod
    def _lay_gia_tri_cot(row, danh_sach_cot_ung_vien, xoa_duoi_thap_phan=False) -> str:
        """Lấy giá trị đầu tiên khác rỗng từ danh sách các tên cột ứng viên (hỗ trợ cả cột chuẩn hóa và cột gốc)."""
        for c in danh_sach_cot_ung_vien:
            if c in row.index:
                val = row[c]
                if isinstance(val, pd.Series):
                    val = val.iloc[0]
                if pd.notna(val):
                    s = str(val).strip()
                    if s and s.lower() not in ['nan', 'none', 'null']:
                        if xoa_duoi_thap_phan:
                            s = re.sub(r'\.0$', '', s)
                        return s
        return ""

    @staticmethod
    def _chuan_hoa_mst(mst_raw) -> str:
        """Làm sạch chuỗi MST, loại bỏ đuôi .0 do Excel ép kiểu số và chuẩn hóa dấu gạch ngang."""
        if pd.isna(mst_raw):
            return ""
        s = re.sub(r'\.0$', '', str(mst_raw).strip()).replace(" ", "")
        if s.lower() in ['nan', 'none', '']:
            return ""
        if len(s) == 13 and s.isdigit():
            return f"{s[:10]}-{s[10:]}"
        if len(s) == 9 and s.isdigit():
            return f"0{s}"
        return s

    # =========================================================================
    # CHỨC NĂNG 2: ĐỐI CHIẾU VỚI BẢNG KÊ 01-1/HT & HÓA ĐƠN MUA VÀO (Phục vụ Worker)
    # =========================================================================
    def check_bang_ke_01_1(self, df_bang_ke: pd.DataFrame) -> tuple[pd.DataFrame, list]:
        warnings = []
        if df_bang_ke is None or df_bang_ke.empty:
            return df_bang_ke, warnings

        # 1. Khởi tạo cột mới với giá trị mặc định sạch (không để NaN làm bẩn UI/Excel)
        col_name = 'Đối chiếu HĐ rủi ro'
        df_bang_ke[col_name] = "Không thuộc DS HĐ rủi ro"
        df_bang_ke['Tổng hợp cảnh báo'] = ""
        df_bang_ke['Row_Color'] = ""

        mst_col = self._tim_cot_mst_nguoi_ban(df_bang_ke.columns)
        if not mst_col:
            warnings.append("⏳ BẢNG KÊ / HÓA ĐƠN MUA VÀO: Không tìm thấy cột Mã số thuế người bán để đối chiếu rủi ro.")
            return df_bang_ke, warnings

        cot_ky_hieu = [
            'KyHieu', 'KyHieuHoaDon', 'Ký hiệu HD', 'Ký hiệu hóa đơn',
            'Ký hiệu mẫu số hóa đơn-ký hiệu hóa đơn', 'Ký hiệu'
        ]
        cot_so_hd = ['SoHoaDon', 'Số HĐ', 'Số hóa đơn', 'Số']
        cot_ngay_hd = ['NgayLap', 'Ngày lập', 'Ngày lập hóa đơn', 'Ngày hóa đơn', 'Ngày, tháng, năm']

        loi_count = 0
        for idx, row in df_bang_ke.iterrows():
            mst_raw = row[mst_col]
            if isinstance(mst_raw, pd.Series):
                mst_raw = mst_raw.iloc[0]

            mst = self._chuan_hoa_mst(mst_raw)
            if not mst:
                continue

            # Tra cứu O(1) trên RAM (hỗ trợ khớp cả MST 13 số chi nhánh về MST 10 số công ty mẹ nếu cần)
            mst_goc_10 = mst.split('-')[0] if '-' in mst else mst
            risk_info = self.risk_data_cache.get(mst) or self.risk_data_cache.get(mst_goc_10)

            if risk_info:
                loi_count += 1
                dau_hieu = risk_info.get('Dau_hieu', 'Cảnh báo rủi ro hóa đơn').strip()
                noi_dung = risk_info.get('Noi_dung', '').strip()

                # 2. Gán kết quả nếu phát hiện rủi ro
                df_bang_ke.at[idx, col_name] = "Thuộc DS hóa đơn rủi ro"
                df_bang_ke.at[idx, 'Row_Color'] = "red"
                chi_tiet_cb = f"❌ NẰM TRONG DANH MỤC RỦI RO | Dấu hiệu: {dau_hieu}"
                if noi_dung:
                    chi_tiet_cb += f" ({noi_dung})"
                df_bang_ke.at[idx, 'Tổng hợp cảnh báo'] = chi_tiet_cb

                # 3. Ghi Log chuẩn tên cột đã chuẩn hóa để hiển thị đầy đủ Số HĐ, Ký hiệu, Ngày lập
                ky_hieu = self._lay_gia_tri_cot(row, cot_ky_hieu)
                so_hd = self._lay_gia_tri_cot(row, cot_so_hd, xoa_duoi_thap_phan=True)
                ngay_hd = self._lay_gia_tri_cot(row, cot_ngay_hd)

                warnings.append(
                    f"❌ RỦI RO HÓA ĐƠN ({ky_hieu} - Số {so_hd} | Ngày {ngay_hd}): Mua của MST {mst}. "
                    f"Dấu hiệu: {dau_hieu}. Văn bản: {noi_dung}"
                )

        if loi_count == 0:
            # Nếu 100% hóa đơn sạch, xóa cột kỹ thuật Row_Color để bảng gọn gàng
            df_bang_ke.drop(columns=['Row_Color'], inplace=True, errors='ignore')
            warnings.append(
                "✅ KIỂM TRA MST RỦI RO: 100% hóa đơn đầu vào không mua của doanh nghiệp nằm trong Danh sách cảnh báo."
            )

        return df_bang_ke, warnings