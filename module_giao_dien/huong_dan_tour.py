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
        self._timer_chuyen_tab = None
        self.parent_widget.installEventFilter(self)
        self.cap_nhat_kich_thuoc()

    def thiet_lap_ui_popup(self):
        self.popup = QFrame(self)
        self.popup.setStyleSheet("""
            QFrame { background-color: #FFFFFF; border: 2px solid #3B82F6; border-radius: 8px; }
            QLabel#TieuDe { font-size: 15px; font-weight: bold; color: #1E3A8A; border: none; }
            QLabel#NoiDung { font-size: 13.5px; color: #374151; border: none; line-height: 1.5; }
            QPushButton { font-weight: bold; padding: 7px 13px; border-radius: 5px; border: none; font-size: 12px; }
            QPushButton#BtnTiep { background-color: #3B82F6; color: white; }
            QPushButton#BtnTiep:hover { background-color: #2563EB; }
            QPushButton#BtnQuayLai { background-color: #F1F5F9; color: #475569; border: 1px solid #CBD5E1; }
            QPushButton#BtnQuayLai:hover { background-color: #E2E8F0; }
            QPushButton#BtnQuayLai:disabled { background-color: #F8FAFC; color: #CBD5E1; border-color: #E2E8F0; }
            QPushButton#BtnBoQua { background-color: transparent; color: #64748B; }
            QPushButton#BtnBoQua:hover { color: #DC2626; text-decoration: underline; }
            QCheckBox { border: none; color: #6B7280; font-size: 11.5px; }
        """)

        layout_tong = QVBoxLayout(self.popup)
        self.lbl_tieu_de = QLabel("Tiêu đề")
        self.lbl_tieu_de.setObjectName("TieuDe")
        self.lbl_noi_dung = QLabel("Nội dung...")
        self.lbl_noi_dung.setObjectName("NoiDung")
        self.lbl_noi_dung.setWordWrap(True)

        layout_tong.addWidget(self.lbl_tieu_de)
        layout_tong.addWidget(self.lbl_noi_dung)
        layout_tong.addSpacing(6)

        khung_btn = QHBoxLayout()
        self.chk_khong_hien_thi = QCheckBox("Không hiện lại")
        self.chk_khong_hien_thi.setChecked(True)

        self.btn_bo_qua = QPushButton("Bỏ qua")
        self.btn_bo_qua.setObjectName("BtnBoQua")
        self.btn_bo_qua.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_bo_qua.clicked.connect(self.ket_thuc_tour)

        self.btn_quay_lai = QPushButton(" Quay lại")
        self.btn_quay_lai.setObjectName("BtnQuayLai")
        self.btn_quay_lai.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_quay_lai.setIcon(qta.icon('fa5s.arrow-left', color='#475569'))
        self.btn_quay_lai.clicked.connect(self.chuyen_buoc_truoc)

        self.btn_tiep_theo = QPushButton("Tiếp theo ")
        self.btn_tiep_theo.setObjectName("BtnTiep")
        self.btn_tiep_theo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tiep_theo.clicked.connect(self.chuyen_buoc_tiep)

        khung_btn.addWidget(self.chk_khong_hien_thi)
        khung_btn.addStretch()
        khung_btn.addWidget(self.btn_bo_qua)
        khung_btn.addWidget(self.btn_quay_lai)
        khung_btn.addWidget(self.btn_tiep_theo)

        layout_tong.addLayout(khung_btn)
        self.popup.setFixedSize(430, 190)

    def cap_nhat_kich_thuoc(self):
        self.resize(self.parent_widget.size())

    def eventFilter(self, obj, event):
        if obj == self.parent_widget and event.type() == QEvent.Type.Resize:
            self.cap_nhat_kich_thuoc()
            self.hien_thi_buoc(self.buoc_hien_tai)
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.ket_thuc_tour()
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.chuyen_buoc_tiep()
        elif key == Qt.Key.Key_Left:
            self.chuyen_buoc_truoc()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        mau_nen_den = QColor(0, 0, 0, 170)

        if not self.target_rect.isEmpty() and self.target_rect.width() > 0:
            vung_toan_man_hinh = QRegion(self.rect())
            rect_halo = self.target_rect.adjusted(-3, -3, 3, 3)
            vung_duc_lo = QRegion(rect_halo)
            vung_con_lai = vung_toan_man_hinh.subtracted(vung_duc_lo)

            painter.setClipRegion(vung_con_lai)
            painter.fillRect(self.rect(), mau_nen_den)

            painter.setClipping(False)
            vieng_sang = QPen(QColor(59, 130, 246), 3)
            painter.setPen(vieng_sang)
            painter.drawRoundedRect(rect_halo, 6, 6)
        else:
            painter.fillRect(self.rect(), mau_nen_den)

    def bat_dau(self):
        self.show()
        self.raise_()
        self.setFocus()
        self.buoc_hien_tai = 0
        self.hien_thi_buoc(0)

    def hien_thi_buoc(self, index):
        if index >= len(self.danh_sach_buoc):
            self.ket_thuc_tour()
            return
        if index < 0:
            index = 0
        self.buoc_hien_tai = index

        thong_tin = self.danh_sach_buoc[index]

        if self._timer_chuyen_tab:
            self._timer_chuyen_tab.stop()
            self._timer_chuyen_tab = None

        # Chỉ khi nào thông số tab_index KHÁC với tab đang mở thì mới ra lệnh chuyển Tab
        if "tab_index" in thong_tin and self.ham_chuyen_tab and thong_tin["tab_index"] != self.tab_dang_mo:
            self.tab_dang_mo = thong_tin["tab_index"]
            self.ham_chuyen_tab(self.tab_dang_mo)
            # Chờ UI chuyển Tab xong mới đục lỗ
            self._timer_chuyen_tab = QTimer()
            self._timer_chuyen_tab.setSingleShot(True)
            self._timer_chuyen_tab.timeout.connect(lambda: self._ve_highlight_buoc(thong_tin, index))
            self._timer_chuyen_tab.start(250)
        else:
            self._ve_highlight_buoc(thong_tin, index)

    def _ve_highlight_buoc(self, thong_tin, index):
        widget_muc_tieu = thong_tin.get("widget")
        if widget_muc_tieu is not None:
            try:
                diem_toan_cuc = widget_muc_tieu.mapToGlobal(QPoint(0, 0))
                diem_cuc_bo = self.mapFromGlobal(diem_toan_cuc)
                self.target_rect = QRect(diem_cuc_bo, widget_muc_tieu.size())
            except Exception:
                self.target_rect = QRect()
        else:
            self.target_rect = QRect()

        self.lbl_tieu_de.setText(f"Bước {index + 1}/{len(self.danh_sach_buoc)}: {thong_tin['tieu_de']}")
        self.lbl_noi_dung.setText(thong_tin['noi_dung'])

        # Cập nhật trạng thái nút Quay lại
        self.btn_quay_lai.setEnabled(index > 0)

        # Cập nhật trạng thái nút Tiếp theo / Hoàn thành
        if index == len(self.danh_sach_buoc) - 1:
            self.btn_tiep_theo.setText("Hoàn thành ")
            self.btn_tiep_theo.setIcon(qta.icon('fa5s.check', color='white'))
            self.btn_tiep_theo.setStyleSheet("background-color: #10B981; color: white;")
        else:
            self.btn_tiep_theo.setText("Tiếp theo ")
            self.btn_tiep_theo.setIcon(qta.icon('fa5s.arrow-right', color='white'))
            self.btn_tiep_theo.setStyleSheet("background-color: #3B82F6; color: white;")

        # ==============================================================
        # THUẬT TOÁN ĐỊNH VỊ THÔNG MINH (SMART POSITIONING)
        # ==============================================================
        pw = self.popup.width()
        ph = self.popup.height()
        sw = self.width()   # Chiều rộng toàn màn hình
        sh = self.height()  # Chiều cao toàn màn hình

        if self.target_rect.isEmpty() or self.target_rect.width() <= 0:
            x_popup = max(15, (sw - pw) // 2)
            y_popup = max(15, (sh - ph) // 2)
        # 1. Nếu widget mục tiêu nằm trên thanh Sidebar bên trái (width < 320)
        elif self.target_rect.right() <= 320 and self.target_rect.width() < 300:
            x_popup = self.target_rect.right() + 15
            y_popup = self.target_rect.center().y() - ph // 2
            if y_popup + ph > sh - 20:
                y_popup = sh - ph - 20
            if y_popup < 20:
                y_popup = 20
        else:
            # 2. Mặc định đặt Popup ở bên DƯỚI nút bấm
            x_popup = self.target_rect.left()
            y_popup = self.target_rect.bottom() + 15

            # Chống kịch trần dưới: Nếu đụng đáy màn hình -> Lật ngược lên TRÊN nút bấm
            if y_popup + ph > sh - 15:
                y_popup = self.target_rect.top() - ph - 15

            # Chống kịch lề phải: Nếu tràn sang phải -> Ép sát vào lề phải
            if x_popup + pw > sw - 15:
                x_popup = sw - pw - 15

            # Chống kịch lề trái & trần trên
            if x_popup < 15:
                x_popup = 15
            if y_popup < 15:
                y_popup = 15

        self.popup.move(x_popup, y_popup)
        self.update()

    def chuyen_buoc_truoc(self):
        if self.buoc_hien_tai > 0:
            self.hien_thi_buoc(self.buoc_hien_tai - 1)

    def chuyen_buoc_tiep(self):
        self.buoc_hien_tai += 1
        self.hien_thi_buoc(self.buoc_hien_tai)

    def ket_thuc_tour(self):
        os.makedirs("Data", exist_ok=True)
        try:
            with open("Data/tour_config.json", "w", encoding="utf-8") as f:
                json.dump({"show_tour": not self.chk_khong_hien_thi.isChecked()}, f)
        except Exception:
            pass

        # Khi kết thúc Tour (hoàn thành hoặc bỏ qua), luôn đưa người dùng về Tab 0 để bắt đầu làm việc
        if self.ham_chuyen_tab:
            try:
                self.ham_chuyen_tab(0)
            except Exception:
                pass

        self.parent_widget.removeEventFilter(self)
        self.hide()
        self.deleteLater()