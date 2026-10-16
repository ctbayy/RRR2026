import xml.etree.ElementTree as ET
from module_doc_xml.tu_dien_chi_tieu import TU_DIEN_TO_KHAI


def phan_tich_xml(duong_dan_file):
    """
    Đọc và trích xuất dữ liệu từ tờ khai 04/GTGT (Phương pháp trực tiếp trên doanh thu).
    """
    tree = ET.parse(duong_dan_file)
    root = tree.getroot()

    # Hàm hỗ trợ tìm kiếm thẻ (tag) bỏ qua các namespace phức tạp của XML
    def lay_gia_tri(node_goc, ten_the):
        for elem in node_goc.iter():
            if elem.tag.endswith(f"}}{ten_the}") or elem.tag == ten_the:
                return elem.text
        return None

    so_lan_raw = lay_gia_tri(root, "soLan") or lay_gia_tri(root, "soLanBS") or lay_gia_tri(root, "lanBS") or lay_gia_tri(root, "soLan_BS") or "0"
    try:
        so_lan_val = int(str(so_lan_raw).strip())
    except (ValueError, TypeError):
        so_lan_val = 0

    ket_qua = {
        "ThongTinChung": {
            "MaTKhai": lay_gia_tri(root, "maTKhai"),
            "TenTKhai": lay_gia_tri(root, "tenTKhai"),
            "MST": lay_gia_tri(root, "mst"),
            "TenNNT": lay_gia_tri(root, "tenNNT"),
            "KyKeKhai": lay_gia_tri(root, "kyKKhai"),
            "KieuKy": lay_gia_tri(root, "kieuKy"),  # Bổ sung meta-data kiểu kỳ
            "CoQuanThue": lay_gia_tri(root, "maCQTNoiNop"),
            "SoLan": so_lan_val,
            "LanBoSung": so_lan_val
        },
        "SoLan": so_lan_val,
        "LanBoSung": so_lan_val,
        "ChiTieuChinh": {}
    }

    # Danh sách các chỉ tiêu dành riêng cho mẫu 04/GTGT
    danh_sach_chi_tieu = [
        "ct21", "ct22", "ct23", "ct24", "ct25", "ct26",
        "ct27", "ct28", "ct29", "ct30", "ct31", "ct32",
        "ct33", "ct34", "ct35", "ct36", "ct37"
    ]

    for ct in danh_sach_chi_tieu:
        # Xử lý trường hợp thẻ XML có thuộc tính xsi:nil="true" (trả về None)
        gia_tri = lay_gia_tri(root, ct)
        if gia_tri is None or gia_tri.strip() == "":
            gia_tri = "0"

        # Lấy diễn giải từ bộ từ điển, mặc định nếu không có
        dien_giai = TU_DIEN_TO_KHAI.get("04/GTGT", {}).get(ct, "Không có thông tin diễn giải")

        ket_qua["ChiTieuChinh"][ct] = {
            "GiaTri": gia_tri,
            "DienGiai": dien_giai
        }

    return ket_qua