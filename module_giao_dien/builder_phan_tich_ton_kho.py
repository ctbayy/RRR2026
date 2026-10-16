# module_giao_dien/builder_phan_tich_ton_kho.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class BuilderPhanTichTonKho(QWidget):
    def __init__(self, data_ton_kho=None, parent=None):
        super().__init__(parent)
        self.layout_chinh = QVBoxLayout(self)
        self.layout_chinh.setContentsMargins(5, 5, 5, 5)
        if data_ton_kho:
            self.nap_du_lieu(data_ton_kho)

    def nap_du_lieu(self, data_ton_kho):
        while self.layout_chinh.count() > 0:
            item = self.layout_chinh.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not data_ton_kho: return

        bang = QTableWidget(0, 8)
        bang.horizontalHeader().setVisible(False)
        bang.verticalHeader().setVisible(False)
        bang.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        bang.setWordWrap(True)
        bang.setTextElideMode(Qt.TextElideMode.ElideNone)

        # Dữ liệu lớn nên bật thanh cuộn dọc/ngang tự động
        bang.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        bang.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        bang.setStyleSheet(
            "QTableWidget { gridline-color: #e2e8f0; background-color: #ffffff; border: 1px solid #cbd5e1; }")

        header = bang.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        bang.setColumnWidth(6, 135)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

        def _tao_o(r_idx, c_idx, text, align_right=False, align_center=False, bg_color=None, fg_color=None,
                   is_bold=False):
            item = QTableWidgetItem(str(text))
            if align_right:
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            elif align_center:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            if bg_color: item.setBackground(QColor(bg_color))
            if fg_color: item.setForeground(QColor(fg_color))
            if is_bold:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            bang.setItem(r_idx, c_idx, item)

        dict_nhom = {}
        for r in data_ton_kho:
            nhom = r.get('nhom', 'Khác')
            if nhom not in dict_nhom: dict_nhom[nhom] = []
            dict_nhom[nhom].append(r)

        for ten_nhom, ds_hang in dict_nhom.items():
            r_head = bang.rowCount()
            bang.insertRow(r_head)
            cols_head = ["STT", "Mặt hàng Bán ra (Xuất)", "SL Xuất", "Mặt hàng Mua vào (Nhập)", "SL Nhập",
                         "Tồn trong kỳ", "Trạng thái", "Đánh giá / Ghi chú"]
            for c, text in enumerate(cols_head):
                _tao_o(r_head, c, text if c != 1 else f"[{ten_nhom}]", align_center=(c != 1), bg_color="#f1f5f9",
                       fg_color="#0f172a", is_bold=True)

            # Rải chi tiết (Sọc ngựa vằn, KHÔNG in đậm số)
            for i, r in enumerate(ds_hang):
                r_idx = bang.rowCount()
                bang.insertRow(r_idx)
                bg_dong = "#f8fafc" if i % 2 == 0 else "#ffffff"

                _tao_o(r_idx, 0, str(i + 1), align_center=True, bg_color=bg_dong)

                # Bọc thêm ĐVT vào Tên Bán ra
                ten_ban_ra = r.get('ban_ra', '')
                if r.get('dvt_ban'): ten_ban_ra += f" [{r.get('dvt_ban')}]"
                _tao_o(r_idx, 1, ten_ban_ra, bg_color=bg_dong)

                sl_ban = f"{r.get('sl_ban', 0):,.2f}".rstrip('0').rstrip('.') if r.get('sl_ban', 0) else "---"
                _tao_o(r_idx, 2, sl_ban, align_right=True, bg_color=bg_dong)

                # Bọc thêm ĐVT vào Tên Mua vào
                ten_mua_vao = r.get('mua_vao', '')
                if r.get('dvt_mua'): ten_mua_vao += f" [{r.get('dvt_mua')}]"
                _tao_o(r_idx, 3, ten_mua_vao, bg_color=bg_dong)

                sl_mua = f"{r.get('sl_mua', 0):,.2f}".rstrip('0').rstrip('.') if r.get('sl_mua', 0) else "---"
                _tao_o(r_idx, 4, sl_mua, align_right=True, bg_color=bg_dong)

                ton = f"{r.get('ton_kho', 0):,.2f}".rstrip('0').rstrip('.')
                _tao_o(r_idx, 5, ton, align_right=True, bg_color=bg_dong)

                muc_do = r.get('muc_do', 'gray')
                if muc_do == 'red': bg_badge = "#ef4444"
                elif muc_do == 'orange': bg_badge = "#f59e0b"
                elif muc_do == 'green': bg_badge = "#10b981"
                else: bg_badge = "#64748b"

                hien_thi = r.get('trang_thai', '')
                html_badge = f"<div style='background-color: {bg_badge}; color: white; padding: 4px 2px; border-radius: 4px; font-weight: bold; text-align: center; font-size: 11px; white-space: normal; word-wrap: break-word;'>{hien_thi}</div>"

                lbl_badge = QLabel(html_badge)
                lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl_badge.setContentsMargins(2, 2, 2, 2)
                lbl_badge.setWordWrap(True)

                item_an = QTableWidgetItem(hien_thi + "\n\n")
                item_an.setForeground(QColor("transparent"))
                item_an.setBackground(QColor(bg_dong))
                bang.setItem(r_idx, 6, item_an)
                bang.setCellWidget(r_idx, 6, lbl_badge)

                _tao_o(r_idx, 7, r.get('thong_diep', ''), bg_color=bg_dong)

        bang.resizeRowsToContents()
        self.layout_chinh.addWidget(bang)