import zipfile
import os
import sys
import io
from math import trunc
import platform
import hashlib

from . import global_values
from . import messages


def process_pmdata():
    pm_all_files = {}
    pm_all_exts = {}
    # pm_all_locks = {}

    for pm in global_values.pm_dict.keys():
        if len(global_values.pm_dict[pm]['files']) > 0:
            for ffile in global_values.pm_dict[pm]['files']:
                pm_all_files[ffile] = pm

        if len(global_values.pm_dict[pm]['exts']) > 0:
            for fext in global_values.pm_dict[pm]['exts']:
                pm_all_exts[fext] = pm

        # if len(global_values.pm_dict[pm]['lock_files']) > 0:
        #     for ffile in global_values.pm_dict[pm]['lock_files']:
        #         pm_all_locks[ffile] = pm

    return pm_all_files, pm_all_exts


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
    dhash = get_path_hash(tdir)

    if dhash not in global_values.dir_dict.keys():
        global_values.counts['dir'][global_values.inarc] += 1
        global_values.dir_dict[dhash] = {
            'path': tdir,
            'num_entries': 1,
            'size': zinfo.file_size,
            'depth': dirdepth,
            'filenamesstring': zinfo.filename + ";",
        }
    else:
        global_values.dir_dict[dhash]['num_entries'] += 1
        global_values.dir_dict[dhash]['size'] += zinfo.file_size
        global_values.dir_dict[dhash]['depth'] = dirdepth
        global_values.dir_dict[dhash]['filenamesstring'] += zinfo.filename + ";"

    # global_values.arc_files_dict[fullpath] = zinfo.CRC
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

    # Store file sizes
    if ext not in global_values.ext_list['arc']:
        if not in_archive:
            global_values.counts['file'][global_values.notinarc] += 1
            global_values.sizes['file'][global_values.notinarc] += size
        else:
            global_values.counts['file'][global_values.inarc] += 1
            global_values.sizes['file'][global_values.inarcunc] += size
            global_values.sizes['file'][global_values.inarccomp] += size_comp
        key = ''
        if size > global_values.hugesize:
            key = 'huge'
        elif size > global_values.largesize:
            key = 'large'

        if key != '':
            if not in_archive:
                global_values.counts[key][global_values.notinarc] += 1
                global_values.sizes[key][global_values.notinarc] += size
                global_values.file_list[key].append(path)
            else:
                global_values.counts[key][global_values.inarc] += 1
                global_values.sizes[key][global_values.inarcunc] += size
                global_values.sizes[key][global_values.inarccomp] += size_comp

    ftype = ''
    fhash = get_path_hash(path)

    if name in pm_allfiles.keys():
        if not in_archive:
            global_values.files_dict['det'][fhash] = {
                'path': path,
                'depth': dirdepth,
            }
        else:
            global_values.file_list['arcs_pm'].append(path)
        ftype = 'det'
    elif os.path.basename(name) in global_values.ext_list['lic']:
        # global_values.file_list['other'].append(path)
        ftype = 'other'
        global_values.counts['lic'][global_values.notinarc] += 1
    elif ext != "":
        if ext in pm_allexts.keys():
            if not in_archive:
                global_values.files_dict['det'][fhash] = {
                    'path': path,
                    'depth': dirdepth,
                }
            ftype = 'det'
        else:
            ftype = ''
            for ltype in ['src', 'jar', 'bin', 'arc', 'pkg']:
                if ext in global_values.ext_list[ltype]:
                    # global_values.file_list[ltype].append(path)
                    ftype = ltype
                    break

    if ftype == '':
        # global_values.file_list['other'].append(path)
        ftype = 'other'
        # print("path:{} type:{}, size_comp:{}, size:{}".format(path, ftype, size_comp, size))

    if not in_archive:
        global_values.file_list[ftype].append(path)
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


def sig_excluded(dir):
    excluded = False
    for exc in global_values.sig_excludes:
        # if dir.find(os.path.pathsep + exc + os.path.pathsep) > 0 or \
        #         dir.endswith(os.path.pathsep + exc):
        if dir.find('/' + exc + '/') > 0 or \
                dir.endswith('/' + exc):
            excluded = True
            break
    return excluded

def det_excluded(dir):
    excluded = False
    for exc in global_values.det_excludes:
        # if dir.find(os.path.pathsep + exc + os.path.pathsep) > 0 or \
        #         dir.endswith(os.path.pathsep + exc):
        if dir.find('/' + exc + '/') > 0 or \
                dir.endswith('/' + exc):
            excluded = True
            break
    return excluded


def process_dir(path, dirdepth):
    dir_size = 0
    dir_entries = 0
    filenames_string = ""
    # global global_values.messages

    if sig_excluded(path):
        return 0

    dirdepth += 1

    # all_bin = False
    try:
        for entry in os.scandir(path):
            # ignorethis = False
            dir_entries += 1
            filenames_string += entry.name + ";"
            if entry.is_dir(follow_symlinks=False):
                global_values.counts['dir'][global_values.notinarc] += 1
                this_size = process_dir(entry.path, dirdepth)
                dir_size += this_size
            else:
                ftype = checkfile(entry.name, entry.path, entry.stat(follow_symlinks=False).st_size, 0,
                                  dirdepth, False)
                # if ftype == 'bin':
                #     if dir_entries == 1:
                #         all_bin = True
                # else:
                #     all_bin = False
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


def check_singlefiles():
    # Check for singleton js & other single files
    sfmatch = False
    sf_list = []
    for thisfile in global_values.file_list['src']:
        if thisfile.find("##") > 0:
            continue
        ext = os.path.splitext(thisfile)[1]
        if ext == '.js':
            # get dir
            # check for .js in filenamesstring
            hash = get_path_hash(os.path.dirname(thisfile))

            thisdir = global_values.dir_dict[hash]

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
        global_values.file_list['js_single'] = sf_list
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


def signature_process(full):
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

    full_rep = ''
    # Produce Recommendations
    if global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][global_values.notinarc] > 5000000000:
        messages.message('SCAN1',
                         trunc((global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][
                             global_values.notinarc]) / 1000000))
    elif global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][global_values.notinarc] > 2000000000:
        messages.message('SCAN2',
                         trunc((global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][
                             global_values.notinarc]) / 1000000))

    if global_values.counts['file'][global_values.notinarc] + global_values.counts['file'][global_values.inarc] > 1000000:
        messages.message('SCAN3',
                         trunc((global_values.counts['file'][global_values.notinarc] + global_values.counts['file'][
                             global_values.inarc])))
    elif global_values.counts['file'][global_values.notinarc] + global_values.counts['file'][global_values.inarc] > 200000:
        messages.message('SCAN4',
                         trunc((global_values.counts['file'][global_values.notinarc] + global_values.counts['file'][
                             global_values.inarc])))

    #
    # Need to add check for nothing to scan (no supported scan files)
    if global_values.counts['src'][global_values.notinarc] + global_values.counts['src'][global_values.inarc] + global_values.counts['jar'][
        global_values.notinarc] + global_values.counts['jar'][global_values.inarc] + \
            global_values.counts['other'][global_values.notinarc] + global_values.counts['other'][global_values.inarc] == 0:
        messages.message('SCAN5')

    if global_values.sizes['bin'][global_values.notinarc] + global_values.sizes['bin'][global_values.inarc] > 20000000:
        messages.message('SCAN6',
                         trunc((global_values.sizes['bin'][global_values.notinarc] + global_values.sizes['bin'][
                             global_values.inarc]) / 1000000), len(global_values.file_list['bin']))
        if full and len(global_values.files_dict['bin_large']) > 0:
            full_rep += ("\nLARGE BINARY FILES:\n")
            for fbin in global_values.files_dict['bin_large'].keys():
                full_rep += ("    {} (Size {:d}MB)\n".format(fbin, int(
                    global_values.files_dict['bin_large'][fbin] / 1000000)))
            full_rep += (
                "\nConsider using the following command to zip binary files and send to binary scan (subject to license):\n    zip binary_files.zip \n")
            # for fbin in global_values.bin_large_dict.keys():
            #     if fbin.find("##") < 0:
            #         binzip_list.append(fbin)
            #     elif fbin.split("##")[0] not in binzip_list:
            #         binzip_list.append(fbin.split("##")[0])
            # num = 0
            # for fbin in binzip_list:
            #     if num > 0:
            #         f.write("\n")
            #     f.write("    {}".format(fbin))
            #     num += 1
            # f.write(
            #     "\n\nThen run Detect with the following options to send the archive for binary scan:\n    --detect.tools=BINARY_SCAN --detect.binary.scan.file.path=binary_files.zip\n\n")

    if global_values.counts['lic'][global_values.notinarc] > 10:
        messages.message('FILES2')

    if global_values.counts['src'][global_values.notinarc] + global_values.counts['src'][global_values.inarc] > 10:
        messages.message('FILES3')

    check_singlefiles()
    print(" Done")


def detector_process(full):
    import shutil

    print("- Processing PM Configurations .....", end="", flush=True)

    pm_allfiles, pm_allexts = process_pmdata()

    count = 0
    det_depth1 = 0
    det_other = 0
    det_max_depth = 0
    det_min_depth = 100

    pm_found_dict = {}

    det_files_by_depth = {}
    if len(global_values.files_dict['det']) > 0:
        for dethash in global_values.files_dict['det'].keys():
            command_exists = False
            detpath = global_values.files_dict['det'][dethash]['path']
            if det_excluded(detpath):
                continue
            depth = global_values.files_dict['det'][dethash]['depth']
            if depth == 1:
                det_depth1 += 1
            elif depth > 1:
                det_other += 1
            if depth > det_max_depth:
                det_max_depth = depth
            if depth < det_min_depth:
                det_min_depth = depth

            fname = os.path.basename(detpath)
            pm = ''
            if fname in pm_allfiles.keys():
                pm = pm_allfiles[fname]
            elif os.path.splitext(fname)[1] in pm_allexts.keys():
                pm = pm_allexts[os.path.splitext(fname)[1]]

            if pm != '':
                # files_rep += detpath + '\n'
                if pm in pm_found_dict.keys():
                    pm_found_dict[pm]['count'] += 1
                    if depth < pm_found_dict[pm]['mindepth']:
                        pm_found_dict[pm]['mindepth'] = depth
                    if depth > pm_found_dict[pm]['maxdepth']:
                        pm_found_dict[pm]['maxdepth'] = depth
                else:
                    pm_found_dict[pm] = {
                        'count': 1,
                        'mindepth': depth,
                        'maxdepth': depth,
                        'exes_missing': False,
                        'lockfound': True,
                    }
                    exes = global_values.pm_dict[pm]['execs']
                    # missing_cmds = ""
                    all_missing = True
                    for exe in exes:
                        if shutil.which(exe) is not None:
                            all_missing = False
                            break
                    if all_missing:
                        pm_found_dict[pm]['exes_missing'] = True
                    global_values.detectors_list.append(pm)

                # Check for lockfiles
                lockfile_message = ''
                if len(global_values.pm_dict[pm]['lock_files']) > 0:
                    dir = os.path.dirname(detpath)
                    found = False
                    for entry in os.listdir(dir):
                        if os.path.isfile(entry) and entry in global_values.pm_dict[pm]['lock_files']:
                            found = True

                    if not found:
                        pm_found_dict[pm]['lockfound'] = False
                        lockfile_message = ' *'

                if depth not in det_files_by_depth.keys():
                    det_files_by_depth[depth] = [detpath + lockfile_message]
                else:
                    det_files_by_depth[depth].append(detpath + lockfile_message)

        global_values.full_rep += "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n" + \
                                  "\nALL PACKAGE MANAGER CONFIG FILES FOUND (sorted by depth - * indicates missing lockfile):"
        for depth in sorted(det_files_by_depth.keys()):
            global_values.full_rep += f"\nDEPTH {depth}:\n- " + '\n- '.join(det_files_by_depth[depth])

        def pm_getter(item):
            return item[1]['mindepth']

        global_values.rep += ("\nPACKAGE MANAGER CONFIG FILE SUMMARY:\n\n"
                              "                MinDepth  MaxDepth    Count   Info\n")
        for item in sorted(pm_found_dict.items(), key=pm_getter):
            pm = item[0]
            info = ''

            # Work out the pm scenario
            lock_missing_reqd = False
            if not item[1]['lockfound'] and global_values.pm_dict[pm]['lockfile_reqd']:
                # Lockfile missing and required
                info += '- Lockfile(s) required but not found '
                if item[1]['mindepth'] == 1:
                    messages.message('PACKAGES12', ','.join(exes)) #To do
                else:
                    messages.message('PACKAGES13', ','.join(exes)) #To do

            # if item[1]['exes_missing']:
            if item[1]['exes_missing'] and global_values.pm_dict[pm]['exec_reqd']:
                exes = global_values.pm_dict[pm]['execs']
                # info = "Missing package manager executables '{}'".format(','.join(exes))
                info = '- Package Manager missing and required '
                if item[1]['mindepth'] == 1:
                    messages.message('PACKAGES3', ','.join(exes))
                else:
                    messages.message('PACKAGES4', ','.join(exes))

                if global_values.pm_dict[pm]['accuracy'] == 'LOW':
                    if (global_values.pm_dict[pm]['exec_reqd'] and item[1]['exes_missing'] and
                        not item[1]['lockfound'] and global_values.pm_dict[pm]['lockfile_reqd']):
                        info += " - LOW accuracy scan due to missing PM/lockfiles"
                        if item[1]['mindepth'] == 1:
                            messages.message('PACKAGES6', ','.join(exes))
                        else:
                            messages.message('PACKAGES7', ','.join(exes))

            if platform.system() != "Linux" and 'linux_only' in global_values.pm_dict[pm] and global_values.pm_dict[pm]['linux_only']:
                if item[1]['mindepth'] == 1:
                    messages.message('PLATFORM3', pm)
                else:
                    messages.message('PLATFORM4', pm)

            if pm in ['PIP', 'PYTHON']:
                check_python_venv(item[1]['mindepth'])

            if pm in ['NPM', 'YARN', 'LERNA', 'PNPM']:
                if item[1]['mindepth'] == 1:
                    messages.message('PACKAGES10')
                else:
                    messages.message('PACKAGES11')

            global_values.rep += \
                "  - {:11} {:>8d}  {:>8d}    {:>5,d}   {}\n".format(
                    item[0], item[1]['mindepth'], item[1]['maxdepth'], item[1]['count'], info)

        global_values.rep += "  TOTAL                               {:>5,d}\n".format(len(
            global_values.files_dict['det']))
        global_values.rep += " (PM config files in archives         {:>5,d})\n".format(
            global_values.counts['det'][global_values.inarc])

    if det_depth1 == 0 and det_other > 0:
        messages.message('PACKAGES1', det_min_depth, det_max_depth)

    if det_depth1 == 0 and det_other == 0:
        messages.message('PACKAGES2')

    if global_values.counts['det'][global_values.inarc] > 0:
        messages.message('PACKAGES5')

    for pm in global_values.detectors_list:
        if 'cli_options' in pm_found_dict[pm]:
            global_values.cli_msgs_dict['dep'] += (
                    f"For {pm}:\n" + global_values.pm_dict[pm]['cli_options'] + '\n')
        if 'cli_reqd' in pm_found_dict[pm]:
            global_values.cli_msgs_dict['crit'] += (
                    f"For {pm}:\n" + global_values.pm_dict[pm]['cli_reqd'] + '\n')

    print(" Done")

    return


def check_python_venv(depth):
    if sys.prefix != sys.base_prefix:
        # In Virtualenv
        return
    if depth == 1:
        messages.message('PACKAGES8')
    else:
        messages.message('PACKAGES9')
