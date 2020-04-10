import os
import zipfile

srcext_list = ['.c', '.h', '.cpp', '.hpp', '.txt']
binext_list = ['.dll', '.obj', '.o', '.a']
arcext_list = ['.zip', '.gz', '.tar', '.Z']

src_list = []
bin_list = []
arc_list = []
other_list = []
folders_binonly_list = []

def process_zip(name,path):
    with zipfile.ZipFile(path, 'r') as zf:
         for f in zf.infolist():
             checkfile(os.path.basename(f.filename), path + "#" + f.filename, f.compress_size)

def checkfile(name, path, size):
    global count_files
    global size_binlarge
    count_files = count_files + 1
    print(path)
    dot = name.find(".")
    if (dot >= 0):
        if name[dot:] in srcext_list:
            src_list.append(path)
            print("source")
        elif name[dot:] in binext_list:
            bin_list.append(path)
            if size > 100000:
                size_binlarge += size
            print("binary")
        elif name[dot:] in arcext_list:
            arc_list.append(path)
            print("archive")
            if name[dot:] == '.zip':
            	process_zip(name, path)
        else:
            print("other")
            other_list.append(path)
    else:
        print("other")
        other_list.append(path)

def process(path):
    totalsize = 0
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            totalsize += process(entry.path)
        else:
            checkfile(entry.name, entry.path, entry.stat(follow_symlinks=False).st_size)
            totalsize += entry.stat(follow_symlinks=False).st_size
    return totalsize

count_files = 0
size_binlarge = 0

print("Total file size = {}".format(process(".")))
print("Total files processed = {}".format(count_files))
print("Source files = {}".format(len(src_list)))
print("Binary files = {}".format(len(bin_list)))
print("Archive files = {}".format(len(arc_list)))
print("Other files = {}".format(len(other_list)))
print("Large binary file size = {}".format(size_binlarge))
