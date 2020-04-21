import os
import zipfile
from math import trunc
#import tempfile
import io
import argparse

#
# Constants
srcext_list = ['.R','.actionscript','.ada','.adb','.ads','.aidl','.as','.asm','.asp',\
'.aspx','.awk','.bas','.bat','.bms','.c','.c++','.cbl','.cc','.cfc','.cfm','.cgi','.cls',\
'.cpp','.cpy','.cs','.cxx','.el','.erl','.f','.f77','.f90','.for','.fpp','.frm','.fs',\
'.g77','.g90','.go','.groovy','.h','.hh','.hpp','.hrl','.hxx','.idl','.java','.js','.jsp',\
'.jws','.l','.lisp','.lsp','.lua','.m','.m4','.mm','.pas','.php','.php3','.php4','.pl',\
'.pm','.py','.rb','.rc','.rexx','.s','.scala','.scm','.sh','.sqb','.sql','.tcl','.tk',\
'.v','.vb','.vbs','.vhd','.vhdl','.y']
binext_list = ['.dll', '.obj', '.o', '.a', '.lib', '.iso', '.qcow2', '.vmdk', '.vdi', \
'.ova', '.nbi', '.vib', '.exe', '.img', '.bin', '.apk', '.aac', '.ipa', '.msi']
arcext_list = ['.zip', '.gz', '.tar', '.xz', '.lz', '.bz2', '.7z', '.rar', '.rar', \
'.cpio', '.Z', '.lz4', '.lha', '.arj']
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

def process_nested_zip(z, zippath, zipdepth):
	global max_arc_depth

	zipdepth += 1
	if zipdepth > max_arc_depth:
		max_arc_depth = zipdepth

	#print("ZIP:{}:{}".format(zipdepth, zippath))
	z2_filedata =  io.BytesIO(z.read())
	try:
		with zipfile.ZipFile(z2_filedata) as nz:
			for zinfo in nz.infolist():
				process_zip_entry(zinfo, zippath)
				if os.path.splitext(zinfo.filename)[1] == ".zip":
					with nz.open(zinfo.filename) as z2:
						process_nested_zip(z2, zippath + "##" + zinfo.filename, zipdepth)
	except:
		print("WARNING: Can't open zip {} (Skipped)".format(zippath))


def process_zip_entry(zinfo, zippath):
	#print("ENTRY:" + zippath + "##" + zinfo.filename)
	fullpath = zippath + "##" + zinfo.filename
	tdir = zippath + "##" + os.path.dirname(zinfo.filename)
	if tdir not in dir_dict.keys():
		counts['dir'][inarc] += 1
		dir_dict[tdir] = {}
		dir_dict[tdir]['num_entries'] = 1
		dir_dict[tdir]['size'] = zinfo.file_size
		dir_dict[tdir]['depth'] = 10
		dir_dict[tdir]['filenamesstring'] = zinfo.filename + ";"
	else:
		dir_dict[tdir]['num_entries'] += 1
		dir_dict[tdir]['size'] += zinfo.file_size
		dir_dict[tdir]['depth'] = 10
		dir_dict[tdir]['filenamesstring'] += zinfo.filename + ";"

	arc_files_dict[fullpath] = zinfo.CRC
	checkfile(zinfo.filename, fullpath, zinfo.file_size, zinfo.compress_size, True)

def process_zip(zippath, zipdepth):
	global max_arc_depth

	zipdepth += 1
	if zipdepth > max_arc_depth:
		max_arc_depth = zipdepth

	#print("ZIP:{}:{}".format(zipdepth, zippath))
	try:
		with zipfile.ZipFile(zippath) as z:
			for zinfo in z.infolist():
				if zinfo.is_dir():
					continue
				fullpath = zippath + "##" + zinfo.filename
				process_zip_entry(zinfo, zippath)
				if os.path.splitext(zinfo.filename)[1] == ".zip":
					with z.open(zinfo.filename) as z2:
						process_nested_zip(z2, fullpath, zipdepth)
	except:
		print("WARNING: Can't open zip {} (Skipped)".format(zippath))

def checkfile(name, path, size, size_comp, inarc):
	ext = os.path.splitext(name)[1]
	if ext != ".zip":
		if not inarc:
			counts['file'][notinarc] += 1
			sizes['file'][notinarc] += size
		else:
			counts['file'][inarc] += 1
			sizes['file'][inarcunc] += size
			sizes['file'][inarccomp] += size_comp
		if size > hugesize:
			huge_list.append(path)
			large_dict[path] = size
			if not inarc:
				counts['huge'][notinarc] += 1
				sizes['huge'][notinarc] += size
			else:
				counts['huge'][inarc] += 1
				sizes['huge'][inarcunc] += size
				sizes['huge'][inarccomp] += size_comp
		elif size > largesize:
			large_list.append(path)
			large_dict[path] = size
			if not inarc:
				counts['large'][notinarc] += 1
				sizes['large'][notinarc] += size
			else:
				counts['large'][inarc] += 1
				sizes['large'][inarcunc] += size
				sizes['large'][inarccomp] += size_comp

	if (ext != ""):
		if ext in srcext_list:
			src_list.append(path)
			ftype = 'src'
		elif ext in jarext_list:
			jar_list.append(path)
			ftype = 'jar'
		elif ext in binext_list:
			bin_list.append(path)
			ftype = 'bin'
		elif ext in arcext_list:
			arc_list.append(path)
			ftype = 'arc'
		else:
			other_list.append(path)
			ftype = 'other'
	else:
		other_list.append(path)
		ftype = 'other'
	#print("name:{} type:{}, size_comp:{}, size:{}".format(name, ftype, size_comp, size))
	if not inarc:
		counts[ftype][notinarc] += 1
		sizes[ftype][notinarc] += size
	else:
		counts[ftype][inarc] += 1
		sizes[ftype][inarcunc] += size
		if size_comp == 0:
			sizes[ftype][inarccomp] += size
		else:
			sizes[ftype][inarccomp] += size_comp


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
			checkfile(entry.name, entry.path, entry.stat(follow_symlinks=False).st_size, 0, False)
			ext = os.path.splitext(entry.name)[1]
			if ext == '.zip':
				process_zip(entry.path, depth)

			dir_size += entry.stat(follow_symlinks=False).st_size
	dir_dict[path]['num_entries'] = dir_entries
	dir_dict[path]['size'] = dir_size
	dir_dict[path]['depth'] = depth
	dir_dict[path]['filenamesstring'] = filenames_string
	return dir_size

def process_largefiledups(f):
	import filecmp

	if f:
		f.write("\nDUPLICATE LARGE FILES:\n")

	fcount = 0
	total_dup_size = 0
	count_dups = 0
	fitems = len(large_dict)
	for apath, asize in large_dict.items():
		fcount += 1
		if fcount % ((fitems//6) + 1) == 0:
			print(".", end="", flush=True)
		dup = False
		for cpath, csize in large_dict.items():
			if apath == cpath:
				continue
			if asize == csize:
				aext = os.path.splitext(apath)[1]
				cext = os.path.splitext(cpath)[1]
				if aext == cext:
					dup = True
				elif aext == "" and cext == "":
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

					if test and dup_large_dict.get(cpath) == None and \
					dup_dir_dict.get(os.path.dirname(apath)) == None and \
					dup_dir_dict.get(os.path.dirname(cpath)) == None:
						dup_large_dict[apath] = cpath
						total_dup_size += asize
						count_dups += 1
						if f:
							f.write("- Dup large file - {}, {} (size {}MB)\n".format(apath,cpath,trunc(asize/1000000)))
	return(count_dups, total_dup_size)

def process_dirdups(f):
	count_dupdirs = 0
	size_dupdirs = 0
	dcount = 0

	tmp_dup_dir_dict = {}

	if f:
		f.write("\nDUPLICATE FOLDERS:\n")

	ditems = len(dir_dict)
	for apath, adict in dir_dict.items():
		dcount += 1
		if dcount % ((ditems//6) + 1) == 0:
			print(".", end="", flush=True)
		if adict['num_entries'] == 0 or adict['size'] < 1000000:
			continue
		dupmatch = False
		for cpath, cdict in dir_dict.items():
			if apath != cpath:
				if adict['num_entries'] == cdict['num_entries'] and adict['size'] == cdict['size'] \
				and adict['filenamesstring'] == cdict['filenamesstring']:
					if adict['depth'] <= cdict['depth']:
						keypath = apath
						valpath = cpath
					else:
						keypath = cpath
						valpath = apath

					newdup = False
					if keypath not in tmp_dup_dir_dict.keys():
						newdup = True
					elif tmp_dup_dir_dict[keypath] != valpath:
						newdup = True
					if newdup:
						tmp_dup_dir_dict[keypath] = valpath
					break

	# Now remove dupdirs with matching parent folders
	for xpath in tmp_dup_dir_dict.keys():
		ypath = tmp_dup_dir_dict[xpath]
		print("Processing folder:" + xpath + " dup " + ypath)
		xdir = os.path.dirname(xpath)
		ydir = os.path.dirname(ypath)
		if xdir in tmp_dup_dir_dict.keys() and tmp_dup_dir_dict[xdir] == ydir:
			# parents match - ignore
			print("Ignorning dup dir: " + xpath + " " + ypath)
		else:
			# Create dupdir entry
			print("Adding dup dir: " + xpath + " " + ypath)
			dup_dir_dict[xpath] = ypath
			count_dupdirs += 1
			size_dupdirs += dir_dict[xpath]['size']
			if f:
				f.write("- Duplicate folder - {}, {} (size {}MB)\n".format(xpath,ypath, \
				trunc(dir_dict[xpath]['size']/1000000)))

	return(count_dupdirs, size_dupdirs)

def check_singlefiles(f):
	# Check for singleton js & other single files
	sfmatch = False
	sf_list = []
	for thisfile in src_list:
		ext = os.path.splitext(thisfile)[1]
		if ext == '.js':
			# get dir
			# check for .js in filenamesstring
			thisdir = dir_dict.get(os.path.dirname(thisfile))
			if thisfile.find("node_modules") > 0:
				continue
			if thisdir != None:
				all_js = True
				for filename in thisdir['filenamesstring'].split(';'):
					srcext = os.path.splitext(filename)[1]
					if srcext != '.js':
						all_js = False
				if not all_js:
					sfmatch = True
					sf_list.append(thisfile)
	if sfmatch:
		print("- INFORMATION: {} singleton .js files found\n	Impact: OSS components within JS files may not be detected\n	Action: Consider specifying Single file matching (--detect.blackduck.signature.scanner.individual.file.matching=SOURCE)".format(len(sf_list)))
		if f:
			f.write("\nSINGLE JS FILES:\n")
			for thisfile in sf_list:
				f.write("- {}\n".format(thisfile))

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

def print_summary():
	print("\nSUMMARY INFO:            Num Outside     Size Outside      Num Inside     Size Inside     Size Inside")
	print("                            Archives         Archives        Archives        Archives        Archives")
	print("                                                                        (UNcompressed)    (compressed)")

	row = "{:25} {:>10,d}    {:>10,d} MB      {:>10,d}   {:>10,d} MB   {:>10,d} MB"
	print("--------------------  --------------   --------------   -------------   -------------   -------------")

	print(row.format("Files (exc. Archives)", \
	counts['file'][notinarc], \
	trunc(sizes['file'][notinarc]/1000000), \
	counts['file'][inarc], \
	trunc(sizes['file'][inarcunc]/1000000), \
	trunc(sizes['file'][inarccomp]/1000000)))

	print(row.format("Archives", \
	counts['arc'][notinarc], \
	trunc(sizes['arc'][notinarc]/1000000), \
	counts['arc'][inarc], \
	trunc(sizes['arc'][inarcunc]/1000000), \
	trunc(sizes['arc'][inarccomp]/1000000)))
	print("--------------------  --------------   --------------   -------------   -------------   -------------")

	print("{:25} {:>10,d}              N/A      {:>10,d}             N/A             N/A   ".format("Folders", \
	counts['dir'][notinarc], \
	counts['dir'][inarc]))

	print(row.format("Source Files", \
	counts['src'][notinarc], \
	trunc(sizes['src'][notinarc]/1000000), \
	counts['src'][inarc], \
	trunc(sizes['src'][inarcunc]/1000000), \
	trunc(sizes['src'][inarccomp]/1000000)))

	print(row.format("JAR Archives", \
	counts['jar'][notinarc], \
	trunc(sizes['jar'][notinarc]/1000000), \
	counts['jar'][inarc], \
	trunc(sizes['jar'][inarcunc]/1000000), \
	trunc(sizes['jar'][inarccomp]/1000000)))

	print(row.format("Binary Files", \
	counts['bin'][notinarc], \
	trunc(sizes['bin'][notinarc]/1000000), \
	counts['bin'][inarc], \
	trunc(sizes['bin'][inarcunc]/1000000), \
	trunc(sizes['bin'][inarccomp]/1000000)))

	print(row.format("Other Files", \
	counts['other'][notinarc], \
	trunc(sizes['other'][notinarc]/1000000), \
	counts['other'][inarc], \
	trunc(sizes['other'][inarcunc]/1000000), \
	trunc(sizes['other'][inarccomp]/1000000)))

	print(row.format("Large Files (>{:1d}MB)".format(trunc(largesize/1000000)), \
	counts['large'][notinarc], \
	trunc(sizes['large'][notinarc]/1000000), \
	counts['large'][inarc], \
	trunc(sizes['large'][inarcunc]/1000000), \
	trunc(sizes['large'][inarccomp]/1000000)))

	print(row.format("Huge Files (>{:2d}MB)".format(trunc(hugesize/1000000)), \
	counts['huge'][notinarc], \
	trunc(sizes['huge'][notinarc]/1000000), \
	counts['huge'][inarc], \
	trunc(sizes['huge'][inarcunc]/1000000), \
	trunc(sizes['huge'][inarccomp]/1000000)))
	print("--------------------  --------------   --------------   -------------   -------------   -------------")

	print(row.format("All Files (Scan size)", counts['file'][notinarc]+counts['arc'][notinarc], \
	trunc((sizes['file'][notinarc]+sizes['arc'][notinarc])/1000000), \
	counts['file'][inarc]+counts['arc'][inarc], \
	trunc((sizes['file'][inarcunc]+sizes['arc'][inarcunc])/1000000), \
	trunc((sizes['file'][inarccomp]+sizes['arc'][inarccomp])/1000000)))

def main_process(folder, repfile):

	if repfile and os.path.exists(repfile):
		print("Report file {} already exists\nExiting".format(repfile))
		return

	if repfile:
		try:
			f = open(repfile, "a")
		except Exception as e:
			print('ERROR: Unable to open output report file \n' + str(e))
			return
	else:
		f = None

	print("\nPROCESSING:")

	print("Working on folder {}".format(folder))

	print("- Reading hierarchy      .....", end="", flush=True)
	process_dir(folder, 0)
	print(" Done")

	# Find duplicates without expanding archives - to avoid processing dups
	print("- Processing folders     ", end="", flush=True)
	num_dirdups, size_dirdups = process_dirdups(f)
	print(" Done")

	print("- Processing large files ", end="", flush=True)
	num_dups, size_dups = process_largefiledups(f)
	print(" Done")

	if (num_dups + num_dirdups == 0):
		print("    None")

	print_summary()

	# Produce Recommendations
	print("\nRECOMMENDATIONS:")

	if sizes['file'][notinarc]+sizes['arc'][notinarc] > 5000000000:
		print("- CRITICAL: Overall scan size ({:>,d} MB) is too large\n	Impact: Scan will fail\n	Action: Ignore folders or remove large files".format(trunc((sizes['file'][notinarc]+sizes['arc'][notinarc])/1000000)))
	elif sizes['file'][notinarc]+sizes['arc'][notinarc] > 2000000000:
		print("- IMPORTANT: Overall scan size ({:>,d} MB) is large\n	Impact: Will impact Capacity license usage\n	Action: Ignore folders or remove large files".format(trunc((sizes['file'][notinarc]+sizes['arc'][notinarc])/1000000)))

	if counts['file'][notinarc]+counts['file'][inarc] > 2000000:
		print("- IMPORTANT: Overall number of files ({:>,d}) is very large\n	Impact: Scan time could be VERY long\n	Action: Ignore folders or split project (scan sub-projects)".format(trunc((counts['file'][notinarc]+sizes['file'][inarc]))))
	elif counts['file'][notinarc]+counts['file'][inarc] > 500000:
		print("- INFORMATION: Overall number of files ({:>,d}) is large\n	Impact: Scan time could be long\n	Action: Ignore folders or split project (scan sub-projects)".format(trunc((counts['file'][notinarc]+sizes['file'][inarc]))))


	if sizes['bin'][notinarc]+sizes['bin'][inarc] > 20000000:
		print("- IMPORTANT: Large amount of data ({:>,d} MB) in {} binary files found\n	Impact: Binary files not analysed by standard scan, will impact Capacity license usage\n	Action: Remove files or ignore folders, also consider zipping binary files and using Binary scan".format(trunc((sizes['bin'][notinarc]+sizes['bin'][inarc])/1000000), len(bin_list)))

	if size_dirdups > 20000000:
		print("- IMPORTANT: Large amount of data ({:,d} MB) in {:,d} duplicate folders\n	Impact: Scan capacity potentially utilised without detecting additional components, will impact Capacity license usage\n	Action: Remove or ignore duplicate folders".format(trunc(size_dirdups/1000000), len(dup_dir_dict)))
		#print("    Example .bdignore file:")
		#for apath, bpath in dup_dir_dict.items():
		#	print("    {}".format(bpath))
		#print("")
	if size_dups > 20000000:
		print("- IMPORTANT: Large amount of data ({:,d} MB) in {:,d} duplicate files\n	Impact: Scan capacity potentially utilised without detecting additional components, will impact Capacity license usage\n	Action: Remove or ignore duplicate folders".format(trunc(size_dups/1000000), len(dup_large_dict)))
		#for apath, bpath in dup_large_dict.items():
		#	if dup_dir_dict.get(os.path.dirname(apath)) == None and dup_dir_dict.get(os.path.dirname(bpath)) == None:
		#		print("    {}".format(bpath))
		#print("")

	check_singlefiles(f)

	print("")

parser = argparse.ArgumentParser(description='Examine files/folders to determine scan recommendations', prog='detect_advisor')

parser.add_argument("scanfolder", help="Project folder to analyse")
parser.add_argument("-r", "--report", help="Output report file")

args = parser.parse_args()

main_process(os.path.abspath(args.scanfolder), args.report)
