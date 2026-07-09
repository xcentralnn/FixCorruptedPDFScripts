import sys
import re

def count_page_obj(filename):
    page_obj_keyword = b'/Page'
    with open(filename,'rb') as file:
        file_data = file.read()
        return file_data.count(page_obj_keyword)

def get_page_obj_id(filename):
    pattern = re.compile(rb"(\d+\s+\d+)\s+obj(.*?)endobj", re.DOTALL)
    extracted_pages = []
    with open(filename,'rb') as file:
        file_data = file.read()
        for match in pattern.finditer(file_data):
            obj_id = match.group(1)
            content = match.group(2)
            
            # 1. Verify it is a Page object
            if re.search(rb"/Type\s*/Page\b", content):
                
                # 2. Search for the Parent reference (e.g., "/Parent 2 0 R")
                # Group 1 of this new regex captures the parent numbers ("2 0")
                parent_match = re.search(rb"/Parent\s+(\d+\s+\d+)\s+R", content)
                
                # Extract the ID if found, otherwise return None (safeguard)
                parent_id = parent_match.group(1) if parent_match else None
                
                extracted_pages.append({
                    'object_id': obj_id,
                    'parent_id': parent_id
                })
    return extracted_pages

def rebuild_page_tree(filename):
    page_objects = [f" {item["object_id"].decode("utf-8")} R" for item in get_page_obj_id(filename)]
    page_count = len(page_objects)
    page_tree_id = get_page_obj_id(filename)[0]["parent_id"]
    template = f'''
{page_tree_id.decode("utf-8")} obj
<<
/Count {page_count}
/Kids [{"".join(page_objects)} ]
/Type /Pages
>>
endobj
'''
    return template

def rebuild_root_obj(filename):
    page_tree_id = get_page_obj_id(filename)[0]["parent_id"]
    template = f'''
1 0 obj
<<
/Pages {page_tree_id.decode("utf-8")} R
/Type /Catalog
>>
endobj
'''
    return template

def overwrite_broken_page_tree(filename):
    xref_section_pattern = re.compile(rb"xref\s+(.*?)\s+trailer", re.DOTALL)
    page_tree = rebuild_page_tree(filename)
    root_obj = rebuild_root_obj(filename)
    with open(filename,"r+b") as file:
        file_data = file.read()
        file_data_array = bytearray(file_data)
        xref_table_content = xref_section_pattern.search(file_data).group(1).decode("utf-8").split("\r\n")
        final_obj_xref_position = int(xref_table_content[-1].split(" ")[0])
        root_xref_position = int(xref_table_content[2].split(" ")[0])
        page_tree_xref_position = int(xref_table_content[3].split(" ")[0])
        final_obj_id = int(xref_table_content[0].split(" ")[-1])-1
        final_obj_pattern= rf"{final_obj_id}\s+0\s+obj".encode("ascii")
        final_obj_position = re.search(final_obj_pattern,file_data_array).start()
        byte_to_shift = final_obj_xref_position - final_obj_position
        fillbyte = b"\x20"
        padding = fillbyte*byte_to_shift
        file_data_array[final_obj_position:final_obj_position] = padding
    
    with open(f"{filename}-fixed.pdf", "wb") as file:
        file.write(file_data_array)
        file.seek(page_tree_xref_position)
        file.write(page_tree.encode("utf-8"))
        file.seek(root_xref_position)
        file.write(root_obj.encode("utf-8"))


if __name__ == '__main__':
    overwrite_broken_page_tree(sys.argv[1])