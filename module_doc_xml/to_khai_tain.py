import xml.etree.ElementTree as ET
from module_doc_xml.tu_dien_chi_tieu import TU_DIEN_TO_KHAI


def phan_tich_xml(duong_dan_file):
    """
    Đọc và trích xuất dữ liệu từ Tờ khai 01/TAIN và Quyết toán 02/TAIN.
    Các bảng kê chi tiết sẽ được đẩy vào "Phụ Lục" để hiển thị trên lưới Grid.
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

    dict_bk = TU_DIEN_TO_KHAI.get("TAIN", {}).get("BangKe", {})
    dict_tc = TU_DIEN_TO_KHAI.get("TAIN", {}).get("ChiTieuChinh", {})

    # =========================================================================
    # 1. TRÍCH XUẤT CÁC BẢNG CHI TIẾT TÀI NGUYÊN
    # =========================================================================
    bang_chi_tiet = None
    for elem in root.iter():
        if elem.tag.endswith("BangChiTietTNguyen"):
            bang_chi_tiet = elem
            break

    if bang_chi_tiet is not None:
        # Lấy các chỉ tiêu Tổng cộng chung của Tờ khai
        for tag in ["tongSanLuong", "tongThuePhaiNop", "tongThueDaKhai", "tongChenhLech"]:
            val = lay_gia_tri(bang_chi_tiet, tag)
            if val is not None:
                dien_giai = dict_tc.get(tag, tag)
                ket_qua["ChiTieuChinh"][tag] = {"GiaTri": val, "DienGiai": dien_giai}

        # --- A.I. Khoáng sản ---
        khoang_san_rows = []
        for mo in bang_chi_tiet.iter():
            if mo.tag.endswith("MoKhoangSan"):
                ten_mo = lay_gia_tri(mo, "ten_moKhoangSan") or ""
                for nd in mo.iter():
                    if nd.tag.endswith("NoiDungMoKhoangSan"):
                        row = {"Tên mỏ khoáng sản": ten_mo}
                        for child in nd:
                            tag_name = child.tag.split('}')[-1]
                            if tag_name in ["ct2_tenKhoangSan", "ct3", "ct4", "ct5", "ct6", "ct7", "ct8", "ct9",
                                            "ct10"]:
                                dien_giai = dict_bk.get(tag_name, f"Chỉ tiêu {tag_name}")
                                row[dien_giai] = child.text if child.text else "0"
                        if len(row) > 1:
                            khoang_san_rows.append(row)
        if khoang_san_rows:
            ket_qua["PhuLuc"]["I. Khoáng sản"] = {"IsBangKe": True,
                                                  "DuLieu": {f"{i + 1}": row for i, row in enumerate(khoang_san_rows)}}

        # --- A.II. Tài nguyên khác ---
        tn_khac_rows = []
        for nd in bang_chi_tiet.iter():
            if nd.tag.endswith("NoiDungTaiNguyenKhac"):
                row = {}
                for child in nd:
                    tag_name = child.tag.split('}')[-1]
                    if tag_name.startswith("ct"):
                        dien_giai = dict_bk.get(tag_name, f"Chỉ tiêu {tag_name}")
                        row[dien_giai] = child.text if child.text else "0"
                if row:
                    tn_khac_rows.append(row)
        if tn_khac_rows:
            ket_qua["PhuLuc"]["II. Tài nguyên khác"] = {"IsBangKe": True, "DuLieu": {f"{i + 1}": row for i, row in
                                                                                     enumerate(tn_khac_rows)}}

        # --- B. Thu mua nộp thay ---
        thu_mua_rows = []
        for nd in bang_chi_tiet.iter():
            if nd.tag.endswith("ThueTaiNguyenThuMuaNopThay"):
                row = {}
                for child in nd:
                    tag_name = child.tag.split('}')[-1]
                    if tag_name.startswith("ct"):
                        dien_giai = dict_bk.get(tag_name, f"Chỉ tiêu {tag_name}")
                        row[dien_giai] = child.text if child.text else "0"
                if row:
                    thu_mua_rows.append(row)
        if thu_mua_rows:
            ket_qua["PhuLuc"]["B. Thu mua nộp thay"] = {"IsBangKe": True, "DuLieu": {f"{i + 1}": row for i, row in
                                                                                     enumerate(thu_mua_rows)}}

        # --- C. Bắt giữ, tịch thu ---
        bat_giu_rows = []
        for nd in bang_chi_tiet.iter():
            if nd.tag.endswith("ThueTaiNguyenBatGiuTichThu"):
                row = {}
                for child in nd:
                    tag_name = child.tag.split('}')[-1]
                    if tag_name.startswith("ct"):
                        dien_giai = dict_bk.get(tag_name, f"Chỉ tiêu {tag_name}")
                        row[dien_giai] = child.text if child.text else "0"
                if row:
                    bat_giu_rows.append(row)
        if bat_giu_rows:
            ket_qua["PhuLuc"]["C. Bắt giữ, tịch thu"] = {"IsBangKe": True, "DuLieu": {f"{i + 1}": row for i, row in
                                                                                      enumerate(bat_giu_rows)}}

    # =========================================================================
    # 2. TRÍCH XUẤT PHỤ LỤC 01-1/TAIN (Nếu có)
    # =========================================================================
    pl01 = None
    for elem in root.iter():
        if elem.tag.endswith("PLuc_01_1_TAIN"):
            pl01 = elem
            break

    if pl01 is not None:
        pl_rows = []
        for nha_may in pl01.iter():
            if nha_may.tag.endswith("TenNhaMay"):
                # Dòng gốc của nhà máy
                row_cha = {}
                for child in nha_may:
                    # Bỏ qua thẻ con chứa địa bàn, chỉ lấy thuộc tính ngang cấp
                    if not list(child):
                        tag_name = child.tag.split('}')[-1]
                        if tag_name in ["ten_nhaMay", "ma_nhaMay", "ct10_a", "ct11_a", "ct12_a"]:
                            dien_giai = dict_bk.get(tag_name, tag_name)
                            row_cha[dien_giai] = child.text if child.text else "0"
                if row_cha:
                    pl_rows.append(row_cha)

                # Dòng địa bàn phân bổ bên trong nhà máy đó
                for db in nha_may.iter():
                    if db.tag.endswith("DiaBanPhanBo"):
                        row_con = {"[05] Tên nhà máy thủy điện": "    ↳ (Địa bàn phân bổ)"}
                        for child in db:
                            tag_name = child.tag.split('}')[-1]
                            if tag_name in ["ct05", "ct06", "ten_xa", "ct08_tinh_ten", "ct09_cqt_ten", "ct10", "ct11",
                                            "ct12"]:
                                dien_giai = dict_bk.get(tag_name, tag_name)
                                row_con[dien_giai] = child.text if child.text else "0"
                        if len(row_con) > 1:
                            pl_rows.append(row_con)

        # Xử lý tổng cộng
        tong_cong = {}
        for tag in ["ct13", "ct14"]:
            val = lay_gia_tri(pl01, tag)
            if val:
                if tag == "ct13": tong_cong["[10] Thuế TN phải nộp của nhà máy"] = val
                if tag == "ct14": tong_cong["[12] Thuế phải nộp cho từng tỉnh"] = val

        if pl_rows:
            ket_qua["PhuLuc"]["PL 01-1/TAIN"] = {"IsBangKe": True,
                                                 "DuLieu": {f"{i + 1}": row for i, row in enumerate(pl_rows)}}
            if tong_cong:
                ket_qua["PhuLuc"]["PL 01-1/TAIN"]["DuLieu"]["Tổng cộng"] = tong_cong

    return ket_qua