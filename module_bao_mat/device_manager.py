# module_bao_mat/device_manager.py
import os
import sys
import hashlib
import base64
import winreg
import ctypes


class DeviceManager:
    """
    Trình quản lý định danh phần cứng (HWID) và dẫn xuất khóa bảo mật thiết bị.
    Hoạt động độc lập, không phụ thuộc wmic, tương thích 100% Windows 10 & Windows 11 (kể cả 24H2).
    """
    _cached_hwid = None
    _SALT = b"RRR_TAX_SECURITY_SALT_2026_HARDWARE_BINDING_V1"

    @classmethod
    def get_machine_id(cls) -> str:
        """
        Lấy mã định danh phần cứng duy nhất (HWID) cố định của máy tính.
        Kết hợp Windows Registry MachineGuid và Volume Serial Number của ổ đĩa C:.
        Định dạng: RRR-XXXX-XXXX-XXXX-XXXX
        """
        if cls._cached_hwid:
            return cls._cached_hwid

        components = []

        # 1. Lấy MachineGuid từ Windows Registry (vĩnh viễn không đổi)
        guid = cls._get_registry_machine_guid()
        if guid:
            components.append(f"GUID:{guid}")

        # 2. Lấy Volume Serial Number của ổ C: qua Windows API Kernel32
        vol_serial = cls._get_system_drive_serial()
        if vol_serial:
            components.append(f"VOL:{vol_serial}")

        # 3. Fallback: Nếu không đọc được cả 2 (rất hiếm), lấy BIOS/Motherboard UUID qua PowerShell CIM
        if len(components) < 2:
            cim_uuid = cls._get_powershell_cim_uuid()
            if cim_uuid:
                components.append(f"CIM:{cim_uuid}")

        # 4. Fallback cuối cùng nếu môi trường bị chặn hoàn toàn
        if not components:
            import uuid
            components.append(f"NODE:{uuid.getnode()}")

        raw_id = "|".join(components)
        h = hashlib.sha256(raw_id.encode('utf-8')).hexdigest().upper()
        # Định dạng mã: RRR-XXXX-XXXX-XXXX-XXXX (16 ký tự phân nhóm đẹp mắt)
        formatted = f"RRR-{h[:4]}-{h[4:8]}-{h[8:12]}-{h[12:16]}"
        cls._cached_hwid = formatted
        return formatted

    @classmethod
    def get_device_encryption_key(cls) -> bytes:
        """
        Tạo khóa Fernet 32-byte được dẫn xuất (PBKDF2) trực tiếp từ HWID của thiết bị này.
        Khóa này dùng để mã hóa Session ngoại tuyến, đảm bảo file session.bin chỉ mở được trên đúng máy này.
        """
        hwid = cls.get_machine_id()
        derived = hashlib.pbkdf2_hmac(
            'sha256',
            hwid.encode('utf-8'),
            cls._SALT,
            iterations=100000,
            dklen=32
        )
        return base64.urlsafe_b64encode(derived)

    @staticmethod
    def _get_registry_machine_guid() -> str:
        """Đọc MachineGuid từ Windows Registry bằng winreg tiêu chuẩn (siêu tốc, không cần subprocess)"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
                guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                if guid:
                    return str(guid).strip().lower()
        except Exception:
            pass
        return ""

    @staticmethod
    def _get_system_drive_serial() -> str:
        """Lấy Volume Serial Number của ổ hệ điều hành (C:\\) qua ctypes Kernel32"""
        try:
            serial = ctypes.c_ulong()
            drive = os.getenv("SystemDrive", "C:") + "\\"
            res = ctypes.windll.kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(drive), None, 0,
                ctypes.byref(serial), None, None, None, 0
            )
            if res and serial.value != 0:
                return f"{serial.value:08X}"
        except Exception:
            pass
        return ""

    @staticmethod
    def _get_powershell_cim_uuid() -> str:
        """Lấy BIOS UUID qua PowerShell CIM (chuẩn hiện đại của Microsoft thay thế wmic)"""
        import subprocess
        try:
            cmd = ['powershell', '-NoProfile', '-NonInteractive', '-Command', '(Get-CimInstance Win32_ComputerSystemProduct).UUID']
            out = subprocess.check_output(cmd, timeout=3, stderr=subprocess.DEVNULL).decode().strip()
            if out and len(out) >= 16:
                return out
        except Exception:
            pass
        return ""
