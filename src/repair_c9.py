import os
import zlib
import argparse

def repair_c9_zlib_tampering(input_path, output_path):
    with open(input_path, 'rb') as f:
        pdf_data = bytearray(f.read())
    
    import re
    streams = []
    for match in re.finditer(rb'stream[\r\n]', pdf_data):
        start_idx = match.end()
        end_idx = pdf_data.find(b'endstream', start_idx)
        if end_idx != -1:
            streams.append((start_idx, end_idx))

    repaired_total = 0
    for start_idx, end_idx in streams:
        stream_data = pdf_data[start_idx : end_idx]
        
        if stream_data.startswith(b'\n'): stream_data = stream_data[1:]
        elif stream_data.startswith(b'\r\n'): stream_data = stream_data[2:]
        
        if not stream_data: continue

        # Chỉ brute-force các luồng có dấu hiệu là Zlib (bắt đầu bằng 0x78)
        # Hoặc luồng đó vốn dĩ không hợp lệ ngay từ đầu
        
        try:
            zlib.decompress(stream_data)
        except zlib.error:
            # Lọc bớt các luồng không phải là zlib nén (ví dụ text thuần)
            # Zlib header thường là 0x78 (120)
            if stream_data[0] != 120 and stream_data[0] != 0x78:
                continue

            print("[INFO] Phat hien luong Zlib bi loi! Dang chay Brute-forcing...")
            repaired = False
            for i in range(min(500, len(stream_data))): # Giới hạn brute-force để tăng tốc
                if repaired: break
                orig_byte = stream_data[i]
                for guess in range(256):
                    if guess == orig_byte: continue
                    stream_data[i] = guess
                    try:
                        zlib.decompress(stream_data)
                        print(f"[SUCCESS] Da khoi phuc byte bi hong tai vi tri {i}. Gia tri dung la: {guess}")
                        offset = start_idx + (1 if pdf_data[start_idx] == 10 else (2 if pdf_data[start_idx:start_idx+2] == b'\r\n' else 0))
                        pdf_data[offset + i] = guess
                        repaired = True
                        repaired_total += 1
                        break
                    except zlib.error:
                        pass
                if not repaired:
                    stream_data[i] = orig_byte 

    with open(output_path, 'wb') as f:
        f.write(pdf_data)
    print(f"[SUCCESS] Hoan tat! Da luu tep phuc hoi: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='../output/demo_c9.pdf')
    parser.add_argument('--output', default='../output/repaired_c9.pdf')
    args = parser.parse_args()
    if os.path.exists(args.input):
        repair_c9_zlib_tampering(args.input, args.output)
