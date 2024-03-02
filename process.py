import global_values
import zipfile
import os
import io
from math import trunc
import platform


def process_nested_zip(z, zippath, zipdepth, dirdepth):
    # global global_values.max_arc_depth
    # global global_values.global_values.messages

    zipdepth += 1
    if zipdepth > global_values.max_arc_depth:
        max_arc_depth = zipdepth

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
    if tdir not in global_values.dir_dict.keys():
        global_values.counts['dir'][global_values.inarc] += 1
        global_values.dir_dict[tdir] = {}
        global_values.dir_dict[tdir]['num_entries'] = 1
        global_values.dir_dict[tdir]['size'] = zinfo.file_size
        global_values.dir_dict[tdir]['depth'] = dirdepth
        global_values.dir_dict[tdir]['filenamesstring'] = zinfo.filename + ";"
    else:
        global_values.dir_dict[tdir]['num_entries'] += 1
        global_values.dir_dict[tdir]['size'] += zinfo.file_size
        global_values.dir_dict[tdir]['depth'] = dirdepth
        global_values.dir_dict[tdir]['filenamesstring'] += zinfo.filename + ";"

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

    if name in global_values.detectors_file_dict.keys() and path.find("node_modules") < 0:
        if not in_archive:
            global_values.det_dict[path] = dirdepth
        ftype = 'det'
    elif os.path.basename(name) in global_values.ext_list['lic']:
        global_values.file_list['other'].append(path)
        ftype = 'other'
        global_values.counts['lic'][global_values.notinarc] += 1
    elif ext != "":
        if ext in global_values.detectors_ext_dict.keys():
            if not in_archive:
                global_values.det_dict[path] = dirdepth
            ftype = 'det'
        elif ext in global_values.ext_list['src']:
            global_values.file_list['src'].append(path)
            ftype = 'src'
        elif ext in global_values.ext_list['jar']:
            global_values.file_list['jar'].append(path)
            ftype = 'jar'
        elif ext in global_values.ext_list['bin']:
            global_values.file_list['bin'].append(path)
            if size > global_values.largesize:
                global_values.bin_large_dict[path] = size
            ftype = 'bin'
        elif ext in global_values.ext_list['arc']:
            global_values.file_list['arc'].append(path)
            ftype = 'arc'
        elif ext in global_values.ext_list['pkg']:
            global_values.file_list['pkg'].append(path)
            ftype = 'pkg'
        else:
            global_values.file_list['other'].append(path)
            ftype = 'other'
    else:
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


def process_dir(path, dirdepth, ignore):
    dir_size = 0
    dir_entries = 0
    filenames_string = ""
    # global global_values.messages

    global_values.dir_dict[path] = {}
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

    global_values.dir_dict[path]['num_entries'] = dir_entries
    global_values.dir_dict[path]['size'] = dir_size
    global_values.dir_dict[path]['depth'] = dirdepth
    global_values.dir_dict[path]['filenamesstring'] = filenames_string
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
            thisdir = global_values.dir_dict.get(os.path.dirname(thisfile))
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
        global_values.recs_msgs_dict['info'] += "- INFORMATION: {} singleton .js files found\n".format(len(sf_list)) + \
                                  "    Impact:  OSS components within JS files may not be detected\n" + \
                                  "    Action:  Consider specifying Single file matching in Signature scan\n" + \
                                  "             (--detect.blackduck.signature.scanner.individual.file.matching=SOURCE)\n\n"
        if global_values.cli_msgs_dict['scan'].find("individual.file.matching") < 0:
            global_values.cli_msgs_dict['scan'] += "--detect.blackduck.signature.scanner.individual.file.matching=SOURCE\n" + \
                                     "    (To include singleton .js files in signature scan for OSS matches)\n"

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


def signature_process(folder, f):
    # print("SIGNATURE SCAN ANALYSIS:")

    # Find duplicates without expanding archives - to avoid processing dups
    # print("- Processing folders         ", end="", flush=True)
    # num_dirdups, size_dirdups = process_dirdups(f)
    # print(" Done")

    # print("- Processing large files     ", end="", flush=True)
    # num_dups, size_dups = process_largefiledups(f)
    # print(" Done")
    #
    print("- Processing Signature Scan  .....", end="", flush=True)

    # Produce Recommendations
    if global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][global_values.notinarc] > 5000000000:
        global_values.recs_msgs_dict['crit'] += "- CRITICAL: Overall scan size ({:>,d} MB) is too large\n".format(
            trunc((global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][global_values.notinarc]) / 1000000)) + \
                                  "    Impact:  Scan will fail\n" + \
                                  "    Action:  Ignore folders, remove large files or use repeated scans of sub-folders (Also consider detect_advisor -b option to create multiple .bdignore files to ignore duplicate folders)\n\n"
    elif global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][global_values.notinarc] > 2000000000:
        global_values.recs_msgs_dict['imp'] += "- IMPORTANT: Overall scan size ({:>,d} MB) is large\n".format(
            trunc((global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][global_values.notinarc]) / 1000000)) + \
                                 "    Impact:  Will impact Capacity license usage\n" + \
                                 "    Action:  Ignore folders, remove large files or use repeated scans of sub-folders (Also consider detect_advisor -b option to create multiple .bdignore files to ignore duplicate folders)\n\n"

    if global_values.counts['file'][global_values.notinarc] + global_values.counts['file'][global_values.inarc] > 1000000:
        global_values.recs_msgs_dict['imp'] += "- IMPORTANT: Overall number of files ({:>,d}) is very large\n".format(
            trunc((global_values.counts['file'][global_values.notinarc] + global_values.counts['file'][global_values.inarc]))) + \
                                 "    Impact:  Scan time could be VERY long\n" + \
                                 "    Action:  Ignore folders or split project (scan sub-projects or consider detect_advisor -b option to create multiple .bdignore files to ignore duplicate folders)\n\n"
    elif global_values.counts['file'][global_values.notinarc] + global_values.counts['file'][global_values.inarc] > 200000:
        global_values.recs_msgs_dict['info'] += "- INFORMATION: Overall number of files ({:>,d}) is large\n".format(
            trunc((global_values.counts['file'][global_values.notinarc] + global_values.counts['file'][global_values.inarc]))) + \
                                  "    Impact:  Scan time could be long\n" + \
                                  "    Action:  Ignore folders or split project (scan sub-projects or consider detect_advisor -b option to create multiple .bdignore files to ignore duplicate folders)\n\n"

    #
    # Need to add check for nothing to scan (no supported scan files)
    if global_values.counts['src'][global_values.notinarc] + global_values.counts['src'][global_values.inarc] + global_values.counts['jar'][global_values.notinarc] + global_values.counts['jar'][global_values.inarc] + \
            global_values.counts['other'][global_values.notinarc] + global_values.counts['other'][global_values.inarc] == 0:
        global_values.recs_msgs_dict['info'] += "- INFORMATION: No source, jar or other files found\n".format(
            trunc((global_values.counts['file'][global_values.notinarc] + global_values.sizes['file'][global_values.inarc]))) + \
                                  "    Impact:  Scan may not detect any OSS from files (dependencies only)\n" + \
                                  "    Action:  Check scan location is correct\n"

    if global_values.sizes['bin'][global_values.notinarc] + global_values.sizes['bin'][global_values.inarc] > 20000000:
        global_values.recs_msgs_dict['imp'] += "- IMPORTANT: Large amount of data ({:>,d} MB) in {} binary files found\n".format(
            trunc((global_values.sizes['bin'][global_values.notinarc] + global_values.sizes['bin'][global_values.inarc]) / 1000000), len(global_values.file_list['bin'])) + \
                                 "    Impact:  Binary files not analysed by standard scan, will impact Capacity license usage\n" + \
                                 "    Action:  Remove files or ignore folders (using .bdignore files), also consider zipping\n" + \
                                 "             files and using Binary scan (See report file produced with -r option)\n\n"
        global_values.cli_msgs_dict['scan'] += "--detect.binary.scan.file.path=binary_files.zip\n" + \
                                 "    (See report file produced with -r option for how to zip binary files; binary scan license required)\n"
        if f and len(global_values.bin_large_dict) > 0:
            f.write("\nLARGE BINARY FILES:\n")
            for fbin in global_values.bin_large_dict.keys():
                f.write("    {} (Size {:d}MB)\n".format(fbin, int(global_values.bin_large_dict[fbin] / 1000000)))
            f.write(
                "\nConsider using the following command to zip binary files and send to binary scan (subject to license):\n    zip binary_files.zip \\\n")
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
        global_values.recs_msgs_dict['info'] += "- INFORMATION: License or notices files found\n" + \
                                  "    Impact:  Local license text may need to be scanned\n" + \
                                  "    Action:  Add options --detect.blackduck.signature.scanner.license.search=true\n" + \
                                  "             and optionally --detect.blackduck.signature.scanner.upload.source.mode=true\n\n"
        global_values.cli_msgs_dict['lic'] += "--detect.blackduck.signature.scanner.license.search=true\n" + \
                                "    (To perform client-side scanning for license files and references)\n"
        if global_values.cli_msgs_dict['lic'].find("upload.source.mode") < 0:
            global_values.cli_msgs_dict['lic'] += "--detect.blackduck.signature.scanner.upload.source.mode=true\n" + \
                                    "    (CAUTION - will upload local source files)\n"

    if global_values.counts['src'][global_values.notinarc] + global_values.counts['src'][global_values.inarc] > 10:
        global_values.recs_msgs_dict['info'] += "- INFORMATION: Source files found for which Snippet analysis supported\n" + \
                                  "    Impact:  Snippet analysis can discover copied OSS source files and functions\n" + \
                                  "    Action:  Add options --detect.blackduck.signature.scanner.snippet.matching=SNIPPET_MATCHING\n\n"
        global_values.cli_msgs_dict['lic'] += "--detect.blackduck.signature.scanner.snippet.matching=SNIPPET_MATCHING\n" + \
                                "    (To search for copied OSS source files and functions within source files)\n"
        if global_values.cli_msgs_dict['lic'].find("upload.source.mode") < 0:
            global_values.cli_msgs_dict['lic'] += "--detect.blackduck.signature.scanner.upload.source.mode=true\n" + \
                                    "    (CAUTION - will upload local source files)\n"

    check_singlefiles(f)
    print(" Done")
    print("")


def detector_process(folder, f):
    import shutil

    print("- Processing Dependency Scan .....", end="", flush=True)

    if f:
        f.write("PROJECT FILES FOUND:\n")

    count = 0
    det_depth1 = 0
    det_other = 0
    cmds_missing1 = ""
    cmds_missingother = ""
    cmds_missing_list = []
    det_max_depth = 0
    det_min_depth = 100
    det_in_arc = 0
    if len(global_values.det_dict) > 0:
        for detpath, depth in global_values.det_dict.items():
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
                if fname in global_values.detectors_file_dict.keys():
                    exes = global_values.detectors_file_dict[fname]
                elif os.path.splitext(fname)[1] in global_values.detectors_ext_dict.keys():
                    exes = global_values.detectors_ext_dict[os.path.splitext(fname)[1]]
                missing_cmds = ""
                for exe in exes:
                    if exe not in global_values.detectors_list:
                        global_values.detectors_list.append(exe)
                        if platform.system() != "Linux" and exe in global_values.linux_only_detectors:
                            if depth == 1:
                                global_values.recs_msgs_dict[
                                    'crit'] += "- CRITICAL: Package manager '{}' requires scanning on a Linux platform\n".format(
                                    exe) + \
                                               "    Impact:  Scan will fail\n" + \
                                               "    Action:  Re-run Detect scan on Linux\n\n"
                            else:
                                global_values.recs_msgs_dict[
                                    'imp'] += "- IMPORTANT: Package manager '{}' requires scanning on a Linux platform\n".format(
                                    exe) + \
                                              "    Impact:  Scan may fail if detector depth changed from default value 0\n" + \
                                              "    Action:  Re-run Detect scan on Linux\n\n"
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

        global_values.rep += "\nPACKAGE MANAGER CONFIG FILES:\n" + \
              "- In invocation folder:   {}\n".format(det_depth1) + \
              "- In sub-folders:         {}\n".format(det_other) + \
              "- In archives:            {}\n".format(det_in_arc) + \
              "- Minimum folder depth:   {}\n".format(det_min_depth) + \
              "- Maximum folder depth:   {}\n".format(det_max_depth) + \
              "---------------------------------\n" + \
              "- Total discovered:       {}\n\n".format(len(global_values.det_dict)) + \
              "Config files for the following Package Managers found: {}\n".format(', '.join(global_values.detectors_list))

    if f and count == 0:
        f.write("    None\n")

    if det_depth1 == 0 and det_other > 0:
        global_values.recs_msgs_dict[
            'imp'] += "- IMPORTANT: No package manager files found in invocation folder but do exist in sub-folders\n" + \
                      "    Impact:  Dependency scan will not be run\n" + \
                      "    Action:  Specify --detect.detector.search.depth={} (although depth could be up to {})\n".format(
                          det_min_depth, det_max_depth) + \
                      "             optionally with -detect.detector.search.continue=true or scan sub-folders separately.\n\n"
        if global_values.cli_msgs_dict['scan'].find("detector.search.depth") < 0:
            global_values.cli_msgs_dict['scan'] += "--detect.detector.search.depth={}\n".format(det_min_depth) + \
                                     "    optionally with optionally with -detect.detector.search.continue=true\n" + \
                                     "    (To find package manager files within sub-folders; note depth {} would find\n".format(
                                         det_max_depth) + \
                                     "    all PM files in sub-folders but higher level projects may already include these)\n"

    if det_depth1 == 0 and det_other == 0:
        global_values.recs_msgs_dict['info'] += "- INFORMATION: No package manager files found in project at all\n" + \
                                  "    Impact:  No dependency scan will be performed\n" + \
                                  "    Action:  This may be expected, but ensure you are scanning the correct location\n\n"

    if cmds_missing1:
        global_values.recs_msgs_dict[
            'crit'] += "- CRITICAL: Package manager programs ({}) missing for package files in invocation folder\n".format(
            cmds_missing1) + \
                       "    Impact:  Scan will fail\n" + \
                       "    Action:  Either install package manager programs or\n" + \
                       "             consider specifying --detect.detector.buildless=true\n\n"
        global_values.cli_msgs_dict['reqd'] += "--detect.detector.buildless=true\n" + \
                                 "    (OR specify --detect.XXXX.path=<LOCATION> where XXX is package manager\n" + \
                                 "    OR install package managers '{}')\n".format(cmds_missing1)

    if cmds_missingother:
        global_values.recs_msgs_dict[
            'imp'] += "- IMPORTANT: Package manager programs ({}) missing for package files in sub-folders\n".format(
            cmds_missingother) + \
                      "    Impact:  The scan will fail if the scan depth is modified from the default\n" + \
                      "    Action:  Install package manager programs\n" + \
                      "             (OR specify --detect.XXXX.path=<LOCATION> where XXX is package manager\n" + \
                      "             OR specify --detect.detector.buildless=true)\n\n"
        if global_values.cli_msgs_dict['scan'].find("detector.buildless") < 0:
            global_values.cli_msgs_dict['scan'] += "--detect.detector.buildless=true\n" + \
                                     "    (OR install package managers '{}'\n".format(cmds_missingother) + \
                                     "    (OR use --detect.XXXX.path=<LOCATION> where XXX is package manager)\n"

    if global_values.counts['det'][global_values.inarc] > 0:
        global_values.recs_msgs_dict['imp'] += "- IMPORTANT: Package manager files found in archives\n" + \
                                 "    Impact:  Dependency scan not performed for projects in archives\n" + \
                                 "    Action:  Extract zip archives and rescan\n\n"

    for cmd in global_values.detectors_list:
        if cmd in global_values.detector_cli_options_dict.keys() and 'dep' in global_values.cli_msgs_dict:
            global_values.cli_msgs_dict['dep'] += " For {}:\n".format(cmd) + global_values.detector_cli_options_dict[cmd]
        if cmd in global_values.detector_cli_required_dict.keys() and 'crit' in global_values.cli_msgs_dict:
            global_values.cli_msgs_dict['crit'] += " For {}:\n".format(cmd) + global_values.detector_cli_required_dict[cmd]

    print(" Done")

    return