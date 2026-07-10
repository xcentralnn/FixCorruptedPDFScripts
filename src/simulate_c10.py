import os
import argparse

def simulate_c10_partial_truncation(input_path, output_path):
    """
    Kịch bản C10: Cắt xén một phần (Partial Truncation).
    Mô phỏng sự cố hỏng tệp khi chỉ giữ lại 70% dữ liệu tính từ đầu tệp.
    """
    with open(input_path, 'rb') as f:
        pdf_data = f.read()
    
    # Cắt bỏ 30% dữ liệu phần cuối tệp
    truncated_size = int(len(pdf_data) * 0.7)
    corrupted_data = pdf_data[:truncated_size]
    
    with open(output_path, 'wb') as f:
        f.write(corrupted_data)
    print(f"[SUCCESS] Đã tạo tệp mô phỏng C10: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mô phỏng lỗi cấu trúc PDF - Kịch bản C10 (Cắt xén tệp).')
    parser.add_argument('--input', type=str, default='../input/demo_input.pdf', help='Đường dẫn tệp PDF gốc')
    parser.add_argument('--output', type=str, default='../output/demo_c10.pdf', help='Đường dẫn tệp đầu ra')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[ERROR] Không tìm thấy tệp đầu vào '{args.input}'.")
        print("[INFO] Cách Demo: ")
        print(f"       Cách 1: Đặt một file PDF hợp lệ, đổi tên thành '{args.input}' và chạy: python simulate_c10.py")
        print("       Cách 2: Truyền trực tiếp đường dẫn file bằng tham số: python simulate_c10.py --input <đường_dẫn_file_của_bạn>")
    else:
        print(f"[INFO] Bắt đầu xử lý kịch bản C10 trên tệp: {args.input}")
        simulate_c10_partial_truncation(args.input, args.output)
