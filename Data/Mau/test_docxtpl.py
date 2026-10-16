from docxtpl import DocxTemplate
import os


class TrinhSinhVanBanTest:
    @staticmethod
    def f_so(val):
        """Hàm format số hiển thị đẹp"""
        try:
            return "{:,.0f}".format(float(val)).replace(",", ".")
        except:
            return str(val)

    @staticmethod
    def xu_ly_nhan_xet_dong(danh_sach_rui_ro):
        """
        Đây là cách xử lý hàng trăm tài khoản không cần 100 lệnh if/else.
        Nó sẽ tự động duyệt qua List lỗi (có thể lấy từ Engine Phân tích của mày).
        """
        if not danh_sach_rui_ro:
            return "Qua rà soát, Tổ kiểm tra chưa phát hiện rủi ro bất thường."

        text_ket_qua = ""
        for loi in danh_sach_rui_ro:
            tk = loi.get('tai_khoan', 'Khác')
            du_lieu = TrinhSinhVanBanTest.f_so(loi.get('so_lieu', 0))
            ly_do = loi.get('van_de', '')
            kien_nghi = loi.get('kien_nghi', 'Đề nghị đơn vị giải trình.')

            # Form câu văn chuẩn:
            text_ket_qua += f"+ Trên BCTC, {tk} có số liệu là {du_lieu} đồng. {ly_do} {kien_nghi}\n\n"

        return text_ket_qua.strip()


def test_xuat_phieu():
    # 1. DỮ LIỆU ĐỘNG: Giả lập kết quả từ Engine phân tích của mày
    du_lieu_nnt = {
        "ten_nnt": "CÔNG TY TNHH QUẢNG CÁO THỜI NAY",
        "mst": "4300308931"
    }

    # Bảng GTGT: Dù là 1 dòng hay 12 tháng, Word tự đẻ thêm dòng bảng khớp 100%
    danh_sach_gtgt = [
        {"stt": 1, "ky": "Quý 1/2025", "hd": "273.926.729", "tk": "353.293.172", "chenh": "79.366.443"},
        {"stt": 2, "ky": "Quý 2/2025", "hd": "239.885.710", "tk": "239.973.710", "chenh": "88.000"}
    ]

    # Danh sách lỗi: Không cần if/else cứng. Mày ném vào 50 lỗi, nó gen ra 50 gạch đầu dòng.
    danh_sach_loi_bctc = [
        {
            "tai_khoan": "Tài khoản 111 (Tiền mặt)",
            "so_lieu": 13591322024,
            "van_de": "Tồn quỹ quá lớn nhưng vẫn phát sinh chi phí lãi vay (TK 635 là 50.989.731 đ).",
            "kien_nghi": "Đề nghị giải trình lý do vay vốn khi tiền mặt còn nhiều."
        },
        {
            "tai_khoan": "Tài khoản 334 (Phải trả NLĐ)",
            "so_lieu": 1609913875,
            "van_de": "Không khớp với Chỉ tiêu 23 trên Tờ khai QTT TNCN (3.796.470.000 đ).",
            "kien_nghi": "Đề nghị đơn vị giải trình rõ chênh lệch này."
        },
        {
            "tai_khoan": "Tài khoản 131 (Phải thu KH)",
            "so_lieu": 15556295182,
            "van_de": "Đang lệch so với tổng Doanh thu và Thuế (TK 511 + TK 3331).",
            "kien_nghi": "Đề nghị cung cấp sổ chi tiết công nợ."
        }
    ]

    # 2. XỬ LÝ SINH CHỮ
    text_rui_ro = TrinhSinhVanBanTest.xu_ly_nhan_xet_dong(danh_sach_loi_bctc)

    # 3. GÓP VÀO DICTIONARY (CONTEXT)
    context = {
        "ten_nnt": du_lieu_nnt["ten_nnt"],
        "mst": du_lieu_nnt["mst"],
        "bang_gtgt": danh_sach_gtgt,  # Truyền thẳng cả cái list vào cho Word tự lo
        "nhan_xet_dong": text_rui_ro
    }

    # 4. RENDER RA FILE WORD (Phép thuật nằm ở đây)
    duong_dan_mau = "Mau_Test.docx"
    doc = DocxTemplate(duong_dan_mau)
    doc.render(context)

    file_xuat = "Ket_Qua_Test.docx"
    doc.save(file_xuat)
    print(f"Đã xuất thành công file: {file_xuat}! Hãy mở lên xem cái bảng.")


if __name__ == "__main__":
    test_xuat_phieu()