# module_giao_dien/dialog_chon_quy_tac.py

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLineEdit, QTreeWidget, QTreeWidgetItem, QCheckBox)
from PySide6.QtCore import Qt
import qtawesome as qta

# Nhập Bộ não quản lý cấu hình (Thay thế cho thư viện json cũ)
from module_ho_tro.quan_ly_cong_thuc import QuanLyCongThuc


class DialogChonQuyTac(QDialog):
    # ĐÃ SỬA: Xóa bỏ tham số duong_dan_json
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bộ lọc Quy tắc Phân tích")
        self.resize(650, 500)
        self.setStyleSheet("""
            QDialog { background-color: #f8fafc; }
            QTreeWidget { border: 1px solid #cbd5e1; border-radius: 5px; background-color: white; font-size: 13px; }
            QTreeWidget::item { padding: 5px; border-bottom: 1px solid #f1f5f9; }
            QLineEdit { padding: 8px; border: 1px solid #94a3b8; border-radius: 4px; }
            QPushButton.BtnLuu { background-color: #059669; color: white; font-weight: bold; padding: 8px 20px; border-radius: 4px; }
            QPushButton.BtnLuu:hover { background-color: #047857; }
        """)

        # ĐÃ SỬA: Gọi trực tiếp bộ não để bốc dữ liệu đã giải mã & gộp (Core + User)
        self.dict_cong_thuc = QuanLyCongThuc.tai_du_lieu_tong_hop()
        self.danh_sach_chon = []

        self.thiet_lap_ui()
        self.nap_du_lieu_len_cay()

    def thiet_lap_ui(self):
        layout = QVBoxLayout(self)

        khung_top = QHBoxLayout()
        self.txt_tim_kiem = QLineEdit()
        self.txt_tim_kiem.setPlaceholderText("Tìm theo tên, mã hoặc nhóm quy tắc...")
        self.txt_tim_kiem.addAction(qta.icon('fa5s.search', color='#94a3b8'), QLineEdit.ActionPosition.LeadingPosition)
        self.txt_tim_kiem.textChanged.connect(self.loc_cay)
        khung_top.addWidget(self.txt_tim_kiem)

        self.chk_chon_tat_ca = QCheckBox("Chọn tất cả")
        self.chk_chon_tat_ca.setChecked(True)
        self.chk_chon_tat_ca.toggled.connect(self.chon_tat_ca_cay)
        khung_top.addWidget(self.chk_chon_tat_ca)
        layout.addLayout(khung_top)

        self.cay_rule = QTreeWidget()
        self.cay_rule.setHeaderLabels(["Danh sách Quy tắc", "Mã"])
        self.cay_rule.setColumnWidth(0, 500)
        self.cay_rule.itemChanged.connect(self.xu_ly_tick_cay)
        layout.addWidget(self.cay_rule)

        khung_btn = QHBoxLayout()

        self.chk_luu_mac_dinh = QCheckBox(" Lưu cấu hình này cho lần mở App sau")
        self.chk_luu_mac_dinh.setStyleSheet("color: #475569; font-style: italic; font-weight: bold;")
        khung_btn.addWidget(self.chk_luu_mac_dinh)

        khung_btn.addStretch()

        btn_huy = QPushButton("Hủy bỏ")
        btn_huy.clicked.connect(self.reject)

        self.btn_xac_nhan = QPushButton(" Xác nhận chạy")
        self.btn_xac_nhan.setProperty("class", "BtnLuu")
        self.btn_xac_nhan.setIcon(qta.icon('fa5s.check', color='white'))
        self.btn_xac_nhan.clicked.connect(self.luu_ket_qua)

        khung_btn.addWidget(btn_huy)
        khung_btn.addWidget(self.btn_xac_nhan)
        layout.addLayout(khung_btn)

        self.luu_vinh_vien = False

    def nap_du_lieu_len_cay(self):
        self.cay_rule.blockSignals(True)
        self.cay_rule.clear()

        nhom_dict = {}
        for ma_pt, cfg in self.dict_cong_thuc.items():
            nhom = cfg.get("nhom", "Chưa phân loại")
            if nhom not in nhom_dict:
                nhom_dict[nhom] = []
            nhom_dict[nhom].append((ma_pt, cfg.get("ten_phan_tich", "")))

        for nhom, ds_rule in nhom_dict.items():
            node_nhom = QTreeWidgetItem(self.cay_rule, [f"📂 {nhom} ({len(ds_rule)})"])
            node_nhom.setFlags(node_nhom.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            node_nhom.setCheckState(0, Qt.CheckState.Checked)
            node_nhom.setFont(0, self.cay_rule.font())
            node_nhom.font(0).setBold(True)

            for ma_pt, ten_pt in ds_rule:
                node_rule = QTreeWidgetItem(node_nhom, [f"{ten_pt}", ma_pt])
                node_rule.setFlags(node_rule.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                node_rule.setCheckState(0, Qt.CheckState.Checked)

        self.cay_rule.expandAll()
        self.cay_rule.blockSignals(False)

    def xu_ly_tick_cay(self, item, column):
        self.cay_rule.blockSignals(True)
        trang_thai = item.checkState(0)

        if item.childCount() > 0:
            for i in range(item.childCount()):
                item.child(i).setCheckState(0, trang_thai)
        else:
            cha = item.parent()
            if cha:
                co_checked = False
                for i in range(cha.childCount()):
                    if cha.child(i).checkState(0) == Qt.CheckState.Checked:
                        co_checked = True
                        break
                cha.setCheckState(0, Qt.CheckState.Checked if co_checked else Qt.CheckState.Unchecked)

        self.cay_rule.blockSignals(False)

    def chon_tat_ca_cay(self, checked):
        trang_thai = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        self.cay_rule.blockSignals(True)
        for i in range(self.cay_rule.topLevelItemCount()):
            cha = self.cay_rule.topLevelItem(i)
            cha.setCheckState(0, trang_thai)
            for j in range(cha.childCount()):
                cha.child(j).setCheckState(0, trang_thai)
        self.cay_rule.blockSignals(False)

    def loc_cay(self, text):
        text = text.lower()
        for i in range(self.cay_rule.topLevelItemCount()):
            cha = self.cay_rule.topLevelItem(i)
            cha_match = text in cha.text(0).lower()
            co_con_match = False

            for j in range(cha.childCount()):
                con = cha.child(j)
                con_match = text in con.text(0).lower() or text in con.text(1).lower()
                con.setHidden(not (con_match or cha_match))
                if con_match: co_con_match = True

            cha.setHidden(not (cha_match or co_con_match))
            if text: cha.setExpanded(True)

    def luu_ket_qua(self):
        self.danh_sach_chon = []
        for i in range(self.cay_rule.topLevelItemCount()):
            cha = self.cay_rule.topLevelItem(i)
            for j in range(cha.childCount()):
                con = cha.child(j)
                if con.checkState(0) == Qt.CheckState.Checked:
                    self.danh_sach_chon.append(con.text(1))

        self.luu_vinh_vien = self.chk_luu_mac_dinh.isChecked()
        self.accept()