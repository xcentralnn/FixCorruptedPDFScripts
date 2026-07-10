import os
import re

def filter_blank_pages(input_path):
    with open(input_path, 'rb') as f:
        data = f.read()
    
    objs = {}
    for match in re.finditer(rb'(\d+)\s+0\s+obj', data):
        obj_id = int(match.group(1))
        objs[obj_id] = match.start()

    page_ids = []
    valid_page_ids = []
    for obj_id, offset in objs.items():
        chunk = data[offset:offset+2000]
        if b'/Type /Page' in chunk or b'/Type/Page' in chunk:
            page_ids.append(obj_id)
            # Find contents
            contents_match = re.search(rb'/Contents\s+(\d+)\s+0\s+R', chunk)
            if contents_match:
                content_id = int(contents_match.group(1))
                if content_id in objs:
                    valid_page_ids.append(obj_id)
            else:
                contents_array_match = re.search(rb'/Contents\s*\[(.*?)\]', chunk)
                if contents_array_match:
                    sub_ids = re.findall(rb'(\d+)\s+0\s+R', contents_array_match.group(1))
                    survived = any(int(sub_id) in objs for sub_id in sub_ids)
                    if survived:
                        valid_page_ids.append(obj_id)
                else:
                    # If it has NO contents tag at all, it's inherently blank
                    pass
                    
    print(f"Total pages found: {len(page_ids)}")
    print(f"Valid pages with content: {len(valid_page_ids)}")
    return valid_page_ids

filter_blank_pages('demo_c10.pdf')
