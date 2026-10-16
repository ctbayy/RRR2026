import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextBrowser, QListWidget, QSplitter
from PySide6.QtCore import Qt


class WidgetHuongDanSuDung(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Tạo thư mục chứa ảnh nếu chưa có
        self.thu_muc_anh = os.path.join(os.getcwd(), "Data", "Images")
        os.makedirs(self.thu_muc_anh, exist_ok=True)
        self.path_img = f"file:///{self.thu_muc_anh.replace(chr(92), '/')}/"

        self.thiet_lap_ui()
        self.nap_du_lieu_docs()

    def thiet_lap_ui(self):
        layout_chinh = QHBoxLayout(self)
        layout_chinh.setContentsMargins(10, 10, 10, 10)

        # Dùng QSplitter để có thể kéo thả độ rộng giữa Menu và Nội dung
        bo_chia = QSplitter(Qt.Horizontal)

        # 1. MENU DANH MỤC BÊN TRÁI
        self.menu_docs = QListWidget()
        self.menu_docs.setMinimumWidth(220)
        self.menu_docs.setMaximumWidth(300)
        self.menu_docs.setStyleSheet("""
            QListWidget {
                background-color: #F8FAFC; border: 1px solid #E5E7EB; border-radius: 8px;
                outline: none; padding: 10px 5px; font-size: 14px; font-weight: 500; color: #334155;
            }
            QListWidget::item { padding: 12px 10px; border-radius: 6px; margin-bottom: 2px; }
            QListWidget::item:hover { background-color: #E2E8F0; }
            QListWidget::item:selected { background-color: #DBEAFE; color: #1D4ED8; font-weight: bold; border-left: 4px solid #2563EB; }
        """)

        danh_muc = [
            "0. Tổng quan Luồng xử lý",
            "1. Cách Nạp Dữ Liệu (XML, HĐ)",
            "2. Cấu hình & Đồng bộ TMS",
            "3. Quản lý Công thức & Rules",
            "4. Rà soát Hóa đơn Rủi ro",
            "5. Đối chiếu Chuỗi Cung ứng",
            "6. Kết xuất Phiếu & Báo cáo"
        ]
        self.menu_docs.addItems(danh_muc)
        self.menu_docs.setCurrentRow(0)

        # 2. KHUNG NỘI DUNG BÊN PHẢI
        self.khung_hien_thi = QTextBrowser()
        self.khung_hien_thi.setOpenExternalLinks(True)
        self.khung_hien_thi.setStyleSheet("""
            QTextBrowser {
                background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px;
                padding: 30px; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14.5px; color: #1F2937; line-height: 1.6;
            }
            h2 { color: #1E3A8A; font-size: 22px; margin-top: 0; border-bottom: 2px solid #BFDBFE; padding-bottom: 8px; }
            h3 { color: #059669; font-size: 18px; margin-top: 20px; }
            p { margin-bottom: 15px; }
            ul { margin-top: 5px; margin-bottom: 15px; }
            li { margin-bottom: 10px; }
            b { color: #111827; }
            .highlight { background-color: #FEF3C7; padding: 2px 6px; border-radius: 4px; color: #B45309; font-weight: bold; }
            .box-note { background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 12px; margin-top: 15px; }
        """)

        bo_chia.addWidget(self.menu_docs)
        bo_chia.addWidget(self.khung_hien_thi)
        bo_chia.setSizes([250, 950])
        layout_chinh.addWidget(bo_chia)

        # Kết nối sự kiện khi bấm menu thì đổi nội dung
        self.menu_docs.currentRowChanged.connect(self.cap_nhat_noi_dung)

    def nap_du_lieu_docs(self):
        # Thiết kế HTML cho từng Tab riêng biệt (Đã tích hợp 6 Slot chờ ảnh)
        self.noi_dung_html = [
            # 0. TỔNG QUAN
            f"""
            <h2>0. SƠ ĐỒ LUỒNG THAO TÁC (WORKFLOW)</h2>
            <p>Hệ thống được thiết kế theo quy trình 4 bước tự động hóa khép kín:</p>
            <ul>
                <li><b>BƯỚC 1: Chuẩn bị dữ liệu:</b> Upload Tờ khai XML, Hóa đơn mua vào/bán ra (Excel) và Bảng CĐSPS theo mẫu excel (đối với TT200/TT99).</li>
                <li><b>BƯỚC 2: Thiết lập Cấu hình & Rule:</b> Chọn các quy tắc rủi ro muốn quét, thiết lập tài khoản TMS.</li>
                <li><b>BƯỚC 3: Phân tích:</b> Nhấn <span class="highlight">PHÂN TÍCH HỒ SƠ</span>. Bot sẽ chạy ngầm để lấy ngày nộp thực tế và quét trạng thái NNT.</li>
                <li><b>BƯỚC 4: Kết xuất Báo cáo:</b> Đọc kết quả chi tiết từng rủi ro, kết xuất Excel hoặc tạo Phiếu Nhận Xét.</li>
            </ul>
            <br>
            <p><i>Mẹo: Hãy bấm vào các mục bên trái để xem hướng dẫn chi tiết cho từng chức năng.</i></p>
            """,

            # 1. NẠP DỮ LIỆU
            f"""
            <h2>1. HƯỚNG DẪN UPLOAD DỮ LIỆU ĐẦU VÀO</h2>
            <h3>A. Tải Tờ khai XML</h3>
            <p>Tại Tab <b>Chuẩn bị dữ liệu</b>, nhấn nút <span class="highlight">Tờ khai XML</span>. Bạn có thể chọn hàng chục file XML cùng lúc. Hệ thống tự động đọc, phân biệt Tờ khai chính thức và Bổ sung.</p>

            <h3>B. Tải Hóa đơn (Excel/CSV) & CĐSPS</h3>
            <p>Nhấn nút <span class="highlight">HĐ Bán ra</span> hoặc <span class="highlight">HĐ Mua vào</span> để tải dữ liệu. Nếu chưa có form chuẩn, hãy click nút <b>Kho File Mẫu</b> để tải biểu mẫu.</p>
            <br>
            <div style="border: 2px dashed #94A3B8; padding: 10px; text-align: center;">
                <img src="{self.path_img}step1_nap_file.png" width="800" alt="[SLOT CHỜ ẢNH 1: Chép file 'step1_nap_file.png' vào thư mục Data/Images]">
            </div>
            """,

            # 2. CẤU HÌNH TMS
            f"""
            <h2>2. CẤU HÌNH VÀ ĐỒNG BỘ TMS</h2>
            <p>Tính năng tự động giúp ứng dụng tự động mở TMS, điền mật khẩu và kết xuất dữ liệu.</p>

            <h3>Cách thiết lập lần đầu:</h3>
            <ol>
                <li>Tick chọn mục <b>Đồng bộ ngày nộp Tờ khai</b> hoặc <b>Tra cứu trạng thái HĐ doanh nghiệp</b>.</li>
                <li>Nhấn nút <span class="highlight">Cấu hình SAP</span>.</li>
                <li>Điền Mã Cơ quan thuế, Tên đăng nhập và Mật khẩu.</li>
            </ol>
            <br>
            <div style="border: 2px dashed #94A3B8; padding: 10px; text-align: center;">
                <img src="{self.path_img}step2_cau_hinh.png" width="800" alt="[SLOT CHỜ ẢNH 2: Chép file 'step2_cau_hinh.png' vào thư mục Data/Images]">
            </div>
            """,

            # 3. QUẢN LÝ CÔNG THỨC
            f"""
            <h2>3. QUẢN LÝ CÔNG THỨC VÀ BỘ QUY TẮC (RULES)</h2>

            <h3>A. Tạo và Sửa Công thức phân tích</h3>
            <p>Nhấn nút <span class="highlight">Quản lý Công thức</span>. Bạn có thể viết công thức Toán học bằng các Mã Chỉ Tiêu (Ví dụ: <code>[01/GTGT_32] + [01/GTGT_33]</code>) và thiết lập ngưỡng rủi ro.</p>

            <h3>B. Chọn Công thức chạy</h3>
            <p>Nhấn nút <span class="highlight">Chọn Công thức chạy</span> để mở bảng lọc. Bỏ tick những Công thức không cần thiết. Tích chọn "Lưu cấu hình làm mặc định" nếu muốn giữ nguyên cho lần sau.</p>
            <br>
            <div style="border: 2px dashed #94A3B8; padding: 10px; text-align: center;">
                <img src="{self.path_img}step3_quan_ly_rule.png" width="900" alt="[SLOT CHỜ ẢNH 3: Chép file 'step3_quan_ly_rule.png' vào thư mục Data/Images]"><br><br>
                <img src="{self.path_img}step3_quan_ly_rule 2.png" width="900" alt="[SLOT CHỜ ẢNH 3: Chép file 'step3_quan_ly_rule.png' vào thư mục Data/Images]"><br><br>
                <img src="{self.path_img}step3_quan_ly_rule 3.png" width="900" alt="[SLOT CHỜ ẢNH 3: Chép file 'step3_quan_ly_rule.png' vào thư mục Data/Images]">
            </div>
            """,

            # 4. HÓA ĐƠN RỦI RO
            f"""
            <h2>4. RÀ SOÁT HÓA ĐƠN RỦI RO</h2>
            <p>Khi tải Hóa đơn, RRR sẽ lập tức quét đối chiếu với dữ liệu rủi ro nội bộ và kết quả từ TMS.</p>
            <ul>
                <li><b>Trạng thái TMS Bất thường:</b> Doanh nghiệp "Không hoạt động tại địa chỉ" bị bôi nền đỏ. Doanh nghiệp "Ngừng hoạt động" bị bôi nền vàng.</li>
                <li><b>Hóa đơn từ Cảnh báo rủi ro:</b> Bị bóc tách và đẩy sang riêng <b>Tab Hóa đơn Rủi ro</b>.</li>
            </ul>
            <br>
            <div style="border: 2px dashed #94A3B8; padding: 10px; text-align: center;">
                <img src="{self.path_img}step4_hoa_don_rui_ro.png" width="900" alt="[SLOT CHỜ ẢNH 4: Chép file 'step4_hoa_don_rui_ro.png' vào thư mục Data/Images]">
            </div>
            """,

            # 5. CHUỖI CUNG ỨNG
            f"""
            <h2>5. ĐỐI CHIẾU CHUỖI CUNG ỨNG & TỒN KHO</h2>

            <h3>A. Phân tích Chuỗi Cung ứng</h3>
            <p>Nhấn nút <span class="highlight">Cấu hình Chuỗi cung ứng</span>. Khai báo định mức nguyên vật liệu đầu vào so với thành phẩm đầu ra để phát hiện mua khống.</p>

            <h3>B. Đối chiếu Tên mặt hàng bằng AI</h3>
            <p>Thuật toán NLP tự động ghép nối Tên hàng hóa mua vào và bán ra để phát hiện rủi ro.</p>
            <br>
            <div style="border: 2px dashed #94A3B8; padding: 10px; text-align: center;">
                <img src="{self.path_img}step5_chuoi_cung_ung.png" width="900" alt="[SLOT CHỜ ẢNH 5: Chép file 'step5_chuoi_cung_ung.png' vào thư mục Data/Images]">
            </div>
            """,

            # 6. XUẤT BÁO CÁO
            f"""
            <h2>6. KẾT XUẤT PHIẾU VÀ BÁO CÁO</h2>
            <p>Mọi kết quả tinh túy nhất đều nằm ở Tab <b>Kết quả Phân tích</b>.</p>

            <h3>Kết xuất Excel</h3>
            <p>Nhấn nút <span class="highlight">Kết xuất Excel</span> góc trên cùng bên phải. Hệ thống bóc tách toàn bộ dữ liệu đối chiếu và cảnh báo rủi ro ra một tệp Excel nhiều Sheet.</p>

            <h3>Soạn thảo Phiếu nhận xét tự động</h3>
            <p>Nhấn nút <span class="highlight">Tạo Phiếu Nhận Xét (Word)</span>. Hệ thống thu thập Tên công ty, MST, Địa chỉ, Danh sách rủi ro và xuất thẳng ra file Word chuẩn quy trình.</p>
            <br>
            <div style="border: 2px dashed #94A3B8; padding: 10px; text-align: center;">
                <img src="{self.path_img}step6_xuat_bao_cao.png" width="900" alt="[SLOT CHỜ ẢNH 6: Chép file 'step6_xuat_bao_cao.png' vào thư mục Data/Images]">
            </div>
            """
        ]
        # Khởi tạo mặc định
        self.khung_hien_thi.setHtml(self.noi_dung_html[0])

    def cap_nhat_noi_dung(self, index):
        """Hàm kích hoạt khi NSD bấm vào menu bên trái"""
        if 0 <= index < len(self.noi_dung_html):
            self.khung_hien_thi.setHtml(self.noi_dung_html[index])