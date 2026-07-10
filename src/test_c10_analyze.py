import os
import re

def analyze_contents(input_path):
    with open(input_path, 'rb') as f:
        data = f.read()
    
    objs = {}
    for match in re.finditer(rb'(\d+)\s+0\s+obj', data):
        obj_id = int(match.group(1))
        objs[obj_id] = match.start()

    for obj_id, offset in objs.items():
        chunk = data[offset:offset+2000]
        if b'/Type /Page' in chunk or b'/Type/Page' in chunk:
            print(f"--- Page {obj_id} ---")
            contents_match = re.search(rb'/Contents\s+(\d+)\s+0\s+R', chunk)
            if contents_match:
                cid = int(contents_match.group(1))
                if cid in objs:
                    c_offset = objs[cid]
                    c_chunk = data[c_offset:c_offset+500]
                    length_match = re.search(rb'/Length\s+(\d+)', c_chunk)
                    length = int(length_match.group(1)) if length_match else -1
                    print(f"Content ID {cid}, Length {length}")
                else:
                    print(f"Content ID {cid} MISSING")
            else:
                print("Array or no contents")

analyze_contents('demo_c10.pdf')
