import json
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QMessageBox, QLabel, QTabWidget, QWidget, QListWidget,
                               QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog)
from PySide6.QtCore import Qt


class DialogCauHinhChuoiCungUng(QDialog):
    def __init__(self, parent=None, config_path="Data/chuoi_cung_ung.json"):
        super().__init__(parent)
        self.config_path = config_path
        self.setWindowTitle("Cấu hình Chuỗi Cung Ứng (Giao diện Trực quan)")
        self.resize(900, 600)
        self.data = {"danh_muc_tag": {}, "luat_cung_ung": []}
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # TAB 1: Quản lý Tag
        tab_tag = QWidget()
        lay_tag = QHBoxLayout(tab_tag)

        khung_trai = QVBoxLayout()
        self.list_tags = QListWidget()
        self.list_tags.currentItemChanged.connect(self.hien_thi_tu_khoa)
        btn_add_tag = QPushButton("Thêm Nhãn")
        btn_add_tag.clicked.connect(self.them_nhan)
        btn_del_tag = QPushButton("Xóa Nhãn")
        btn_del_tag.clicked.connect(self.xoa_nhan)
        khung_trai.addWidget(QLabel("Danh sách Nhãn (Tag):"))
        khung_trai.addWidget(self.list_tags)
        khung_trai.addWidget(btn_add_tag)
        khung_trai.addWidget(btn_del_tag)
        lay_tag.addLayout(khung_trai, 1)

        khung_phai = QVBoxLayout()
        self.txt_tu_khoa = QTextEdit()
        btn_luu_tu_khoa = QPushButton("Cập nhật Từ khóa")
        btn_luu_tu_khoa.clicked.connect(self.cap_nhat_tu_khoa)
        khung_phai.addWidget(QLabel("Từ khóa nhận diện (cách nhau bằng dấu phẩy):"))
        khung_phai.addWidget(self.txt_tu_khoa)
        khung_phai.addWidget(btn_luu_tu_khoa)
        lay_tag.addLayout(khung_phai, 2)

        self.tabs.addTab(tab_tag, "Quản lý Nhãn")

        # TAB 2: Quản lý Luật
        tab_rule = QWidget()
        lay_rule = QVBoxLayout(tab_rule)
        self.table_rules = QTableWidget(0, 4)
        self.table_rules.setHorizontalHeaderLabels(
            ["Mã", "Tên Mô hình", "Đầu vào (cách bởi phẩy)", "Đầu ra (cách bởi phẩy)"])
        self.table_rules.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        khung_btn_rule = QHBoxLayout()
        btn_add_rule = QPushButton("Thêm Mô hình")
        btn_add_rule.clicked.connect(self.them_rule)
        btn_del_rule = QPushButton("Xóa Mô hình")
        btn_del_rule.clicked.connect(self.xoa_rule)
        khung_btn_rule.addWidget(btn_add_rule)
        khung_btn_rule.addWidget(btn_del_rule)
        khung_btn_rule.addStretch()

        lay_rule.addLayout(khung_btn_rule)
        lay_rule.addWidget(self.table_rules)
        self.tabs.addTab(tab_rule, "Cấu hình Mô hình")

        btn_luu_all = QPushButton("LƯU CẤU HÌNH")
        btn_luu_all.clicked.connect(self.luu_toan_bo)
        layout.addWidget(btn_luu_all)

    def load_data(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

        self.list_tags.clear()
        for group, tags in self.data.get("danh_muc_tag", {}).items():
            if group == "Mô tả": continue
            for tag in tags.keys():
                if tag != "Mô tả":
                    self.list_tags.addItem(tag)

        rules = self.data.get("luat_cung_ung", [])
        self.table_rules.setRowCount(0)
        for r in rules:
            row = self.table_rules.rowCount()
            self.table_rules.insertRow(row)
            self.table_rules.setItem(row, 0, QTableWidgetItem(r.get("ma_loai_hinh", "")))
            self.table_rules.setItem(row, 1, QTableWidgetItem(r.get("ten_mo_hinh", "")))
            self.table_rules.setItem(row, 2, QTableWidgetItem(", ".join(r.get("dau_vao_bat_buoc", []))))
            self.table_rules.setItem(row, 3, QTableWidgetItem(", ".join(r.get("dau_ra_hop_le", []))))

    def hien_thi_tu_khoa(self, current, previous):
        if not current: return
        tag_name = current.text()
        for group, tags in self.data.get("danh_muc_tag", {}).items():
            if tag_name in tags:
                self.txt_tu_khoa.setPlainText(", ".join(tags[tag_name]))
                return

    def them_nhan(self):
        ten_nhan, ok = QInputDialog.getText(self, "Thêm Nhãn", "Nhập tên nhãn mới (VD: [HÀNG HÓA MỚI]):")
        if ok and ten_nhan:
            self.list_tags.addItem(ten_nhan)
            if "1. CHI PHÍ CƠ BẢN VÀ TÀI SẢN" not in self.data["danh_muc_tag"]:
                self.data["danh_muc_tag"]["1. CHI PHÍ CƠ BẢN VÀ TÀI SẢN"] = {}
            self.data["danh_muc_tag"]["1. CHI PHÍ CƠ BẢN VÀ TÀI SẢN"][ten_nhan] = []

    def xoa_nhan(self):
        curr = self.list_tags.currentItem()
        if curr:
            tag_name = curr.text()
            for group, tags in self.data["danh_muc_tag"].items():
                if tag_name in tags:
                    del self.data["danh_muc_tag"][group][tag_name]
                    break
            self.list_tags.takeItem(self.list_tags.row(curr))
            self.txt_tu_khoa.clear()

    def cap_nhat_tu_khoa(self):
        curr = self.list_tags.currentItem()
        if curr:
            tag_name = curr.text()
            tu_khoa_moi = [k.strip() for k in self.txt_tu_khoa.toPlainText().split(",") if k.strip()]
            for group, tags in self.data["danh_muc_tag"].items():
                if tag_name in tags:
                    self.data["danh_muc_tag"][group][tag_name] = tu_khoa_moi
                    QMessageBox.information(self, "Thành công", f"Đã cập nhật từ khóa cho {tag_name}")
                    return

    def them_rule(self):
        row = self.table_rules.rowCount()
        self.table_rules.insertRow(row)

    def xoa_rule(self):
        curr = self.table_rules.currentRow()
        if curr >= 0:
            self.table_rules.removeRow(curr)

    def luu_toan_bo(self):
        new_rules = []
        for row in range(self.table_rules.rowCount()):
            ma = self.table_rules.item(row, 0).text() if self.table_rules.item(row, 0) else ""
            ten = self.table_rules.item(row, 1).text() if self.table_rules.item(row, 1) else ""
            vao = self.table_rules.item(row, 2).text() if self.table_rules.item(row, 2) else ""
            ra = self.table_rules.item(row, 3).text() if self.table_rules.item(row, 3) else ""

            new_rules.append({
                "ma_loai_hinh": ma,
                "ten_mo_hinh": ten,
                "quy_tac_doi_chieu": "CHUOI_GIA_TRI",
                "dau_vao_bat_buoc": [k.strip() for k in vao.split(",") if k.strip()],
                "dau_ra_hop_le": [k.strip() for k in ra.split(",") if k.strip()],
                "canh_bao_ty_trong": []
            })

        self.data["luat_cung_ung"] = new_rules
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

        QMessageBox.information(self, "Thành công", "Đã lưu cấu hình!")
        self.accept()