import re

def find_content_streams(input_path):
    with open(input_path, 'rb') as f:
        data = f.read()
    
    objs = {}
    for match in re.finditer(rb'(\d+)\s+0\s+obj', data):
        obj_id = int(match.group(1))
        objs[obj_id] = match.start()

    content_streams = []
    
    for obj_id, offset in objs.items():
        chunk = data[offset:offset+1000]
        if b'/Type /Page' in chunk or b'/Type/Page' in chunk:
            contents_match = re.search(rb'/Contents\s+(\d+)\s+0\s+R', chunk)
            if contents_match:
                cid = int(contents_match.group(1))
                content_streams.append(cid)
            else:
                contents_array_match = re.search(rb'/Contents\s*\[(.*?)\]', chunk)
                if contents_array_match:
                    sub_ids = re.findall(rb'(\d+)\s+0\s+R', contents_array_match.group(1))
                    if sub_ids:
                        content_streams.append(int(sub_ids[0]))

    print(f"Content Stream IDs: {content_streams}")
    
    # Find offsets for these streams
    offsets = []
    for cid in content_streams:
        if cid in objs:
            c_offset = objs[cid]
            c_chunk = data[c_offset:c_offset+500]
            stream_match = re.search(rb'stream[\r\n]', c_chunk)
            if stream_match:
                stream_data_start = c_offset + stream_match.end()
                offsets.append(stream_data_start)
    
    print(f"Content Stream Data Starts: {offsets}")

find_content_streams('demo_input.pdf')
