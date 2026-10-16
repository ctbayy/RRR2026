import pandas as pd
import re
import traceback
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class InventoryReconciler:
    def __init__(self, input_df, output_df, synonyms=None):
        self.synonyms = synonyms if synonyms else {}
        self._match_cache = {}  # Vùng nhớ đệm O(1) siêu tốc

        # 1. Trích xuất danh sách mặt hàng
        self.input_items = self._extract_unique_items(input_df)
        self.output_items = self._extract_unique_items(output_df)

        # 2. Khôi phục bộ nhớ cache số lượng và giá trị
        self.input_metrics = self._precalculate_metrics(input_df)
        self.output_metrics = self._precalculate_metrics(output_df)

        # 3. Chuẩn bị AI Scikit-learn
        self.input_matrix = None
        try:
            self.input_items_normalized = [self._normalize_text(item) for item in self.input_items]
            # Sử dụng n-gram bắt cặp ký tự để chống sai chính tả/gõ tắt
            self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))

            if self.input_items_normalized:
                self.input_matrix = self.vectorizer.fit_transform(self.input_items_normalized)

                # [TỐI ƯU CỰC ĐẠI]: Tính toán toàn bộ điểm số của 10.000 mặt hàng trong 1 lần duy nhất!
                self._batch_compute_all_matches()
        except Exception as e:
            print(f"[ML Init Error] Lỗi khởi tạo AI: {e}")

    def _extract_unique_items(self, df):
        if df is None or df.empty: return []
        col = 'TenHangHoa' if 'TenHangHoa' in df.columns else df.columns[0]
        return [str(i).strip() for i in df[col].dropna().unique() if len(str(i)) > 2]

    def _precalculate_metrics(self, pd_df):
        """Tính sẵn Số lượng & Đơn giá (Tránh tính lại khi click vào dòng)"""
        if pd_df is None or pd_df.empty or 'TenHangHoa' not in pd_df.columns:
            return {}

        cols_to_keep = ['TenHangHoa', 'SoLuong']
        if 'TongTienChuaThue' in pd_df.columns:
            cols_to_keep.append('TongTienChuaThue')

        temp_df = pd_df[cols_to_keep].copy()

        # Làm sạch số liệu an toàn
        temp_df['SoLuong'] = pd.to_numeric(temp_df['SoLuong'].astype(str).str.replace(',', '', regex=False),
                                           errors='coerce').fillna(0.0)
        if 'TongTienChuaThue' in temp_df.columns:
            temp_df['TongTienChuaThue'] = pd.to_numeric(
                temp_df['TongTienChuaThue'].astype(str).str.replace(',', '', regex=False), errors='coerce').fillna(0.0)
        else:
            temp_df['TongTienChuaThue'] = 0.0

        # Gom nhóm tính tổng
        summary = temp_df.groupby('TenHangHoa', as_index=False).sum()

        metrics_dict = {}
        for _, row in summary.iterrows():
            ten_hang = str(row['TenHangHoa']).strip()
            qty = row['SoLuong']
            val = row['TongTienChuaThue']
            avg_price = val / qty if qty > 0 else 0.0
            metrics_dict[ten_hang] = (qty, avg_price)

        return metrics_dict

    def _normalize_text(self, text):
        if not text: return ""
        text = str(text).lower().strip()

        for abbr, full in self.synonyms.items():
            pattern = r'\b' + re.escape(abbr.lower()) + r'\b'
            text = re.sub(pattern, full.lower(), text)

        text = re.sub(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', '', text)
        text = re.sub(r'\b(tháng|t|quý|q|năm)\s*[\d/-]+', '', text)

        common_units = r'\b(kg|cái|chiếc|bao|hộp|thùng|lít|mét|m2|m3|bộ|viên|cuộn|tấn|ta|yến)\b'
        text = re.sub(common_units, '', text)

        stop_words = r'\b(chi|phí|tiền|khoản|thu|dịch|vụ|của|các|cho|tại|theo|hợp|đồng|số|hóa|đơn|gtgt|vat|tt|thanh|toán|cước|vnđ|vnd)\b'
        text = re.sub(stop_words, '', text)

        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _batch_compute_all_matches(self):
        """Hành quyết toàn bộ dữ liệu bằng Matrix Multiplication (Tốc độ ánh sáng)"""
        if not self.output_items or self.input_matrix is None:
            return

        # 1. Băm toàn bộ tên hàng hóa bán ra thành ma trận Vector 1 lần duy nhất
        out_norm = [self._normalize_text(item) for item in self.output_items]
        out_matrix = self.vectorizer.transform(out_norm)

        # 2. Nhân 2 ma trận với nhau (Đo độ tương đồng Cosine của tất cả các mặt hàng cùng lúc)
        similarities = cosine_similarity(out_matrix, self.input_matrix)

        # 3. Trút kết quả vào vùng nhớ đệm (Cache)
        for i, out_item in enumerate(self.output_items):
            row_sim = similarities[i]
            # Sắp xếp và lấy top 10 (argsort siêu nhanh của Numpy)
            top_indices = np.argsort(row_sim)[-10:][::-1]

            results = []
            for idx in top_indices:
                score = float(row_sim[idx])
                if score > 0.15:  # Lọc rác
                    results.append({
                        "item": self.input_items[idx],
                        "score": score
                    })
            self._match_cache[out_item] = results

    def get_item_metrics(self, item_name, is_input=True):
        """Hàm trả về dữ liệu khi UI click vào bảng (Đã bọc chống Crash)"""
        try:
            metrics = self.input_metrics if is_input else self.output_metrics
            return metrics.get(str(item_name).strip(), (0.0, 0.0))
        except Exception as e:
            print(f"[UI Crash Prevented] Error in get_item_metrics: {e}")
            return (0.0, 0.0)

    def get_top_matches(self, output_item_name, top_n=5):
        """Hàm này giờ chỉ việc thò tay vào kho (Cache) lấy đồ ra, tốc độ tính bằng milli-giây"""
        try:
            cached_results = self._match_cache.get(output_item_name, [])
            return cached_results[:top_n]
        except Exception as e:
            print(f"[Crash Prevented] Error in get_top_matches: {e}\n{traceback.format_exc()}")
            return []

    def analyze_discrepancies(self, threshold=0.4):
        try:
            results = []
            for out_item in self.output_items:
                # Gọi thẳng hàm get_top_matches siêu tốc
                matches = self.get_top_matches(out_item, top_n=1)
                best_match = matches[0] if matches else None
                score = best_match['score'] if best_match else 0

                status = "Hợp lệ"
                if score < threshold:
                    status = "Rủi ro"
                elif score < 0.7:
                    status = "Cảnh báo"

                results.append({
                    "Mặt hàng Mua vào (Gợi ý)": best_match['item'] if best_match else "---",
                    "Mặt hàng Bán ra (Thực tế)": out_item,
                    "Độ tin cậy": f"{score:.0%}",
                    "Kết quả": status
                })

            df = pd.DataFrame(results)
            if not df.empty:
                df.sort_values(by="Độ tin cậy", ascending=True, inplace=True)
                cols = ["Mặt hàng Mua vào (Gợi ý)", "Mặt hàng Bán ra (Thực tế)", "Độ tin cậy", "Kết quả"]
                df = df[cols]
            return df

        except Exception as e:
            print(f"[Crash Prevented] Error in analyze_discrepancies: {e}\n{traceback.format_exc()}")
            return pd.DataFrame()