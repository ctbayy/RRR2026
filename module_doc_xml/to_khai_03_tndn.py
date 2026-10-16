import xml.etree.ElementTree as ET
from module_doc_xml.tu_dien_chi_tieu import TU_DIEN_TO_KHAI, MAP_TEN_TO_KHAI


def phan_tich_xml(duong_dan_file):
    """
    Đọc và trích xuất dữ liệu từ tờ khai Quyết toán 03/TNDN.
    Áp dụng cơ chế Quét Động (Whitelist) bằng danh sách chỉ tiêu trong bộ từ điển.
    Tự động phân biệt cấu trúc Bảng kê và Bảng phẳng trong Phụ lục.
    """
    tree = ET.parse(duong_dan_file)
    root = tree.getroot()

    def lay_gia_tri(node_goc, ten_the):
        for elem in node_goc.iter():
            if elem.tag.endswith(f"}}{ten_the}") or elem.tag == ten_the:
                return elem.text
        return None

    ma_tkhai = lay_gia_tri(root, "maTKhai")
    # Ánh xạ từ mã số ra tên form trong từ điển (VD: "03/TNDN")
    ten_form = MAP_TEN_TO_KHAI.get(ma_tkhai, "03/TNDN")

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
    # 1. TRÍCH XUẤT TỜ KHAI CHÍNH (QUÉT ĐỘNG DỰA VÀO TỪ ĐIỂN)
    # =========================================================================
    # Lấy ra danh sách các Key nằm trong từ điển để làm Whitelist
    tu_dien_chinh = TU_DIEN_TO_KHAI.get(ten_form, {}).get("ToKhaiChinh", {})
    danh_sach_hop_le = list(tu_dien_chinh.keys())

    ctieu_chinh_node = None
    for elem in root.iter():
        if elem.tag.endswith("}CTieuTKhaiChinh") or elem.tag == "CTieuTKhaiChinh":
            ctieu_chinh_node = elem
            break

    if ctieu_chinh_node is not None:
        # Quét xuyên mọi lớp thẻ lồng nhau trong CTieuTKhaiChinh
        for child in ctieu_chinh_node.iter():
            tag_name = child.tag.split('}')[-1]

            # Chỉ nhặt các thẻ tồn tại trong từ điển và có chứa dữ liệu
            if tag_name in danh_sach_hop_le and child.text is not None and child.text.strip():
                ket_qua["ChiTieuChinh"][tag_name] = {
                    "GiaTri": child.text,
                    "DienGiai": tu_dien_chinh.get(tag_name, f"Chỉ tiêu {tag_name}")
                }

    # =========================================================================
    # 2. TRÍCH XUẤT PHỤ LỤC (QUÉT ĐỆ QUY THEO CẤU TRÚC THẺ TAG BAO NGOÀI)
    # =========================================================================
    phu_luc_node = None
    for elem in root.iter():
        if elem.tag.endswith("}PLuc") or elem.tag == "PLuc":
            phu_luc_node = elem
            break

    if phu_luc_node is not None:
        map_pl = {
            "PLuc_03_1A_TNDN": ("PL 03-1A", "PL 03-1A"),
            "PL03_1A_TNDN": ("PL 03-1A", "PL 03-1A"),
            "PLuc_03_1B_TNDN": ("PL 03-1B", "PL 03-1B"),
            "PL03_1B_TNDN": ("PL 03-1B", "PL 03-1B"),
            "PLuc_03_1C_TNDN": ("PL 03-1C", "PL 03-1C"),
            "PL03_1C_TNDN": ("PL 03-1C", "PL 03-1C"),
            "PLuc_03_2_TNDN": ("PL 03-2", "PL 03-2"),
            "PLuc_03_3A_TNDN": ("PL 03-3A", "PL_UU_DAI"),
            "PL03_3A_TNDN": ("PL 03-3A", "PL_UU_DAI"),
            "PLuc_03_3B_TNDN": ("PL 03-3B", "PL_UU_DAI"),
            "PLuc_03_3C_TNDN": ("PL 03-3C", "PL_UU_DAI"),
            "PLuc_03_3D_TNDN": ("PL 03-3D", "PL_UU_DAI"),
            "PLuc_03_4_TNDN": ("PL 03-4", "PL 03-4"),
            "PLuc_03_5_TNDN": ("PL 03-5", "PL 03-5"),
            "PLuc_03_6_TNDN": ("PL 03-6", "PL_QUY_KHCN"),
            "PLuc_03_6A_TNDN": ("PL 03-6A", "PL_QUY_KHCN"),
            "PLuc_03_6B_TNDN": ("PL 03-6B", "PL_QUY_KHCN"),
            "PLuc_03_8_TNDN": ("PL 03-8", "PL 03-8"),
            "PLuc_03_8A_TNDN": ("PL 03-8A", "PL 03-8A"),
            "PLuc_03_8B_TNDN": ("PL 03-8B", "PL 03-8B"),
            "PLuc_03_8C_TNDN": ("PL 03-8C", "PL 03-8C"),
            "PLuc_03_9_TNDN": ("PL 03-9", "PL 03-9"),
            "PL_GDLK2-01": ("PL 01/NĐ132", "PL 01/NĐ132"),
            "PL_GDLK2-02": ("PL 02/NĐ132", "PL 02/NĐ132"),
            "PL_GDLK2-03": ("PL 03/NĐ132", "PL 03/NĐ132"),
            "PL_GDLK2-04": ("PL 04/NĐ132", "PL 04/NĐ132")
        }

        # Hàm đệ quy: Giữ nguyên cấu trúc cây XML để làm Tên Dòng
        def parse_appendix_recursively(node, current_path, result_dict, tu_dien_pl):
            for child in list(node):
                tag = child.tag.split('}')[-1]
                sub_children = list(child)

                # Bỏ qua các thẻ hệ thống rỗng (VD: <co>0</co>, <khong>0</khong>) để tránh làm rác bảng
                if tag in ["co", "khong"] and len(sub_children) == 0:
                    continue

                if len(sub_children) > 0:
                    # Là thẻ bao ngoài (Ví dụ: Muc_I, Dong_1, BangChiTietSoLo)
                    node_id = child.attrib.get('id', '').replace('ID_', '')
                    path_name = f"{tag} ({node_id})" if node_id else tag
                    parse_appendix_recursively(child, current_path + [path_name], result_dict, tu_dien_pl)
                else:
                    # Là thẻ lá chứa dữ liệu (Ví dụ: ct03, ct2)
                    if child.text is not None and child.text.strip() != "":
                        val = child.text.strip()
                        # Dùng chuỗi đường dẫn thẻ bao ngoài làm Tên Dòng
                        row_name = " -> ".join(current_path) if current_path else "FLAT_TABLE"

                        if row_name not in result_dict:
                            result_dict[row_name] = {}

                        # Ghép từ điển nếu có, không có thì hiện nguyên tag XML
                        if row_name == "FLAT_TABLE":
                            result_dict[row_name][tag] = {
                                "GiaTri": val,
                                "DienGiai": tu_dien_pl.get(tag, f"[{tag}]") if tu_dien_pl else f"[{tag}]"
                            }
                        else:
                            dien_giai_cot = tu_dien_pl.get(tag, f"[{tag}]") if tu_dien_pl else f"[{tag}]"
                            result_dict[row_name][dien_giai_cot] = val

        # Tiến hành quét cho từng Phụ lục
        for pl_child in phu_luc_node:
            tag_pl = pl_child.tag.split('}')[-1]

            if tag_pl in map_pl:
                ten_hien_thi, key_tu_dien = map_pl[tag_pl]
                tu_dien_pl = TU_DIEN_TO_KHAI.get(ten_form, {}).get(key_tu_dien, {})
                if not tu_dien_pl:
                    tu_dien_pl = TU_DIEN_TO_KHAI.get("03/TNDN", {}).get(key_tu_dien, {})

                extracted_data = {}
                parse_appendix_recursively(pl_child, [], extracted_data, tu_dien_pl)

                if extracted_data:
                    # NẾU LÀ BẢNG PHẲNG (Không có thẻ bao ngoài, chỉ có các the lá độc lập)
                    if len(extracted_data) == 1 and "FLAT_TABLE" in extracted_data:
                        ket_qua["PhuLuc"][ten_hien_thi] = {"IsBangKe": False, "DuLieu": extracted_data["FLAT_TABLE"]}

                    # NẾU LÀ BẢNG KÊ / MA TRẬN
                    else:
                        grid_data = {}
                        for r_name, r_data in extracted_data.items():
                            if r_name == "FLAT_TABLE":
                                # Nếu có dữ liệu hỗn hợp (vừa phẳng vừa lưới), đẩy phần phẳng vào dòng "Dữ liệu chung"
                                flat_row = {}
                                for tag_key, info in r_data.items():
                                    flat_row[info["DienGiai"]] = info["GiaTri"]
                                grid_data["Dữ liệu chung"] = flat_row
                            else:
                                grid_data[r_name] = r_data

                        ket_qua["PhuLuc"][ten_hien_thi] = {"IsBangKe": True, "DuLieu": grid_data}

        # --- Xử lý riêng Phụ lục Giải trình KHBS (Bảng Kê) ---
        # (Đoạn này mày giữ nguyên code bên dưới)

        # --- Xử lý riêng Phụ lục Giải trình KHBS (Bảng Kê) ---
        pl01_1_khbs = None
        for elem in phu_luc_node.iter():
            if elem.tag.endswith("PL01_1_KHBS"):
                pl01_1_khbs = elem
                break

        if pl01_1_khbs is not None:
            ds_hso = None
            for elem in pl01_1_khbs.iter():
                if elem.tag.endswith("DSachHSo"):
                    ds_hso = elem
                    break

            if ds_hso is not None:
                khbs_rows = []
                for bke in ds_hso.iter():
                    if bke.tag.endswith("BKeHSo"):
                        ten_hso = lay_gia_tri(bke, "ten_HSo") or "Tờ khai"
                        for chi_tiet in bke.iter():
                            if chi_tiet.tag.endswith("ChiTiet"):
                                dong = {"Tên tờ khai": ten_hso}
                                dong["Mã CT"] = lay_gia_tri(chi_tiet, "ct3_ma") or ""
                                dong["Tên chỉ tiêu"] = lay_gia_tri(chi_tiet, "ct3_ten") or ""
                                dong["Số đã kê khai (ct04)"] = lay_gia_tri(chi_tiet, "ct04") or "0"
                                dong["Số điều chỉnh (ct05)"] = lay_gia_tri(chi_tiet, "ct05") or "0"
                                dong["Chênh lệch (ct06)"] = lay_gia_tri(chi_tiet, "ct06") or "0"
                                if dong["Mã CT"]:
                                    khbs_rows.append(dong)

                if khbs_rows:
                    ket_qua["PhuLuc"]["Giải trình KHBS (PL01-1)"] = {
                        "IsBangKe": True,
                        "DuLieu": {f"{i + 1}": row for i, row in enumerate(khbs_rows)}
                    }

    return ket_qua