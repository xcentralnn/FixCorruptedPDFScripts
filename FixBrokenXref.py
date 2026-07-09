import sys
import re

obj_pattern = b'\x20\x6f\x62\x6a'
endobj_pattern = b'\x65\x6e\x64\x6f\x62\x6a'

def count_obj(filename):
    with open(filename, 'rb') as file:
        file_data = file.read()
        return file_data.count(obj_pattern)

def list_position(filename, pattern):
    offsets=[]
    start = 0
    with open(filename,'rb') as file:
        file_data = file.read()
        while True:
            pos = file_data.find(pattern, start)
            if pos == -1:
                break
            offsets.append(pos-4)
            start = pos + 1
    return offsets

def generate_xref_table(filename):
    # keyword='xref'
    number_of_object=count_obj(filename)
    obj_list = list_position(filename,obj_pattern)
    table=list()
    # table.append(keyword)
    table.append(f'{0} {number_of_object+1}')
    table.append('0000000000 65535 f')
    for i in range(0,number_of_object):
        table.append(f'{obj_list[i]:010} 00000 n')
    return table

def find_regex(filename):
    xref_section_pattern = b"xref\s+(.*?)\s+trailer"
    new_table = '\n'.join(generate_xref_table(filename))
    new_content=b''
    with open(filename,'r+b') as file:
        file_data = file.read()
        file_data_array = bytearray(file_data)
        if re.search(xref_section_pattern,file_data):
            new_content = re.sub(xref_section_pattern, new_table,file_data)
            file.write(new_content)
        else:
            last_endobj_position = list(re.finditer(endobj_pattern, file_data))[-1].start()
            fillbyte = b"\x20"
            byte_to_shift = len(new_table)
            padding = fillbyte*(byte_to_shift+6)
            file_data_array[last_endobj_position+6:last_endobj_position+6] = ("\nxref\n" + new_table).encode("ascii")
        
        with open(f"{filename.split(".")[0]}-fixed.pdf","wb") as file:
            file.write(file_data_array)


            

        #     print("No match found.")
    # with open(filename,"wb") as new_file:
    #     new_file.write(new_content)



if __name__ == "__main__":
    #count_obj(sys.argv[1])
    # print(list_position(sys.argv[1],obj_pat tern))
    # print(list_position(sys.argv[1],endobj_pattern))
    # for i in generate_xref_table(sys.argv[1]):
    #     print(i)
    find_regex(sys.argv[1])