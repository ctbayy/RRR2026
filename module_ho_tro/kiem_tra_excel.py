# module_ho_tro/kiem_tra_excel.py
import re
import pandas as pd
import numpy as np


def _chuan_hoa_so_tien(val):
    """Chuyển đổi chuỗi tiền tệ bất kỳ sang float chuẩn, xử lý số âm trong ngoặc và dấu phân cách"""
    if pd.isna(val) or val is None:
        return 0.0
    s = str(val).strip()
    if s in ["", "-", "nan", "None", "null"]:
        return 0.0
    is_am = False
    if s.startswith("(") and s.endswith(")"):
        is_am = True
        s = s[1:-1].strip()
    s = s.replace(" ", "")
    if "." in s and "," in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s and "." not in s:
        parts = s.split(",")
        if len(parts) == 2 and len(parts[1]) != 3:
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    try:
        num = float(s)
        return -num if is_am else num
    except Exception:
        return 0.0


def _tim_sheet_phu_hop(excel_file):
    """Tìm sheet phù hợp nhất chứa dữ liệu CĐSPS"""
    sheet_names = excel_file.sheet_names
    # 1. Ưu tiên sheet chuẩn template
    for name in sheet_names:
        if name.strip().lower() == "dulieu_cdsps":
            return name

    # 2. Ưu tiên sheet có tên chứa từ khóa kế toán
    uu_tien = ["cdsps", "b04", "can doi", "cân đối", "phat sinh", "phát sinh", "trial balance", "so phat sinh"]
    for kw in uu_tien:
        for name in sheet_names:
            if kw in name.strip().lower():
                return name

    # 3. Lấy sheet đầu tiên không phải sheet hướng dẫn
    for name in sheet_names:
        name_l = name.strip().lower()
        if "huong_dan" not in name_l and "guide" not in name_l and "help" not in name_l:
            return name

    return sheet_names[0]


def _trich_xuat_nam_tai_chinh(df_raw):
    """Tìm năm tài chính trong các dòng đầu tiên của file Excel"""
    for r in range(min(15, len(df_raw))):
        row_str = " ".join([str(x) for x in df_raw.iloc[r].dropna().tolist()])
        # Mẫu: 'Năm 2024', 'Kỳ 2024', 'Year 2024'
        match = re.search(r'(?:năm|kỳ|year)\s*[:\-]?\s*(20[123]\d)', row_str, re.IGNORECASE)
        if match:
            return match.group(1)
        # Mẫu ngày: 31/12/2024
        match_date = re.search(r'\d{1,2}[/\-\.]\d{1,2}[/\-\.](20[123]\d)', row_str)
        if match_date:
            return match_date.group(1)
        # Số năm độc lập 20xx
        match_yr = re.search(r'\b(20[123]\d)\b', row_str)
        if match_yr:
            return match_yr.group(1)
    return None


def kiem_tra_file_upload(file_path, tu_dien_tk=None):
    """
    Đọc và xác thực dữ liệu từ file Excel Bảng Cân đối Số phát sinh (Thông tư 200).
    Tự động nhận diện Sheet, tự động tìm dòng Header, tự động bóc tách Năm tài chính,
    lọc bỏ dòng tổng cộng/chữ ký, chống tính trùng lặp (Anti Double-Counting) giữa tài khoản Mẹ và Con.

    Trả về: (Trạng_thái_Hợp_lệ_Boolean, Danh_sách_Thông_báo_List, Dữ_liệu_Sạch_DataFrame, Năm_Phát_Hiện_Str)
    """
    try:
        excel_file = pd.ExcelFile(file_path)
    except Exception as e:
        return False, [f"❌ LỖI ĐỌC FILE: Không thể mở file Excel ({str(e)})"], None, None

    sheet_chon = _tim_sheet_phu_hop(excel_file)
    try:
        df_raw = excel_file.parse(sheet_chon, header=None, dtype=str)
    except Exception as e:
        return False, [f"❌ LỖI ĐỌC SHEET '{sheet_chon}': {str(e)}"], None, None

    if df_raw.empty or len(df_raw) < 2:
        return False, [f"❌ LỖI: Sheet '{sheet_chon}' không có đủ dữ liệu!"], None, None

    # 1. Trích xuất năm tài chính nếu có
    nam_phat_hien = _trich_xuat_nam_tai_chinh(df_raw)

    # 2. Tìm vị trí dòng Header và cột Mã TK
    header_row = -1
    col_matk = 0
    kws_matk = ['mã tk', 'số hiệu', 'so hieu', 'mã số', 'tài khoản', 'tai khoan', 'matk', 'sh tk', 'số tk', 'so tk']

    for r in range(min(25, len(df_raw))):
        row_vals = [str(x).strip().lower() for x in df_raw.iloc[r]]
        for idx, val in enumerate(row_vals):
            if any(k == val or k in val for k in kws_matk):
                header_row = r
                col_matk = idx
                break
        if header_row != -1:
            break

    if header_row == -1:
        header_row = 1 if len(df_raw) > 1 else 0
        col_matk = 0

    col_tentk = col_matk + 1

    # Kiểm tra xem dòng tiếp theo có phải là sub-header (ví dụ dòng Nợ, Có) hay đã là dữ liệu tài khoản
    data_start = header_row + 1
    if data_start < len(df_raw):
        next_cell = str(df_raw.iloc[data_start, col_matk]).strip()
        if next_cell.endswith('.0') and next_cell[:-2].isdigit():
            next_cell = next_cell[:-2]
        if not re.match(r'^[0-9]{3,6}$', next_cell):
            data_start += 1

    # Kiểm tra số lượng cột
    tong_so_cot = df_raw.shape[1]
    if tong_so_cot < col_matk + 8:
        return False, [
            f"❌ LỖI CẤU TRÚC: Sheet '{sheet_chon}' chỉ có {tong_so_cot} cột, "
            f"không đủ 8 cột chuẩn của Bảng CĐSPS (Mã TK, Tên TK, 2 cột ĐK, 2 cột PS, 2 cột CK)!"
        ], None, nam_phat_hien

    # 3. Đọc và làm sạch từng dòng tài khoản
    du_lieu_sach = []
    cac_truong_tien = ["DuNoDauKy", "DuCoDauKy", "PhatSinhNo", "PhatSinhCo", "DuNoCuoiKy", "DuCoCuoiKy"]

    for r in range(data_start, len(df_raw)):
        row = df_raw.iloc[r]
        raw_ma = str(row.iloc[col_matk]).strip()
        if raw_ma.endswith('.0') and raw_ma[:-2].isdigit():
            raw_ma = raw_ma[:-2]

        # Bỏ qua dòng trống, nan hoặc chữ ký/tổng cộng
        if not raw_ma or raw_ma.lower() in ["nan", "none", ""]:
            continue

        # Lọc bỏ dòng tổng cộng hoặc tiêu đề footer
        tu_khoa_loai_tru = ["cộng", "tổng", "total", "người lập", "kế toán trưởng", "giám đốc", "ngày", "trang"]
        if any(kw in raw_ma.lower() for kw in tu_khoa_loai_tru):
            continue

        raw_ten = str(row.iloc[col_tentk]).strip() if col_tentk < tong_so_cot else ""
        if raw_ten.lower() in ["nan", "none"]:
            raw_ten = ""

        # Nếu tên chứa "tổng cộng" và mã không phải số chuẩn -> bỏ qua
        if any(kw in raw_ten.lower() for kw in ["tổng cộng", "cộng các"]) and not re.match(r'^[0-9]{3,6}$', raw_ma):
            continue

        # Mã tài khoản kế toán Việt Nam bắt buộc là 3 đến 6 chữ số
        if not re.match(r'^[0-9]{3,6}$', raw_ma):
            continue

        # Tự động điền tên tài khoản từ từ điển nếu file để trống
        if not raw_ten and tu_dien_tk and raw_ma in tu_dien_tk:
            raw_ten = tu_dien_tk[raw_ma]

        dict_dong = {
            "MaTK": raw_ma,
            "TenTK": raw_ten
        }

        # Đọc 6 cột số tiền (ĐK Nợ/Có, PS Nợ/Có, CK Nợ/Có)
        for i, ten_truong in enumerate(cac_truong_tien):
            c_idx = col_matk + 2 + i
            val_o = row.iloc[c_idx] if c_idx < tong_so_cot else 0.0
            dict_dong[ten_truong] = _chuan_hoa_so_tien(val_o)

        du_lieu_sach.append(dict_dong)

    if not du_lieu_sach:
        return False, [f"❌ LỖI: Không tìm thấy dòng tài khoản hợp lệ nào trong sheet '{sheet_chon}'!"], None, nam_phat_hien

    df_sach = pd.DataFrame(du_lieu_sach)

    # 4. Phân cấp Tài khoản Mẹ - Con và Chống tính trùng lặp (Anti Double-Counting)
    danh_sach_ma = set(df_sach["MaTK"].tolist())
    is_leaf_list = []
    for ma in df_sach["MaTK"]:
        # Tài khoản 'ma' là chi tiết nhất (Leaf) nếu không có tài khoản con nào khác trong bảng bắt đầu bằng 'ma'
        co_con = any(m != ma and m.startswith(ma) for m in danh_sach_ma)
        is_leaf_list.append(not co_con)

    df_sach["IsLeaf"] = is_leaf_list
    df_sach["CapTK"] = df_sach["MaTK"].apply(lambda x: 1 if len(x) == 3 else (2 if len(x) == 4 else 3))

    # 5. Kiểm tra Cân đối Kế toán chuẩn Thông tư 200 (Chỉ tính trên các tài khoản lá chi tiết)
    df_leaf = df_sach[df_sach["IsLeaf"] == True]
    if df_leaf.empty:
        df_leaf = df_sach

    sum_no_dk = df_leaf["DuNoDauKy"].sum()
    sum_co_dk = df_leaf["DuCoDauKy"].sum()
    sum_ps_no = df_leaf["PhatSinhNo"].sum()
    sum_ps_co = df_leaf["PhatSinhCo"].sum()
    sum_no_ck = df_leaf["DuNoCuoiKy"].sum()
    sum_co_ck = df_leaf["DuCoCuoiKy"].sum()

    danh_sach_msg = []
    so_tk = len(df_sach)
    so_leaf = len(df_leaf)
    nam_str = f" (Năm phát hiện: {nam_phat_hien})" if nam_phat_hien else ""
    danh_sach_msg.append(f"✅ Đọc thành công {so_tk} tài khoản từ sheet '{sheet_chon}'{nam_str}.")
    if so_leaf < so_tk:
        danh_sach_msg.append(f"ℹ️ Đã tự động phân cấp: {so_tk - so_leaf} tài khoản mẹ (tổng hợp) và {so_leaf} tài khoản chi tiết.")

    # Kiểm tra 3 cặp cân đối (cho phép sai số làm tròn <= 100 đồng)
    co_canh_bao = False
    if abs(sum_no_dk - sum_co_dk) > 100:
        co_canh_bao = True
        danh_sach_msg.append(
            f"⚠️ CẢNH BÁO ĐẦU KỲ: Dư Nợ ĐK ({sum_no_dk:,.0f}) LỆCH Dư Có ĐK ({sum_co_dk:,.0f}) — Chênh lệch: {abs(sum_no_dk - sum_co_dk):,.0f} đ."
        )

    if abs(sum_ps_no - sum_ps_co) > 100:
        co_canh_bao = True
        danh_sach_msg.append(
            f"⚠️ CẢNH BÁO PHÁT SINH: PS Nợ ({sum_ps_no:,.0f}) LỆCH PS Có ({sum_ps_co:,.0f}) — Chênh lệch: {abs(sum_ps_no - sum_ps_co):,.0f} đ."
        )

    if abs(sum_no_ck - sum_co_ck) > 100:
        co_canh_bao = True
        danh_sach_msg.append(
            f"⚠️ CẢNH BÁO CUỐI KỲ: Dư Nợ CK ({sum_no_ck:,.0f}) LỆCH Dư Có CK ({sum_co_ck:,.0f}) — Chênh lệch: {abs(sum_no_ck - sum_co_ck):,.0f} đ."
        )

    if not co_canh_bao:
        danh_sach_msg.append("✅ Ba cặp cân đối kế toán (Đầu kỳ, Trong kỳ, Cuối kỳ) hoàn toàn khớp đúng!")

    return True, danh_sach_msg, df_sach, nam_phat_hien