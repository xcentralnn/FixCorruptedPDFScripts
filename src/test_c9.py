import os
import re

def corrupt_contents_stream(input_path, output_path):
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())
    
    # Tìm object chứa /Contents
    # Pattern: \d+ 0 obj ... /Contents ... stream ... endstream
    # Khá khó bằng regex đơn giản, nhưng thường PDF có: /Contents 12 0 R
    # Hoặc nội dung trực tiếp: /Length 123 /Filter /FlateDecode ... stream\n
    
    # Giải pháp chắc chắn nhất để thấy lỗi: lật bit ở TẤT CẢ các stream có kích thước > 500 byte
    # Lật ở ngay byte thứ 5 của dữ liệu (ngay sau zlib header) để phá hỏng toàn bộ cục nén
    
    streams = []
    for match in re.finditer(rb'stream[\r\n]', data):
        start_idx = match.end()
        end_idx = data.find(b'endstream', start_idx)
        if end_idx != -1 and (end_idx - start_idx) > 500:
            streams.append(start_idx)
            
    if not streams:
        print("[ERROR] Khong tim thay stream.")
        return
        
    for start_idx in streams:
        # Lật bit ở byte thứ 10 của mỗi luồng để nó toang ngay từ đầu
        data[start_idx + 10] ^= 0xFF
        
    with open(output_path, 'wb') as f:
        f.write(data)
    print(f"[SUCCESS] Đã tạo tệp C9 với {len(streams)} luồng bị phá ở byte đầu: {output_path}")

corrupt_contents_stream('demo_input.pdf', 'demo_c9.pdf')
