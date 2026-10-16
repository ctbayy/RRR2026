# app/utils/helpers.py
import sys
import os
import xml.etree.ElementTree as ET
import pandas as pd # <<< THÊM DÒNG NÀY
def _get_base_path():
    """
    Hàm nội bộ: Xác định thư mục gốc của ứng dụng.
    """
    if getattr(sys, 'frozen', False):
        # TRƯỜNG HỢP 1: CHẠY TỪ FILE .EXE
        # Trả về thư mục chứa file .exe
        return os.path.dirname(sys.executable)
    else:
        # TRƯỜNG HỢP 2: CHẠY TỪ CODE PYTHON (DEV)
        # __file__ nằm trong module_ho_tro/helpers.py -> lùi 2 cấp dirname để về thư mục gốc dự án
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. GỌI HÀM SAU (Để tính toán biến toàn cục)
BASE_APP_PATH = _get_base_path()

def get_persistent_data_path(relative_path_inside_data_dir):
    """Lấy đường dẫn đến file/thư mục trong thư mục Data cạnh file .exe hoặc gốc dự án."""
    application_path = _get_base_path()
    norm_rel = os.path.normpath(relative_path_inside_data_dir)
    if norm_rel.lower().startswith("data" + os.sep):
        full_path = os.path.join(application_path, norm_rel)
    elif norm_rel.lower() == "data":
        full_path = os.path.join(application_path, "Data")
    else:
        full_path = os.path.join(application_path, "Data", norm_rel)
    parent_dir = os.path.dirname(full_path)
    os.makedirs(parent_dir, exist_ok=True)
    return full_path


import pandas as pd
import re


def format_vn_number(value, col_name=""):
    """Định dạng số theo chuẩn VN (VD: 1.000.000,9). Tự động né các cột ID, Số HĐ, MST."""
    try:
        if pd.isna(value) or value == "":
            return ""

        if isinstance(value, str):
            if col_name:
                col_lower = str(col_name).lower()

                # 1. BỘ LỌC TỪ CHỐI (BLACKLIST) - Bảo vệ nghiêm ngặt các cột Định danh & Phân tích
                exclude_kw = [
                    'mã', 'ma ', 'mst', 'ký hiệu', 'mẫu', 'stt', 'ngày', 'tên', 'số tài khoản',
                    'số tk', 'số hđ', 'số hóa đơn', 'tài khoản', 'điện thoại',
                    'cảnh báo', 'canh bao', 'đối chiếu', 'doi chieu', 'trạng thái', 'trang thai',
                    'ghi chú', 'lệch', 'lech','số'
                ]
                if any(ex in col_lower for ex in exclude_kw):
                    return str(value)  # <-- BẢN VÁ: Ép chuẩn str()

                                 # 2. BỘ LỌC CHẤP NHẬN (WHITELIST) - Bao phủ mọi định dạng có dấu/không dấu
                money_kw = [
                    'tiền', 'tien', 'thuế', 'thue', 'giá trị', 'gia tri', 'doanh thu',
                    'tổng', 'tong', 'đơn giá', 'don gia', 'dongia', 'số lượng', 'so luong',
                    'trị giá', 'tri gia', 'ngoại tệ', 'thanhtien', 'chietkhau','Tổng Trị Giá Tính Thuế TK'
                ]

                is_money_col = any(k in col_lower for k in money_kw) or col_lower.startswith(
                    ('ct', '[ct')) or "(lbs:" in col_lower

                if not is_money_col:
                    return str(value)

            # --- CHỐT CHẶN BẢO VỆ CHỮ CÁI THUẦN TÚY ---
            # Nếu chuỗi có chứa bất kỳ chữ cái nào (tiếng Việt hoặc Anh), trả lại nguyên bản
            if re.search(r'[a-zA-ZáàảãạâấầẩẫậăắằẳẵặéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđĐ]', str(value)):
                return str(value)

            # 3. THUẬT TOÁN LÀM SẠCH CHUỖI SIÊU BỀN
            s = str(value).strip().replace(' ', '')
            if ',' in s and '.' in s:
                if s.rfind(',') > s.rfind('.'):
                    s = s.replace('.', '').replace(',', '.')
                else:
                    s = s.replace(',', '')
            elif ',' in s and '.' not in s:
                parts = s.split(',')
                if len(parts) == 2 and len(parts[1]) != 3:
                    s = s.replace(',', '.')
                else:
                    s = s.replace(',', '')
            elif '.' in s and ',' not in s:
                if len(s.split('.')) > 2:
                    s = s.replace('.', '')

            s = re.sub(r'[^\d\.-]', '', s)
            if not s or s == '-' or s == '.':
                return str(value)  # <-- BẢN VÁ: Trả lại nguyên gốc nếu không parse được

            f_val = float(s)
        else:
            f_val = float(value)

        if col_name and "năm" in str(col_name).lower() and 1900 <= f_val <= 2100:
            return str(int(f_val))

        # 4. CHUYỂN ĐỔI CHUẨN VIỆT NAM (1.000.000,9)
        if f_val.is_integer():
            return f"{int(f_val):,}".replace(",", ".")
        else:
            formatted = f"{f_val:,.4f}".rstrip("0").rstrip(".")
            return formatted.replace(",", "X").replace(".", ",").replace("X", ".")

    except Exception:
        return str(value)


def resource_path(relative_path):
    """
    Lấy đường dẫn tài nguyên (Đọc).
    Luôn trỏ ra ngoài thư mục gốc.
    """
    return os.path.join(BASE_APP_PATH, relative_path)

def get_maCQTNoiNop_from_xml(file_path: str) -> str | None:
    """
    Đọc nhanh thẻ <maCQTNoiNop> từ file XML mà không cần parse toàn bộ.
    Sử dụng iterparse để tối ưu tốc độ.
    """
    try:
        for event, elem in ET.iterparse(file_path, events=('end',)):
            tag_name = elem.tag.split('}')[-1]
            if tag_name == 'maCQTNoiNop':
                ma_cqt = elem.text.strip() if elem.text else None
                elem.clear()
                return ma_cqt
            elem.clear()
        return None
    except ET.ParseError as e:
        print(f"[WARN] utils.get_maCQTNoiNop: Lỗi parse XML file {os.path.basename(file_path)}: {e}")
        return None
    except FileNotFoundError:
        print(f"[ERROR] utils.get_maCQTNoiNop: Không tìm thấy file {os.path.basename(file_path)}")
        return None
    except Exception as e:
        print(f"[ERROR] utils.get_maCQTNoiNop: Lỗi không xác định khi đọc {os.path.basename(file_path)}: {e}")
        return None

def validate_cqt_match(xml_files: list[str], user_ma_cqt: str | None) -> tuple[bool, str | None]:
    """
    Kiểm tra xem maCQTNoiNop của tất cả các file XML có khớp với maCQT của người dùng không.
    """
    if not user_ma_cqt or not user_ma_cqt.strip():
        print("[Validate CQT] Người dùng không có maCQT, bỏ qua kiểm tra.")
        return True, None

    allowed_cqt_list = [code.strip() for code in user_ma_cqt.split(',') if code.strip()]
    if not allowed_cqt_list:
        print("[Validate CQT] Danh sách maCQT cho phép rỗng, bỏ qua kiểm tra.")
        return True, None

    print(f"[Validate CQT] Kiểm tra file với danh sách CQT: {allowed_cqt_list}")
    mismatched_files = []

    for file_path in xml_files:
        file_ma_cqt = get_maCQTNoiNop_from_xml(file_path)
        if file_ma_cqt is None:
            print(f"[Validate CQT] Lỗi: Không đọc được maCQTNoiNop từ file {os.path.basename(file_path)}")
            return False, f"Không thể đọc Mã CQT nơi nộp từ tệp: {os.path.basename(file_path)}"

        if file_ma_cqt not in allowed_cqt_list:
            mismatched_files.append(f"- {os.path.basename(file_path)} (Mã CQT: {file_ma_cqt})")

    if mismatched_files:
        print(f"[Validate CQT] Phát hiện {len(mismatched_files)} file không khớp CQT.")
        error_message = ("Tài khoản chưa được cấp quyền, liên hệ admin để hỗ trợ\n")
        return False, error_message
    else:
        print("[Validate CQT] Tất cả file đều khớp CQT.")
        return True, None
# ... (Giữ nguyên các hàm get_persistent_data_path, resource_path, ... đã có) ...

# === BẮT ĐẦU BỔ SUNG TỪ LOGIC.PY ===

def format_vietnamese_number(number, decimal_places=0):
    """Định dạng số theo kiểu Việt Nam (1.234,56). (Đã sửa lỗi NaN)"""
    if not isinstance(number, (int, float)):
        return str(number)

    # <<< SỬA LỖI: Bổ sung dòng kiểm tra NaN bị mất >>>
    if pd.isna(number):
        return "-"  # Trả về gạch ngang cho giá trị NaN

    try:
        if decimal_places == 0:
            number = round(number)  # Dòng này giờ đã an toàn
            return f"{number:,}".replace(',', '.')

        formatted_str = f"{number:,.{decimal_places}f}"
        integer_part, decimal_part = formatted_str.split('.')
        # Sửa lỗi logic ghép chuỗi thập phân
        integer_part_vn = integer_part.replace(',', '.')
        return f"{integer_part_vn},{decimal_part}"

    except (ValueError, TypeError):
        return str(number)  # Trả về chuỗi nếu vẫn lỗi


def get_single_value(data, key, default=0):
    """
    Lấy một giá trị số từ dictionary.
    Nếu không tìm thấy hoặc giá trị không hợp lệ, trả về giá trị default.
    """
    value = data.get(key, default)
    try:
        if isinstance(value, list):
            value = value[0] if value else default
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

# === KẾT THÚC BỔ SUNG ===