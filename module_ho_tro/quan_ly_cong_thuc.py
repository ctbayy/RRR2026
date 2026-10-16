import json
import os
from cryptography.fernet import Fernet


class QuanLyCongThuc:
    MASTER_KEY = b'HsgOyfePep06jXTgMPK2GmGDAzqvhMPE5CPyJlJ4Q4w='
    FILE_CORE = "Data/cong_thuc_core.bin"
    FILE_USER = "Data/cong_thuc_user.json"

    @classmethod
    def tai_du_lieu_tong_hop(cls):
        """Đọc và Gộp dữ liệu từ Core và User có tích hợp Debug log"""
        dict_tong = {}

        print("\n" + "=" * 40)
        print("🔍 BẮT ĐẦU DEBUG ĐỌC FILE BẢO MẬT")

        # --- 1. ĐỌC FILE LÕI (CORE BIN) ---
        duong_dan_core = os.path.abspath(cls.FILE_CORE)
        print(f"👉 Đường dẫn Core: {duong_dan_core}")
        print(f"👉 File Core có tồn tại không? {os.path.exists(cls.FILE_CORE)}")

        if os.path.exists(cls.FILE_CORE):
            try:
                fernet = Fernet(cls.MASTER_KEY)
                with open(cls.FILE_CORE, "rb") as f:
                    du_lieu_ma_hoa = f.read()

                print(f"👉 Kích thước file mã hóa: {len(du_lieu_ma_hoa)} bytes")

                # Giải mã
                du_lieu_giai_ma = fernet.decrypt(du_lieu_ma_hoa).decode('utf-8')
                print("👉 Giải mã thành công! Đang bóc tách JSON...")

                dict_core = json.loads(du_lieu_giai_ma)
                dict_tong.update(dict_core)
                print(f"✅ Đã nạp thành công {len(dict_core)} công thức từ Core.")

            except Exception as e:
                print(f"❌ LỖI GIẢI MÃ CORE: {type(e).__name__} - {e}")
                print("   -> Gợi ý: Sai MASTER_KEY, file .bin bị chỉnh sửa bậy, hoặc sai cấu trúc JSON gốc.")

        # --- 2. ĐỌC FILE USER (JSON) ---
        print(f"👉 File User có tồn tại không? {os.path.exists(cls.FILE_USER)}")
        if os.path.exists(cls.FILE_USER):
            try:
                with open(cls.FILE_USER, "r", encoding="utf-8") as f:
                    dict_user = json.load(f)
                dict_tong.update(dict_user)
                print(f"✅ Đã nạp thành công {len(dict_user)} công thức từ User.")
            except Exception as e:
                print(f"❌ LỖI ĐỌC USER: {type(e).__name__} - {e}")

        print("=" * 40 + "\n")
        return dict_tong

    @classmethod
    def them_hoac_sua_1_rule(cls, ma_rule, data_rule, luu_vao_core=False):
        """Chỉ cập nhật đúng 1 Rule vào file tương ứng, không làm ảnh hưởng các Rule khác"""
        os.makedirs("Data", exist_ok=True)
        file_target = cls.FILE_CORE if luu_vao_core else cls.FILE_USER

        try:
            # 1. Đọc dữ liệu hiện tại của file mục tiêu
            dict_hien_tai = {}
            if luu_vao_core and os.path.exists(cls.FILE_CORE):
                fernet = Fernet(cls.MASTER_KEY)
                with open(cls.FILE_CORE, "rb") as f:
                    dict_hien_tai = json.loads(fernet.decrypt(f.read()).decode('utf-8'))
            elif not luu_vao_core and os.path.exists(cls.FILE_USER):
                with open(cls.FILE_USER, "r", encoding="utf-8") as f:
                    dict_hien_tai = json.load(f)

            # 2. Bơm/Đè Rule mới vào
            dict_hien_tai[ma_rule] = data_rule

            # 3. Ghi lại vào ổ cứng
            if luu_vao_core:
                chuoi_json = json.dumps(dict_hien_tai, ensure_ascii=False, indent=4)
                with open(cls.FILE_CORE, "wb") as f:
                    f.write(Fernet(cls.MASTER_KEY).encrypt(chuoi_json.encode('utf-8')))
            else:
                with open(cls.FILE_USER, "w", encoding="utf-8") as f:
                    json.dump(dict_hien_tai, f, ensure_ascii=False, indent=4)
            return True, "Lưu thành công!"
        except Exception as e:
            return False, f"Lỗi lưu trữ: {e}"

    @classmethod
    def xoa_rule(cls, ma_rule):
        """Xóa rule. Ưu tiên xóa ở User trước, nếu không có thì hỏi pass để xóa Core."""
        xoa_thanh_cong = False
        # Xóa ở User
        if os.path.exists(cls.FILE_USER):
            with open(cls.FILE_USER, "r", encoding="utf-8") as f:
                dict_user = json.load(f)
            if ma_rule in dict_user:
                del dict_user[ma_rule]
                with open(cls.FILE_USER, "w", encoding="utf-8") as f: json.dump(dict_user, f, ensure_ascii=False,
                                                                                indent=4)
                xoa_thanh_cong = True

        # Nếu chưa bị xóa, quét tiếp ở Core
        if not xoa_thanh_cong and os.path.exists(cls.FILE_CORE):
            fernet = Fernet(cls.MASTER_KEY)
            with open(cls.FILE_CORE, "rb") as f:
                dict_core = json.loads(fernet.decrypt(f.read()).decode('utf-8'))
            if ma_rule in dict_core:
                del dict_core[ma_rule]
                chuoi_json = json.dumps(dict_core, ensure_ascii=False, indent=4)
                with open(cls.FILE_CORE, "wb") as f: f.write(fernet.encrypt(chuoi_json.encode('utf-8')))
                xoa_thanh_cong = True

        return xoa_thanh_cong

    @classmethod
    def khoi_phuc_mac_dinh(cls, xoa_sach_toan_bo=False):
        """
        xoa_sach_toan_bo = True: Xóa trắng file user.json (Factory Reset)
        xoa_sach_toan_bo = False: Chỉ xóa các rule gốc bị sửa, giữ lại rule mới do user tự tạo
        """
        if not os.path.exists(cls.FILE_USER):
            return True, "Hệ thống đang ở trạng thái mặc định, không có gì để khôi phục."

        try:
            if xoa_sach_toan_bo:
                # Lựa chọn 2: Quét sạch sành sanh
                os.remove(cls.FILE_USER)
                return True, "Đã khôi phục cài đặt gốc và XÓA TOÀN BỘ Rule cá nhân!"
            else:
                # Lựa chọn 1: Khôi phục có chọn lọc
                fernet = Fernet(cls.MASTER_KEY)
                dict_core = {}
                if os.path.exists(cls.FILE_CORE):
                    with open(cls.FILE_CORE, "rb") as f:
                        dict_core = json.loads(fernet.decrypt(f.read()).decode('utf-8'))

                with open(cls.FILE_USER, "r", encoding="utf-8") as f:
                    dict_user = json.load(f)

                # BỘ LỌC MA THUẬT: Giữ lại những Rule trong User MÀ KHÔNG CÓ TRONG Core
                dict_user_moi = {k: v for k, v in dict_user.items() if k not in dict_core}

                if not dict_user_moi:
                    os.remove(cls.FILE_USER)  # Nếu lọc xong mà rỗng tuếch thì xóa luôn file cho nhẹ
                else:
                    with open(cls.FILE_USER, "w", encoding="utf-8") as f:
                        json.dump(dict_user_moi, f, ensure_ascii=False, indent=4)

                return True, "Đã khôi phục các Rule mặc định. Các Rule mới do bạn TỰ TẠO vẫn được giữ nguyên!"
        except Exception as e:
            return False, f"Lỗi khôi phục: {e}"