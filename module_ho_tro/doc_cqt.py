# module_ho_tro/doc_cqt.py
import pandas as pd
import os


def lay_danh_sach_cqt():
    """Đọc file Excel danh sách CQT, trả về mảng ['10100 - Cục Thuế TP Hà Nội', ...]"""
    try:
        # Chỏ đường dẫn vào thư mục Data gốc
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "Data", "danh_sach_co_quan_thue.xlsx")

        if not os.path.exists(file_path):
            return ["* - Tất cả Cơ quan Thuế (Admin)"]

        # Đọc 2 cột đầu tiên (Mã CQT và Tên CQT)
        df = pd.read_excel(file_path, dtype=str, usecols=[0, 1])
        cqt_list = []
        for _, row in df.iterrows():
            ma_cqt = str(row.iloc[0]).strip()
            ten_cqt = str(row.iloc[1]).strip() if len(row) > 1 else ""
            if ma_cqt and ma_cqt.lower() != "nan":
                cqt_list.append(f"{ma_cqt} - {ten_cqt}")
        return cqt_list
    except Exception as e:
        print(f"Lỗi đọc file CQT: {e}")
        return ["* - Tất cả Cơ quan Thuế (Admin)"]