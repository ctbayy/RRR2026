from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QGroupBox, QTreeWidget, QTreeWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from module_ho_tro.dinh_dang_so import dinh_dang_so_vn


class BuilderPhanTichChuoiCungUng(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_chinh = QVBoxLayout(self)
        self.layout_chinh.setContentsMargins(5, 5, 5, 5)

    def nap_du_lieu(self, sc_result):
        if not sc_result: return

        grp_ket_luan = QGroupBox("CẢNH BÁO CHUỖI GIÁ TRỊ (MACRO)")
        grp_ket_luan.setStyleSheet("QGroupBox { font-weight: bold; color: #B91C1C; font-size: 14px; }")
        lay_kl = QVBoxLayout(grp_ket_luan)

        lbl_mohinh = QLabel(f"🎯 Mô hình nhận diện: <b>{sc_result['mo_hinh']}</b>")
        lbl_mohinh.setStyleSheet("font-size: 14px; color: #1E3A8A;")
        lay_kl.addWidget(lbl_mohinh)

        for cb in sc_result['canh_bao']:
            lbl_cb = QLabel(cb)
            lbl_cb.setWordWrap(True)
            if "✅" in cb:
                lbl_cb.setStyleSheet("color: #059669; font-weight: bold; font-size: 13px; padding: 5px;")
            else:
                lbl_cb.setStyleSheet(
                    "color: #DC2626; font-weight: bold; font-size: 13px; padding: 5px; background-color: #FEE2E2; border-radius: 4px;")
            lay_kl.addWidget(lbl_cb)

        self.layout_chinh.addWidget(grp_ket_luan)

        khung_bang = QHBoxLayout()
        # Ném thêm cái mảng chi tiết (details) vào hàm vẽ cây
        khung_bang.addWidget(
            self._ve_bang_tree("📥 DÒNG TIỀN ĐẦU VÀO (MUA VÀO)", sc_result['in_tags'], sc_result['in_details'],
                               sc_result['in_total']))
        khung_bang.addWidget(
            self._ve_bang_tree("📤 DÒNG TIỀN ĐẦU RA (BÁN RA)", sc_result['out_tags'], sc_result['out_details'],
                               sc_result['out_total']))

        self.layout_chinh.addLayout(khung_bang)

    # =========================================================================
    # [SIÊU PHẨM PIVOT]: VẼ CÂY THƯ MỤC THAY VÌ BẢNG PHẲNG
    # =========================================================================
    def _ve_bang_tree(self, tieu_de, dict_tags, dict_details, tong_tien):
        grp = QGroupBox(tieu_de)
        grp.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        lay = QVBoxLayout(grp)

        tree = QTreeWidget()
        tree.setHeaderLabels(["Nhóm ngành / Chi tiết mặt hàng", "Tổng tiền", "Tỷ trọng"])
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        tree.setStyleSheet("""
            QTreeWidget { background-color: white; border: 1px solid #E5E7EB; font-size: 13px; }
            QTreeWidget::item { padding: 5px; border-bottom: 1px solid #F3F4F6; }
            QTreeWidget::item:hover { background-color: #F9FAFB; }
        """)

        bold_font = QFont()
        bold_font.setBold(True)

        for tag, tien in sorted(dict_tags.items(), key=lambda x: x[1], reverse=True):
            if tien == 0: continue

            # 1. TẠO DÒNG CHA (GROUP TAG)
            root_item = QTreeWidgetItem(tree)
            root_item.setText(0, tag)
            root_item.setText(1, dinh_dang_so_vn(tien))
            root_item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            ty_trong = (tien / tong_tien * 100) if tong_tien > 0 else 0
            root_item.setText(2, f"{ty_trong:.1f}%")
            root_item.setTextAlignment(2, Qt.AlignmentFlag.AlignCenter)

            if "[CHƯA_PHÂN_LOẠI]" in tag:
                root_item.setForeground(0, QColor("#9CA3AF"))
            else:
                root_item.setFont(0, bold_font)
                root_item.setForeground(0, QColor("#0284C7"))

            root_item.setFont(1, bold_font)
            root_item.setFont(2, bold_font)

            # 2. TẠO CÁC DÒNG CON (CHI TIẾT MẶT HÀNG BÊN TRONG TAG)
            danh_sach_chi_tiet = dict_details.get(tag, [])

            # Trí khôn: Cộng dồn các mặt hàng trùng tên nhau cho đỡ dài
            gom_chitiet = {}
            for item in danh_sach_chi_tiet:
                ten = item['ten']
                gom_chitiet[ten] = gom_chitiet.get(ten, 0) + item['tien']

            # Đổ dữ liệu con vào dưới Node cha
            for ten_hang, tien_hang in sorted(gom_chitiet.items(), key=lambda x: x[1], reverse=True):
                child_item = QTreeWidgetItem(root_item)
                child_item.setText(0, f" ↳ {ten_hang}")
                child_item.setForeground(0, QColor("#4B5563"))  # Màu xám xám cho phân biệt

                child_item.setText(1, dinh_dang_so_vn(tien_hang))
                child_item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                child_item.setForeground(1, QColor("#4B5563"))

                child_item.setText(2, "")  # Cột tỷ trọng để trống ở dòng con cho đỡ rối

        lay.addWidget(tree)

        lbl_tong = QLabel(f"💰 TỔNG CỘNG: <b>{dinh_dang_so_vn(tong_tien)}</b>")
        lbl_tong.setStyleSheet("font-size: 13px; color: #111827; padding-top: 5px;")
        lay.addWidget(lbl_tong)

        return grp