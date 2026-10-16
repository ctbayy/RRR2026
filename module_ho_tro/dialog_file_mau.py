import pandas as pd
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel, QFileDialog
from PySide6.QtCore import Qt
import qtawesome as qta
import xlsxwriter
from module_ho_tro.tao_template_excel import tao_file_mau_cdsps


class DialogKhoFileMau(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📥 Kho File Mẫu (Templates)")
        self.resize(380, 200)

        # Áp Style hiện đại
        self.setStyleSheet("""
            QDialog { background-color: #F8FAFC; }
            QLabel { font-size: 13px; font-weight: bold; color: #334155; }
        """)
        self.thiet_lap_ui()

    def thiet_lap_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Vui lòng chọn loại Biểu mẫu cần tải về:"))

        # 1. NÚT TẢI MẪU HÓA ĐƠN
        self.btn_mau_hoa_don = QPushButton(" Tải Mẫu Bảng kê Hóa đơn")
        self.btn_mau_hoa_don.setIcon(qta.icon('fa5s.file-excel', color='#10B981'))
        self.btn_mau_hoa_don.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mau_hoa_don.setStyleSheet("""
            QPushButton { padding: 14px; font-size: 13px; font-weight: bold; color: #065F46; 
                          background-color: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 6px; text-align: left; }
            QPushButton:hover { background-color: #D1FAE5; }
        """)
        self.btn_mau_hoa_don.clicked.connect(self.tai_mau_hoa_don)
        layout.addWidget(self.btn_mau_hoa_don)

        # 2. NÚT TẢI MẪU CĐSPS (TT200)
        self.btn_mau_tt200 = QPushButton(" Tải Mẫu Bảng CĐSPS (Thông tư 200)")
        self.btn_mau_tt200.setIcon(qta.icon('fa5s.file-excel', color='#2563EB'))
        self.btn_mau_tt200.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mau_tt200.setStyleSheet("""
            QPushButton { padding: 14px; font-size: 13px; font-weight: bold; color: #1E3A8A; 
                          background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 6px; text-align: left; }
            QPushButton:hover { background-color: #DBEAFE; }
        """)
        self.btn_mau_tt200.clicked.connect(self.tai_mau_tt200)
        layout.addWidget(self.btn_mau_tt200)

        layout.addStretch()

    def tai_mau_hoa_don(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu Mẫu Hóa Đơn", "Template_Hoa_Don_Chuan.xlsx",
                                                   "Excel Files (*.xlsx)")
        if not file_path: return

        # Cột chuẩn tiếng Việt
        columns = [
            'STT', 'Trạng thái hóa đơn', 'Ký hiệu HĐ', 'Số HĐ', 'Ngày lập',
            'Mã số thuế người bán', 'Tên người bán', 'MST người mua', 'Tên người mua',
            'Tên hàng hóa/dịch vụ', 'Đơn vị tính', 'Số lượng', 'Đơn giá',
            'Số tiền chiết khấu', 'Thành tiền', 'Thuế suất GTGT(%)', 'Tiền thuế',
            'Tổng tiền thanh toán', 'Tính chất', 'Ghi chú'
        ]

        try:
            df = pd.DataFrame(columns=columns)
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Hoadon_Chitiet', index=False)
                workbook = writer.book
                worksheet = writer.sheets['Hoadon_Chitiet']

                # Format Header
                header_format = workbook.add_format(
                    {'bold': True, 'valign': 'center', 'align': 'center', 'fg_color': '#005FB8', 'font_color': 'white',
                     'border': 1})
                text_format = workbook.add_format({'num_format': '@'})

                # Set độ rộng cột
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    if value in ['Tên người bán', 'Tên người mua', 'Tên hàng hóa/dịch vụ']:
                        worksheet.set_column(col_num, col_num, 40, text_format)
                    elif 'Mã số thuế' in value or 'MST' in value or 'Số HĐ' in value:
                        worksheet.set_column(col_num, col_num, 18, text_format)
                    elif value == 'STT':
                        worksheet.set_column(col_num, col_num, 8)
                    else:
                        worksheet.set_column(col_num, col_num, 15)

            QMessageBox.information(self, "Thành công", f"Đã lưu file mẫu Hóa đơn tại:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {e}")

    def tai_mau_tt200(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu Mẫu Bảng CĐSPS", "Bang_CDSPS_TT200_Template.xlsx",
                                                   "Excel Files (*.xlsx)")
        if file_path:
            try:
                tao_file_mau_cdsps(file_path)
                QMessageBox.information(self, "Thành công", f"Đã lưu file mẫu CĐSPS tại:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {e}")