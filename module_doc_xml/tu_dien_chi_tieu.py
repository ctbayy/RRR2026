# Bộ từ điển ánh xạ mã chỉ tiêu sang nội dung diễn giải dựa trên XSLT
MAP_TEN_TO_KHAI = {
    "01": "01/GTGT",      # Bổ sung mã tờ khai 01/GTGT
    "842": "01/GTGT",
    "844": "02/GTGT",
    "02": "02/GTGT",    # Bổ sung mã tờ khai 02/GTGT mẫu cũ (TT26)
    "847": "04/GTGT",
    "892": "03/TNDN",
    "03": "03/TNDN",   # Mẫu cũ TT151
    "402": "BCTC_TT200",# Bổ sung tờ khai Quyết toán TNDN
    "683": "BCTC_TT133",
    "953": "05/QTT-TNCN",
    "864": "05/KK-TNCN",
    "832": "01/TAIN",     # Tờ khai thuế tài nguyên (TT80)[cite: 28]
    "924": "02/TAIN",
    "833": "04/TNDN"

}

TU_DIEN_TO_KHAI = {
    "01/GTGT": {
        "ct21": "Không phát sinh hoạt động mua, bán trong kỳ",  # [cite: 2]
        "ct22": "Thuế giá trị gia tăng còn được khấu trừ kỳ trước chuyển sang",  # [cite: 2]
        "ct23": "Giá trị của hàng hóa, dịch vụ mua vào",  # [cite: 2]
        "ct24": "Thuế giá trị gia tăng của hàng hóa, dịch vụ mua vào",  # [cite: 2]
        "ct23a": "Giá trị hàng hóa, dịch vụ nhập khẩu",  # [cite: 2]
        "ct24a": "Thuế giá trị gia tăng hàng hóa, dịch vụ nhập khẩu",  # [cite: 2]
        "ct25": "Thuế giá trị gia tăng của hàng hóa, dịch vụ mua vào được khấu trừ kỳ này",  # [cite: 2]
        "ct26": "Hàng hóa, dịch vụ bán ra không chịu thuế giá trị gia tăng",  # [cite: 2]
        "ct27": "Giá trị hàng hóa, dịch vụ bán ra chịu thuế giá trị gia tăng",  # [cite: 2]
        "ct28": "Thuế giá trị gia tăng của hàng hóa, dịch vụ bán ra chịu thuế",  # [cite: 2]
        "ct29": "Hàng hoá, dịch vụ bán ra chịu thuế suất 0%",  # [cite: 2]
        "ct30": "Giá trị hàng hoá, dịch vụ bán ra chịu thuế suất 5%",  # [cite: 2]
        "ct31": "Thuế giá trị gia tăng hàng hoá, dịch vụ bán ra chịu thuế suất 5%",  # [cite: 2]
        "ct32": "Giá trị hàng hoá, dịch vụ bán ra chịu thuế suất 10%",  # [cite: 2]
        "ct33": "Thuế giá trị gia tăng hàng hoá, dịch vụ bán ra chịu thuế suất 10%",  # [cite: 2]
        "ct32a": "Hàng hoá, dịch vụ bán ra không tính thuế",  # [cite: 2]
        "ct34": "Tổng doanh thu của hàng hóa, dịch vụ bán ra",  # [cite: 2]
        "ct35": "Tổng thuế giá trị gia tăng của hàng hóa, dịch vụ bán ra",  # [cite: 2]
        "ct36": "Thuế giá trị gia tăng phát sinh trong kỳ",  # [cite: 2]
        "ct37": "Điều chỉnh giảm thuế GTGT còn được khấu trừ của các kỳ trước",  # [cite: 2]
        "ct38": "Điều chỉnh tăng thuế GTGT còn được khấu trừ của các kỳ trước",  # [cite: 2]
        "ct39": "Thuế GTGT đã nộp ở địa phương khác của hoạt động kinh doanh xây dựng, lắp đặt, bán bất động sản ngoại tỉnh",
        "ct39a": "Thuế giá trị gia tăng nhận bàn giao được khấu trừ trong kỳ",  # [cite: 2]
        "ct40a": "Thuế giá trị gia tăng phải nộp của hoạt động sản xuất kinh doanh trong kỳ",  # [cite: 2]
        "ct40b": "Thuế giá trị gia tăng mua vào của dự án đầu tư được bù trừ với thuế GTGT còn phải nộp",  # [cite: 2]
        "ct40": "Thuế giá trị gia tăng còn phải nộp trong kỳ",  # [cite: 2]
        "ct41": "Thuế giá trị gia tăng chưa khấu trừ hết kỳ này",  # [cite: 2]
        "ct42": "Thuế giá trị gia tăng đề nghị hoàn",  # [cite: 2]
        "ct43": "Thuế giá trị gia tăng còn được khấu trừ chuyển kỳ sau"  # [cite: 2]
    },

    "02/GTGT": {
        "ct21": "Thuế giá trị gia tăng chưa được hoàn kỳ trước chuyển sang",  # [cite: 3]
        "ct21a": "Thuế giá trị gia tăng đầu vào của dự án đầu tư nhận bàn giao",  # [cite: 3]
        "ct22": "Giá trị hàng hoá, dịch vụ mua vào trong kỳ",  # [cite: 3]
        "ct23": "Thuế giá trị gia tăng hàng hoá, dịch vụ mua vào trong kỳ",  # [cite: 3]
        "ct22a": "Giá trị hàng hóa, dịch vụ nhập khẩu",  # [cite: 3]
        "ct23a": "Thuế giá trị gia tăng hàng hóa, dịch vụ nhập khẩu",  # [cite: 3]
        "ct24": "Điều chỉnh tăng giá trị hàng hóa, dịch vụ mua vào các kỳ trước",  # [cite: 3]
        "ct25": "Điều chỉnh tăng thuế GTGT của hàng hóa, dịch vụ mua vào các kỳ trước",  # [cite: 3]
        "ct26": "Điều chỉnh giảm giá trị hàng hóa, dịch vụ mua vào các kỳ trước",  # [cite: 3]
        "ct27": "Điều chỉnh giảm thuế GTGT của hàng hóa, dịch vụ mua vào các kỳ trước",  # [cite: 3]
        "ct28": "Tổng số thuế giá trị gia tăng đầu vào của hàng hóa, dịch vụ mua vào",  # [cite: 3]
        "ct28a": "Thuế GTGT mua vào của dự án đầu tư bù trừ với thuế GTGT phải nộp của HĐSXKD cùng kỳ",  # [cite: 3]
        "ct28b": "Thuế GTGT mua vào của DAĐT bù trừ với thuế GTGT phải nộp của HĐSXKD cùng kỳ của chủ đầu tư",
        # [cite: 3]
        "ct29": "Thuế giá trị gia tăng đầu vào chưa được hoàn đến kỳ tính thuế của dự án đầu tư",  # [cite: 3]
        "ct30": "Thuế giá trị gia tăng đề nghị hoàn",  # [cite: 3]
        "ct30a": "Thuế GTGT đầu vào của dự án đầu tư nhận bàn giao", # BỔ SUNG CHỈ TIÊU NÀY CHO MẪU CŨ
        "ct31": "Thuế giá trị gia tăng đầu vào của dự án đầu tư chưa được hoàn bàn giao trong kỳ",  # [cite: 3]
        "ct32": "Thuế giá trị gia tăng đầu vào của dự án đầu tư chưa được hoàn chuyển kỳ sau"  # [cite: 3]
    },

    "04/GTGT": {
        "ct21": "Doanh thu hàng hoá, dịch vụ chịu thuế suất 0% và không chịu thuế",  # [cite: 4]
        "ct22": "Doanh thu chịu thuế - Phân phối, cung cấp hàng hoá",  # [cite: 4]
        "ct23": "Thuế GTGT phải nộp - Phân phối, cung cấp hàng hoá",  # [cite: 4]
        "ct24": "Doanh thu chịu thuế - Dịch vụ, xây dựng không bao thầu nguyên vật liệu",  # [cite: 4]
        "ct25": "Thuế GTGT phải nộp - Dịch vụ, xây dựng không bao thầu nguyên vật liệu",  # [cite: 4]
        "ct26": "Doanh thu chịu thuế - Sản xuất, vận tải, dịch vụ có gắn với hàng hoá, xây dựng có bao thầu",
        # [cite: 4]
        "ct27": "Thuế GTGT phải nộp - Sản xuất, vận tải, dịch vụ có gắn với hàng hoá, xây dựng có bao thầu",
        # [cite: 4]
        "ct28": "Doanh thu chịu thuế - Hoạt động kinh doanh khác",  # [cite: 4]
        "ct29": "Thuế GTGT phải nộp - Hoạt động kinh doanh khác",  # [cite: 4]
        "ct30": "Tổng doanh thu chịu thuế giá trị gia tăng",  # [cite: 4]
        "ct31": "Tổng số thuế giá trị gia tăng phải nộp",  # [cite: 4]
        "ct32": "Tổng doanh thu",  # [cite: 4]
        "ct33": "Doanh thu chưa có thuế GTGT (Khai riêng khoản thu hộ)",  # [cite: 4]
        "ct34": "Thuế suất (Khai riêng khoản thu hộ)",  # [cite: 4]
        "ct35": "Thuế GTGT phải nộp (Khai riêng khoản thu hộ)",  # [cite: 4]
        "ct36": "Tổng Doanh thu (Khai riêng khoản thu hộ)",  # [cite: 4]
        "ct37": "Tổng số thuế phải nộp (Khai riêng khoản thu hộ)"  # [cite: 4]
    }
}
TU_DIEN_TO_KHAI["03/TNDN"] = {
    "ToKhaiChinh": {
        # --- BỔ SUNG CÁC CHỈ TIÊU HEADER VÀ CHI TIẾT MỚI (TT80) ---
        "ct04_ten": "[04] Ngành nghề có tỷ lệ doanh thu cao nhất",
        "ct05": "[05] Tỷ lệ (%)",
        "ctC2_soThuNhap": "Chi tiết số thu nhập miễn thuế",
        "ctC7_thuNhap": "Thu nhập tính thuế theo chi tiết mức thuế suất",
        "ctC7_tenThueSuat": "Tên mức thuế suất áp dụng",
        "ctC7_thueSuat": "Mức thuế suất (%)",
        "thueTNDN_tamnop_sxkd": "Thuế TNDN đã tạm nộp của HĐ SXKD",
        "thueTNDN_tamnop_cnbds": "Thuế TNDN đã tạm nộp của HĐ chuyển nhượng BĐS",
        "soKK": "Số tiền kê khai",
        "tieuMuc1052": "Tiểu mục 1052 (Thuế TNDN của các đơn vị không hạch toán toàn ngành)",
        "tieuMuc1053": "Tiểu mục 1053 (Thuế TNDN từ chuyển nhượng BĐS)",
        "tieuMuc1056": "Tiểu mục 1056 (Thuế TNDN từ hoạt động xổ số kiến thiết)",
        "tieuMuc1057": "Tiểu mục 1057 (Thuế TNDN từ hoạt động dầu khí)",
        "tieuMuc1099": "Tiểu mục 1099 (Thuế TNDN khác)",
        "tong1052": "Tổng tiền Tiểu mục 1052",
        "tong1053": "Tổng tiền Tiểu mục 1053",
        "tong1056": "Tổng tiền Tiểu mục 1056",
        "tong1057": "Tổng tiền Tiểu mục 1057",

        # --- CÁC CHỈ TIÊU GỐC ---
        "ctA1": "A1. Tổng lợi nhuận kế toán trước thuế thu nhập doanh nghiệp",
        "ctB1": "B1. Điều chỉnh tăng tổng lợi nhuận trước thuế TNDN",
        "ctB2": "B2. Các khoản điều chỉnh tăng doanh thu",
        "ctB3": "B3. Chi phí của phần doanh thu điều chỉnh giảm",
        "ctB4": "B4. Các khoản chi không được trừ khi xác định thu nhập chịu thuế",
        "ctB5": "B5. Thuế thu nhập đã nộp cho phần thu nhập nhận được ở nước ngoài",
        "ctB6": "B6. Điều chỉnh tăng lợi nhuận do xác định giá thị trường đối với giao dịch liên kết",
        "ctB7": "B7. Các khoản điều chỉnh làm tăng lợi nhuận trước thuế khác",
        "ctB8": "B8. Điều chỉnh giảm tổng lợi nhuận trước thuế TNDN",
        "ctB9": "B9. Giảm trừ các khoản doanh thu đã tính thuế năm trước",
        "ctB10": "B10. Chi phí của phần doanh thu điều chỉnh tăng",
        "ctB11": "B11. Chi phí lãi vay không được trừ kỳ trước được chuyển sang kỳ này",
        "ctB12": "B12. Các khoản điều chỉnh làm giảm lợi nhuận trước thuế khác",
        "ctB13": "B13. Tổng thu nhập chịu thuế",
        "ctB14": "B14. Thu nhập chịu thuế từ hoạt động sản xuất kinh doanh",
        "ctB15": "B15. Thu nhập chịu thuế từ hoạt động chuyển nhượng BĐS",
        "ctC1": "C1. Thu nhập chịu thuế",
        "ctC2": "C2. Thu nhập miễn thuế",
        "ctC3": "C3. Chuyển lỗ và bù trừ lãi, lỗ",
        "ctC3a": "C3a. Lỗ từ hoạt động SXKD được chuyển trong kỳ",
        "ctC3b": "C3b. Lỗ từ chuyển nhượng BĐS được bù trừ với lãi SXKD",
        "ctC4": "C4. Thu nhập tính thuế",
        "ctC5": "C5. Trích lập quỹ khoa học công nghệ",
        "ctC6": "C6. Thu nhập tính thuế sau khi trích lập quỹ khoa học công nghệ",
        "ctC7": "C7. Thu nhập tính thuế áp dụng thuế suất ưu đãi",
        "ctC8": "C8. Thu nhập tính thuế theo thuế suất không ưu đãi khác",
        "ctC8a": "C8a. Thuế suất không ưu đãi khác (%)",
        "ctC9": "C9. Thuế TNDN từ hoạt động SXKD tính theo thuế suất không ưu đãi",
        "ctC9a": "C9a. Thuế suất 20%",
        "ctC10": "C10. Thuế TNDN được ưu đãi",
        "ctC11": "C11. Thuế TNDN chênh lệch do áp dụng mức thuế suất ưu đãi",
        "ctC12": "C12. Thuế TNDN được miễn trong kỳ",
        "ctC13": "C13. Thuế TNDN được giảm trong kỳ",
        "ctC14": "C14. Thuế TNDN được miễn, giảm theo Hiệp định thuế",
        "ctC15": "C15. Thuế TNDN được miễn, giảm theo từng thời kỳ",
        "ctC16": "C16. Thuế thu nhập đã nộp ở nước ngoài được trừ",
        "ctC17": "C17. Thuế TNDN phải nộp của hoạt động sản xuất kinh doanh",
        "ctD": "D. TỔNG SỐ THUẾ TNDN PHẢI NỘP",
        "ctD1": "D1. Thu nhập chịu thuế BĐS",
        "ctD2": "D2. Lỗ từ hoạt động chuyển nhượng BĐS được chuyển trong kỳ",
        "ctD3": "D3. Thu nhập tính thuế BĐS",
        "ctD4": "D4. Trích lập quỹ khoa học công nghệ (BĐS)",
        "ctD5": "D5. TNTT sau khi đã trích lập quỹ khoa học công nghệ (BĐS)",
        "ctD6": "D6. Thuế TNDN phải nộp của hoạt động chuyển nhượng BĐS trong kỳ",
        "ctD7": "D7. Thuế TNDN chênh lệch do áp dụng ưu đãi BĐS",
        "ctD8": "D8. Thuế TNDN của hoạt động chuyển nhượng BĐS còn phải nộp",
        "ctE": "E. Số thuế TNDN phải nộp quyết toán trong kỳ",
        "ctE1": "E1. Thuế TNDN của hoạt động sản xuất kinh doanh",
        "ctE2": "E2. Thuế TNDN từ hoạt động chuyển nhượng bất động sản",
        "ctE3": "E3. Thuế TNDN từ hoạt động chuyển nhượng bất động sản (khác)",
        "ctE4": "E4. Thuế TNDN chuyển nhượng cơ sở hạ tầng có thu tiền theo tiến độ",
        "ctE5": "E5. Thuế TNDN phải nộp khác",
        "ctE6": "E6. Thuế TNDN từ xử lý Quỹ phát triển khoa học công nghệ",
        "ctG": "G. Số thuế TNDN đã tạm nộp",
        "ctG1": "G1. Thuế TNDN nộp thừa kỳ trước chuyển sang kỳ này",
        "ctG2": "G2. Thuế TNDN đã tạm nộp trong năm",
        "ctG3": "G3. Thuế TNDN nộp thừa BĐS kỳ trước chuyển sang",
        "ctG4": "G4. Thuế TNDN BĐS đã tạm nộp trong năm",
        "ctG5": "G5. Thuế TNDN đã tạm nộp CSHT thu tiền theo tiến độ",
        "ctH": "H. Chênh lệch giữa số thuế phải nộp và số thuế đã tạm nộp",
        "ctH1": "H1. Chênh lệch giữa thuế phải nộp và tạm nộp trong năm SXKD",
        "ctH2": "H2. Chênh lệch giữa thuế phải nộp và tạm nộp BĐS",
        "ctH3": "H3. Chênh lệch giữa thuế phải nộp và tạm nộp CSHT",
        "ctI": "I. Số thuế TNDN còn phải nộp",
        "ctI1": "I1. Thuế TNDN còn phải nộp của hoạt động sản xuất kinh doanh",
        "ctI2": "I2. Thuế TNDN còn phải nộp của hoạt động chuyển nhượng BĐS"
    },

    "PL 03-1A": {
        "ct04": "[04] Doanh thu bán hàng và cung cấp dịch vụ",
        "ct05": "[05] Doanh thu bán hàng hoá, dịch vụ xuất khẩu",
        "ct06": "[06] Các khoản giảm trừ doanh thu",
        "ct07": "[07] Chiết khấu thương mại",
        "ct08": "[08] Giảm giá hàng bán",
        "ct09": "[09] Giá trị hàng bán bị trả lại",
        "ct10": "[10] Doanh thu hoạt động tài chính",
        "ct11": "[11] Trong đó: Doanh thu từ lãi tiền gửi",
        "ct12": "[12] Chi phí sản xuất, kinh doanh hàng hoá, dịch vụ",
        "ct13": "[13] Giá vốn hàng bán",
        "ct14": "[14] Chi phí bán hàng",
        "ct15": "[15] Chi phí quản lý doanh nghiệp",
        "ct16": "[16] Chi phí tài chính",
        "ct17": "[17] Trong đó: Chi phí lãi tiền vay",
        "ct18": "[18] Lợi nhuận thuần từ hoạt động kinh doanh",
        "ct19": "[19] Thu nhập khác",
        "ct20": "[20] Chi phí khác",
        "ct21": "[21] Lợi nhuận khác",
        "ct22": "[22] Tổng lợi nhuận kế toán trước thuế thu nhập doanh nghiệp"
    },

    "PL 03-1B": {
        "ct04": "Thu nhập lãi và các khoản thu nhập tương tự",
        "ct05": "Chi phí lãi và các chi phí tương tự",
        "ct06": "Thu nhập lãi thuần",
        "ct07": "Thu nhập từ hoạt động dịch vụ",
        "ct08": "Chi phí hoạt động dịch vụ",
        "ct09": "Lãi / lỗ thuần từ hoạt động dịch vụ",
        "ct10": "Lãi / lỗ thuần từ hoạt động kinh doanh ngoại hối",
        "ct11": "Lãi / lỗ thuần từ mua bán chứng khoán kinh doanh",
        "ct12": "Lãi / lỗ thuần từ mua bán chứng khoán đầu tư",
        "ct13": "Thu nhập từ hoạt động khác",
        "ct14": "Chi phí hoạt động khác",
        "ct15": "Lãi / lỗ thuần từ hoạt động khác",
        "ct16": "Thu nhập từ góp vốn, mua cổ phần",
        "ct17": "Chi phí hoạt động",
        "ct18": "Chi phí dự phòng rủi ro tín dụng",
        "ct19": "Tổng lợi nhuận trước thuế"
    },

    "PL 03-1C": {
        "ct_1": "Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)",
        "ct_01_1": "Lãi bán các tài sản tài chính FVTPL",
        "ct_01_2": "Chênh lệch tăng về đánh giá lại các TSTC FVTPL",
        "ct_01_3": "Cổ tức, tiền lãi phát sinh từ tài sản tài chính FVTPL",
        "ct_2": "Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)",
        "ct_3": "Lãi từ các khoản cho vay và phải thu",
        "ct_4": "Lãi từ tài sản tài chính sẵn sàng để bán (AFS)",
        "ct_5": "Lãi từ các công cụ phái sinh phòng ngừa rủi ro",
        "ct_6": "Doanh thu nghiệp vụ môi giới chứng khoán",
        "ct_7": "Doanh thu nghiệp vụ bảo lãnh, đại lý phát hành chứng khoán",
        "ct_8": "Doanh thu nghiệp vụ tư vấn đầu tư chứng khoán",
        "ct_9": "Doanh thu nghiệp vụ lưu ký chứng khoán",
        "ct_10": "Doanh thu hoạt động tư vấn tài chính",
        "ct_11": "Thu nhập hoạt động khác",
        "ct_20": "Cộng doanh thu hoạt động",
        "ct_21": "Lỗ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)",
        "ct_21_1": "Lỗ bán các tài sản tài chính FVTPL",
        "ct_21_2": "Chênh lệch giảm đánh giá lại các TSTC FVTPL",
        "ct_21_3": "Chi phí giao dịch mua các tài sản tài chính FVTPL",
        "ct_22": "Lỗ các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)",
        "ct_23": "Lỗ và ghi nhận chênh lệch đánh giá theo giá trị hợp lý (AFS)",
        "ct_24": "Chi phí dự phòng tài sản tài chính...",
        "ct_25": "Lỗ từ các tài sản tài chính phái sinh phòng ngừa rủi ro",
        "ct_26": "Chi phí hoạt động tự doanh",
        "ct_27": "Chi phí nghiệp vụ môi giới chứng khoán",
        "ct_28": "Chi phí nghiệp vụ bảo lãnh, đại lý phát hành chứng khoán",
        "ct_29": "Chi phí nghiệp vụ tư vấn đầu tư chứng khoán",
        "ct_30": "Chi phí nghiệp vụ lưu ký chứng khoán",
        "ct_31": "Chi phí hoạt động tư vấn tài chính",
        "ct_32": "Chi phí các dịch vụ khác",
        "ct_40": "Cộng chi phí hoạt động",
        "ct_41": "Chênh lệch lãi tỷ giá hối đoái đã và chưa thực hiện",
        "ct_42": "Doanh thu, dự thu cổ tức, lãi tiền gửi ngân hàng",
        "ct_43": "Lãi bán, thanh lý các khoản đầu tư",
        "ct_44": "Doanh thu khác về đầu tư",
        "ct_50": "Cộng doanh thu hoạt động tài chính",
        "ct_51": "Chênh lệch lỗ tỷ giá hối đoái đã và chưa thực hiện",
        "ct_52": "Chi phí lãi vay",
        "ct_53": "Lỗ bán, thanh lý các khoản đầu tư",
        "ct_54": "Chi phí dự phòng suy giảm giá trị các khoản đầu tư",
        "ct_55": "Chi phí tài chính khác",
        "ct_60": "Cộng chi phí tài chính",
        "ct_61": "Chi phí bán hàng",
        "ct_62": "Chi phí quản lý công ty",
        "ct_70": "Kết quả hoạt động",
        "ct_71": "Thu nhập khác",
        "ct_72": "Chi phí khác",
        "ct_80": "Cộng kết quả hoạt động khác",
        "ct_90": "Tổng lợi nhuận kế toán trước thuế"
    },

    "PL 03-2": {
        "ct2": "Năm phát sinh lỗ",
        "ct3": "Số lỗ phát sinh",
        "ct4": "Số lỗ đã chuyển trong các kỳ tính thuế trước",
        "ct5": "Số lỗ được chuyển trong kỳ tính thuế này",
        "ct6": "Số lỗ còn được chuyển sang các kỳ tính thuế sau"
    },

    # Gom chung các PL 03-3A, 03-3B, 03-3C, 03-3D vì chúng dùng chung một bộ khung thẻ chỉ tiêu về Ưu đãi
    "PL_UU_DAI": {
        # --- BỔ SUNG THẺ NHẬN DIỆN MỚI CHO PL ƯU ĐÃI ---
        "uuDai_ten": "Trường hợp ưu đãi",
        "ct09a_ten": "Địa phương phụ thuộc - Xã phường",
        "ct09b_ten": "Địa phương phụ thuộc - Quận huyện",
        "ct09c_ten": "Địa phương phụ thuộc - Tỉnh Thành phố",
        "ct10_ten": "Cơ quan thuế quản lý cơ sở ưu đãi",
        "dn_sdld_nu": "Doanh nghiệp sử dụng nhiều lao động nữ",
        "giam_TNDN_ldNu": "Số thuế TNDN được giảm do sử dụng LĐ nữ",
        "dn_sdld_dtoc": "Doanh nghiệp sử dụng LĐ người dân tộc thiểu số",
        "giam_TNDN_ldDToc": "Số thuế TNDN được giảm do sử dụng LĐ dân tộc thiểu số",
        "dn_chuyenGiao": "Doanh nghiệp thực hiện chuyển giao công nghệ",
        "dn_khoaHocCN": "Doanh nghiệp khoa học và công nghệ",

        # --- CÁC THẺ CHI TIẾT GỐC ---
        "ct2": "Tên NNT, đơn vị phụ thuộc, địa điểm kinh doanh / Năm phát sinh lỗ",
        "ct3": "Mã số thuế NNT, đơn vị phụ thuộc / Số lỗ phát sinh",
        "ct4_ten": "Cơ quan thuế quản lý NNT, đơn vị phụ thuộc",
        "ct5_ten": "Tiêu chí đáp ứng dự án đầu tư mở rộng",
        "ct6": "Lĩnh vực hoạt động",
        "ct7": "Số năm ưu đãi thuế suất",
        "ct8_ten": "Từ năm ưu đãi thuế suất",
        "ct9": "Số năm miễn giảm thuế",
        "ct9_ten": "Từ năm miễn giảm thuế",
        "ct10": "Doanh thu tính thuế / Doanh thu chuyển giao công nghệ",
        "ct11": "Chi phí tính thuế / Chi phí chuyển giao công nghệ",
        "ct12": "Thu nhập miễn thuế / Thu nhập tính thuế TNDN",
        "ct13": "Chuyển lỗ và bù trừ lãi, lỗ / Tỷ lệ giảm thuế",
        "ct14": "Thu nhập tính thuế được hưởng ưu đãi / Số thuế TNDN được giảm",
        "ct15": "Thuế suất ưu đãi (%) / Doanh thu từ việc sản xuất sản phẩm khoa học công nghệ",
        "ct16": "Thuế TNDN phải nộp theo thuế suất phổ thông / Tổng doanh thu",
        "ct17": "Số thuế TNDN tính theo thuế suất ưu đãi / Tỷ lệ doanh thu xét ưu đãi",
        "ct18": "Số thuế chênh lệch do áp dụng thuế suất ưu đãi / Năm bắt đầu có thu nhập chịu thuế",
        "ct19": "Tỷ lệ giảm thuế (%) / Tổng chi cho LĐ dân tộc thiểu số",
        "ct20": "Số thuế được miễn / Thuế TNDN được giảm (LĐ dân tộc)",
        "ct21": "Số thuế được giảm / Thuế TNDN phải nộp của hoạt động được ưu đãi",
        "ct22": "Tổng số thuế được ưu đãi / Thuế TNDN nộp thừa kỳ trước",
        "ct23": "Thuế TNDN phải nộp của hoạt động được ưu đãi / Thuế tạm nộp trong năm",
        "ct24": "Thuế TNDN nộp thừa kỳ trước chuyển sang / Chênh lệch thuế",
        "ct25": "Thuế TNDN đã tạm nộp trong năm / Thuế TNDN còn phải nộp",
        "ct26": "Chênh lệch giữa số thuế phải nộp và số thuế đã tạm nộp",
        "ct27": "Thuế TNDN còn phải nộp (Hoạt động ưu đãi)"
    },

    "PL 03-4": {
        "ct2a": "Tên và địa chỉ của Người nộp thuế khấu trừ thuế ở nước ngoài",
        "ct2b": "Địa chỉ của NNT khấu trừ thuế ở nước ngoài",
        "ct2c_ten": "Quốc gia",
        "ct3": "Thu nhập nhận được ở nước ngoài",
        "ct4": "Thuế thu nhập đã nộp ở nước ngoài",
        "ct5": "Thu nhập chịu thuế theo Luật thuế TNDN",
        "ct6": "Thuế suất thuế TNDN (%)",
        "ct7": "Số thuế phải nộp theo Luật thuế TNDN",
        "ct8": "Số thuế đã nộp ở nước ngoài được trừ"
    },

    "PL 03-5": {
        "ct04": "Doanh thu từ hoạt động chuyển nhượng bất động sản",
        "ct05": "Chi phí từ hoạt động chuyển nhượng bất động sản",
        "ct06": "Giá vốn của đất chuyển nhượng",
        "ct07": "Chi phí đền bù thiệt hại về đất",
        "ct08": "Chi phí đền bù thiệt hại về hoa màu",
        "ct09": "Chi phí cải tạo san lấp mặt bằng",
        "ct10": "Chi phí đầu tư xây dựng kết cấu hạ tầng",
        "ct11": "Chi phí khác",
        "ct12": "Thu nhập từ hoạt động chuyển nhượng bất động sản đã bàn giao",
        "ct13": "Thu nhập từ dự án đầu tư nhà ở xã hội"
    },

    "PL_QUY_KHCN": {
        "ct04": "Mức trích lập (%)",
        "ct05": "Số tiền trích lập",
        "ct2": "Năm trích lập",
        "ct3": "Mức trích lập trong kỳ tính thuế",
        "ct4": "Số tiền trích lập trong kỳ tính thuế",
        "ct5": "Số nhận điều chuyển trong kỳ tính thuế",
        "ct6": "Số điều chuyển trong kỳ tính thuế",
        "ct7": "Số tiền đã sử dụng trong kỳ tính thuế trước / Doanh nghiệp không sử dụng",
        "ct8": "Số tiền đã sử dụng trong kỳ tính thuế này / Nộp về Quỹ KHCN",
        "ct9": "Số tiền được chuyển sang các kỳ tính thuế sau / Quỹ còn lại (sử dụng không hết 70%)",
        "ct10": "Số tiền Quỹ sử dụng không đúng mục đích",
        "ct11": "Thuế suất thuế TNDN",
        "ct12": "Thuế TNDN phải nộp",
        "ct13": "Tiền lãi phải nộp (Sử dụng không hết 70%)",
        "ct14": "Tiền lãi phải nộp (Sử dụng sai mục đích)",
        "ct15": "Tổng số tiền phải nộp"
    },

    "PL 03-8": {
        # --- BỔ SUNG CÁC THẺ MỚI ---
        "ct05a_ten": "Tên cơ quan thuế quản lý nơi đóng trụ sở chính",
        "loai": "Loại phân bổ",

        # --- CÁC THẺ GỐC ---
        "ct04": "Tổng số thuế TNDN phải nộp được phân bổ",
        "ct05": "Tổng chi phí được phân bổ",
        "ct2": "Tên cơ sở sản xuất",
        "ct3": "Mã số thuế / Mã địa điểm kinh doanh",
        "ten_xa": "Xã/phường/đặc khu",
        "ct4_ten": "Huyện",
        "ct5_ten": "Tỉnh",
        "ct6_ten": "Cơ quan thuế quản lý địa bàn nhận phân bổ",
        "ct7": "Chi phí của cơ sở sản xuất",
        "ct8": "Tỷ lệ phân bổ (%)",
        "ct9": "Số thuế TNDN phải nộp",
        "ct10": "Số thuế TNDN nộp thừa kỳ trước chuyển sang kỳ này",
        "ct11": "Số thuế TNDN đã tạm nộp",
        "ct12": "Chênh lệch giữa số thuế phải nộp và số thuế đã tạm nộp trong năm",
        "ct13": "Số thuế TNDN còn phải nộp"
    },

    "PL 03-8A": {
        "loai": "Loại phân bổ",
        "ct04": "Số thuế phải nộp còn lại phân bổ cho Tỉnh nơi đóng trụ sở chính",
        "ct05": "Số thuế TNDN nộp thừa BĐS kỳ trước chuyển sang",
        "ct2": "Tên hoạt động / Đơn vị",
        "ct3": "Mã số thuế / Mã địa điểm kinh doanh (nếu có)",
        "ten_xa": "Xã/phường/đặc khu",
        "ct5_ten": "Tỉnh",
        "ct6_ten": "Cơ quan thuế quản lý địa bàn nhận phân bổ",
        "ct7": "Doanh thu tính thuế theo từng tỉnh",
        "ct8": "Số thuế TNDN phải nộp cho từng tỉnh (Quyết toán)",
        "ct9": "Số thuế đã nộp các kỳ trước cho từng tỉnh",
        "ct10": "Số thuế TNDN đã nộp kỳ này cho từng tỉnh",
        "ct11": "Chênh lệch giữa số thuế phải nộp và số thuế đã tạm nộp",
        "ct12": "Số thuế TNDN còn phải nộp cho từng tỉnh",
        "ct13": "Số tiền thu theo tiến độ theo từng tỉnh",
        "ct14": "Số thuế TNDN phải nộp cho từng tỉnh (Chưa quyết toán)",
        "ct15": "Số thuế TNDN đã nộp cho từng tỉnh (Chưa quyết toán)",
        "ct16": "Số thuế TNDN còn phải nộp cho từng tỉnh (Chưa quyết toán)"
    },

    "PL 03-8B": {
        "loai": "Loại phân bổ",
        "ten_nhaMay": "Tên nhà máy thủy điện",
        "ma_nhaMay": "Mã nhà máy thủy điện",
        "ct10_a": "Số thuế TNDN phải nộp của nhà máy",
        "ct05": "Tên đơn vị phụ thuộc / Địa điểm",
        "ten_xa": "Xã/phường/đặc khu",
        "ct07_ten": "Huyện",
        "ct08_ten": "Tỉnh",
        "ct09_ten": "Cơ quan thuế quản lý địa bàn nhận phân bổ",
        "ct11": "Tỷ lệ phân bổ (%)",
        "ct12": "Số thuế TNDN phải nộp cho từng tỉnh",
        "ct13": "Số thuế TNDN nộp thừa kỳ trước chuyển sang kỳ này",
        "ct14": "Số thuế TNDN đã tạm nộp cho từng tỉnh đến thời điểm khai quyết toán",
        "ct15": "Số thuế TNDN còn phải nộp cho từng tỉnh"
    },

    "PL 03-8C": {
        "loai": "Loại phân bổ",
        "ct04": "Tổng số thuế TNDN phải nộp được phân bổ",
        "ct05": "Tổng doanh thu bán vé thực tế",
        "ct07": "Tên đơn vị",
        "ct08": "Mã số thuế/Mã địa điểm kinh doanh",
        "ten_xa": "Xã/phường/đặc khu",
        "ct10_ten": "Tỉnh",
        "ct11_ten": "Cơ quan thuế quản lý địa bàn nhận phân bổ",
        "ct12": "Doanh thu bán vé thực tế trên địa bàn",
        "ct13": "Tỷ lệ phân bổ (%)",
        "ct14": "Số thuế TNDN phải nộp cả năm theo quyết toán cho từng tỉnh",
        "ct15": "Số thuế TNDN nộp thừa kỳ trước chuyển sang kỳ này",
        "ct16": "Số thuế TNDN đã tạm nộp cho từng tỉnh",
        "ct17": "Chênh lệch giữa số thuế phải nộp và số thuế đã tạm nộp",
        "ct18": "Số thuế TNDN còn phải nộp cho từng tỉnh"
    },

    "PL 03-9": {
        "ThueTNDN_KyTruoc_ct04": "Số thuế TNDN đã tạm nộp bù trừ với số thuế phải nộp theo quyết toán kỳ này (Kỳ trước)",
        "ThueTNDN_KyTruoc_ct05": "Số tiền thuế đã tạm nộp chưa quyết toán chuyển kỳ sau (Kỳ trước)",
        "ThueTNDN_KyNay_ct06": "Tổng số tiền thu theo tiến độ trong kỳ (Kỳ này)",
        "ThueTNDN_KyNay_ct07": "Tổng số thuế TNDN đã tạm nộp trong kỳ (Kỳ này)",
        "ThueTNDN_KyNay_ct08": "Tổng số thuế TNDN đã tạm nộp bù trừ trong kỳ (Kỳ này)",
        "TongThueTNDN_ct09": "Tổng số tiền thu theo tiến độ (Toàn bộ)",
        "TongThueTNDN_ct10": "Tổng số thuế TNDN đã tạm nộp chưa quyết toán chuyển kỳ sau (Toàn bộ)",
        "chiTiet_ThueTNDN_ct2": "Tên dự án bất động sản",
        "chiTiet_DuanBDS_ct3_so": "Số chứng từ",
        "chiTiet_DuanBDS_ct3_ngay": "Ngày chứng từ",
        "chiTiet_ThueTNDN_ct4_ten": "Huyện",
        "chiTiet_ThueTNDN_ct5_ten": "Tỉnh",
        "chiTiet_ThueTNDN_ct6_ten": "Tên cơ quan thu",
        "chiTiet_DuanBDS_ct7": "Số tiền thu theo tiến độ",
        "chiTiet_ThueTNDN_ct8": "Số thuế TNDN đã tạm nộp",
        "chiTiet_ThueTNDN_ct9": "Số thuế TNDN đã tạm nộp bù trừ",
        "chiTiet_ThueTNDN_ct10": "Số tiền thuế đã tạm nộp chưa quyết toán chuyển kỳ sau"
    }
}
# Thêm từ điển ánh xạ cho Báo cáo tài chính TT200
TU_DIEN_TO_KHAI["BCTC_TT200"] = {

    # =================================================================
    # 1. BẢNG CÂN ĐỐI KẾ TOÁN (B01 - DN)
    # Lưu ý: Bảng này dùng cột "Số cuối năm" và "Số đầu năm"[cite: 56]
    # =================================================================
    "B01_CDKT": {
        "ct100": "A - TÀI SẢN NGẮN HẠN",  # [cite: 56]
        "ct110": "I. Tiền và các khoản tương đương tiền",  # [cite: 56]
        "ct111": "1. Tiền",  # [cite: 56]
        "ct112": "2. Các khoản tương đương tiền",  # [cite: 56]
        "ct120": "II. Đầu tư tài chính ngắn hạn",  # [cite: 56]
        "ct121": "1. Chứng khoán kinh doanh",  # [cite: 56]
        "ct122": "2. Dự phòng giảm giá chứng khoán kinh doanh",  # [cite: 56]
        "ct123": "3. Đầu tư nắm giữ đến ngày đáo hạn / Đầu tư vào công ty con (KLT)",  # [cite: 56]
        "ct124": "4. Đầu tư vào công ty liên doanh, liên kết (KLT)",  # [cite: 56]
        "ct125": "5. Đầu tư góp vốn vào đơn vị khác (KLT)",  # [cite: 56]
        "ct130": "III. Các khoản phải thu ngắn hạn",  # [cite: 56]
        "ct131": "1. Phải thu ngắn hạn của khách hàng",  # [cite: 56]
        "ct132": "2. Trả trước cho người bán ngắn hạn",  # [cite: 56]
        "ct133": "3. Phải thu nội bộ ngắn hạn / Vốn kinh doanh ở đơn vị trực thuộc (KLT)",  # [cite: 56]
        "ct134": "4. Phải thu theo tiến độ kế hoạch hợp đồng xây dựng / Phải thu nội bộ (KLT)",  # [cite: 56]
        "ct135": "5. Phải thu về cho vay ngắn hạn",  # [cite: 56]
        "ct136": "6. Phải thu ngắn hạn khác / Phải thu theo tiến độ KHHĐXD (KLT)",  # [cite: 56]
        "ct137": "7. Dự phòng phải thu ngắn hạn khó đòi / Phải thu khác (KLT)",  # [cite: 56]
        "ct138": "8. Tài sản thiếu chờ xử lý (KLT)",  # [cite: 56]
        "ct139": "8. Tài sản thiếu chờ xử lý",  # [cite: 56]
        "ct140": "IV. Hàng tồn kho",  # [cite: 56]
        "ct141": "1. Hàng tồn kho",  # [cite: 56]
        "ct149": "2. Dự phòng giảm giá hàng tồn kho",  # [cite: 56]
        "ct150": "V. Tài sản ngắn hạn khác / Tài sản cố định (KLT)",  # [cite: 56]
        "ct151": "1. Chi phí trả trước ngắn hạn / TSCĐ hữu hình (KLT)",  # [cite: 56]
        "ct152": "2. Thuế GTGT được khấu trừ / TSCĐ thuê tài chính (KLT)",  # [cite: 56]
        "ct153": "3. Thuế và các khoản khác phải thu Nhà nước / TSCĐ vô hình (KLT)",  # [cite: 56]
        "ct154": "4. Giao dịch mua bán lại trái phiếu Chính phủ",  # [cite: 56]
        "ct155": "5. Tài sản ngắn hạn khác",  # [cite: 56]
        "ct160": "VI. Bất động sản đầu tư (KLT)",  # [cite: 56]
        "ct170": "VII. Chi phí xây dựng cơ bản dở dang (KLT)",  # [cite: 56]
        "ct180": "VIII. Tài sản khác (KLT)",  # [cite: 56]
        "ct181": "1. Chi phí trả trước (KLT)",  # [cite: 56]
        "ct182": "2. Thuế GTGT được khấu trừ (KLT)",  # [cite: 56]
        "ct183": "3. Thuế và các khoản khác phải thu NN (KLT)",  # [cite: 56]
        "ct184": "4. Giao dịch mua bán lại trái phiếu Chính phủ (KLT)",  # [cite: 56]
        "ct185": "5. Tài sản thuế thu nhập hoãn lại (KLT)",  # [cite: 56]
        "ct186": "6. Tài sản khác (KLT)",  # [cite: 56]
        "ct200": "B - TÀI SẢN DÀI HẠN",  # [cite: 56]
        "ct210": "I. Các khoản phải thu dài hạn",  # [cite: 56]
        "ct211": "1. Phải thu dài hạn của khách hàng",  # [cite: 56]
        "ct212": "2. Trả trước cho người bán dài hạn",  # [cite: 56]
        "ct213": "3. Vốn kinh doanh ở đơn vị trực thuộc",  # [cite: 56]
        "ct214": "4. Phải thu nội bộ dài hạn",  # [cite: 56]
        "ct215": "5. Phải thu về cho vay dài hạn",  # [cite: 56]
        "ct216": "6. Phải thu dài hạn khác",  # [cite: 56]
        "ct219": "7. Dự phòng phải thu dài hạn khó đòi",  # [cite: 56]
        "ct220": "II. Tài sản cố định",  # [cite: 56]
        "ct221": "1. Tài sản cố định hữu hình",  # [cite: 56]
        "ct222": "- Nguyên giá TSCĐ hữu hình",  # [cite: 56]
        "ct223": "- Giá trị hao mòn luỹ kế TSCĐ hữu hình",  # [cite: 56]
        "ct224": "2. Tài sản cố định thuê tài chính",  # [cite: 56]
        "ct225": "- Nguyên giá TSCĐ thuê tài chính",  # [cite: 56]
        "ct226": "- Giá trị hao mòn luỹ kế TSCĐ thuê tài chính",  # [cite: 56]
        "ct227": "3. Tài sản cố định vô hình",  # [cite: 56]
        "ct228": "- Nguyên giá TSCĐ vô hình",  # [cite: 56]
        "ct229": "- Giá trị hao mòn luỹ kế TSCĐ vô hình",  # [cite: 56]
        "ct230": "III. Bất động sản đầu tư",  # [cite: 56]
        "ct231": "- Nguyên giá BĐS đầu tư",  # [cite: 56]
        "ct232": "- Giá trị hao mòn lũy kế BĐS đầu tư",  # [cite: 56]
        "ct240": "IV. Tài sản dang dở dài hạn",  # [cite: 56]
        "ct241": "1. Chi phí sản xuất, kinh doanh dở dang dài hạn",  # [cite: 56]
        "ct242": "2. Chi phí xây dựng cơ bản dở dang",  # [cite: 56]
        "ct250": "V. Đầu tư tài chính dài hạn",  # [cite: 56]
        "ct251": "1. Đầu tư vào công ty con",  # [cite: 56]
        "ct252": "2. Đầu tư vào công ty liên kết, liên doanh",  # [cite: 56]
        "ct253": "3. Đầu tư khác vào đơn vị khác",  # [cite: 56]
        "ct254": "4. Dự phòng đầu tư tài chính dài hạn",  # [cite: 56]
        "ct255": "5. Đầu tư nắm giữ đến ngày đáo hạn",  # [cite: 56]
        "ct260": "VI. Tài sản dài hạn khác",  # [cite: 56]
        "ct261": "1. Chi phí trả trước dài hạn",  # [cite: 56]
        "ct262": "2. Tài sản thuế thu nhập hoãn lại",  # [cite: 56]
        "ct263": "3. Thiết bị, vật tư, phụ tùng thay thế dài hạn",  # [cite: 56]
        "ct268": "4. Tài sản dài hạn khác",  # [cite: 56]
        "ct269": "5. Lợi thế thương mại",  # [cite: 56]
        "ct270": "TỔNG CỘNG TÀI SẢN (270 = 100 + 200)",  # [cite: 56]

        "ct300": "C - NỢ PHẢI TRẢ",  # [cite: 56]
        "ct310": "I. Nợ ngắn hạn",  # [cite: 56]
        "ct311": "1. Phải trả người bán ngắn hạn",  # [cite: 56]
        "ct312": "2. Người mua trả tiền trước ngắn hạn",  # [cite: 56]
        "ct313": "3. Thuế và các khoản phải nộp Nhà nước",  # [cite: 56]
        "ct314": "4. Phải trả người lao động",  # [cite: 56]
        "ct315": "5. Chi phí phải trả ngắn hạn",  # [cite: 56]
        "ct316": "6. Phải trả nội bộ ngắn hạn / Phải trả nội bộ khác (KLT)",  # [cite: 56]
        "ct317": "7. Phải trả theo tiến độ kế hoạch hợp đồng xây dựng",  # [cite: 56]
        "ct318": "8. Doanh thu chưa thực hiện ngắn hạn",  # [cite: 56]
        "ct319": "9. Phải trả ngắn hạn khác",  # [cite: 56]
        "ct320": "10. Vay và nợ thuê tài chính ngắn hạn",  # [cite: 56]
        "ct321": "11. Dự phòng phải trả ngắn hạn",  # [cite: 56]
        "ct322": "12. Quỹ khen thưởng, phúc lợi",  # [cite: 56]
        "ct323": "13. Quỹ bình ổn giá",  # [cite: 56]
        "ct324": "14. Giao dịch mua bán lại trái phiếu Chính phủ",  # [cite: 56]
        "ct330": "II. Nợ dài hạn",  # [cite: 56]
        "ct331": "1. Phải trả người bán dài hạn",  # [cite: 56]
        "ct332": "2. Người mua trả tiền trước dài hạn",  # [cite: 56]
        "ct333": "3. Chi phí phải trả dài hạn",  # [cite: 56]
        "ct334": "4. Phải trả nội bộ về vốn kinh doanh",  # [cite: 56]
        "ct335": "5. Phải trả nội bộ dài hạn",  # [cite: 56]
        "ct336": "6. Doanh thu chưa thực hiện dài hạn",  # [cite: 56]
        "ct337": "7. Phải trả dài hạn khác",  # [cite: 56]
        "ct338": "8. Vay và nợ thuê tài chính dài hạn",  # [cite: 56]
        "ct339": "9. Trái phiếu chuyển đổi",  # [cite: 56]
        "ct340": "10. Cổ phiếu ưu đãi",  # [cite: 56]
        "ct341": "11. Thuế thu nhập hoãn lại phải trả",  # [cite: 56]
        "ct342": "12. Dự phòng phải trả dài hạn",  # [cite: 56]
        "ct343": "13. Quỹ phát triển khoa học và công nghệ",  # [cite: 56]

        "ct400": "D - VỐN CHỦ SỞ HỮU",  # [cite: 56]
        "ct410": "I. Vốn chủ sở hữu",  # [cite: 56]
        "ct411": "1. Vốn góp của chủ sở hữu",  # [cite: 56]
        "ct411a": "- Cổ phiếu phổ thông có quyền biểu quyết",  # [cite: 56]
        "ct411b": "- Cổ phiếu ưu đãi",  # [cite: 56]
        "ct412": "2. Thặng dư vốn cổ phần",  # [cite: 56]
        "ct413": "3. Quyền chọn chuyển đổi trái phiếu",  # [cite: 56]
        "ct414": "4. Vốn khác của chủ sở hữu",  # [cite: 56]
        "ct415": "5. Cổ phiếu quỹ",  # [cite: 56]
        "ct416": "6. Chênh lệch đánh giá lại tài sản",  # [cite: 56]
        "ct417": "7. Chênh lệch tỷ giá hối đoái",  # [cite: 56]
        "ct418": "8. Quỹ đầu tư phát triển",  # [cite: 56]
        "ct419": "9. Quỹ hỗ trợ sắp xếp doanh nghiệp",  # [cite: 56]
        "ct420": "10. Quỹ khác thuộc vốn chủ sở hữu",  # [cite: 56]
        "ct421": "11. Lợi nhuận sau thuế chưa phân phối",  # [cite: 56]
        "ct421a": "- LNST chưa phân phối lũy kế đến cuối kỳ trước",  # [cite: 56]
        "ct421b": "- LNST chưa phân phối kỳ này",  # [cite: 56]
        "ct422": "12. Nguồn vốn đầu tư XDCB",  # [cite: 56]
        "ct429": "13. Lợi ích cổ đông không kiểm soát",  # [cite: 56]
        "ct430": "II. Nguồn kinh phí và quỹ khác",  # [cite: 56]
        "ct431": "1. Nguồn kinh phí",  # [cite: 56]
        "ct432": "2. Nguồn kinh phí đã hình thành TSCĐ",  # [cite: 56]
        "ct440": "TỔNG CỘNG NGUỒN VỐN (440 = 300 + 400)"  # [cite: 56]
    },

    # =================================================================
    # 2. BÁO CÁO KẾT QUẢ HOẠT ĐỘNG KINH DOANH (B02 - DN)[cite: 53]
    # Lưu ý: Bảng này dùng cột "Năm nay" và "Năm trước"[cite: 53]
    # =================================================================
    "B02_KQKD": {
        "ct01": "1. Doanh thu bán hàng và cung cấp dịch vụ",  # [cite: 53]
        "ct02": "2. Các khoản giảm trừ doanh thu",  # [cite: 53]
        "ct10": "3. Doanh thu thuần về bán hàng và cung cấp dịch vụ (10 = 01 - 02)",  # [cite: 53]
        "ct11": "4. Giá vốn hàng bán",  # [cite: 53]
        "ct20": "5. Lợi nhuận gộp về bán hàng và cung cấp dịch vụ (20 = 10 - 11)",  # [cite: 53]
        "ct21": "6. Doanh thu hoạt động tài chính",  # [cite: 53]
        "ct22": "7. Chi phí tài chính",  # [cite: 53]
        "ct23": "- Trong đó: Chi phí lãi vay",  # [cite: 53]
        "ct24": "8. Phần lãi hoặc lỗ trong công ty liên doanh, liên kết",  # [cite: 53]
        "ct25": "9. Chi phí bán hàng",  # [cite: 53]
        "ct26": "10. Chi phí quản lý doanh nghiệp",  # [cite: 53]
        "ct30": "11 Lợi nhuận thuần từ hoạt động kinh doanh {30 = 20 + (21 - 22) - (25 + 26) + 24}",  # [cite: 53]
        "ct31": "12. Thu nhập khác",  # [cite: 53]
        "ct32": "13. Chi phí khác",  # [cite: 53]
        "ct40": "14. Lợi nhuận khác (40 = 31 - 32)",  # [cite: 53]
        "ct50": "15. Tổng lợi nhuận kế toán trước thuế (50 = 30 + 40)",  # [cite: 53]
        "ct51": "16. Chi phí thuế TNDN hiện hành",  # [cite: 53]
        "ct52": "17. Chi phí thuế TNDN hoãn lại",  # [cite: 53]
        "ct60": "18. Lợi nhuận sau thuế thu nhập doanh nghiệp (60 = 50 - 51 - 52)",  # [cite: 53]
        "ct61": "19. Lợi nhuận sau thuế của công ty mẹ",  # [cite: 53]
        "ct62": "20. Lợi nhuận sau thuế của cổ đông không kiểm soát",  # [cite: 53]
        "ct70": "21. Lãi cơ bản trên cổ phiếu",  # [cite: 53]
        "ct71": "22. Lãi suy giảm trên cổ phiếu"  # [cite: 53]
    },

    # =================================================================
    # 3. BÁO CÁO LƯU CHUYỂN TIỀN TỆ TRỰC TIẾP (B03 - DN)[cite: 55]
    # Lưu ý: Bảng này dùng cột "Năm nay" và "Năm trước"[cite: 55]
    # =================================================================
    "B03_LCTT_TT": {
        "ct01": "1. Tiền thu từ bán hàng, cung cấp dịch vụ và doanh thu khác",  # [cite: 55]
        "ct02": "2. Tiền chi trả cho người cung cấp hàng hóa và dịch vụ",  # [cite: 55]
        "ct03": "3. Tiền chi trả cho người lao động",  # [cite: 55]
        "ct04": "4. Tiền lãi vay đã trả",  # [cite: 55]
        "ct05": "5. Thuế thu nhập doanh nghiệp đã nộp",  # [cite: 55]
        "ct06": "6. Tiền thu khác từ hoạt động kinh doanh",  # [cite: 55]
        "ct07": "7. Tiền chi khác cho hoạt động kinh doanh",  # [cite: 55]
        "ct20": "Lưu chuyển tiền thuần từ hoạt động kinh doanh",  # [cite: 55]
        "ct21": "1. Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác",  # [cite: 55]
        "ct22": "2. Tiền thu từ thanh lý, nhượng bán TSCĐ và các tài sản dài hạn khác",  # [cite: 55]
        "ct23": "3. Tiền chi cho vay, mua các công cụ nợ của đơn vị khác",  # [cite: 55]
        "ct24": "4. Tiền thu hồi cho vay, bán lại các công cụ nợ của đơn vị khác",  # [cite: 55]
        "ct25": "5. Tiền chi đầu tư góp vốn vào đơn vị khác",  # [cite: 55]
        "ct26": "6. Tiền thu hồi đầu tư góp vốn vào đơn vị khác",  # [cite: 55]
        "ct27": "7. Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia",  # [cite: 55]
        "ct30": "Lưu chuyển tiền thuần từ hoạt động đầu tư",  # [cite: 55]
        "ct31": "1. Tiền thu từ phát hành cổ phiếu, nhận vốn góp của chủ sở hữu",  # [cite: 55]
        "ct32": "2. Tiền chi trả vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp đã phát hành",
        # [cite: 55]
        "ct33": "3. Tiền thu từ đi vay",  # [cite: 55]
        "ct34": "4. Tiền trả nợ gốc vay",  # [cite: 55]
        "ct35": "5. Tiền trả nợ gốc thuê tài chính",  # [cite: 55]
        "ct36": "6. Cổ tức, lợi nhuận đã trả cho chủ sở hữu",  # [cite: 55]
        "ct40": "Lưu chuyển tiền thuần từ hoạt động tài chính",  # [cite: 55]
        "ct50": "Lưu chuyển tiền thuần trong kỳ (50 = 20+30+40)",  # [cite: 55]
        "ct60": "Tiền và tương đương tiền đầu kỳ",  # [cite: 55]
        "ct61": "Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ",  # [cite: 55]
        "ct70": "Tiền và tương đương tiền cuối kỳ (70 = 50+60+61)"  # [cite: 55]
    },

    # =================================================================
    # 4. BÁO CÁO LƯU CHUYỂN TIỀN TỆ GIÁN TIẾP (B03 - DN)[cite: 54]
    # Lưu ý: Bảng này dùng cột "Năm nay" và "Năm trước"[cite: 54]
    # =================================================================
    "B03_LCTT_GT": {
        "ct01": "1. Lợi nhuận trước thuế",  # [cite: 54]
        "ct02": "- Khấu hao TSCĐ và BĐSĐT",  # [cite: 54]
        "ct03": "- Các khoản dự phòng",  # [cite: 54]
        "ct04": "- Lãi, lỗ chênh lệch tỷ giá hối đoái do đánh giá lại các khoản mục tiền tệ",  # [cite: 54]
        "ct05": "- Lãi, lỗ từ hoạt động đầu tư",  # [cite: 54]
        "ct06": "- Chi phí lãi vay",  # [cite: 54]
        "ct07": "- Các khoản điều chỉnh khác",  # [cite: 54]
        "ct08": "3. Lợi nhuận từ hoạt động kinh doanh trước thay đổi vốn lưu động",  # [cite: 54]
        "ct09": "- Tăng, giảm các khoản phải thu",  # [cite: 54]
        "ct10": "- Tăng, giảm hàng tồn kho",  # [cite: 54]
        "ct11": "- Tăng, giảm các khoản phải trả (Không kể lãi vay phải trả, thuế TNDN phải nộp)",  # [cite: 54]
        "ct12": "- Tăng, giảm chi phí trả trước",  # [cite: 54]
        "ct13": "- Tăng, giảm chứng khoán kinh doanh",  # [cite: 54]
        "ct14": "- Tiền lãi vay đã trả",  # [cite: 54]
        "ct15": "- Thuế thu nhập doanh nghiệp đã nộp",  # [cite: 54]
        "ct16": "- Tiền thu khác từ hoạt động kinh doanh",  # [cite: 54]
        "ct17": "- Tiền chi khác cho hoạt động kinh doanh",  # [cite: 54]
        "ct20": "Lưu chuyển tiền thuần từ hoạt động kinh doanh",  # [cite: 54]
        "ct21": "1. Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác",  # [cite: 54]
        "ct22": "2. Tiền thu từ thanh lý, nhượng bán TSCĐ và các tài sản dài hạn khác",  # [cite: 54]
        "ct23": "3. Tiền chi cho vay, mua các công cụ nợ của đơn vị khác",  # [cite: 54]
        "ct24": "4. Tiền thu hồi cho vay, bán lại các công cụ nợ của đơn vị khác",  # [cite: 54]
        "ct25": "5. Tiền chi đầu tư góp vốn vào đơn vị khác",  # [cite: 54]
        "ct26": "6. Tiền thu hồi đầu tư góp vốn vào đơn vị khác",  # [cite: 54]
        "ct27": "7. Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia",  # [cite: 54]
        "ct30": "Lưu chuyển tiền thuần từ hoạt động đầu tư",  # [cite: 54]
        "ct31": "1. Tiền thu từ phát hành cổ phiếu, nhận vốn góp của chủ sở hữu",  # [cite: 54]
        "ct32": "2. Tiền chi trả vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp",  # [cite: 54]
        "ct33": "3. Tiền thu từ đi vay",  # [cite: 54]
        "ct34": "4. Tiền trả nợ gốc vay",  # [cite: 54]
        "ct35": "5. Tiền trả nợ gốc thuê tài chính",  # [cite: 54]
        "ct36": "6. Cổ tức, lợi nhuận đã trả cho chủ sở hữu",  # [cite: 54]
        "ct40": "Lưu chuyển tiền thuần từ hoạt động tài chính",  # [cite: 54]
        "ct50": "Lưu chuyển tiền thuần trong kỳ (50 = 20+30+40)",  # [cite: 54]
        "ct60": "Tiền và tương đương tiền đầu kỳ",  # [cite: 54]
        "ct61": "Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ",  # [cite: 54]
        "ct70": "Tiền và tương đương tiền cuối kỳ (70 = 50+60+61)"  # [cite: 54]
    },
}

# Thêm từ điển ánh xạ cho Báo cáo tài chính TT133
# Thêm từ điển ánh xạ cho Báo cáo tài chính TT133
TU_DIEN_TO_KHAI["BCTC_TT133"] = {

    # =================================================================
    # 1. BẢNG CÂN ĐỐI KẾ TOÁN (B01a, B01b - DNN, DNNKLT, DNSN)
    # =================================================================
    "B01_CDKT": {
        "ct100": "A – TÀI SẢN NGẮN HẠN (B01b) / TÀI SẢN NGẮN HẠN (B01a)",
        "ct110": "I. Tiền và các khoản tương đương tiền / 1. Tiền và các khoản tương đương tiền (SN)",
        "ct120": "II. Đầu tư tài chính / 2. Các khoản đầu tư (SN)",
        "ct121": "1. Chứng khoán kinh doanh",
        "ct122": "2. Đầu tư nắm giữ đến ngày đáo hạn / Dự phòng giảm giá chứng khoán kinh doanh (B01b)",
        "ct123": "3. Đầu tư góp vốn vào đơn vị khác / Đầu tư nắm giữ đến ngày đáo hạn ngắn hạn (B01b)",
        "ct124": "4. Dự phòng tổn thất đầu tư tài chính",
        "ct130": "III. Các khoản phải thu / 3. Các khoản phải thu (SN)",
        "ct131": "1. Phải thu của khách hàng",
        "ct132": "2. Trả trước cho người bán",
        "ct133": "3. Vốn kinh doanh ở đơn vị trực thuộc / Phải thu ngắn hạn khác (B01b)",
        "ct134": "4. Phải thu khác / Tài sản thiếu chờ xử lý (B01b)",
        "ct135": "5. Tài sản thiếu chờ xử lý / Dự phòng phải thu ngắn hạn khó đòi (B01b)",
        "ct136": "6. Dự phòng phải thu khó đòi",
        "ct140": "IV. Hàng tồn kho / 4. Hàng tồn kho (SN)",
        "ct141": "1. Hàng tồn kho",
        "ct142": "2. Dự phòng giảm giá hàng tồn kho",
        "ct150": "V. Tài sản cố định và bất động sản đầu tư / V. Tài sản ngắn hạn khác (B01b) / 5. Giá trị còn lại của TSCĐ và BĐSĐT (SN)",
        "ct151": "- Nguyên giá / Thuế GTGT được khấu trừ (B01b)",
        "ct152": "- Giá trị hao mòn lũy kế / Tài sản ngắn hạn khác (B01b)",
        "ct160": "VI. Xây dựng cơ bản dở dang / Bất động sản đầu tư / 6. Tài sản khác (SN)",
        "ct161": "- Nguyên giá BĐSĐT",
        "ct162": "- Giá trị hao mòn lũy kế BĐSĐT",
        "ct170": "VII. Tài sản khác / XDCB dở dang",
        "ct171": "1. Thuế GTGT được khấu trừ",
        "ct172": "2. Tài sản khác",
        "ct180": "VIII. Tài sản khác",
        "ct181": "1. Thuế GTGT được khấu trừ",
        "ct182": "2. Tài sản khác",

        "ct200": "TỔNG CỘNG TÀI SẢN (B01a) / B - TÀI SẢN DÀI HẠN (B01b)",
        "ct210": "I. Các khoản phải thu dài hạn",
        "ct211": "1. Phải thu dài hạn của khách hàng",
        "ct212": "2. Trả trước cho người bán dài hạn",
        "ct213": "3. Vốn kinh doanh ở đơn vị trực thuộc",
        "ct214": "4. Phải thu dài hạn khác",
        "ct215": "5. Dự phòng phải thu dài hạn khó đòi",
        "ct220": "II. Tài sản cố định",
        "ct221": "- Nguyên giá",
        "ct222": "- Giá trị hao mòn lũy kế",
        "ct230": "III. Bất động sản đầu tư",
        "ct231": "- Nguyên giá",
        "ct232": "- Giá trị hao mòn lũy kế",
        "ct240": "IV. Xây dựng cơ bản dở dang",
        "ct250": "V. Đầu tư tài chính dài hạn",
        "ct251": "1. Đầu tư góp vốn vào đơn vị khác",
        "ct252": "2. Dự phòng tổn thất đầu tư vào đơn vị khác",
        "ct253": "3. Đầu tư nắm giữ đến ngày đáo hạn dài hạn",
        "ct260": "VI. Tài sản dài hạn khác",
        "ct300": "C - NỢ PHẢI TRẢ (B01b) / I. Nợ phải trả (B01a) / TỔNG CỘNG TÀI SẢN (B01b)",

        "ct310": "1. Phải trả người bán (SN) / I. Nợ ngắn hạn (B01b)",
        "ct311": "1. Phải trả người bán / 1. Phải trả người bán ngắn hạn (B01b)",
        "ct312": "2. Người mua trả tiền trước / 2. Người mua trả tiền trước ngắn hạn (B01b)",
        "ct313": "3. Thuế và các khoản phải nộp Nhà nước",
        "ct314": "4. Phải trả người lao động",
        "ct315": "5. Phải trả khác / 5. Phải trả ngắn hạn khác (B01b)",
        "ct316": "6. Vay và nợ thuê tài chính / 6. Vay và nợ thuê tài chính ngắn hạn (B01b)",
        "ct317": "7. Phải trả nội bộ về vốn kinh doanh / 7. Dự phòng phải trả ngắn hạn (B01b)",
        "ct318": "8. Dự phòng phải trả / 8. Quỹ khen thưởng, phúc lợi (B01b)",
        "ct319": "9. Quỹ khen thưởng, phúc lợi",
        "ct320": "10. Quỹ phát triển khoa học và công nghệ / 2. Người mua trả tiền trước (SN)",
        "ct330": "3. Thuế và các khoản phải nộp Nhà nước (SN)",
        "ct340": "4. Phải trả người lao động (SN)",
        "ct350": "5. Phải trả nợ vay (SN)",
        "ct360": "6. Phải trả khác (SN)",

        "ct400": "II. Vốn chủ sở hữu / D - VỐN CHỦ SỞ HỮU (B01b)",
        "ct410": "1. Vốn đầu tư của chủ sở hữu (SN) / I. Nợ ngắn hạn (B01b)",
        "ct411": "1. Vốn góp của chủ sở hữu / 1. Phải trả người bán ngắn hạn (B01b)",
        "ct412": "2. Thặng dư vốn cổ phần / 2. Người mua trả tiền trước ngắn hạn (B01b)",
        "ct413": "3. Vốn khác của chủ sở hữu / 3. Thuế và các khoản phải nộp Nhà nước (B01b)",
        "ct414": "4. Cổ phiếu quỹ / 4. Phải trả người lao động (B01b)",
        "ct415": "5. Chênh lệch tỷ giá hối đoái / 5. Phải trả ngắn hạn khác (B01b)",
        "ct416": "6. Các quỹ thuộc vốn chủ sở hữu / 6. Vay và nợ thuê tài chính ngắn hạn (B01b)",
        "ct417": "7. Lợi nhuận sau thuế chưa phân phối / 7. Dự phòng phải trả ngắn hạn (B01b)",
        "ct418": "8. Quỹ khen thưởng, phúc lợi (B01b)",
        "ct420": "2. Lợi nhuận sau thuế chưa phân phối (SN) / II. Nợ dài hạn (B01b)",
        "ct421": "1. Phải trả người bán dài hạn (B01b)",
        "ct422": "2. Người mua trả tiền trước dài hạn (B01b)",
        "ct423": "3. Phải trả nội bộ về vốn kinh doanh (B01b)",
        "ct424": "4. Phải trả dài hạn khác (B01b)",
        "ct425": "5. Vay và nợ thuê tài chính dài hạn (B01b)",
        "ct426": "6. Dự phòng phải trả dài hạn (B01b)",
        "ct427": "7. Quỹ phát triển khoa học và công nghệ (B01b)",
        "ct430": "3. Các khoản mục khác thuộc vốn chủ sở hữu (SN)",

        "ct500": "TỔNG CỘNG NGUỒN VỐN / D - VỐN CHỦ SỞ HỮU (B01b)",
        "ct511": "1. Vốn góp của chủ sở hữu (B01b)",
        "ct512": "2. Thặng dư vốn cổ phần (B01b)",
        "ct513": "3. Vốn khác của chủ sở hữu (B01b)",
        "ct514": "4. Cổ phiếu quỹ (B01b)",
        "ct515": "5. Chênh lệch tỷ giá hối đoái (B01b)",
        "ct516": "6. Các quỹ thuộc vốn chủ sở hữu (B01b)",
        "ct517": "7. Lợi nhuận sau thuế chưa phân phối (B01b)",
        "ct600": "TỔNG CỘNG NGUỒN VỐN (B01b)"
    },

    # =================================================================
    # 2. BÁO CÁO KẾT QUẢ HOẠT ĐỘNG KINH DOANH (B02 - DNN)
    # =================================================================
    "B02_KQKD": {
        "ct01": "1. Doanh thu bán hàng và cung cấp dịch vụ / Doanh thu thuần về bán hàng và cung cấp dịch vụ",
        "ct02": "2. Các khoản giảm trừ doanh thu / Giá vốn hàng bán",
        "ct03": "3. Chi phí quản lý kinh doanh",
        "ct04": "4. Lãi/lỗ hoạt động tài chính và hoạt động khác",
        "ct05": "5. Lợi nhuận kế toán trước thuế (05=01-02-03+04)",
        "ct06": "6. Chi phí thuế TNDN",
        "ct07": "7. Lợi nhuận sau thuế thu nhập doanh nghiệp (07=05-06)",
        "ct10": "3. Doanh thu thuần về bán hàng và cung cấp dịch vụ (10= 01-02)",
        "ct11": "4. Giá vốn hàng bán",
        "ct20": "5. Lợi nhuận gộp về bán hàng và cung cấp dịch vụ (20=10-11)",
        "ct21": "6. Doanh thu hoạt động tài chính",
        "ct22": "7. Chi phí tài chính",
        "ct23": "- Trong đó: Chi phí lãi vay",
        "ct24": "8. Chi phí quản lý kinh doanh",
        "ct30": "9. Lợi nhuận thuần từ hoạt động kinh doanh (30 = 20 + 21 - 22 - 24)",
        "ct31": "10. Thu nhập khác",
        "ct32": "11. Chi phí khác",
        "ct40": "12. Lợi nhuận khác (40 = 31 - 32)",
        "ct50": "13. Tổng lợi nhuận kế toán trước thuế (50 = 30 + 40)",
        "ct51": "14. Chi phí thuế TNDN",
        "ct60": "15. Lợi nhuận sau thuế thu nhập doanh nghiệp (60=50 - 51)"
    },

    # =================================================================
    # 3. BÁO CÁO LƯU CHUYỂN TIỀN TỆ TRỰC TIẾP VÀ GIÁN TIẾP (B03 - DNN)
    # =================================================================
    "B03_LCTT_TT": {
        "ct01": "1. Tiền thu từ bán hàng, cung cấp dịch vụ và doanh thu khác",
        "ct02": "2. Tiền chi trả cho người cung cấp hàng hóa và dịch vụ",
        "ct03": "3. Tiền chi trả cho người lao động",
        "ct04": "4. Tiền lãi vay đã trả",
        "ct05": "5. Thuế thu nhập doanh nghiệp đã nộp",
        "ct06": "6. Tiền thu khác từ hoạt động kinh doanh",
        "ct07": "7. Tiền chi khác cho hoạt động kinh doanh",
        "ct20": "Lưu chuyển tiền thuần từ hoạt động kinh doanh",
        "ct21": "1. Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác",
        "ct22": "2. Tiền thu từ thanh lý, nhượng bán TSCĐ và các tài sản dài hạn khác",
        "ct23": "3. Tiền chi cho vay, mua các công cụ nợ của đơn vị khác",
        "ct24": "4. Tiền thu hồi cho vay, bán lại các công cụ nợ của đơn vị khác",
        "ct25": "5. Tiền chi đầu tư góp vốn vào đơn vị khác",
        "ct26": "6. Tiền thu hồi đầu tư góp vốn vào đơn vị khác",
        "ct27": "7. Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia",
        "ct30": "Lưu chuyển tiền thuần từ hoạt động đầu tư",
        "ct31": "1. Tiền thu từ phát hành cổ phiếu, nhận vốn góp của chủ sở hữu",
        "ct32": "2. Tiền chi trả vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp",
        "ct33": "3. Tiền thu từ đi vay",
        "ct34": "4. Tiền trả nợ gốc vay",
        "ct35": "5. Tiền trả nợ gốc thuê tài chính",
        "ct36": "6. Cổ tức, lợi nhuận đã trả cho chủ sở hữu",
        "ct40": "Lưu chuyển tiền thuần từ hoạt động tài chính",
        "ct50": "Lưu chuyển tiền thuần trong kỳ (50 = 20+30+40)",
        "ct60": "Tiền và tương đương tiền đầu kỳ",
        "ct61": "Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ",
        "ct70": "Tiền và tương đương tiền cuối kỳ (70 = 50+60+61)"
    },

    "B03_LCTT_GT": {
        "ct01": "1. Lợi nhuận trước thuế",
        "ct02": "- Khấu hao TSCĐ và BĐSĐT / Điều chỉnh cho các khoản",
        "ct03": "- Các khoản dự phòng",
        "ct04": "- Lãi, lỗ chênh lệch tỷ giá hối đoái do đánh giá lại các khoản mục tiền tệ",
        "ct05": "- Lãi, lỗ từ hoạt động đầu tư",
        "ct06": "- Chi phí lãi vay",
        "ct07": "- Các khoản điều chỉnh khác",
        "ct08": "3. Lợi nhuận từ hoạt động kinh doanh trước thay đổi vốn lưu động",
        "ct09": "- Tăng, giảm các khoản phải thu",
        "ct10": "- Tăng, giảm hàng tồn kho",
        "ct11": "- Tăng, giảm các khoản phải trả (Không kể lãi vay phải trả, thuế TNDN phải nộp)",
        "ct12": "- Tăng, giảm chi phí trả trước",
        "ct13": "- Tăng, giảm chứng khoán kinh doanh",
        "ct14": "- Tiền lãi vay đã trả",
        "ct15": "- Thuế thu nhập doanh nghiệp đã nộp",
        "ct16": "- Tiền thu khác từ hoạt động kinh doanh",
        "ct17": "- Tiền chi khác cho hoạt động kinh doanh",
        "ct18": "- Tiền chi khác cho hoạt động kinh doanh",
        "ct20": "Lưu chuyển tiền thuần từ hoạt động kinh doanh",
        "ct21": "1. Tiền chi để mua sắm, xây dựng TSCĐ, BĐSĐT và các tài sản dài hạn khác",
        "ct22": "2. Tiền thu từ thanh lý, nhượng bán TSCĐ, BĐSĐT và các tài sản dài hạn khác",
        "ct23": "3. Tiền chi cho vay, mua các công cụ nợ của đơn vị khác",
        "ct24": "4. Tiền thu hồi cho vay, bán lại các công cụ nợ của đơn vị khác",
        "ct25": "5. Tiền chi đầu tư góp vốn vào đơn vị khác",
        "ct26": "6. Tiền thu hồi đầu tư góp vốn vào đơn vị khác",
        "ct27": "7. Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia",
        "ct30": "Lưu chuyển tiền thuần từ hoạt động đầu tư",
        "ct31": "1. Tiền thu từ phát hành cổ phiếu, nhận vốn góp của chủ sở hữu",
        "ct32": "2. Tiền chi trả vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp",
        "ct33": "3. Tiền thu từ đi vay",
        "ct34": "4. Tiền trả nợ gốc vay",
        "ct35": "5. Tiền trả nợ gốc thuê tài chính",
        "ct36": "6. Cổ tức, lợi nhuận đã trả cho chủ sở hữu",
        "ct40": "Lưu chuyển tiền thuần từ hoạt động tài chính",
        "ct50": "Lưu chuyển tiền thuần trong kỳ (50 = 20+30+40)",
        "ct60": "Tiền và tương đương tiền đầu kỳ",
        "ct61": "Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ",
        "ct70": "Tiền và tương đương tiền cuối kỳ (70 = 50+60+61)"
    },

    # =================================================================
    # 4. CÂN ĐỐI TÀI KHOẢN (PL_CDTK)
    # =================================================================
    "B04_CDTK": {
        "ct111": "Tài khoản 111 - Tiền mặt",  # [cite: 47]
        "ct1111": "Tài khoản 1111 - Tiền Việt Nam",  # [cite: 47]
        "ct1112": "Tài khoản 1112 - Ngoại tệ",  # [cite: 47]
        "ct112": "Tài khoản 112 - Tiền gửi Ngân hàng",  # [cite: 47]
        "ct1121": "Tài khoản 1121 - Tiền Việt Nam",  # [cite: 47]
        "ct1122": "Tài khoản 1122 - Ngoại tệ",  # [cite: 47]
        "ct121": "Tài khoản 121 - Chứng khoán kinh doanh",  # [cite: 47]
        "ct128": "Tài khoản 128 - Đầu tư nắm giữ đến ngày đáo hạn",  # [cite: 47]
        "ct1281": "Tài khoản 1281 - Tiền gửi có kỳ hạn",  # [cite: 47]
        "ct1288": "Tài khoản 1288 - Các khoản đầu tư khác nắm giữ đến ngày đáo hạn",  # [cite: 47]
        "ct131": "Tài khoản 131 - Phải thu của khách hàng",  # [cite: 47]
        "ct133": "Tài khoản 133 - Thuế GTGT được khấu trừ",  # [cite: 47]
        "ct1331": "Tài khoản 1331 - Thuế GTGT được khấu trừ của hàng hoá, dịch vụ",  # [cite: 47]
        "ct1332": "Tài khoản 1332 - Thuế GTGT được khấu trừ của TSCĐ",  # [cite: 47]
        "ct136": "Tài khoản 136 - Phải thu nội bộ",  # [cite: 47]
        "ct1361": "Tài khoản 1361 - Vốn kinh doanh ở đơn vị trực thuộc",  # [cite: 47]
        "ct1368": "Tài khoản 1368 - Phải thu nội bộ khác",  # [cite: 47]
        "ct138": "Tài khoản 138 - Phải thu khác",  # [cite: 47]
        "ct1381": "Tài khoản 1381 - Tài sản thiếu chờ xử lý",  # [cite: 47]
        "ct1386": "Tài khoản 1386 - Cầm cố, thế chấp, ký quỹ, ký cược",  # [cite: 47]
        "ct1388": "Tài khoản 1388 - Phải thu khác",  # [cite: 47]
        "ct141": "Tài khoản 141 - Tạm ứng",  # [cite: 47]
        "ct151": "Tài khoản 151 - Hàng mua đang đi đường",  # [cite: 47]
        "ct152": "Tài khoản 152 - Nguyên liệu, vật liệu",  # [cite: 47]
        "ct153": "Tài khoản 153 - Công cụ, dụng cụ",  # [cite: 47]
        "ct154": "Tài khoản 154 - Chi phí sản xuất, kinh doanh dở dang",  # [cite: 47]
        "ct155": "Tài khoản 155 - Thành phẩm",  # [cite: 47]
        "ct156": "Tài khoản 156 - Hàng hoá",  # [cite: 47]
        "ct157": "Tài khoản 157 - Hàng gửi đi bán",  # [cite: 47]
        "ct211": "Tài khoản 211 - Tài sản cố định",  # [cite: 47]
        "ct2111": "Tài khoản 2111 - TSCĐ hữu hình",  # [cite: 47]
        "ct2112": "Tài khoản 2112 - TSCĐ thuê tài chính",  # [cite: 47]
        "ct2113": "Tài khoản 2113 - TSCĐ vô hình",  # [cite: 47]
        "ct214": "Tài khoản 214 - Hao mòn TSCĐ",  # [cite: 47]
        "ct2141": "Tài khoản 2141 - Hao mòn TSCĐ hữu hình",  # [cite: 47]
        "ct2142": "Tài khoản 2142 - Hao mòn TSCĐ thuê tài chính",  # [cite: 47]
        "ct2143": "Tài khoản 2143 - Hao mòn TSCĐ vô hình",  # [cite: 47]
        "ct2147": "Tài khoản 2147 - Hao mòn bất động sản đầu tư",  # [cite: 47]
        "ct217": "Tài khoản 217 - Bất động sản đầu tư",  # [cite: 47]
        "ct228": "Tài khoản 228 - Đầu tư góp vốn vào đơn vị khác",  # [cite: 47]
        "ct2281": "Tài khoản 2281 - Đầu tư vào công ty liên doanh, liên kết",  # [cite: 47]
        "ct2288": "Tài khoản 2288 - Đầu tư khác",  # [cite: 47]
        "ct229": "Tài khoản 229 - Dự phòng tổn thất tài sản",  # [cite: 47]
        "ct2291": "Tài khoản 2291 - Dự phòng giảm giá chứng khoán kinh doanh",  # [cite: 47]
        "ct2292": "Tài khoản 2292 - Dự phòng tổn thất đầu tư vào đơn vị khác",  # [cite: 47]
        "ct2293": "Tài khoản 2293 - Dự phòng phải thu khó đòi",  # [cite: 47]
        "ct2294": "Tài khoản 2294 - Dự phòng giảm giá hàng tồn kho",  # [cite: 47]
        "ct241": "Tài khoản 241 - Xây dựng cơ bản dở dang",  # [cite: 47]
        "ct2411": "Tài khoản 2411 - Mua sắm TSCĐ",  # [cite: 47]
        "ct2412": "Tài khoản 2412 - Xây dựng cơ bản",  # [cite: 47]
        "ct2413": "Tài khoản 2413 - Sửa chữa lớn TSCĐ",  # [cite: 47]
        "ct242": "Tài khoản 242 - Chi phí trả trước",  # [cite: 47]

        "ct331": "Tài khoản 331 - Phải trả cho người bán",  # [cite: 47]
        "ct333": "Tài khoản 333 - Thuế và các khoản phải nộp Nhà nước",  # [cite: 47]
        "ct3331": "Tài khoản 3331 - Thuế giá trị gia tăng phải nộp",  # [cite: 47]
        "ct33311": "Tài khoản 33311 - Thuế GTGT đầu ra",  # [cite: 47]
        "ct33312": "Tài khoản 33312 - Thuế GTGT hàng nhập khẩu",  # [cite: 47]
        "ct3332": "Tài khoản 3332 - Thuế tiêu thụ đặc biệt",  # [cite: 47]
        "ct3333": "Tài khoản 3333 - Thuế xuất, nhập khẩu",  # [cite: 47]
        "ct3334": "Tài khoản 3334 - Thuế thu nhập doanh nghiệp",  # [cite: 47]
        "ct3335": "Tài khoản 3335 - Thuế thu nhập cá nhân",  # [cite: 47]
        "ct3336": "Tài khoản 3336 - Thuế tài nguyên",  # [cite: 47]
        "ct3337": "Tài khoản 3337 - Thuế nhà đất, tiền thuê đất",  # [cite: 47]
        "ct3338": "Tài khoản 3338 - Thuế bảo vệ môi trường và các loại thuế khác",  # [cite: 47]
        "ct33381": "Tài khoản 33381 - Thuế bảo vệ môi trường",  # [cite: 47]
        "ct33382": "Tài khoản 33382 - Các loại thuế khác",  # [cite: 47]
        "ct3339": "Tài khoản 3339 - Phí, lệ phí và các khoản phải nộp khác",  # [cite: 47]
        "ct334": "Tài khoản 334 - Phải trả người lao động",  # [cite: 47]
        "ct335": "Tài khoản 335 - Chi phí phải trả",  # [cite: 47]
        "ct336": "Tài khoản 336 - Phải trả nội bộ",  # [cite: 47]
        "ct3361": "Tài khoản 3361 - Phải trả nội bộ về vốn kinh doanh",  # [cite: 47]
        "ct3368": "Tài khoản 3368 - Phải trả nội bộ khác",  # [cite: 47]
        "ct338": "Tài khoản 338 - Phải trả, phải nộp khác",  # [cite: 47]
        "ct3381": "Tài khoản 3381 - Tài sản thừa chờ giải quyết",  # [cite: 47]
        "ct3382": "Tài khoản 3382 - Kinh phí công đoàn",  # [cite: 47]
        "ct3383": "Tài khoản 3383 - Bảo hiểm xã hội",  # [cite: 47]
        "ct3384": "Tài khoản 3384 - Bảo hiểm y tế",  # [cite: 47]
        "ct3385": "Tài khoản 3385 - Bảo hiểm thất nghiệp",  # [cite: 47]
        "ct3386": "Tài khoản 3386 - Nhận ký quỹ, ký cược",  # [cite: 47]
        "ct3387": "Tài khoản 3387 - Doanh thu chưa thực hiện",  # [cite: 47]
        "ct3388": "Tài khoản 3388 - Phải trả, phải nộp khác",  # [cite: 47]
        "ct341": "Tài khoản 341 - Vay và nợ thuê tài chính",  # [cite: 47]
        "ct3411": "Tài khoản 3411 - Các khoản đi vay",  # [cite: 47]
        "ct3412": "Tài khoản 3412 - Nợ thuê tài chính",  # [cite: 47]
        "ct352": "Tài khoản 352 - Dự phòng phải trả",  # [cite: 47]
        "ct3521": "Tài khoản 3521 - Dự phòng bảo hành sản phẩm hàng hóa",  # [cite: 47]
        "ct3522": "Tài khoản 3522 - Dự phòng bảo hành công trình xây dựng",  # [cite: 47]
        "ct3524": "Tài khoản 3524 - Dự phòng phải trả khác",  # [cite: 47]
        "ct353": "Tài khoản 353 - Quỹ khen thưởng, phúc lợi",  # [cite: 47]
        "ct3531": "Tài khoản 3531 - Quỹ khen thưởng",  # [cite: 47]
        "ct3532": "Tài khoản 3532 - Quỹ phúc lợi",  # [cite: 47]
        "ct3533": "Tài khoản 3533 - Quỹ phúc lợi đã hình thành TSCĐ",  # [cite: 47]
        "ct3534": "Tài khoản 3534 - Quỹ thưởng ban quản lý điều hành công ty",  # [cite: 47]
        "ct356": "Tài khoản 356 - Quỹ phát triển khoa học và công nghệ",  # [cite: 47]
        "ct3561": "Tài khoản 3561 - Quỹ phát triển khoa học và công nghệ",  # [cite: 47]
        "ct3562": "Tài khoản 3562 - Quỹ phát triển khoa học và công nghệ đã hình thành TSCĐ",  # [cite: 47]

        "ct411": "Tài khoản 411 - Vốn đầu tư của chủ sở hữu",  # [cite: 47]
        "ct4111": "Tài khoản 4111 - Vốn đầu tư của chủ sở hữu",  # [cite: 47]
        "ct4112": "Tài khoản 4112 - Thặng dư vốn cổ phần",  # [cite: 47]
        "ct4118": "Tài khoản 4118 - Vốn khác",  # [cite: 47]
        "ct413": "Tài khoản 413 - Chênh lệch tỷ giá hối đoái",  # [cite: 47]
        "ct418": "Tài khoản 418 - Các quỹ thuộc vốn chủ sở hữu",  # [cite: 47]
        "ct419": "Tài khoản 419 - Cổ phiếu quỹ",  # [cite: 47]
        "ct421": "Tài khoản 421 - Lợi nhuận sau thuế chưa phân phối",  # [cite: 47]
        "ct4211": "Tài khoản 4211 - Lợi nhuận chưa phân phối năm trước",  # [cite: 47]
        "ct4212": "Tài khoản 4212 - Lợi nhuận chưa phân phối năm nay",  # [cite: 47]

        "ct511": "Tài khoản 511 - Doanh thu bán hàng và cung cấp dịch vụ",  # [cite: 47]
        "ct5111": "Tài khoản 5111 - Doanh thu bán hàng hoá",  # [cite: 47]
        "ct5112": "Tài khoản 5112 - Doanh thu bán thành phẩm",  # [cite: 47]
        "ct5113": "Tài khoản 5113 - Doanh thu cung cấp dịch vụ",  # [cite: 47]
        "ct5118": "Tài khoản 5118 - Doanh thu khác",  # [cite: 47]
        "ct515": "Tài khoản 515 - Doanh thu hoạt động tài chính",  # [cite: 47]

        "ct611": "Tài khoản 611 - Mua hàng",  # [cite: 47]
        "ct631": "Tài khoản 631 - Giá thành sản xuất",  # [cite: 47]
        "ct632": "Tài khoản 632 - Giá vốn hàng bán",  # [cite: 47]
        "ct635": "Tài khoản 635 - Chi phí tài chính",  # [cite: 47]
        "ct642": "Tài khoản 642 - Chi phí quản lý kinh doanh",  # [cite: 47]
        "ct6421": "Tài khoản 6421 - Chi phí bán hàng",  # [cite: 47]
        "ct6422": "Tài khoản 6422 - Chi phí quản lý doanh nghiệp",  # [cite: 47]

        "ct711": "Tài khoản 711 - Thu nhập khác",  # [cite: 47]
        "ct811": "Tài khoản 811 - Chi phí khác",  # [cite: 47]
        "ct821": "Tài khoản 821 - Chi phí thuế thu nhập doanh nghiệp",  # [cite: 47]
        "ct911": "Tài khoản 911 - Xác định kết quả kinh doanh",  # [cite: 47]
        "tongCong": "Tổng cộng"  # [cite: 47]
    }
}
TU_DIEN_TO_KHAI["05/QTT_TNCN"] = {
    "ToKhaiChinh": {
        "NVuKhauTruThue_ct16": "Tổng số người lao động",
        "NVuKhauTruThue_ct17": "Trong đó: Cá nhân cư trú có hợp đồng lao động",
        "NVuKhauTruThue_ct18": "Tổng số cá nhân đã khấu trừ thuế [18]=[19]+[20]",
        "NVuKhauTruThue_ct19": "Cá nhân cư trú (Đã khấu trừ thuế)",
        "NVuKhauTruThue_ct20": "Cá nhân không cư trú (Đã khấu trừ thuế)",
        "NVuKhauTruThue_ct21": "Tổng số cá nhân thuộc diện miễn, giảm thuế theo Hiệp định",
        "NVuKhauTruThue_ct22": "Tổng số cá nhân giảm trừ gia cảnh",
        "NVuKhauTruThue_ct23": "Tổng thu nhập chịu thuế trả cho cá nhân [23]=[24]+[25]",
        "NVuKhauTruThue_ct24": "Cá nhân cư trú (TNCT)",
        "NVuKhauTruThue_ct25": "Cá nhân không cư trú (TNCT)",
        "NVuKhauTruThue_ct26": "Trong đó: Tổng TNCT từ phí mua bảo hiểm nhân thọ...",
        "NVuKhauTruThue_ct27": "Trong đó tổng TNCT được miễn theo Hợp đồng dầu khí",
        "NVuKhauTruThue_ct28": "Tổng TNCT trả cho cá nhân thuộc diện phải khấu trừ thuế",
        "NVuKhauTruThue_ct29": "Cá nhân cư trú (TNCT phải khấu trừ)",
        "NVuKhauTruThue_ct30": "Cá nhân không cư trú (TNCT phải khấu trừ)",
        "NVuKhauTruThue_ct31": "Tổng số thuế TNCN đã khấu trừ [31]=[32]+[33]",
        "NVuKhauTruThue_ct32": "Cá nhân cư trú (Thuế đã khấu trừ)",
        "NVuKhauTruThue_ct33": "Cá nhân không cư trú (Thuế đã khấu trừ)",
        "NVuKhauTruThue_ct34": "Trong đó: Tổng số thuế TNCN đã khấu trừ trên tiền phí mua BHNT",

        "NVuQToanThay_ct35": "Tổng số cá nhân uỷ quyền quyết toán thay",
        "NVuQToanThay_ct36": "Tổng số thuế TNCN đã khấu trừ (Quyết toán thay)",
        "NVuQToanThay_ct37": "Trong đó: Số thuế TNCN đã khấu trừ tại tổ chức trước khi điều chuyển",
        "NVuQToanThay_ct38": "Tổng số thuế TNCN phải nộp",
        "NVuQToanThay_ct39": "Tổng số thuế TNCN được miễn (do còn phải nộp <= 50.000đ)",
        "NVuQToanThay_ct40": "Tổng số thuế TNCN còn phải nộp",
        "NVuQToanThay_ct41": "Tổng số thuế TNCN đã nộp thừa"
    },

    "PL 05-1": {
        "ct07": "Họ và tên",
        "ct08": "Mã số thuế",
        "ct09a_ten": "Loại giấy tờ",
        "ct09": "Số CMND/CCCD/SĐDCN Hộ chiếu",
        "ct10": "Cá nhân uỷ quyền quyết toán thay",
        "ct11": "CN nước ngoài ủy quyền quyết toán dưới 12 tháng",
        "ct12": "Tổng thu nhập chịu thuế",
        "ct13": "TNCT tại tổ chức trước khi điều chuyển",
        "ct14": "Trong đó: thu nhập chịu thuế được miễn theo Hiệp định",
        "ct15": "Trong đó: thu nhập chịu thuế được miễn theo Hợp đồng dầu khí",
        "ct15.1": "Thu nhập miễn thuế TNCN theo các Nghị quyết",
        "ct16": "Số lượng NPT tính giảm trừ",
        "ct17": "Tổng số tiền giảm trừ gia cảnh",
        "ct18": "Từ thiện, nhân đạo, khuyến học",
        "ct19": "Bảo hiểm được trừ",
        "ct20": "Quỹ hưu trí tự nguyện được trừ",
        "ct21": "Thu nhập tính thuế",
        "ct22": "Tổng số thuế TNCN đã khấu trừ",
        "ct23": "Trong đó: số thuế đã khấu trừ tại tổ chức trước khi điều chuyển",
        "ct24": "Tổng số thuế phải nộp",
        "ct25": "Số thuế đã nộp thừa",
        "ct26": "Số thuế còn phải nộp",
        "ct27": "Cá nhân có số thuế được miễn do có số thuế còn phải nộp <= 50.000đ",

        # --- Các chỉ tiêu của dòng TỔNG CỘNG ---
        "ct28": "Tổng thu nhập chịu thuế",
        "ct29": "TNCT tại tổ chức trước khi điều chuyển",
        "ct30": "Trong đó: thu nhập chịu thuế được miễn theo Hiệp định",
        "ct31": "Trong đó: thu nhập chịu thuế được miễn theo Hợp đồng dầu khí",
        "ct31.1": "Thu nhập miễn thuế TNCN theo các Nghị quyết",
        "ct32": "Số lượng NPT tính giảm trừ",
        "ct33": "Tổng số tiền giảm trừ gia cảnh",
        "ct34": "Từ thiện, nhân đạo, khuyến học",
        "ct35": "Bảo hiểm được trừ",
        "ct36": "Quỹ hưu trí tự nguyện được trừ",
        "ct37": "Thu nhập tính thuế",
        "ct38": "Tổng số thuế TNCN đã khấu trừ",
        "ct39": "Trong đó: số thuế đã khấu trừ tại tổ chức trước khi điều chuyển",
        "ct40": "Tổng số thuế phải nộp",
        "ct41": "Số thuế đã nộp thừa",
        "ct42": "Số thuế còn phải nộp",
        "ct43": "Cá nhân có số thuế được miễn do có số thuế còn phải nộp <= 50.000đ"
    },

    "PL 05-2": {
        "ct07": "Họ và tên",
        "ct08": "Mã số thuế",
        "ct09a_ten": "Loại giấy tờ",
        "ct09": "Số CMND/CCCD/Hộ chiếu",
        "ct10": "Cá nhân không cư trú",
        "ct11": "Tổng số (Thu nhập chịu thuế)",
        "ct12": "Trong đó: TNCT từ phí mua BH nhân thọ...",
        "ct13": "Trong đó thu nhập chịu thuế được miễn theo Hiệp định",
        "ct14": "Trong đó TN chịu thuế được miễn theo Hợp đồng dầu khí",
        "ct14.1": "Thu nhập miễn thuế TNCN theo các Nghị quyết",
        "ct15": "Tổng số (Số thuế TNCN đã khấu trừ)",
        "ct16": "Trong đó: Số thuế từ phí mua BH nhân thọ...",

        # --- Các chỉ tiêu của dòng TỔNG CỘNG ---
        "ct17": "Tổng số (Thu nhập chịu thuế)",
        "ct18": "Trong đó: TNCT từ phí mua BH nhân thọ...",
        "ct19": "Trong đó thu nhập chịu thuế được miễn theo Hiệp định",
        "ct20": "Trong đó TN chịu thuế được miễn theo Hợp đồng dầu khí",
        "ct20.1": "Thu nhập miễn thuế TNCN theo các Nghị quyết",
        "ct21": "Tổng số (Số thuế TNCN đã khấu trừ)",
        "ct22": "Trong đó: Số thuế từ phí mua BH nhân thọ..."
    },

    "PL 05-3": {
        "ct07": "Họ và tên NNT là người lao động",
        "ct08": "MST của NNT",
        "ct09": "Họ và tên người phụ thuộc",
        "ct10": "Ngày sinh người phụ thuộc",
        "ct11": "MST của người phụ thuộc",
        "ct12_ten": "Loại giấy tờ NPT",
        "ct13": "Số giấy tờ",
        "ct14_ten": "Quan hệ với người nộp thuế",
        "ct15": "Từ tháng (Giảm trừ)",
        "ct16": "Đến tháng (Giảm trừ)"
    }
}
TU_DIEN_TO_KHAI["05/KK_TNCN"] = {
    "ToKhaiChinh": {
        "ct16": "Tổng số người lao động", #[cite: 28, 29]
        "ct17": "Trong đó: Cá nhân cư trú có hợp đồng lao động", #[cite: 28, 29]
        "ct18": "Tổng số cá nhân đã khấu trừ thuế [18]=[19]+[20]", #[cite: 28, 29]
        "ct19": "Cá nhân cư trú (Đã khấu trừ)", #[cite: 28, 29]
        "ct20": "Cá nhân không cư trú (Đã khấu trừ)", #[cite: 28, 29]
        "ct21": "Tổng thu nhập chịu thuế (TNCT) trả cho cá nhân [21]=[22]+[23]", #[cite: 28, 29]
        "ct22": "Cá nhân cư trú (TNCT)", #[cite: 28, 29]
        "ct23": "Cá nhân không cư trú (TNCT)", #[cite: 28, 29]
        "ct24": "Trong đó: Tổng TNCT từ phí mua BHNT, BH không bắt buộc...", #[cite: 28, 29]
        "ct25": "Trong đó: Tổng TNCT được miễn theo quy định của Hợp đồng dầu khí", #[cite: 28, 29]
        "ct26": "Tổng thu nhập chịu thuế trả cho cá nhân thuộc diện phải khấu trừ thuế [26]=[27]+[28]", #[cite: 28, 29]
        "ct27": "Cá nhân cư trú (TNCT phải khấu trừ)", #[cite: 28, 29]
        "ct28": "Cá nhân không cư trú (TNCT phải khấu trừ)", #[cite: 28, 29]
        "ct29": "Tổng số thuế TNCN đã khấu trừ [29]=[30]+[31]", #[cite: 28, 29]
        "ct30": "Cá nhân cư trú (Thuế đã khấu trừ)", #[cite: 28, 29]
        "ct31": "Cá nhân không cư trú (Thuế đã khấu trừ)", #[cite: 28, 29]
        "ct32": "Trong đó: Tổng thuế TNCN đã khấu trừ trên tiền phí mua BHNT..." #[cite: 28, 29]
    }
}
TU_DIEN_TO_KHAI["TAIN"] = {
    "ChiTieuChinh": {
        "tongSanLuong": "Tổng sản lượng tài nguyên tính thuế",  # [cite: 25, 26]
        "tongThuePhaiNop": "Tổng thuế tài nguyên phải nộp",  # [cite: 25, 26]
        "tongThueDaKhai": "Tổng thuế tài nguyên đã kê khai trong năm",  # [cite: 26]
        "tongChenhLech": "Tổng chênh lệch"  # [cite: 26]
    },
    "BangKe": {
        # Các cột chung của Tờ khai 01/TAIN và 02/TAIN
        "ten_moKhoangSan": "Tên mỏ khoáng sản",  # [cite: 25, 26]
        "ct2_tenKhoangSan": "(2) Tên loại tài nguyên",  # [cite: 25, 26]
        "ct2_tenTaiNguyen": "(2) Tên loại tài nguyên",  # [cite: 25, 26]
        "ct3": "(3) Đơn vị tính",  # [cite: 25, 26]
        "ct4": "(4) Sản lượng",  # [cite: 25, 26]
        "ct5": "(5) Giá tính thuế đơn vị",  # [cite: 25, 26]
        "ct6": "(6) Thuế suất (%)",  # [cite: 25, 26]
        "ct7": "(7) Mức thuế ấn định",  # [cite: 25, 26]
        "ct8": "(8) Thuế phải nộp",  # [cite: 25, 26]
        "ct9": "(9) Thuế đã kê khai",  # [cite: 26]
        "ct10": "(10) Chênh lệch",  # [cite: 26]

        # Các cột của Phụ lục 01-1/TAIN
        "ten_nhaMay": "[05] Tên nhà máy thủy điện",  # [cite: 27]
        "ma_nhaMay": "[06] Mã nhà máy / Mã số thuế",  # [cite: 27]
        "ct05": "[05] Đơn vị phụ thuộc/Địa điểm",  # [cite: 27]
        "ct06": "[06] Mã số thuế / Mã địa điểm KD",  # [cite: 27]
        "ten_xa": "[07] Xã/phường/đặc khu",  # [cite: 27]
        "ct08_tinh_ten": "[08] Tỉnh",  # [cite: 27]
        "ct09_cqt_ten": "[09] Cơ quan thuế quản lý",  # [cite: 27]
        "ct10_a": "[10] Thuế TN phải nộp của nhà máy",  # [cite: 27]
        "ct11_a": "[11] Tỷ lệ phân bổ (%)",  # [cite: 27]
        "ct12_a": "[12] Thuế phải nộp cho từng tỉnh",  # [cite: 27]
        "ct10": "[10] Thuế TN phải nộp của nhà máy",  # [cite: 27]
        "ct11": "[11] Tỷ lệ phân bổ (%)",  # [cite: 27]
        "ct12": "[12] Thuế phải nộp cho từng tỉnh"  # [cite: 27]
    }
}
TU_DIEN_TO_KHAI["04/TNDN"] = {
    "ToKhaiChinh": {
        "ct11": "1. Doanh thu tính thuế thu nhập doanh nghiệp", #[cite: 30]
        "ct12": "1.1 Hoạt động dịch vụ", #[cite: 30]
        "ct13": "1.2 Hoạt động kinh doanh hàng hóa", #[cite: 30]
        "ct14": "1.3 Hoạt động khác", #[cite: 30]
        "ct15": "2. Tỷ lệ tính thuế TNDN", #[cite: 30]
        "ct16": "2.1 Hoạt động dịch vụ", #[cite: 30]
        "ct17": "2.2 Hoạt động kinh doanh hàng hóa", #[cite: 30]
        "ct18": "2.3 Hoạt động khác", #[cite: 30]
        "ct19": "3. Số thuế TNDN phải nộp [19]=[12]x[16]+[13]x[17]+[14]x[18]", #[cite: 30]
        "ct20": "4. Số thuế TNDN được miễn, giảm", #[cite: 30]
        "ct21": "5. Số thuế TNDN phải nộp sau miễn, giảm ([21]=[19]-[20])", #[cite: 30]
        "ct22": "6. Số thuế TNDN nộp thừa kỳ trước chuyển sang kỳ này (nếu có)", #[cite: 30]
        "ct23": "7. Số thuế TNDN đã tạm nộp trong năm đến thời điểm quyết toán", #[cite: 30]
        "ct24": "8. Chênh lệch giữa số thuế phải nộp và số thuế đã tạm nộp trong năm ([24]=[21]-[23])", #[cite: 30]
        "ct25": "9. Số thuế TNDN còn phải nộp sau quyết toán ([25]=[21]-[22]-[23])" #[cite: 30]
    }
}