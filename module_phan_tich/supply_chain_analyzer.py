import json
import os
import pandas as pd


class SupplyChainAnalyzer:
    def __init__(self, df_in, df_out, config_path="Data/chuoi_cung_ung.json"):
        self.df_in = df_in
        self.df_out = df_out
        self.config_path = config_path

    def run_analysis(self):
        if not os.path.exists(self.config_path):
            return None

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Lỗi đọc JSON chuỗi cung ứng: {e}")
            return None

        danh_muc = config.get("danh_muc_tag", {})
        luat_list = config.get("luat_cung_ung", [])

        kw_map = {}
        all_tags = []
        for group, tags in danh_muc.items():
            if group == "Mô tả": continue
            for tag, keywords in tags.items():
                if tag == "Mô tả": continue
                all_tags.append(tag)
                for kw in keywords:
                    kw_map[str(kw).strip().lower()] = tag

        # =========================================================
        # [VÁ LỖI]: THUẬT TOÁN "CÁ LỚN NUỐT CÁ BÉ" (LONGEST MATCH)
        # Ép máy tính phải dò các từ khóa DÀI trước, từ NGẮN sau
        # Để "Cột điện" ăn trước "Điện", "Mực in" ăn trước "In"
        # =========================================================
        danh_sach_uu_tien = sorted(kw_map.keys(), key=len, reverse=True)

        def _gom_tien(df):
            kq = {}
            chi_tiet = {}
            tong_tien = 0
            if not isinstance(df, pd.DataFrame) or df.empty or 'TenHangHoa' not in df.columns:
                return kq, chi_tiet, tong_tien

            col_tien = 'TongTienChuaThue' if 'TongTienChuaThue' in df.columns else 'ThanhTienChuaThue'
            if col_tien not in df.columns: return kq, chi_tiet, tong_tien

            for _, r in df.iterrows():
                ten_goc = str(r['TenHangHoa']).strip()
                ten_lower = ten_goc.lower()
                try:
                    tien = float(str(r[col_tien]).replace(',', ''))
                except:
                    tien = 0
                tong_tien += tien

                tag_found = "[CHƯA_PHÂN_LOẠI]"

                # Quét theo danh sách đã được sắp xếp độ dài
                for kw in danh_sach_uu_tien:
                    if kw in ten_lower:
                        tag_found = kw_map[kw]
                        break

                kq[tag_found] = kq.get(tag_found, 0) + tien

                if tag_found not in chi_tiet:
                    chi_tiet[tag_found] = []
                chi_tiet[tag_found].append({"ten": ten_goc, "tien": tien})

            return kq, chi_tiet, tong_tien

        in_tags, in_details, in_total = _gom_tien(self.df_in)
        out_tags, out_details, out_total = _gom_tien(self.df_out)

        if in_total == 0 and out_total == 0:
            return None

        main_out_tag = None
        max_out_val = 0
        for t, v in out_tags.items():
            if t != "[CHƯA_PHÂN_LOẠI]" and v > max_out_val:
                max_out_val = v
                main_out_tag = t

        canh_bao = []
        mo_hinh = "Chưa nhận diện được mô hình (Khả năng Rủi ro cao)"

        if main_out_tag:
            rule_match = None
            for r in luat_list:
                if main_out_tag in r.get("dau_ra_hop_le", []) or "*" in r.get("dau_ra_hop_le", []):
                    rule_match = r
                    break

            if rule_match:
                mo_hinh = rule_match["ten_mo_hinh"]
                env = {tag: 0 for tag in all_tags}
                env.update(in_tags)
                env.update(out_tags)

                tong_doanh_thu = out_total if out_total > 0 else 1
                tong_vat_tu = in_total - env.get("[CHI PHÍ QUẢN LÝ]", 0) - env.get("[TÀI SẢN MÁY MÓC]", 0)

                for cb in rule_match.get("canh_bao_ty_trong", []):
                    dk_eval = cb["dieu_kien"]
                    for k, v in env.items():
                        dk_eval = dk_eval.replace(k, str(v))
                    dk_eval = dk_eval.replace("Tong_Doanh_Thu", str(tong_doanh_thu))
                    dk_eval = dk_eval.replace("Tong_Vat_Tu_Nhap_Vao", str(tong_vat_tu))

                    try:
                        if eval(dk_eval):
                            canh_bao.append(cb["thong_diep"])
                    except Exception:
                        pass

        if not canh_bao:
            if mo_hinh != "Chưa nhận diện được mô hình (Khả năng Rủi ro cao)":
                canh_bao.append(f"✅ Hợp lý! Chuỗi cung ứng khớp với mô hình: {mo_hinh}")
            else:
                canh_bao.append("⚠️ RỦI RO: Không nhận diện được mô hình. Đầu ra đéo khớp với bất kỳ Đầu vào nào!")

        return {
            "in_tags": in_tags,
            "in_details": in_details,
            "out_tags": out_tags,
            "out_details": out_details,
            "in_total": in_total,
            "out_total": out_total,
            "mo_hinh": mo_hinh,
            "canh_bao": canh_bao
        }