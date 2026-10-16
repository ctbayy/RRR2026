from cryptography.fernet import Fernet
import os

print("=" * 50)
print("🚀 KHỞI ĐỘNG TOOL MÃ HÓA CÔNG THỨC")
print("=" * 50)

# 1. Sinh ra 1 cái Chìa Khóa (Master Key) ngẫu nhiên và duy nhất
key = Fernet.generate_key()

print("\n🔑 BƯỚC 1: COPY DÒNG LỆNH SAU VÀ DÁN VÀO FILE quan_ly_cong_thuc.py:")
print(f"    MASTER_KEY = {key}")
print("-" * 50)

# 2. Đọc file JSON cũ của mày
duong_dan_json = "Data/cong_thuc_mau.json"
duong_dan_bin = "Data/cong_thuc_core.bin"

if not os.path.exists(duong_dan_json):
    print(f"❌ LỖI: Không tìm thấy file {duong_dan_json}. Hãy chắc chắn file cũ vẫn nằm ở đó.")
else:
    try:
        with open(duong_dan_json, "r", encoding="utf-8") as f:
            du_lieu_json_goc = f.read()

        # 3. Dùng Chìa Khóa vừa sinh ra để mã hóa dữ liệu
        fernet = Fernet(key)
        du_lieu_ma_hoa = fernet.encrypt(du_lieu_json_goc.encode('utf-8'))

        # 4. Ghi ra file Nhị phân (.bin)
        os.makedirs("Data", exist_ok=True)
        with open(duong_dan_bin, "wb") as f:
            f.write(du_lieu_ma_hoa)

        print("✅ BƯỚC 2: Đã mã hóa và tạo thành công file: Data/cong_thuc_core.bin")
        print("🗑️ BƯỚC 3: Bây giờ mày có thể XÓA file Data/cong_thuc_mau.json đi cho an toàn.")
        print("=" * 50)
    except Exception as e:
        print(f"❌ Lỗi trong quá trình mã hóa: {e}")