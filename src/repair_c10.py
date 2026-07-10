import os
import re
import argparse

def repair_c10_advanced(input_path, output_path):
    """
    Kịch bản phục hồi C10 (Deep Page Tree Reconstruction).
    Thực hiện quét lại toàn bộ dữ liệu vật lý để tìm các trang (Pages) còn sót lại,
    tạo mới cấu trúc Cây trang (Page Tree), Root Catalog, và Bảng XRef/Trailer.
    """
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # 1. Tìm tất cả các đối tượng hợp lệ còn sót lại
    objs = {}
    for match in re.finditer(rb'(\d+)\s+0\s+obj', data):
        obj_id = int(match.group(1))
        offset = match.start()
        objs[obj_id] = offset

    if not objs:
        print("[ERROR] Khong tim thay bat ky object nao de khoi phuc.")
        return

    # 2. Định vị các trang (Pages) còn sống sót
    page_ids = []
    for obj_id, offset in objs.items():
        chunk = data[offset:offset+2000]
        if b'/Type /Page' in chunk or b'/Type/Page' in chunk:
            # Đảm bảo đây thực sự là Page
            if b'/Parent' in chunk or b'/MediaBox' in chunk or b'/Contents' in chunk:
                page_ids.append(obj_id)

    print(f"[INFO] Cuu vot thanh cong {len(page_ids)} trang du lieu: {page_ids}")

    out_data = bytearray(data)
    if not out_data.endswith(b'\n'):
        out_data.extend(b'\n')

    max_obj_id = max(objs.keys())
    
    # 3. Tái thiết lập Cây trang (Page Tree) và Catalog
    if page_ids:
        pages_obj_id = max_obj_id + 1
        catalog_obj_id = max_obj_id + 2
        
        kids_str = " ".join([f"{pid} 0 R" for pid in page_ids])
        pages_obj = f"{pages_obj_id} 0 obj\n<< /Type /Pages /Kids [{kids_str}] /Count {len(page_ids)} >>\nendobj\n".encode('ascii')
        catalog_obj = f"{catalog_obj_id} 0 obj\n<< /Type /Catalog /Pages {pages_obj_id} 0 R >>\nendobj\n".encode('ascii')

        objs[pages_obj_id] = len(out_data)
        out_data.extend(pages_obj)
        
        objs[catalog_obj_id] = len(out_data)
        out_data.extend(catalog_obj)
        
        root_id = catalog_obj_id
    else:
        root_id = 1
        for obj_id, offset in objs.items():
            chunk = data[offset:offset+1000]
            if b'/Type /Catalog' in chunk or b'/Type/Catalog' in chunk:
                root_id = obj_id
                break

    # 4. Tái thiết lập Bảng tham chiếu chéo (XRef Table)
    max_obj_id = max(objs.keys())
    xref_offset = len(out_data)
    
    out_data.extend(b'xref\n')
    out_data.extend(f'0 {max_obj_id + 1}\n'.encode('ascii'))
    
    for i in range(max_obj_id + 1):
        if i == 0:
            out_data.extend(b'0000000000 65535 f \n')
        elif i in objs:
            out_data.extend(f'{objs[i]:010d} 00000 n \n'.encode('ascii'))
        else:
            out_data.extend(b'0000000000 65535 f \n')

    # 5. Tái thiết lập Trailer
    out_data.extend(b'trailer\n<<\n')
    out_data.extend(f'/Size {max_obj_id + 1}\n'.encode('ascii'))
    out_data.extend(f'/Root {root_id} 0 R\n'.encode('ascii'))
    out_data.extend(b'>>\nstartxref\n')
    out_data.extend(f'{xref_offset}\n'.encode('ascii'))
    out_data.extend(b'%%EOF\n')

    with open(output_path, 'wb') as f:
        f.write(out_data)
    print(f"[SUCCESS] Da tai tao thanh cong cau truc tep PDF C10: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Công cụ phục hồi cấu trúc tệp PDF bị cắt xén (C10).')
    parser.add_argument('--input', default='../output/demo_c10.pdf')
    parser.add_argument('--output', default='../output/repaired_c10.pdf')
    args = parser.parse_args()
    
    if os.path.exists(args.input):
        repair_c10_advanced(args.input, args.output)
    else:
        print(f"[ERROR] Khong tim thay file loi '{args.input}'")
