import os
import argparse

def simulate_c8_font_deletion(input_path, output_path):
    """
    Kịch bản C8: Xóa tài nguyên phông chữ (Font Resources Deletion).
    Mô phỏng việc mất dữ liệu phông chữ nhúng và bảng ánh xạ Unicode.
    """
    with open(input_path, 'rb') as f:
        pdf_data = f.read()
    
    # Xóa tham chiếu tới /FontFile2 và /ToUnicode bằng cách ghi đè khoảng trắng
    corrupted_data = pdf_data.replace(b'/FontFile2', b'          ')
    corrupted_data = corrupted_data.replace(b'/ToUnicode', b'          ')
    
    with open(output_path, 'wb') as f:
        f.write(corrupted_data)
    print(f"[SUCCESS] Đã tạo tệp mô phỏng C8: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mô phỏng lỗi cấu trúc PDF - Kịch bản C8 (Mất phông chữ).')
    parser.add_argument('--input', type=str, default='../input/demo_input.pdf', help='Đường dẫn tệp PDF gốc')
    parser.add_argument('--output', type=str, default='../output/demo_c8.pdf', help='Đường dẫn tệp đầu ra')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[ERROR] Không tìm thấy tệp đầu vào '{args.input}'.")
        print("[INFO] Cách Demo: ")
        print(f"       Cách 1: Đặt một file PDF hợp lệ, đổi tên thành '{args.input}' và chạy: python simulate_c8.py")
        print("       Cách 2: Truyền trực tiếp đường dẫn file bằng tham số: python simulate_c8.py --input <đường_dẫn_file_của_bạn>")
    else:
        print(f"[INFO] Bắt đầu xử lý kịch bản C8 trên tệp: {args.input}")
        simulate_c8_font_deletion(args.input, args.output)
