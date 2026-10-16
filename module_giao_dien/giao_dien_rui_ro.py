# module_giao_dien/giao_dien_rui_ro.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                               QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
import qtawesome as qta
from module_doc_hoadon.hoadon_ruiro import HoaDonRuiRoManager


class GiaoDienQuanLyRuiRo(QWidget):  # Đổi từ QDialog sang QWidget
    def __init__(self, parent=None):
        super().__init__(parent)

        # Khởi tạo cỗ máy lõi của mày
        self.ruiro_mgr = HoaDonRuiRoManager()

        # Thiết kế dạng phẳng (Flat), không viền, nền trắng tinh tế
        self.setStyleSheet("""
            QWidget { background-color: #FFFFFF; font-family: 'Segoe UI', Arial; border-radius: 8px; }
            QLabel.Title { font-size: 18px; font-weight: bold; color: #0F172A; }
            QPushButton { font-weight: bold; padding: 10px 15px; border-radius: 6px; font-size: 13px; border: none; }
            QPushButton#BtnSync { background-color: #0284C7; color: white; }
            QPushButton#BtnSync:hover { background-color: #0369A1; }
            QPushButton#BtnUpload { background-color: #DC2626; color: white; }
            QPushButton#BtnUpload:hover { background-color: #B91C1C; }

            QTableWidget { background-color: #F9FAFB; border: 1px solid #E5E7EB; gridline-color: transparent; border-radius: 8px; }
            QHeaderView::section { background-color: #E2EEF9; color: #334155; font-weight: bold; border: none; border-bottom: 2px solid #C0D6E4; padding: 12px; text-align: left; }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #E5E7EB; }
            QTableWidget::item:hover { background-color: #EFF6FF; }
        """)

        self.thiet_lap_ui()
        self.hien_thi_danh_sach()

    def thiet_lap_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        lbl_title = QLabel(" DANH MỤC MÃ SỐ THUẾ CẢNH BÁO RỦI RO")
        lbl_title.setProperty("class", "Title")

        btn_sync = QPushButton(" Đồng bộ Cloud")
        btn_sync.setObjectName("BtnSync")
        btn_sync.setIcon(qta.icon('fa5s.sync-alt', color='white'))
        btn_sync.clicked.connect(self.dong_bo_cloud)

        btn_upload = QPushButton(" Tải file Excel Cập nhật")
        btn_upload.setObjectName("BtnUpload")
        btn_upload.setIcon(qta.icon('fa5s.file-excel', color='white'))
        btn_upload.clicked.connect(self.tai_file_cap_nhat)

        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(btn_sync)
        header_layout.addWidget(btn_upload)
        layout.addLayout(header_layout)

        # --- BẢNG HIỂN THỊ DỮ LIỆU ---
        self.bang_du_lieu = QTableWidget()
        self.bang_du_lieu.setColumnCount(4)
        self.bang_du_lieu.setHorizontalHeaderLabels([
            "Mã số thuế", "Dấu hiệu vi phạm", "Nội dung văn bản / Quyết định", "Cập nhật lần cuối"
        ])
        self.bang_du_lieu.setEditTriggers(QTableWidget.NoEditTriggers)
        self.bang_du_lieu.setAlternatingRowColors(True)

        header = self.bang_du_lieu.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        self.bang_du_lieu.setColumnWidth(0, 120)
        self.bang_du_lieu.setColumnWidth(1, 280)
        self.bang_du_lieu.setColumnWidth(3, 180)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.bang_du_lieu.setWordWrap(True)
        self.bang_du_lieu.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        layout.addWidget(self.bang_du_lieu)

    def hien_thi_danh_sach(self):
        df = self.ruiro_mgr.get_all_data_as_df()
        self.bang_du_lieu.setRowCount(len(df))
        for row_idx, row in df.iterrows():
            self.bang_du_lieu.setItem(row_idx, 0, QTableWidgetItem(str(row['MST'])))
            self.bang_du_lieu.setItem(row_idx, 1, QTableWidgetItem(str(row['Dấu hiệu'])))
            self.bang_du_lieu.setItem(row_idx, 2, QTableWidgetItem(str(row['Nội dung'])))
            self.bang_du_lieu.setItem(row_idx, 3, QTableWidgetItem(str(row['Cập nhật lần cuối'])))

    def dong_bo_cloud(self):
        thanh_cong, msg = self.ruiro_mgr.sync_from_cloud()
        if thanh_cong:
            self.hien_thi_danh_sach()
            QMessageBox.information(self, "Đồng bộ thành công", msg)
        else:
            QMessageBox.warning(self, "Lỗi đồng bộ", msg)

    def tai_file_cap_nhat(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file Excel mẫu chứa MST Rủi ro", "",
                                                   "Excel Files (*.xlsx *.xls)")
        if file_path:
            thanh_cong, msg = self.ruiro_mgr.upload_data_from_template(file_path)
            if thanh_cong:
                self.hien_thi_danh_sach()
                QMessageBox.information(self, "Cập nhật thành công", msg)
            else:
                QMessageBox.warning(self, "Lỗi cập nhật", msg)