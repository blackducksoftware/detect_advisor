import os
import zipfile

srcext_list = ['.c', '.h', '.cpp', '.hpp', '.txt']
binext_list = ['.dll', '.obj', '.o', '.a']
arcext_list = ['.zip', '.gz', '.tar', '.Z']
jarext_list = ['.jar', '.ear', '.war']

src_list = []
bin_list = []
large_list = []
huge_list = []
arc_list = []
jar_list = []
other_list = []

dup_dir_dict = {}
dup_large_dict = {}

dir_dict = {}
large_dict = {}

def process_zip(name,path):
	with zipfile.ZipFile(path, 'r') as zf:
		 for f in zf.infolist():
			 checkfile(os.path.basename(f.filename), path + "#" + f.filename, f.compress_size)

def checkfile(name, path, size):
	global size_total
	global count_files
	global size_large
	global size_huge
	count_files = count_files + 1
	size_total += size
	#print(path)
	dot = name.rfind(".")
	if (dot > 1):
		if name[dot:] in srcext_list:
			src_list.append(path)
			#print("source")
		elif name[dot:] in jarext_list:
			jar_list.append(path)
			#print("jar")
		elif name[dot:] in binext_list:
			bin_list.append(path)
			#print("binary")
		elif name[dot:] in arcext_list:
			arc_list.append(path)
			#print("archive")
			#if name[dot:] == '.zip':
			#	process_zip(name, path)
		else:
			#print("other")
			other_list.append(path)
	else:
		#print("other")
		other_list.append(path)
	if size > 10000000:
		huge_list.append(path)
		size_huge += size
		large_dict[path] = size
		#print("huge")
	elif size > 500000:
		large_list.append(path)
		size_large += size
		large_dict[path] = size

def process_dir(path):
	global count_dirs
	dir_size = 0
	dir_files = 0
	filenames_string = ""
	
	dir_dict[path] = {}
	for entry in os.scandir(path):
		if entry.is_dir(follow_symlinks=False):
			count_dirs += 1
			process_dir(entry.path)
		else:
			checkfile(entry.name, entry.path, entry.stat(follow_symlinks=False).st_size)
			dir_size += entry.stat(follow_symlinks=False).st_size
			dir_files += 1
			filenames_string += entry.name + ";"
	dir_dict[path]['num_files'] = dir_files
	dir_dict[path]['size'] = dir_size
	dir_dict[path]['filenamesstring'] = filenames_string

def process_largefiledups():
	import filecmp
	total_dup_size = 0
	count_dups = 0
	for path, size in large_dict.items():
		dup = False
		for cpath, csize in large_dict.items():
			if path == cpath:
				continue
			if size == csize:
				dot = path.rfind(".")
				cdot = cpath.rfind(".")
				if (dot > 1) and (cdot > 1):
					if path[dot:] == cpath[cdot:]:
						dup = True
				elif (dot == 0) and (cdot == 0):
					dup = True
				if dup:
					if filecmp.cmp(path, cpath, True):
						dup_large_dict[path] = cpath
						total_dup_size += size
						count_dups += 1
						print("Dup large file - {}, {}".format(path,cpath))
	return(count_dups, total_dup_size)						

def process_dirdups():
	count_dupdirs = 0
	size_dupdirs = 0
	for apath, adict in dir_dict.items():
		if adict['num_files'] == 0:
			continue
		for cpath, cdict  in dir_dict.items():
			if apath != cpath:
				if adict['num_files'] == cdict['num_files'] and adict['size'] == cdict['size'] and adict['filenamesstring'] == cdict['filenamesstring']:
					print("Dup folder - {}, {}".format(apath,cpath))
					dup_dir_dict[apath] = cpath
					count_dupdirs += 1
					size_dupdirs += adict['size']
	return(count_dupdirs, size_dupdirs)

count_files = 0
size_total = 0
size_large = 0
size_huge = 0
count_dirs = 0

process_dir(".")

print("Total files processed = {}".format(count_files))
print("Total file size = {}".format(size_total))
print("Folders = {}".format(count_dirs))
print("Source files = {}".format(len(src_list)))
print("Binary files = {}".format(len(bin_list)))
print("Jar files = {}".format(len(jar_list)))
print("Archive files = {}".format(len(arc_list)))
print("Other files = {}\n".format(len(other_list)))

print("Large files (>500KB) = {} (Total size {})".format(len(large_list), size_large))
print("Huge files (>10MB) = {} (Total size {})\n".format(len(huge_list), size_huge))

num_dups, size_dups = process_largefiledups()
if size_dups > 50000000:
	print("RECOMMENDATION: Remove large duplicate files (save {}MB)".format(size_dups/1000000))
num_dirdups, size_dirdups = process_dirdups()
if size_dirdups > 50000000:
	print("RECOMMENDATION: Remove duplicate folders or create .bdignore (save {}MB)".format(size_dirdups/1000000))
