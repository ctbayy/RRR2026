# module_doc_hoadon/doc_hoa_don_excel.py

import pandas as pd
import numpy as np
from module_doc_hoadon.tu_dien_hoa_don import MAU_HOA_DON


def doc_file_hoa_don(duong_dan_file):
    """
    Đọc file Excel hóa đơn bằng 100% Pandas DataFrame.
    Tự động chuẩn hóa kiểu số (Float) và parse Ngày/Tháng/Quý/Năm để phục vụ gom nhóm đa kỳ.
    """
    try:
        xls = pd.ExcelFile(duong_dan_file)
        df_raw = None
        cac_cot_chuan = None
        header_idx = -1

        # 1. Quét tìm Sheet chứa bảng kê và nhận diện Mẫu (Giữ nguyên logic cực hay của mày)
        max_matched_cols = 0
        for sheet_name in xls.sheet_names:
            df_temp = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            for i in range(min(20, len(df_temp))):
                row_str = [str(val).strip() for val in df_temp.iloc[i].values if pd.notna(val)]
                for ten_mau, danh_sach_cot in MAU_HOA_DON.items():
                    matched = sum(1 for cot in danh_sach_cot if cot in row_str)
                    if matched > 5 and matched > max_matched_cols:
                        max_matched_cols = matched
                        df_raw = df_temp
                        cac_cot_chuan = danh_sach_cot
                        header_idx = i

        if df_raw is None or cac_cot_chuan is None:
            print("Không tìm thấy cấu trúc bảng hóa đơn hợp lệ trong file này.")
            return None

        # 2. Cắt cúp DataFrame và đặt lại Header
        headers_thuc_te = [str(val).strip() for val in df_raw.iloc[header_idx].values]
        df = df_raw.iloc[header_idx + 1:].copy()
        df.columns = headers_thuc_te

        # Chỉ giữ lại những cột có trong danh sách chuẩn (Lọc rác)
        cot_giao_nhau = [cot for cot in cac_cot_chuan if cot in df.columns]
        df = df[cot_giao_nhau].copy()
        df = df.dropna(how='all')

        # 3. Lọc bỏ các dòng rác (Tổng cộng, Ký tên...) bằng Vector hóa
        col_so_hd = next((c for c in ["Số hóa đơn", "SoHoaDon", "Số HĐ"] if c in df.columns), None)
        col_ten_hh = next((c for c in ["Tên hàng hóa-dịch vụ", "Tên hàng hóa/dịch vụ", "TenNguoiBan",
                                       "Tên người mua/Tên người nhận hàng"] if c in df.columns), None)

        mask_valid = pd.Series(True, index=df.index)
        if col_so_hd and col_ten_hh:
            mask_valid = df[col_so_hd].notna() | df[col_ten_hh].notna()
        df = df[mask_valid]

        # 4. CHUẨN HÓA DỮ LIỆU ĐỒNG LOẠT (Tốc độ tính bằng mili-giây)
        for cot in df.columns:
            # A. Chuẩn hóa Cột Tiền (Ép về định dạng số Float để sum không bị lỗi)
            if any(tu_khoa in cot.lower() for tu_khoa in ["tiền", "thuế", "đơn giá", "số lượng", "tỷ giá"]):
                df[cot] = pd.to_numeric(df[cot].astype(str).str.replace(',', '').str.replace(' ', ''),
                                        errors='coerce').fillna(0)

            # B. Chuẩn hóa Cột Ngày tháng & Tạo Cột Gom Nhóm
            elif cot in ["Ngày lập hóa đơn", "NgayLap", "Ngày lập", "Ngày hóa đơn"]:
                # Parse ngày tháng chuẩn VN (dayfirst=True)
                df['_Ngay_Parse'] = pd.to_datetime(df[cot], dayfirst=True, errors='coerce')

                # Tự động sinh ra 3 cột cực kỳ lợi hại để Engine đối chiếu
                df['_Thang'] = df['_Ngay_Parse'].dt.strftime('%m/%Y')  # VD: 01/2025
                df['_Quy'] = 'Q' + df['_Ngay_Parse'].dt.quarter.astype(str) + '/' + df['_Ngay_Parse'].dt.year.astype(
                    str)  # VD: Q1/2025
                df['_Nam'] = df['_Ngay_Parse'].dt.year.astype(str).str.replace('.0', '')  # VD: 2025

                # Format lại cột gốc cho đẹp để xuất Excel
                df[cot] = df['_Ngay_Parse'].dt.strftime("%d/%m/%Y").fillna("")

        # Trả về nguyên cái DataFrame khỏe khoắn này cho phần mềm!
        return df

    except Exception as e:
        print(f"Lỗi phân tích hóa đơn: {e}")
        return None