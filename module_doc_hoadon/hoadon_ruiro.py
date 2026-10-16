# core/hoadon_ruiro.py
import pandas as pd
import json
import os
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
            except:
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
                except:
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

    # =========================================================================
    # CHỨC NĂNG 2: ĐỐI CHIẾU VỚI BẢNG KÊ 01-1/HT (Phục vụ Worker)
    # =========================================================================
    def check_bang_ke_01_1(self, df_bang_ke: pd.DataFrame) -> tuple[pd.DataFrame, list]:
        warnings = []
        if df_bang_ke is None or df_bang_ke.empty:
            return df_bang_ke, warnings

        # 1. Khởi tạo cột mới với giá trị mặc định là Sạch
        col_name = 'Đối chiếu HĐ rủi ro'
        if col_name not in df_bang_ke.columns:
            df_bang_ke[col_name] = "Không thuộc DS HĐ rủi ro"
        mst_col = next((c for c in df_bang_ke.columns if 'MST' in str(c).upper() or 'MÃ SỐ THUẾ' in str(c).upper()),
                       None)
        if not mst_col:
            warnings.append("⏳ BẢNG KÊ 01-1: Không tìm thấy cột Mã số thuế người bán để đối chiếu rủi ro.")
            return df_bang_ke, warnings

        loi_count = 0
        for idx, row in df_bang_ke.iterrows():
            mst_raw = row[mst_col]
            # =================================================================
            # KHẮC PHỤC LỖI AMBIGUOUS DO TRÙNG TÊN CỘT TRÊN RAM
            # =================================================================
            if isinstance(mst_raw, pd.Series):
                mst_raw = mst_raw.iloc[0]
                # =================================================================
            if pd.isna(mst_raw): continue

            # Quét vào RAM O(1)
            mst = str(mst_raw).strip()
            if mst in self.risk_data_cache:
                loi_count += 1
                risk_info = self.risk_data_cache[mst]

                # 2. Gán kết quả nếu phát hiện rủi ro
                df_bang_ke.at[idx, col_name] = "Thuộc DS hóa đơn rủi ro"
                df_bang_ke.at[idx, 'Row_Color'] = "red"
                df_bang_ke.at[idx, 'Tổng hợp cảnh báo'] = "❌ NẰM TRONG DANH MỤC RỦI RO"

                # 3. Ghi Log để bắn lên Bảng Ma Trận
                ky_hieu = str(row.get('Ký hiệu', ''))
                so_hd = str(row.get('Số', ''))
                ngay_hd = str(row.get('Ngày, tháng, năm', ''))

                warnings.append(
                    f"❌ RỦI RO HÓA ĐƠN ({ky_hieu} - {so_hd} | Ngày {ngay_hd}): Mua của MST {mst}. "
                    f"Dấu hiệu: {risk_info.get('Dau_hieu', '')}. Văn bản: {risk_info.get('Noi_dung', '')}"
                )

        if loi_count == 0:
            warnings.append(
                "✅ KIỂM TRA MST RỦI RO: 100% hóa đơn đầu vào trên Bảng kê 01-1/HT không mua của doanh nghiệp nằm trong Danh sách cảnh báo.")

        return df_bang_ke, warnings