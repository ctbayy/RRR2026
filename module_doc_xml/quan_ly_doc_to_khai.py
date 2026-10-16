import xml.etree.ElementTree as ET
from module_doc_xml import to_khai_01_gtgt
from module_doc_xml import to_khai_02_gtgt
from module_doc_xml import to_khai_04_gtgt  # Bổ sung import module 04/GTGT
from module_doc_xml import to_khai_03_tndn # Bổ sung import module 03/TNDN
from module_doc_xml import to_khai_bctc_tt200 # Import module mới
from module_doc_xml import to_khai_bctc_tt133 # Import thêm module 133
from module_doc_xml import to_khai_05_qtt_tncn
from module_doc_xml import to_khai_05_kk_tncn # Import module 05/KK
from module_doc_xml import to_khai_tain # Nạp module TAIN
from module_doc_xml import to_khai_04_tndn # Import module 04/TNDN

class QuanLyDocToKhaiXML:
    def __init__(self):
        pass

    def xac_dinh_loai_to_khai(self, duong_dan_file):
        """Đọc lướt file XML để lấy mã tờ khai"""
        try:
            tree = ET.parse(duong_dan_file)
            root = tree.getroot()
            for elem in root.iter():
                if elem.tag.endswith('maTKhai'):
                    return elem.text
        except Exception:
            return None
        return None

    def xu_ly_file_xml(self, duong_dan_file):
        """
        Hàm thực thi trong luồng nền.
        Định tuyến xử lý dựa trên mã tờ khai.
        """
        ma_to_khai = self.xac_dinh_loai_to_khai(duong_dan_file)

        # 842: Mã của tờ khai 01/GTGT TT80
        if ma_to_khai == "842":
            return to_khai_01_gtgt.phan_tich_xml(duong_dan_file)
        elif ma_to_khai == "01":
            return to_khai_01_gtgt.phan_tich_xml(duong_dan_file)
        # 844: Mã của tờ khai 02/GTGT TT80
        elif ma_to_khai in ["02", "844"]:
            return to_khai_02_gtgt.phan_tich_xml(duong_dan_file)

        # 847: Mã của tờ khai 04/GTGT TT80
        elif ma_to_khai == "847":
            return to_khai_04_gtgt.phan_tich_xml(duong_dan_file)
        # 892: Mã của tờ khai Quyết toán 03/TNDN
        elif ma_to_khai in ["03", "892"]:
            return to_khai_03_tndn.phan_tich_xml(duong_dan_file)
        # 402: Mã của Báo cáo tài chính theo Thông tư 200
        elif ma_to_khai == "402":
            return to_khai_bctc_tt200.phan_tich_xml(duong_dan_file)
        # Định tuyến cho BCTC TT133 (Mã 683)
        elif ma_to_khai in ["683","684","685","686","699"]:
            return to_khai_bctc_tt133.phan_tich_xml(duong_dan_file)
        elif ma_to_khai == "953":
            return to_khai_05_qtt_tncn.phan_tich_xml(duong_dan_file)
        elif ma_to_khai == "864":
            return to_khai_05_kk_tncn.phan_tich_xml(duong_dan_file)
        elif ma_to_khai in ["832", "924"]:
            return to_khai_tain.phan_tich_xml(duong_dan_file)
        elif ma_to_khai == "833":
            return to_khai_04_tndn.phan_tich_xml(duong_dan_file)
        elif ma_to_khai is None:
            raise ValueError("Không thể đọc định dạng file XML này hoặc file bị hỏng.")
        else:
            raise NotImplementedError(f"Hệ thống chưa hỗ trợ module đọc mã tờ khai: {ma_to_khai}")