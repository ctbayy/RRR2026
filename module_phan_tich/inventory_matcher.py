import pandas as pd
import re
import difflib


class InventoryReconcilerLight:
    def __init__(self, input_df, output_df, synonyms=None):
        self.synonyms = synonyms if synonyms else {}

        # Gom nhóm Tính tổng & Chuẩn hóa ngay từ đầu
        self.input_metrics = self._aggregate_data(input_df)
        self.output_metrics = self._aggregate_data(output_df)

    def _normalize_text(self, text):
        """Giữ lại toàn bộ con số (kích thước, model), chỉ xóa ký tự đặc biệt"""
        if not text: return ""
        text = str(text).lower().strip()
        for abbr, full in self.synonyms.items():
            text = re.sub(r'\b' + re.escape(abbr.lower()) + r'\b', full.lower(), text)
        text = re.sub(r'[^\w\s\d]', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    

    def _is_hang_hoa_that(self, text):
        """Bộ lọc từ khóa để loại bỏ các mặt hàng phi vật chất / rác"""
        text = str(text).lower()
        tu_khoa_rac = [
            'cước', 'phí', 'dịch vụ', 'điều chỉnh', 'thay thế',
            'lãi vay', 'chiết khấu', 'khuyến mại', 'tiền điện',
            'tiền nước', 'bảo hiểm', 'hoa hồng', 'tiền thuê'
        ]
        for kw in tu_khoa_rac:
            if kw in text: return False
        return True

    def _aggregate_data(self, df):
        """Gom cục số lượng theo từng mặt hàng và bổ sung ĐVT"""
        if df is None or df.empty or 'TenHangHoa' not in df.columns: return {}

        # Bắt thêm Đơn vị tính nếu có
        cols = ['TenHangHoa', 'SoLuong']
        if 'DonViTinh' in df.columns: cols.append('DonViTinh')

        temp = df[cols].copy()
        temp['SoLuong'] = pd.to_numeric(temp['SoLuong'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
        temp['DonViTinh'] = temp.get('DonViTinh', pd.Series([''] * len(temp))).astype(str).replace('nan', '')

        # Gom nhóm theo cả Tên và ĐVT để không bị lỗi cộng dồn
        grouped = temp.groupby(['TenHangHoa', 'DonViTinh'], as_index=False).sum()
        res = {}
        for _, r in grouped.iterrows():
            orig_name = str(r['TenHangHoa']).strip()

            # Kích hoạt màng lọc rác
            if not orig_name or not self._is_hang_hoa_that(orig_name): continue

            norm = self._normalize_text(orig_name)
            dvt = str(r['DonViTinh']).strip()

            if norm in res:
                res[norm]['qty'] += r['SoLuong']
                # Ưu tiên lấy ĐVT nếu dòng trước đó bị trống
                if dvt and not res[norm]['dvt']:
                    res[norm]['dvt'] = dvt
            else:
                res[norm] = {'orig_name': orig_name, 'qty': r['SoLuong'], 'dvt': dvt}
        return res

    def analyze_inventory(self, threshold=0.75):
        """Logic 3 Tầng: Map dữ liệu, Trừ kho và Phân luồng rủi ro"""
        results = []
        matched_inputs = set()
        input_norms = list(self.input_metrics.keys())

        # 1. Quét Hàng Bán Ra
        for out_norm, out_data in self.output_metrics.items():
            out_orig = out_data['orig_name']
            out_qty = out_data['qty']
            out_dvt = out_data['dvt']

            best_match_norm = None

            if out_norm in self.input_metrics:
                best_match_norm = out_norm
            else:
                matches = difflib.get_close_matches(out_norm, input_norms, n=1, cutoff=threshold)
                if matches: best_match_norm = matches[0]

            if best_match_norm:
                matched_inputs.add(best_match_norm)
                in_data = self.input_metrics[best_match_norm]
                ton_kho = in_data['qty'] - out_qty

                if ton_kho < 0:
                    trang_thai, muc_do = "❌ ÂM KHO", "red"
                    thong_diep = "Nhập < Xuất. Rủi ro xuất khống hoặc thiếu HĐ đầu vào (Cần đối chiếu thêm tồn kho đầu kỳ)."
                else:
                    trang_thai, muc_do = "✅ HỢP LÝ", "green"
                    thong_diep = "Số lượng nhập đủ bù đắp lượng xuất bán."

                results.append({
                    "nhom": "1. HÀNG THƯƠNG MẠI (Có Mua - Có Bán)",
                    "ban_ra": out_orig, "sl_ban": out_qty, "dvt_ban": out_dvt,
                    "mua_vao": in_data['orig_name'], "sl_mua": in_data['qty'], "dvt_mua": in_data['dvt'],
                    "ton_kho": ton_kho, "trang_thai": trang_thai, "muc_do": muc_do, "thong_diep": thong_diep
                })
            else:
                results.append({
                    "nhom": "2. CHƯA RÕ NGUỒN GỐC (Chỉ Bán - Không Mua)",
                    "ban_ra": out_orig, "sl_ban": out_qty, "dvt_ban": out_dvt,
                    "mua_vao": "---", "sl_mua": 0.0, "dvt_mua": "",
                    "ton_kho": -out_qty, "trang_thai": "⚠️ THIẾU ĐẦU VÀO", "muc_do": "orange",
                    "thong_diep": "Khả năng là SP tự sản xuất/lắp ráp, Dịch vụ hoặc rủi ro xuất khống."
                })

        # 2. Quét Hàng Mua Vào còn tồn đọng
        for in_norm, in_data in self.input_metrics.items():
            if in_norm not in matched_inputs:
                results.append({
                    "nhom": "3. TỒN KHO/NVL (Chỉ Mua - Không Bán)",
                    "ban_ra": "---", "sl_ban": 0.0, "dvt_ban": "",
                    "mua_vao": in_data['orig_name'], "sl_mua": in_data['qty'], "dvt_mua": in_data['dvt'],
                    "ton_kho": in_data['qty'], "trang_thai": "ℹ️ LƯU KHO", "muc_do": "gray",
                    "thong_diep": "Nguyên vật liệu, Tài sản, Chi phí hoặc hàng đang tồn kho chờ bán."
                })

        results.sort(key=lambda x: x['nhom'])
        return results