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

# detectors_dict = {
# 'Bitbake': {'exe': ['bitbake'], 'files':['build.env']},
# 'Clang': {'exe': ['clang'], 'files':['compile_commands.json']},
# 'Cocoapods': {'exe': [''], 'files':['Podfile.lock']},
# 'Conda': {'exe': ['conda'], 'files':['environment.yml']},
# 'Cpan': {'exe': ['cpan'], 'files':['Makefile.PL']},
# 'Cran': {'exe': ['rtools'], 'files':['packrat.lock']},
# 'Go Dep': {'exe': ['go'], 'files':['Gopkg.lock']},
# 'Go Gradle': {'exe': ['go'], 'files':['gogradle.lock']},
# 'Go Mod': {'exe': ['go'], 'files':['go.mod']},
# 'Go Vendor': {'exe': ['go'], 'files':['vendor.json']},
# 'Go Vndr': {'exe': ['go'], 'files':['vendor.conf']},
# 'Gradle': {'exe': ['gradlew','gradle'], 'files':['build.gradle','build.gradle.kts']},
# 'Hex': {'exe': ['rebar3'], 'files':['rebar.config']},
# 'Maven': {'exe': ['mvnw','mvn'], 'files':['pom.xml','pom.groovy']},
# 'Npm': {'exe': ['npm'], 'files':['node_modules','package.json','package-lock.json','npm-shrinkwrap.json']},
# 'NuGet': {'exe': ['dotnet'], 'files':['*.csproj','*.fsproj','*.vbproj','*.asaproj','*.dcproj','*.shproj','*.ccproj','*.sfproj','*.njsproj','*.vcxproj','*.vcproj','*.xproj','*.pyproj','*.hiveproj','*.pigproj','*.jsproj','*.usqlproj','*.deployproj','*.msbuildproj','*.sqlproj','*.dbproj','*.rproj','*.sln']},
# 'Packagist': {'exe': [''], 'files':['composer.lock','composer.json']},
# 'Pear': {'exe': ['pear'], 'files':['package.xml']},
# 'Pip Env': {'exe': ['python','python3','pipenv'], 'files':['Pipfile','Pipfile.lock']},
# 'Pip': {'exe': ['python','python3','pip'], 'files':['setup.py','requirements.txt']},
# 'RubyGems': {'exe': [''], 'files':['Gemfile.lock']},
# 'SBT': {'exe': ['sbt'], 'files':['build.sbt']},
# 'Swift': {'exe': ['swift'], 'files':['Package.swift']},
# 'Yarn': {'exe': [''], 'files':['yarn.lock','package.json']}
# }

detectors_file_dict = {
'build.env': ['bitbake'],
'compile_commands.json': ['clang'],
'Podfile.lock': ['pod'],
'environment.yml': ['conda'],
'Makefile.PL': ['cpan'],
'packrat.lock': ['rtools'],
'Gopkg.lock': ['go'],
'gogradle.lock': ['go'],
'go.mod': ['go'],
'vendor.json': ['go'],
'vendor.conf': ['go'],
'build.gradle': ['gradlew','gradle'],
'build.gradle.kts': ['gradlew','gradle'],
'rebar.config': ['rebar3'],
'pom.xml': ['mvnw','mvn'],
'pom.groovy': ['mvnw','mvn'],
'node_modules': ['npm'],
'package.json': ['npm'],
'package-lock.json': ['npm'],
'npm-shrinkwrap.json': ['npm'],
'composer.lock': ['composer'],
'composer.json': ['composer'],
'package.xml': ['pear'],
'pipfile': ['python','python3','pipenv'],
'pipfile.lock': ['python','python3','pipenv'],
'setup.py': ['python','python3','pip'],
'requirements.txt': ['python','python3','pip'],
'Gemfile.lock': ['gem'],
'build.sbt': ['sbt'],
'Package.swift': ['swift'],
'yarn.lock': ['yarn']
}

detectors_ext_dict = {
'.csproj': ['dotnet'],
'.fsproj': ['dotnet'],
'.vbproj': ['dotnet'],
'.asaproj': ['dotnet'],
'.dcproj': ['dotnet'],
'.shproj': ['dotnet'],
'.ccproj': ['dotnet'],
'.sfproj': ['dotnet'],
'.njsproj': ['dotnet'],
'.vcxproj': ['dotnet'],
'.vcproj': ['dotnet'],
'.xproj': ['dotnet'],
'.pyproj': ['dotnet'],
'.hiveproj': ['dotnet'],
'.pigproj': ['dotnet'],
'.jsproj': ['dotnet'],
'.usqlproj': ['dotnet'],
'.deployproj': ['dotnet'],
'.msbuildproj': ['dotnet'],
'.sqlproj': ['dotnet'],
'.dbproj': ['dotnet'],
'.rproj': ['dotnet'],
'.sln': ['dotnet']
}

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
'det' : [0,0],
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
'det' : [0,0,0],
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

det_dict = {}

crc_dict = {}

dup_dir_dict = {}
dup_large_dict = {}

dir_dict = {}
large_dict = {}
arc_files_dict = {}

messages = ""

def process_nested_zip(z, zippath, zipdepth, dirdepth):
	global max_arc_depth
	global messages

	zipdepth += 1
	if zipdepth > max_arc_depth:
		max_arc_depth = zipdepth

	#print("ZIP:{}:{}".format(zipdepth, zippath))
	z2_filedata =  io.BytesIO(z.read())
	try:
		with zipfile.ZipFile(z2_filedata) as nz:
			for zinfo in nz.infolist():
				dirdepth = process_zip_entry(zinfo, zippath, dirdepth)
				if os.path.splitext(zinfo.filename)[1] == ".zip":
					with nz.open(zinfo.filename) as z2:
						process_nested_zip(z2, zippath + "##" + zinfo.filename, zipdepth, dirdepth)
	except:
		messages += "WARNING: Can't open nested zip {} (Skipped)".format(zippath)


def process_zip_entry(zinfo, zippath, dirdepth):
	#print("ENTRY:" + zippath + "##" + zinfo.filename)
	fullpath = zippath + "##" + zinfo.filename
	odir = zinfo.filename
	dir = os.path.dirname(zinfo.filename)
	depthinzip = 0
	while dir != odir:
		depthinzip += 1
		odir = dir
		dir = os.path.dirname(dir)

	dirdepth = dirdepth + depthinzip
	tdir = zippath + "##" + os.path.dirname(zinfo.filename)
	if tdir not in dir_dict.keys():
		counts['dir'][inarc] += 1
		dir_dict[tdir] = {}
		dir_dict[tdir]['num_entries'] = 1
		dir_dict[tdir]['size'] = zinfo.file_size
		dir_dict[tdir]['depth'] = dirdepth
		dir_dict[tdir]['filenamesstring'] = zinfo.filename + ";"
	else:
		dir_dict[tdir]['num_entries'] += 1
		dir_dict[tdir]['size'] += zinfo.file_size
		dir_dict[tdir]['depth'] = dirdepth
		dir_dict[tdir]['filenamesstring'] += zinfo.filename + ";"

	arc_files_dict[fullpath] = zinfo.CRC
	checkfile(zinfo.filename, fullpath, zinfo.file_size, zinfo.compress_size, dirdepth, True)
	return dirdepth

def process_zip(zippath, zipdepth, dirdepth):
	global max_arc_depth
	global messages

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
				process_zip_entry(zinfo, zippath, dirdepth)
				if os.path.splitext(zinfo.filename)[1] == ".zip":
					with z.open(zinfo.filename) as z2:
						process_nested_zip(z2, fullpath, zipdepth, dirdepth)
	except:
		messages += "WARNING: Can't open zip {} (Skipped)".format(zippath)

def checkfile(name, path, size, size_comp, dirdepth, inarc):
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

	if os.path.basename(name) in detectors_file_dict.keys():
		if not inarc:
			det_dict[path] = dirdepth
		ftype = 'det'
	elif (ext != ""):
		if ext in detectors_ext_dict.keys():
			if not inarc:
				det_dict[path] = dirdepth
			ftype = 'det'
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


def process_dir(path, dirdepth):
	dir_size = 0
	dir_entries = 0
	filenames_string = ""
	global messages

	dir_dict[path] = {}
	dirdepth += 1
	try:
		for entry in os.scandir(path):
			dir_entries += 1
			filenames_string += entry.name + ";"
			if entry.is_dir(follow_symlinks=False):
				counts['dir'][notinarc] += 1
				dir_size += process_dir(entry.path, dirdepth)
			else:
				checkfile(entry.name, entry.path, entry.stat(follow_symlinks=False).st_size, 0, dirdepth, False)
				ext = os.path.splitext(entry.name)[1]
				if ext == '.zip':
					process_zip(entry.path, 0, dirdepth)

				dir_size += entry.stat(follow_symlinks=False).st_size
	except OSError:
		messages += "ERROR: Unable to open folder {}\n".format(path)
		return 0

	dir_dict[path]['num_entries'] = dir_entries
	dir_dict[path]['size'] = dir_size
	dir_dict[path]['depth'] = dirdepth
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
		#print("Processing folder:" + xpath + " dup " + ypath)
		xdir = os.path.dirname(xpath)
		ydir = os.path.dirname(ypath)
		if xdir in tmp_dup_dir_dict.keys() and tmp_dup_dir_dict[xdir] == ydir:
			# parents match - ignore
			#print("Ignorning dup dir: " + xpath + " " + ypath)
			pass
		else:
			# Create dupdir entry
			#print("Adding dup dir: " + xpath + " " + ypath)
			dup_dir_dict[xpath] = ypath
			count_dupdirs += 1
			size_dupdirs += dir_dict[xpath]['size']
			if f:
				f.write("- Duplicate folder - {}, {} (size {}MB)\n".format(xpath,ypath, \
				trunc(dir_dict[xpath]['size']/1000000)))

	return(count_dupdirs, size_dupdirs)

def check_singlefiles(f):
	global recs_other

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
		recs_other += "- INFORMATION: {} singleton .js files found\n".format(len(sf_list)) + \
		"	Impact:	OSS components within JS files may not be detected\n" + \
		"	Action:	Consider specifying Single file matching\n" + \
		"		(--detect.blackduck.signature.scanner.individual.file.matching=SOURCE)"
		if f:
			f.write("\nSINGLE JS FILES:\n")
			for thisfile in sf_list:
				f.write("- {}\n".format(thisfile))

def get_crc(myfile):
	import zlib
	buffersize = 65536

	crcvalue = 0
	try:
		with open(myfile, 'rb') as afile:
			buffr = afile.read(buffersize)
			while len(buffr) > 0:
				crcvalue = zlib.crc32(buffr, crcvalue)
				buffr = afile.read(buffersize)
	except:
		messages += "ERROR: Unable to open file {} to calculate CRC\n".format(myfile)
		return(0)
	return(crcvalue)

def print_summary(f):
	global rep

	summary = "\nSUMMARY INFO:            Num Outside     Size Outside      Num Inside     Size Inside     Size Inside\n" + \
	"                            Archives         Archives        Archives        Archives        Archives\n" + \
	"                                                                        (UNcompressed)    (compressed)\n" + \
	"--------------------  --------------   --------------   -------------   -------------   -------------\n"

	row = "{:25} {:>10,d}    {:>10,d} MB      {:>10,d}   {:>10,d} MB   {:>10,d} MB\n"

	summary += row.format("Files (exc. Archives)", \
	counts['file'][notinarc], \
	trunc(sizes['file'][notinarc]/1000000), \
	counts['file'][inarc], \
	trunc(sizes['file'][inarcunc]/1000000), \
	trunc(sizes['file'][inarccomp]/1000000))

	summary += row.format("Archives", \
	counts['arc'][notinarc], \
	trunc(sizes['arc'][notinarc]/1000000), \
	counts['arc'][inarc], \
	trunc(sizes['arc'][inarcunc]/1000000), \
	trunc(sizes['arc'][inarccomp]/1000000))

	summary += "--------------------  --------------   --------------   -------------   -------------   -------------\n"

	summary += "{:25} {:>10,d}              N/A      {:>10,d}             N/A             N/A   \n".format("Folders", \
	counts['dir'][notinarc], \
	counts['dir'][inarc])

	summary += row.format("Source Files", \
	counts['src'][notinarc], \
	trunc(sizes['src'][notinarc]/1000000), \
	counts['src'][inarc], \
	trunc(sizes['src'][inarcunc]/1000000), \
	trunc(sizes['src'][inarccomp]/1000000))

	summary += row.format("JAR Archives", \
	counts['jar'][notinarc], \
	trunc(sizes['jar'][notinarc]/1000000), \
	counts['jar'][inarc], \
	trunc(sizes['jar'][inarcunc]/1000000), \
	trunc(sizes['jar'][inarccomp]/1000000))

	summary += row.format("Binary Files", \
	counts['bin'][notinarc], \
	trunc(sizes['bin'][notinarc]/1000000), \
	counts['bin'][inarc], \
	trunc(sizes['bin'][inarcunc]/1000000), \
	trunc(sizes['bin'][inarccomp]/1000000))

	summary += row.format("Other Files", \
	counts['other'][notinarc], \
	trunc(sizes['other'][notinarc]/1000000), \
	counts['other'][inarc], \
	trunc(sizes['other'][inarcunc]/1000000), \
	trunc(sizes['other'][inarccomp]/1000000))

	summary += row.format("Package Mgr Files", \
	counts['det'][notinarc], \
	trunc(sizes['det'][notinarc]/1000000), \
	counts['det'][inarc], \
	trunc(sizes['det'][inarcunc]/1000000), \
	trunc(sizes['det'][inarccomp]/1000000))

	summary += row.format("Large Files (>{:1d}MB)".format(trunc(largesize/1000000)), \
	counts['large'][notinarc], \
	trunc(sizes['large'][notinarc]/1000000), \
	counts['large'][inarc], \
	trunc(sizes['large'][inarcunc]/1000000), \
	trunc(sizes['large'][inarccomp]/1000000))

	summary += row.format("Huge Files (>{:2d}MB)".format(trunc(hugesize/1000000)), \
	counts['huge'][notinarc], \
	trunc(sizes['huge'][notinarc]/1000000), \
	counts['huge'][inarc], \
	trunc(sizes['huge'][inarcunc]/1000000), \
	trunc(sizes['huge'][inarccomp]/1000000))

	summary += "--------------------  --------------   --------------   -------------   -------------   -------------\n"

	summary += row.format("All Files (Scan size)", counts['file'][notinarc]+counts['arc'][notinarc], \
	trunc((sizes['file'][notinarc]+sizes['arc'][notinarc])/1000000), \
	counts['file'][inarc]+counts['arc'][inarc], \
	trunc((sizes['file'][inarcunc]+sizes['arc'][inarcunc])/1000000), \
	trunc((sizes['file'][inarccomp]+sizes['arc'][inarccomp])/1000000))

	summary += rep + "\n\n"

	print(summary)
	if f:
		f.write(summary)

def signature_process(folder, f):
	global recs_critical
	global recs_important
	global recs_other

	#print("SIGNATURE SCAN ANALYSIS:")

	# Find duplicates without expanding archives - to avoid processing dups
	print("- Processing folders     ", end="", flush=True)
	num_dirdups, size_dirdups = process_dirdups(f)
	print(" Done")

	print("- Processing large files ", end="", flush=True)
	num_dups, size_dups = process_largefiledups(f)
	print(" Done")

	# Produce Recommendations
	if sizes['file'][notinarc]+sizes['arc'][notinarc] > 5000000000:
		recs_critical += "- CRITICAL: Overall scan size ({:>,d} MB) is too large\n".format(trunc((sizes['file'][notinarc]+sizes['arc'][notinarc])/1000000)) + \
		"	Impact:	Scan will fail\n" + \
		"	Action:	Ignore folders or remove large files\n"
	elif sizes['file'][notinarc]+sizes['arc'][notinarc] > 2000000000:
		recs_important += "- IMPORTANT: Overall scan size ({:>,d} MB) is large\n".format(trunc((sizes['file'][notinarc]+sizes['arc'][notinarc])/1000000)) + \
		"	Impact:	Will impact Capacity license usage\n" + \
		"	Action:	Ignore folders or remove large files\n"

	if counts['file'][notinarc]+counts['file'][inarc] > 2000000:
		recs_important += "- IMPORTANT: Overall number of files ({:>,d}) is very large\n".format(trunc((counts['file'][notinarc]+sizes['file'][inarc]))) + \
		"	Impact:	Scan time could be VERY long\n" + \
		"	Action:	Ignore folders or split project (scan sub-projects)\n"
	elif counts['file'][notinarc]+counts['file'][inarc] > 500000:
		recs_other += "- INFORMATION: Overall number of files ({:>,d}) is large\n".format(trunc((counts['file'][notinarc]+sizes['file'][inarc])) + \
		"	Impact:	Scan time could be long\n" + \
		"	Action:	Ignore folders or split project (scan sub-projects)\n")

	#
	# Need to add check for nothing to scan (no supported scan files)
	if counts['src'][notinarc]+counts['src'][inarc]+counts['jar'][notinarc]+counts['jar'][inarc]+counts['other'][notinarc]+counts['other'][inarc] == 0:
		recs_other += "- INFORMATION: No source, jar or other files found\n".format(trunc((counts['file'][notinarc]+sizes['file'][inarc]))) + \
		"	Impact:	Scan may not detect any OSS from files (dependencies only)\n" + \
		"	Action:	Check scan location is correct\n"

	if sizes['bin'][notinarc]+sizes['bin'][inarc] > 20000000:
		recs_important += "- IMPORTANT: Large amount of data ({:>,d} MB) in {} binary files found\n".format(trunc((sizes['bin'][notinarc]+sizes['bin'][inarc])/1000000), len(bin_list)) + \
		"	Impact:	Binary files not analysed by standard scan,\n" + \
		"		will impact Capacity license usage\n" + \
		"	Action:	Remove files or ignore folders, also consider zipping\n" + \
		"		binary files and using Binary scan\n"

	if size_dirdups > 20000000:
		recs_important += "- IMPORTANT: Large amount of data ({:,d} MB) in {:,d} duplicate folders\n".format(trunc(size_dirdups/1000000), len(dup_dir_dict)) + \
		"	Impact:	Scan capacity potentially utilised without detecting additional\n" + \
		"		components, will impact Capacity license usage\n" + \
		"	Action:	Remove or ignore duplicate folders\n"
		#print("    Example .bdignore file:")
		#for apath, bpath in dup_dir_dict.items():
		#	print("    {}".format(bpath))
		#print("")
	if size_dups > 20000000:
		recs_important += "- IMPORTANT: Large amount of data ({:,d} MB) in {:,d} duplicate files\n".format(trunc(size_dups/1000000), len(dup_large_dict)) + \
		"	Impact:	Scan capacity potentially utilised without detecting additional\n" + \
		"		components, will impact Capacity license usage\n" + \
		"	Action:	Remove or ignore duplicate folders\n"
		#for apath, bpath in dup_large_dict.items():
		#	if dup_dir_dict.get(os.path.dirname(apath)) == None and dup_dir_dict.get(os.path.dirname(bpath)) == None:
		#		print("    {}".format(bpath))
		#print("")

	check_singlefiles(f)

	print("")

def detector_process(folder, f):
	import shutil

	global recs_critical
	global recs_important
	global recs_other
	global rep

	rep = "\nPACKAGE MANAGER FILES:\n" + \
	"- Total discovered:	{}\n".format(len(det_dict))

	if f:
		f.write("PROJECT FILES FOUND:\n")

	det_depth1 = 0
	det_other = 0
	cmds_missing1 = ""
	cmds_missingother = ""
	cmds_missing_list = []
	det_max_depth = 0
	det_min_depth = 100
	det_in_arc = 0
	if len(det_dict) > 0:
		for detpath, depth in det_dict.items():
			command_exists = False
			if detpath.find("##") > 0:
				# in archive
				det_in_arc += 1
			else:
				if depth == 1:
					det_depth1 += 1
				elif depth > 1:
					det_other += 1
				if depth > det_max_depth:
					det_max_depth = depth
				if depth < det_min_depth:
					det_min_depth = depth
				fname = os.path.basename(detpath)
				exes = ""
				if fname in detectors_file_dict.keys():
					exes = detectors_file_dict[fname]
				elif os.path.splitext(fname)[1] in detectors_ext_dict.keys():
					exes = detectors_ext_dict[os.path.splitext(fname)[1]]
				missing_cmds = ""
				for exe in exes:
					if shutil.which(exe) is not None:
						command_exists = True
					else:
						if exe not in cmds_missing_list:
							cmds_missing_list.append(exe)
							if missing_cmds:
								missing_cmds += " OR " + exe
							else:
								missing_cmds = exe
				if f:
					f.write("{}\n".format(detpath))

				if not command_exists and missing_cmds:
					if depth == 1:
						if cmds_missing1:
							cmds_missing1 += " AND " + missing_cmds
						else:
							cmds_missing1 = missing_cmds
					else:
						if cmds_missingother:
							cmds_missingother += " AND " + missing_cmds
						else:
							cmds_missingother = missing_cmds

		rep += "- In invocation folder:	{}\n".format(det_depth1)
		rep += "- In sub-folders:	{}\n".format(det_other)
		rep += "- Maximum folder depth:	{}\n".format(det_max_depth)
		rep += "- In archives:	{}\n".format(det_in_arc)

	if det_depth1 == 0 and det_other > 0:
		recs_important += "- IMPORTANT: No package manager files found in invocation folder but do exist in sub-folders\n" + \
		"	Impact:	Dependency scan will not be run\n" + \
		"	Action:	Specify --detect.detector.depth={}\n".format(det_min_depth)

	if det_depth1 == 0 and det_other == 0:
		recs_other += "- INFORMATION: No package manager files found in project at all\n" + \
		"	Impact:	No dependency scan will be performed\n" + \
		"	Action:	This may be expected, but ensure you are scanning the correct location\n"

	if cmds_missing1:
		recs_critical += "- CRITICAL: Package manager programs ({}) missing for package files in invocation folder\n".format(cmds_missing1) + \
		"	Impact:	Scan will fail\n" + \
		"	Action:	Either install package manager programs or\n" + \
		"		consider specifying --detect.detector.buildless=true\n"

	if cmds_missingother:
		recs_important += "- IMPORTANT: Package manager programs ({}) missing for package files in sub-folders\n".format(cmds_missingother) + \
		"	Impact:	Dependency \n" + \
		"	Action:	Either install package manager programs or\n" + \
		"		consider specifying --detect.detector.buildless=true\n"

	if counts['det'][inarc] > 0:
		recs_important += "- IMPORTANT: Package manager files found in archives\n" + \
		"	Impact:	Dependency scan not performed for projects in archives\n" + \
		"	Action:	Extract zip archives and rescan\n"

	return

def print_recs(critical_only, f):
	global recs_critical
	global recs_important
	global recs_other
	global messages

	if f:
		f.write(messages + "\n")

	print("RECOMMENDATIONS:")
	if f:
		f.write("\nRECOMMENDATIONS:\n")

	if recs_critical:
		print(recs_critical)
		if f:
			f.write(recs_critical)

	if recs_important and not critical_only:
		print(recs_important)
		if f:
			f.write(recs_important)

	if recs_other and not critical_only:
		print(recs_other)
		if f:
			f.write(recs_other)

	if (not recs_critical and not recs_important and not recs_other) or (critical_only and not recs_critical):
		print("- None")
		if f:
			f.write("None\n")

	if f:
		print("Further information in output report file")
	else:
		print("Use '-r repfile' to produce report file with more information")



def check_prereqs():
	import subprocess
	import re
	import shutil

	global recs_critical
	global recs_important
	global recs_other
	global messages

	# Check java
	if shutil.which("java") is None:
		recs_critical += "- CRITICAL: Java is not installed or on the PATH\n" + \
		"	Impact:	Detect program will fail\n" + \
		"	Action:	Install Java 1.8 or 1.11\n"
	else:
		javaversion = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)
		if javaversion:
			version_number = javaversion.decode("utf-8").splitlines()[0].split()[-1].strip('"')
			major, minor, _ = version_number.split('.')
			if major != "1" or (major == "1" and (minor != "8" and minor != "11")):
				recs_critical += "- CRITICAL: Java version {} is not supported by Detect\n".format(version_number) + \
				"	Impact:	Scan will fail\n" + \
				"	Action:	Install Java or OpenJDK version 1.8 or 1.11\n"

parser = argparse.ArgumentParser(description='Examine files/folders to determine scan recommendations', prog='detect_advisor')

parser.add_argument("scanfolder", help="Project folder to analyse")
parser.add_argument("-r", "--report", help="Output report file")
parser.add_argument("-d", "--detectors_only", help="Check for detector files and prerequisites only",action='store_true')
parser.add_argument("-s", "--signature_only", help="Check for files and folders for signature scan only",action='store_true')
parser.add_argument("-c", "--critical_only", help="Only show critical issues which will causes detect to fail",action='store_true')

args = parser.parse_args()

if not os.path.isdir(args.scanfolder):
	print("Scan location {} does not exist\nExiting".format(args.scanfolder))
	exit(1)

if args.report and os.path.exists(args.report):
	print("Report file {} already exists\nExiting".format(args.report))
	exit(2)

recs_critical = ""
recs_important = ""
recs_other = ""
rep = ""

print("\nPROCESSING:")

print("Working on project folder {}".format(args.scanfolder))

print("- Reading hierarchy      .....", end="", flush=True)
process_dir(args.scanfolder, 0)
print(" Done")

if args.report:
	try:
		f = open(args.report, "a")
	except Exception as e:
		print('ERROR: Unable to open output report file \n' + str(e))
		exit(3)
else:
	f = None

if not args.signature_only:
	#detector_process(os.path.abspath(args.scanfolder), args.report)
	detector_process(args.scanfolder, f)

if not args.detectors_only:
	#signature_process(os.path.abspath(args.scanfolder), args.report)
	signature_process(args.scanfolder, f)

if not args.critical_only:
	print_summary(f)

check_prereqs()

print_recs(args.critical_only, f)

if f:
	f.write("\n")
	f.close()