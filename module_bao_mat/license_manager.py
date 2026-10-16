# module_bao_mat/license_manager.py
import os
import json
import base64
from datetime import datetime, date
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.fernet import Fernet
from module_bao_mat.device_manager import DeviceManager

# KHÓA CÔNG KHAI (PUBLIC KEY) CHÍNH THỨC DÙNG ĐỂ XÁC THỰC BẢN QUYỀN TRÊN MÁY CLIENT
# Khóa này an toàn để nhúng trong ứng dụng vì chỉ dùng để kiểm tra chữ ký, không thể dùng để tạo key mới.
PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4Wh9t/XHx17S+UGXQ5LZ
kx0xPpa8sOuarErQyofyTl5mdL9W8EiAUwH8L3vrlgBxGWJO/Lhhn1hQV7sLJotT
PqUEhiP2NSqMzPYgbBYBxLGgbt5zDXXi5/We79UGfEGPbxDesMWyqPWroLLo1/KZ
L7+zSdLAj4D8ZPgNYb683vUIqc7J9VT4cpjHjO2pb0KSji0QpK3plJ4801L5IPbK
aU5hiQHM2GUIOS4j8g700MI+ir0l32x6ABissEy5mz0yMtOvPBt08iqZcIvKzj+e
ztLKU0GZF5gy30UNEdWP3jDuuEdveOGgxVCN1p+d2OPZ5JU0RPR74UKgbTibKMjf
gQIDAQAB
-----END PUBLIC KEY-----"""


class LicenseManager:
    """
    Hệ thống kiểm tra và quản lý Giấy phép Bản quyền Ký số RSA 2048-bit (Level 2)
    kết hợp Phiên bản quyền kích hoạt tự động qua Cloud (Smart Hybrid Licensing).
    Hoạt động ngoại tuyến 100%, bảo mật bất đối xứng và khóa cứng theo phần cứng máy tính.
    """
    LICENSE_FILE = "Data/license.lic"
    SESSION_FILE = "Data/session.bin"
    MASTER_KEY = b'v_M_E_tqN-K0T1X-yG6PjCq4g-p3L2hX8sK_A5rZ1M0='

    @classmethod
    def verify_license_token(cls, token_str: str) -> tuple[bool, str, dict]:
        """
        Xác thực chuỗi giấy phép bản quyền.
        Chuỗi token có cấu trúc: base64(payload_json).base64(signature)
        Trả về: (hop_le: bool, thong_diep: str, data: dict)
        """
        if not token_str or "." not in token_str:
            return False, "Định dạng chuỗi License không hợp lệ!", {}

        parts = token_str.strip().split(".")
        if len(parts) != 2:
            return False, "Cấu trúc mã License bị sai định dạng!", {}

        try:
            payload_bytes = base64.urlsafe_b64decode(parts[0].encode('utf-8'))
            signature_bytes = base64.urlsafe_b64decode(parts[1].encode('utf-8'))
            payload_data = json.loads(payload_bytes.decode('utf-8'))
        except Exception:
            return False, "Không thể giải mã dữ liệu License. Mã bị hỏng hoặc sai định dạng!", {}

        # 1. Xác thực Chữ ký số RSA 2048-bit bằng Public Key
        try:
            public_key = serialization.load_pem_public_key(PUBLIC_KEY_PEM)
            public_key.verify(
                signature_bytes,
                payload_bytes,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
        except Exception:
            return False, "❌ CHỮ KÝ BẢN QUYỀN KHÔNG HỢP LỆ! Dữ liệu giấy phép đã bị chỉnh sửa hoặc làm giả.", {}

        # 2. Kiểm tra HWID có khớp với thiết bị hiện tại không
        license_hwid = str(payload_data.get("hwid", "")).strip().upper()
        current_hwid = DeviceManager.get_machine_id().strip().upper()

        if license_hwid != current_hwid and license_hwid != "*":
            return False, (
                f"❌ MÃ MÁY KHÔNG KHỚP!\n"
                f"Giấy phép này chỉ cấp cho thiết bị: {license_hwid}\n"
                f"Mã thiết bị hiện tại của bạn là: {current_hwid}"
            ), payload_data

        # 3. Kiểm tra Thời hạn sử dụng (Expires At)
        expires_at_str = str(payload_data.get("expires_at", "")).strip()
        if expires_at_str and expires_at_str.lower() not in ["never", "vinh_vien", "vô thời hạn"]:
            try:
                exp_date = datetime.strptime(expires_at_str, "%Y-%m-%d").date()
                today = date.today()
                if today > exp_date:
                    return False, f"⚠️ GIẤY PHÉP ĐÃ HẾT HẠN vào ngày {exp_date.strftime('%d/%m/%Y')}! Vui lòng liên hệ để gia hạn.", payload_data
            except ValueError:
                return False, f"Ngày hết hạn trong giấy phép không đúng định dạng YYYY-MM-DD ({expires_at_str})!", payload_data

        return True, "✅ Giấy phép bản quyền hợp lệ!", payload_data

    @classmethod
    def save_license(cls, token_str: str, file_path: str = None) -> bool:
        """Lưu chuỗi License vào file local"""
        target = file_path or cls.LICENSE_FILE
        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(token_str.strip())
            return True
        except Exception:
            return False

    @classmethod
    def load_and_verify(cls, file_path: str = None) -> tuple[bool, str, dict]:
        """Đọc và kiểm tra file license trên đĩa"""
        target = file_path or cls.LICENSE_FILE
        if not os.path.exists(target):
            return False, "Chưa tìm thấy file giấy phép bản quyền.", {}

        try:
            with open(target, "r", encoding="utf-8") as f:
                token_str = f.read().strip()
            return cls.verify_license_token(token_str)
        except Exception as e:
            return False, f"Lỗi đọc file license: {e}", {}

    @classmethod
    def save_cloud_session(cls, session_dict: dict) -> bool:
        """
        Lưu phiên bản quyền Cloud mã hóa chặt bằng khóa phần cứng máy tính (Level 1).
        Chỉ máy tính có đúng HWID này mới giải mã được.
        """
        try:
            device_key = DeviceManager.get_device_encryption_key()
            fernet = Fernet(device_key)
            encrypted = fernet.encrypt(json.dumps(session_dict, ensure_ascii=False).encode('utf-8'))
            os.makedirs(os.path.dirname(cls.SESSION_FILE), exist_ok=True)
            with open(cls.SESSION_FILE, "wb") as f:
                f.write(encrypted)
            return True
        except Exception:
            return False

    @classmethod
    def load_active_license(cls) -> tuple[bool, str, dict]:
        """
        Kiểm tra trạng thái bản quyền đang hoạt động của thiết bị này.
        Ưu tiên:
          1. File License RSA 2048-bit (Data/license.lic) - Dành cho máy ngoại tuyến hoặc Admin cấp.
          2. Phiên bản quyền Cloud mã hóa (Data/session.bin) - Tự động sinh khi đăng nhập Online.
        Trả về: (hop_le: bool, thong_diep: str, payload_chuan: dict)
        """
        # 1. ƯU TIÊN 1: Kiểm tra file license RSA offline (.lic)
        if os.path.exists(cls.LICENSE_FILE):
            hop_le, msg, payload = cls.load_and_verify(cls.LICENSE_FILE)
            if hop_le:
                user_val = payload.get("username") or payload.get("user") or "NguoiDung_BanQuyen"
                payload_clean = {
                    "username": user_val,
                    "role": payload.get("role", "admin"),
                    "allowed_cqt": payload.get("allowed_cqt", "*"),
                    "expires_at": payload.get("expires_at", "Vĩnh viễn"),
                    "hwid": payload.get("hwid", DeviceManager.get_machine_id()),
                    "source": "rsa_file",
                    "source_label": "Giấy phép RSA 2048-bit (Ngoại tuyến)"
                }
                return True, "Giấy phép bản quyền RSA 2048-bit hợp lệ!", payload_clean

        # 2. ƯU TIÊN 2: Kiểm tra phiên bản quyền Cloud gắn với phần cứng máy (.bin)
        if os.path.exists(cls.SESSION_FILE):
            try:
                with open(cls.SESSION_FILE, "rb") as f:
                    raw_bytes = f.read()

                decrypted_data = None
                # Thử giải mã bằng khóa phần cứng máy tính
                try:
                    device_key = DeviceManager.get_device_encryption_key()
                    fernet = Fernet(device_key)
                    decrypted_data = fernet.decrypt(raw_bytes).decode('utf-8')
                except Exception:
                    # Fallback Master key cũ
                    try:
                        fernet_master = Fernet(cls.MASTER_KEY)
                        decrypted_data = fernet_master.decrypt(raw_bytes).decode('utf-8')
                        # Nâng cấp ngay lên khóa phần cứng
                        cls.save_cloud_session(json.loads(decrypted_data))
                    except Exception:
                        pass

                if decrypted_data:
                    session_data = json.loads(decrypted_data)
                    # Kiểm tra HWID có thuộc về máy này không
                    session_hwid = str(session_data.get("hwid", "")).strip().upper()
                    current_hwid = DeviceManager.get_machine_id().strip().upper()
                    if session_hwid and session_hwid != current_hwid and session_hwid != "*":
                        return False, "❌ Phiên bản quyền bị sao chép từ thiết bị khác (Không khớp HWID)!", {}

                    # Kiểm tra thời hạn
                    exp_str = str(session_data.get("expires_at", "")).strip()
                    if exp_str and exp_str.lower() not in ["never", "vinh_vien", "vô thời hạn", "vĩnh viễn", ""]:
                        try:
                            exp_date = datetime.strptime(exp_str, "%Y-%m-%d").date()
                            if date.today() > exp_date:
                                return False, f"⚠️ Bản quyền đã hết hạn vào ngày {exp_date.strftime('%d/%m/%Y')}!", {}
                        except ValueError:
                            pass

                    payload_clean = {
                        "username": session_data.get("username", "Cloud_User"),
                        "role": session_data.get("role", "admin"),
                        "allowed_cqt": session_data.get("allowed_cqt", "*"),
                        "expires_at": session_data.get("expires_at", "Vĩnh viễn"),
                        "hwid": current_hwid,
                        "source": "cloud_session",
                        "source_label": "Tài khoản Cloud (Tự động kích hoạt)"
                    }
                    return True, "Bản quyền Tài khoản Cloud hợp lệ!", payload_clean
            except Exception:
                pass

        return False, "Thiết bị chưa được kích hoạt bản quyền.", {}

    @classmethod
    def revoke_license(cls) -> bool:
        """Đăng xuất / Xóa toàn bộ bản quyền trên máy này"""
        xoa_duoc = True
        for path in [cls.LICENSE_FILE, cls.SESSION_FILE]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    xoa_duoc = False
        return xoa_duoc
