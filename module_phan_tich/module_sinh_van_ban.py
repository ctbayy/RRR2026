class TrinhSinhVanBan:
    @staticmethod
    def f_so(val):
        """Format số tiền chuẩn Việt Nam"""
        try:
            return "{:,.0f}".format(float(val)).replace(",", ".")
        except:
            return "0"

    @staticmethod
    def nhan_xet_tncn(tnct_qtt, tnct_thang, thue_qtt, thue_thang, tk334, nam):
        text = ""
        # 1. Chênh lệch Thu nhập chịu thuế
        if abs(tnct_qtt - tnct_thang) > 0:
            text += (
                f"+ Tổng thu nhập chịu thuế trả cho cá nhân (chỉ tiêu 23) trên tờ khai QTT TNCN mẫu 05/QTT năm {nam} là {TrinhSinhVanBan.f_so(tnct_qtt)} đồng, "
                f"Tổng thu nhập chịu thuế trả cho cá nhân trên tờ khai khấu trừ thuế TNCN (mẫu 05/KK-TNCN các quý) là {TrinhSinhVanBan.f_so(tnct_thang)} đồng. Đề nghị đơn vị giải trình rõ chênh lệch này.\n")

        # 2. Chênh lệch Thuế đã khấu trừ
        chenh_thue = abs(thue_qtt - thue_thang)
        if chenh_thue > 0:
            text += (
                f"+ Tổng số thuế TNCN đã khấu trừ (chỉ tiêu 31) trên tờ khai QTT TNCN mẫu 05/QTT năm {nam} là {TrinhSinhVanBan.f_so(thue_qtt)} đồng "
                f"có sự chênh lệch với Tổng số thuế TNCN đã khấu trừ (chỉ tiêu 29) trên tờ khai khấu trừ (các quý) là {TrinhSinhVanBan.f_so(thue_thang)} đồng, "
                f"chênh lệch {TrinhSinhVanBan.f_so(chenh_thue)} đồng. Đề nghị đơn vị giải trình rõ chênh lệch này.\n")

        # 3. Chênh lệch TK 334 và Chỉ tiêu 23
        chenh_334 = abs(tk334 - tnct_qtt)
        if chenh_334 > 0 and tk334 > 0:
            text += (
                f"+ Trên bảng cân đối tài khoản kèm theo BCTC năm {nam}, Có TK 334- Phải trả người lao động {TrinhSinhVanBan.f_so(tk334)} đồng "
                f"đối chiếu với Tổng thu nhập chịu thuế trả cho cá nhân (chỉ tiêu 23) trên QTT TNCN năm {nam} {TrinhSinhVanBan.f_so(tnct_qtt)} đồng, "
                f"chênh lệch {TrinhSinhVanBan.f_so(chenh_334)} đồng. Đề nghị đơn vị giải trình rõ chênh lệch này.\n")

        return text.strip() if text else "Qua rà soát, Tổ kiểm tra chưa phát hiện rủi ro về thuế TNCN."

    @staticmethod
    def nhan_xet_tndn_va_bctc(dt_hddt, dt_qtt, tk111, tk3411, tk411_dau, tk411_cuoi, cp_lai_vay, tk131, tk511, tk3331,
                              tk1331, thue_gtgt_vao, tk1388, nam):
        text = ""
        # 1. Thuế TNDN (HĐĐT vs QTT)
        chenh_dt = abs(dt_hddt - dt_qtt)
        if chenh_dt > 0:
            text += (
                f"Tổng doanh thu của HHDV bán ra trên dữ liệu HĐĐT là {TrinhSinhVanBan.f_so(dt_hddt)} đồng đối chiếu với "
                f"Tổng Doanh thu bán hàng hóa và cung cấp dịch vụ và Thu nhập khác trên phụ lục 03-1A/TNDN kèm theo Tờ khai QTT TNDN "
                f"là {TrinhSinhVanBan.f_so(dt_qtt)} đồng, chênh lệch {TrinhSinhVanBan.f_so(chenh_dt)} đồng. Đề nghị đơn vị giải trình rõ chênh lệch này.\n")

        # 2. Báo cáo tài chính
        text += f"Trên bảng cân đối tài khoản kèm theo Báo cáo tài chính năm {nam}:\n"

        if tk111 > 1000000000 and cp_lai_vay > 0:  # Đặt ngưỡng tiền mặt dư lớn
            text += (f"+ Tài khoản 111- Tiền mặt có số dư Nợ cuối kỳ {TrinhSinhVanBan.f_so(tk111)} đồng. "
                     f"Tài khoản 3411- Các khoản đi vay có số dư Nợ cuối kỳ {TrinhSinhVanBan.f_so(tk3411)} đồng. "
                     f"Đề nghị đơn vị giải trình lý do tiền mặt tồn quỹ lớn nhưng vẫn phát sinh chi phí lãi vay trong kỳ.\n")

        if cp_lai_vay > 0 and tk411_dau != tk411_cuoi:
            text += (
                f"+ Tài khoản 411- Vốn đầu tư của chủ sở hữu có số dư Có đầu kỳ {TrinhSinhVanBan.f_so(tk411_dau)} đồng, "
                f"số dư Có cuối kỳ {TrinhSinhVanBan.f_so(tk411_cuoi)} đồng; trên phụ lục Kết quả SXKD kèm BCTC mã số 23- Chi phí lãi vay "
                f"có {TrinhSinhVanBan.f_so(cp_lai_vay)} đồng. Đề nghị giải trình việc xác định chi phí lãi vay được trừ đối với phần vốn điều lệ đăng ký còn thiếu.\n")

        chenh_doanh_thu_thue = abs(tk131 - (tk511 + tk3331))
        if chenh_doanh_thu_thue > 0:
            text += (
                f"+ Số phát sinh Nợ TK 131- Phải thu của khách hàng {TrinhSinhVanBan.f_so(tk131)} đồng. Đối chiếu với số phát sinh Có TK 511 "
                f"({TrinhSinhVanBan.f_so(tk511)} đồng) + Phát sinh Có TK 3331 ({TrinhSinhVanBan.f_so(tk3331)} đồng) là {TrinhSinhVanBan.f_so(tk511 + tk3331)} đồng, "
                f"chênh lệch {TrinhSinhVanBan.f_so(chenh_doanh_thu_thue)} đồng. Đề nghị đơn vị giải trình.\n")

        chenh_gtgt_vao = abs(tk1331 - thue_gtgt_vao)
        if chenh_gtgt_vao > 0:
            text += (
                f"+ Số phát sinh Nợ tài khoản 1331- Thuế GTGT được khấu trừ là {TrinhSinhVanBan.f_so(tk1331)} đồng đối chiếu với "
                f"Thuế GTGT của HHDV mua vào được khấu trừ năm {nam} trên tờ khai Thuế GTGT là {TrinhSinhVanBan.f_so(thue_gtgt_vao)} đồng, "
                f"chênh lệch {TrinhSinhVanBan.f_so(chenh_gtgt_vao)} đồng. Đề nghị đơn vị giải trình.\n")

        if tk1388 > 0:
            text += (
                f"+ Số phát sinh Nợ TK 1388- Phải thu khác là {TrinhSinhVanBan.f_so(tk1388)} đồng, đề nghị đơn vị giải trình chi tiết "
                f"khoản phải thu khác này có phải là giao dịch hàng hóa/dịch vụ không.\n")

        return text.strip()