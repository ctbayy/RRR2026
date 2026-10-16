from PySide6.QtWidgets import QCheckBox
from PySide6.QtCore import Qt, QPropertyAnimation, Property, QEasingCurve, QRect, QPointF, QSize
from PySide6.QtGui import QPainter, QColor


class FluentToggle(QCheckBox):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._position = 0.0  # 0.0 là Tắt (Trái), 1.0 là Bật (Phải)

        # Cỗ máy tạo độ mượt 250ms
        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.toggled.connect(self.truot_animation)

    @Property(float)
    def position(self):
        return self._position

    @position.setter
    def position(self, pos):
        self._position = pos
        self.update()  # Ép vẽ lại khung hình liên tục

    def truot_animation(self, checked):
        self.animation.setEndValue(1.0 if checked else 0.0)
        self.animation.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)  # Bật khử răng cưa

        # 1. Tọa độ khung trượt (Rộng 40, Cao 20)
        w, h = 40, 20
        y_offset = (self.height() - h) // 2
        rect = QRect(0, y_offset, w, h)

        # 2. Nội suy màu nền (Từ Xám nhạt sang Xanh Fluent)
        r = int(209 + (0 - 209) * self._position)
        g = int(213 + (95 - 213) * self._position)
        b = int(219 + (184 - 219) * self._position)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(r, g, b))
        p.drawRoundedRect(rect, h / 2, h / 2)

        # 3. Tính toán vị trí và màu cục tròn
        thumb_radius = 6 + (1 * self._position)  # Bật lên thì cục tròn to ra một chút
        thumb_x = 10 + (20 * self._position)  # Trượt từ tọa độ X=10 sang X=30
        thumb_y = y_offset + (h / 2)

        # Màu cục tròn (Từ Xám đậm sang Trắng tinh)
        tr = int(107 + (255 - 107) * self._position)
        tg = int(114 + (255 - 114) * self._position)
        tb = int(128 + (255 - 128) * self._position)

        p.setBrush(QColor(tr, tg, tb))
        p.drawEllipse(QPointF(thumb_x, thumb_y), thumb_radius, thumb_radius)

        # 4. Vẽ Text bên cạnh
        p.setPen(QColor("#374151"))
        text_rect = QRect(w + 12, 0, self.width() - w - 12, self.height())
        p.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.text())
        p.end()
    # BỔ SUNG HÀM NÀY ĐỂ BÁO KÍCH THƯỚC THẬT CHO HỆ THỐNG
    def sizeHint(self):
        font_metrics = self.fontMetrics()
        # Tính toán: Độ rộng cục tròn (40px) + Khoảng cách (12px) + Chiều dài đoạn text + Padding (10px)
        text_width = font_metrics.horizontalAdvance(self.text())
        return QSize(40 + 12 + text_width + 10, 24)