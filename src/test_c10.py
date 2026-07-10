import re
import os

def repair_c10_deep(input_path, output_path):
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # 1. Quét tìm tất cả các Object
    objs = {}
    for match in re.finditer(rb'(\d+)\s+0\s+obj', data):
        obj_id = int(match.group(1))
        offset = match.start()
        objs[obj_id] = offset

    if not objs:
        print("[ERROR] Không tìm thấy object.")
        return

    # 2. Tìm các Page Object còn sót lại
    page_ids = []
    for obj_id, offset in objs.items():
        chunk = data[offset:offset+2000]
        if b'/Type /Page' in chunk or b'/Type/Page' in chunk:
            # Check if it's actually a page, usually contains /Parent or /MediaBox
            if b'/Parent' in chunk or b'/MediaBox' in chunk or b'/Contents' in chunk:
                page_ids.append(obj_id)

    print(f"Found {len(page_ids)} surviving pages: {page_ids}")

    # Nếu không tìm thấy trang nào, thử tìm các lệnh vẽ text (BT...ET) để xem có data không
    if not page_ids:
        print("[WARN] Khong the tim thay /Page, root fallback.")
        page_ids = []

    out_data = bytearray(data)
    if not out_data.endswith(b'\n'):
        out_data.extend(b'\n')

    max_obj_id = max(objs.keys())
    
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
        # Fallback to existing Catalog if we can find one
        root_id = 1
        for obj_id, offset in objs.items():
            chunk = data[offset:offset+1000]
            if b'/Type /Catalog' in chunk or b'/Type/Catalog' in chunk:
                root_id = obj_id
                break

    # 3. Rebuild XRef
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

    # 4. Rebuild Trailer
    out_data.extend(b'trailer\n<<\n')
    out_data.extend(f'/Size {max_obj_id + 1}\n'.encode('ascii'))
    out_data.extend(f'/Root {root_id} 0 R\n'.encode('ascii'))
    out_data.extend(b'>>\nstartxref\n')
    out_data.extend(f'{xref_offset}\n'.encode('ascii'))
    out_data.extend(b'%%EOF\n')

    with open(output_path, 'wb') as f:
        f.write(out_data)
    print(f"[SUCCESS] Rebuilt PDF saved to {output_path}")

repair_c10_deep('demo_c10.pdf', 'test_rebuild_c10.pdf')
