# module_phan_tich/bao_cao_doanh_so.py

import pandas as pd
from module_doc_hoadon.invoice_processor import InvoiceProcessor


class BaoCaoDoanhSoEngine:
    @staticmethod
    def _lay_to_khai_moi_nhat(ky_base, dict_form):
        """Hàm nội bộ: Quét tất cả các bản KHBS của cùng 1 kỳ và lấy bản có số Lần Bổ Sung cao nhất"""
        ky_base_fix = ky_base.replace('0', '', 1) if ky_base.startswith('0') else ky_base
        latest_data = {}
        max_lan = -1

        for k, v in dict_form.items():
            # Tách bỏ các tiền tố/hậu tố nếu có (VD: 01/2026_BS1 -> 01/2026)
            k_clean = str(k).split('_')[0]
            if k_clean == ky_base or k_clean == ky_base_fix:
                thong_tin = v.get("ThongTinChung", {})
                # Bắt số lần bổ sung
                lan_bs = int(thong_tin.get("LanBoSung", v.get("SoLan", 0)))
                if lan_bs > max_lan:
                    max_lan = lan_bs
                    latest_data = v

        return latest_data

    @classmethod
    def xuat_du_lieu_bao_cao(cls, dict_hd, du_lieu_he_thong_to_khai, nam_pt, is_mua_vao=False, ghi_log=None):
        """Nhà máy xử lý kép: Chạy được cho cả Hóa đơn Bán ra và Mua vào (Đã Fix Lỗi Mất Quý & Đúp Dòng)"""
        try:
            df_hd = dict_hd
            # Bỏ lệnh IF kiểm tra dict đi, ép chạy thẳng qua hàm lọc luôn (vì hàm lọc đã bọc thép sẵn rồi)
            df_hd = InvoiceProcessor.loc_hoa_don_tinh_toan(df_hd)

            # 1. Lọc hóa đơn theo năm phân tích
            cac_nam_can_quyet = []
            if isinstance(df_hd, pd.DataFrame) and not df_hd.empty:
                if nam_pt != "Tất cả các năm" and '_Nam' in df_hd.columns:
                    df_hd = df_hd[df_hd['_Nam'] == str(nam_pt)]
                    cac_nam_can_quyet = [str(nam_pt)]
                elif '_Nam' in df_hd.columns:
                    cac_nam_can_quyet = df_hd['_Nam'].dropna().unique().tolist()

            dict_tk_gtgt = du_lieu_he_thong_to_khai.get('01/GTGT', {})

            # 2. KIỂM TRA CHẾ ĐỘ KÊ KHAI (Nếu có bất kỳ tờ khai nào là Quý -> Chốt năm đó khai Quý)
            is_quarterly_filer = False
            for k, v in dict_tk_gtgt.items():
                k_clean = str(k).split('_')[0]
                if nam_pt == "Tất cả các năm" or str(nam_pt) in k_clean:
                    if v.get("ThongTinChung", {}).get("KieuKy", "M") == "Q":
                        is_quarterly_filer = True
                        break

            ket_qua_tam = {} # Dùng Dictionary để bóp chết các dòng bị trùng lặp
            cac_thang_da_xu_ly = set() # Ghi sổ các tháng đã hút hóa đơn

            # --- HÀM NỘI BỘ: HÚT HÓA ĐƠN ---
            def get_tong_hd(danh_sach_thang, nam_str):
                hd_truoc_sum, hd_thue_sum = 0.0, 0.0
                if isinstance(df_hd, pd.DataFrame) and not df_hd.empty and '_Thang' in df_hd.columns:
                    cac_chuoi_thang = []
                    for t in danh_sach_thang:
                        t_str = str(t).zfill(2)
                        cac_chuoi_thang.extend([f"{t_str}/{nam_str}", f"{int(t)}/{nam_str}"])
                        cac_thang_da_xu_ly.add(f"{t_str}/{nam_str}")

                    mask = df_hd['_Thang'].isin(cac_chuoi_thang)
                    df_loc = df_hd[mask]
                    if 'TongTienChuaThue' in df_loc.columns: hd_truoc_sum = float(df_loc['TongTienChuaThue'].sum())
                    if 'TongTienThue' in df_loc.columns: hd_thue_sum = float(df_loc['TongTienThue'].sum())
                return hd_truoc_sum, hd_thue_sum

            # 3. QUÉT XỬ LÝ THEO TRỤ CỘT TỜ KHAI
            for ky, dict_ky_tk in dict_tk_gtgt.items():
                ky_clean = str(ky).split('_')[0]
                if nam_pt != "Tất cả các năm" and str(nam_pt) not in ky_clean:
                    continue

                nam_cua_ky = ky_clean.split('/')[1] if '/' in ky_clean else str(nam_pt)
                kieu_ky = dict_ky_tk.get("ThongTinChung", {}).get("KieuKy", "M")

                hd_truoc = hd_thue = tk_truoc = tk_thue = 0.0
                ky_hien_thi = ky_clean

                # Hút Hóa đơn tùy theo loại kỳ của tờ khai này
                if kieu_ky == "Q":
                    quy_num = int(ky_clean.split('/')[0])
                    ky_hien_thi = f"Q{quy_num}/{nam_cua_ky}"
                    cac_thang = [(quy_num-1)*3 + 1, (quy_num-1)*3 + 2, (quy_num-1)*3 + 3]
                    hd_truoc, hd_thue = get_tong_hd(cac_thang, nam_cua_ky)
                else:
                    thang_num = int(ky_clean.split('/')[0])
                    hd_truoc, hd_thue = get_tong_hd([thang_num], nam_cua_ky)

                # Bốc số liệu Tờ khai
                dict_moi_nhat = cls._lay_to_khai_moi_nhat(ky, dict_tk_gtgt)
                if dict_moi_nhat:
                    ctc = dict_moi_nhat.get('ChiTieuChinh', {})
                    def get_val(ma):
                        try: return float(str(ctc.get(ma, {}).get("GiaTri", 0)).replace(',', ''))
                        except: return 0.0

                    if not is_mua_vao:
                        tk_truoc = get_val('ct26') + get_val('ct32a') + get_val('ct34')
                        if tk_truoc == 0: tk_truoc = get_val('ct26') + get_val('ct29') + get_val('ct30') + get_val('ct32') + get_val('ct32a')
                        tk_thue = get_val('ct35')
                        if tk_thue == 0: tk_thue = get_val('ct31') + get_val('ct33')
                    else:
                        tk_truoc = get_val('ct23')
                        tk_thue = get_val('ct24')

                # Lưu vào Dictionary (Nếu có trùng lặp sẽ tự động đè lên nhau, triệt tiêu đúp dòng)
                ket_qua_tam[ky_hien_thi] = {
                    "ky": ky_hien_thi, "hd_truoc": hd_truoc, "hd_thue": hd_thue,
                    "tk_truoc": tk_truoc, "tk_thue": tk_thue
                }

            # 4. QUÉT HÓA ĐƠN MỒ CÔI (Ép mẻ lưới cuối cùng)
            if not cac_nam_can_quyet and nam_pt != "Tất cả các năm":
                cac_nam_can_quyet = [str(nam_pt)]

            for n_str in cac_nam_can_quyet:
                if is_quarterly_filer:
                    # Chế độ Quý: Ép tất cả hóa đơn còn sót vào 4 Quý
                    for q in range(1, 5):
                        ky_q = f"Q{q}/{n_str}"
                        if ky_q not in ket_qua_tam:  # Chỉ xử lý nếu Quý này chưa có Tờ khai
                            cac_thang = [(q-1)*3 + 1, (q-1)*3 + 2, (q-1)*3 + 3]
                            hd_t, hd_th = get_tong_hd(cac_thang, n_str)
                            # Đảm bảo hiển thị Quý kể cả khi cả HĐ và TK đều trống, hoặc chỉ hiện khi có HĐ?
                            # -> Hiện nếu có phát sinh HĐ (để soi chênh lệch)
                            if hd_t > 0 or hd_th > 0:
                                ket_qua_tam[ky_q] = {"ky": ky_q, "hd_truoc": hd_t, "hd_thue": hd_th, "tk_truoc": 0, "tk_thue": 0}
                else:
                    # Chế độ Tháng: Ép hóa đơn còn sót vào 12 Tháng
                    for m in range(1, 13):
                        ky_m = f"{str(m).zfill(2)}/{n_str}"
                        if ky_m not in ket_qua_tam and f"{str(m).zfill(2)}/{n_str}" not in cac_thang_da_xu_ly:
                            hd_t, hd_th = get_tong_hd([m], n_str)
                            if hd_t > 0 or hd_th > 0:
                                ket_qua_tam[ky_m] = {"ky": ky_m, "hd_truoc": hd_t, "hd_thue": hd_th, "tk_truoc": 0, "tk_thue": 0}

            # 5. SẮP XẾP CHUẨN THỜI GIAN
            def sort_key(x):
                k = x['ky']
                if '/' not in k: return k
                phan_ky, nam = k.split('/')
                # Quy đổi Quý ra tháng ảo để máy tính tự động xếp tăng dần (Q1->Tháng 1, Q2->Tháng 4...)
                if 'Q' in phan_ky:
                    thang_tuong_duong = int(phan_ky.replace('Q', '')) * 3 - 2
                else:
                    thang_tuong_duong = int(phan_ky)
                return f"{nam}_{thang_tuong_duong:02d}"

            danh_sach_du_lieu = list(ket_qua_tam.values())
            danh_sach_du_lieu.sort(key=sort_key)

            return danh_sach_du_lieu

        except Exception as e:
            if ghi_log: ghi_log(f"  ❌ Lỗi kết xuất báo cáo doanh số: {e}")
            return []

