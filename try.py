import os
import zipfile
from math import trunc
import tempfile
import io

srcext_list = ['.c', '.h', '.cpp', '.hpp', '.txt', '.js']
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
crc_dict = {}

dup_dir_dict = {}
dup_large_dict = {}

dir_dict = {}
large_dict = {}
arc_files_dict = {}

#tempdir = tempfile.mkdtemp()

# EXAMPLE EXTRACT ZIP FROM ZIP
# with zipfile.ZipFile('zip2.zip') as z:
# 	with z.open('zip1.zip') as z2:
# 		z2_filedata =  io.BytesIO(z2.read())
# 		with zipfile.ZipFile(z2_filedata) as nested_zip:
# 			print( nested_zip.open('try.py').read())

def process_zip(name, path, depth, zipinfo):
#
# zipinfo is a zipinfo entry - if None then file should be processed otherwise process zipinfo
	print("Processing {}".format(path))
	depth += 1
	if zipinfo == None:
		with zipfile.ZipFile(path, 'r') as zf:
			for zinfo in zf.infolist():
				fullpath = path + "##" + zinfo.filename
				arc_files_dict[fullpath] = zinfo.CRC
				dot = zinfo.filename.rfind(".")
				if dot > 1:
					if zinfo.filename[dot:] == ".zip":
# 						zf.extract(zinfo, os.path.join(tempdir, newzpath))
# 						print(os.path.join(tempdir, newzpath))
# 						process_zip(zinfo.filename, fullpath, depth)
						with zf.open(zinfo.filename) as z2:
							z2_filedata =  io.BytesIO(z2.read())
							try:
								with zipfile.ZipFile(z2_filedata) as nested_zip:
									print("Processing zip in zip {}".format(zinfo.filename))
									process_zip(zinfo.filename, fullpath, depth, nested_zip)
# 									print( nested_zip.open('try.py').read())
							except:
								print("ERROR: Can't open zip")
								return
	else:
		for zinfo in zipinfo.infolist():
			fullpath = path + "##" + zinfo.filename
			arc_files_dict[fullpath] = zinfo.CRC
			dot = zinfo.filename.rfind(".")
			if dot > 1:
				if zinfo.filename[dot:] == ".zip":
# 						zf.extract(zinfo, os.path.join(tempdir, newzpath))
# 						print(os.path.join(tempdir, newzpath))
# 						process_zip(zinfo.filename, fullpath, depth)
					try:
						with z.open(zinfo.filename) as z2:
							z2_filedata =  io.BytesIO(z2.read())
							with zipfile.ZipFile(z2_filedata) as nested_zip:
								print("Processing zip in zip {}".format(zinfo.filename))
								process_zip(zinfo.filename, fullpath, depth, nested_zip)
# 								print( nested_zip.open('try.py').read())
					except:
						print("ERROR: Can't open zip")
						return

def checkfile(name, path, size, depth):
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
			if name[dot:] == '.zip':
				process_zip(name, path, depth, None)
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

def process_dir(path, depth):
	global count_dirs
	dir_size = 0
	dir_entries = 0
	filenames_string = ""

	dir_dict[path] = {}
	depth += 1
	for entry in os.scandir(path):
		dir_entries += 1
		filenames_string += entry.name + ";"
		if entry.is_dir(follow_symlinks=False):
			count_dirs += 1
			dir_size += process_dir(entry.path, depth)
		else:
			checkfile(entry.name, entry.path, entry.stat(follow_symlinks=False).st_size, depth)
			dir_size += entry.stat(follow_symlinks=False).st_size
	dir_dict[path]['num_entries'] = dir_entries
	dir_dict[path]['size'] = dir_size
	dir_dict[path]['depth'] = depth
	dir_dict[path]['filenamesstring'] = filenames_string
	return dir_size

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
					if path.find("##") > 0:
						if arc_files_dict.get(path) != None:
							test = get_crc(cpath) and arc_files_dict[path]
					elif cpath.find("##") > 0:
						if arc_files_dict.get(cpath) != None:
							test = get_crc(path) and arc_files_dict[cpath]						
					else:
						test = filecmp.cmp(path, cpath, True)
					if test and dup_large_dict.get(cpath) == None and dup_dir_dict.get(os.path.dirname(path)) == None and dup_dir_dict.get(os.path.dirname(cpath)) == None:
						dup_large_dict[path] = cpath
						total_dup_size += size
						count_dups += 1
						print("- Dup large file - {}, {} (size {}MB)".format(path,cpath,trunc(size/1000000)))
	return(count_dups, total_dup_size)

def process_dirdups():
	count_dupdirs = 0
	size_dupdirs = 0
	count = 0
	items = len(dir_dict)
	print("Processing Folders .", end="", flush=True)
	for apath, adict in dir_dict.items():
		count += 1
		#print(count, count % (items//100) )
		if count % ((items//50) + 1) == 0:
			print(".", end="", flush=True)
		if adict['num_entries'] == 0 or adict['size'] == 0:
			continue
		for cpath, cdict in dir_dict.items():
			if apath != cpath:
				if adict['num_entries'] == cdict['num_entries'] and adict['size'] == cdict['size'] and adict['filenamesstring'] == cdict['filenamesstring']:
					if not (dup_dir_dict.get(apath) == cpath or dup_dir_dict.get(cpath) == apath):
						#
						# Need to check whether this dupdir exists or can replace existing entries (is higher up)
						keydir = ""
						valuedir = ""
						if adict['depth'] <= cdict['depth']:
							keydir = apath
							valuedir = cpath
							#print("- Dup folder - {}, {} (size {}MB)".format(apath,cpath, trunc(dir_dict[apath]['size']/1000000)))
						else:
							keydir = cpath
							valuedir = apath
							#print("- Dup folder - {}, {} (size {}MB)".format(cpath,apath, trunc(dir_dict[apath]['size']/1000000)))
						checkdir = valuedir
						found = False
						while checkdir != "":
							checkdir = os.path.dirname(checkdir)
							if checkdir in dup_dir_dict.keys() or checkdir in dup_dir_dict.values():
								found = True
								break

						if found == False:
							dup_dir_dict[keydir] = valuedir
							count_dupdirs += 1
							size_dupdirs += adict['size']
	print(" OK\n- {} Duplicate folders identified".format(count_dupdirs))
	
	return(count_dupdirs, size_dupdirs)

def check_singlefiles():
	# Check for singleton js & other single files
	sfmatch = False
	sf_list = []
	for thisfile in src_list:
		dot = thisfile.rfind(".")
		if (dot > 1) and thisfile[dot:] == '.js':
			# get dir
			# check for .js in filenamesstring
			thisdir = dir_dict.get(os.path.dirname(thisfile))
			if os.path.basename(os.path.dirname(thisfile)) == "node_modules":
				continue
			if thisdir != None:
				all_js = True
				for filename in thisdir['filenamesstring'].split(';'):
					srcdot = filename.rfind('.')
					if srcdot > 1 and filename[srcdot:] != '.js':
						all_js = False
					else:
						all_js = False
				if not all_js:
					sfmatch = True
					sf_list.append(thisfile)
	if sfmatch:
		print("- Consider using Single file matching - singleton .js files found:")
		for thisfile in sf_list:
			print("    {}".format(thisfile))

def get_crc(myfile):
	import zlib
	buffersize = 65536

	crcvalue = 0
	with open(myfile, 'rb') as afile:
		buffr = afile.read(buffersize)
		while len(buffr) > 0:
			crcvalue = zlib.crc32(buffr, crcvalue)
			buffr = afile.read(buffersize)
	return(crcvalue)

#def check_binaryscan():

count_files = 0
size_total = 0
size_large = 0
size_huge = 0
count_dirs = 0

process_dir(".", 0)

print("INFO:")
print("- Total files processed = {}".format(count_files))
print("- Total file size = {}MB".format(trunc(size_total/1000000)))
print("- Folders = {}".format(count_dirs))
print("- Source files = {}".format(len(src_list)))
print("- Binary files = {}".format(len(bin_list)))
print("- Jar files = {}".format(len(jar_list)))
print("- Archive files = {}".format(len(arc_list)))
print("- Other files = {}".format(len(other_list)))
print("- Large files (>500KB) = {} (Total size {}MB)".format(len(large_list), trunc(size_large/1000000)))
print("- Huge files (>10MB) = {} (Total size {}MB)".format(len(huge_list), trunc(size_huge/1000000)))

print("\nDUPLICATES:")

# Find duplicates without expanding archives - to avoid processing dups
num_dirdups, size_dirdups = process_dirdups()
num_dups, size_dups = process_largefiledups()
if (num_dups + num_dirdups == 0):
	print("    None")

# Produce Recommendations
print("\nRECOMMENDATIONS:")
if size_dirdups > 20000000:
	print("- Remove duplicate folders or create .bdignore (save {}MB)".format(trunc(size_dirdups/1000000)))
	print("    Example .bdignore file:")
	for apath, bpath in dup_dir_dict.items():
		print("    {}".format(bpath))
	print("")
if size_dups > 20000000:
	print("- Remove large duplicate files (save {}MB):".format(trunc(size_dups/1000000)))
	for apath, bpath in dup_large_dict.items():
		if dup_dir_dict.get(os.path.dirname(apath)) == None and dup_dir_dict.get(os.path.dirname(bpath)) == None:
			print("    {}".format(bpath))
	print("")

check_singlefiles()
#check_binaryscan()

print("")