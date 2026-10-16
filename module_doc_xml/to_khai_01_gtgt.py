import xml.etree.ElementTree as ET
from module_doc_xml.tu_dien_chi_tieu import TU_DIEN_TO_KHAI


def phan_tich_xml(duong_dan_file):
    """
    Đọc và trích xuất dữ liệu từ tờ khai 01/GTGT.
    Định tuyến và lấy chính xác danh sách chỉ tiêu theo từng phiên bản Thông tư.
    """
    tree = ET.parse(duong_dan_file)
    root = tree.getroot()

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
            "KieuKy": lay_gia_tri(root, "kieuKy"),  # Bổ sung meta-data kiểu kỳ (M hoặc Q)
            "CoQuanThue": lay_gia_tri(root, "maCQTNoiNop"),
            "SoLan": so_lan_val,
            "LanBoSung": so_lan_val
        },
        "SoLan": so_lan_val,
        "LanBoSung": so_lan_val,
        "ChiTieuChinh": {},
        "PhuLuc": {}
    }

    # ĐỊNH TUYẾN DANH SÁCH CHỈ TIÊU CHUẨN THEO MÃ TỜ KHAI
    if ma_tkhai == "01":
        # Mẫu cũ (TT26) - Có ct39, không có ct23a, ct24a, ct39a
        danh_sach_hop_le = [
            "ct21", "ct22", "ct23", "ct24", "ct25", "ct26", "ct27", "ct28",
            "ct29", "ct30", "ct31", "ct32", "ct33", "ct32a", "ct34", "ct35",
            "ct36", "ct37", "ct38", "ct39", "ct40a", "ct40b", "ct40", "ct41",
            "ct42", "ct43"
        ]
    elif ma_tkhai == "842":
        # Mẫu mới (TT80) - Có ct23a, ct24a, ct39a, không có ct39
        danh_sach_hop_le = [
            "ct21", "ct22", "ct23", "ct24", "ct23a", "ct24a", "ct25", "ct26",
            "ct27", "ct28", "ct29", "ct30", "ct31", "ct32", "ct33", "ct32a",
            "ct34", "ct35", "ct36", "ct37", "ct38", "ct39a", "ct40a", "ct40b",
            "ct40", "ct41", "ct42", "ct43"
        ]
    else:
        danh_sach_hop_le = []

    # =========================================================================
    # 1. TRÍCH XUẤT TỜ KHAI CHÍNH
    # =========================================================================
    ctieu_chinh_node = None
    for elem in root.iter():
        if elem.tag.endswith("}CTieuTKhaiChinh") or elem.tag == "CTieuTKhaiChinh":
            ctieu_chinh_node = elem
            break

    if ctieu_chinh_node is not None:
        tu_dien = TU_DIEN_TO_KHAI.get("01/GTGT", {})

        # Quét sâu qua các thẻ lồng nhau nhưng chỉ nhặt các thẻ nằm trong danh_sach_hop_le
        for child in ctieu_chinh_node.iter():
            tag_name = child.tag.split('}')[-1]

            if tag_name in danh_sach_hop_le and child.text is not None and child.text.strip():
                gia_tri = child.text
                dien_giai = tu_dien.get(tag_name, f"Chỉ tiêu {tag_name}")

                ket_qua["ChiTieuChinh"][tag_name] = {
                    "GiaTri": gia_tri,
                    "DienGiai": dien_giai
                }

    # =========================================================================
    # 2. TRÍCH XUẤT PHỤ LỤC KHAI BỔ SUNG (NẾU CÓ)
    # =========================================================================
    pl01_1_khbs = None
    for elem in root.iter():
        if elem.tag.endswith("}PL01_1_KHBS") or elem.tag == "PL01_1_KHBS":
            pl01_1_khbs = elem
            break

    if pl01_1_khbs is not None:
        ds_hso = None
        for elem in pl01_1_khbs.iter():
            if elem.tag.endswith("}DSachHSo"):
                ds_hso = elem
                break

        if ds_hso is not None:
            danh_sach_dong = []
            for bke in ds_hso.iter():
                if bke.tag.endswith("}BKeHSo"):
                    ten_hso = lay_gia_tri(bke, "ten_HSo") or "Tờ khai"
                    for chi_tiet in bke.iter():
                        if chi_tiet.tag.endswith("}ChiTiet"):
                            dong = {"Tên tờ khai": ten_hso}

                            ma_chi_tieu = lay_gia_tri(chi_tiet, "ct3_ma")
                            ten_chi_tieu = lay_gia_tri(chi_tiet, "ct3_ten")

                            dong["Mã CT"] = ma_chi_tieu if ma_chi_tieu else ""
                            dong["Tên chỉ tiêu"] = ten_chi_tieu if ten_chi_tieu else ""
                            dong["Số đã kê khai (ct04)"] = lay_gia_tri(chi_tiet, "ct04") or "0"
                            dong["Số điều chỉnh (ct05)"] = lay_gia_tri(chi_tiet, "ct05") or "0"
                            dong["Chênh lệch (ct06)"] = lay_gia_tri(chi_tiet, "ct06") or "0"
                            dong["Lý do (ct8)"] = lay_gia_tri(chi_tiet, "ct8") or ""

                            if dong["Mã CT"]:
                                danh_sach_dong.append(dong)

            if danh_sach_dong:
                ket_qua["PhuLuc"]["Giải trình KHBS (PL01-1)"] = {
                    "IsBangKe": True,
                    "DuLieu": {f"{i + 1}": row for i, row in enumerate(danh_sach_dong)}
                }

    return ket_qua