import xml.etree.ElementTree as ET
from module_doc_xml.tu_dien_chi_tieu import TU_DIEN_TO_KHAI


def phan_tich_xml(duong_dan_file):
    """
    Đọc và trích xuất dữ liệu từ tờ khai 05/KK-TNCN (Thuế TNCN Tháng/Quý).
    (Cấu trúc phẳng, tất cả nằm trong CTieuTKhaiChinh)
    """
    tree = ET.parse(duong_dan_file)
    root = tree.getroot()

    # Hàm hỗ trợ tìm nhanh nội dung một thẻ XML
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

    # Khởi tạo khung dữ liệu trả về
    ket_qua = {
        "ThongTinChung": {
            "MaTKhai": lay_gia_tri(root, "maTKhai"),  # 864
            "TenTKhai": lay_gia_tri(root, "tenTKhai"),
            "MST": lay_gia_tri(root, "mst"),
            "TenNNT": lay_gia_tri(root, "tenNNT"),
            "KyKeKhai": lay_gia_tri(root, "kyKKhai"),
            "CoQuanThue": lay_gia_tri(root, "maCQTNoiNop"),
            "SoLan": so_lan_val,
            "LanBoSung": so_lan_val
        },
        "SoLan": so_lan_val,
        "LanBoSung": so_lan_val,
        "ChiTieuChinh": {},
        "PhuLuc": {}  # Mẫu 05/KK không có Phụ lục
    }

    # =========================================================================
    # 1. TRÍCH XUẤT CHỈ TIÊU CHÍNH TỜ KHAI
    # =========================================================================
    ctieu_chinh_node = None
    for elem in root.iter():
        if elem.tag.endswith("}CTieuTKhaiChinh") or elem.tag == "CTieuTKhaiChinh":
            ctieu_chinh_node = elem
            break

    if ctieu_chinh_node is not None:
        dict_tk_chinh = TU_DIEN_TO_KHAI.get("05/KK_TNCN", {}).get("ToKhaiChinh", {})

        for child in ctieu_chinh_node:
            tag_name = child.tag.split('}')[-1]
            if tag_name.startswith("ct"):
                gia_tri = child.text if child.text else "0"
                dien_giai = dict_tk_chinh.get(tag_name, f"Chỉ tiêu {tag_name}")

                ket_qua["ChiTieuChinh"][tag_name] = {
                    "GiaTri": gia_tri,
                    "DienGiai": dien_giai
                }

    return ket_qua