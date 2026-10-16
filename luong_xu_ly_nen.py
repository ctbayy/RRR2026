from PySide6.QtCore import QThread, Signal

class LuongXuLy(QThread):
    ket_qua_tra_ve = Signal(object)
    bao_loi = Signal(str)

    def __init__(self, ham_thuc_thi, *args, **kwargs):
        super().__init__()
        self.ham_thuc_thi = ham_thuc_thi
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            # Thực thi hàm nặng (ví dụ: đọc XML, ghi Excel)
            ket_qua = self.ham_thuc_thi(*self.args, **self.kwargs)
            self.ket_qua_tra_ve.emit(ket_qua)
        except Exception as e:
            self.bao_loi.emit(str(e))