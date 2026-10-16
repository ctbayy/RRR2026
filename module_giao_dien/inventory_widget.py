from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QListWidget, QLabel, QGroupBox, QTableWidget,
                             QTableWidgetItem, QHeaderView, QPushButton, QLineEdit,
                             QListWidgetItem, QMessageBox, QCheckBox, QFrame, QProgressBar, QMenu)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QAction

from module_phan_tich.inventory_matcher1 import InventoryReconciler
from module_giao_dien.synonym_dialog import SynonymManagerDialog
from module_ho_tro.dictionary_loader import load_synonyms, add_single_synonym


# =====================================================================
# LỚP GIAO DIỆN: THẺ CẢNH BÁO RỦI RO THUẬT TOÁN
# =====================================================================
class InventoryWarningCard(QFrame):
    """Thẻ cảnh báo rủi ro thiết kế dạng dải băng (Ribbon) cực gọn"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(38)  # Ép cứng chiều cao siêu mỏng
        self.setStyleSheet("""
            QFrame {
                background-color: #FFF4CE;
                border: 1px solid #F6C000;
                border-radius: 5px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)

        # Icon
        lbl_icon = QLabel("⚠️")
        lbl_icon.setStyleSheet("font-size: 14px; border: none; background: transparent;")

        # Text cô đọng trên 1 dòng
        lbl_text = QLabel(
            "<b>LƯU Ý:</b> Thuật toán đối chiếu đang tối ưu cho DN Thương mại. Đối với DN Sản xuất/Xây lắp/Dịch vụ, hệ thống chưa tự quy đổi ra mặt hàng chính xác. Vui lòng tự rà soát mặt hàng có độ khớp thấp."
        )
        lbl_text.setStyleSheet("color: #D83B01; font-size: 12px; border: none; background: transparent;")
        lbl_text.setWordWrap(True)

        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_text, 1)  # stretch=1 để text chiếm hết không gian còn lại


# =====================================================================
# LỚP GIAO DIỆN CHÍNH: TAB ĐỐI CHIẾU KHO
# =====================================================================
class InventoryAnalysisWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.matcher = None
        self.raw_df_in = None
        self.raw_df_out = None
        self.current_out_item = None  # Lưu món đang chọn để dùng cho Menu
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- [THÊM MỚI]: THẺ CẢNH BÁO ---
        self.warning_card = InventoryWarningCard(self)
        main_layout.addWidget(self.warning_card)

        # --- [PHẦN 1: DASHBOARD MINI] ---
        stats_container = QWidget()
        stats_container.setFixedHeight(40)
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)

        # Thẻ chỉ số
        self.lbl_total_val = self._create_badge(stats_layout, "📦 Tổng:", "0", "#34495E", "#ECF0F1")
        self.lbl_risk_val = self._create_badge(stats_layout, "🔴 Rủi ro:", "0", "#C0392B", "#FADBD8")
        self.lbl_warn_val = self._create_badge(stats_layout, "⚠️ Cảnh báo:", "0", "#F39C12", "#FCF3CF")  # Vàng nền nhẹ
        self.lbl_safe_val = self._create_badge(stats_layout, "✅ Khớp:", "0", "#27AE60", "#D5F5E3")

        stats_layout.addStretch()

        # Thanh tiến độ
        self.progress_overview = QProgressBar()
        self.progress_overview.setTextVisible(True)
        self.progress_overview.setFormat(" Độ an toàn: %p% ")
        self.progress_overview.setFixedWidth(180)
        self.progress_overview.setFixedHeight(24)
        self.progress_overview.setStyleSheet("""
            QProgressBar {
                border: 1px solid #BDC3C7;
                border-radius: 12px;
                text-align: center;
                background-color: white;
                font-size: 11px;
                color: #555;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #27AE60;
                border-radius: 12px;
            }
        """)
        stats_layout.addWidget(self.progress_overview)

        main_layout.addWidget(stats_container)

        # --- [PHẦN 2: THANH CÔNG CỤ] ---
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Gõ để lọc mặt hàng...")
        self.search_box.setFixedHeight(30)
        self.search_box.setStyleSheet("QLineEdit { padding-left: 8px; border: 1px solid #BDC3C7; border-radius: 4px; }")
        self.search_box.textChanged.connect(self.filter_output_list)

        # [SỬA MÀU CHECKBOX]: Chữ Đen Xám (#2C3E50) cho dễ đọc
        self.chk_show_risk_only = QCheckBox("Chỉ hiện Rủi ro")
        self.chk_show_risk_only.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_show_risk_only.setStyleSheet("""
            QCheckBox { 
                font-weight: bold; 
                color: #2C3E50; /* Chữ màu đậm rõ ràng */
                margin-left: 10px; 
            }
            QCheckBox::indicator { 
                width: 16px; 
                height: 16px;
                border: 1px solid #BDC3C7;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #C0392B; /* Tick vào thì ô màu đỏ */
                border: 1px solid #C0392B;
            }
        """)
        self.chk_show_risk_only.toggled.connect(self.filter_output_list)

        self.btn_dictionary = QPushButton("📚 Từ điển")
        self.btn_dictionary.setFixedHeight(30)
        self.btn_dictionary.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_dictionary.setStyleSheet("""
            QPushButton { background-color: #2980B9; color: white; font-weight: bold; border-radius: 4px; padding: 0 15px; }
            QPushButton:hover { background-color: #3498DB; }
        """)
        self.btn_dictionary.clicked.connect(self.open_dictionary_manager)

        toolbar.addWidget(self.search_box, 1)
        toolbar.addWidget(self.chk_show_risk_only)
        # <<< [THÊM MỚI] Label hiển thị tiến độ (1/2000) >>>
        self.lbl_progress = QLabel("")
        self.lbl_progress.setStyleSheet(
            "color: #2980B9; font-weight: bold; font-style: italic; margin-left: 10px; margin-right: 10px;")
        toolbar.addWidget(self.lbl_progress)

        toolbar.addWidget(self.btn_dictionary)
        main_layout.addLayout(toolbar)

        # --- [PHẦN 3: KHU VỰC CHÍNH (CÓ MENU CHUỘT PHẢI)] ---
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Bảng Trái
        left_panel = QGroupBox("Danh sách Bán ra")
        left_layout = QVBoxLayout(left_panel)
        self.output_list = QListWidget()
        self.output_list.itemClicked.connect(self.on_output_item_clicked)
        left_layout.addWidget(self.output_list)
        splitter.addWidget(left_panel)

        # Bảng Phải
        right_panel = QGroupBox("Gợi ý Mua vào")
        right_layout = QVBoxLayout(right_panel)

        # Label thông tin chi tiết (Hiển thị Giá/Lượng)
        self.lbl_selected_item = QLabel("Chọn mặt hàng để xem...")
        self.lbl_selected_item.setWordWrap(True)
        self.lbl_selected_item.setStyleSheet("font-size: 13px; padding: 5px;")
        right_layout.addWidget(self.lbl_selected_item)

        self.suggestion_table = QTableWidget()
        self.suggestion_table.setColumnCount(3)
        self.suggestion_table.setHorizontalHeaderLabels(["Gợi ý Mua vào", "Độ giống", "Trạng thái"])
        self.suggestion_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        # [KÍCH HOẠT MENU CHUỘT PHẢI]
        self.suggestion_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.suggestion_table.customContextMenuRequested.connect(self.show_context_menu)

        right_layout.addWidget(self.suggestion_table)

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)
        main_layout.addWidget(splitter)

    def _create_badge(self, layout, title, value, text_color, bg_color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 15px;
                border: 1px solid {bg_color};
            }}
        """)
        frame.setFixedHeight(30)

        flayout = QHBoxLayout(frame)
        flayout.setContentsMargins(10, 0, 15, 0)
        flayout.setSpacing(5)

        lbl_t = QLabel(title)
        lbl_t.setStyleSheet(f"color: {text_color}; font-weight: normal; border: none; font-size: 11px;")

        lbl_v = QLabel(value)
        lbl_v.setStyleSheet(f"color: {text_color}; font-weight: bold; border: none; font-size: 13px;")

        flayout.addWidget(lbl_t)
        flayout.addWidget(lbl_v)

        layout.addWidget(frame)
        return lbl_v

    def update_dashboard(self, total, risk, warn, safe):
        self.lbl_total_val.setText(str(total))
        self.lbl_risk_val.setText(str(risk))
        self.lbl_warn_val.setText(str(warn))
        self.lbl_safe_val.setText(str(safe))

        if total > 0:
            safe_pct = int((safe / total) * 100)
            self.progress_overview.setValue(safe_pct)

            color = "#27AE60"
            if safe_pct < 50:
                color = "#C0392B"
            elif safe_pct < 80:
                color = "#F39C12"

            self.progress_overview.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #BDC3C7;
                    border-radius: 12px;
                    text-align: center;
                    background-color: white;
                    font-size: 11px;
                    color: #555;
                    font-weight: bold;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 12px;
                }}
            """)
        else:
            self.progress_overview.setValue(0)

    def load_data(self, df_in, df_out):
        self.raw_df_in = df_in
        self.raw_df_out = df_out
        real_synonyms = load_synonyms()
        self.matcher = InventoryReconciler(df_in, df_out, synonyms=real_synonyms)

        self.output_list.clear()

        scored_items = []
        c_risk = c_warn = c_safe = 0

        for item_name in self.matcher.output_items:
            top_match = self.matcher.get_top_matches(item_name, top_n=1)
            best_score = top_match[0]['score'] if top_match else 0
            scored_items.append((best_score, item_name))

            if best_score < 0.4:
                c_risk += 1
            elif best_score < 0.7:
                c_warn += 1
            else:
                c_safe += 1

        self.update_dashboard(len(scored_items), c_risk, c_warn, c_safe)

        scored_items.sort(key=lambda x: x[0])
        # [FIX LỖI FONT]: Tạo sẵn Font chuẩn, không dùng font mặc định
        std_font = QFont("Segoe UI", 10)
        bold_font = QFont("Segoe UI", 10)
        bold_font.setBold(True)
        for score, name in scored_items:
            item_widget = QListWidgetItem(name)
            if score < 0.4:
                item_widget.setForeground(QColor("#C0392B"))  # Đỏ
                item_widget.setToolTip(f"Rủi ro ({score:.0%})")
                item_widget.setFont(bold_font)  # Ép dùng font Segoe UI in đậm
                item_widget.setData(Qt.ItemDataRole.UserRole, "RISK")
            elif score < 0.7:
                item_widget.setForeground(QColor("#F39C12"))  # [SỬA LẠI] Vàng Đậm
                item_widget.setToolTip(f"Cảnh báo ({score:.0%})")
                item_widget.setFont(bold_font)  # Ép dùng font Segoe UI in đậm
                item_widget.setData(Qt.ItemDataRole.UserRole, "WARNING")
            else:
                item_widget.setForeground(QColor("#27AE60"))
                item_widget.setToolTip(f"Khớp ({score:.0%})")
                item_widget.setData(Qt.ItemDataRole.UserRole, "SAFE")

            self.output_list.addItem(item_widget)

        self.lbl_selected_item.setText(f"Đã tải {len(scored_items)} mặt hàng.")

    def on_output_item_clicked(self, item):
        if not self.matcher: return
        out_name = item.text()
        self.current_out_item = out_name

        # Lấy điểm cao nhất để hiển thị
        top_match = self.matcher.get_top_matches(out_name, top_n=1)
        best_score = top_match[0]['score'] if top_match else 0

        # Màu sắc cho label tiêu đề
        color_style = "color: #27AE60"  # Xanh
        if best_score < 0.4:
            color_style = "color: #C0392B"  # Đỏ
        elif best_score < 0.7:
            color_style = "color: #F39C12"  # Vàng

        self.lbl_selected_item.setText(
            f"Đang soi: <b>{out_name}</b> - Độ khớp: <span style='{color_style}; font-size:14px'><b>{best_score:.0%}</b></span>"
        )

        # Load bảng gợi ý (Đã bỏ cảnh báo Giá/Lượng)
        suggestions = self.matcher.get_top_matches(out_name, top_n=10)
        self.suggestion_table.setRowCount(0)
        # [FIX LỖI FONT]: Tạo font cho bảng chi tiết
        table_font = QFont("Segoe UI", 10)
        table_font_bold = QFont("Segoe UI", 10)
        table_font_bold.setBold(True)
        for row_idx, sugg in enumerate(suggestions):
            self.suggestion_table.insertRow(row_idx)
            in_name = sugg['item']
            pct = sugg['score'] * 100

            # --- [PHẦN ĐÃ SỬA: CHỈ HIỆN TRẠNG THÁI KHỚP TÊN] ---
            status = "Rủi ro"
            color = QColor("#C0392B")
            is_bold = False  # Cờ đánh dấu in đậm
            if pct >= 70:
                status = "Khớp";
                color = QColor("#27AE60")
            elif pct >= 40:
                status = "Ngờ vực";
                color = QColor("#F39C12");
                is_bold = True  # Vàng đậm
            else:
                is_bold = True  # Rủi ro cũng in đậm
            it_name = QTableWidgetItem(in_name)
            it_name.setFont(table_font)

            # Tính toán tooltip ẩn
            qty_in, price_in = self.matcher.get_item_metrics(in_name, is_input=True)
            it_name.setToolTip(f"Thông tin tham khảo:\n- SL Mua: {qty_in:,.0f}\n- Giá TB Mua: {price_in:,.0f}")

            # Cột 2: Điểm
            it_score = QTableWidgetItem(f"{pct:.1f}%")
            it_score.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_score.setFont(table_font)

            # Cột 3: Trạng thái
            it_status = QTableWidgetItem(status)
            it_status.setForeground(color)
            if is_bold:
                it_status.setFont(table_font_bold)
            else:
                it_status.setFont(table_font)

            self.suggestion_table.setItem(row_idx, 0, it_name)
            self.suggestion_table.setItem(row_idx, 1, it_score)
            self.suggestion_table.setItem(row_idx, 2, it_status)

    def filter_output_list(self):
        text = self.search_box.text().lower()
        show_risk_only = self.chk_show_risk_only.isChecked()
        for i in range(self.output_list.count()):
            item = self.output_list.item(i)
            item_type = item.data(Qt.ItemDataRole.UserRole)
            match_text = text in item.text().lower()
            match_risk = True
            if show_risk_only and item_type == "SAFE": match_risk = False
            item.setHidden(not (match_text and match_risk))

    def open_dictionary_manager(self):
        dialog = SynonymManagerDialog(self)
        if dialog.exec():
            if self.raw_df_in is not None and self.raw_df_out is not None:
                self.load_data(self.raw_df_in, self.raw_df_out)
                QMessageBox.information(self, "Cập nhật", "Đã áp dụng từ điển mới!")

    def show_context_menu(self, pos):
        """Hiện menu chuột phải để thêm từ điển"""
        if not self.current_out_item: return

        # Lấy dòng đang được click chuột phải
        item_in_table = self.suggestion_table.itemAt(pos)
        if not item_in_table: return

        # Lấy tên mặt hàng mua vào (Cột 0)
        row = item_in_table.row()
        in_name = self.suggestion_table.item(row, 0).text()

        menu = QMenu(self)
        action_add = QAction(f"🔗 Ghép '{self.current_out_item}' = '{in_name}'", self)

        def add_synonym_handler():
            # Thêm vào từ điển: Key = Tên Bán (Ngắn/Sai), Value = Tên Mua (Chuẩn)
            if add_single_synonym(self.current_out_item, in_name):
                # Reload lại dữ liệu ngay lập tức
                if self.raw_df_in is not None:
                    self.load_data(self.raw_df_in, self.raw_df_out)
                    # Chọn lại dòng cũ để xem kết quả
                    # (Logic tìm lại item hơi phức tạp, tạm thời reset list)
                    QMessageBox.information(self, "Đã học", "Đã cập nhật từ điển và tính toán lại!")

        action_add.triggered.connect(add_synonym_handler)
        menu.addAction(action_add)
        menu.exec(self.suggestion_table.mapToGlobal(pos))

    def clear_data(self):
        self.output_list.clear()
        self.suggestion_table.setRowCount(0)
        self.lbl_selected_item.setText("")
        self.update_dashboard(0, 0, 0, 0)
        self.matcher = None
        self.raw_df_in = None
        self.raw_df_out = None

    # <<< [THÊM MỚI] Hàm cập nhật Label >>>
    def update_status_label(self, text):
        self.lbl_progress.setText(text)

    # <<< [THÊM MỚI] Hàm nhận dữ liệu ĐÃ TÍNH XONG từ Worker >>>
    def load_precalculated_data(self, matcher, df_in, df_out):
        """Hàm này nhận Matcher và Dataframe từ Worker, chỉ việc hiển thị"""
        self.matcher = matcher
        self.raw_df_in = df_in
        self.raw_df_out = df_out

        self.output_list.clear()
        scored_items = []
        c_risk = c_warn = c_safe = 0

        # Lấy items từ matcher (dữ liệu đã có sẵn trong RAM)
        for item_name in self.matcher.output_items:
            top_match = self.matcher.get_top_matches(item_name, top_n=1)
            best_score = top_match[0]['score'] if top_match else 0
            scored_items.append((best_score, item_name))

            if best_score < 0.4:
                c_risk += 1
            elif best_score < 0.7:
                c_warn += 1
            else:
                c_safe += 1

        self.update_dashboard(len(scored_items), c_risk, c_warn, c_safe)

        # Sắp xếp và vẽ List (Giữ nguyên logic cũ)
        scored_items.sort(key=lambda x: x[0])
        std_font = QFont("Segoe UI", 10)
        bold_font = QFont("Segoe UI", 10)
        bold_font.setBold(True)

        for score, name in scored_items:
            item_widget = QListWidgetItem(name)
            # ... (Logic set màu/icon giữ nguyên như cũ)
            if score < 0.4:
                item_widget.setForeground(QColor("#C0392B"))
                item_widget.setFont(bold_font)
                item_widget.setData(Qt.ItemDataRole.UserRole, "RISK")
            elif score < 0.7:
                item_widget.setForeground(QColor("#F39C12"))
                item_widget.setFont(bold_font)
                item_widget.setData(Qt.ItemDataRole.UserRole, "WARNING")
            else:
                item_widget.setForeground(QColor("#27AE60"))
                item_widget.setData(Qt.ItemDataRole.UserRole, "SAFE")

            self.output_list.addItem(item_widget)

        self.lbl_selected_item.setText(f"Đã tải {len(scored_items)} mặt hàng.")
        # Reset label tiến độ khi xong
        self.lbl_progress.setText("✅ Sẵn sàng")