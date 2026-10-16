from module_doc_hoadon.invoice_processor import InvoiceProcessor

# CHÚ Ý: Điền đúng đường dẫn file master_data_map.json của mày
JSON_MAP_PATH = "Data/master_data_map.json"


def doc_file_hoa_don_v2(duong_dan_file, is_mua_vao=False):
    """
    Hàm cầu nối bọc InvoiceProcessor.
    Phân luồng xử lý XML hoặc Excel/CSV tự động để trả về 1 chuẩn DataFrame duy nhất.
    """
    processor = InvoiceProcessor()

    # Quất thẳng vào hàm xử lý Excel/CSV
    if duong_dan_file.lower().endswith(('.xlsx', '.xls', '.csv')):
        df = processor.process_excel_csv_invoices(duong_dan_file, JSON_MAP_PATH, is_mua_vao)
        return df
    else:
        print(f"Bỏ qua định dạng file không hỗ trợ: {duong_dan_file}")
        return None