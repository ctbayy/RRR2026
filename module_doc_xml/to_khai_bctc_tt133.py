import xml.etree.ElementTree as ET
from module_doc_xml.tu_dien_chi_tieu import TU_DIEN_TO_KHAI


def phan_tich_xml(duong_dan_file):
    """
    Đọc và trích xuất dữ liệu từ Báo cáo tài chính (TT133/2016/TT-BTC).
    Bao gồm: Bảng cân đối kế toán, KQKD, LCTT và Cân đối tài khoản.
    """
    tree = ET.parse(duong_dan_file)
    root = tree.getroot()

    def lay_gia_tri(node_goc, ten_the):
        for elem in node_goc.iter():
            if elem.tag.endswith(f"}}{ten_the}") or elem.tag == ten_the:
                return elem.text
        return None

    ky_ke_khai = lay_gia_tri(root, "kyKKhai") or "Năm"
    ky_truoc = str(int(ky_ke_khai) - 1) if ky_ke_khai.isdigit() else "Năm Trước"

    so_lan_raw = lay_gia_tri(root, "soLan") or lay_gia_tri(root, "soLanBS") or lay_gia_tri(root, "lanBS") or lay_gia_tri(root, "soLan_BS") or "0"
    try:
        so_lan_val = int(str(so_lan_raw).strip())
    except (ValueError, TypeError):
        so_lan_val = 0

    ket_qua = {
        "ThongTinChung": {
            "MaTKhai": lay_gia_tri(root, "maTKhai"),  # Mã 683
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
        "B01_CDKT": {},
        "B02_KQKD": {},
        "B03_LCTT": {},
        "B04_CDTK": {}  # Bảng Cân đối tài khoản
    }

    # =========================================================================
    # 1. TRÍCH XUẤT BẢNG CÂN ĐỐI KẾ TOÁN (B01 - CDKT)
    # =========================================================================
    cdkt_node = lay_node_bởi_hậu_tố(root, "CTieuTKhaiChinh")

    if cdkt_node is not None:
        so_cuoi_nam_node = lay_node(cdkt_node, "SoCuoiNam")
        so_dau_nam_node = lay_node(cdkt_node, "SoDauNam")

        tu_dien_cdkt = TU_DIEN_TO_KHAI.get("BCTC_TT133", {}).get("B01_CDKT", {})

        if so_cuoi_nam_node is not None and so_dau_nam_node is not None:
            for child in so_cuoi_nam_node:
                tag_name = child.tag.split('}')[-1]
                if tag_name.startswith("ct"):
                    gia_tri_cuoi = child.text if child.text else "0"

                    the_dau_nam = lay_node(so_dau_nam_node, tag_name)
                    gia_tri_dau = the_dau_nam.text if (the_dau_nam is not None and the_dau_nam.text) else "0"

                    dien_giai = tu_dien_cdkt.get(tag_name, f"Chỉ tiêu {tag_name}")

                    ket_qua["B01_CDKT"][tag_name] = {
                        "DienGiai": dien_giai,
                        f"Số cuối năm": gia_tri_cuoi,
                        f"Số đầu năm": gia_tri_dau
                    }

    # =========================================================================
    # 2. TRÍCH XUẤT CÁC BÁO CÁO TRONG PHỤ LỤC
    # =========================================================================
    phu_luc_node = lay_node_bởi_hậu_tố(root, "PLuc")

    if phu_luc_node is not None:
        for pl_child in phu_luc_node:
            tag_pl = pl_child.tag.split('}')[-1]

            # --- XỬ LÝ KẾT QUẢ KINH DOANH VÀ LƯU CHUYỂN TIỀN TỆ ---
            if tag_pl in ["PL_KQHDSXKD", "PL_LCTTTT", "PL_LCTTGT"]:
                if tag_pl == "PL_KQHDSXKD":
                    nhom_bao_cao = "B02_KQKD"
                    tu_dien_pl = TU_DIEN_TO_KHAI.get("BCTC_TT133", {}).get("B02_KQKD", {})
                elif tag_pl == "PL_LCTTTT":
                    nhom_bao_cao = "B03_LCTT"
                    tu_dien_pl = TU_DIEN_TO_KHAI.get("BCTC_TT133", {}).get("B03_LCTT_TT", {})
                else:
                    nhom_bao_cao = "B03_LCTT"
                    tu_dien_pl = TU_DIEN_TO_KHAI.get("BCTC_TT133", {}).get("B03_LCTT_GT", {})

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

                            ket_qua[nhom_bao_cao][tag_name] = {
                                "DienGiai": dien_giai,
                                f"Năm nay": gia_tri_nay,
                                f"Năm trước": gia_tri_truoc
                            }

            # --- XỬ LÝ BẢNG CÂN ĐỐI TÀI KHOẢN (6 CỘT) ---
            # --- XỬ LÝ BẢNG CÂN ĐỐI TÀI KHOẢN (6 CỘT) ---
            # --- XỬ LÝ BẢNG CÂN ĐỐI TÀI KHOẢN (6 CỘT) ---
            elif tag_pl == "PL_CDTK":
                nhom_bao_cao = "B04_CDTK"
                # CHỈ ĐỊNH CHÍNH XÁC VÀO BỘ TỪ ĐIỂN B04_CDTK ĐỂ TRÁNH NHẦM LẪN VỚI B01_CDKT
                tu_dien_cdtk = TU_DIEN_TO_KHAI.get("BCTC_TT133", {}).get("B04_CDTK", {})

                khoi_dau_ky = lay_node(pl_child, "SoDuDauKy")
                khoi_phat_sinh = lay_node(pl_child, "SoPhatSinhTrongKy")
                khoi_cuoi_ky = lay_node(pl_child, "SoDuCuoiKy")

                def get_no_co(khoi_node, tag_tk):
                    if khoi_node is None: return "0", "0"
                    no_node = lay_node(khoi_node, "No")
                    co_node = lay_node(khoi_node, "Co")

                    val_no = lay_node(no_node, tag_tk).text if lay_node(no_node, tag_tk) is not None else "0"
                    val_co = lay_node(co_node, tag_tk).text if lay_node(co_node, tag_tk) is not None else "0"
                    return val_no or "0", val_co or "0"

                if khoi_dau_ky is not None:
                    no_dau_ky_node = lay_node(khoi_dau_ky, "No")
                    if no_dau_ky_node is not None:
                        for child in no_dau_ky_node:
                            tag_tk = child.tag.split('}')[-1]

                            ten_tk = tag_tk[2:] if tag_tk.startswith("ct") else tag_tk
                            if ten_tk == "ngCong": ten_tk = "Tổng Cộng"

                            dau_no, dau_co = get_no_co(khoi_dau_ky, tag_tk)
                            ps_no, ps_co = get_no_co(khoi_phat_sinh, tag_tk)
                            cuoi_no, cuoi_co = get_no_co(khoi_cuoi_ky, tag_tk)

                            # ĐÃ FIX: ÉP BUỘC TRA CỨU TRONG B04_CDTK, NẾU KHÔNG CÓ THÌ BÁO "Tài khoản..."
                            dien_giai = tu_dien_cdtk.get(tag_tk, f"Tài khoản {ten_tk}")

                            ket_qua["B04_CDTK"][tag_tk] = {
                                "DienGiai": dien_giai,
                                "Dư đầu kỳ (Nợ)": dau_no,
                                "Dư đầu kỳ (Có)": dau_co,
                                "Phát sinh (Nợ)": ps_no,
                                "Phát sinh (Có)": ps_co,
                                "Dư cuối kỳ (Nợ)": cuoi_no,
                                "Dư cuối kỳ (Có)": cuoi_co
                            }

    return ket_qua


def lay_node(node_goc, ten_the):
    for child in node_goc:
        if child.tag.endswith(f"}}{ten_the}") or child.tag == ten_the:
            return child
    return None


def lay_node_bởi_hậu_tố(node_goc, hau_to):
    for elem in node_goc.iter():
        if elem.tag.endswith(f"}}{hau_to}") or elem.tag == hau_to:
            return elem
    return None