import sys

magic_number = b'\x25\x50\x44\x46\x2d\x31\x2e\x37\x0a\x0a\x34\x20'

def overwrite_header(filename):
    with  open(filename,"r+b") as f:
        f.seek(0)
        f.write(magic_number)

if __name__ == "__main__":
    # if(argc < 2):
    #     print("Usage: FixBrokenHeader.py [filename]")
    #     return
    filename = sys.argv[1]
    overwrite_header(filename)