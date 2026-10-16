# app/analysis/khbs_parser.py
import xml.etree.ElementTree as ET
import pandas as pd
import os
#from analysis.xml_parser import get_declaration_metadata
from module_doc_xml.xml_parser import get_declaration_metadata

# TỪ ĐIỂN MAPPING 01/GTGT
GTGT_01_INDICATOR_NAMES = {
    'ct22': 'Thuế GTGT còn được khấu trừ kỳ trước chuyển sang',
    'ct23': 'Giá trị của hàng hóa, dịch vụ mua vào',
    'ct24': 'Thuế GTGT của hàng hóa, dịch vụ mua vào',
    'ct25': 'Tổng số thuế GTGT được khấu trừ',
    'ct26': 'Hàng hóa, dịch vụ bán ra không chịu thuế GTGT',
    'ct27': 'Giá trị HHDV bán ra chịu thuế GTGT (ct27=29+30+32+32a)',
    'ct28': 'Thuế GTGT của HHDV bán ra (ct28=31+33)',
    'ct29': 'Hàng hóa, dịch vụ bán ra chịu thuế suất 0%',
    'ct30': 'Hàng hóa, dịch vụ bán ra chịu thuế suất 5%',
    'ct31': 'Thuế GTGT của HHDV bán ra chịu thuế suất 5%',
    'ct32': 'Hàng hóa, dịch vụ bán ra chịu thuế suất 10%',
    'ct33': 'Thuế GTGT của HHDV bán ra chịu thuế suất 10%',
    'ct32a': 'Hàng hóa, dịch vụ bán ra không tính thuế',
    'ct34': 'Tổng doanh thu của HHDV bán ra',
    'ct35': 'Tổng số thuế GTGT của HHDV bán ra',
    'ct36': 'Thuế GTGT phát sinh trong kỳ',
    'ct37': 'Điều chỉnh giảm thuế GTGT còn được khấu trừ',
    'ct38': 'Điều chỉnh tăng thuế GTGT còn được khấu trừ',
    'ct39': 'Thuế GTGT đã nộp ở địa phương khác',
    'ct40': 'Thuế GTGT còn phải nộp trong kỳ',
    'ct41': 'Thuế GTGT chưa khấu trừ hết kỳ này',
    'ct42': 'Thuế GTGT đề nghị hoàn',
    'ct43': 'Thuế GTGT còn được khấu trừ chuyển kỳ sau'
}

# TỪ ĐIỂN MAPPING 02/GTGT
GTGT_02_INDICATOR_NAMES = {
    'ct21': 'Thuế GTGT chưa được hoàn kỳ trước chuyển sang',
    'ct21a': 'Thuế GTGT đầu vào của dự án đầu tư nhận bàn giao',
    'ct22': 'Thuế GTGT của HHDV mua vào cho dự án đầu tư',
    'ct22a': 'Trong đó: giá trị HHDV nhập khẩu',
    'ct23': 'Thuế GTGT của hàng hóa, dịch vụ mua vào',
    'ct23a': 'Trong đó: thuế GTGT HHDV nhập khẩu',
    'ct24': 'Điều chỉnh tăng giá trị của HHDV mua vào các kỳ trước',
    'ct25': 'Điều chỉnh tăng thuế GTGT của HHDV mua vào các kỳ trước',
    'ct26': 'Điều chỉnh giảm giá trị của HHDV mua vào các kỳ trước',
    'ct27': 'Điều chỉnh giảm thuế GTGT của HHDV mua vào các kỳ trước',
    'ct28': 'Tổng thuế GTGT đầu vào của HHDV mua vào',
    'ct28a': 'Bù trừ với thuế phải nộp của hoạt động SXKD cùng tỉnh/TP',
    'ct29': 'Thuế GTGT đầu vào chưa được hoàn chuyển sang kỳ sau',
    'ct30': 'Số thuế GTGT đề nghị hoàn',
    'ct31': 'Thuế GTGT đầu vào của DAĐT bàn giao cho DN mới thành lập',
    'ct31a': 'Thuế GTGT đầu vào của DAĐT chuyển đi hoặc đã đi vào hoạt động',
    'ct32': 'Thuế GTGT đầu vào của DAĐT chưa được hoàn chuyển kỳ sau',
}


class KHBSParser:
    def parse_file(self, file_path):
        meta_info = get_declaration_metadata(file_path)
        if not meta_info: return None

        current_loai_tk = meta_info.get('loai_tk', 'Khác')
        so_lan = meta_info.get('so_lan', 0)

        try:
            tree = ET.parse(file_path)
            data_rows = []

            # TÚI CHỨA DỮ LIỆU TỜ KHAI CHÍNH (Đọc 1 lần lưu vào RAM)
            main_values = {}

            kieu_ky = 'M'
            ky_kkhai = meta_info.get('ky_kk', '')

            # VÉT SẠCH DỮ LIỆU TRONG 1 LẦN QUÉT
            for elem in tree.iter():
                tag = elem.tag.split('}', 1)[-1]
                if tag == 'kieuKy' and elem.text:
                    kieu_ky = elem.text.strip()
                elif tag == 'kyKKhai' and elem.text:
                    ky_kkhai = elem.text.strip()
                elif tag.startswith('ct') and elem.text:
                    # Chỉ lấy giá trị xuất hiện ĐẦU TIÊN (thuộc Tờ khai chính phía trên)
                    # Bỏ qua các thẻ ct trùng tên nằm lồng trong Phụ lục KHBS phía dưới
                    if tag not in main_values:
                        try:
                            main_values[tag] = float(elem.text)
                        except ValueError:
                            pass

            if kieu_ky == 'Q':
                ky_tinh_thue_chuan = f"Q{ky_kkhai}" if not ky_kkhai.startswith('Q') else ky_kkhai
            else:
                ky_tinh_thue_chuan = ky_kkhai

            if so_lan == 0:
                data_rows = self._parse_official_return(tree, current_loai_tk)
            else:
                data_rows = self._parse_supplementary_return(tree, current_loai_tk)

            final_meta = {
                'loai_tk_xml': current_loai_tk,
                'loai_tk_type': 'C' if so_lan == 0 else 'B',
                'lan_bs': so_lan,
                'ky_tinh_thue': ky_tinh_thue_chuan,
                'kieu_ky': kieu_ky,
                'ngay_lap': meta_info.get('ngay_lap', ''),
                'ma_tk': str(meta_info.get('ma_tk', '')),
                'file_path': file_path
            }

            # NÉM CẢ main_values RA NGOÀI CHO GIAO DIỆN SỬ DỤNG
            return {'meta': final_meta, 'df': pd.DataFrame(data_rows), 'main_values': main_values}

        except Exception as e:
            print(f"LỖI KHBS PARSER: {str(e)}")
            return None


    def _get_mapping(self, loai_tk):
        """Trả về đúng từ điển dựa vào loại tờ khai"""
        if '02/GTGT' in loai_tk:
            return GTGT_02_INDICATOR_NAMES
        return GTGT_01_INDICATOR_NAMES  # Mặc định

    def _parse_official_return(self, tree, loai_tk):
        rows = []
        mapping = self._get_mapping(loai_tk)

        for elem in tree.iter():
            tag = elem.tag.split('}', 1)[-1]
            val = elem.text.strip() if elem.text else "0"

            if tag in mapping:
                try:
                    gia_tri = float(val) if val else 0.0
                    ten_chi_tieu = mapping[tag]
                    rows.append({
                        'ma_so': tag,
                        'noi_dung': ten_chi_tieu,
                        'gia_tri': gia_tri
                    })
                except:
                    pass
        return rows

    def _parse_supplementary_return(self, tree, loai_tk):
        rows = []
        mapping = self._get_mapping(loai_tk)
        parent_map = {c: p for p in tree.iter() for c in p}

        is_tt80 = any(elem.tag.split('}', 1)[-1] == 'ct3_ma' for elem in tree.iter())

        # [TRACKING 2] Kiểm tra chuẩn XML
        print(f"  -> Bộ đọc Phụ lục BS: Kích hoạt chuẩn TT80 = {is_tt80}")

        for elem in tree.iter():
            tag = elem.tag.split('}', 1)[-1]

            if is_tt80:
                if tag == 'ct3_ma' and elem.text:
                    if self._is_inside_khbs(elem, parent_map):
                        parent = parent_map.get(elem)
                        if parent:
                            row_data = self._extract_row_data_tt80(parent)
                            clean_ma = elem.text.strip().replace('[', 'ct').replace(']', '')

                            # [TRACKING 3] Theo dõi chi tiết từng chỉ tiêu bên trong Phụ lục BS
                            print(f"    + Quét thấy Chỉ tiêu: {clean_ma}")
                            print(
                                f"      - Đã kê khai: {row_data['so_da_ke_khai']} | Kê khai đúng: {row_data['so_ke_khai_dung']} | Chênh lệch: {row_data['so_dieu_chinh']}")

                            noi_dung = row_data['noi_dung'] or mapping.get(clean_ma, f"Chỉ tiêu {elem.text.strip()}")

                            if row_data['so_dieu_chinh'] != 0 or row_data['so_da_ke_khai'] != 0:
                                rows.append({
                                    'ma_so': clean_ma, 'noi_dung': noi_dung,
                                    'so_da_ke_khai': row_data['so_da_ke_khai'],
                                    'so_ke_khai_dung': row_data['so_ke_khai_dung'],
                                    'gia_tri': row_data['so_dieu_chinh'],
                                    'ghi_chu': ''
                                })
            else:
                # Logic cũ (giữ nguyên)
                if tag in ['KHBSDieuChinhTang', 'KHBSDieuChinhGiam', 'TongHopDCTangGiamPNop'] or tag.startswith('ct'):
                    child_tags = [c.tag.split('}', 1)[-1] for c in elem]
                    if 'ct3' in child_tags and 'ct4' in child_tags and 'ct6' in child_tags:
                        row_data = self._extract_row_data_old(elem)
                        if row_data['ma_so']:
                            clean_ma = f"ct{row_data['ma_so']}"
                            noi_dung = row_data['noi_dung'] or mapping.get(clean_ma, f"Chỉ tiêu {row_data['ma_so']}")
                            if row_data['so_dieu_chinh'] != 0 or row_data['so_da_ke_khai'] != 0:
                                rows.append({
                                    'ma_so': clean_ma, 'noi_dung': noi_dung,
                                    'so_da_ke_khai': row_data['so_da_ke_khai'],
                                    'so_ke_khai_dung': row_data['so_ke_khai_dung'],
                                    'gia_tri': row_data['so_dieu_chinh'],
                                    'ghi_chu': 'Mẫu cũ - Tự rà soát'
                                })
        return rows

    def _extract_row_data_tt80(self, parent_elem):
        res = {'noi_dung': '', 'so_da_ke_khai': 0.0, 'so_ke_khai_dung': 0.0, 'so_dieu_chinh': 0.0}
        for child in parent_elem:
            tag = child.tag.split('}', 1)[-1]
            val = child.text.strip() if child.text else ""
            if not val: continue

            if tag == 'ct3_ten':
                res['noi_dung'] = val
            elif tag in ['ct04', 'ct4']:
                res['so_da_ke_khai'] = self._to_float(val)
            elif tag in ['ct05', 'ct5']:
                res['so_ke_khai_dung'] = self._to_float(val)
            elif tag in ['ct06', 'ct6']:
                res['so_dieu_chinh'] = self._to_float(val)
        return res

    def _extract_row_data_old(self, parent_elem):
        res = {'ma_so': '', 'noi_dung': '', 'so_da_ke_khai': 0.0, 'so_ke_khai_dung': 0.0, 'so_dieu_chinh': 0.0}
        for child in parent_elem:
            tag = child.tag.split('}', 1)[-1]
            val = child.text.strip() if child.text else ""
            if not val: continue

            if tag == 'ct3':
                res['ma_so'] = val
            elif tag == 'ct2':
                res['noi_dung'] = val
            elif tag == 'ct4':
                res['so_da_ke_khai'] = self._to_float(val)
            elif tag == 'ct5':
                res['so_ke_khai_dung'] = self._to_float(val)
            elif tag == 'ct6':
                res['so_dieu_chinh'] = self._to_float(val)
        return res

    def _to_float(self, val_str):
        try:
            return float(val_str)
        except:
            return 0.0

    def _is_inside_khbs(self, elem, parent_map):
        curr = elem
        while curr is not None:
            tag = curr.tag.split('}', 1)[-1]
            if tag in ['PL01_1_KHBS', 'PL01_KHBS']: return True
            curr = parent_map.get(curr)
        return False