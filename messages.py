import global_values

messages_dict = {
    'JAVA1': {
        'level': 'crit',
        'desc': 'Java is not installed or on the PATH',
        'impact': 'Detect program will fail',
        'action': 'Install Java or OpenJDK 1.8+',
    },

    'JAVA2': {
        'level': 'crit',
        'desc': 'Java program version cannot be determined',
        'impact': 'Scan may fail',
        'action': 'Check Java or OpenJDK version 1.8 or 1.11 is installed',
    },

    'JAVA3': {
        'level': 'crit',
        'desc': 'Java is not installed or on the PATH',
        'impact': 'Detect program will fail',
        'action': 'Install OpenJDK 1.8 or 1.11',
    },

    'PLATFORM1': {
        'level': 'crit',
        'desc': 'bash is not installed or on the PATH',
        'impact': 'Detect program will fail',
        'action': 'Install Bash or add to PATH',
    },

    'PLATFORM2': {
        'level': 'crit',
        'desc': 'Curl is not installed or on the PATH',
        'impact': 'Detect program will fail',
        'action': 'Install Curl or add to PATH'
    },

    'PLATFORM3': {
        'level': 'crit',
        'desc': 'Package manager "{}" requires scanning on a Linux platform',
        'impact': 'Scan will fail',
        'action': 'Re-run Detect scan on Linux'
    },

    'PLATFORM4': {
        'level': 'imp',
        'desc': 'Package manager "{}" required for package config found lower than level 0 requires scanning on a Linux platform',
        'impact': 'Scan may fail if detector depth changed from default value 0',
        'action': 'Re-run Detect scan on Linux'
    },

    'NETWORK1': {
        'level': 'crit',
        'desc': 'No connection to https://detect.synopsys.com',
        'impact': 'Detect wrapper script cannot be downloaded, Detect cannot be started',
        'action': 'Either configure proxy (See CLI section) or download Detect manually and run offline (see docs)'
    },

    'NETWORK2': {
        'level': 'crit',
        'desc': 'No connection to https://sig-repo.synopsys.com',
        'impact': 'Detect jar cannot be downloaded; Detect cannot run',
        'action': 'Either configure proxy (See CLI section) or download Detect manually and run offline (see docs)'
    },

    'FILES1': {
        'level': 'info',
        'desc': '{} singleton .js files found',
        'impact': 'OSS components within JS files may not be detected',
        'action': 'Consider specifying Single file matching in Signature scan (--detect.blackduck.signature.scanner.individual.file.matching=SOURCE)',
        'cli': 'scan',
        'cli_search': 'detect.blackduck.signature.scanner.individual.file.matching',
        'cli_text': '--detect.blackduck.signature.scanner.individual.file.matching=SOURCE (To include singleton .js files in signature scan for OSS matches)'
    },

    'FILES2': {
        'level': 'info',
        'desc': 'License or notices files found',
        'impact': 'Local license text may need to be scanned',
        'action': 'Add options --detect.blackduck.signature.scanner.license.search=true and optionally --detect.blackduck.signature.scanner.upload.source.mode=true',
        'cli': 'lic',
        'cli_search': 'detect.blackduck.signature.scanner.upload.source.mode',
        'cli_text': '--detect.blackduck.signature.scanner.upload.source.mode=true (CAUTION - will upload local source files)',
    },

    'FILES3': {
        'level': 'info',
        'desc': 'Source files found for which Snippet analysis supported',
        'impact': 'Snippet analysis can discover copied OSS source files and functions',
        'action': 'Add option --detect.blackduck.signature.scanner.snippet.matching=SNIPPET_MATCHING',
        'cli': 'lic',
        'cli_search': 'detect.blackduck.signature.scanner.snippet.matching',
        'cli_text': '--detect.blackduck.signature.scanner.snippet.matching=SNIPPET_MATCHING (To search for copied OSS source files and functions within source files)',
    },

    'SCAN1': {
        'level': 'crit',
        'desc': 'Overall scan size {:>,d} MB) is too large (default max scan size 5GB)',
        'impact': 'Scan will fail',
        'action': 'Ignore folders, remove large files or use repeated scans of sub-folders',
    },

    'SCAN2': {
        'level': 'imp',
        'desc': 'IMPORTANT: Overall scan size ({:>,d} MB) is large',
        'impact': 'Will impact Capacity license usage',
        'action': 'Ignore folders, remove large files or use repeated scans of sub-folders',
    },

    'SCAN3': {
        'level': 'imp',
        'desc': 'Overall number of files ({:>,d}) is very large',
        'impact': 'Scan time could be VERY long',
        'action': 'Ignore folders or split project (scan sub-projects)',
    },

    'SCAN4': {
        'level': 'info',
        'desc': 'Overall number of files ({:>,d}) is large',
        'impact': 'Scan time could be long',
        'action': 'Ignore folders or split project (scan sub-projects)',
    },

    'SCAN5': {
        'level': 'info',
        'desc': 'No source, jar or other files found',
        'impact': 'Scan may not detect any OSS from files (dependencies only)',
        'action': 'Check scan location is correct',
    },

    'SCAN6': {
        'level': 'imp',
        'desc': 'Large amount of data ({:>,d} MB) in {} binary files found',
        'impact': 'Binary files not analysed by standard scan, will increase scan size and impact Capacity license usage',
        'action': 'Remove files or ignore folders (using .bdignore files), also consider zipping files and using Binary scan',
        'cli': 'scan',
        'cli_text': '--detect.binary.scan.file.path=binary_files.zip\n(See report file produced with -r option for how to zip binary files; binary scan license required)'
    },

    'PACKAGES1': {
        'level': 'imp',
        'desc': 'No package manager files found in invocation folder but do exist in sub-folders (minimum {}, maximum {} folders deep)',
        'impact': 'Dependency scan will not be run',
        'action': 'Specify --detect.detector.search.depth=X optionally with --detect.detector.search.continue=true or scan sub-folders separately',
        'cli': 'scan',
        'cli_search': 'detect.detector.search.depth',
        'cli_text': '--detect.detector.search.depth=X optionally with --detect.detector.search.continue=true (To find package manager files within sub-folders)',
    },

    'PACKAGES2': {
        'level': 'info',
        'desc': 'No package manager files found in project at all',
        'impact': 'No dependency scan will be performed',
        'action': 'This may be expected, but ensure you are scanning the correct project location',
    },

    'PACKAGES3': {
        'level': 'crit',
        'desc': 'Package manager programs ({}) missing for package files in invocation folder',
        'impact': 'Scan will fail',
        'action': 'Either install required package manager programs or consider specifying --detect.detector.buildless=true',
        'cli': 'reqd',
        'cli_search': 'detect.detector.buildless',
        'cli_text': '--detect.detector.buildless=true (OR specify --detect.XXXX.path=<LOCATION> where XXX is package manager OR install package managers)',
    },

    'PACKAGES4': {
        'level': 'imp',
        'desc': 'Package manager programs ({}) missing for package files in sub-folders',
        'impact': 'The scan will fail if the scan depth is modified from the default level 0',
        'action': 'Either install required package manager programs or consider specifying --detect.detector.buildless=true',
        'cli': 'reqd',
        'cli_search': 'detect.detector.buildless',
        'cli_text': '--detect.detector.buildless=true (OR specify --detect.XXXX.path=<LOCATION> where XXX is package manager OR install package managers)',
    },

    'PACKAGES5': {
        'level': 'imp',
        'desc': 'Package manager files found in archives',
        'impact': 'Dependency scan not performed for projects in archives',
        'action': 'Optionally extract zip archives and rescan',
    },
}


levtexts = {
    'crit': 'CRITICAL',
    'imp': 'IMPORTANT',
    'info': 'INFO',
    'other': 'OTHER'
}


def message(id, val1='', val2=''):
    if id in messages_dict:
        if val2 != '':
            mtext = f"- {levtexts[messages_dict[id]['level']]}: " + messages_dict[id]['desc'].format(val1, val2) + '\n'
        elif val1 != '':
            mtext = f"- {levtexts[messages_dict[id]['level']]}: " + messages_dict[id]['desc'].format(val1) + '\n'
        else:
            mtext = f"- {levtexts[messages_dict[id]['level']]}: {messages_dict[id]['desc']}\n"

        mtext += f"    Impact:  {messages_dict[id]['impact']}\n" + \
                 f"    Action:  {messages_dict[id]['action']}\n\n"

        global_values.recs_msgs_dict[messages_dict[id]['level']] += mtext

        if 'cli' in messages_dict[id]:
            if 'cli_search' in messages_dict[id]:
                if global_values.cli_msgs_dict[messages_dict[id]['cli']].find(messages_dict[id]['cli_search']) < 0:
                   global_values.cli_msgs_dict[messages_dict[id]['cli']] += messages_dict[id]['cli_text'] + '\n'
            elif 'cli_text' in messages_dict[id]:
               global_values.cli_msgs_dict[messages_dict[id]['cli']] += messages_dict[id]['cli_text'] + '\n'

    return
