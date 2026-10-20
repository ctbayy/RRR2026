# -*- coding: utf-8 -*-
"""
THƯ VIỆN NỘI DUNG DIỄN GIẢI & MẪU CÂU KIỂM TRA THUẾ
Hỗ trợ sinh tự động câu văn giải trình cho Phiếu nhận xét, Thông báo giải trình và Tờ trình.
Loại bỏ hoàn toàn các thuật ngữ 'Vế A', 'Vế B', phiên dịch chi tiết các mã chỉ tiêu và tài khoản kế toán.
"""

import re
import json
import os
from module_ho_tro.dinh_dang_so import dinh_dang_so_vn


def format_tien(val):
    """Định dạng số tiền VNĐ chuẩn Việt Nam (phân cách hàng nghìn bằng dấu chấm)"""
    try:
        if val is None or val == "":
            return "0"
        num = round(float(str(val).replace(',', '').strip()), 0)
        return dinh_dang_so_vn(num, 0)
    except Exception:
        return str(val)


# BỘ TỪ ĐIỂN TÀI KHOẢN KẾ TOÁN CHUẨN
MAP_TK_DETAIL = {
    '111': 'TK 111 - Tiền mặt',
    '112': 'TK 112 - Tiền gửi ngân hàng',
    '128': 'TK 128 - Đầu tư nắm giữ đến ngày đáo hạn',
    '131': 'TK 131 - Phải thu của khách hàng',
    '138': 'TK 138 - Phải thu khác',
    '1388': 'TK 1388 - Phải thu khác',
    '141': 'TK 141 - Tạm ứng',
    '152': 'TK 152 - Nguyên liệu, vật liệu',
    '153': 'TK 153 - Công cụ, dụng cụ',
    '154': 'TK 154 - Chi phí SXKD dở dang',
    '155': 'TK 155 - Thành phẩm',
    '156': 'TK 156 - Hàng hóa',
    '211': 'TK 211 - Tài sản cố định hữu hình',
    '214': 'TK 214 - Hao mòn tài sản cố định',
    '241': 'TK 241 - Xây dựng cơ bản dở dang',
    '242': 'TK 242 - Chi phí trả trước',
    '331': 'TK 331 - Phải trả cho người bán',
    '3331': 'TK 3331 - Thuế GTGT phải nộp',
    '333': 'TK 333 - Thuế và các khoản phải nộp Nhà nước',
    '334': 'TK 334 - Phải trả người lao động',
    '338': 'TK 338 - Phải trả, phải nộp khác',
    '3388': 'TK 3388 - Phải trả khác',
    '341': 'TK 341 - Vay và nợ thuê tài chính',
    '411': 'TK 411 - Vốn đầu tư của chủ sở hữu',
    '511': 'TK 511 - Doanh thu bán hàng và cung cấp dịch vụ',
    '515': 'TK 515 - Doanh thu hoạt động tài chính',
    '621': 'TK 621 - Chi phí NVL trực tiếp',
    '622': 'TK 622 - Chi phí nhân công trực tiếp',
    '623': 'TK 623 - Chi phí sử dụng máy thi công',
    '627': 'TK 627 - Chi phí sản xuất chung',
    '632': 'TK 632 - Giá vốn hàng bán',
    '635': 'TK 635 - Chi phí tài chính',
    '641': 'TK 641 - Chi phí bán hàng',
    '642': 'TK 642 - Chi phí quản lý doanh nghiệp',
    '711': 'TK 711 - Thu nhập khác',
    '811': 'TK 811 - Chi phí khác',
    '911': 'TK 911 - Xác định kết quả kinh doanh',
}

# BỘ TỪ ĐIỂN CHỈ TIÊU TỜ KHAI CHUẨN
MAP_CHI_TIEU_DETAIL = {
    "ct21": "Chỉ tiêu [21] - Không phát sinh hoạt động mua bán trong kỳ",
    "ct22": "Chỉ tiêu [22] - Thuế GTGT còn được khấu trừ kỳ trước chuyển sang",
    "ct23": "Chỉ tiêu [23] - Giá trị của hàng hóa, dịch vụ mua vào",
    "ct24": "Chỉ tiêu [24] - Thuế GTGT của hàng hóa, dịch vụ mua vào",
    "ct25": "Chỉ tiêu [25] - Thuế GTGT mua vào được khấu trừ kỳ này",
    "ct26": "Chỉ tiêu [26] - Doanh thu hàng hóa, dịch vụ bán ra không chịu thuế GTGT",
    "ct27": "Chỉ tiêu [27] - Giá trị HHDV bán ra chịu thuế GTGT",
    "ct28": "Chỉ tiêu [28] - Thuế GTGT của HHDV bán ra chịu thuế",
    "ct29": "Chỉ tiêu [29] - HHDV bán ra chịu thuế suất 0%",
    "ct30": "Chỉ tiêu [30] - Doanh thu HHDV bán ra chịu thuế suất 5%",
    "ct31": "Chỉ tiêu [31] - Thuế GTGT HHDV bán ra chịu thuế suất 5%",
    "ct32": "Chỉ tiêu [32] - Doanh thu HHDV bán ra chịu thuế suất 10%",
    "ct33": "Chỉ tiêu [33] - Thuế GTGT HHDV bán ra chịu thuế suất 10%",
    "ct32a": "Chỉ tiêu [32a] - Hàng hóa, dịch vụ bán ra không tính thuế",
    "ct34": "Chỉ tiêu [34] - Tổng doanh thu của HHDV bán ra trên tờ khai GTGT",
    "ct35": "Chỉ tiêu [35] - Tổng thuế GTGT của HHDV bán ra",
    "ct36": "Chỉ tiêu [36] - Thuế GTGT phát sinh trong kỳ",
    "ct37": "Chỉ tiêu [37] - Điều chỉnh giảm thuế GTGT còn được khấu trừ của các kỳ trước",
    "ct38": "Chỉ tiêu [38] - Điều chỉnh tăng thuế GTGT còn được khấu trừ của các kỳ trước",
    "ct40": "Chỉ tiêu [40] - Thuế GTGT còn phải nộp trong kỳ",
    "ct40a": "Chỉ tiêu [40a] - Thuế GTGT phải nộp của hoạt động SXKD",
    "ct43": "Chỉ tiêu [43] - Thuế GTGT còn được khấu trừ chuyển kỳ sau",
    "ct04": "Chỉ tiêu [04] - Doanh thu bán hàng và CCDV trên Phụ lục 03-1A/TNDN",
    "ct10": "Chỉ tiêu [10] - Doanh thu tài chính trên Phụ lục 03-1A/TNDN",
    "ct13": "Chỉ tiêu [13] - Giá vốn hàng bán trên Phụ lục 03-1A/TNDN",
    "ct14": "Chỉ tiêu [14] - Chi phí bán hàng trên Phụ lục 03-1A/TNDN",
    "ct15": "Chỉ tiêu [15] - Chi phí quản lý DN trên Phụ lục 03-1A/TNDN",
    "ct16": "Chỉ tiêu [16] - Chi phí tài chính trên Phụ lục 03-1A/TNDN",
    "ct19": "Chỉ tiêu [19] - Thu nhập khác trên Phụ lục 03-1A/TNDN",
    "ct20": "Chỉ tiêu [20] - Chi phí khác trên Phụ lục 03-1A/TNDN",
    "ct22": "Chỉ tiêu [22] - Tổng lợi nhuận kế toán trước thuế TNDN",
    "ctA1": "Chỉ tiêu [A1] - Tổng lợi nhuận kế toán trước thuế TNDN",
    "ctB1": "Chỉ tiêu [B1] - Điều chỉnh tăng tổng lợi nhuận trước thuế",
    "ctB4": "Chỉ tiêu [B4] - Các khoản chi không được trừ khi xác định thu nhập chịu thuế",
    "ctC1": "Chỉ tiêu [C1] - Thu nhập chịu thuế TNDN",
    "ctC4": "Chỉ tiêu [C4] - Thu nhập tính thuế TNDN",
    "ctD": "Chỉ tiêu [D] - Tổng số thuế TNDN phải nộp",
    "ct141": "Chỉ tiêu [141] - Hàng tồn kho trên BCTC",
    "ct312": "Chỉ tiêu [312] - Người mua trả tiền trước ngắn hạn",
    "ct332": "Chỉ tiêu [332] - Người mua trả tiền trước dài hạn",
    "ct151": "Chỉ tiêu [151] - Chi phí trả trước ngắn hạn",
    "ct261": "Chỉ tiêu [261] - Chi phí trả trước dài hạn",
    "ct270": "Chỉ tiêu [270] - Tổng tài sản trên BCTC"
}


def dich_ten_chi_tieu(expr, rui_ro_dict=None, is_ve_b=False):
    """
    Chuyển đổi các tag/mã công thức sang tên tiếng Việt chuẩn mực ngành Thuế.
    Loại bỏ hoàn toàn các từ 'Vế A', 'Vế B', 'Chỉ tiêu Vế A/B'.
    """
    s = str(expr or '').strip()

    # Nếu chuỗi rỗng hoặc chứa Vế A/B, tự động nội suy từ thông tin rủi ro
    if not s or any(v in s.lower() for v in ['vế a', 'vế b', 've a', 've b', 'chỉ tiêu vế', 'chỉ tiêu đối chiếu']):
        ten_pt = str(rui_ro_dict.get('ten_phan_tich', '') if rui_ro_dict else '').strip()
        if is_ve_b:
            if '511' in ten_pt and '3331' in ten_pt:
                return 'Tổng phát sinh Có TK 511 (Doanh thu) và Có TK 3331 (Thuế GTGT)'
            elif '621' in ten_pt:
                return 'Chi phí NVL trực tiếp (TK 621)'
            elif 'gtgt' in ten_pt.lower() or 'tờ khai' in ten_pt.lower():
                return 'Số liệu kê khai trên Tờ khai thuế GTGT'
            elif 'tk 511' in ten_pt.lower():
                return 'Phát sinh Có TK 511 - Doanh thu bán hàng'
            else:
                return 'Chỉ tiêu đối chiếu liên quan'
        else:
            return ten_pt or 'Chỉ tiêu kê khai'

    # Tra cứu từ điển chuẩn ngành Thuế TU_DIEN_TO_KHAI
    try:
        from module_doc_xml.tu_dien_chi_tieu import TU_DIEN_TO_KHAI
    except ImportError:
        TU_DIEN_TO_KHAI = {}

    def tim_tu_dien_chuan(form_key, code):
        c_clean = str(code).replace('ct', '').strip()
        if form_key and form_key in TU_DIEN_TO_KHAI:
            f_d = TU_DIEN_TO_KHAI[form_key]
            if isinstance(f_d, dict):
                for p, p_d in f_d.items():
                    if isinstance(p_d, dict):
                        for k, v in p_d.items():
                            if k == code or k == c_clean or k == f'ct{c_clean}':
                                return v
        # Tìm quét toàn bộ từ điển nếu chưa thấy
        for f, f_d in TU_DIEN_TO_KHAI.items():
            if isinstance(f_d, dict):
                for p, p_d in f_d.items():
                    if isinstance(p_d, dict):
                        for k, v in p_d.items():
                            if k == code or k == c_clean or k == f'ct{c_clean}':
                                return v
        return ''

    # 1. Regex cho CDTK: [BCTC_TT133 | CDTK_NoPhatSinh | ct131] hoặc [| CDTK_CoCuoiKy | ct3387]
    def rep_cdtk(m):
        phu_luc = m.group(1)
        code = m.group(2).replace('ct', '').strip()
        d = {
            'CDTK_NoPhatSinh': 'Phát sinh Nợ TK',
            'CDTK_CoPhatSinh': 'Phát sinh Có TK',
            'CDTK_NoCuoiKy': 'Số dư Nợ cuối kỳ TK',
            'CDTK_CoCuoiKy': 'Số dư Có cuối kỳ TK',
            'CDTK_NoDauKy': 'Số dư Nợ đầu kỳ TK',
            'CDTK_CoDauKy': 'Số dư Có đầu kỳ TK'
        }
        ten_tk = tim_tu_dien_chuan('BCTC_TT133', f'ct{code}') or MAP_TK_DETAIL.get(code, '')
        label = d.get(phu_luc, 'Phát sinh TK')
        if ten_tk and 'Tài khoản' in ten_tk:
            return f'{label} {code} ({ten_tk})'
        elif ten_tk:
            return f'{label} {code} - {ten_tk}'
        return f'{label} {code}'

    s = re.sub(r'\[\s*(?:BCTC_TT\d+)?\s*\|\s*(CDTK_\w+)\s*\|\s*ct(\w+)\]', rep_cdtk, s)

    # 2. Regex cho CDKT: [BCTC_TT133 | CDKT_SoCuoiNam | ct315] hoặc [| CDKT_SoCuoiNam | ct315]
    def rep_cdkt(m):
        phu_luc = m.group(1)
        code = m.group(2).strip()
        c_num = code.replace('ct', '')
        ten_ct = tim_tu_dien_chuan('BCTC_TT133', code) or tim_tu_dien_chuan('BCTC_TT200', code) or MAP_CHI_TIEU_DETAIL.get(f'ct{c_num}', '')
        dau_ky = " (đầu năm)" if "DauNam" in phu_luc else ""
        if ten_ct:
            clean_name = re.sub(r'^\d+\.\s*', '', ten_ct)
            return f'Chỉ tiêu [{c_num}] - {clean_name}{dau_ky}'
        return f'Chỉ tiêu [{c_num}] trên BCTC{dau_ky}'

    s = re.sub(r'\[\s*(?:BCTC_TT\d+)?\s*\|\s*(CDKT_\w+)\s*\|\s*ct(\w+)\]', rep_cdkt, s)

    # 3. Regex cho 03/TNDN: [03/TNDN | ChiTieuChinh | ctB15] hoặc [03/TNDN | PL 03-1A | ct04]
    def rep_tndn(m):
        code = m.group(1).strip()
        c_num = code.replace('ct', '')
        ten_ct = tim_tu_dien_chuan('03/TNDN', code) or MAP_CHI_TIEU_DETAIL.get(f'ct{c_num}', '')
        if ten_ct:
            clean_name = re.sub(r'^[A-Za-z0-9]+\.\s*', '', ten_ct)
            return f'Chỉ tiêu [{c_num}] - {clean_name}'
        return f'Chỉ tiêu [{c_num}] trên tờ khai QTT TNDN'

    s = re.sub(r'\[03/TNDN\s*\|\s*.*?\s*\|\s*ct(\w+)\]', rep_tndn, s)

    # 4. Regex cho 01/GTGT: [01/GTGT | ChiTieuChinh | ct34]
    def rep_gtgt(m):
        code = m.group(1).strip()
        c_num = code.replace('ct', '')
        ten_ct = tim_tu_dien_chuan('01/GTGT', code) or MAP_CHI_TIEU_DETAIL.get(f'ct{c_num}', '')
        if ten_ct:
            clean_name = re.sub(r'^[A-Za-z0-9]+\.\s*', '', ten_ct)
            return f'Chỉ tiêu [{c_num}] - {clean_name}'
        return f'Chỉ tiêu [{c_num}] trên tờ khai GTGT'

    s = re.sub(r'\[01/GTGT\s*\|\s*.*?\s*\|\s*ct(\w+)\]', rep_gtgt, s)

    # Xử lý các tiền tố biểu mẫu
    s = re.sub(r'BCTC_TT\d+\s*\(?', '', s)
    s = re.sub(r'Tờ khai\s*', '', s)
    s = s.replace('[|', '').replace('|', ' - ')

    # Thay thế chỉ tiêu tờ khai (sắp xếp giảm dần theo độ dài để ct312 match trước ct31)
    for ct_code, ct_desc in sorted(MAP_CHI_TIEU_DETAIL.items(), key=lambda x: len(x[0]), reverse=True):
        s = re.sub(r'\bChỉ tiêu\s+' + re.escape(ct_code) + r'\b', ct_desc, s)
        s = re.sub(r'\b' + re.escape(ct_code) + r'\b', ct_desc, s)

    # Thay thế tài khoản (sắp xếp giảm dần để 1388 match trước 138)
    for tk_code, tk_desc in sorted(MAP_TK_DETAIL.items(), key=lambda x: len(x[0]), reverse=True):
        s = re.sub(r'\bTK\s+' + re.escape(tk_code) + r'\b', tk_desc, s)

    # Chuẩn hóa diễn giải phát sinh
    s = s.replace('CDTK_PhatSinhNo', 'Phát sinh Nợ')
    s = s.replace('CDTK_PhatSinhCo', 'Phát sinh Có')
    s = s.replace('Phát sinh NỢ', 'Phát sinh Nợ')
    s = s.replace('Phát sinh CÓ', 'Phát sinh Có')
    s = s.replace('Dư CÓ cuối kỳ', 'Số dư Có cuối kỳ')
    s = s.replace('Dư NỢ cuối kỳ', 'Số dư Nợ cuối kỳ')
    s = s.replace('Dư CÓ đầu kỳ', 'Số dư Có đầu kỳ')
    s = s.replace('Dư NỢ đầu kỳ', 'Số dư Nợ đầu kỳ')

    # Dọn dẹp khoảng trắng thừa và dấu ngoặc rác
    s = s.replace('ve B', 'Chỉ tiêu đối chiếu').replace('ve A', 'Chỉ tiêu kê khai')
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.strip('+-*/ ')
    return s


def la_canh_bao_rac(finding):
    """
    Kiểm tra xem một phát hiện rủi ro có phải là 'cảnh báo rác' không.
    Cảnh báo rác bao gồm:
    - Báo thiếu dữ liệu tờ khai / BCTC
    - Trạng thái 'CHƯA THỂ PHÂN TÍCH', 'THIẾU DỮ LIỆU', 'KHÔNG TÌM THẤY'
    - Thông điệp dạng nhắc nhở 'Vui lòng tải lên...' hoặc 'Chưa thỏa mãn...'
    - Chênh lệch = 0 hoặc rủi ro = False và kết quả số = 0
    - Các chênh lệch làm tròn siêu nhỏ (<= 10 đồng) khi KHÔNG có cờ rủi ro
    Tuyệt đối KHÔNG loại bỏ các chỉ số tỷ lệ tài chính hoặc rủi ro BCTC đã được xác nhận (is_rui_ro = True).
    """
    if not finding or not isinstance(finding, dict):
        return True

    trang_thai = str(finding.get('trang_thai', '')).upper()
    if any(k in trang_thai for k in ["CHƯA THỂ PHÂN TÍCH", "THIẾU DỮ LIỆU", "KHÔNG TÌM THẤY"]):
        return True

    thong_diep = str(finding.get('thong_diep', '')).strip()
    if any(thong_diep.startswith(p) for p in ["Vui lòng tải lên", "Thiếu dữ liệu", "Chưa có dữ liệu", "Hệ thống chưa đủ dữ liệu"]):
        return True
    if thong_diep.upper() in ["OK", "AN TOÀN", "KHÔNG CÓ RỦI RO"] or "chưa thỏa mãn điều kiện" in thong_diep.lower():
        return True

    raw_kq = finding.get('ket_qua_so', 0)
    if raw_kq in ["Thiếu dữ liệu", "---", "Chưa thể phân tích", None]:
        return True

    # 🟢 QUY TẮC VÀNG: Nếu là RỦI RO ĐÃ ĐƯỢC XÁC NHẬN (is_rui_ro = True) -> TUYỆT ĐỐI GIỮ LẠI!
    # Kể cả tỷ lệ tài chính nhỏ (ví dụ 0.15, 0.8, 1.2, 5.0) hoặc chỉ số rủi ro = 1/True
    if finding.get('is_rui_ro', False):
        return False

    try:
        val_so = float(str(raw_kq).replace(',', '').strip())
    except Exception:
        return True

    gia_tri_a = 0.0
    gia_tri_b = 0.0
    try:
        gia_tri_a = float(str(finding.get('gia_tri_a', 0)).replace(',', '').strip())
        gia_tri_b = float(str(finding.get('gia_tri_b', 0)).replace(',', '').strip())
    except Exception:
        pass

    # Nếu không phải rủi ro và cả 2 vế đều là 0
    if abs(val_so) < 1:
        if abs(gia_tri_a) < 1 and abs(gia_tri_b) < 1:
            return True
        return True

    # Loại bỏ chênh lệch làm tròn siêu nhỏ (ví dụ 2 đồng) khi không có rủi ro
    if abs(val_so) <= 10:
        return True

    return False


# DANH MỤC CĂN CỨ PHÁP LÝ CHUẨN TRONG THANH KIỂM TRA THUẾ
DANH_MUC_CAN_CU_PHAP_LY = [
    {
        "id": "LUAT_QLT",
        "ten": "Luật Quản lý thuế số 38/2019/QH14 ngày 13/6/2019 của Quốc hội",
        "mac_dinh": True
    },
    {
        "id": "LUAT_GTGT",
        "ten": "Luật Thuế Giá trị gia tăng và các văn bản hướng dẫn thi hành",
        "mac_dinh": True
    },
    {
        "id": "LUAT_TNDN",
        "ten": "Luật Thuế Thu nhập doanh nghiệp và các văn bản hướng dẫn thi hành",
        "mac_dinh": True
    },
    {
        "id": "ND_123",
        "ten": "Nghị định số 123/2020/NĐ-CP ngày 19/10/2020 của Chính phủ quy định về hóa đơn, chứng từ",
        "mac_dinh": True
    },
    {
        "id": "TT_80",
        "ten": "Thông tư số 80/2021/TT-BTC ngày 29/9/2021 của Bộ Tài chính hướng dẫn Luật Quản lý thuế",
        "mac_dinh": True
    },
    {
        "id": "TT_26",
        "ten": "Thông tư số 26/2015/TT-BTC ngày 27/02/2015 của Bộ Tài chính hướng dẫn thuế GTGT và quản lý thuế",
        "mac_dinh": False
    },
    {
        "id": "TT_78",
        "ten": "Thông tư số 78/2014/TT-BTC ngày 18/6/2014 của Bộ Tài chính hướng dẫn về thuế TNDN",
        "mac_dinh": False
    },
    {
        "id": "TT_200",
        "ten": "Thông tư số 200/2014/TT-BTC ngày 22/12/2014 của Bộ Tài chính hướng dẫn Chế độ kế toán doanh nghiệp",
        "mac_dinh": False
    },
    {
        "id": "QD_1161",
        "ten": "Quyết định số 1161/QĐ-CT ngày 14/8/2026 của Cục Thuế về việc ban hành Quy trình Kiểm tra thuế",
        "mac_dinh": True
    },
    {
        "id": "QD_970",
        "ten": "Quyết định số 970/QĐ-TCT ngày 14/7/2023 của Tổng cục Thuế về Quy trình kiểm tra thuế",
        "mac_dinh": False
    }
]


# BỘ THƯ VIỆN MẪU CÂU PHÂN TÍCH CHUẨN
DANH_SACH_MAU_CAU_CHUAN = [
    # -------------------------------------------------------------
    # 1. THUẾ TNDN VS THUẾ GTGT
    # -------------------------------------------------------------
    {
        "id": "TNDN_GTGT_01",
        "nhom": "Thuế TNDN",
        "tieu_de": "Doanh thu Quyết toán TNDN vs Tổng Doanh thu GTGT các kỳ",
        "mau_cau": "Doanh thu bán hàng và cung cấp dịch vụ trên tờ khai quyết toán thuế TNDN năm {nam} {so_tien_tndn} đồng đối chiếu với Tổng doanh thu của HHDV bán ra trên tờ khai thuế GTGT {so_ky_gtgt} năm {nam} {so_tien_gtgt} đồng, chênh lệch {chenh_lech} đồng. Đề nghị đơn vị giải trình nội dung này.",
        "can_cu": "Luật Thuế TNDN, Thông tư 78/2014/TT-BTC, Thông tư 80/2021/TT-BTC",
        "yeu_cau": "Giải trình nguyên nhân chênh lệch giữa doanh thu tính thuế TNDN và doanh thu tính thuế GTGT."
    },
    {
        "id": "GTGT_PHU_LUC_03_1A",
        "nhom": "Thuế TNDN",
        "tieu_de": "Doanh thu GTGT vs Phụ lục 03-1A/TNDN (Bán hàng + Thu nhập khác)",
        "mau_cau": "Tổng doanh thu của HHDV bán ra trên tờ khai thuế GTGT năm {nam} là {so_tien_gtgt} đồng. Đối chiếu Tổng Doanh thu bán hàng hóa và cung cấp dịch vụ và Thu nhập khác trên phụ lục 03-1A/TNDN kèm theo Tờ khai quyết toán thuế TNDN năm {nam} là {so_tien_tndn} đồng (={dt_ban_hang} đồng + {thu_nhap_khac} đồng), chênh lệch {chenh_lech} đồng. Đề nghị đơn vị giải trình nội dung chênh lệch này, đồng thời làm rõ khoản thu nhập khác từ hoạt động nào?",
        "can_cu": "Thông tư số 78/2014/TT-BTC Điều 5 và Điều 7 quy định về Doanh thu và Thu nhập khác tính thuế TNDN",
        "yeu_cau": "Giải trình nội dung chênh lệch, làm rõ khoản thu nhập khác từ hoạt động nào và cung cấp chứng từ liên quan."
    },
    {
        "id": "TNDN_DOANH_THU_VS_TK511",
        "nhom": "Thuế TNDN",
        "tieu_de": "Đối chiếu Doanh thu Quyết toán TNDN và Doanh thu TK 511",
        "mau_cau": "Doanh thu trên tờ khai quyết toán thuế TNDN năm {nam} là {so_tien_tndn} đồng đối chiếu với Phát sinh Có TK 511 - Doanh thu bán hàng và cung cấp dịch vụ trên BCTC là {ps_co_511} đồng, chênh lệch {chenh_lech} đồng. Đề nghị đơn vị giải trình nguyên nhân chênh lệch giữa doanh thu kế toán và doanh thu tính thuế.",
        "can_cu": "Thông tư số 200/2014/TT-BTC và Thông tư số 78/2014/TT-BTC",
        "yeu_cau": "Giải trình nguyên nhân chênh lệch giữa doanh thu hạch toán kế toán và doanh thu kê khai tính thuế TNDN."
    },
    {
        "id": "TNDN_BCTC_01",
        "nhom": "Thuế TNDN",
        "tieu_de": "Doanh thu Báo cáo tài chính (BCKQKD) vs Doanh thu Quyết toán TNDN",
        "mau_cau": "Doanh thu bán hàng và cung cấp dịch vụ trên Báo cáo kết quả hoạt động kinh doanh (BCTC) năm {nam} là {dt_bctc} đồng, đối chiếu với Doanh thu trên Tờ khai quyết toán thuế TNDN {dt_tndn} đồng, chênh lệch {chenh_lech} đồng. Đề nghị đơn vị giải trình nguyên nhân có sự khác biệt giữa doanh thu kế toán và doanh thu tính thuế.",
        "can_cu": "Thông tư số 200/2014/TT-BTC và Thông tư số 78/2014/TT-BTC",
        "yeu_cau": "Giải trình nguyên nhân chênh lệch giữa doanh thu kế toán và doanh thu tính thuế TNDN."
    },

    # -------------------------------------------------------------
    # 2. BÁO CÁO TÀI CHÍNH / BẢNG CÂN ĐỐI KẾ TOÁN & CÂN ĐỐI TÀI KHOẢN
    # -------------------------------------------------------------
    {
        "id": "BCTC_131_PHAI_THU",
        "nhom": "Báo cáo Tài chính",
        "tieu_de": "Số dư Chỉ tiêu 131 - Phải thu ngắn hạn khách hàng lớn",
        "mau_cau": "Trên bảng cân đối kế toán năm {nam}, phát sinh chỉ tiêu 131- Phải thu ngắn hạn của khách hàng {so_tien_131} đồng. Đề nghị công ty giải trình chi tiết nội dung này, cung cấp danh sách chi tiết các khách hàng có số dư lớn và biên bản đối chiếu công nợ tại thời điểm kết thúc năm tài chính.",
        "can_cu": "Chuẩn mực Kế toán số 01, Thông tư số 200/2014/TT-BTC",
        "yeu_cau": "Giải trình chi tiết số dư nợ phải thu, cung cấp biên bản đối chiếu công nợ và tình hình thu hồi nợ."
    },
    {
        "id": "CDSPS_NO_131_CO_511_3331",
        "nhom": "Báo cáo Tài chính",
        "tieu_de": "Đối chiếu Phát sinh Nợ TK 131 vs Phát sinh Có TK 511 + Có TK 3331",
        "mau_cau": "Trên Bảng cân đối tài khoản, Báo cáo tài chính năm {nam} có số phát sinh Nợ TK 131-Phải thu của khách hàng {ps_no_131} đồng, đối chiếu với Tổng số phát sinh Có TK 511-Doanh thu bán hàng và cung cấp dịch vụ {ps_co_511} đồng và số phát sinh Có TK 3331-Thuế giá trị gia tăng phải nộp {ps_co_3331} đồng chênh lệch {chenh_lech} đồng. Đề nghị đơn vị giải trình chi tiết nội dung chênh lệch này.",
        "can_cu": "Thông tư số 200/2014/TT-BTC và Nghị định số 123/2020/NĐ-CP",
        "yeu_cau": "Giải trình chi tiết nội dung chênh lệch đối ứng Nợ 131 và Có 511, 3331 (làm rõ các khoản thu tiền trước, hàng trả lại, giảm giá hoặc doanh thu chưa thực hiện)."
    },
    {
        "id": "BCTC_131_VS_TK_GTGT",
        "nhom": "Báo cáo Tài chính",
        "tieu_de": "Đối chiếu Phải thu của khách hàng và Doanh thu trên tờ khai GTGT",
        "mau_cau": "Số phát sinh Nợ TK 131 - Phải thu của khách hàng năm {nam} là {ps_no_131} đồng đối chiếu với Tổng doanh thu trên tờ khai thuế GTGT là {dt_gtgt} đồng, chênh lệch {chenh_lech} đồng. Đề nghị đơn vị giải trình làm rõ nguyên nhân chênh lệch.",
        "can_cu": "Thông tư số 200/2014/TT-BTC và Thông tư số 219/2013/TT-BTC",
        "yeu_cau": "Giải trình nguyên nhân chênh lệch giữa số phát sinh phải thu khách hàng và doanh thu kê khai thuế GTGT."
    },
    {
        "id": "BCTC_131_DU_CO",
        "nhom": "Báo cáo Tài chính",
        "tieu_de": "Kiểm tra số dư Có TK 131 - Khách hàng ứng trước tiền hàng",
        "mau_cau": "Trên Báo cáo tài chính năm {nam}, phát sinh số dư Có TK 131 - Khách hàng trả tiền trước là {so_tien_du_co} đồng. Đề nghị đơn vị giải trình chi tiết các khoản khách hàng ứng trước tiền hàng, làm rõ đã xuất hóa đơn và kê khai thuế GTGT theo thời điểm nhận tiền theo quy định tại Điều 9 Nghị định 123/2020/NĐ-CP hay chưa.",
        "can_cu": "Nghị định số 123/2020/NĐ-CP Điều 9 và Thông tư số 200/2014/TT-BTC",
        "yeu_cau": "Cung cấp danh mục khách hàng ứng trước tiền hàng, hợp đồng kinh tế và giải trình thời điểm xuất hóa đơn."
    },
    {
        "id": "BCTC_211_TANG_GIAM",
        "nhom": "Báo cáo Tài chính",
        "tieu_de": "Kiểm tra tăng/giảm TSCĐ hữu hình (TK 211)",
        "mau_cau": "Trên BCTC năm {nam} phát sinh tăng/giảm TSCĐ hữu hình (TK 211) là {so_tien_tscd} đồng. Đề nghị công ty giải trình chi tiết tình hình tăng giảm TSCĐ, cung cấp hồ sơ mua sắm, biên bản nghiệm thu đưa vào sử dụng và đăng ký phương pháp trích khấu hao.",
        "can_cu": "Thông tư số 45/2013/TT-BTC ngày 25/4/2013 của Bộ Tài chính hướng dẫn chế độ quản lý, trích khấu hao TSCĐ",
        "yeu_cau": "Cung cấp hồ sơ mua sắm TSCĐ, hóa đơn chứng từ, biên bản bàn giao nghiệm thu đưa vào sử dụng."
    },
    {
        "id": "BCTC_214_KHAU_HAO",
        "nhom": "Báo cáo Tài chính",
        "tieu_de": "Kiểm tra trích khấu hao tài sản cố định (TK 214)",
        "mau_cau": "Trên BCTC năm {nam} phát sinh chi phí khấu hao TSCĐ (TK 214) là {so_tien_khau_hao} đồng. Đề nghị công ty cung cấp bảng tính khấu hao TSCĐ, giải trình nguyên tắc trích khấu hao theo Thông tư 45/2013/TT-BTC và việc trích khấu hao các tài sản không phục vụ hoạt động SXKD (nếu có).",
        "can_cu": "Thông tư số 45/2013/TT-BTC và Thông tư số 78/2014/TT-BTC",
        "yeu_cau": "Cung cấp bảng phân bổ khấu hao TSCĐ chi tiết cho từng bộ phận sản xuất, bán hàng và quản lý."
    },
    {
        "id": "BCTC_331_DU_CO",
        "nhom": "Báo cáo Tài chính",
        "tieu_de": "Kiểm tra số dư Có TK 331 - Phải trả người bán",
        "mau_cau": "Trên BCTC năm {nam} ghi nhận số dư Có TK 331 - Phải trả cho người bán là {so_tien_331} đồng. Đề nghị đơn vị giải trình chi tiết các khoản nợ phải trả, cung cấp biên bản đối chiếu công nợ cuối năm và hợp đồng kinh tế liên quan.",
        "can_cu": "Chuẩn mực Kế toán số 01 và Thông tư số 200/2014/TT-BTC",
        "yeu_cau": "Cung cấp sổ chi tiết công nợ phải trả theo từng nhà cung cấp và biên bản xác nhận công nợ."
    },
    {
        "id": "BCTC_331_VS_MUA_VAO_GTGT",
        "nhom": "Báo cáo Tài chính",
        "tieu_de": "Đối chiếu TK 331 với Tổng doanh số mua vào đã có thuế GTGT",
        "mau_cau": "Đối chiếu số phát sinh TK 331 (Phải trả người bán) {ps_331} đồng với Tổng doanh số mua vào đã có thuế GTGT trên tờ khai thuế {tong_mua_vao} đồng năm {nam}, chênh lệch {chenh_lech} đồng. Đề nghị đơn vị giải trình nguyên nhân chênh lệch giữa công nợ mua vào và số liệu kê khai thuế.",
        "can_cu": "Thông tư số 219/2013/TT-BTC và Thông tư số 200/2014/TT-BTC",
        "yeu_cau": "Lập bảng đối chiếu chi tiết giữa phát sinh Có TK 331 với hóa đơn mua vào kê khai trên tờ khai GTGT."
    },
    {
        "id": "BCTC_152_VS_621",
        "nhom": "Báo cáo Tài chính",
        "tieu_de": "Đối chiếu TK 152 (Nguyên vật liệu) và TK 621 (Chi phí NVL trực tiếp)",
        "mau_cau": "Trên Báo cáo tài chính năm {nam}, đối chiếu số liệu phát sinh giữa TK 152 (Nguyên vật liệu) {ps_152} đồng và TK 621 (Chi phí NVL trực tiếp) {ps_621} đồng chênh lệch {chenh_lech} đồng. Đề nghị đơn vị cung cấp bảng định mức tiêu hao nguyên vật liệu và giải trình tính hợp lý của chi phí NVL đưa vào sản xuất.",
        "can_cu": "Thông tư số 78/2014/TT-BTC và Thông tư số 200/2014/TT-BTC",
        "yeu_cau": "Cung cấp bảng định mức tiêu hao nguyên vật liệu, phiếu xuất kho và thẻ tính giá thành sản phẩm."
    },
    {
        "id": "BCTC_154_GIA_THANH",
        "nhom": "Báo cáo Tài chính",
        "tieu_de": "Đối chiếu tập hợp chi phí giá thành (TK 154 vs TK 621, 622, 623, 627)",
        "mau_cau": "Đối chiếu số liệu tập hợp chi phí giá thành năm {nam}: Phát sinh Có TK 154 nhập kho thành phẩm {ps_154} đồng đối chiếu với tổng chi phí sản xuất phát sinh trong kỳ {ps_chi_phi} đồng, chênh lệch {chenh_lech} đồng. Đề nghị đơn vị giải trình quy trình tính giá thành sản phẩm và cung cấp thẻ tính giá thành chi tiết.",
        "can_cu": "Thông tư số 200/2014/TT-BTC về phương pháp tính giá thành sản phẩm",
        "yeu_cau": "Giải trình quy trình tính giá thành, cung cấp báo cáo tổng hợp chi phí sản xuất và thẻ tính giá thành."
    },
    {
        "id": "BCTC_3388_PHAI_TRA_KHAC",
        "nhom": "Báo cáo Tài chính",
        "tieu_de": "Kiểm tra Tài khoản 3388 - Phải trả, phải nộp khác",
        "mau_cau": "Trên Báo cáo tài chính năm {nam}, chỉ tiêu TK 3388 - Phải trả, phải nộp khác ghi nhận số dư {so_tien_3388} đồng. Đề nghị đơn vị giải trình chi tiết nội dung các khoản phải trả khác, làm rõ có liên quan đến doanh thu tính thuế hoặc chi phí không được trừ hay không.",
        "can_cu": "Thông tư số 200/2014/TT-BTC và Luật Quản lý thuế số 38/2019/QH14",
        "yeu_cau": "Cung cấp bảng kê chi tiết các khoản công nợ theo dõi trên TK 3388 và chứng từ phát sinh liên quan."
    },
    {
        "id": "BCTC_111_112_TIEN_MAT",
        "nhom": "Báo cáo Tài chính",
        "tieu_de": "Tồn quỹ Tiền mặt (TK 111) lớn bất thường trong khi có vay vốn",
        "mau_cau": "Trên Bảng cân đối kế toán năm {nam}, chỉ tiêu Tiền mặt tồn quỹ ghi nhận số dư {so_tien_tien_mat} đồng, trong khi đơn vị phát sinh chi phí lãi vay {chi_phi_lai_vay} đồng. Đề nghị đơn vị giải trình tính hợp lý của việc duy trì quỹ tiền mặt tồn lớn nhưng vẫn đi vay vốn kinh doanh tính vào chi phí được trừ.",
        "can_cu": "Thông tư số 78/2014/TT-BTC Điều 6 Khoản 2 Điểm 2.18",
        "yeu_cau": "Làm rõ mục đích tồn quỹ tiền mặt và giải trình tính hợp lệ của chi phí lãi vay."
    },
    {
        "id": "BCTC_HANG_TON_KHO_BAN_KHONG_XUAT_HD",
        "nhom": "Báo cáo Tài chính",
        "tieu_de": "Rủi ro Bán hàng không xuất hóa đơn (Hàng tồn kho tồn lớn)",
        "mau_cau": "Qua phân tích hồ sơ khai thuế và Báo cáo tài chính năm {nam}, ghi nhận chỉ tiêu Hàng tồn kho (TK 152, 155, 156) có số dư tồn kho lớn, tiềm ẩn rủi ro về việc xuất bán hàng nhưng không lập hóa đơn, không kê khai doanh thu tính thuế GTGT và thuế TNDN. Đề nghị đơn vị giải trình chi tiết cơ cấu hàng tồn kho, cung cấp biên bản kiểm kê và chứng từ chứng minh tính có thực của hàng tồn kho.",
        "can_cu": "Nghị định số 123/2020/NĐ-CP và Luật Quản lý thuế số 38/2019/QH14",
        "yeu_cau": "Cung cấp biên bản kiểm kê hàng tồn kho tại thời điểm 31/12 và bảng tổng hợp nhập - xuất - tồn chi tiết."
    },
    {
        "id": "BCTC_GIAU_DOANH_THU_UNG_TRUOC",
        "nhom": "Báo cáo Tài chính",
        "tieu_de": "Giấu Doanh thu qua Khoản Nhận ứng trước Khách hàng",
        "mau_cau": "Qua rà soát Báo cáo tài chính năm {nam}, ghi nhận biến động hàng tồn kho và số dư nhận tiền ứng trước của khách hàng (TK 131) phát sinh {so_tien} đồng. Đề nghị đơn vị giải trình làm rõ: đơn vị đã thu tiền ứng trước của khách hàng, hàng hóa/dịch vụ đã hoàn thành hoặc giao cho khách hàng nhưng chưa xuất hóa đơn GTGT và hoãn kê khai doanh thu hay chưa.",
        "can_cu": "Điều 9 Nghị định số 123/2020/NĐ-CP và Thông tư số 200/2014/TT-BTC",
        "yeu_cau": "Cung cấp bảng kê chi tiết các khoản khách hàng trả tiền trước, biên bản giao nhận hàng hóa và thời điểm phát sinh nghĩa vụ thuế."
    },
    {
        "id": "TY_LE_DOANH_THU_BIEN_DONG_DOT_BIEN",
        "nhom": "Phân tích tỷ lệ",
        "tieu_de": "Biến động Doanh thu trên tờ khai tăng/giảm đột biến",
        "mau_cau": "Qua phân tích chỉ tiêu Doanh thu bán ra trên tờ khai thuế GTGT năm {nam} so với kỳ trước, ghi nhận mức biến động {ty_le}% (tăng/giảm từ 20% trở lên). Đề nghị đơn vị giải trình nguyên nhân biến động đột biến của doanh thu hoạt động sản xuất kinh doanh.",
        "can_cu": "Quy trình Kiểm tra thuế theo Quyết định số 1161/QĐ-CT và Bộ tiêu chí rủi ro của Tổng cục Thuế",
        "yeu_cau": "Giải trình nguyên nhân biến động doanh thu và các yếu tố thị trường hoặc năng lực sản xuất kinh doanh tác động."
    },

    # -------------------------------------------------------------
    # 3. THUẾ GIÁ TRỊ GIA TĂNG (GTGT) & TỜ KHAI BỔ SUNG (KHBS)
    # -------------------------------------------------------------
    {
        "id": "GTGT_DOANH_THU_KCT_PHAN_BO",
        "nhom": "Thuế GTGT",
        "tieu_de": "Phát sinh Doanh thu không chịu thuế GTGT - Yêu cầu phân bổ thuế đầu vào",
        "mau_cau": "Tờ khai thuế GTGT năm {nam} phát sinh Doanh thu không chịu thuế GTGT {so_tien_kct} đồng. Đề nghị đơn vị giải trình đã thực hiện phân bổ thuế GTGT đầu vào được khấu trừ theo quy định tại điểm a, khoản 9, Điều 1, Thông tư 26/2015/TT-BTC ngày 27/02/2015 của Bộ Tài chính hay chưa? Đã giải trình rõ và cung cấp bảng tính phân bổ số thuế GTGT đầu vào dùng chung cho hoạt động chịu thuế và không chịu thuế.",
        "can_cu": "Điểm a, Khoản 9, Điều 1, Thông tư số 26/2015/TT-BTC ngày 27/02/2015 của Bộ Tài chính",
        "yeu_cau": "Cung cấp bảng phân bổ thuế GTGT đầu vào được khấu trừ của từng kỳ và quyết toán năm."
    },
    {
        "id": "GTGT_KHBS_DIEU_CHINH_GIAM",
        "nhom": "Thuế GTGT",
        "tieu_de": "Tờ khai bổ sung KHBS điều chỉnh giảm thuế GTGT khấu trừ",
        "mau_cau": "Trên tờ khai thuế GTGT bổ sung lần {lan_bs} kỳ {ky} nộp ngày {ngay_nop}, đơn vị kê khai tại chỉ tiêu điều chỉnh giảm thuế GTGT còn được khấu trừ là {so_tien_giam} đồng. Đề nghị đơn vị giải trình nội dung kê khai điều chỉnh bổ sung, nguyên nhân sai sót của kỳ gốc và việc kê khai chỉ tiêu [37] trên tờ khai của kỳ phát hiện sai sót.",
        "can_cu": "Điều 47 Luật Quản lý thuế số 38/2019/QH14 và Thông tư số 80/2021/TT-BTC",
        "yeu_cau": "Giải trình nguyên nhân sai sót dẫn đến kê khai bổ sung và chứng minh việc chuyển số thuế điều chỉnh vào kỳ hiện tại."
    },
    {
        "id": "GTGT_KHBS_TANG_THUE_NOP",
        "nhom": "Thuế GTGT",
        "tieu_de": "Tờ khai bổ sung KHBS làm tăng số thuế phải nộp",
        "mau_cau": "Tại tờ khai thuế GTGT bổ sung lần {lan_bs} kỳ {ky} nộp ngày {ngay_nop}, đơn vị kê khai làm tăng số thuế GTGT phải nộp là {so_tien_tang} đồng. Đề nghị đơn vị cung cấp chứng từ nộp số tiền thuế tăng thêm vào NSNN và chứng từ nộp tiền chậm nộp theo quy định.",
        "can_cu": "Điều 59 Luật Quản lý thuế số 38/2019/QH14 về xử lý tiền chậm nộp",
        "yeu_cau": "Cung cấp giấy nộp tiền vào NSNN và bảng tính tiền chậm nộp."
    },

    # -------------------------------------------------------------
    # 4. ĐỐI CHIẾU HÓA ĐƠN ĐIỆN TỬ VÀ TỜ KHAI
    # -------------------------------------------------------------
    {
        "id": "HD_BAN_RA_VS_TK_GTGT",
        "nhom": "Hóa đơn Điện tử",
        "tieu_de": "Đối chiếu Hóa đơn Điện tử Bán ra vs Doanh thu Tờ khai GTGT",
        "mau_cau": "Đối chiếu dữ liệu hóa đơn điện tử bán ra ({tong_hd_br} đồng chưa thuế, thuế GTGT {thue_hd_br} đồng) với Doanh thu và thuế GTGT trên hồ sơ khai thuế ({tong_tk_br} đồng doanh thu, thuế GTGT {thue_tk_br} đồng) năm {nam}, chênh lệch giá trị chưa thuế {chenh_lech_gt} đồng, chênh lệch thuế GTGT {chenh_lech_thue} đồng. Đề nghị đơn vị rà soát đối chiếu và giải trình nguyên nhân chênh lệch.",
        "can_cu": "Nghị định số 123/2020/NĐ-CP và Thông tư số 78/2021/TT-BTC",
        "yeu_cau": "Giải trình nguyên nhân chênh lệch giữa hóa đơn bán ra đã xuất và số liệu kê khai trên tờ khai GTGT."
    },
    {
        "id": "HD_MUA_VAO_VS_TK_GTGT",
        "nhom": "Hóa đơn Điện tử",
        "tieu_de": "Đối chiếu Hóa đơn Điện tử Mua vào vs Tờ khai GTGT",
        "mau_cau": "Đối chiếu dữ liệu hóa đơn điện tử mua vào ({tong_hd_mv} đồng giá trị chưa thuế, thuế GTGT {thue_hd_mv} đồng) với Giá trị và thuế GTGT đầu vào trên tờ khai thuế GTGT ({tong_tk_mv} đồng giá trị, thuế GTGT {thue_tk_mv} đồng) năm {nam}, chênh lệch {chenh_lech} đồng. Đề nghị đơn vị giải trình nguyên nhân chênh lệch, làm rõ các hóa đơn đầu vào chưa kê khai hoặc kê khai trùng lặp.",
        "can_cu": "Thông tư số 219/2013/TT-BTC Điều 15 về điều kiện khấu trừ thuế GTGT đầu vào",
        "yeu_cau": "Lập bảng đối chiếu danh sách hóa đơn mua vào chưa kê khai hoặc có chênh lệch."
    },
    {
        "id": "HD_RUI_RO_BO_DIA_CHI",
        "nhom": "Hóa đơn Rủi ro",
        "tieu_de": "Hóa đơn mua từ Doanh nghiệp bỏ địa chỉ / Cảnh báo rủi ro",
        "mau_cau": "Qua rà soát dữ liệu hóa đơn mua vào, phát hiện đơn vị có sử dụng {so_luong_hd} số hóa đơn với tổng tiền chưa thuế {tong_tien} đồng (thuế GTGT {tien_thue} đồng) của {so_luong_dn} doanh nghiệp có trạng thái 'Người nộp thuế không hoạt động tại địa chỉ đã đăng ký' hoặc thuộc danh sách cảnh báo rủi ro về hóa đơn của cơ quan thuế (gồm các MST: {danh_sach_mst}). Đề nghị đơn vị giải trình tính có thực của các giao dịch mua bán, cung cấp toàn bộ hồ sơ hợp đồng kinh tế, chứng từ vận chuyển, biên bản bàn giao và chứng từ thanh toán không dùng tiền mặt.",
        "can_cu": "Luật Quản lý thuế số 38/2019/QH14 và các công văn chỉ đạo về hóa đơn rủi ro của Tổng cục Thuế",
        "yeu_cau": "Cung cấp toàn bộ hồ sơ chứng minh tính có thực của hàng hóa dịch vụ mua vào từ các doanh nghiệp rủi ro."
    },

    # -------------------------------------------------------------
    # 5. CÔNG THỨC SO SÁNH TỔNG QUÁT (KHÔNG DÙNG VẾ A/B)
    # -------------------------------------------------------------
    {
        "id": "QUY_TAC_CHUNG_AB",
        "nhom": "Quy tắc Chung",
        "tieu_de": "Đối chiếu so sánh hai chỉ tiêu",
        "mau_cau": "Đối chiếu {ten_chi_tieu_a} số tiền {val_a} đồng với {ten_chi_tieu_b} số tiền {val_b} đồng năm {nam}, chênh lệch {chenh_lech} đồng. Đề nghị đơn vị rà soát và giải trình làm rõ nguyên nhân chênh lệch này.",
        "can_cu": "Quy trình Kiểm tra thuế và các văn bản quy phạm pháp luật thuế hiện hành",
        "yeu_cau": "Giải trình nguyên nhân chênh lệch và cung cấp tài liệu chứng từ có liên quan."
    },
    {
        "id": "QUY_TAC_DON",
        "nhom": "Quy tắc Chung",
        "tieu_de": "Cảnh báo chỉ tiêu phát sinh bất thường",
        "mau_cau": "Qua rà soát hồ sơ khai thuế năm {nam}, phát hiện {ten_chi_tieu_a} phát sinh số tiền {val_a} đồng. Đề nghị đơn vị kiểm tra lại và giải trình chi tiết: {thong_diep}",
        "can_cu": "Quy trình Kiểm tra thuế theo Quyết định số 1161/QĐ-CT",
        "yeu_cau": "Giải trình căn cứ số liệu kê khai bất thường và cung cấp hồ sơ chứng từ minh chứng."
    }
]


class ThuVienMauCau:
    """Bộ máy quản lý và tự động hóa sinh mẫu câu diễn giải"""

    def __init__(self):
        self.danh_sach_mau = list(DANH_SACH_MAU_CAU_CHUAN)
        self.file_custom = "Data/custom_mau_cau.json"
        self._tai_mau_custom()

    def _tai_mau_custom(self):
        if os.path.exists(self.file_custom):
            try:
                with open(self.file_custom, 'r', encoding='utf-8') as f:
                    custom = json.load(f)
                    if isinstance(custom, list):
                        self.danh_sach_mau.extend(custom)
            except Exception:
                pass

    def lay_danh_sach(self):
        return self.danh_sach_mau

    def lay_mau_theo_id(self, mau_id):
        for m in self.danh_sach_mau:
            if m.get("id") == mau_id:
                return m
        return None

    def tu_dong_sinh_cau(self, rui_ro_dict, nam="2025", he_thong_data=None):
        """
        Dựa trên một item rủi ro từ Engine phân tích, tự động nhận diện
        và lắp ráp vào mẫu câu phù hợp nhất với đầy đủ số liệu thực tế.
        Tuyệt đối KHÔNG xuất hiện các từ 'Vế A' hoặc 'Vế B'.
        """
        ten_loi = str(rui_ro_dict.get('ten_phan_tich', '')).strip()
        nhom = str(rui_ro_dict.get('nhom', 'Khác')).strip()
        thong_diep = str(rui_ro_dict.get('thong_diep', '')).strip()

        # Số liệu cơ bản
        val_a = format_tien(rui_ro_dict.get('gia_tri_a', 0))
        val_b = format_tien(rui_ro_dict.get('gia_tri_b', 0))

        try:
            so_kq = float(rui_ro_dict.get('ket_qua_so', 0))
        except Exception:
            so_kq = 0
        chenh_lech = format_tien(abs(so_kq))

        # Phiên dịch tên chỉ tiêu chuẩn (Xóa sổ hoàn toàn Vế A / Vế B)
        raw_a = rui_ro_dict.get('ve_a_goc') or rui_ro_dict.get('ten_ve_a', '')
        raw_b = rui_ro_dict.get('ve_b_goc') or rui_ro_dict.get('ten_ve_b', '')
        ten_chi_tieu_a = dich_ten_chi_tieu(raw_a, rui_ro_dict=rui_ro_dict, is_ve_b=False)
        ten_chi_tieu_b = dich_ten_chi_tieu(raw_b, rui_ro_dict=rui_ro_dict, is_ve_b=True)

        ten_lower = (ten_loi + " " + nhom).lower()

        # -----------------------------------------------------------------
        # 1. NHẬN DIỆN: Doanh thu Quyết toán TNDN vs TK 511
        # -----------------------------------------------------------------
        if ("tndn" in ten_lower and "511" in ten_lower) or ("doanh thu quyết toán tndn và tk 511" in ten_lower):
            mau = self.lay_mau_theo_id("TNDN_DOANH_THU_VS_TK511")
            text = mau["mau_cau"].format(
                nam=nam,
                so_tien_tndn=val_a,
                ps_co_511=val_b,
                chenh_lech=chenh_lech
            )
            return {
                "mau_id": "TNDN_DOANH_THU_VS_TK511",
                "tieu_de": "Đối chiếu Doanh thu Quyết toán TNDN và TK 511",
                "nhom": "Thuế TNDN",
                "cau_van": text,
                "can_cu": mau["can_cu"],
                "yeu_cau": mau["yeu_cau"],
                "du_lieu_goc": rui_ro_dict
            }

        # -----------------------------------------------------------------
        # 2. NHẬN DIỆN: Doanh thu TNDN vs GTGT
        # -----------------------------------------------------------------
        if ("doanh thu" in ten_lower and ("tndn" in ten_lower or "03/tndn" in ten_lower) and "gtgt" in ten_lower) or \
           ("tndn" in ten_lower and "gtgt" in ten_lower and "chênh lệch" in ten_lower) or \
           ("so sánh doanh thu tính thuế tndn và doanh thu kê khai thuế gtgt" in ten_lower):
            if "phụ lục" in ten_lower or "03-1a" in ten_lower or "thu nhập khác" in ten_lower:
                mau = self.lay_mau_theo_id("GTGT_PHU_LUC_03_1A")
                text = mau["mau_cau"].format(
                    nam=nam,
                    so_tien_gtgt=val_b if val_b != "0" else val_a,
                    so_tien_tndn=val_a if val_b != "0" else val_b,
                    dt_ban_hang=val_a,
                    thu_nhap_khac=chenh_lech,
                    chenh_lech=chenh_lech
                )
                return {
                    "mau_id": "GTGT_PHU_LUC_03_1A",
                    "tieu_de": "Chênh lệch Doanh thu GTGT và Phụ lục 03-1A/TNDN",
                    "nhom": "Thuế TNDN",
                    "cau_van": text,
                    "can_cu": mau["can_cu"],
                    "yeu_cau": mau["yeu_cau"],
                    "du_lieu_goc": rui_ro_dict
                }
            else:
                mau = self.lay_mau_theo_id("TNDN_GTGT_01")
                text = mau["mau_cau"].format(
                    nam=nam,
                    so_tien_tndn=val_a,
                    so_ky_gtgt="các kỳ trong",
                    so_tien_gtgt=val_b,
                    chenh_lech=chenh_lech
                )
                return {
                    "mau_id": "TNDN_GTGT_01",
                    "tieu_de": "Chênh lệch Doanh thu Quyết toán TNDN vs Tờ khai GTGT",
                    "nhom": "Thuế TNDN",
                    "cau_van": text,
                    "can_cu": mau["can_cu"],
                    "yeu_cau": mau["yeu_cau"],
                    "du_lieu_goc": rui_ro_dict
                }

        # -----------------------------------------------------------------
        # 3. NHẬN DIỆN: BCTC Chỉ tiêu 131 - Phải thu khách hàng
        # -----------------------------------------------------------------
        if "131" in ten_lower or ("phải thu" in ten_lower and ("khách hàng" in ten_lower or "gtgt" in ten_lower)):
            if "511" in ten_lower or "3331" in ten_lower:
                mau = self.lay_mau_theo_id("CDSPS_NO_131_CO_511_3331")
                text = mau["mau_cau"].format(
                    nam=nam,
                    ps_no_131=val_a,
                    ps_co_511=val_b,
                    ps_co_3331=format_tien(rui_ro_dict.get('thue_gtgt_lien_quan', 0)),
                    chenh_lech=chenh_lech
                )
                return {
                    "mau_id": "CDSPS_NO_131_CO_511_3331",
                    "tieu_de": "Đối chiếu Nợ 131 vs Có 511 + Có 3331",
                    "nhom": "Báo cáo Tài chính",
                    "cau_van": text,
                    "can_cu": mau["can_cu"],
                    "yeu_cau": mau["yeu_cau"],
                    "du_lieu_goc": rui_ro_dict
                }
            elif "doanh thu trên tờ khai gtgt" in ten_lower or ("phải thu" in ten_lower and "gtgt" in ten_lower) or ("131" in ten_lower and "gtgt" in ten_lower):
                mau = self.lay_mau_theo_id("BCTC_131_VS_TK_GTGT")
                text = mau["mau_cau"].format(
                    nam=nam,
                    ps_no_131=val_a,
                    dt_gtgt=val_b,
                    chenh_lech=chenh_lech
                )
                return {
                    "mau_id": "BCTC_131_VS_TK_GTGT",
                    "tieu_de": "Đối chiếu Phải thu 131 vs Doanh thu Tờ khai GTGT",
                    "nhom": "Báo cáo Tài chính",
                    "cau_van": text,
                    "can_cu": mau["can_cu"],
                    "yeu_cau": mau["yeu_cau"],
                    "du_lieu_goc": rui_ro_dict
                }
            elif "dư có" in ten_lower or "số dư có" in ten_lower:
                mau = self.lay_mau_theo_id("BCTC_131_DU_CO")
                text = mau["mau_cau"].format(
                    nam=nam,
                    so_tien_du_co=val_a
                )
                return {
                    "mau_id": "BCTC_131_DU_CO",
                    "tieu_de": "Kiểm tra Số dư Có TK 131 (Khách hàng trả trước)",
                    "nhom": "Báo cáo Tài chính",
                    "cau_van": text,
                    "can_cu": mau["can_cu"],
                    "yeu_cau": mau["yeu_cau"],
                    "du_lieu_goc": rui_ro_dict
                }
            elif "phải thu" in ten_lower or "chỉ tiêu" in ten_lower or "bảng cân đối" in ten_lower:
                mau = self.lay_mau_theo_id("BCTC_131_PHAI_THU")
                text = mau["mau_cau"].format(
                    nam=nam,
                    so_tien_131=val_a
                )
                return {
                    "mau_id": "BCTC_131_PHAI_THU",
                    "tieu_de": "Phát sinh số dư Chỉ tiêu 131 - Phải thu khách hàng lớn",
                    "nhom": "Báo cáo Tài chính",
                    "cau_van": text,
                    "can_cu": mau["can_cu"],
                    "yeu_cau": mau["yeu_cau"],
                    "du_lieu_goc": rui_ro_dict
                }

        # -----------------------------------------------------------------
        # 4. NHẬN DIỆN: Khấu hao (TK 214) & TSCĐ (TK 211)
        # (Ưu tiên kiểm tra TK 214 / khấu hao trước để tránh nhầm sang TK 211)
        # -----------------------------------------------------------------
        if "214" in ten_lower or "khấu hao" in ten_lower or "hao mòn" in ten_lower:
            mau = self.lay_mau_theo_id("BCTC_214_KHAU_HAO")
            text = mau["mau_cau"].format(
                nam=nam,
                so_tien_khau_hao=val_a
            )
            return {
                "mau_id": "BCTC_214_KHAU_HAO",
                "tieu_de": "Kiểm tra trích khấu hao TSCĐ (TK 214)",
                "nhom": "Báo cáo Tài chính",
                "cau_van": text,
                "can_cu": mau["can_cu"],
                "yeu_cau": mau["yeu_cau"],
                "du_lieu_goc": rui_ro_dict
            }

        if "211" in ten_lower or "tài sản cố định" in ten_lower:
            mau = self.lay_mau_theo_id("BCTC_211_TANG_GIAM")
            text = mau["mau_cau"].format(
                nam=nam,
                so_tien_tscd=val_a
            )
            return {
                "mau_id": "BCTC_211_TANG_GIAM",
                "tieu_de": "Kiểm tra biến động TSCĐ hữu hình (TK 211)",
                "nhom": "Báo cáo Tài chính",
                "cau_van": text,
                "can_cu": mau["can_cu"],
                "yeu_cau": mau["yeu_cau"],
                "du_lieu_goc": rui_ro_dict
            }

        # -----------------------------------------------------------------
        # 5. NHẬN DIỆN: Phải trả người bán (TK 331) & Phải trả khác (TK 3388)
        # -----------------------------------------------------------------
        if "3388" in ten_lower:
            mau = self.lay_mau_theo_id("BCTC_3388_PHAI_TRA_KHAC")
            text = mau["mau_cau"].format(
                nam=nam,
                so_tien_3388=val_a
            )
            return {
                "mau_id": "BCTC_3388_PHAI_TRA_KHAC",
                "tieu_de": "Kiểm tra Tài khoản 3388 - Phải trả khác",
                "nhom": "Báo cáo Tài chính",
                "cau_van": text,
                "can_cu": mau["can_cu"],
                "yeu_cau": mau["yeu_cau"],
                "du_lieu_goc": rui_ro_dict
            }

        if "331" in ten_lower:
            if "mua vào" in ten_lower or "doanh số mua" in ten_lower:
                mau = self.lay_mau_theo_id("BCTC_331_VS_MUA_VAO_GTGT")
                text = mau["mau_cau"].format(
                    nam=nam,
                    ps_331=val_a,
                    tong_mua_vao=val_b,
                    chenh_lech=chenh_lech
                )
                return {
                    "mau_id": "BCTC_331_VS_MUA_VAO_GTGT",
                    "tieu_de": "Đối chiếu TK 331 với Mua vào trên Tờ khai GTGT",
                    "nhom": "Báo cáo Tài chính",
                    "cau_van": text,
                    "can_cu": mau["can_cu"],
                    "yeu_cau": mau["yeu_cau"],
                    "du_lieu_goc": rui_ro_dict
                }
            else:
                mau = self.lay_mau_theo_id("BCTC_331_DU_CO")
                text = mau["mau_cau"].format(
                    nam=nam,
                    so_tien_331=val_a
                )
                return {
                    "mau_id": "BCTC_331_DU_CO",
                    "tieu_de": "Kiểm tra Số dư Có TK 331 - Phải trả người bán",
                    "nhom": "Báo cáo Tài chính",
                    "cau_van": text,
                    "can_cu": mau["can_cu"],
                    "yeu_cau": mau["yeu_cau"],
                    "du_lieu_goc": rui_ro_dict
                }

        # -----------------------------------------------------------------
        # 6. NHẬN DIỆN: Nguyên vật liệu (TK 152 vs TK 621) & Giá thành (TK 154)
        # -----------------------------------------------------------------
        if "152" in ten_lower and "621" in ten_lower:
            mau = self.lay_mau_theo_id("BCTC_152_VS_621")
            text = mau["mau_cau"].format(
                nam=nam,
                ps_152=val_a,
                ps_621=val_b,
                chenh_lech=chenh_lech
            )
            return {
                "mau_id": "BCTC_152_VS_621",
                "tieu_de": "Đối chiếu TK 152 (Nguyên vật liệu) và TK 621 (Chi phí NVL)",
                "nhom": "Báo cáo Tài chính",
                "cau_van": text,
                "can_cu": mau["can_cu"],
                "yeu_cau": mau["yeu_cau"],
                "du_lieu_goc": rui_ro_dict
            }

        if "154" in ten_lower:
            mau = self.lay_mau_theo_id("BCTC_154_GIA_THANH")
            text = mau["mau_cau"].format(
                nam=nam,
                ps_154=val_a,
                ps_chi_phi=val_b if val_b != "0" else val_a,
                chenh_lech=chenh_lech
            )
            return {
                "mau_id": "BCTC_154_GIA_THANH",
                "tieu_de": "Đối chiếu tập hợp chi phí giá thành (TK 154)",
                "nhom": "Báo cáo Tài chính",
                "cau_van": text,
                "can_cu": mau["can_cu"],
                "yeu_cau": mau["yeu_cau"],
                "du_lieu_goc": rui_ro_dict
            }

        # -----------------------------------------------------------------
        # 7. NHẬN DIỆN: Doanh thu không chịu thuế / Phân bổ thuế đầu vào (TT26)
        # -----------------------------------------------------------------
        if ("không chịu thuế" in ten_lower or "kct" in ten_lower or "chỉ tiêu 26" in ten_lower) and \
           ("phân bổ" in ten_lower or "khấu trừ" in ten_lower or "thông tư 26" in ten_lower or "gtgt" in ten_lower):
            mau = self.lay_mau_theo_id("GTGT_DOANH_THU_KCT_PHAN_BO")
            text = mau["mau_cau"].format(
                nam=nam,
                so_tien_kct=val_a
            )
            return {
                "mau_id": "GTGT_DOANH_THU_KCT_PHAN_BO",
                "tieu_de": "Doanh thu không chịu thuế GTGT & Phân bổ thuế đầu vào",
                "nhom": "Thuế GTGT",
                "cau_van": text,
                "can_cu": mau["can_cu"],
                "yeu_cau": mau["yeu_cau"],
                "du_lieu_goc": rui_ro_dict
            }

        # -----------------------------------------------------------------
        # 8. NHẬN DIỆN: Tờ khai bổ sung KHBS
        # -----------------------------------------------------------------
        if "khbs" in ten_lower or "bổ sung" in ten_lower:
            lan_bs = rui_ro_dict.get('lan_bs', '1')
            ky = rui_ro_dict.get('ky', f"năm {nam}")
            ngay_nop = rui_ro_dict.get('ngay_nop', '...')
            if "giảm" in ten_lower or "37" in ten_lower or "khấu trừ" in ten_lower:
                mau = self.lay_mau_theo_id("GTGT_KHBS_DIEU_CHINH_GIAM")
                text = mau["mau_cau"].format(
                    lan_bs=lan_bs, ky=ky, ngay_nop=ngay_nop, so_tien_giam=chenh_lech if chenh_lech != "0" else val_a
                )
                return {
                    "mau_id": "GTGT_KHBS_DIEU_CHINH_GIAM",
                    "tieu_de": f"KHBS điều chỉnh giảm thuế khấu trừ kỳ {ky}",
                    "nhom": "Thuế GTGT",
                    "cau_van": text,
                    "can_cu": mau["can_cu"],
                    "yeu_cau": mau["yeu_cau"],
                    "du_lieu_goc": rui_ro_dict
                }
            else:
                mau = self.lay_mau_theo_id("GTGT_KHBS_TANG_THUE_NOP")
                text = mau["mau_cau"].format(
                    lan_bs=lan_bs, ky=ky, ngay_nop=ngay_nop, so_tien_tang=chenh_lech if chenh_lech != "0" else val_a
                )
                return {
                    "mau_id": "GTGT_KHBS_TANG_THUE_NOP",
                    "tieu_de": f"KHBS làm tăng thuế phải nộp kỳ {ky}",
                    "nhom": "Thuế GTGT",
                    "cau_van": text,
                    "can_cu": mau["can_cu"],
                    "yeu_cau": mau["yeu_cau"],
                    "du_lieu_goc": rui_ro_dict
                }

        # -----------------------------------------------------------------
        # 8.1 NHẬN DIỆN: Rủi ro Hàng tồn kho lớn / Bán hàng không xuất hóa đơn
        # -----------------------------------------------------------------
        if "không xuất hóa đơn" in ten_lower or ("hàng tồn kho" in ten_lower and ("tồn lớn" in ten_lower or "bán hàng" in ten_lower)):
            mau = self.lay_mau_theo_id("BCTC_HANG_TON_KHO_BAN_KHONG_XUAT_HD")
            text = mau["mau_cau"].format(nam=nam)
            return {
                "mau_id": "BCTC_HANG_TON_KHO_BAN_KHONG_XUAT_HD",
                "tieu_de": "Rủi ro Bán hàng không xuất hóa đơn (Hàng tồn kho tồn lớn)",
                "nhom": "Báo cáo Tài chính",
                "cau_van": text,
                "can_cu": mau["can_cu"],
                "yeu_cau": mau["yeu_cau"],
                "du_lieu_goc": rui_ro_dict
            }

        # -----------------------------------------------------------------
        # 8.2 NHẬN DIỆN: Giấu doanh thu qua khoản nhận ứng trước khách hàng
        # -----------------------------------------------------------------
        if "ứng trước" in ten_lower and ("giấu doanh thu" in ten_lower or "khách hàng" in ten_lower or "131" in ten_lower):
            mau = self.lay_mau_theo_id("BCTC_GIAU_DOANH_THU_UNG_TRUOC")
            text = mau["mau_cau"].format(nam=nam, so_tien=val_a if val_a != "0" else chenh_lech)
            return {
                "mau_id": "BCTC_GIAU_DOANH_THU_UNG_TRUOC",
                "tieu_de": "Giấu Doanh thu qua Khoản Nhận ứng trước Khách hàng",
                "nhom": "Báo cáo Tài chính",
                "cau_van": text,
                "can_cu": mau["can_cu"],
                "yeu_cau": mau["yeu_cau"],
                "du_lieu_goc": rui_ro_dict
            }

        # -----------------------------------------------------------------
        # 8.3 NHẬN DIỆN: Biến động doanh thu tăng/giảm đột biến (Phân tích tỷ lệ)
        # -----------------------------------------------------------------
        if "đột biến" in ten_lower or ("tăng/giảm" in ten_lower and "doanh thu" in ten_lower):
            mau = self.lay_mau_theo_id("TY_LE_DOANH_THU_BIEN_DONG_DOT_BIEN")
            text = mau["mau_cau"].format(nam=nam, ty_le=val_a if val_a != "0" else chenh_lech)
            return {
                "mau_id": "TY_LE_DOANH_THU_BIEN_DONG_DOT_BIEN",
                "tieu_de": "Biến động Doanh thu trên tờ khai tăng/giảm đột biến",
                "nhom": "Phân tích tỷ lệ",
                "cau_van": text,
                "can_cu": mau["can_cu"],
                "yeu_cau": mau["yeu_cau"],
                "du_lieu_goc": rui_ro_dict
            }

        # -----------------------------------------------------------------
        # 9. NHẬN DIỆN: Hóa đơn rủi ro / Bỏ địa chỉ
        # -----------------------------------------------------------------
        if ("bỏ trốn" in ten_lower or "bỏ địa chỉ" in ten_lower or "không hoạt động" in ten_lower or "ngừng hoạt động" in ten_lower or ("doanh nghiệp rủi ro" in ten_lower and "hóa đơn" in ten_lower)):
            mau = self.lay_mau_theo_id("HD_RUI_RO_BO_DIA_CHI")
            sl_hd = rui_ro_dict.get('so_luong_hd', '01')
            sl_dn = rui_ro_dict.get('so_luong_dn', '01')
            mst_list = rui_ro_dict.get('danh_sach_mst', rui_ro_dict.get('mst', '...'))
            text = mau["mau_cau"].format(
                so_luong_hd=sl_hd,
                tong_tien=val_a,
                tien_thue=chenh_lech,
                so_luong_dn=sl_dn,
                danh_sach_mst=mst_list
            )
            return {
                "mau_id": "HD_RUI_RO_BO_DIA_CHI",
                "tieu_de": "Hóa đơn mua vào từ DN bỏ địa chỉ kinh doanh / Rủi ro",
                "nhom": "Hóa đơn Rủi ro",
                "cau_van": text,
                "can_cu": mau["can_cu"],
                "yeu_cau": mau["yeu_cau"],
                "du_lieu_goc": rui_ro_dict
            }

        # -----------------------------------------------------------------
        # 10. NHẬN DIỆN: Đối chiếu Hóa đơn vs Tờ khai
        # -----------------------------------------------------------------
        if "hóa đơn" in ten_lower and "tờ khai" in ten_lower:
            if "bán ra" in ten_lower:
                mau = self.lay_mau_theo_id("HD_BAN_RA_VS_TK_GTGT")
                text = mau["mau_cau"].format(
                    nam=nam,
                    tong_hd_br=val_a,
                    thue_hd_br="0",
                    tong_tk_br=val_b,
                    thue_tk_br="0",
                    chenh_lech_gt=chenh_lech,
                    chenh_lech_thue="0"
                )
                return {
                    "mau_id": "HD_BAN_RA_VS_TK_GTGT",
                    "tieu_de": "Đối chiếu HĐĐT Bán ra vs Tờ khai GTGT",
                    "nhom": "Hóa đơn Điện tử",
                    "cau_van": text,
                    "can_cu": mau["can_cu"],
                    "yeu_cau": mau["yeu_cau"],
                    "du_lieu_goc": rui_ro_dict
                }
            else:
                mau = self.lay_mau_theo_id("HD_MUA_VAO_VS_TK_GTGT")
                text = mau["mau_cau"].format(
                    nam=nam,
                    tong_hd_mv=val_a,
                    thue_hd_mv="0",
                    tong_tk_mv=val_b,
                    thue_tk_mv="0",
                    chenh_lech=chenh_lech
                )
                return {
                    "mau_id": "HD_MUA_VAO_VS_TK_GTGT",
                    "tieu_de": "Đối chiếu HĐĐT Mua vào vs Tờ khai GTGT",
                    "nhom": "Hóa đơn Điện tử",
                    "cau_van": text,
                    "can_cu": mau["can_cu"],
                    "yeu_cau": mau["yeu_cau"],
                    "du_lieu_goc": rui_ro_dict
                }

        # -----------------------------------------------------------------
        # 11. MẶC ĐỊNH CHO CÁC QUY TẮC ĐỐI CHIẾU 2 CHỈ TIÊU (KHÔNG DÙNG VẾ A/B)
        # -----------------------------------------------------------------
        co_ve_b_hop_le = (val_b != "0" and val_b != "") and (raw_b != "" and raw_b is not None)
        if rui_ro_dict.get('is_ab', False) and co_ve_b_hop_le:
            mau = self.lay_mau_theo_id("QUY_TAC_CHUNG_AB")
            text = mau["mau_cau"].format(
                ten_chi_tieu_a=ten_chi_tieu_a,
                val_a=val_a,
                ten_chi_tieu_b=ten_chi_tieu_b,
                val_b=val_b,
                nam=nam,
                chenh_lech=chenh_lech
            )
            return {
                "mau_id": "QUY_TAC_CHUNG_AB",
                "tieu_de": ten_loi,
                "nhom": nhom,
                "cau_van": text,
                "can_cu": mau["can_cu"],
                "yeu_cau": mau["yeu_cau"],
                "du_lieu_goc": rui_ro_dict
            }
        else:
            mau = self.lay_mau_theo_id("QUY_TAC_DON")
            ten_ct_sach = ten_chi_tieu_a
            if "(" in ten_ct_sach or ")" in ten_ct_sach or "+" in ten_ct_sach or "/" in ten_ct_sach:
                ten_ct_sach = f"chỉ tiêu liên quan đến {ten_loi}"
            text = mau["mau_cau"].format(
                ten_chi_tieu_a=ten_ct_sach,
                nam=nam,
                val_a=val_a if val_a != "0" else chenh_lech,
                thong_diep=thong_diep if thong_diep else "Đề nghị đơn vị giải trình rõ nguyên nhân phát sinh."
            )
            return {
                "mau_id": "QUY_TAC_DON",
                "tieu_de": ten_loi,
                "nhom": nhom,
                "cau_van": text,
                "can_cu": mau["can_cu"],
                "yeu_cau": mau["yeu_cau"],
                "du_lieu_goc": rui_ro_dict
            }


# =============================================================================
# TRÍCH XUẤT SỐ LIỆU TỜ KHAI CHO BIỂU MẪU CHUẨN (TABLE 1, TABLE 2)
# =============================================================================
TEN_CHI_TIEU_BANG_GTGT = {
    1: "Giá trị của hàng hóa, dịch vụ mua vào",
    2: "Thuế giá trị gia tăng của hàng hóa, dịch vụ mua vào",
    3: "Thuế giá trị gia tăng của hàng hóa, dịch vụ mua vào được khấu trừ kỳ này",
    4: "Giá trị hàng hóa, dịch vụ bán ra chịu thuế giá trị gia tăng",
    5: "Thuế giá trị gia tăng của hàng hóa, dịch vụ bán ra chịu thuế",
    6: "Giá trị hàng hoá, dịch vụ bán ra chịu thuế suất 10%",
    7: "Thuế giá trị gia tăng hàng hoá, dịch vụ bán ra chịu thuế suất 10%",
    8: "Tổng doanh thu của hàng hóa, dịch vụ bán ra",
    9: "Tổng thuế giá trị gia tăng của hàng hóa, dịch vụ bán ra",
    10: "Thuế giá trị gia tăng phát sinh trong kỳ",
    11: "Điều chỉnh giảm thuế GTGT còn được khấu trừ của các kỳ trước",
    12: "Thuế giá trị gia tăng phải nộp của hoạt động sản xuất kinh doanh trong kỳ"
}


def trich_xuat_bang_gtgt(du_lieu_to_khai, nam_list=None):
    """
    Trích xuất 12 chỉ tiêu tờ khai 01/GTGT theo từng năm phục vụ Bảng 1 PhieuNhanXet.docx
    """
    if not du_lieu_to_khai or not isinstance(du_lieu_to_khai, dict):
        return {}

    gtgt_data = du_lieu_to_khai.get('01/GTGT', {})
    if not gtgt_data:
        # Thử tìm theo tên form khác
        for k, v in du_lieu_to_khai.items():
            if '01' in str(k) and 'gtgt' in str(k).lower():
                gtgt_data = v
                break

    if not gtgt_data:
        return {}

    years = sorted(list(set(str(k).split('/')[-1] for k in gtgt_data.keys())))
    if nam_list:
        nam_set = set(str(n) for n in nam_list)
        years = [y for y in years if y in nam_set]

    res = {}
    for y in years:
        tot = {i: 0.0 for i in range(1, 13)}
        ky_nam = [k for k in gtgt_data.keys() if str(k).endswith(y)]
        for k in ky_nam:
            tk = gtgt_data[k]
            ct = tk.get('ChiTieuChinh', {})

            def v(code):
                try:
                    raw = ct.get(code, {}).get('GiaTri', 0)
                    return float(str(raw).replace(',', ''))
                except Exception:
                    return 0.0

            tot[1] += v('ct23')
            tot[2] += v('ct24')
            tot[3] += v('ct25')
            tot[4] += (v('ct27') if v('ct27') != 0 else (v('ct29') + v('ct30') + v('ct32')))
            tot[5] += (v('ct28') if v('ct28') != 0 else v('ct35'))
            tot[6] += (v('ct32') if v('ct32') != 0 else v('ct28'))
            tot[7] += (v('ct33') if v('ct33') != 0 else v('ct35'))
            tot[8] += v('ct34')
            tot[9] += v('ct35')
            tot[10] += (v('ct36') if v('ct36') != 0 else v('ct40a'))
            tot[11] += v('ct37')
            tot[12] += v('ct40a')

        res[y] = tot

    return res


def trich_xuat_bang_tncn(du_lieu_to_khai, nam_list=None):
    """
    Trích xuất chỉ tiêu quyết toán TNCN (05/QTT-TNCN) phục vụ Bảng 2 PhieuNhanXet.docx
    """
    if not du_lieu_to_khai or not isinstance(du_lieu_to_khai, dict):
        return {}

    tncn_data = du_lieu_to_khai.get('05/QTT-TNCN', {})
    if not tncn_data:
        for k, v in du_lieu_to_khai.items():
            if '05' in str(k) and ('tncn' in str(k).lower() or 'qtt' in str(k).lower()):
                tncn_data = v
                break

    if not tncn_data:
        return {}

    years = sorted(list(set(str(k).split('/')[-1] for k in tncn_data.keys())))
    if nam_list:
        nam_set = set(str(n) for n in nam_list)
        years = [y for y in years if y in nam_set]

    res = {}
    for y in years:
        ct = tncn_data[y].get('ChiTieuChinh', {})

        def v(keys):
            for c in keys:
                if c in ct:
                    try:
                        raw = ct[c].get('GiaTri', 0)
                        return float(str(raw).replace(',', ''))
                    except Exception:
                        pass
            return 0.0

        tnct = v(['NVuKhauTruThue_ct23', 'ct23', 'ct26', 'NVuKhauTruThue_ct26'])
        thue = v(['NVuKhauTruThue_ct31', 'ct31', 'ct32', 'NVuKhauTruThue_ct32'])
        res[y] = {'tnct': tnct, 'thue': thue}

    return res

