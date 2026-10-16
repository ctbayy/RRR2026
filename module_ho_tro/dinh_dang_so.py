def dinh_dang_so_vn(gia_tri, so_thap_phan=0):
    """
    Định dạng số theo chuẩn Việt Nam (VD: 1.000.000,99).
    """
    try:
        if gia_tri is None or str(gia_tri).strip() == "":
            return "0"

        # Tiền xử lý nếu đầu vào là chuỗi có sẵn định dạng quốc tế
        if isinstance(gia_tri, str):
            gia_tri = gia_tri.replace(',', '')

        so_thuc = float(gia_tri)

        # Nếu là số tròn và không yêu cầu thập phân thì bỏ phần đuôi
        if so_thuc.is_integer() and so_thap_phan == 0:
            chuoi_quoc_te = f"{int(so_thuc):,}"
        else:
            # Format chuẩn quốc tế với số chữ số thập phân tương ứng
            chuoi_quoc_te = f"{so_thuc:,.{so_thap_phan}f}"

        # Thuật toán hoán đổi: Phẩy -> Tạm(X) | Chấm -> Phẩy | Tạm(X) -> Chấm
        chuoi_vn = chuoi_quoc_te.replace(',', 'X').replace('.', ',').replace('X', '.')

        return chuoi_vn
    except (ValueError, TypeError):
        # Trả về chuỗi gốc nếu dữ liệu không phải là số (VD: chữ text)
        return str(gia_tri)