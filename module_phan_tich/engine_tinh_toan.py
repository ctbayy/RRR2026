import ast
import json
import re
from module_ho_tro.dinh_dang_so import dinh_dang_so_vn
from module_doc_hoadon.invoice_processor import InvoiceProcessor


def _safe_div(a, b):
    """Phép chia an toàn chống crash ZeroDivisionError cho toàn bộ hệ thống"""
    try:
        a_f, b_f = float(a), float(b)
        if b_f == 0.0:
            if a_f > 0:
                return 999999.0
            elif a_f < 0:
                return -999999.0
            else:
                return 0.0
        return a_f / b_f
    except Exception:
        return 0.0


class SafeDivTransformer(ast.NodeTransformer):
    """AST Transformer tự động chuyển mọi phép chia a / b thành _safe_div(a, b)"""
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Div):
            return ast.Call(
                func=ast.Name(id='_safe_div', ctx=ast.Load()),
                args=[node.left, node.right],
                keywords=[]
            )
        return node


def _chuan_hoa_bieu_thuc(expr_str):
    """Chuẩn hóa biểu thức: dấu phẩy thập phân -> dấu chấm, dấu = đơn -> == so sánh"""
    if not expr_str:
        return ""
    s = str(expr_str).strip()
    # Chuyển dấu phẩy giữa các chữ số thành dấu chấm (ví dụ: 0,8 -> 0.8)
    s = re.sub(r'(\d+),(\d+)', r'\1.\2', s)
    # Chuyển dấu '=' đơn độc thành '==' để so sánh bằng an toàn
    s = re.sub(r'(?<![<>=!])=(?!=)', '==', s)
    return s


def safe_eval(expr_str, safe_dict, local_dict=None):
    """Hàm eval an toàn tuyệt đối: bọc phép chia, chuẩn hóa cú pháp, không crash"""
    s = _chuan_hoa_bieu_thuc(expr_str)
    if not s:
        return 0.0
    ns = dict(safe_dict) if safe_dict else {}
    ns['_safe_div'] = _safe_div
    try:
        tree = ast.parse(s, mode='eval')
        tree = SafeDivTransformer().visit(tree)
        ast.fix_missing_locations(tree)
        code = compile(tree, filename='<calc>', mode='eval')
        return eval(code, ns, local_dict)
    except Exception:
        try:
            return eval(s, ns, local_dict)
        except Exception:
            return 0.0


class EnginePhanTich:
    def __init__(self, dict_cong_thuc, log_callback=None):
        self.log_callback = log_callback
        self.danh_sach_cong_thuc = dict_cong_thuc

    def _ghi_log(self, msg):
        if self.log_callback: self.log_callback(msg)

    def _chuan_hoa_chuoi(self, s):
        """Lọc sạch ký tự thừa, bỏ dấu tiếng Việt, đưa về viết thường để so sánh chuẩn xác"""
        s = str(s).lower()
        s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
        s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
        s = re.sub(r'[ìíịỉĩ]', 'i', s)
        s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
        s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
        s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
        s = re.sub(r'[đ]', 'd', s)
        return re.sub(r'[^a-z0-9]', '', s)

    def _boc_tach_ve(self, cong_thuc):
        """Chẻ đôi công thức (Vế A) - (Vế B) do Builder tạo ra để hiển thị riêng lẻ"""
        if cong_thuc.startswith("(") and ") - (" in cong_thuc and cong_thuc.endswith(")"):
            loi = cong_thuc[1:-1]
            parts = loi.split(") - (")
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip(), True
        return cong_thuc, "", False

    def _quet_danh_sach_nam(self, dict_he_thong_to_khai):
        cac_nam = set()
        for ma_form, dict_ky in dict_he_thong_to_khai.items():
            for ky in dict_ky.keys():
                try:
                    nam = str(ky).split('/')[-1]
                    if len(nam) == 4 and nam.isdigit():
                        cac_nam.add(nam)
                except:
                    pass
        return sorted(list(cac_nam))

    def _lay_gia_tri_tu_dict(self, tag, dict_he_thong, is_sum=False, nam_phan_tich="Tất cả các năm", ds_thieu=None,
                             df_cdsps_tt200=None):
        try:
            nam_truy_xuat = str(nam_phan_tich)
            is_n1 = False
            if tag.endswith("_N1"):
                is_n1 = True
                tag = tag[:-3]
                try:
                    nam_truy_xuat = str(int(nam_phan_tich) - 1)
                except:
                    pass

            thanh_phan = [x.strip() for x in tag.split('|')]
            if len(thanh_phan) != 3: return 0.0
            ma_form, phu_luc, ma_ct = thanh_phan

            import pandas as pd
            if "BCTC_TT200" in ma_form and "CDTK_" in phu_luc:
                df_target = None
                if isinstance(df_cdsps_tt200, dict):
                    df_target = df_cdsps_tt200.get(str(nam_truy_xuat))
                    if df_target is None and not is_n1 and len(df_cdsps_tt200) == 1:
                        df_target = list(df_cdsps_tt200.values())[0]
                elif isinstance(df_cdsps_tt200, pd.DataFrame):
                    df_target = df_cdsps_tt200

                # Xử lý trường hợp hỏi số dư năm trước (_N1) nhưng không nạp file năm trước
                if (df_target is None or df_target.empty) and is_n1 and isinstance(df_cdsps_tt200, dict):
                    df_curr = df_cdsps_tt200.get(str(nam_phan_tich))
                    if isinstance(df_curr, pd.DataFrame) and not df_curr.empty:
                        ma_tk = ma_ct.replace('ct', '')
                        dong_tk = df_curr[df_curr['MaTK'] == ma_tk]
                        if dong_tk.empty:
                            dong_tk = df_curr[df_curr['MaTK'].str.startswith(ma_tk)]
                            if 'IsLeaf' in dong_tk.columns and dong_tk['IsLeaf'].any():
                                dong_tk = dong_tk[dong_tk['IsLeaf'] == True]
                        if not dong_tk.empty:
                            # Dư cuối kỳ năm trước = Dư đầu kỳ năm nay
                            if phu_luc in ["CDTK_NoCuoiKy", "CDTK_NoPhatSinh"]:
                                return float(dong_tk["DuNoDauKy"].sum())
                            elif phu_luc in ["CDTK_CoCuoiKy", "CDTK_CoPhatSinh"]:
                                return float(dong_tk["DuCoDauKy"].sum())

                if isinstance(df_target, pd.DataFrame) and not df_target.empty:
                    ma_tk = ma_ct.replace('ct', '')
                    dong_tk = df_target[df_target['MaTK'] == ma_tk]
                    if dong_tk.empty:
                        dong_tk = df_target[df_target['MaTK'].str.startswith(ma_tk)]
                        # Chống Double-Counting: Nếu có phân cấp, chỉ lấy dòng chi tiết (IsLeaf)
                        if 'IsLeaf' in dong_tk.columns and dong_tk['IsLeaf'].any():
                            dong_tk = dong_tk[dong_tk['IsLeaf'] == True]
                    if not dong_tk.empty:
                        val = 0.0
                        if phu_luc == "CDTK_NoPhatSinh":
                            val = dong_tk["PhatSinhNo"].sum()
                        elif phu_luc == "CDTK_CoPhatSinh":
                            val = dong_tk["PhatSinhCo"].sum()
                        elif phu_luc == "CDTK_NoCuoiKy":
                            val = dong_tk["DuNoCuoiKy"].sum()
                        elif phu_luc == "CDTK_CoCuoiKy":
                            val = dong_tk["DuCoCuoiKy"].sum()
                        elif phu_luc == "CDTK_NoDauKy":
                            val = dong_tk["DuNoDauKy"].sum()
                        elif phu_luc == "CDTK_CoDauKy":
                            val = dong_tk["DuCoDauKy"].sum()
                        return float(val)
                    else:
                        return 0.0
                else:
                    if ds_thieu is not None: ds_thieu.append(f"Bảng CĐSPS TT200 (Năm {nam_truy_xuat})")
                    return 0.0

            dict_ky_cua_form = dict_he_thong.get(ma_form, {})
            if not dict_ky_cua_form:
                MAP_MA_XML = {
                    "01/GTGT": ["01", "842"], "02/GTGT": ["02", "844"],
                    "03/TNDN": ["03", "892"], "04/GTGT": ["847"],
                    "04/TNDN": ["833"], "05/QTT": ["953"], "05/KK": ["864"],
                    "TAIN": ["832", "924"],
                    "BCTC_TT200": ["402", "465", "671", "672", "675", "676"],
                    "BCTC_TT133": ["683", "684", "685", "686","699"]
                }
                danh_sach_ma_can_tim = []
                for key_map, list_ma in MAP_MA_XML.items():
                    if key_map in ma_form: danh_sach_ma_can_tim.extend(list_ma)

                for key_dict, dict_ky in dict_he_thong.items():
                    if isinstance(dict_ky, dict):
                        ma_tk_goc = ""
                        for ky, data_ky in dict_ky.items():
                            if isinstance(data_ky, dict) and "ThongTinChung" in data_ky:
                                ttc = data_ky.get("ThongTinChung", {})
                                ma_tk_goc = str(ttc.get("maTKhai", ttc.get("MaTKhai", ttc.get("MaToKhai", "")))).strip()
                                if ma_tk_goc: break
                        if not ma_tk_goc and "ThongTinChung" in dict_ky:
                            ttc = dict_ky.get("ThongTinChung", {})
                            ma_tk_goc = str(ttc.get("maTKhai", ttc.get("MaTKhai", ttc.get("MaToKhai", "")))).strip()
                        if ma_tk_goc and ma_tk_goc in danh_sach_ma_can_tim:
                            dict_ky_cua_form = dict_ky
                            break

                if not dict_ky_cua_form:
                    for k, v in dict_he_thong.items():
                        if str(ma_form).replace(" ", "") in str(k).replace(" ", ""):
                            dict_ky_cua_form = v
                            break

            if not dict_ky_cua_form:
                if ds_thieu is not None: ds_thieu.append(f"Tờ khai/BCTC {ma_form}")
                return 0.0

            if "ThongTinChung" in dict_ky_cua_form:
                ky_kk = str(dict_ky_cua_form.get("ThongTinChung", {}).get("KyKeKhai", nam_truy_xuat))
                dict_ky_cua_form = {ky_kk: dict_ky_cua_form}

            tong_cong = 0.0
            co_du_lieu_nam = False

            for ky, dict_to_khai in dict_ky_cua_form.items():
                if nam_truy_xuat != "Tất cả các năm" and str(nam_truy_xuat) not in str(ky): continue
                co_du_lieu_nam = True
                gia_tri_str = "0"
                phu_luc_thuc_te = phu_luc
                if phu_luc.startswith("CDKT_"):
                    phu_luc_thuc_te = "B01_CDKT"
                elif phu_luc.startswith("KQKD_"):
                    phu_luc_thuc_te = "B02_KQKD"
                elif phu_luc.startswith("LCTT_"):
                    phu_luc_thuc_te = "B03_LCTT"

                if phu_luc == "ChiTieuChinh":
                    item_ct = dict_to_khai.get("ChiTieuChinh", {}).get(ma_ct, "0")
                    gia_tri_str = item_ct.get("GiaTri", "0") if isinstance(item_ct, dict) else item_ct
                elif phu_luc_thuc_te in ["B01_CDKT", "B02_KQKD", "B03_LCTT"]:
                    dict_bctc = dict_to_khai.get(phu_luc_thuc_te, {}).get(ma_ct, {})
                    for ten_cot, gia_tri in dict_bctc.items():
                        ten_cot_lower = ten_cot.lower()
                        if "cuoinam" in phu_luc.lower() and "cuối" in ten_cot_lower:
                            gia_tri_str = gia_tri; break
                        elif "daunam" in phu_luc.lower() and "đầu" in ten_cot_lower:
                            gia_tri_str = gia_tri; break
                        elif "namnay" in phu_luc.lower() and "nay" in ten_cot_lower:
                            gia_tri_str = gia_tri; break
                        elif "namtruoc" in phu_luc.lower() and "trước" in ten_cot_lower:
                            gia_tri_str = gia_tri; break
                        elif "cuối" in ten_cot_lower or "nay" in ten_cot_lower or "phát sinh" in ten_cot_lower:
                            gia_tri_str = gia_tri
                elif phu_luc.startswith("CDTK_"):
                    dict_cdtk = dict_to_khai.get("B04_CDTK", {}).get(ma_ct, {})
                    map_cot = {
                        "CDTK_NoDauKy": "Dư đầu kỳ (Nợ)", "CDTK_CoDauKy": "Dư đầu kỳ (Có)",
                        "CDTK_NoPhatSinh": "Phát sinh (Nợ)", "CDTK_CoPhatSinh": "Phát sinh (Có)",
                        "CDTK_NoCuoiKy": "Dư cuối kỳ (Nợ)", "CDTK_CoCuoiKy": "Dư cuối kỳ (Có)"
                    }
                    ten_cot_can_tim = map_cot.get(phu_luc, "")
                    gia_tri_str = dict_cdtk.get(ten_cot_can_tim, "0")
                else:
                    dict_pl = dict_to_khai.get("PhuLuc", {}).get(phu_luc, {})
                    if not dict_pl.get("IsBangKe", False):
                        gia_tri_str = dict_pl.get("DuLieu", {}).get(ma_ct, {}).get("GiaTri", "0")

                try:
                    tong_cong += float(str(gia_tri_str).replace(",", ""))
                except ValueError:
                    pass

            if not co_du_lieu_nam:
                if ds_thieu is not None: ds_thieu.append(f"Tờ khai {ma_form} (Năm {nam_truy_xuat})")
                return 0.0
            return tong_cong
        except Exception:
            return 0.0

    def _lay_gia_tri_tai_khoan(self, tag_tk, dict_he_thong, nam_phan_tich="Tất cả các năm", ds_thieu=None,
                               df_cdsps_tt200=None):
        try:
            nam_truy_xuat = str(nam_phan_tich)
            is_n1 = False
            if tag_tk.endswith("_N1"):
                is_n1 = True
                tag_tk = tag_tk[:-3]
                try:
                    nam_truy_xuat = str(int(nam_phan_tich) - 1)
                except:
                    pass

            loai_so, ma_tk = [x.strip() for x in tag_tk.split('|')]
            import pandas as pd
            df_target = None
            if isinstance(df_cdsps_tt200, dict):
                df_target = df_cdsps_tt200.get(str(nam_truy_xuat))
                if df_target is None and not is_n1 and len(df_cdsps_tt200) == 1:
                    df_target = list(df_cdsps_tt200.values())[0]
            elif isinstance(df_cdsps_tt200, pd.DataFrame):
                df_target = df_cdsps_tt200

            # Fallback cho _N1: Dư cuối kỳ năm trước = Dư đầu kỳ năm nay
            if (df_target is None or df_target.empty) and is_n1 and isinstance(df_cdsps_tt200, dict):
                df_curr = df_cdsps_tt200.get(str(nam_phan_tich))
                if isinstance(df_curr, pd.DataFrame) and not df_curr.empty:
                    dong_tk_curr = df_curr[df_curr['MaTK'] == ma_tk]
                    if dong_tk_curr.empty:
                        dong_tk_curr = df_curr[df_curr['MaTK'].str.startswith(ma_tk)]
                        if 'IsLeaf' in dong_tk_curr.columns and dong_tk_curr['IsLeaf'].any():
                            dong_tk_curr = dong_tk_curr[dong_tk_curr['IsLeaf'] == True]
                    if not dong_tk_curr.empty:
                        if loai_so == "DU_NO":
                            return float(dong_tk_curr["DuNoDauKy"].sum())
                        elif loai_so == "DU_CO":
                            return float(dong_tk_curr["DuCoDauKy"].sum())

            if isinstance(df_target, pd.DataFrame) and not df_target.empty:
                dong_tk = df_target[df_target['MaTK'] == ma_tk]
                if dong_tk.empty:
                    dong_tk = df_target[df_target['MaTK'].str.startswith(ma_tk)]
                    # Chống Double-Counting: Nếu có phân cấp, chỉ lấy dòng chi tiết (IsLeaf)
                    if 'IsLeaf' in dong_tk.columns and dong_tk['IsLeaf'].any():
                        dong_tk = dong_tk[dong_tk['IsLeaf'] == True]
                if not dong_tk.empty:
                    val = 0.0
                    if loai_so == "PS_NO":
                        val = dong_tk["PhatSinhNo"].sum()
                    elif loai_so == "PS_CO":
                        val = dong_tk["PhatSinhCo"].sum()
                    elif loai_so == "DU_NO":
                        val = dong_tk["DuNoCuoiKy"].sum()
                    elif loai_so == "DU_CO":
                        val = dong_tk["DuCoCuoiKy"].sum()
                    elif loai_so == "SD_NO":
                        val = dong_tk["DuNoDauKy"].sum()
                    elif loai_so == "SD_CO":
                        val = dong_tk["DuCoDauKy"].sum()
                    return float(val)
                else:
                    return 0.0

            tong_tien = 0.0
            co_du_lieu = False
            for ma_form, dict_ky in dict_he_thong.items():
                if isinstance(dict_ky, dict) and "ThongTinChung" in dict_ky:
                    ky_kk = str(dict_ky.get("ThongTinChung", {}).get("KyKeKhai", nam_truy_xuat))
                    dict_ky = {ky_kk: dict_ky}
                for ky, ket_qua in dict_ky.items():
                    if nam_truy_xuat != "Tất cả các năm" and str(nam_truy_xuat) not in str(ky): continue
                    dict_cdtk = ket_qua.get("B04_CDTK", {})
                    if not dict_cdtk: continue
                    co_du_lieu = True
                    for key_ct, row_data in dict_cdtk.items():
                        tk_hien_tai = key_ct.replace("ct", "")
                        if tk_hien_tai == ma_tk:
                            val_str = "0"
                            if loai_so == "PS_NO":
                                val_str = row_data.get("Phát sinh (Nợ)", "0")
                            elif loai_so == "PS_CO":
                                val_str = row_data.get("Phát sinh (Có)", "0")
                            elif loai_so == "DU_NO":
                                val_str = row_data.get("Dư cuối kỳ (Nợ)", "0")
                            elif loai_so == "DU_CO":
                                val_str = row_data.get("Dư cuối kỳ (Có)", "0")
                            elif loai_so == "SD_NO":
                                val_str = row_data.get("Dư đầu kỳ (Nợ)", "0")
                            elif loai_so == "SD_CO":
                                val_str = row_data.get("Dư đầu kỳ (Có)", "0")
                            try:
                                tong_tien += float(str(val_str).replace(",", ""))
                            except ValueError:
                                pass

            if not co_du_lieu:
                if ds_thieu is not None: ds_thieu.append(f"CĐTK / (Năm {nam_truy_xuat})")
                return 0.0
            return tong_tien
        except Exception:
            return 0.0

    def _tinh_tong_mang(self, tag_sum, df_hoa_don, nam_phan_tich="Tất cả các năm", dict_he_thong_to_khai=None,
                        ds_thieu=None):
        try:
            nam_truy_xuat = str(nam_phan_tich)
            if tag_sum.endswith("_N1"):
                tag_sum = tag_sum[:-3]
                try:
                    nam_truy_xuat = str(int(nam_phan_tich) - 1)
                except:
                    pass

            thanh_phan = [x.strip() for x in tag_sum.split('|')]
            if len(thanh_phan) != 2: return 0.0
            loai_hd, ten_cot = thanh_phan

            import pandas as pd
            if not isinstance(df_hoa_don, pd.DataFrame) or df_hoa_don.empty:
                ten_loai = "Hóa đơn Bán ra" if "BAN_RA" in loai_hd else "Hóa đơn Mua vào"
                if ds_thieu is not None: ds_thieu.append(ten_loai)
                return 0.0

            ky_kham_xet = set()
            ky_nam = set()
            if dict_he_thong_to_khai:
                for ma_form, dict_ky in dict_he_thong_to_khai.items():
                    for ky in dict_ky.keys():
                        if nam_truy_xuat == "Tất cả các năm" or str(nam_truy_xuat) in str(ky):
                            ky_str = str(ky).strip().upper()
                            if len(ky_str) == 4 and ky_str.isdigit():
                                ky_nam.add(ky_str)
                            else:
                                if len(ky_str.split('/')[0]) == 1 and "Q" not in ky_str:
                                    t, n = ky_str.split('/')
                                    ky_kham_xet.add(f"0{t}/{n}")
                                    ky_kham_xet.add(f"Q{t}/{n}")
                                else:
                                    ky_kham_xet.add(ky_str)

            df_filtered = df_hoa_don.copy()
            if nam_truy_xuat != "Tất cả các năm" and '_Nam' in df_filtered.columns:
                df_filtered = df_filtered[df_filtered['_Nam'] == str(nam_truy_xuat)]

            if ky_kham_xet and '_Thang' in df_filtered.columns and '_Quy' in df_filtered.columns:
                mask_ky = df_filtered['_Thang'].isin(ky_kham_xet) | df_filtered['_Quy'].isin(ky_kham_xet)
                if ky_nam and '_Nam' in df_filtered.columns: mask_ky = mask_ky | df_filtered['_Nam'].isin(ky_nam)
                df_filtered = df_filtered[mask_ky]
            elif ky_nam and '_Nam' in df_filtered.columns:
                mask_ky = df_filtered['_Nam'].isin(ky_nam)
                df_filtered = df_filtered[mask_ky]

            ten_cot_norm = self._chuan_hoa_chuoi(ten_cot)
            tong = 0.0
            for col in df_filtered.columns:
                if self._chuan_hoa_chuoi(col) == ten_cot_norm:
                    tong = float(df_filtered[col].sum())
                    break
            return tong
        except Exception:
            return 0.0

    # ========================================================
    # HÀM BÓC TÁCH VÀ DỊCH TAG TỰ ĐỘNG (DÙNG CHUNG V1 VÀ V2)
    # ========================================================
    def _dich_tag_thanh_so(self, chuoi_goc, nam_hien_tai, df_ban_ra, df_mua_vao, dict_he_thong, df_cdsps, ds_thieu):
        chuoi_tinh = chuoi_goc
        if not chuoi_tinh: return ""

        mang_sum_hd = set(re.findall(r'SUM\[(.*?)\]', chuoi_tinh))
        for m in mang_sum_hd:
            loai_hd = m.split('|')[0].strip()
            dict_nguon = df_ban_ra if "BAN_RA" in loai_hd else df_mua_vao
            val = self._tinh_tong_mang(m, dict_nguon, nam_hien_tai, dict_he_thong, ds_thieu)
            chuoi_tinh = chuoi_tinh.replace(f"SUM[{m}]", str(val))

        mang_sum_tk = set(re.findall(r'SUM_TK\[(.*?)\]', chuoi_tinh))
        for m in mang_sum_tk:
            val = self._lay_gia_tri_tu_dict(m, dict_he_thong, True, nam_hien_tai, ds_thieu)
            chuoi_tinh = chuoi_tinh.replace(f"SUM_TK[{m}]", str(val))

        mang_tk = set(re.findall(r'TK\[(.*?)\]', chuoi_tinh))
        for tk in mang_tk:
            val = self._lay_gia_tri_tai_khoan(tk, dict_he_thong, nam_hien_tai, ds_thieu, df_cdsps)
            chuoi_tinh = chuoi_tinh.replace(f"TK[{tk}]", str(val))

        mang_prev = set(re.findall(r'PREV\[(.*?)\]', chuoi_tinh))
        for p in mang_prev:
            nam_truoc = str(int(nam_hien_tai) - 1) if str(nam_hien_tai).isdigit() else nam_hien_tai
            val = self._lay_gia_tri_tu_dict(p, dict_he_thong, False, nam_truoc, ds_thieu, df_cdsps)
            chuoi_tinh = chuoi_tinh.replace(f"PREV[{p}]", str(val))

        mang_bien = set(re.findall(r'\[(.*?)\]', chuoi_tinh))
        for b in mang_bien:
            if "HD_" in b or b in mang_sum_tk or b in mang_tk: continue
            val = self._lay_gia_tri_tu_dict(b, dict_he_thong, False, nam_hien_tai, ds_thieu, df_cdsps)
            chuoi_tinh = chuoi_tinh.replace(f"[{b}]", str(val))

        return chuoi_tinh

    # ========================================================
    # HÀM THỰC THI CHÍNH (KIẾN TRÚC DUAL-CORE)
    # ========================================================
    def thuc_thi_phan_tich(self, dict_he_thong_to_khai, dict_hd_ban_ra, dict_hd_mua_vao, nam_phan_tich="Tất cả các năm", df_cdsps_tt200=None, loai_bctc="", danh_sach_rule_chon=None):
        ket_qua_phan_tich = []
        df_ban_ra_sach = InvoiceProcessor.loc_hoa_don_tinh_toan(dict_hd_ban_ra)
        df_mua_vao_sach = InvoiceProcessor.loc_hoa_don_tinh_toan(dict_hd_mua_vao)

        # =====================================================================
        # 🟢 BẢN VÁ: ENGINE TỰ ĐỘNG "ĐÁNH HƠI" MÃ XML NẾU UI TRUYỀN VÀO "TỰ ĐỘNG"
        # =====================================================================
        loai_bctc_thuc_te = str(loai_bctc)
        if "200" not in loai_bctc_thuc_te and "133" not in loai_bctc_thuc_te:
            thay_200 = False
            thay_133 = False
            # Lục lọi toàn bộ file XML đã nạp vào RAM
            for key_dict, dict_ky in dict_he_thong_to_khai.items():
                if isinstance(dict_ky, dict):
                    # Quét lớp 1 (Cấu trúc phẳng)
                    if "ThongTinChung" in dict_ky:
                        ma_tk = str(dict_ky["ThongTinChung"].get("maTKhai", "")).strip()
                        if ma_tk in ["402","465","671","672","675","676"]: thay_200 = True
                        elif ma_tk in ["683","684","685","686","699"]: thay_133 = True
                    # Quét lớp 2 (Cấu trúc phân kỳ theo năm)
                    for ky, data_ky in dict_ky.items():
                        if isinstance(data_ky, dict) and "ThongTinChung" in data_ky:
                            ma_tk = str(data_ky["ThongTinChung"].get("maTKhai", "")).strip()
                            if ma_tk in ["402","465","671","672","675","676"]: thay_200 = True
                            elif ma_tk in ["683","684","685","686","699"]: thay_133 = True

            # Ép lại chế độ thực tế
            if thay_200: loai_bctc_thuc_te = "200"
            elif thay_133: loai_bctc_thuc_te = "133"

            self._ghi_log(f"🔍 [Auto-Detect] Chế độ Tự động đã nhận diện được BCTC: TT{loai_bctc_thuc_te}")
        # =====================================================================

        danh_sach_nam = self._quet_danh_sach_nam(dict_he_thong_to_khai) if nam_phan_tich == "Tất cả các năm" else [str(nam_phan_tich)]
        if not danh_sach_nam: danh_sach_nam = ["Chưa xác định"]

        # Cấp phép hàm Toán học an toàn cho eval
        safe_dict = {"__builtins__": None, "abs": abs, "min": min, "max": max, "round": round, "_safe_div": _safe_div}

        for nam_hien_tai in danh_sach_nam:
            self._ghi_log(f"\n{'='*20} BẮT ĐẦU PHÂN TÍCH NĂM {nam_hien_tai} {'='*20}")

            for ma_pt, cfg in self.danh_sach_cong_thuc.items():
                if danh_sach_rule_chon is not None and ma_pt not in danh_sach_rule_chon: continue

                ten_pt = cfg.get("ten_phan_tich", "")
                nhom_pt = cfg.get("nhom", "Chưa phân loại")
                self._ghi_log(f"\nĐang chạy Rule: {ten_pt}")

                # Phiên dịch tự động TT133 <-> TT200 (Giữ nguyên cấu trúc Dict)
                cfg_str = json.dumps(cfg)
                if "200" in loai_bctc_thuc_te:
                    cfg_str = cfg_str.replace("BCTC_TT133", "BCTC_TT200")
                elif "133" in loai_bctc_thuc_te:
                    cfg_str = cfg_str.replace("BCTC_TT200", "BCTC_TT133")
                cfg_chuan = json.loads(cfg_str)

                ds_thieu = []
                is_rui_ro = False
                thong_diep_chot = ""
                gia_tri_a, gia_tri_b, ket_qua_so = 0.0, 0.0, 0.0
                is_ab = False
                ve_a_goc, ve_b_goc = "", ""
                bo_nho_bien = {}

                # =======================================================
                # BỘ ĐỊNH TUYẾN: KIỂM TRA PHIÊN BẢN RULE (DUAL-CORE)
                # =======================================================
                if "bien_so" in cfg_chuan:
                    # 🟢 LUỒNG V2: HYBRID ENGINE
                    danh_sach_bien_goc = cfg_chuan.get("bien_so", {})

                    # 1. Tính toán tất cả các biến
                    for ten_bien, ct_goc in danh_sach_bien_goc.items():
                        ct_so = self._dich_tag_thanh_so(ct_goc, nam_hien_tai, df_ban_ra_sach, df_mua_vao_sach,
                                                        dict_he_thong_to_khai, df_cdsps_tt200, ds_thieu)
                        try:
                            bo_nho_bien[ten_bien] = safe_eval(ct_so, safe_dict)
                        except Exception:
                            bo_nho_bien[ten_bien] = 0.0

                    if len(ds_thieu) == 0:
                        try:
                            # 2. Chạy Biểu thức Logic Rủi ro (Boolean)
                            bieu_thuc_rr = cfg_chuan.get("bieu_thuc_rui_ro", "False")
                            is_rui_ro = bool(safe_eval(bieu_thuc_rr, safe_dict, bo_nho_bien))
                            thong_diep_chot = cfg_chuan.get("thong_diep_rui_ro") if is_rui_ro else cfg_chuan.get(
                                "thong_diep_an_toan")

                            # 3. ĐỒNG BỘ HIỂN THỊ CHUẨN CẢ V1 VÀ V2
                            ht_a = str(cfg_chuan.get("hien_thi_ve_a", "")).strip()
                            ht_b = str(cfg_chuan.get("hien_thi_ve_b", "")).strip()

                            # Tự suy luận biến hiển thị nếu rule chưa khai báo hien_thi_ve_a / b
                            danh_sach_keys = list(danh_sach_bien_goc.keys())
                            if not ht_a and len(danh_sach_keys) >= 1:
                                ht_a = danh_sach_keys[0]
                                if not ht_b and len(danh_sach_keys) >= 2:
                                    ht_b = danh_sach_keys[1]

                            # Tính giá trị số A
                            try:
                                gia_tri_a = float(safe_eval(ht_a, safe_dict, bo_nho_bien)) if ht_a else 0.0
                            except Exception:
                                gia_tri_a = 0.0

                            # Tính giá trị số B
                            if ht_b:
                                try:
                                    gia_tri_b = float(safe_eval(ht_b, safe_dict, bo_nho_bien))
                                except Exception:
                                    gia_tri_b = 0.0
                                is_ab = True
                            else:
                                gia_tri_b = 0.0
                                is_ab = False

                            ket_qua_so = gia_tri_a - gia_tri_b if is_ab else gia_tri_a

                            # Dịch công thức tag gốc để làm tiêu đề vế / tooltip
                            def _tim_tag_goc(ht_expr):
                                if not ht_expr:
                                    return ""
                                if ht_expr in danh_sach_bien_goc:
                                    return danh_sach_bien_goc[ht_expr]
                                expr_tmp = ht_expr
                                for k, tag in danh_sach_bien_goc.items():
                                    expr_tmp = re.sub(r'\b' + re.escape(k) + r'\b', tag, expr_tmp)
                                return expr_tmp

                            ve_a_goc = _tim_tag_goc(ht_a)
                            ve_b_goc = _tim_tag_goc(ht_b) if ht_b else ""

                        except Exception as e:
                            self._ghi_log(f"  ❌ Lỗi logic V2: {e}")
                            continue
                else:
                    # 🟠 LUỒNG V1: ENGINE CŨ
                    cong_thuc_goc = cfg_chuan.get("cong_thuc", "")
                    tien_de_goc = cfg_chuan.get("dieu_kien_tien_de", "")
                    dieu_kien = cfg_chuan.get("dieu_kien_rui_ro", "")
                    ve_a_goc, ve_b_goc, is_ab = self._boc_tach_ve(cong_thuc_goc)

                    tien_de_tinh = self._dich_tag_thanh_so(tien_de_goc, nam_hien_tai, df_ban_ra_sach, df_mua_vao_sach,
                                                           dict_he_thong_to_khai, df_cdsps_tt200, ds_thieu)
                    ct_so = self._dich_tag_thanh_so(cong_thuc_goc, nam_hien_tai, df_ban_ra_sach, df_mua_vao_sach,
                                                    dict_he_thong_to_khai, df_cdsps_tt200, ds_thieu)

                    # NGẮT MẠCH NGAY NẾU THIẾU DỮ LIỆU
                    if len(ds_thieu) > 0:
                        pass
                    else:
                        if tien_de_tinh.strip():
                            try:
                                if not safe_eval(tien_de_tinh, safe_dict):
                                    self._ghi_log(f"  ✅ Không thỏa mãn điều kiện tiền đề.")
                                    # Lấy luôn số liệu thực tế để xuất ra báo cáo
                                    ve_a_tinh, ve_b_tinh, _ = self._boc_tach_ve(ct_so)
                                    try:
                                        gia_tri_a = float(safe_eval(ve_a_tinh, safe_dict)) if is_ab else float(safe_eval(ct_so, safe_dict))
                                    except Exception:
                                        gia_tri_a = 0.0
                                    try:
                                        gia_tri_b = float(safe_eval(ve_b_tinh, safe_dict)) if is_ab else 0.0
                                    except Exception:
                                        gia_tri_b = 0.0

                                    ket_qua_phan_tich.append({
                                        "nam_ap_dung": nam_hien_tai, "nhom": nhom_pt, "ten_phan_tich": ten_pt,
                                        "ve_a_goc": self._dich_cong_thuc(ve_a_goc),
                                        "ve_b_goc": self._dich_cong_thuc(ve_b_goc),
                                        "gia_tri_a": round(gia_tri_a, 2),
                                        "gia_tri_b": round(gia_tri_b, 2),
                                        "is_ab": is_ab,
                                        "ket_qua_so": round(gia_tri_a - gia_tri_b, 2) if is_ab else round(gia_tri_a, 2),
                                        "trang_thai": "AN TOÀN", "is_rui_ro": False,
                                        "chi_tiet_bien": {},
                                        "thong_diep": "Chưa thỏa mãn điều kiện cần để đưa ra cảnh báo rủi ro."
                                    })
                                    continue
                            except Exception as e:
                                self._ghi_log(f"  ❌ Lỗi Điều kiện tiền đề: {e}")
                                continue

                        ve_a_tinh, ve_b_tinh, _ = self._boc_tach_ve(ct_so)
                        try:
                            if is_ab:
                                gia_tri_a = float(safe_eval(ve_a_tinh, safe_dict))
                                gia_tri_b = float(safe_eval(ve_b_tinh, safe_dict))
                                ket_qua_so = gia_tri_a - gia_tri_b
                            else:
                                gia_tri_a = float(safe_eval(ct_so, safe_dict))
                                gia_tri_b = 0.0
                                ket_qua_so = gia_tri_a

                            if dieu_kien:
                                dieu_kien_clean = _chuan_hoa_bieu_thuc(dieu_kien)
                                is_rui_ro = bool(safe_eval(f"{ket_qua_so} {dieu_kien_clean}", safe_dict))
                            thong_diep_chot = cfg_chuan.get("thong_diep_rui_ro") if is_rui_ro else cfg_chuan.get(
                                "thong_diep_an_toan")
                        except Exception as e:
                            self._ghi_log(f"  ❌ Lỗi tính toán V1: {e}")
                            continue

                # =======================================================
                # ĐÓNG GÓI KẾT QUẢ XUẤT RA BÁO CÁO (CHUNG CHO CẢ 2)
                # =======================================================
                if len(ds_thieu) > 0:
                    cac_thieu = list(set(ds_thieu))
                    self._ghi_log(f"  ⚠️ Thiếu dữ liệu: {', '.join(cac_thieu)}")
                    ket_qua_phan_tich.append({
                        "nam_ap_dung": nam_hien_tai, "nhom": nhom_pt, "ten_phan_tich": ten_pt,
                        "ve_a_goc": self._dich_cong_thuc(ve_a_goc) if ve_a_goc else "Chỉ tiêu Vế A",
                        "ve_b_goc": self._dich_cong_thuc(ve_b_goc) if ve_b_goc else "Chỉ tiêu Vế B",
                        "is_ab": is_ab, "ket_qua_so": "Thiếu dữ liệu", "trang_thai": "CHƯA THỂ PHÂN TÍCH",
                        "thong_diep": f"Vui lòng tải lên {', '.join(cac_thieu)} để hệ thống thực hiện đối chiếu.",
                        "is_rui_ro": False, "gia_tri_a": "---", "gia_tri_b": "---",
                        "chi_tiet_bien": {}
                    })
                    continue

                # Chi tiết các biến (nếu có trong V2) để hỗ trợ Tooltip và chi tiết phân tích
                chi_tiet_bien = {}
                if "bien_so" in cfg_chuan and isinstance(bo_nho_bien, dict):
                    chi_tiet_bien = {k: v for k, v in bo_nho_bien.items()}

                # Đảm bảo ket_qua_so, gia_tri_a, gia_tri_b luôn là số thực float
                gia_tri_a_so = round(float(gia_tri_a), 2) if isinstance(gia_tri_a, (int, float)) else 0.0
                gia_tri_b_so = round(float(gia_tri_b), 2) if isinstance(gia_tri_b, (int, float)) else 0.0
                ket_qua_so_val = round(float(ket_qua_so), 2) if isinstance(ket_qua_so, (int, float)) else round(gia_tri_a_so - gia_tri_b_so, 2)

                ket_qua_phan_tich.append({
                    "nam_ap_dung": nam_hien_tai,
                    "nhom": nhom_pt,
                    "ten_phan_tich": ten_pt,
                    "is_rui_ro": is_rui_ro,
                    "thong_diep": thong_diep_chot,
                    "ve_a_goc": self._dich_cong_thuc(ve_a_goc) if ve_a_goc else "Chỉ tiêu Vế A",
                    "ve_b_goc": self._dich_cong_thuc(ve_b_goc) if ve_b_goc else ("Chỉ tiêu Vế B" if is_ab else ""),
                    "is_ab": is_ab,
                    "gia_tri_a": gia_tri_a_so,
                    "gia_tri_b": gia_tri_b_so if is_ab else 0.0,
                    "ket_qua_so": ket_qua_so_val,
                    "chi_tiet_bien": chi_tiet_bien,
                    "trang_thai": "CẢNH BÁO RỦI RO" if is_rui_ro else "AN TOÀN"
                })

        # Cuối cùng chạy luôn cái KHBS
        ket_qua_phan_tich.extend(self._kiem_tra_chuyen_ky_khbs(dict_he_thong_to_khai))

        # =======================================================
        # BỘ SẮP XẾP KẾT QUẢ HIỂN THỊ (RỦI RO -> AN TOÀN -> THIẾU DATA)
        # =======================================================
        def thu_tu_uu_tien(item):
            tt = str(item.get("trang_thai", "")).upper()
            if "CẢNH BÁO" in tt:
                return 1  # Ưu tiên số 1: Lên đỉnh bảng
            elif "AN TOÀN" in tt:
                return 2  # Ưu tiên số 2: Nằm giữa
            elif "CHƯA THỂ" in tt:
                return 3  # Ưu tiên số 3: Dạt xuống đáy bảng (Thiếu dữ liệu)
            else:
                return 4  # Các trường hợp phát sinh khác

        # Chạy lệnh sort ép danh sách tự sắp xếp lại theo trọng số từ 1 đến 4
        ket_qua_phan_tich.sort(key=thu_tu_uu_tien)
        return ket_qua_phan_tich

    def _dich_cong_thuc(self, text):
        if not text: return ""

        def r_sum_tk(m):
            parts = [x.strip() for x in m.group(1).split('|')]
            return f"Tổng nhiều kỳ {parts[0]} (Chỉ tiêu {parts[2]})" if len(parts) == 3 else m.group(0)

        text = re.sub(r'SUM_TK\[(.*?)\]', r_sum_tk, text)

        def r_sum_hd(m):
            parts = [x.strip() for x in m.group(1).split('|')]
            if len(parts) == 2: return f"Tổng HĐ {'Bán ra' if 'BAN_RA' in parts[0] else 'Mua vào'} (Cột: {parts[1]})"
            return m.group(0)

        text = re.sub(r'SUM\[(.*?)\]', r_sum_hd, text)

        def r_tk(m):
            parts = [x.strip() for x in m.group(1).split('|')]
            if len(parts) == 2:
                d = {"PS_NO": "Phát sinh NỢ", "PS_CO": "Phát sinh CÓ", "DU_NO": "Dư NỢ cuối kỳ",
                     "DU_CO": "Dư CÓ cuối kỳ", "SD_NO": "Dư NỢ đầu kỳ", "SD_CO": "Dư CÓ đầu kỳ"}
                return f"{d.get(parts[0], parts[0])} TK {parts[1]}"
            return m.group(0)

        text = re.sub(r'TK\[(.*?)\]', r_tk, text)

        def r_prev(m):
            parts = [x.strip() for x in m.group(1).split('|')]
            if len(parts) == 3:
                ma_form, phu_luc, ma_ct = parts
                if phu_luc.startswith("CDTK_"):
                    d = {"CDTK_NoDauKy": "Dư NỢ đầu kỳ", "CDTK_CoDauKy": "Dư CÓ đầu kỳ",
                         "CDTK_NoPhatSinh": "Phát sinh NỢ", "CDTK_CoPhatSinh": "Phát sinh CÓ",
                         "CDTK_NoCuoiKy": "Dư NỢ cuối kỳ", "CDTK_CoCuoiKy": "Dư CÓ cuối kỳ"}
                    return f"NĂM TRƯỚC: {ma_form} ({d.get(phu_luc, phu_luc)} TK {ma_ct.replace('ct', '')})"
                return f"NĂM TRƯỚC: Tờ khai {ma_form} (Chỉ tiêu {ma_ct})"
            return m.group(0)

        text = re.sub(r'PREV\[(.*?)\]', r_prev, text)

        def r_tinh(m):
            parts = [x.strip() for x in m.group(1).split('|')]
            if len(parts) == 3:
                ma_form, phu_luc, ma_ct = parts
                if phu_luc.startswith("CDTK_"):
                    d = {"CDTK_NoDauKy": "Dư NỢ đầu kỳ", "CDTK_CoDauKy": "Dư CÓ đầu kỳ",
                         "CDTK_NoPhatSinh": "Phát sinh NỢ", "CDTK_CoPhatSinh": "Phát sinh CÓ",
                         "CDTK_NoCuoiKy": "Dư NỢ cuối kỳ", "CDTK_CoCuoiKy": "Dư CÓ cuối kỳ"}
                    return f"{ma_form} ({d.get(phu_luc, phu_luc)} TK {ma_ct.replace('ct', '')})"
                return f"Tờ khai {ma_form} (Chỉ tiêu {ma_ct})"
            return m.group(0)

        text = re.sub(r'\[(.*?)\]', r_tinh, text)
        return text

    def _kiem_tra_chuyen_ky_khbs(self, dict_he_thong_to_khai):
        ket_qua_khbs = []
        KHBS_RULES = {
            '01/GTGT': [{'source': 'ct43', 'up': 'ct38', 'down': 'ct37', 'label': 'Thuế GTGT còn được khấu trừ'}],
            '02/GTGT': [{'source': 'ct32', 'up': 'ct25', 'down': 'ct27', 'label': 'Thuế GTGT dự án đầu tư chưa hoàn'},
                        {'source': 'ct22', 'up': 'ct24', 'down': 'ct26', 'label': 'Giá trị HHDV mua vào dự án đầu tư'}]
        }
        for ma_form, rules in KHBS_RULES.items():
            if ma_form not in dict_he_thong_to_khai: continue

            # Cần bổ sung hàm _sort_ky_helper hoặc logic sắp xếp tại đây nếu ứng dụng cần
            try:
                dict_ky = dict_he_thong_to_khai[ma_form]
                danh_sach_ky = sorted(list(dict_ky.keys()))
                for i, ky_hien_tai in enumerate(danh_sach_ky):
                    data_hien_tai = dict_ky[ky_hien_tai]
                    so_lan_bs = data_hien_tai.get("SoLan", 0)
                    if so_lan_bs == 0: continue
                    if i + 1 < len(danh_sach_ky):
                        ky_dich = danh_sach_ky[i + 1]
                        data_dich = dict_ky[ky_dich]
                        for rule in rules:
                            # Tương lai sẽ định nghĩa chi tiết _lay_chenh_lech_khbs
                            delta_val = 0
                            if delta_val == 0: continue
                            ct_up = float(data_dich.get("ChiTieuChinh", {}).get(rule['up'], {}).get("GiaTri", 0))
                            ct_down = float(data_dich.get("ChiTieuChinh", {}).get(rule['down'], {}).get("GiaTri", 0))

                            is_rui_ro = False
                            thong_diep = ""
                            if delta_val > 0 and abs(ct_up - delta_val) > 1000:
                                is_rui_ro = True
                                thong_diep = f"Kỳ {ky_dich}: Kê khai bổ sung làm TĂNG {rule['label']} ({rule['source']}) số tiền {delta_val:,.0f}. Đáng lẽ phải kê vào {rule['up']}, nhưng thực tế đang kê {ct_up:,.0f}."
                            elif delta_val < 0 and abs(ct_down - abs(delta_val)) > 1000:
                                is_rui_ro = True
                                thong_diep = f"Kỳ {ky_dich}: Kê khai bổ sung làm GIẢM {rule['label']} ({rule['source']}) số tiền {abs(delta_val):,.0f}. Đáng lẽ phải kê vào {rule['down']}, nhưng thực tế đang kê {ct_down:,.0f}."

                            if is_rui_ro:
                                ket_qua_khbs.append({
                                    "nhom": "Rà soát KHBS", "ten_phan_tich": f"Luân chuyển số liệu KHBS - {ma_form}",
                                    "ve_a_goc": f"KHBS kỳ {ky_hien_tai} ({rule['source']})",
                                    "gia_tri_a": abs(delta_val),
                                    "ve_b_goc": f"Kê khai kỳ {ky_dich}",
                                    "gia_tri_b": ct_up if delta_val > 0 else ct_down,
                                    "ket_qua_so": abs((ct_up if delta_val > 0 else ct_down) - abs(delta_val)),
                                    "is_rui_ro": True, "trang_thai": "Cảnh báo", "thong_diep": thong_diep
                                })
            except Exception:
                pass
        return ket_qua_khbs