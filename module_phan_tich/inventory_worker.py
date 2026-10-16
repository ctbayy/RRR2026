# app/inventory_worker.py
import traceback
from PySide6.QtCore import QObject, Signal # <-- Đã sửa thành PySide6 và Signal
import pandas as pd
# Import logic nghiệp vụ (Nhớ sửa đường dẫn app.analysis... cho khớp với thư mục của mày)
from module_phan_tich.inventory_matcher1 import InventoryReconciler
from module_ho_tro.dictionary_loader import load_synonyms

class InventoryAnalysisWorker(QObject):
    """
    Worker chuyên biệt xử lý đối chiếu kho (chạy luồng riêng).
    """
    finished = Signal(object, object)  # Trả về: (matcher, inventory_df)
    progress_text = Signal(str)  # Bắn text tiến độ: "Đang soi 10/2000..."
    error = Signal(str)

    def __init__(self, df_in, df_out):
        super().__init__()
        self.df_in = df_in
        self.df_out = df_out

    def run_analysis(self):
        try:
            self.progress_text.emit("⏳ Đang khởi tạo bộ dữ liệu kho...")

            # 1. Load từ điển & Khởi tạo Matcher
            real_synonyms = load_synonyms()
            matcher = InventoryReconciler(self.df_in, self.df_out, synonyms=real_synonyms)

            # 2. Lấy danh sách item bán ra cần soi
            output_items = matcher.output_items
            total_items = len(output_items)

            if total_items == 0:
                self.progress_text.emit("⚠️ Không tìm thấy mặt hàng bán ra.")
                inventory_df = pd.DataFrame()
            else:
                # 3. Vòng lặp tính toán (Warm-up Cache & Báo tiến độ)
                # Đây là bước tốn thời gian nhất -> Cần loop để UI không đơ
                for i, item in enumerate(output_items):
                    # Update tiến độ mỗi 5 item (đỡ spam signal quá nhiều)
                    if i % 5 == 0:
                        self.progress_text.emit(f"🔄 Đang đối chiếu: {i + 1}/{total_items}")

                    # Gọi hàm tính toán điểm (Matcher sẽ tự cache kết quả lại)
                    matcher.get_top_matches(item, top_n=1)

                self.progress_text.emit("✅ Đang tổng hợp báo cáo cuối cùng...")

                # 4. Lấy kết quả tổng hợp (Rất nhanh vì đã có cache bước 3)
                inventory_df = matcher.analyze_discrepancies(threshold=0.4)

            self.progress_text.emit(f"🎉 Hoàn tất ({total_items} mặt hàng)!")
            self.finished.emit(matcher, inventory_df)

        except Exception as e:
            # Bắt lỗi và gửi về UI
            msg = f"Lỗi luồng đối chiếu kho: {str(e)}\n{traceback.format_exc()}"
            self.error.emit(msg)