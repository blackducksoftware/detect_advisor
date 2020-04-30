# Synopsys Detect Advisor Script - detect_advisor.py v0.2 Beta
# OVERVIEW
This script is provided under an OSS license (specified in the LICENSE file) to assist users when scanning projects using the Synopsys Detect program to scan projects.

It does not represent any extension of licensed functionality of Synopsys software itself and is provided as-is, without warranty or liability.

# DESCRIPTION

The `detect_advisor.py` script processes the specified folder (and sub-folders) to provide recommendations on how to run Synopsys Detect to scan optimally.

It will check the prerequisites to run Detect (including the correct version of Java) and scan the project location for files and archives, calculate the total scan size, check for project files and package managers and will also detect large duplicate files and folders.

It will expand .zip and .jar files automatically, processing recursive files (zips within zips etc.). Other archive types (.gz, .tar, .Z etc.) are not currently expanded.

It will produce a set of categorized recommendations and Detect command line options to support different types of scans and other operations.

It can optionally write a report file including the console output and other information, and also create a .bdignore and .yml project config file with appropariate options.

# PREREQUISITES

Python 3 must be installed prior to using this script.

# USAGE

The `detect_advisor.py` script can be invoked as follows:

    usage: detect_advisor [-h] [-r REPORT] [-d] [-s] [-c] [-f] scanfolder

    Examine files/folders to determine scan recommendations

    positional arguments:
      scanfolder            Project folder to analyse

    optional arguments:
      -h, --help            show this help message and exit
      -r REPORT, --report REPORT
                            Output report file (must not exist already)
      -d, --detectors_only  Check for detector files and prerequisites only
      -s, --signature_only  Check for files and folders for signature scan only
      -c, --critical_only   Only show critical issues which will cause Detect to fail
      -o, --output_config   Create .yml config and .bdignore file in project folder

The `scanfolder` is required and can be a relative or absolute path.

The `-r` or `--report` option allows a report file to be specified which will contain the console output and additional information; when the `-f` or `--full` option is also specified, lists of found files and other information will be added.

The `-c` or `--critical_only` option will limit the console output to critical issues only and skip the summary section and other information, although these sections will be written to the report file if specified with `-r repfile`.

The `-d` and `-s` options specify that only Dependency (Detector) or Signature scan checking should be performed respectively.

# EXAMPLE USAGE

The following command will run the script on the `myproject` sub-folder, producing standard console output only:

    python3 detect_advisor.py myproject
    
The following command will run the script on the `myproject` sub-folder, producing standard console output and outputting additional information to the `myreport.txt` file (which must not already exist):

    python3 detect_advisor.py -r myreport.txt myproject

The following command will scan the absolute path `/users/matthew/myproject`; the `-c` option will reduce the console output to only include critical issues while writing full output in the `myreport.txt` file:

    python3 detect_advisor.py -c -r myreport.txt /users/matthew/myproject
    
The following command will scan the absolute path `/users/matthew/myproject`; the `-o` option will cause `.bdignore` and `application-project.yml` files to be written to the project folder:

    python3 detect_advisor.py -o /users/matthew/myproject

The following command will scan the absolute path `/users/matthew/myproject`; the `-s` option will cause only Singature scan checking to be performed:

    python3 detect_advisor.py -s -r myreport.txt /users/matthew/myproject

# SUMMARY INFO

This section includes counts and size analysis for the files and folders.

    SUMMARY INFO:            Num Outside     Size Outside      Num Inside     Size Inside     Size Inside
                                Archives         Archives        Archives        Archives        Archives
                                                                            (UNcompressed)    (compressed)
    --------------------  --------------   --------------   -------------   -------------   -------------
    Files (exc. Archives)        337,763         5,759 MB         130,126          653 MB          160 MB
    Archives (exc. Jars)              27           761 MB               0            0 MB            0 MB
    --------------------  --------------   --------------   -------------   -------------   -------------
    Folders                       34,599              N/A          10,309             N/A             N/A   
    Source Files                 168,351         1,050 MB          53,740          171 MB           34 MB
    JAR Archives                      18           195 MB               9            0 MB            0 MB
    Binary Files                      56           395 MB              10            0 MB            0 MB
    Other Files                  169,323         3,545 MB          76,376          481 MB          125 MB
    Package Mgr Files                  0             0 MB               0            0 MB            0 MB
    Large Files (>5MB)                41           361 MB               1            9 MB            4 MB
    Huge Files (>20MB)                33         2,150 MB               1           35 MB            6 MB
    --------------------  --------------   --------------   -------------   -------------   -------------
    All Files (Scan size)        337,790         6,520 MB         130,126          653 MB          160 MB
    
    PACKAGE MANAGER FILES:
    - In invocation folder:   0
    - In sub-folders:         3329
    - In archives:            0
    - Minimum folder depth:   5
    - Maximum folder depth:   14
    ---------------------------------
    - Total discovered:       3329

# RECOMMENDATIONS

This section includes a list of findings categorised into CRITICAL (will cause Detect to fail), IMPORTANT (may impact the scope and type of scan) and INFORMATION (potential additional options subject to requirements but which will not impact scope of the standard scan) sections:

    RECOMMENDATIONS:
    - CRITICAL: Overall scan size (6,520 MB) is too large
        Impact:  Scan will fail
        Action:  Ignore folders or remove large files

    -----------------------------------------------------------------------------------------------------    
    - IMPORTANT: No package manager files found in invocation folder but do exist in sub-folders
        Impact:  Dependency scan will not be run
        Action:  Specify --detect.detector.depth=5
        
    - IMPORTANT: Package manager programs (dotnet) missing for package files in sub-folders
        Impact:  The scan will fail if the scan depth is modified from the default
        Action:  Either install package manager programs or
                 consider specifying --detect.detector.buildless=true
                 
    - IMPORTANT: Large amount of data (396 MB) in 66 binary files found
        Impact:  Binary files not analysed by standard scan, will impact Capacity license usage
        Action:  Remove files or ignore folders, also consider zipping
                 binary files and using Binary scan
                 
    - IMPORTANT: Large amount of data (594 MB) in 8 duplicate folders
        Impact:  Scan capacity potentially utilised without detecting additional
                 components, will impact Capacity license usage
        Action:  Remove or ignore duplicate folders
        
    - IMPORTANT: Large amount of data (556 MB) in 17 duplicate files
        Impact:  Scan capacity potentially utilised without detecting additional
                 components, will impact Capacity license usage
        Action:  Remove duplicate files or ignore folders
    
    -----------------------------------------------------------------------------------------------------    
    - INFORMATION: Overall number of files (653,981,695) is large
        Impact:  Scan time could be long
        Action:  Ignore folders or split project (scan sub-projects)
        
    - INFORMATION: License or notices files found
        Impact:  Local license text may need to be scanned
        Action:  Add options --detect.blackduck.signature.scanner.license.search=true
                 and optionally --detect.blackduck.signature.scanner.upload.source.mode=true

    - INFORMATION: Source files found for which Snippet analysis supported
        Impact:  Snippet analysis can discover copied OSS source files and functions
        Action:  Add options --detect.blackduck.signature.scanner.snippet.matching=SNIPPET_MATCHING

    - INFORMATION: 5739 singleton .js files found
        Impact:  OSS components within JS files may not be detected
        Action:  Consider specifying Single file matching
                 (--detect.blackduck.signature.scanner.individual.file.matching=SOURCE)

# DETECT CLI

This section includes recommended CLI options for Synopsys Detect. Note that a `.bdignore` file may also be recommended which will be listed in the optional report file (`-r repfile`) if specified.

    DETECT CLI

        MINIMUM REQUIRED OPTIONS:
            --blackduck.url=https://YOURSERVER
            --blackduck.api.token=YOURTOKEN
            --detect.source.path='/Users/matthewbrady/Documents/detect_adviser'
            --detect.detector.buildless=true
                (OR install package managers 'dotnet' OR use --detect.XXXX.path=<LOCATION> where XXX is package manager)
    
            (Note that .bdignore exclude file is recommended - see the report file 'repfile.txt' or use '-o' option)
    
        PROJECT OPTIONS:
            --detect.project.name=PROJECT_NAME
            --detect.project.version.name=VERSION_NAME
                (Optionally specify project and version names)
            --detect.project.tier=X
                (Optionally define project tier numeric)
            --detect.project.version.phase=ARCHIVED/DEPRECATED/DEVELOPMENT/PLANNING/PRERELEASE/RELEASED
                (Optionally specify project phase - default DEVELOPMENT)
            --detect.project.version.distribution=EXTERNAL/SAAS/INTERNAL/OPENSOURCE
                (Optionally specify version distribution - default EXTERNAL)

    Further information in output report file 'repfile.txt'

# REPORT FILE

An optional report file can be specified (`-r repfile` or `--report repfile`) including full information with lists of duplicate large files, duplicate large folders, binary files etc.

If large duplicate files or folders are identified (or folders containing only binary files), then a recommended `.bdignore` with list of folders to ignore is also produced in the report file.

A list of large binary files is also produced in the report file, and you should consider sending them to Binary scan (note this a separate licensed product to standard Black Duck) by zipping into an archive, and using the Detect `--detect.binary.scan.file.path=XXX.zip` option.
