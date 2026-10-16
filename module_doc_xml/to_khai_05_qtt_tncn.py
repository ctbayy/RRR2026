import xml.etree.ElementTree as ET
from module_doc_xml.tu_dien_chi_tieu import TU_DIEN_TO_KHAI


def phan_tich_xml(duong_dan_file):
    """
    Đọc và trích xuất dữ liệu từ tờ khai 05/QTT-TNCN.
    (Đã xử lý dóng hàng dòng Tổng cộng vào đúng các cột chi tiết)
    """
    tree = ET.parse(duong_dan_file)
    root = tree.getroot()

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
            "CoQuanThue": lay_gia_tri(root, "maCQTNoiNop"),
            "SoLan": so_lan_val,
            "LanBoSung": so_lan_val
        },
        "SoLan": so_lan_val,
        "LanBoSung": so_lan_val,
        "ChiTieuChinh": {},
        "PhuLuc": {}
    }

    # =========================================================================
    # 1. TRÍCH XUẤT TỜ KHAI CHÍNH
    # =========================================================================
    ctieu_chinh_node = None
    for elem in root.iter():
        if elem.tag.endswith("}CTieuTKhaiChinh") or elem.tag == "CTieuTKhaiChinh":
            ctieu_chinh_node = elem
            break

    if ctieu_chinh_node is not None:
        dict_tk_chinh = TU_DIEN_TO_KHAI.get("05/QTT_TNCN", {}).get("ToKhaiChinh", {})
        cac_khoi_chinh = ["NVuKhauTruThue", "NVuQToanThay"]

        for khoi in cac_khoi_chinh:
            khoi_node = None
            for elem in ctieu_chinh_node.iter():
                if elem.tag.endswith(f"}}{khoi}") or elem.tag == khoi:
                    khoi_node = elem
                    break

            if khoi_node is not None:
                for child in khoi_node:
                    tag_name = child.tag.split('}')[-1]
                    if tag_name.startswith("ct"):
                        unique_key = f"{khoi}_{tag_name}"
                        gia_tri = child.text if child.text else "0"
                        dien_giai = dict_tk_chinh.get(unique_key, f"Chỉ tiêu {tag_name}")

                        ket_qua["ChiTieuChinh"][unique_key] = {
                            "GiaTri": gia_tri,
                            "DienGiai": dien_giai
                        }

    # =========================================================================
    # 2. TRÍCH XUẤT BẢNG KÊ PHỤ LỤC
    # =========================================================================
    # Bộ định tuyến bẻ lái các thẻ Tổng cộng về đúng tên cột chi tiết
    map_tong_cong = {
        "PL 05-1": {
            "ct28": "ct12", "ct29": "ct13", "ct30": "ct14", "ct31": "ct15", "ct31.1": "ct15.1",
            "ct32": "ct16", "ct33": "ct17", "ct34": "ct18", "ct35": "ct19", "ct36": "ct20",
            "ct37": "ct21", "ct38": "ct22", "ct39": "ct23", "ct40": "ct24", "ct41": "ct25",
            "ct42": "ct26", "ct43": "ct27"
        },
        "PL 05-2": {
            "ct17": "ct11", "ct18": "ct12", "ct19": "ct13", "ct20": "ct14", "ct20.1": "ct14.1",
            "ct21": "ct15", "ct22": "ct16"
        }
    }

    phu_luc_node = None
    for elem in root.iter():
        if elem.tag.endswith("}PLuc") or elem.tag == "PLuc":
            phu_luc_node = elem
            break

    if phu_luc_node is not None:
        map_ten_pl = {
            "PLuc_05_1_BK_QTT": "PL 05-1",
            "PLuc_05_2_BK_QTT": "PL 05-2",
            "PLuc_05_3_BK_QTT": "PL 05-3"
        }

        for pl_child in phu_luc_node:
            tag_pl = pl_child.tag.split('}')[-1]
            if tag_pl in map_ten_pl:
                ten_hien_thi = map_ten_pl[tag_pl]
                dict_phu_luc = TU_DIEN_TO_KHAI.get("05/QTT_TNCN", {}).get(ten_hien_thi, {})

                danh_sach_dong = [elem for elem in pl_child.iter() if
                                  elem.tag.split('}')[-1] in ["BKeCTietCNhan", "BKeTTinNPT"]]

                if danh_sach_dong:
                    ket_qua["PhuLuc"][ten_hien_thi] = {"IsBangKe": True, "DuLieu": {}}

                    # 2.1 Quét danh sách chi tiết cá nhân
                    for index, record in enumerate(danh_sach_dong):
                        dong_du_lieu = {}
                        for child in record:
                            tag_name = child.tag.split('}')[-1]
                            # Loại bỏ các thẻ không phải ct... ra khỏi lưới
                            if tag_name.startswith("ct") and child.text is not None:
                                gia_tri = child.text
                                if gia_tri.lower() == "true":
                                    gia_tri = "x"
                                elif gia_tri.lower() == "false":
                                    gia_tri = ""

                                dien_giai = dict_phu_luc.get(tag_name, f"Chỉ tiêu {tag_name}")
                                dong_du_lieu[dien_giai] = gia_tri

                        if dong_du_lieu:
                            ket_qua["PhuLuc"][ten_hien_thi]["DuLieu"][f"{index + 1}"] = dong_du_lieu

                    # 2.2 Quét riêng dòng Tổng cộng (Bẻ lái XML)
                    tong_cong = {}
                    map_tc_hien_tai = map_tong_cong.get(ten_hien_thi, {})

                    for child in pl_child:
                        tag_name = child.tag.split('}')[-1]
                        # Nếu mã tag nằm trong danh sách cần bẻ lái (VD: ct28)
                        if tag_name in map_tc_hien_tai and child.text is not None:
                            # Đổi mã về cột gốc (VD: ct28 -> ct12)
                            tag_cot_goc = map_tc_hien_tai[tag_name]

                            # Lấy tên cột chuẩn từ từ điển dựa trên mã gốc để đảm bảo trùng khớp key 100%
                            ten_cot_goc = dict_phu_luc.get(tag_cot_goc, f"Chỉ tiêu {tag_cot_goc}")
                            tong_cong[ten_cot_goc] = child.text

                    if tong_cong:
                        ket_qua["PhuLuc"][ten_hien_thi]["DuLieu"]["Tổng cộng"] = tong_cong

    return ket_qua