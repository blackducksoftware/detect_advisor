import global_values
import zipfile
import os
import io
from math import trunc
import platform
import hashlib

import messages


def process_nested_zip(z, zippath, zipdepth, dirdepth):
    # global global_values.max_arc_depth
    # global global_values.global_values.messages

    zipdepth += 1
    if zipdepth > global_values.max_arc_depth:
        global_values.max_arc_depth = zipdepth

    # print("ZIP:{}:{}".format(zipdepth, zippath))
    z2_filedata = io.BytesIO(z.read())
    try:
        with zipfile.ZipFile(z2_filedata) as nz:
            for zinfo in nz.infolist():
                dirdepth = process_zip_entry(zinfo, zippath, dirdepth)
                if os.path.splitext(zinfo.filename)[1] in global_values.ext_list['zip']:
                    with nz.open(zinfo.filename) as z2:
                        process_nested_zip(z2, zippath + "##" + zinfo.filename, zipdepth, dirdepth)
    except:
        global_values.messages += "WARNING: Can't open nested zip {} (Skipped)\n".format(zippath)


def process_zip_entry(zinfo, zippath, dirdepth):
    # print("ENTRY:" + zippath + "##" + zinfo.filename)
    fullpath = zippath + "##" + zinfo.filename
    odir = zinfo.filename
    zdir = os.path.dirname(zinfo.filename)
    depthinzip = 0
    while zdir != odir:
        depthinzip += 1
        odir = zdir
        zdir = os.path.dirname(zdir)

    dirdepth = dirdepth + depthinzip
    tdir = zippath + "##" + os.path.dirname(zinfo.filename)
    hash = get_path_hash(tdir)

    if hash not in global_values.dir_dict.keys():
        global_values.counts['dir'][global_values.inarc] += 1
        global_values.dir_dict[hash] = {
            'path': tdir,
            'num_entries': 1,
            'size': zinfo.file_size,
            'depth': dirdepth,
            'filenamesstring': zinfo.filename + ";",
        }
    else:
        global_values.dir_dict[hash]['num_entries'] += 1
        global_values.dir_dict[hash]['size'] += zinfo.file_size
        global_values.dir_dict[hash]['depth'] = dirdepth
        global_values.dir_dict[hash]['filenamesstring'] += zinfo.filename + ";"

    global_values.arc_files_dict[fullpath] = zinfo.CRC
    checkfile(zinfo.filename, fullpath, zinfo.file_size, zinfo.compress_size, dirdepth, True)
    return dirdepth


def process_zip(zippath, zipdepth, dirdepth):
    # global max_arc_depth
    # global global_values.messages

    zipdepth += 1
    if zipdepth > global_values.max_arc_depth:
        global_values.max_arc_depth = zipdepth

    # print("ZIP:{}:{}".format(zipdepth, zippath))
    try:
        with zipfile.ZipFile(zippath) as z:
            for zinfo in z.infolist():
                if zinfo.is_dir():
                    continue
                fullpath = zippath + "##" + zinfo.filename
                process_zip_entry(zinfo, zippath, dirdepth)
                if os.path.splitext(zinfo.filename)[1] in global_values.ext_list['zip']:
                    with z.open(zinfo.filename) as z2:
                        process_nested_zip(z2, fullpath, zipdepth, dirdepth)
    except:
        global_values.messages += "WARNING: Can't open zip {} (Skipped)\n".format(zippath)


def checkfile(name, path, size, size_comp, dirdepth, in_archive):

    pm_allfiles, pm_allexts = process_pmdata()

    ext = os.path.splitext(name)[1]
    #	print(ext)
    if ext != ".zip":
        if not in_archive:
            global_values.counts['file'][global_values.notinarc] += 1
            global_values.sizes['file'][global_values.notinarc] += size
        else:
            global_values.counts['file'][global_values.inarc] += 1
            global_values.sizes['file'][global_values.inarcunc] += size
            global_values.sizes['file'][global_values.inarccomp] += size_comp
        if size > global_values.hugesize:
            global_values.file_list['huge'].append(path)
            global_values.large_dict[path] = size
            if not in_archive:
                global_values.counts['huge'][global_values.notinarc] += 1
                global_values.sizes['huge'][global_values.notinarc] += size
            else:
                global_values.counts['huge'][global_values.inarc] += 1
                global_values.sizes['huge'][global_values.inarcunc] += size
                global_values.sizes['huge'][global_values.inarccomp] += size_comp
        elif size > global_values.largesize:
            global_values.file_list['large'].append(path)
            global_values.large_dict[path] = size
            if not in_archive:
                global_values.counts['large'][global_values.notinarc] += 1
                global_values.sizes['large'][global_values.notinarc] += size
            else:
                global_values.counts['large'][global_values.inarc] += 1
                global_values.sizes['large'][global_values.inarcunc] += size
                global_values.sizes['large'][global_values.inarccomp] += size_comp

    ftype = ''
    hash = get_path_hash(path)

    if name in pm_allfiles.keys() and path.find("node_modules") < 0:
        if not in_archive:
            global_values.det_dict[hash] = {
                'path': path,
                'depth': dirdepth,
            }
        ftype = 'det'
    elif os.path.basename(name) in global_values.ext_list['lic']:
        global_values.file_list['other'].append(path)
        ftype = 'other'
        global_values.counts['lic'][global_values.notinarc] += 1
    elif ext != "":
        if ext in pm_allexts.keys():
            if not in_archive:
                global_values.det_dict[hash] = {
                    'path': path,
                    'depth': dirdepth,
                }
            ftype = 'det'
        else:
            ftype = ''
            for ltype in ['src', 'jar', 'bin', 'arc', 'pkg']:
                if ext in global_values.ext_list[ltype]:
                    global_values.file_list[ltype].append(path)
                    ftype = ltype
                    break
    if ftype == '':
        global_values.file_list['other'].append(path)
        ftype = 'other'
        # print("path:{} type:{}, size_comp:{}, size:{}".format(path, ftype, size_comp, size))

    if not in_archive:
        global_values.counts[ftype][global_values.notinarc] += 1
        global_values.sizes[ftype][global_values.notinarc] += size
    else:
        global_values.counts[ftype][global_values.inarc] += 1
        global_values.sizes[ftype][global_values.inarcunc] += size
        if size_comp == 0:
            global_values.sizes[ftype][global_values.inarccomp] += size
        else:
            global_values.sizes[ftype][global_values.inarccomp] += size_comp
    return ftype


def get_path_hash(path):
    m = hashlib.sha256()
    m.update(path.encode())
    return m.hexdigest()


def process_dir(path, dirdepth, ignore):
    dir_size = 0
    dir_entries = 0
    filenames_string = ""
    # global global_values.messages

    dirdepth += 1

    # all_bin = False
    try:
        for entry in os.scandir(path):
            ignorethis = False
            dir_entries += 1
            filenames_string += entry.name + ";"
            if entry.is_dir(follow_symlinks=False):
                global_values.counts['dir'][global_values.notinarc] += 1
                this_size = process_dir(entry.path, dirdepth, ignorethis)
                dir_size += this_size
            else:
                ftype = checkfile(entry.name, entry.path, entry.stat(follow_symlinks=False).st_size, 0,
                                  dirdepth, False)
                if ftype == 'bin':
                    if dir_entries == 1:
                        all_bin = True
                else:
                    all_bin = False
                ext = os.path.splitext(entry.name)[1]
                if ext in global_values.ext_list['zip']:
                    process_zip(entry.path, 0, dirdepth)

                dir_size += entry.stat(follow_symlinks=False).st_size
    except OSError:
        global_values.messages += "ERROR: Unable to open folder {}\n".format(path)
        return 0

    hash = get_path_hash(path)
    global_values.dir_dict[hash] = {
        'path': path,
        'num_entries': dir_entries,
        'size': dir_size,
        'depth': dirdepth,
        'filenamesstring': filenames_string,
    }
    return dir_size


def check_singlefiles(f):
    # Check for singleton js & other single files
    sfmatch = False
    sf_list = []
    for thisfile in global_values.file_list['src']:
        ext = os.path.splitext(thisfile)[1]
        if ext == '.js':
            # get dir
            # check for .js in filenamesstring
            hash = get_path_hash(os.path.dirname(thisfile))

            thisdir = global_values.dir_dict[hash]
            if thisfile.find("node_modules") > 0:
                continue
            if thisdir is not None:
                all_js = True
                for filename in thisdir['filenamesstring'].split(';'):
                    srcext = os.path.splitext(filename)[1]
                    if srcext != '.js':
                        all_js = False
                if not all_js:
                    sfmatch = True
                    sf_list.append(thisfile)
    if sfmatch:
        messages.message('FILES1', len(sf_list))

    # if f:
    #	f.write("\nSINGLE JS FILES:\n")
    #	for thisfile in sf_list:
    #		f.write("- {}\n".format(thisfile))


def get_crc(myfile):
    import zlib
    # global global_values.messages

    buffersize = 65536

    crcvalue = 0
    try:
        with open(myfile, 'rb') as afile:
            buffr = afile.read(buffersize)
            while len(buffr) > 0:
                crcvalue = zlib.crc32(buffr, crcvalue)
                buffr = afile.read(buffersize)
    except:
        global_values.messages += "WARNING: Unable to open file {} to calculate CRC\n".format(myfile)
        return 0
    return crcvalue


def signature_process(f):
    # print("SIGNATURE SCAN ANALYSIS:")

    # Find duplicates without expanding archives - to avoid processing dups
    # print("- Processing folders         ", end="", flush=True)
    # num_dirdups, size_dirdups = process_dirdups(f)
    # print(" Done")

    # print("- Processing large files     ", end="", flush=True)
    # num_dups, size_dups = process_largefiledups(f)
    # print(" Done")
    #
    print("- Processing Signature Scan    .....", end="", flush=True)

    # Produce Recommendations
    if global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][global_values.notinarc] > 5000000000:
        messages.message('SCAN1',
            trunc((global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][global_values.notinarc]) / 1000000))
    elif global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][global_values.notinarc] > 2000000000:
        messages.message('SCAN2',
            trunc((global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][global_values.notinarc]) / 1000000))

    if global_values.counts['file'][global_values.notinarc] + global_values.counts['file'][global_values.inarc] > 1000000:
        messages.message('SCAN3',
            trunc((global_values.counts['file'][global_values.notinarc] + global_values.counts['file'][global_values.inarc])))
    elif global_values.counts['file'][global_values.notinarc] + global_values.counts['file'][global_values.inarc] > 200000:
        messages.message('SCAN4',
            trunc((global_values.counts['file'][global_values.notinarc] + global_values.counts['file'][global_values.inarc])))

    #
    # Need to add check for nothing to scan (no supported scan files)
    if global_values.counts['src'][global_values.notinarc] + global_values.counts['src'][global_values.inarc] + global_values.counts['jar'][global_values.notinarc] + global_values.counts['jar'][global_values.inarc] + \
            global_values.counts['other'][global_values.notinarc] + global_values.counts['other'][global_values.inarc] == 0:
        messages.message('SCAN5')

    if global_values.sizes['bin'][global_values.notinarc] + global_values.sizes['bin'][global_values.inarc] > 20000000:
        messages.message('SCAN6',
            trunc((global_values.sizes['bin'][global_values.notinarc] + global_values.sizes['bin'][global_values.inarc]) / 1000000), len(global_values.file_list['bin']))
        if f and len(global_values.bin_large_dict) > 0:
            f.write("\nLARGE BINARY FILES:\n")
            for fbin in global_values.bin_large_dict.keys():
                f.write("    {} (Size {:d}MB)\n".format(fbin, int(global_values.bin_large_dict[fbin] / 1000000)))
            f.write(
                "\nConsider using the following command to zip binary files and send to binary scan (subject to license):\n    zip binary_files.zip \n")
            binzip_list = []
            for fbin in global_values.bin_large_dict.keys():
                if fbin.find("##") < 0:
                    binzip_list.append(fbin)
                elif fbin.split("##")[0] not in binzip_list:
                    binzip_list.append(fbin.split("##")[0])
            num = 0
            for fbin in binzip_list:
                if num > 0:
                    f.write(" \\\n")
                f.write("    {}".format(fbin))
                num += 1
            f.write(
                "\n\nThen run Detect with the following options to send the archive for binary scan:\n    --detect.tools=BINARY_SCAN --detect.binary.scan.file.path=binary_files.zip\n\n")

    if global_values.counts['lic'][global_values.notinarc] > 10:
        messages.message('FILES2')

    if global_values.counts['src'][global_values.notinarc] + global_values.counts['src'][global_values.inarc] > 10:
        messages.message('FILES3')

    check_singlefiles(f)
    print(" Done")
    print("")


def detector_process(f):
    import shutil

    print("- Processing PM Configurations .....", end="", flush=True)

    pm_allfiles, pm_allexts = process_pmdata()

    if f:
        f.write("PACKAGE MANAGER CONFIG FILES FOUND:\n")

    count = 0
    det_depth1 = 0
    det_other = 0
    cmds_missing1 = ""
    cmds_missingother = ""
    cmds_missing_list = []
    det_max_depth = 0
    det_min_depth = 100
    det_in_arc = 0

    pm_dict = {}
    if len(global_values.det_dict) > 0:
        for dethash in global_values.det_dict.keys():
            command_exists = False
            detpath = global_values.det_dict[dethash]['path']
            depth = global_values.det_dict[dethash]['depth']
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
                exes = ''
                pm = ''
                if fname in pm_allfiles.keys():
                    pm = pm_allfiles[fname]
                elif os.path.splitext(fname)[1] in pm_allexts.keys():
                    pm = pm_allexts[os.path.splitext(fname)[1]]
                if pm != '':
                    if pm in pm_dict.keys():
                        pm_dict[pm]['count'] += 1
                        if depth < pm_dict[pm]['mindepth']:
                            pm_dict[pm]['mindepth'] = depth
                        if depth > pm_dict[pm]['maxdepth']:
                            pm_dict[pm]['maxdepth'] = depth
                    else:
                        pm_dict[pm] = {
                            'count': 1,
                            'mindepth': depth,
                            'maxdepth': depth,
                        }
                    exes = global_values.pm_dict[pm]['execs']

                missing_cmds = ""
                for exe in exes:
                    if exe not in global_values.detectors_list:
                        global_values.detectors_list.append(exe)
                        if shutil.which(exe) is not None:
                            command_exists = True
                            if platform.system() != "Linux" and exe in global_values.linux_only_detectors:
                                if depth == 1:
                                    messages.message('PLATFORM3', pm)
                                else:
                                    messages.message('PLATFORM4', pm)
                        else:
                            if exe not in cmds_missing_list:
                                cmds_missing_list.append(exe)
                                if missing_cmds:
                                    missing_cmds += " OR " + exe
                                else:
                                    missing_cmds = exe
                if f:
                    f.write("{}\n".format(detpath))
                    count += 1

                if not command_exists and missing_cmds:
                    if missing_cmds.find(" OR ") > 0:
                        missing_cmds = "(" + missing_cmds + ")"
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

        global_values.rep += ("\nPACKAGE MANAGER CONFIG FILES:\n" +
              f"- In invocation folder:   {det_depth1}\n" +
              f"- In sub-folders:         {det_other}\n" +
              f"- In archives:            {det_in_arc}\n" +
              f"- Minimum folder depth:   {det_min_depth}\n" +
              f"- Maximum folder depth:   {det_max_depth}\n" +
              "---------------------------------\n" +
              f"- Total discovered:       {len(global_values.det_dict)}\n\n")

        def value_getter(item):
            return item[1]['mindepth']

        global_values.rep += "  Config files for the following Package Managers found:\n                Count  MinDepth  MaxDepth\n"
        for item in sorted(pm_dict.items(), key=value_getter):
            global_values.rep += \
                "  - {:11} {:>5,d}  {:>8d}  {:>8d}\n".format(
                    item[0], item[1]['count'], item[1]['mindepth'], item[1]['maxdepth'])

    if f and count == 0:
        f.write("    None\n")

    if det_depth1 == 0 and det_other > 0:
        messages.message('PACKAGES1', det_min_depth, det_max_depth)

    if det_depth1 == 0 and det_other == 0:
        messages.message('PACKAGES2')

    if cmds_missing1:
        messages.message('PACKAGES3', cmds_missing1)

    if cmds_missingother:
        messages.message('PACKAGES4', cmds_missingother)

    if global_values.counts['det'][global_values.inarc] > 0:
        messages.message('PACKAGES5')

    for pm in global_values.detectors_list:
        if cmd in global_values.detector_cli_options_dict.keys() and 'dep' in global_values.cli_msgs_dict:
            global_values.cli_msgs_dict['dep'] += "For {}:\n".format(cmd) + global_values.detector_cli_options_dict[cmd] + '\n'
        if cmd in global_values.detector_cli_required_dict.keys() and 'crit' in global_values.cli_msgs_dict:
            global_values.cli_msgs_dict['crit'] += "For {}:\n".format(cmd) + global_values.detector_cli_required_dict[cmd] + '\n'

    print(" Done")

    return


def process_pmdata():
    pm_allfiles = {}
    pm_allexts = {}

    for pm in global_values.pm_dict.keys():
        if len(global_values.pm_dict[pm]['files']) > 0:
            for ffile in global_values.pm_dict[pm]['files']:
                pm_allfiles[ffile] = pm

        if len(global_values.pm_dict[pm]['exts']) > 0:
            for fext in global_values.pm_dict[pm]['exts']:
                pm_allexts[fext] = pm

    return pm_allfiles, pm_allexts