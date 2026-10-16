# app/analysis/dictionary_loader.py
import os
import json
import pandas as pd
from module_ho_tro.helpers import get_persistent_data_path

# Đường dẫn file lưu trữ: Đổi đuôi thành .json và chuyển sang thư mục Data
DICT_PATH = get_persistent_data_path(os.path.join('Data', 'dictionary.json'))

def load_synonyms():
    """Tải từ điển từ file JSON (Siêu tốc độ)"""
    if not os.path.exists(DICT_PATH):
        return {}
    try:
        with open(DICT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('synonyms', {}) if isinstance(data, dict) else {}
    except Exception as e:
        print(f"Lỗi đọc từ điển: {e}")
        return {}

def save_synonyms(synonyms_dict):
    """Lưu từ điển xuống file JSON"""
    try:
        os.makedirs(os.path.dirname(DICT_PATH), exist_ok=True)
        # ensure_ascii=False để lưu chuẩn Tiếng Việt có dấu, indent=4 để format đẹp
        with open(DICT_PATH, 'w', encoding='utf-8') as f:
            json.dump({'synonyms': synonyms_dict}, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Lỗi lưu từ điển: {e}")
        return False

def import_from_excel(file_path):
    """
    Đọc file Excel mẫu.
    Yêu cầu file Excel có 2 cột: 'VietTat' và 'DayDu' (hoặc cột A và B)
    """
    try:
        # Đọc header dòng 0, nếu không thấy cột chuẩn thì thử đọc không header
        df = pd.read_excel(file_path, dtype=str)

        # Chuẩn hóa tên cột
        df.columns = [str(c).strip().lower() for c in df.columns]

        # Mapping cột linh hoạt
        col_abbr = next((c for c in df.columns if c in ['viettat', 'viết tắt', 'mã', 'code']), None)
        col_full = next((c for c in df.columns if c in ['daydu', 'đầy đủ', 'tên', 'name']), None)

        # Nếu không tìm thấy tên cột, giả định cột 0 là viết tắt, cột 1 là đầy đủ
        if not col_abbr or not col_full:
            df = pd.read_excel(file_path, header=None, dtype=str)
            if df.shape[1] >= 2:
                new_dict = pd.Series(df.iloc[:, 1].values, index=df.iloc[:, 0]).to_dict()
            else:
                return None
        else:
            new_dict = pd.Series(df[col_full].values, index=df[col_abbr]).to_dict()

        # Làm sạch dữ liệu (xóa nan, trim khoảng trắng)
        clean_dict = {
            str(k).strip(): str(v).strip()
            for k, v in new_dict.items()
            if pd.notna(k) and pd.notna(v) and str(k).strip()
        }
        return clean_dict
    except Exception as e:
        print(f"Lỗi import Excel: {e}")
        return None

def add_single_synonym(abbr, full):
    """Thêm một cặp từ đồng nghĩa mới và lưu ngay"""
    current_dict = load_synonyms()

    # Chuẩn hóa key
    abbr = str(abbr).strip()
    full = str(full).strip()

    if not abbr or not full: return False

    current_dict[abbr] = full
    return save_synonyms(current_dict)