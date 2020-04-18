import os
import zipfile
from math import trunc
import tempfile
import io

#
# Constants
srcext_list = ['.c', '.h', '.cpp', '.hpp', '.txt', '.js']
binext_list = ['.dll', '.obj', '.o', '.a', '.iso']
arcext_list = ['.zip', '.gz', '.tar', '.Z']
jarext_list = ['.jar', '.ear', '.war']

largesize = 1000000
hugesize = 20000000

notinarc = 0
inarc = 1
inarcunc = 1
inarccomp = 2

#
# Variables
max_arc_depth = 0

counts = {
'file' : [0,0],
'dir' : [0,0],
'arc' : [0,0],
'bin' : [0,0],
'jar' : [0,0],
'src' : [0,0],
'large' : [0,0],
'huge' : [0,0],
'other' : [0,0]
}

sizes = {
'file' : [0,0,0],
'dir' : [0,0,0],
'arc' : [0,0,0],
'bin' : [0,0,0],
'jar' : [0,0,0],
'src' : [0,0,0],
'large' : [0,0,0],
'huge' : [0,0,0],
'other' : [0,0,0]
}

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

def process_zip(name, path, zipdepth, zipinfo):
#
# zipinfo is a zipinfo entry - if None then file should be processed otherwise process zipinfo
#	print("Processing {}".format(path))
	global max_arc_depth
	
	zipdepth += 1
	if zipdepth > max_arc_depth:
		max_arc_depth = zipdepth
	if zipinfo == None:
		with zipfile.ZipFile(path, 'r') as zf:
			for zinfo in zf.infolist():
				fullpath = path + "##" + zinfo.filename
				if zinfo.is_dir():
					continue
				#
				# Process folder containing file in zip
				tdir = path + "##" + os.path.dirname(zinfo.filename)
				if tdir not in dir_dict.keys():
					counts['dir'][inarc] += 1
					dir_dict[tdir] = {}
					dir_dict[tdir]['num_entries'] = 1
					dir_dict[tdir]['size'] = zinfo.file_size
					dir_dict[tdir]['depth'] = 0
					dir_dict[tdir]['filenamesstring'] = zinfo.filename + ";"
				else:
					dir_dict[tdir]['num_entries'] += 1
					dir_dict[tdir]['size'] += zinfo.file_size
					dir_dict[tdir]['depth'] = 0
					dir_dict[tdir]['filenamesstring'] += zinfo.filename + ";"
				
				counts['file'][inarc] += 1
				arc_files_dict[fullpath] = zinfo.CRC
				checkfile(zinfo.filename, fullpath, zinfo.file_size, zinfo.compress_size)
				dot = zinfo.filename.rfind(".")
				if dot > 1:
					if zinfo.filename[dot:] == ".zip":
						arc_list.append(fullpath)
						with zf.open(zinfo.filename) as z2:
							z2_filedata =  io.BytesIO(z2.read())
							try:
								with zipfile.ZipFile(z2_filedata) as nested_zip:
									#print("Processing zip in zip {}".format(zinfo.filename))
									process_zip(zinfo.filename, fullpath, zipdepth, nested_zip)
							except:
								print("WARNING: Can't open zip {} (Skipped)".format(fullpath))
								continue
	else:
		for zinfo in zipinfo.infolist():
			fullpath = path + "##" + zinfo.filename
			if not zinfo.is_dir():
				counts['dir'][inarc] += 1
			else:
				counts['file'][inarc] += 1
			arc_files_dict[fullpath] = zinfo.CRC
			checkfile(zinfo.filename, fullpath, zinfo.file_size, zinfo.compress_size)
			dot = zinfo.filename.rfind(".")
			if dot > 1:
				if zinfo.filename[dot:] == ".zip":
					try:
						with z.open(zinfo.filename) as z2:
							z2_filedata =  io.BytesIO(z2.read())
							with zipfile.ZipFile(z2_filedata) as nested_zip:
								print("Processing zip in zip {}".format(zinfo.filename))
								process_zip(zinfo.filename, fullpath, zipdepth, nested_zip)
					except:
						print("WARNING: Can't open zip {} (Skipped)".format(fullpath))
						continue

def checkfile(name, path, size, size_comp):
	if size_comp == 0:
		counts['file'][notinarc] += 1
		sizes['file'][notinarc] += size
	else:
		counts['file'][inarc] += 1
		sizes['file'][inarcunc] += size
		sizes['file'][inarccomp] += size_comp
	dot = name.rfind(".")
	if (dot > 1):
		if name[dot:] in srcext_list:
			src_list.append(path)
			ftype = 'src'
		elif name[dot:] in jarext_list:
			jar_list.append(path)
			ftype = 'jar'
		elif name[dot:] in binext_list:
			bin_list.append(path)
			ftype = 'bin'
		elif name[dot:] in arcext_list:
			arc_list.append(path)
			ftype = 'arc'
		else:
			#print("other")
			other_list.append(path)
			ftype = 'other'			
	else:
		ftype = 'other'
		other_list.append(path)

	if size_comp == 0:
		counts[ftype][notinarc] += 1
		sizes[ftype][notinarc] += size
	else:
		counts[ftype][inarc] += 1
		sizes[ftype][inarcunc] += size
		sizes[ftype][inarccomp] += size_comp

	if size > hugesize:
		huge_list.append(path)
		large_dict[path] = size
		if size_comp == 0:
			counts['huge'][notinarc] += 1
			sizes['huge'][notinarc] += size
		else:
			counts['huge'][inarc] += 1
			sizes['huge'][inarcunc] += size
			sizes['huge'][inarccomp] += size_comp
	elif size > largesize:
		large_list.append(path)
		large_dict[path] = size
		if size_comp == 0:
			counts['large'][notinarc] += 1
			sizes['large'][notinarc] += size
		else:
			counts['large'][inarc] += 1
			sizes['large'][inarcunc] += size
			sizes['large'][inarccomp] += size_comp

def process_dir(path, depth):
	dir_size = 0
	dir_entries = 0
	filenames_string = ""

	dir_dict[path] = {}
	depth += 1
	for entry in os.scandir(path):
		dir_entries += 1
		filenames_string += entry.name + ";"
		if entry.is_dir(follow_symlinks=False):
			counts['dir'][notinarc] += 1
			dir_size += process_dir(entry.path, depth)
		else:
			checkfile(entry.name, entry.path, entry.stat(follow_symlinks=False).st_size, 0)
			dot = entry.name.rfind(".")
			if entry.name[dot:] == '.zip':
				process_zip(entry.name, entry.path, depth, None)

			dir_size += entry.stat(follow_symlinks=False).st_size
	dir_dict[path]['num_entries'] = dir_entries
	dir_dict[path]['size'] = dir_size
	dir_dict[path]['depth'] = depth
	dir_dict[path]['filenamesstring'] = filenames_string
	return dir_size

def process_largefiledups():
	import filecmp
	fcount = 0
	total_dup_size = 0
	count_dups = 0
	fitems = len(large_dict)
	for apath, asize in large_dict.items():
		fcount += 1
		if fcount % ((fitems//5) + 1) == 0:
			print(".", end="", flush=True)
		dup = False
		for cpath, csize in large_dict.items():
			if apath == cpath:
				continue
			if asize == csize:
				adot = apath.rfind(".")
				cdot = cpath.rfind(".")
				if (adot > 1) and (cdot > 1):
					if apath[adot:] == cpath[cdot:]:
						dup = True
				elif (adot == 0) and (cdot == 0):
					dup = True
				if dup:
					if apath.find("##") > 0 or cpath.find("##") > 0:
						if apath.find("##") > 0:
							acrc = arc_files_dict[apath]
						else:
							acrc = get_crc(apath)
						if cpath.find("##") > 0:
							ccrc = arc_files_dict[cpath]
						else:
							ccrc = get_crc(cpath)
						test = (acrc == ccrc)
					else:
						test = filecmp.cmp(apath, cpath, True)

					if test and dup_large_dict.get(cpath) == None and dup_dir_dict.get(os.path.dirname(apath)) == None and dup_dir_dict.get(os.path.dirname(cpath)) == None:
						dup_large_dict[apath] = cpath
						total_dup_size += asize
						count_dups += 1
						#print("- Dup large file - {}, {} (size {}MB)".format(apath,cpath,trunc(asize/1000000)))
	return(count_dups, total_dup_size)

def process_dirdups():
	count_dupdirs = 0
	size_dupdirs = 0
	dcount = 0
	ditems = len(dir_dict)
	for apath, adict in dir_dict.items():
		dcount += 1
		#print(count, count % (items//100) )
		if dcount % ((ditems//5) + 1) == 0:
			print(".", end="", flush=True)
		if adict['num_entries'] == 0 or adict['size'] == 0:
			continue
		for cpath, cdict in dir_dict.items():
			if apath != cpath:
#				print(apath, cpath)
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
		print("- Consider using Single file matching - {} singleton .js files found".format(len(sf_list)))
# 		for thisfile in sf_list:
# 			print("    {}".format(thisfile))

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

def print_summary():
	print("\nSUMMARY INFO:            Num Outside     Size Outside      Num Inside     Size Inside     Size Inside")
	print("                            Archives         Archives        Archives        Archives        Archives")
	print("                                                                        (UNcompressed)    (compressed)")
	
	row = "{:25} {:>10,d}    {:>10,d} MB      {:>10,d}   {:>10,d} MB   {:>10,d} MB"
	print("{:25} {:>10,d}    {:>10,d} MB             N/A             N/A             N/A   ".format("All Files", \
	counts['file'][notinarc]+counts['arc'][notinarc], \
	trunc((sizes['file'][notinarc]+sizes['arc'][notinarc])/1000000)))
	print("--------------------  --------------   --------------   -------------   -------------   -------------")

	print(row.format("Files (exc. Archives)", \
	counts['file'][notinarc], \
	trunc(sizes['file'][notinarc]/1000000), \
	counts['file'][1], \
	trunc(sizes['file'][1]/1000000), \
	trunc(sizes['file'][2]/1000000)))

	print(row.format("Archives", \
	counts['arc'][0], \
	trunc(sizes['arc'][0]/1000000), \
	counts['arc'][1], \
	trunc(sizes['arc'][1]/1000000), \
	trunc(sizes['arc'][2]/1000000)))
	print("--------------------  --------------   --------------   -------------   -------------   -------------")
	
	print("{:25} {:>10,d}              N/A      {:>10,d}             N/A             N/A   ".format("Folders", \
	counts['dir'][0], \
	trunc(sizes['dir'][0]/1000000), \
	counts['dir'][1], \
	trunc(sizes['dir'][1]/1000000), \
	trunc(sizes['dir'][2]/1000000)))
	
	print(row.format("Source Files", \
	counts['src'][0], \
	trunc(sizes['src'][0]/1000000), \
	counts['src'][1], \
	trunc(sizes['src'][1]/1000000), \
	trunc(sizes['src'][2]/1000000)))

	print(row.format("JAR Archives", \
	counts['jar'][0], \
	trunc(sizes['jar'][0]/1000000), \
	counts['jar'][1], \
	trunc(sizes['jar'][1]/1000000), \
	trunc(sizes['jar'][2]/1000000)))

	print(row.format("Binary Files", \
	counts['bin'][0], \
	trunc(sizes['bin'][0]/1000000), \
	counts['bin'][1], \
	trunc(sizes['bin'][1]/1000000), \
	trunc(sizes['bin'][2]/1000000)))

	print(row.format("Other Files", \
	counts['other'][0], \
	trunc(sizes['other'][0]/1000000), \
	counts['other'][1], \
	trunc(sizes['other'][1]/1000000), \
	trunc(sizes['other'][2]/1000000)))

	print(row.format("Large Files (>{:1d}MB)".format(trunc(largesize/1000000)), \
	counts['large'][0], \
	trunc(sizes['large'][0]/1000000), \
	counts['large'][1], \
	trunc(sizes['large'][1]/1000000), \
	trunc(sizes['large'][2]/1000000)))

	print(row.format("Huge Files (>{:2d}MB)".format(trunc(hugesize/1000000)), \
	counts['huge'][0], \
	trunc(sizes['huge'][0]/1000000), \
	counts['huge'][1], \
	trunc(sizes['huge'][1]/1000000), \
	trunc(sizes['huge'][2]/1000000)))
	print("--------------------  --------------   --------------   -------------   -------------   -------------")

print("\nPROCESSING:")

print("- Reading folders        .....", end="", flush=True)
process_dir(".", 0)
print(" Done")

# Find duplicates without expanding archives - to avoid processing dups
print("- Processing folders     ", end="", flush=True)
num_dirdups, size_dirdups = process_dirdups()
print(" Done")

print("- Processing large files ", end="", flush=True)
num_dups, size_dups = process_largefiledups()
print(" Done")

if (num_dups + num_dirdups == 0):
	print("    None")

print_summary()

# Produce Recommendations
print("\nRECOMMENDATIONS:")
if size_dirdups > 20000000:
	print("- Remove duplicate folders or create .bdignore (save {}MB)".format(trunc(size_dirdups/1000000)))
	#print("    Example .bdignore file:")
	#for apath, bpath in dup_dir_dict.items():
	#	print("    {}".format(bpath))
	#print("")
if size_dups > 20000000:
	print("- Remove large duplicate files (save {}MB):".format(trunc(size_dups/1000000)))
	#for apath, bpath in dup_large_dict.items():
	#	if dup_dir_dict.get(os.path.dirname(apath)) == None and dup_dir_dict.get(os.path.dirname(bpath)) == None:
	#		print("    {}".format(bpath))
	#print("")

check_singlefiles()
#check_binaryscan()

print("")