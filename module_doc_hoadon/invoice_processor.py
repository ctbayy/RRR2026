import os
import re
import json
import logging
import pandas as pd
import xml.etree.ElementTree as ET


class InvoiceProcessor:
    # Từ khóa nhận diện Hóa đơn rác (Không còn giá trị tính thuế/doanh thu/tồn kho)
    GARBAGE_KEYWORDS = [
        'xóa bỏ', 'hủy bỏ', 'hủy', 'bị xóa bỏ', 'bị hủy', 'bị thay thế',
        'xoa bo', 'huy bo', 'bi xoa bo', 'bi huy', 'bi thay the'
    ]

    # Từ khóa nhận diện Hóa đơn có trạng thái/tính chất đặc biệt (Cần theo dõi & đối chiếu)
    SPECIAL_STATUS_KEYWORDS = [
        'thay thế', 'điều chỉnh', 'bị điều chỉnh', 'chiết khấu', 'trả lại',
        'thay the', 'dieu chinh', 'bi dieu chinh', 'chiet khau', 'tra lai'
    ]

    # Từ khóa nhận diện Hóa đơn điều chỉnh giảm (Cần đảm bảo giá trị âm khi cộng dồn)
    DECREASE_ADJUST_KEYWORDS = [
        'điều chỉnh giảm', 'dieu chinh giam', 'giảm giá', 'giam gia', 'hàng trả lại', 'trả lại hàng'
    ]

    def __init__(self):
        self.summary_data = {}
        self.special_invoices_df = pd.DataFrame()
        self.abnormal_tax_df = pd.DataFrame()
        self.error_messages = []
        self.logger = logging.getLogger("InvoiceProcessor")

    @staticmethod
    def _safe_numeric_convert(val):
        if pd.isna(val) or val == '':
            return 0.0
        s = str(val).strip()
        if not s:
            return 0.0
        s = re.sub(r'[^\d.,-]', '', s)
        if s.count(',') > 1:
            s = s.replace(',', '')
        elif ',' in s and '.' in s:
            if s.rfind(',') > s.rfind('.'):
                s = s.replace('.', '').replace(',', '.')
            else:
                s = s.replace(',', '')
        elif ',' in s:
            parts = s.split(',')
            if len(parts[-1]) == 3:
                s = s.replace(',', '')
            else:
                s = s.replace(',', '.')
        elif '.' in s and s.count('.') > 1:
            s = s.replace('.', '')
        try:
            return float(s)
        except Exception:
            return 0.0

    def _apply_custom_symbol_logic(self, df):
        if df is None or df.empty:
            return df
        required_cols = [
            'Mã số thuế người bán', 'Tên người bán', 'Ký hiệu HD', 'Số HĐ',
            'Ngày lập', 'STT', 'Tên hàng hóa/dịch vụ', 'Đơn vị tính',
            'Số lượng', 'Đơn giá', 'Số tiền chiết khấu', ' Thành tiền',
            'Thuế suất GTGT(%)', 'Tính chất', 'Trạng thái hóa đơn',
            'Ký hiệu HĐ gốc ', 'Số HĐ gốc', 'Ngày lập HĐ gốc',
            'MST người mua', 'Tên người mua', 'Đơn vị CCGP'
        ]
        if len(df.columns) == len(required_cols) and set(df.columns) == set(required_cols):
            thue_suat = df['Thuế suất GTGT(%)'].fillna('').astype(str).str.strip().str.lower()
            ky_hieu = df['Ký hiệu HD'].fillna('').astype(str).str.strip()
            is_empty_tax = thue_suat.isin(['', 'nan', 'none', 'null'])
            mask_starts_with_alpha = ky_hieu.str.match(r'^[a-zA-Z]', na=False)
            df.loc[is_empty_tax & mask_starts_with_alpha, 'Ký hiệu HD'] = '2' + ky_hieu
            df.loc[(~is_empty_tax) & mask_starts_with_alpha, 'Ký hiệu HD'] = '1' + ky_hieu
        return df

    def _load_invoice_mapping(self, json_path, sheet_name="Hoadon"):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                all_maps = json.load(f)
        except Exception as e:
            raise FileNotFoundError(f"Lỗi đọc file JSON Map: {e}")
        config_list = all_maps.get(sheet_name, [])
        ordered_columns, dtype_map, mapping_dict_lower = [], {}, {}
        for item in config_list:
            std_name = item.get("Standard_Column_Name")
            if not std_name:
                continue
            ordered_columns.append(std_name)
            dtype_map[std_name] = item.get("Data_Type", "text")
            for src in item.get("Source_Column_Names", []):
                if src:
                    mapping_dict_lower[str(src).strip().lower()] = std_name
        return mapping_dict_lower, ordered_columns, dtype_map

    def _process_and_standardize_df(self, df, mapping_config):
        mapping_dict_lower, ordered_columns, dtype_map = mapping_config
        df.columns = df.columns.astype(str).str.strip()
        rename_dict = {
            col: mapping_dict_lower.get(col.lower(), col)
            for col in df.columns if col.lower() in mapping_dict_lower
        }
        df.rename(columns=rename_dict, inplace=True)
        std_cols = [col for col in ordered_columns if col in df.columns]
        if not std_cols:
            return None

        std_df = df[std_cols].copy()
        for col, dtype in dtype_map.items():
            if col in std_df.columns:
                if dtype == 'numeric':
                    # [VÁ LỖI 1]: Bắt buộc ép kiểu float để hàm sum() hoạt động
                    std_df[col] = std_df[col].apply(self._safe_numeric_convert).astype(float)
                elif 'MST' in str(col):
                    std_df[col] = std_df[col].fillna('').astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
                elif dtype == 'datetime':
                    # --- [VÁ LỖI 2]: LUỒNG XỬ LÝ NGÀY THÁNG THÔNG MINH ---
                    s = std_df[col].fillna('').astype(str).replace('nan', '')
                    s = s.str.split(' ').str[0].str.strip()
                    mask_iso = s.str.match(r'^\d{4}[-/]', na=False)
                    parsed_dates = pd.Series(pd.NaT, index=s.index)

                    if mask_iso.any():
                        parsed_dates[mask_iso] = pd.to_datetime(s[mask_iso], errors='coerce')
                    if (~mask_iso).any():
                        parsed_dates[~mask_iso] = pd.to_datetime(s[~mask_iso], dayfirst=True, errors='coerce')

                    std_df[col] = parsed_dates.dt.strftime('%d/%m/%Y').fillna('')

        for col in ordered_columns:
            if col not in std_df.columns:
                std_df[col] = 0.0 if dtype_map.get(col) == 'numeric' else ""

        if 'NgayLap' in std_df.columns:
            dt_parse = pd.to_datetime(std_df['NgayLap'], format='%d/%m/%Y', errors='coerce')
            std_df['_Thang'] = dt_parse.dt.strftime('%m/%Y')
            std_df['_Quy'] = 'Q' + dt_parse.dt.quarter.astype(str) + '/' + dt_parse.dt.year.astype(str).str.replace('.0', '')
            std_df['_Nam'] = dt_parse.dt.year.astype(str).str.replace('.0', '')
        return std_df

    @classmethod
    def _lay_chuoi_trang_thai_ket_hop(cls, df: pd.DataFrame) -> pd.Series:
        """Gộp nội dung cột Trạng thái hóa đơn và Tính chất để nhận diện không sót trường hợp đặc biệt."""
        combined = pd.Series("", index=df.index, dtype=str)
        for col in df.columns:
            col_lower = str(col).lower().replace(" ", "").replace("_", "")
            if any(k in col_lower for k in ["trạngthái", "trangthai", "tínhchất", "tinhchat"]):
                s_col = df[col].fillna('').astype(str).str.lower().str.strip()
                combined = combined + " | " + s_col
        return combined

    def _normalize_financial_data(self, df):
        core_cols = ['ThanhTien', 'TongTienChuaThue', 'TongTienThue', 'TongTienThanhToan', 'ThueSuat']
        for col in core_cols:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        mask_has_tong_chua_thue = (df['TongTienChuaThue'] != 0) & (df['ThanhTien'] == 0)
        df.loc[mask_has_tong_chua_thue, 'ThanhTien'] = df.loc[mask_has_tong_chua_thue, 'TongTienChuaThue']

        mask_has_thanh_tien = (df['ThanhTien'] != 0) & (df['TongTienChuaThue'] == 0)
        df.loc[mask_has_thanh_tien, 'TongTienChuaThue'] = df.loc[mask_has_thanh_tien, 'ThanhTien']

        mask_missing_tax = (df['TongTienThue'] == 0) & (df['ThanhTien'] != 0) & (df['ThueSuat'] > 0)
        rates = df.loc[mask_missing_tax, 'ThueSuat'].copy()
        rates = rates.apply(lambda x: x / 100.0 if x > 1 else x)
        df.loc[mask_missing_tax, 'TongTienThue'] = df.loc[mask_missing_tax, 'ThanhTien'] * rates

        mask_missing_total = (df['TongTienThanhToan'] == 0)
        df.loc[mask_missing_total, 'TongTienThanhToan'] = (
            df.loc[mask_missing_total, 'ThanhTien'] + df.loc[mask_missing_total, 'TongTienThue']
        )

        # [VÁ LỖI NGHIỆP VỤ]: Chuẩn hóa dấu âm (-) cho Hóa đơn điều chỉnh giảm nếu file gốc ghi số dương
        stt_combined = self._lay_chuoi_trang_thai_ket_hop(df)
        if 'TenHangHoa' in df.columns:
            stt_combined = stt_combined + " | " + df['TenHangHoa'].fillna('').astype(str).str.lower()

        mask_giam = stt_combined.str.contains('|'.join(self.DECREASE_ADJUST_KEYWORDS), case=False, na=False)
        if mask_giam.any():
            money_cols = ['ThanhTien', 'TongTienChuaThue', 'TongTienThue', 'TongTienThanhToan']
            for m_col in money_cols:
                if m_col in df.columns:
                    mask_pos = mask_giam & (df[m_col] > 0)
                    df.loc[mask_pos, m_col] = -df.loc[mask_pos, m_col]
            if 'SoLuong' in df.columns:
                df['SoLuong'] = pd.to_numeric(df['SoLuong'], errors='coerce').fillna(0.0)
                mask_sl_pos = mask_giam & (df['SoLuong'] > 0)
                df.loc[mask_sl_pos, 'SoLuong'] = -df.loc[mask_sl_pos, 'SoLuong']

        return df

    def _extract_special_and_abnormal_invoices(self, df):
        """Bóc tách danh sách Hóa đơn có trạng thái đặc biệt và Hóa đơn có thuế suất bất thường."""
        if df is None or df.empty:
            self.special_invoices_df = pd.DataFrame()
            self.abnormal_tax_df = pd.DataFrame()
            return df

        df_out = df.copy()
        stt_combined = self._lay_chuoi_trang_thai_ket_hop(df_out)

        mask_garbage = stt_combined.str.contains('|'.join(self.GARBAGE_KEYWORDS), case=False, na=False)
        mask_special = (~mask_garbage) & stt_combined.str.contains(
            '|'.join(self.SPECIAL_STATUS_KEYWORDS), case=False, na=False
        )

        # Gắn cột Phân loại trạng thái để hiển thị trực quan và phục vụ lọc
        df_out['PhanLoaiTrangThai'] = "Bình thường"
        df_out.loc[mask_special, 'PhanLoaiTrangThai'] = "⚠️ Đặc biệt (Thay thế / Điều chỉnh)"
        df_out.loc[mask_garbage, 'PhanLoaiTrangThai'] = "❌ Loại trừ (Hủy / Xóa bỏ / Bị thay thế)"

        self.special_invoices_df = df_out[mask_garbage | mask_special].copy()

        # Kiểm tra thuế suất bất thường (khác 0%, 5%, 8%, 10%)
        if 'ThueSuat' in df_out.columns:
            ts_num = pd.to_numeric(df_out['ThueSuat'], errors='coerce').fillna(0.0)
            ts_pct = ts_num.apply(lambda x: round(x * 100, 2) if 0 < abs(x) < 1 else round(x, 2))
            mask_abnormal_tax = ~ts_pct.isin([0.0, 5.0, 8.0, 10.0])
            self.abnormal_tax_df = df_out[mask_abnormal_tax].copy()

        return df_out

    def _print_debug_info(self, module_name, df):
        """Hàm Print để nội soi dòng tiền"""
        print(f"\n" + "=" * 50)
        print(f"🔍 DEBUG [{module_name}]")
        print(f"👉 1. Các cột hiện có: {list(df.columns)}")
        if 'ThanhTien' in df.columns:
            tong_tien = df['ThanhTien'].sum()
            print(f"👉 2. TỔNG CỘNG CỘT [ThanhTien] = {tong_tien:,.0f}")
            print(f"👉 3. TỔNG CỘNG CỘT [TongTienThue] = {df['TongTienThue'].sum():,.0f}")
        else:
            print(f"👉 2. ❌ KHÔNG TÌM THẤY CỘT [ThanhTien]!")
        print("=" * 50 + "\n")

    def _read_file_smart_auto_detect(self, file_path, map_chitiet, map_tonghop):
        """Thuật toán dò quét kép: So sánh điểm số để nhận diện chuẩn xác Mẫu bảng kê (Hỗ trợ quét đa Sheet)"""
        try:
            dict_chitiet = map_chitiet[0]  # mapping_dict_lower của Mẫu Chi Tiết
            dict_tonghop = map_tonghop[0]  # mapping_dict_lower của Mẫu Tổng Hợp

            best_score_chitiet = 0
            header_idx_chitiet = 0
            best_df_chitiet = None

            best_score_tonghop = 0
            header_idx_tonghop = 0
            best_df_tonghop = None

            def _cham_diem(df_temp):
                nonlocal best_score_chitiet, header_idx_chitiet, best_df_chitiet
                nonlocal best_score_tonghop, header_idx_tonghop, best_df_tonghop

                if df_temp is None or df_temp.empty:
                    return

                for i in range(min(20, len(df_temp))):
                    row_vals = [str(v).strip().lower() for v in df_temp.iloc[i].values if pd.notna(v)]

                    score_ct = sum(1 for val in row_vals if val in dict_chitiet)
                    if score_ct > best_score_chitiet:
                        best_score_chitiet = score_ct
                        header_idx_chitiet = i
                        best_df_chitiet = df_temp

                    score_th = sum(1 for val in row_vals if val in dict_tonghop)
                    if score_th > best_score_tonghop:
                        best_score_tonghop = score_th
                        header_idx_tonghop = i
                        best_df_tonghop = df_temp

            # 1. ĐỌC VÀ CHẤM ĐIỂM NẾU LÀ FILE CSV
            if file_path.lower().endswith('.csv'):
                for enc in ['utf-8', 'utf-8-sig', 'cp1252', 'latin1']:
                    try:
                        df_csv = pd.read_csv(
                            file_path, encoding=enc, sep=',', header=None, dtype=str, on_bad_lines='skip'
                        )
                        if len(df_csv.columns) > 1:
                            _cham_diem(df_csv)
                            break
                    except Exception:
                        continue

            # 2. ĐỌC VÀ CHẤM ĐIỂM NẾU LÀ FILE EXCEL (QUÉT TẤT CẢ CÁC SHEET)
            elif file_path.lower().endswith(('.xlsx', '.xls')):
                loai_dong_co = 'xlrd' if file_path.lower().endswith('.xls') else 'openpyxl'
                xls = pd.ExcelFile(file_path, engine=loai_dong_co)

                for sheet_name in xls.sheet_names:
                    df_sheet = pd.read_excel(xls, sheet_name=sheet_name, header=None, dtype=str)
                    _cham_diem(df_sheet)

            # 3. LUẬN KIẾM: So sánh điểm để quyết định dùng Sheet và Mẫu nào
            if best_score_chitiet < 3 and best_score_tonghop < 3:
                self.logger.warning(f"Không tìm thấy cấu trúc bảng trong: {file_path}")
                return None

            if best_score_tonghop > best_score_chitiet:
                best_idx = header_idx_tonghop
                best_map_config = map_tonghop
                map_name = "TỔNG HỢP (Hoadon)"
                df_raw = best_df_tonghop
            else:
                best_idx = header_idx_chitiet
                best_map_config = map_chitiet
                map_name = "CHI TIẾT (Hoadon_Chitiet)"
                df_raw = best_df_chitiet

            # 4. Cắt cúp DataFrame dựa trên dòng Header chiến thắng
            df = df_raw.iloc[best_idx + 1:].copy()
            df.columns = [str(v).strip() for v in df_raw.iloc[best_idx].values]

            df = self._apply_custom_symbol_logic(df)

            return df, best_map_config, map_name

        except Exception as e:
            self.error_messages.append(f"Lỗi quét thông minh: {e}")
            return None

    def process_excel_csv_invoices(self, file_path, json_path, is_mua_vao=False):
        """Hàm công khai xử lý Hóa đơn - Tự động nhận diện Form"""
        sheet_chitiet = "Hoadon_Muavao_Chitiet" if is_mua_vao else "Hoadon_Chitiet"
        sheet_tonghop = "Hoadon"

        try:
            map_chitiet = self._load_invoice_mapping(json_path, sheet_chitiet)
            map_tonghop = self._load_invoice_mapping(json_path, sheet_tonghop)
        except Exception as e:
            self.logger.error(f"Lỗi tải file Map JSON: {e}")
            return None

        result = self._read_file_smart_auto_detect(file_path, map_chitiet, map_tonghop)
        if not result:
            return None

        df_raw, best_mapping_config, map_name = result

        df_std = self._process_and_standardize_df(df_raw, best_mapping_config)
        if df_std is None:
            return None

        df_std = self._normalize_financial_data(df_std)
        df_std = self._extract_special_and_abnormal_invoices(df_std)

        print(f"\n✅ ĐÃ TỰ ĐỘNG NHẬN DIỆN MẪU BẢNG KÊ: {map_name}")
        self._print_debug_info(f"EXCEL/CSV - {os.path.basename(file_path)}", df_std)

        return df_std

    @classmethod
    def loc_hoa_don_trang_thai_dac_biet(cls, df: pd.DataFrame, loai_hd: str = "") -> pd.DataFrame:
        """
        Trích xuất danh sách các Hóa đơn có trạng thái / tính chất đặc biệt:
        - Hóa đơn Xóa bỏ / Hủy / Bị thay thế (Đã loại khỏi tính toán)
        - Hóa đơn Thay thế / Điều chỉnh / Bị điều chỉnh (Cần rà soát cặp hóa đơn gốc - điều chỉnh/thay thế)
        """
        if df is None or isinstance(df, dict) or not isinstance(df, pd.DataFrame) or df.empty:
            return pd.DataFrame()

        df_check = df.copy()
        stt_combined = cls._lay_chuoi_trang_thai_ket_hop(df_check)

        mask_garbage = stt_combined.str.contains('|'.join(cls.GARBAGE_KEYWORDS), case=False, na=False)
        mask_special = (~mask_garbage) & stt_combined.str.contains(
            '|'.join(cls.SPECIAL_STATUS_KEYWORDS), case=False, na=False
        )

        mask_all_special = mask_garbage | mask_special
        if not mask_all_special.any():
            return pd.DataFrame()

        df_res = df_check[mask_all_special].copy()
        if loai_hd:
            df_res.insert(0, 'Phân hệ HĐ', loai_hd)

        df_res['Nhóm Trạng Thái Đặc Biệt'] = ""
        df_res.loc[mask_special, 'Nhóm Trạng Thái Đặc Biệt'] = "⚠️ Thay thế / Điều chỉnh (Cần đối chiếu HĐ gốc)"
        df_res.loc[mask_garbage, 'Nhóm Trạng Thái Đặc Biệt'] = "❌ Hủy / Xóa bỏ / Bị thay thế (Đã loại khi tính tổng)"

        return df_res

    @classmethod
    def loc_hoa_don_tinh_toan(cls, df):
        """
        [HÀM DÀNH RIÊNG CHO ENGINE TÍNH TOÁN, ĐỐI CHIẾU DOANH SỐ & TỒN KHO]
        1. Lọc bỏ hóa đơn rác (Hủy, Xóa bỏ, Bị xóa bỏ, Bị thay thế) trên cả cột Trạng thái và Tính chất.
        2. Đảm bảo hóa đơn điều chỉnh giảm mang dấu âm (-) trước khi cộng dồn số liệu.
        """
        if df is None or isinstance(df, dict) or (isinstance(df, pd.DataFrame) and df.empty):
            return df

        df_calc = df.copy()

        # 1. Quét trên cả cột Trạng thái hóa đơn và Tính chất
        stt_combined = cls._lay_chuoi_trang_thai_ket_hop(df_calc)

        # Tạo mặt nạ lọc rác
        mask_garbage = stt_combined.str.contains('|'.join(cls.GARBAGE_KEYWORDS), case=False, na=False)
        df_calc = df_calc[~mask_garbage].copy()

        if df_calc.empty:
            return df_calc

        # 2. Đảm bảo các dòng điều chỉnh giảm mang giá trị âm khi tính tổng
        stt_valid = cls._lay_chuoi_trang_thai_ket_hop(df_calc)
        if 'TenHangHoa' in df_calc.columns:
            stt_valid = stt_valid + " | " + df_calc['TenHangHoa'].fillna('').astype(str).str.lower()

        mask_giam = stt_valid.str.contains('|'.join(cls.DECREASE_ADJUST_KEYWORDS), case=False, na=False)
        if mask_giam.any():
            for m_col in ['ThanhTien', 'TongTienChuaThue', 'TongTienThue', 'TongTienThanhToan']:
                if m_col in df_calc.columns:
                    df_calc[m_col] = pd.to_numeric(df_calc[m_col], errors='coerce').fillna(0.0)
                    mask_pos = mask_giam & (df_calc[m_col] > 0)
                    df_calc.loc[mask_pos, m_col] = -df_calc.loc[mask_pos, m_col]
            if 'SoLuong' in df_calc.columns:
                df_calc['SoLuong'] = pd.to_numeric(df_calc['SoLuong'], errors='coerce').fillna(0.0)
                mask_sl_pos = mask_giam & (df_calc['SoLuong'] > 0)
                df_calc.loc[mask_sl_pos, 'SoLuong'] = -df_calc.loc[mask_sl_pos, 'SoLuong']

        return df_calc