# app/analysis/xml_parser.py
import os
import xml.etree.ElementTree as ET
import traceback
from module_ho_tro.helpers import get_single_value
from datetime import datetime

# --- CẤU HÌNH MÃ TỜ KHAI (Bao hàm cả TT80 hiện hành và các TT cũ) ---
MA_TK_MAP = {
    # ==========================================
    # 1. DẢI MÁ THEO TT80/2021 (HIỆN HÀNH)
    # ==========================================
    '842': '01/GTGT',
    '844': '02/GTGT',
    '847': '04/GTGT',
    '892': '03/TNDN',
    '833': '04/TNDN',
    '953': '05/QTT-TNCN',
    '864': '05/KK-TNCN',

    # ==========================================
    # 2. DẢI MÃ THEO CÁC TT CŨ (TT156, TT26, TT92...)
    # (Phục vụ thanh tra, rà soát lại dữ liệu các năm trước)
    # ==========================================
    '01': '01/GTGT',  # Mẫu 01/GTGT cũ
    '02': '02/GTGT',  # Mẫu 02/GTGT cũ
    '03': '03/TNDN',  # Mẫu 03/TNDN cũ
    '394': '05/KK-TNCN',  # Mẫu 05/KK-TNCN theo TT92
    '395': '05/QTT-TNCN',  # Mẫu 05/QTT-TNCN theo TT92

    # ==========================================
    # 3. BÁO CÁO TÀI CHÍNH & CÁC TỜ KHAI KHÁC
    # ==========================================
    # BCTC theo Thông tư 200
    '402': 'BCTC_TT200', '671': 'BCTC_TT200', '672': 'BCTC_TT200',
    '676': 'BCTC_TT200', '675': 'BCTC_TT200',

    # BCTC theo Thông tư 133
    '699': 'BCTC_TT133', '695': 'BCTC_TT133', '696': 'BCTC_TT133',
    '684': 'BCTC_TT133', '685': 'BCTC_TT133', '686': 'BCTC_TT133',
    '683': 'BCTC_TT133',

    # Các loại thuế khác
    '924': '02/TAIN',
    '878': '01/PBVMT'
}
XML_TAG_MAP = {
    '01/GTGT': {
        # --- ĐẦU KỲ & MUA VÀO ---
        'gtgt_khau_tru_ky_truoc': 'ct22',
        'gia_tri_mua_vao_tong': 'ct23',
        'gia_tri_mua_vao_nhap_khau': 'ct23a',  # Điểm mới của TT80
        'thue_mua_vao_tong': 'ct24',
        'thue_mua_vao_nhap_khau': 'ct24a',     # Điểm mới của TT80
        'thue_duoc_khau_tru_ky_nay': 'ct25',

        # --- BÁN RA ---
        'doanh_thu_kct': 'ct26',
        'doanh_thu_0': 'ct29',
        'doanh_thu_5': 'ct30',
        'thue_ban_ra_5': 'ct31',
        'doanh_thu_10': 'ct32',
        'doanh_thu_khong_tinh_thue': 'ct32a',  # TT80 thay đổi bản chất chỉ tiêu này
        'thue_ban_ra_10': 'ct33',
        'tong_doanh_thu': 'ct34',
        'tong_thue_ban_ra': 'ct35',

        # --- TÍNH TOÁN & KẾT CHUYỂN ---
        'thue_phat_sinh_trong_ky': 'ct36',
        'dieu_chinh_giam_ky_truoc': 'ct37',
        'dieu_chinh_tang_ky_truoc': 'ct38',
        'thue_da_nop_dia_phuong_khac': 'ct39', # Khác biệt lớn ở TT80 (Phân bổ)
        'thue_phai_nop_sxkd': 'ct40a',         # Điểm mới TT80
        'thue_mua_vao_da_bu_tru': 'ct40b',     # Điểm mới TT80
        'thue_phai_nop_cuoi_cung': 'ct40',
        'thue_chua_khau_tru_het': 'ct41',
        'thue_de_nghi_hoan': 'ct42',
        'thue_chuyen_ky_sau': 'ct43'
    },

    '02/GTGT': {
        'gtgt_chua_hoan_ky_truoc': 'ct21',
        'gtgt_nhan_ban_giao': 'ct21a',
        'gia_tri_mua_vao_da': 'ct22',
        'gia_tri_mua_vao_nhap_khau_da': 'ct22a', # Điểm mới TT80
        'thue_mua_vao_da': 'ct23',
        'thue_mua_vao_nhap_khau_da': 'ct23a',    # Điểm mới TT80
        'dc_tang_gia_tri': 'ct24',
        'dc_tang_thue': 'ct25',
        'dc_giam_gia_tri': 'ct26',
        'dc_giam_thue': 'ct27',
        'tong_thue_mua_vao_da': 'ct28',
        'bu_tru_sxkd_cung_tinh': 'ct28a',
        'thue_chua_hoan_chuyen_ky_sau_da': 'ct29',
        'thue_de_nghi_hoan_da': 'ct30',
        'thue_ban_giao_dn_moi': 'ct31',
        'thue_ban_giao_hoat_dong': 'ct31a',
        'thue_chua_hoan_chuyen_ky_sau_cuoi': 'ct32'
    },
    # ------------------------------------
    '03/TNDN': {
        'tong_doanh_thu_pl': 'pl_03_1a_ct04', 'doanh_thu_xuat_khau_pl': 'pl_03_1a_ct05',
        'thu_nhap_khac_pl': 'pl_03_1a_ct19', 'loi_nhuan_truoc_thue': 'ctA1',
        'chi_phi_pl': 'pl_03_1a_ct12', 'thue_tndn_phai_nop': 'ctC9'
    },
    'BCTC_TT133': {
        'tien_scn': 'scn_ct110', 'hang_ton_kho_scn': 'scn_ct140', 'no_phai_tra_scn': 'scn_ct300',
        'von_chu_so_huu_scn': 'scn_ct400',
        'tien_sdn': 'sdn_ct110', 'hang_ton_kho_sdn': 'sdn_ct140', 'no_phai_tra_sdn': 'sdn_ct300',
        'von_chu_so_huu_sdn': 'sdn_ct400',
        'doanh_thu_bh_nn': 'kqkd_nn_ct01', 'gia_von_nn': 'kqkd_nn_ct11', 'chi_phi_lai_vay_nn': 'kqkd_nn_ct23',
        'loi_nhuan_truoc_thue_nn': 'kqkd_nn_ct50', 'loi_nhuan_sau_thue_nn': 'kqkd_nn_ct60',
        'doanh_thu_bh_nt': 'kqkd_nt_ct01', 'gia_von_nt': 'kqkd_nt_ct11', 'chi_phi_lai_vay_nt': 'kqkd_nt_ct23',
        'loi_nhuan_truoc_thue_nt': 'kqkd_nt_ct50', 'loi_nhuan_sau_thue_nt': 'kqkd_nt_ct60',
    },
    'BCTC_TT200': {
        'tien_scn': 'scn_ct110', 'hang_ton_kho_scn': 'scn_ct140', 'no_phai_tra_scn': 'scn_ct300',
        'von_chu_so_huu_scn': 'scn_ct400',
        'tien_sdn': 'sdn_ct110', 'hang_ton_kho_sdn': 'sdn_ct140', 'no_phai_tra_sdn': 'sdn_ct300',
        'von_chu_so_huu_sdn': 'sdn_ct400',
        'doanh_thu_bh_nn': 'ct01', 'gia_von_nn': 'ct11', 'chi_phi_lai_vay_nn': 'ct23',
        'loi_nhuan_truoc_thue_nn': 'ct50', 'loi_nhuan_sau_thue_nn': 'ct60',
        'doanh_thu_bh_nt': 'ct01_nt', 'gia_von_nt': 'ct11_nt', 'chi_phi_lai_vay_nt': 'ct23_nt',
        'loi_nhuan_truoc_thue_nt': 'ct50_nt', 'loi_nhuan_sau_thue_nt': 'ct60_nt',
        'lctt_kd_nn': 'ct20', 'lctt_dtu_nn': 'ct30', 'lctt_tc_nn': 'ct40', 'tien_tuong_duong_ck_nn': 'ct70',
    },
    '05/KK-TNCN': {
        'tong_so_ld': 'ct16', 'tong_tnct': 'ct21', 'tong_thue_da_khau_tru': 'ct29'
    },
    '05/QTT-TNCN': {
        'tong_so_ld': 'ct16', 'tong_tnct_phai_kt': 'ct28', 'tong_thue_da_khau_tru': 'ct31',
        'tong_so_ld_kt': "ct19", "tong_so_gtgc": "ct22", "tong_tnct_all": "ct23",
        'pl_05_1_ho_ten': 'ct07', 'pl_05_1_mst': 'ct08', 'pl_05_1_tnct': 'ct12',
        'pl_05_1_giam_tru_gia_canh': 'ct17', 'pl_05_1_tn_tinh_thue': 'ct21',
        'pl_05_1_thue_da_khau_tru': 'ct22', 'pl_05_1_so_thue_phai_nop': 'ct24'
    },
    '02/TAIN': {'tong_san_luong': 'tongSanLuong', 'tong_thue_phai_nop': 'tongThuePhaiNop'},
    '01/PBVMT': {'tong_phi_phai_nop': 'tongPhiPNop'}
}


def parse_xml_data(file_path):
    """ (Hàm này giữ nguyên như cũ, chỉ để đọc dữ liệu chi tiết) """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        tree = ET.fromstring(xml_content)
        data = {}
        parent_map = {c: p for p in tree.iter() for c in p}
        single_value_tags = ['maTKhai', 'kyKKhai', 'mst', 'tenNNT', 'dchiNNT', 'tenHuyenNNT', 'tenTinhNNT', 'loaiTKhai',
                             'soLan', 'kieuKy','ngayLapTKhai']

        ma_tk_elem = tree.find('.//maTKhai')
        if ma_tk_elem is not None: data['maTKhai'] = ma_tk_elem.text

        for elem in tree.iter():
            if not (elem.text and elem.text.strip()): continue
            tag = elem.tag.split('}', 1)[-1]
            key = tag;
            value = elem.text.strip()
            parent = parent_map.get(elem)
            parent_tag = parent.tag.split('}', 1)[-1] if parent is not None else None
            grandparent = parent_map.get(parent) if parent is not None else None
            grandparent_tag = grandparent.tag.split('}', 1)[-1] if grandparent is not None else None

            if grandparent_tag == 'PL_KQHDSXKD':
                if parent_tag == 'NamNay' and tag.startswith('ct'):
                    key = f"kqkd_nn_{tag}"
                elif parent_tag == 'NamTruoc' and tag.startswith('ct'):
                    key = f"kqkd_nt_{tag}"
            elif grandparent_tag == 'PL_LCTTTT':
                current_loai_tk = MA_TK_MAP.get(data.get('maTKhai'))
                if current_loai_tk == 'BCTC_TT200':
                    if parent_tag == 'NamNay' and tag.startswith('ct'):
                        key = f"lctt_nn_{tag}"
                    elif parent_tag == 'NamTruoc' and tag.startswith('ct'):
                        key = f"lctt_nt_{tag}"
            elif parent_tag == 'PLuc_03_1A_TNDN' and tag.startswith('ct'):
                key = f"pl_03_1a_{tag}"
            elif parent_tag == 'SoCuoiNam' and tag.startswith('ct'):
                key = f"scn_{tag}"
            elif parent_tag == 'SoDauNam' and tag.startswith('ct'):
                key = f"sdn_{tag}"
            elif grandparent_tag == 'SoPhatSinhTrongKy':
                if parent_tag == 'No':
                    key = f"ps_no_{tag}"
                elif parent_tag == 'Co':
                    key = f"ps_co_{tag}"
            elif grandparent_tag == 'SoDuDauKy':
                if parent_tag == 'No':
                    key = f"sddk_no_{tag}"
                elif parent_tag == 'Co':
                    key = f"sddk_co_{tag}"
            elif grandparent_tag == 'SoDuCuoiKy':
                if parent_tag == 'No':
                    key = f"sdck_no_{tag}"
                elif parent_tag == 'Co':
                    key = f"sdck_co_{tag}"

            if tag in single_value_tags:
                if tag not in data: data[tag] = value
            else:
                if key in data:
                    if not isinstance(data[key], list): data[key] = [data[key]]
                    data[key].append(value)
                else:
                    data[key] = value
        return data
    except:
        return {}


def get_declaration_metadata(file_path):
    """
    Đọc metadata (Phiên bản 'Ăn tạp' - Bỏ qua Namespace để tìm thẻ chính xác).
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Danh sách các thẻ cần tìm (bỏ qua namespace)
        target_tags = {
            'maTKhai': None,
            'kyKKhai': None,
            'kieuKy': None,
            'soLan': None,
            'loaiTKhai': None,  # XML tag C/B
            'ngayLapTKhai': None
        }

        # Quét toàn bộ cây XML một cách phẳng (Iterate)
        # Cách này an toàn hơn .find() vì nó không quan tâm cấu trúc lồng nhau hay namespace
        for elem in root.iter():
            # Lấy tên thẻ thuần (bỏ phần {http://...})
            clean_tag = elem.tag.split('}')[-1]

            if clean_tag in target_tags and target_tags[clean_tag] is None:
                # Chỉ lấy giá trị đầu tiên tìm thấy (thường nằm ở phần Thông tin chung)
                target_tags[clean_tag] = elem.text.strip() if elem.text else ""

        # Trích xuất dữ liệu
        ma_tk = target_tags['maTKhai']
        ky_kk = target_tags['kyKKhai'] if target_tags['kyKKhai'] else "Không rõ"
        ngay_lap = target_tags['ngayLapTKhai'] if target_tags['ngayLapTKhai'] else ""
        # [LOGIC MỚI] FORMAT LẠI NGÀY THÀNH dd/mm/yyyy
        if ngay_lap:
            try:
                # Thử parse theo chuẩn XML (YYYY-MM-DD)
                dt_obj = datetime.strptime(ngay_lap, '%Y-%m-%d')
                ngay_lap = dt_obj.strftime('%d/%m/%Y')
            except:
                # Nếu lỗi (do khác format hoặc rỗng), giữ nguyên giá trị gốc
                pass
        # ---------------------------------------------
        # Mặc định kieuKy là 'M' nếu không tìm thấy, để tránh lỗi logic
        kieu_ky_raw = target_tags['kieuKy']
        kieu_ky = kieu_ky_raw.upper() if kieu_ky_raw else "M"

        so_lan = 0
        if target_tags['soLan'] and target_tags['soLan'].isdigit():
            so_lan = int(target_tags['soLan'])

        if ma_tk:
            loai_tk = MA_TK_MAP.get(ma_tk, "Không xác định")

            # Phân tích năm dựa trên kỳ và kiểu kỳ tìm được
            y, _, _ = parse_period(ky_kk, kieu_ky)
            nam = str(y) if y > 0 else "N/A"

            return {
                'file_path': file_path,
                'loai_tk': loai_tk,
                'ky_kk': ky_kk,
                'nam': nam,
                'ma_tk': ma_tk,
                'so_lan': so_lan,
                'kieu_ky': kieu_ky,
                'loai_tk_xml': target_tags['loaiTKhai'] or '',
                'ngay_lap': ngay_lap
            }

        return None

    except Exception as e:
        print(f"Lỗi quét metadata file {os.path.basename(file_path)}: {e}")
        return None


def parse_period(ky_kk_str, kieu_ky='M'):
    """
    Phân tích kỳ dựa trên Kiểu Kỳ (kieu_ky).
    - kieu_ky='Q': Số là Quý.
    - kieu_ky='M': Số là Tháng.
    - kieu_ky='Y'/'CN': Số là Năm.
    """
    if not isinstance(ky_kk_str, str): return 0, 0, 0
    clean_str = ky_kk_str.strip().upper()
    year, quarter, month = 0, 0, 0

    try:
        # Xử lý trường hợp có gạch chéo: "01/2024", "Q1/2024"
        if '/' in clean_str:
            parts = clean_str.split('/')
            if len(parts) == 2 and parts[-1].isdigit():
                year = int(parts[-1])
                first_part = parts[0]

                # Nếu có chữ Q (Q1) -> Chắc chắn là Quý
                if 'Q' in first_part:
                    quarter = int(first_part.replace('Q', ''))
                # Nếu có chữ T (T1) -> Chắc chắn là Tháng
                elif 'T' in first_part:
                    month = int(first_part.replace('T', ''))
                # Nếu chỉ có số (1) -> Dựa vào kieu_ky để quyết định
                elif first_part.isdigit():
                    val = int(first_part)
                    if kieu_ky == 'Q':
                        quarter = val
                    elif kieu_ky == 'M':
                        month = val
                    else:
                        # Fallback nếu kieu_ky lạ: Đoán <=4 là Quý (Rủi ro nhưng phải chấp nhận nếu thiếu data)
                        if val <= 4:
                            quarter = val
                        else:
                            month = val

        # Xử lý trường hợp chỉ có năm: "2024", "N2024"
        elif len(clean_str) == 4 and clean_str.isdigit():
            year = int(clean_str)
        elif clean_str.startswith('N') and clean_str[1:].isdigit():
            year = int(clean_str[1:])

    except:
        return 0, 0, 0

    return year, quarter, month


def _get_sort_key_for_period(ky_kk_str, kieu_ky='M'):
    """
    Tạo khóa sắp xếp. Nhận thêm kieu_ky.
    """
    year, quarter, month = parse_period(ky_kk_str, kieu_ky)
    # Quy đổi ra đơn vị tháng để sort: Quý 1 -> Tháng 3, Quý 2 -> Tháng 6...
    period_val = month
    if quarter > 0:
        period_val = quarter * 3

    return (year, period_val)