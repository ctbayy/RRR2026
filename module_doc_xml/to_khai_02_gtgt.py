import xml.etree.ElementTree as ET
from module_doc_xml.tu_dien_chi_tieu import TU_DIEN_TO_KHAI


def phan_tich_xml(duong_dan_file):
    """
    Đọc và trích xuất dữ liệu từ tờ khai 02/GTGT (Dành cho dự án đầu tư).
    Hỗ trợ cả mẫu cũ (TT26) và mẫu mới (TT80), xử lý thẻ lồng nhau qua .iter().
    """
    tree = ET.parse(duong_dan_file)
    root = tree.getroot()

    # Hàm hỗ trợ tìm kiếm thẻ (tag) bỏ qua các namespace phức tạp của XML
    def lay_gia_tri(node_goc, ten_the):
        for elem in node_goc.iter():
            if elem.tag.endswith(f"}}{ten_the}") or elem.tag == ten_the:
                return elem.text
        return None

    ma_tkhai = lay_gia_tri(root, "maTKhai")

    so_lan_raw = lay_gia_tri(root, "soLan") or lay_gia_tri(root, "soLanBS") or lay_gia_tri(root, "lanBS") or lay_gia_tri(root, "soLan_BS") or "0"
    try:
        so_lan_val = int(str(so_lan_raw).strip())
    except (ValueError, TypeError):
        so_lan_val = 0

    ket_qua = {
        "ThongTinChung": {
            "MaTKhai": ma_tkhai,
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

    # ĐỊNH TUYẾN DANH SÁCH CHỈ TIÊU CHUẨN THEO MÃ TỜ KHAI
    if ma_tkhai == "02":
        # Mẫu cũ (TT26) - Có ct30a, không có ct22a, ct23a, ct28b
        danh_sach_hop_le = [
            "ct21", "ct21a", "ct22", "ct23", "ct24", "ct25",
            "ct26", "ct27", "ct28", "ct28a", "ct29", "ct30a",
            "ct30", "ct31", "ct32"
        ]
    elif ma_tkhai == "844":
        # Mẫu mới (TT80) - Có ct22a, ct23a, ct28b, không có ct30a
        danh_sach_hop_le = [
            "ct21", "ct21a", "ct22", "ct23", "ct22a", "ct23a",
            "ct24", "ct25", "ct26", "ct27", "ct28", "ct28a",
            "ct28b", "ct29", "ct30", "ct31", "ct32"
        ]
    else:
        danh_sach_hop_le = []

    # =========================================================================
    # TRÍCH XUẤT TỜ KHAI CHÍNH BẰNG CƠ CHẾ QUÉT ĐỘNG
    # =========================================================================
    ctieu_chinh_node = None
    for elem in root.iter():
        if elem.tag.endswith("}CTieuTKhaiChinh") or elem.tag == "CTieuTKhaiChinh":
            ctieu_chinh_node = elem
            break

    if ctieu_chinh_node is not None:
        tu_dien = TU_DIEN_TO_KHAI.get("02/GTGT", {})

        # Dùng .iter() quét xuyên qua các lớp thẻ lồng nhau
        for child in ctieu_chinh_node.iter():
            tag_name = child.tag.split('}')[-1]

            # Chỉ bắt các thẻ ct... nằm trong whitelist của phiên bản tờ khai tương ứng
            if tag_name in danh_sach_hop_le and child.text is not None and child.text.strip():
                gia_tri = child.text
                dien_giai = tu_dien.get(tag_name, f"Chỉ tiêu {tag_name}")

                ket_qua["ChiTieuChinh"][tag_name] = {
                    "GiaTri": gia_tri,
                    "DienGiai": dien_giai
                }

    return ket_qua