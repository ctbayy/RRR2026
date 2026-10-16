#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CÔNG CỤ TẠO LICENSE BẢN QUYỀN (CHỈ DÀNH RIÊNG CHO QUẢN TRỊ VIÊN / TÁC GIẢ)
Sử dụng Private Key RSA 2048-bit để ký số giấy phép bản quyền cho khách hàng.
"""
import os
import sys
import json
import base64
import argparse
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization


PRIVATE_KEY_PATH = "Data/admin_private_key.pem"


def load_private_key():
    if not os.path.exists(PRIVATE_KEY_PATH):
        print(f"❌ Không tìm thấy file Private Key tại: {PRIVATE_KEY_PATH}")
        sys.exit(1)
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def tao_chuoi_license(hwid: str, username: str, expires_at: str, role: str = "admin", allowed_cqt: str = "*") -> str:
    """Ký số và tạo ra chuỗi license token"""
    private_key = load_private_key()

    payload = {
        "hwid": hwid.strip().upper(),
        "username": username.strip(),
        "role": role.strip(),
        "allowed_cqt": allowed_cqt.strip(),
        "issued_at": datetime.now().strftime("%Y-%m-%d"),
        "expires_at": expires_at.strip()
    }

    # Bọc dữ liệu thành JSON chuẩn đã sắp xếp key
    payload_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')

    # Ký số bằng RSA 2048-bit SHA-256
    signature = private_key.sign(
        payload_bytes,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    part_payload = base64.urlsafe_b64encode(payload_bytes).decode('utf-8')
    part_sig = base64.urlsafe_b64encode(signature).decode('utf-8')

    token = f"{part_payload}.{part_sig}"
    return token, payload


def main():
    parser = argparse.ArgumentParser(description="Công cụ tạo License Key RSA 2048-bit")
    parser.add_argument("--hwid", help="Mã HWID của máy khách (VD: RRR-BE90-49CA-2790-744B)")
    parser.add_argument("--user", help="Tên khách hàng / Đơn vị", default="NguoiDung_BanQuyen")
    parser.add_argument("--exp", help="Ngày hết hạn (YYYY-MM-DD hoặc 'never')", default=None)
    parser.add_argument("--role", help="Vai trò (admin/user)", default="admin")
    parser.add_argument("--cqt", help="Mã Cơ quan thuế (* hoặc danh sách ngăn cách bởi dấu phẩy)", default="*")
    parser.add_argument("--out", help="Đường dẫn file .lic xuất ra", default=None)

    args = parser.parse_args()

    hwid = args.hwid
    user = args.user
    exp = args.exp
    role = args.role
    cqt = args.cqt

    # Nếu không truyền argument, chạy chế độ tương tác (Interactive CLI)
    if not hwid:
        print("=" * 60)
        print("🔐 HỆ THỐNG PHÁT HÀNH GIẤY PHÉP BẢN QUYỀN RRR (RSA 2048-BIT)")
        print("=" * 60)

        # Lấy thử HWID máy này làm gợi ý
        from module_bao_mat.device_manager import DeviceManager
        hwid_hien_tai = DeviceManager.get_machine_id()

        nhap_hwid = input(f"👉 Nhập HWID máy khách [Mặc định máy này: {hwid_hien_tai}]: ").strip()
        hwid = nhap_hwid if nhap_hwid else hwid_hien_tai

        nhap_user = input("👉 Tên khách hàng / Đơn vị [Mặc định: KhachHang_UuTien]: ").strip()
        user = nhap_user if nhap_user else "KhachHang_UuTien"

        ngay_mac_dinh = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        nhap_exp = input(f"👉 Ngày hết hạn (YYYY-MM-DD hoặc 'never') [Mặc định 1 năm: {ngay_mac_dinh}]: ").strip()
        exp = nhap_exp if nhap_exp else ngay_mac_dinh

        nhap_role = input("👉 Quyền sử dụng (admin/user) [Mặc định: admin]: ").strip()
        role = nhap_role if nhap_role else "admin"

        nhap_cqt = input("👉 Mã CQT được phép (* là tất cả) [Mặc định: *]: ").strip()
        cqt = nhap_cqt if nhap_cqt else "*"
    else:
        if not exp:
            exp = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")

    token, payload = tao_chuoi_license(hwid, user, exp, role, cqt)

    print("\n" + "=" * 60)
    print("✅ ĐÃ TẠO LICENSE THÀNH CÔNG!")
    print("=" * 60)
    print(f"📌 HWID Thiết bị:   {payload['hwid']}")
    print(f"👤 Khách hàng:      {payload['username']}")
    print(f"⏳ Hạn sử dụng:     {payload['expires_at']}")
    print(f"🛡️ Quyền truy cập:  {payload['role']}")
    print(f"🏢 CQT cho phép:    {payload['allowed_cqt']}")
    print("-" * 60)
    print("🔑 CHUỖI LICENSE KEY (Gửi chuỗi này hoặc file .lic cho khách):")
    print(token)
    print("-" * 60)

    # Lưu ra file
    file_out = args.out or f"Data/license_{payload['hwid'].replace('RRR-', '')}.lic"
    with open(file_out, "w", encoding="utf-8") as f:
        f.write(token)
    print(f"💾 Đã lưu file giấy phép tại: {file_out}")

    # Đồng thời lưu vào Data/license.lic nếu là máy hiện tại để kích hoạt ngay
    from module_bao_mat.device_manager import DeviceManager
    if payload['hwid'] == DeviceManager.get_machine_id():
        with open("Data/license.lic", "w", encoding="utf-8") as f:
            f.write(token)
        print("✨ Thiết bị này đã được tự động kích hoạt vào file 'Data/license.lic'!")
    print("=" * 60)


if __name__ == "__main__":
    main()
