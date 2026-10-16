import json
import os
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox, QFrame
from PySide6.QtCore import Qt, QRect, QPoint, QEvent, QTimer
from PySide6.QtGui import QPainter, QColor, QRegion, QPen
import qtawesome as qta


class HuongDanTour(QWidget):
    # ĐÃ SỬA: Thêm tham số ham_chuyen_tab
    def __init__(self, parent, danh_sach_buoc, ham_chuyen_tab=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.danh_sach_buoc = danh_sach_buoc
        self.ham_chuyen_tab = ham_chuyen_tab
        self.buoc_hien_tai = 0
        self.target_rect = QRect()
        # ---> THÊM BIẾN NÀY ĐỂ NHỚ XEM ĐANG Ở TAB NÀO <---
        self.tab_dang_mo = -1
        self.setWindowFlags(Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        self.thiet_lap_ui_popup()
        self.parent_widget.installEventFilter(self)
        self.cap_nhat_kich_thuoc()

    def thiet_lap_ui_popup(self):
        self.popup = QFrame(self)
        self.popup.setStyleSheet("""
            QFrame { background-color: #FFFFFF; border: 2px solid #3B82F6; border-radius: 8px; }
            QLabel#TieuDe { font-size: 16px; font-weight: bold; color: #1E3A8A; border: none; }
            QLabel#NoiDung { font-size: 14px; color: #374151; border: none; }
            QPushButton { font-weight: bold; padding: 8px 15px; border-radius: 4px; border: none; }
            QPushButton#BtnTiep { background-color: #3B82F6; color: white; }
            QPushButton#BtnTiep:hover { background-color: #2563EB; }
            QPushButton#BtnBoQua { background-color: #F3F4F6; color: #4B5563; }
            QPushButton#BtnBoQua:hover { background-color: #E5E7EB; }
            QCheckBox { border: none; color: #6B7280; font-size: 12px; }
        """)

        layout_tong = QVBoxLayout(self.popup)
        self.lbl_tieu_de = QLabel("Tiêu đề")
        self.lbl_tieu_de.setObjectName("TieuDe")
        self.lbl_noi_dung = QLabel("Nội dung...")
        self.lbl_noi_dung.setObjectName("NoiDung")
        self.lbl_noi_dung.setWordWrap(True)

        layout_tong.addWidget(self.lbl_tieu_de)
        layout_tong.addWidget(self.lbl_noi_dung)
        layout_tong.addSpacing(10)

        khung_btn = QHBoxLayout()
        self.chk_khong_hien_thi = QCheckBox("Không hiện lại lần sau")
        self.chk_khong_hien_thi.setChecked(True)

        self.btn_bo_qua = QPushButton(" Bỏ qua")
        self.btn_bo_qua.setObjectName("BtnBoQua")
        self.btn_bo_qua.setIcon(qta.icon('fa5s.times', color='#4B5563'))
        self.btn_bo_qua.clicked.connect(self.ket_thuc_tour)

        self.btn_tiep_theo = QPushButton("Tiếp theo ")
        self.btn_tiep_theo.setObjectName("BtnTiep")
        self.btn_tiep_theo.clicked.connect(self.chuyen_buoc_tiep)

        khung_btn.addWidget(self.chk_khong_hien_thi)
        khung_btn.addStretch()
        khung_btn.addWidget(self.btn_bo_qua)
        khung_btn.addWidget(self.btn_tiep_theo)

        layout_tong.addLayout(khung_btn)
        self.popup.setFixedSize(400, 180)

    def cap_nhat_kich_thuoc(self):
        self.resize(self.parent_widget.size())

    def eventFilter(self, obj, event):
        if obj == self.parent_widget and event.type() == QEvent.Type.Resize:
            self.cap_nhat_kich_thuoc()
            self.hien_thi_buoc(self.buoc_hien_tai)
        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        mau_nen_den = QColor(0, 0, 0, 170)
        vung_toan_man_hinh = QRegion(self.rect())
        vung_duc_lo = QRegion(self.target_rect)
        vung_con_lai = vung_toan_man_hinh.subtracted(vung_duc_lo)

        painter.setClipRegion(vung_con_lai)
        painter.fillRect(self.rect(), mau_nen_den)

        painter.setClipping(False)
        vieng_sang = QPen(QColor(59, 130, 246), 4)
        painter.setPen(vieng_sang)
        painter.drawRoundedRect(self.target_rect.adjusted(-2, -2, 2, 2), 4, 4)

    def bat_dau(self):
        self.show()
        self.raise_()
        self.hien_thi_buoc(0)

    # ĐÃ SỬA: Tách luồng bằng QTimer để chờ Giao diện load xong Tab mới
    def hien_thi_buoc(self, index):
        if index >= len(self.danh_sach_buoc):
            self.ket_thuc_tour()
            return

        thong_tin = self.danh_sach_buoc[index]

        # ---> ĐÃ SỬA LẠI LOGIC CHUYỂN TAB Ở ĐÂY <---
        # Chỉ khi nào thông số tab_index KHÁC với tab đang mở thì mới ra lệnh chuyển Tab
        if "tab_index" in thong_tin and self.ham_chuyen_tab and thong_tin["tab_index"] != self.tab_dang_mo:
            self.tab_dang_mo = thong_tin["tab_index"]
            self.ham_chuyen_tab(self.tab_dang_mo)
            # Nghỉ 250ms chờ UI chuyển Tab xong mới đục lỗ
            QTimer.singleShot(250, lambda: self._ve_highlight_buoc(thong_tin, index))
        else:
            # Nếu vẫn ở Tab cũ, đục lỗ sang nút khác luôn không cần delay
            self._ve_highlight_buoc(thong_tin, index)

    def _ve_highlight_buoc(self, thong_tin, index):
        widget_muc_tieu = thong_tin["widget"]
        diem_toan_cuc = widget_muc_tieu.mapToGlobal(QPoint(0, 0))
        diem_cuc_bo = self.mapFromGlobal(diem_toan_cuc)
        self.target_rect = QRect(diem_cuc_bo, widget_muc_tieu.size())

        self.lbl_tieu_de.setText(f"Bước {index + 1}/{len(self.danh_sach_buoc)}: {thong_tin['tieu_de']}")
        self.lbl_noi_dung.setText(thong_tin['noi_dung'])

        if index == len(self.danh_sach_buoc) - 1:
            self.btn_tiep_theo.setText("Hoàn thành ")
            self.btn_tiep_theo.setIcon(qta.icon('fa5s.check', color='white'))
            self.btn_tiep_theo.setStyleSheet("background-color: #10B981;")
        else:
            self.btn_tiep_theo.setText("Tiếp theo ")
            self.btn_tiep_theo.setIcon(qta.icon('fa5s.arrow-right', color='white'))
            self.btn_tiep_theo.setStyleSheet("background-color: #3B82F6;")

        # ==============================================================
        # THUẬT TOÁN ĐỊNH VỊ THÔNG MINH (SMART POSITIONING)
        # ==============================================================
        pw = self.popup.width()
        ph = self.popup.height()
        sw = self.width()  # Chiều rộng toàn màn hình phần mềm
        sh = self.height()  # Chiều cao toàn màn hình phần mềm

        # 1. Mặc định đặt Popup ở bên DƯỚI nút bấm
        x_popup = self.target_rect.left()
        y_popup = self.target_rect.bottom() + 15

        # 2. Chống kịch TRẦN DƯỚI: Nếu đụng đáy màn hình -> Lật ngược lên TRÊN nút bấm
        if y_popup + ph > sh:
            y_popup = self.target_rect.top() - ph - 15

        # 3. Chống kịch LỀ PHẢI: Nếu tràn sang phải -> Ép sát nó vào lề phải màn hình
        if x_popup + pw > sw:
            x_popup = sw - pw - 15

        # 4. Chống kịch LỀ TRÁI: (Dự phòng) Ép sát vào lề trái
        if x_popup < 0:
            x_popup = 15

        self.popup.move(x_popup, y_popup)
        self.update()

    def chuyen_buoc_tiep(self):
        self.buoc_hien_tai += 1
        self.hien_thi_buoc(self.buoc_hien_tai)

    def ket_thuc_tour(self):
        if self.chk_khong_hien_thi.isChecked():
            os.makedirs("Data", exist_ok=True)
            try:
                with open("Data/tour_config.json", "w", encoding="utf-8") as f:
                    json.dump({"show_tour": False}, f)
            except:
                pass

        self.parent_widget.removeEventFilter(self)
        self.hide()
        self.deleteLater()