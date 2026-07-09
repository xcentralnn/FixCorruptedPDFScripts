import sys
import re

def count_obj(filename):
    obj_pattern = b'\x20\x6f\x62\x6a'
    with open(filename, 'rb') as file:
        file_data = file.read()
        return file_data.count(obj_pattern)

def get_xref_position(filename):
    keyword = b'\x78\x72\x65\x66'
    with open(filename,'rb') as file:
        file_data = file.read()
        position = file_data.find(keyword)
    return position

def create_new_trailer(filename):
    template = f'''trailer
<<
/Root 1 0 R
/size {count_obj(filename)+1}
>>
startxref
{get_xref_position(filename)}
%%EOF'''
    return template

def overwrite_trailer(filename):
    keyword = b'\x74\x72\x61\x69\x6C\x65\x72'
    trailer_re = b'trailer.*'
    template = create_new_trailer(filename)
    with open(filename,'r+b') as file:
        file_data = file.read()
        if file_data.find(keyword) != -1:
            print("Trailer found, replacing trailer")
            new_file = re.sub(trailer_re,template.encode('utf-8'),file_data,flags=re.DOTALL)
            file.seek(0)
            file.write(new_file)
        else:
            print("Trailer not detected, writing new trailer")
            file.seek(0,2)
            file.write(template)

if __name__ == '__main__':
    # print(get_xref_position(sys.argv[1]))
    overwrite_trailer(sys.argv[1])