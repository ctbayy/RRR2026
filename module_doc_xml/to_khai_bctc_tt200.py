import xml.etree.ElementTree as ET
from module_doc_xml.tu_dien_chi_tieu import TU_DIEN_TO_KHAI


def phan_tich_xml(duong_dan_file):
    """
    Đọc và trích xuất dữ liệu từ Báo cáo tài chính (TT200/2014/TT-BTC).
    Bao gồm: Bảng cân đối kế toán, Báo cáo KQKD, và Báo cáo Lưu chuyển tiền tệ.
    """
    tree = ET.parse(duong_dan_file)
    root = tree.getroot()

    def lay_gia_tri(node_goc, ten_the):
        for elem in node_goc.iter():
            if elem.tag.endswith(f"}}{ten_the}") or elem.tag == ten_the:
                return elem.text
        return None

    # Tách lấy năm kê khai (ví dụ 2025) để làm tiêu đề cột
    ky_ke_khai = lay_gia_tri(root, "kyKKhai") or "Năm"
    ky_truoc = str(int(ky_ke_khai) - 1) if ky_ke_khai.isdigit() else "Năm Trước"

    so_lan_raw = lay_gia_tri(root, "soLan") or lay_gia_tri(root, "soLanBS") or lay_gia_tri(root, "lanBS") or lay_gia_tri(root, "soLan_BS") or "0"
    try:
        so_lan_val = int(str(so_lan_raw).strip())
    except (ValueError, TypeError):
        so_lan_val = 0

    ket_qua = {
        "ThongTinChung": {
            "MaTKhai": lay_gia_tri(root, "maTKhai"),  # Mã 402
            "TenTKhai": lay_gia_tri(root, "tenTKhai"),
            "MST": lay_gia_tri(root, "mst"),
            "TenNNT": lay_gia_tri(root, "tenNNT"),
            "KyKeKhai": ky_ke_khai,
            "CoQuanThue": lay_gia_tri(root, "maCQTNoiNop"),
            "SoLan": so_lan_val,
            "LanBoSung": so_lan_val
        },
        "SoLan": so_lan_val,
        "LanBoSung": so_lan_val,
        # Chứa Bảng cân đối kế toán (Do nằm ở thẻ CTieuTKhaiChinh)
        "B01_CDKT": {},

        # Chứa Báo cáo KQKD và LCTT (Do nằm ở thẻ PLuc)
        "B02_KQKD": {},
        "B03_LCTT": {}
    }

    # =========================================================================
    # 1. TRÍCH XUẤT BẢNG CÂN ĐỐI KẾ TOÁN (B01 - CDKT)
    # =========================================================================
    # Bảng CDKT được chia làm 2 khối: <SoCuoiNam> và <SoDauNam>
    # =========================================================================
    # 1. TRÍCH XUẤT BẢNG CÂN ĐỐI KẾ TOÁN (B01 - CDKT)
    # =========================================================================
    cdkt_node = None
    for elem in root.iter():
        if elem.tag.endswith("CDKT_HoatDongLienTuc") or elem.tag.endswith("CDKT_HoatDongKhongLienTuc"):
            cdkt_node = elem
            break

    if cdkt_node is not None:
        so_cuoi_nam_node = lay_node(cdkt_node, "SoCuoiNam")
        so_dau_nam_node = lay_node(cdkt_node, "SoDauNam")

        # ĐÃ FIX: ÉP BUỘC CHỈ TRA CỨU TRONG B01_CDKT
        tu_dien_cdkt = TU_DIEN_TO_KHAI.get("BCTC_TT200", {}).get("B01_CDKT", {})

        if so_cuoi_nam_node is not None and so_dau_nam_node is not None:
            for child in so_cuoi_nam_node:
                tag_name = child.tag.split('}')[-1]
                if tag_name.startswith("ct"):
                    gia_tri_cuoi = child.text if child.text else "0"

                    the_dau_nam = lay_node(so_dau_nam_node, tag_name)
                    gia_tri_dau = the_dau_nam.text if (the_dau_nam is not None and the_dau_nam.text) else "0"

                    # TRA CỨU CHÍNH XÁC
                    dien_giai = tu_dien_cdkt.get(tag_name, f"Chỉ tiêu {tag_name}")

                    ket_qua["B01_CDKT"][tag_name] = {
                        "DienGiai": dien_giai,
                        f"Giá trị cuối {ky_ke_khai}": gia_tri_cuoi,
                        f"Giá trị đầu {ky_ke_khai}": gia_tri_dau
                    }

    # =========================================================================
    # 2. TRÍCH XUẤT BÁO CÁO KQKD (B02) VÀ LƯU CHUYỂN TIỀN TỆ (B03)
    # =========================================================================
    # Các báo cáo này nằm trong <PLuc> và chia thành <NamNay> và <NamTruoc>
    phu_luc_node = None
    for elem in root.iter():
        if elem.tag.endswith("PLuc") or elem.tag == "PLuc":
            phu_luc_node = elem
            break

    if phu_luc_node is not None:
        for pl_child in phu_luc_node:
            tag_pl = pl_child.tag.split('}')[-1]

            # Phân loại báo cáo và chọn bộ từ điển tương ứng
            if "PL_KQHDSXKD" in tag_pl:
                nhom_bao_cao = "B02_KQKD"
                tu_dien_pl = TU_DIEN_TO_KHAI.get("BCTC_TT200", {}).get("B02_KQKD", {})
            elif "PL_LCTTTT" in tag_pl:
                nhom_bao_cao = "B03_LCTT"
                tu_dien_pl = TU_DIEN_TO_KHAI.get("BCTC_TT200", {}).get("B03_LCTT_TT", {})
            elif "PL_LCTTGT" in tag_pl:
                nhom_bao_cao = "B03_LCTT"
                tu_dien_pl = TU_DIEN_TO_KHAI.get("BCTC_TT200", {}).get("B03_LCTT_GT", {})
            else:
                continue  # Bỏ qua nếu là phụ lục không xác định

            nam_nay_node = lay_node(pl_child, "NamNay")
            nam_truoc_node = lay_node(pl_child, "NamTruoc")

            if nam_nay_node is not None and nam_truoc_node is not None:
                for child in nam_nay_node:
                    tag_name = child.tag.split('}')[-1]
                    if tag_name.startswith("ct"):
                        gia_tri_nay = child.text if child.text else "0"

                        the_truoc = lay_node(nam_truoc_node, tag_name)
                        gia_tri_truoc = the_truoc.text if (the_truoc is not None and the_truoc.text) else "0"

                        dien_giai = tu_dien_pl.get(tag_name, f"Chỉ tiêu {tag_name}")

                        # Đẩy dữ liệu vào
                        ket_qua[nhom_bao_cao][tag_name] = {
                            "DienGiai": dien_giai,
                            f"Phát sinh năm {ky_ke_khai}": gia_tri_nay,
                            f"Phát sinh năm {ky_truoc}": gia_tri_truoc
                        }

    return ket_qua


def lay_node(node_goc, ten_the):
    """Hàm hỗ trợ tìm Node con trực tiếp"""
    for child in node_goc:
        if child.tag.endswith(f"}}{ten_the}") or child.tag == ten_the:
            return child
    return None