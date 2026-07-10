import os
import re
import argparse

def simulate_c9_zlib_tampering(input_path, output_path):
    """
    Kịch bản C9: Mô phỏng hỏng dữ liệu nén Zlib.
    Phiên bản này sẽ nhắm CHÍNH XÁC vào luồng chứa nội dung văn bản (Content Stream) của 1 trang duy nhất,
    để đảm bảo bạn thấy được kết quả Demo là có đúng 1 trang trắng xóa và các trang còn lại bình thường.
    Đồng thời tối ưu thời gian chạy script phục hồi (Repair) cực kỳ nhanh.
    """
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())
    
    # 1. Tìm tất cả các object
    objs = {}
    for match in re.finditer(rb'(\d+)\s+0\s+obj', data):
        obj_id = int(match.group(1))
        objs[obj_id] = match.start()

    # 2. Định vị luồng dữ liệu chứa văn bản của trang đầu tiên
    content_stream_id = None
    for obj_id, offset in objs.items():
        chunk = data[offset:offset+1000]
        if b'/Type /Page' in chunk or b'/Type/Page' in chunk:
            contents_match = re.search(rb'/Contents\s+(\d+)\s+0\s+R', chunk)
            if contents_match:
                content_stream_id = int(contents_match.group(1))
                break
            else:
                contents_array_match = re.search(rb'/Contents\s*\[(.*?)\]', chunk)
                if contents_array_match:
                    sub_ids = re.findall(rb'(\d+)\s+0\s+R', contents_array_match.group(1))
                    if sub_ids:
                        content_stream_id = int(sub_ids[0])
                        break
                        
    if not content_stream_id or content_stream_id not in objs:
        print("[ERROR] Không tìm thấy luồng văn bản phù hợp.")
        return
        
    # 3. Lấy vị trí bắt đầu của luồng Zlib đó
    c_offset = objs[content_stream_id]
    c_chunk = data[c_offset:c_offset+500]
    stream_match = re.search(rb'stream[\r\n]', c_chunk)
    
    if not stream_match:
        print("[ERROR] Không định vị được từ khóa stream.")
        return
        
    stream_data_start = c_offset + stream_match.end()
    
    # 4. Bắn hỏng đúng 1 byte (byte thứ 10) của luồng văn bản trang này
    data[stream_data_start + 10] ^= 0xFF
        
    with open(output_path, 'wb') as f:
        f.write(data)
    print(f"[SUCCESS] Đã tạo tệp mô phỏng C9 (Phá hủy chính xác 1 trang nội dung): {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mô phỏng lỗi cấu trúc PDF - Kịch bản C9 (Lỗi nén Zlib chính xác 1 trang).')
    parser.add_argument('--input', type=str, default='../input/demo_input.pdf', help='Đường dẫn tệp PDF gốc')
    parser.add_argument('--output', type=str, default='../output/demo_c9.pdf', help='Đường dẫn tệp đầu ra')
    args = parser.parse_args()
    
    if os.path.exists(args.input):
        simulate_c9_zlib_tampering(args.input, args.output)
    else:
        print(f"[ERROR] Không tìm thấy tệp '{args.input}'")
