import os
from math import trunc
# import tempfile
import re
import platform, sys
import global_values
import config
import process


def print_summary(critical_only, f):
    summary = "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n" + \
              "SUMMARY INFO:\nTotal Scan Size = {:,d} MB\n\n".format(
                  trunc((global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][global_values.notinarc]) / 1000000)) + \
              "                         Num Outside     Size Outside      Num Inside     Size Inside     Size Inside\n" + \
              "                            Archives         Archives        Archives        Archives        Archives\n" + \
              "                                                                        (UNcompressed)    (compressed)\n" + \
              "====================  ==============   ==============   =============   =============   =============\n"

    row = "{:25} {:>10,d}    {:>10,d} MB      {:>10,d}   {:>10,d} MB   {:>10,d} MB\n"

    summary += row.format("Files (exc. Archives)",
                          global_values.counts['file'][global_values.notinarc],
                          trunc(global_values.sizes['file'][global_values.notinarc] / 1000000),
                          global_values.counts['file'][global_values.inarc],
                          trunc(global_values.sizes['file'][global_values.inarcunc] / 1000000),
                          trunc(global_values.sizes['file'][global_values.inarccomp] / 1000000))

    summary += row.format("Archives (exc. Jars)",
                          global_values.counts['arc'][global_values.notinarc],
                          trunc(global_values.sizes['arc'][global_values.notinarc] / 1000000),
                          global_values.counts['arc'][global_values.inarc],
                          trunc(global_values.sizes['arc'][global_values.inarcunc] / 1000000),
                          trunc(global_values.sizes['arc'][global_values.inarccomp] / 1000000))

    summary += "====================  ==============   ==============   =============   =============   =============\n"

    summary += row.format("ALL FILES (Scan size)", global_values.counts['file'][global_values.notinarc] + global_values.counts['arc'][global_values.notinarc],
                          trunc((global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][global_values.notinarc]) / 1000000),
                          global_values.counts['file'][global_values.inarc] + global_values.counts['arc'][global_values.inarc],
                          trunc((global_values.sizes['file'][global_values.inarcunc] + global_values.sizes['arc'][global_values.inarcunc]) / 1000000),
                          trunc((global_values.sizes['file'][global_values.inarccomp] + global_values.sizes['arc'][global_values.inarccomp]) / 1000000))

    summary += "====================  ==============   ==============   =============   =============   =============\n"

    summary += "{:25} {:>10,d}              N/A      {:>10,d}             N/A             N/A   \n".format("Folders",
                                                                                                           global_values.counts[
                                                                                                               'dir'][
                                                                                                               global_values.notinarc],
                                                                                                           global_values.counts[
                                                                                                               'dir'][
                                                                                                               global_values.inarc])

    summary += row.format("Ignored Folders",
                          global_values.counts['ignoredir'][global_values.notinarc],
                          trunc(global_values.sizes['ignoredir'][global_values.notinarc] / 1000000),
                          global_values.counts['ignoredir'][global_values.inarc],
                          trunc(global_values.sizes['ignoredir'][global_values.inarcunc] / 1000000),
                          trunc(global_values.sizes['ignoredir'][global_values.inarccomp] / 1000000))

    summary += row.format("Source Files",
                          global_values.counts['src'][global_values.notinarc],
                          trunc(global_values.sizes['src'][global_values.notinarc] / 1000000),
                          global_values.counts['src'][global_values.inarc],
                          trunc(global_values.sizes['src'][global_values.inarcunc] / 1000000),
                          trunc(global_values.sizes['src'][global_values.inarccomp] / 1000000))

    summary += row.format("JAR Archives",
                          global_values.counts['jar'][global_values.notinarc],
                          trunc(global_values.sizes['jar'][global_values.notinarc] / 1000000),
                          global_values.counts['jar'][global_values.inarc],
                          trunc(global_values.sizes['jar'][global_values.inarcunc] / 1000000),
                          trunc(global_values.sizes['jar'][global_values.inarccomp] / 1000000))

    summary += row.format("Binary Files",
                          global_values.counts['bin'][global_values.notinarc],
                          trunc(global_values.sizes['bin'][global_values.notinarc] / 1000000),
                          global_values.counts['bin'][global_values.inarc],
                          trunc(global_values.sizes['bin'][global_values.inarcunc] / 1000000),
                          trunc(global_values.sizes['bin'][global_values.inarccomp] / 1000000))

    summary += row.format("Other Files",
                          global_values.counts['other'][global_values.notinarc],
                          trunc(global_values.sizes['other'][global_values.notinarc] / 1000000),
                          global_values.counts['other'][global_values.inarc],
                          trunc(global_values.sizes['other'][global_values.inarcunc] / 1000000),
                          trunc(global_values.sizes['other'][global_values.inarccomp] / 1000000))

    summary += row.format("Package Mgr Files",
                          global_values.counts['det'][global_values.notinarc],
                          trunc(global_values.sizes['det'][global_values.notinarc] / 1000000),
                          global_values.counts['det'][global_values.inarc],
                          trunc(global_values.sizes['det'][global_values.inarcunc] / 1000000),
                          trunc(global_values.sizes['det'][global_values.inarccomp] / 1000000))

    summary += row.format("OS Package Files",
                          global_values.counts['pkg'][global_values.notinarc],
                          trunc(global_values.sizes['pkg'][global_values.notinarc] / 1000000),
                          global_values.counts['pkg'][global_values.inarc],
                          trunc(global_values.sizes['pkg'][global_values.inarcunc] / 1000000),
                          trunc(global_values.sizes['pkg'][global_values.inarccomp] / 1000000))

    summary += "--------------------  --------------   --------------   -------------   -------------   -------------\n"

    summary += row.format("Large Files (>{:1d}MB)".format(trunc(global_values.largesize / 1000000)),
                          global_values.counts['large'][global_values.notinarc],
                          trunc(global_values.sizes['large'][global_values.notinarc] / 1000000),
                          global_values.counts['large'][global_values.inarc],
                          trunc(global_values.sizes['large'][global_values.inarcunc] / 1000000),
                          trunc(global_values.sizes['large'][global_values.inarccomp] / 1000000))

    summary += row.format("Huge Files (>{:2d}MB)".format(trunc(global_values.hugesize / 1000000)),
                          global_values.counts['huge'][global_values.notinarc],
                          trunc(global_values.sizes['huge'][global_values.notinarc] / 1000000),
                          global_values.counts['huge'][global_values.inarc],
                          trunc(global_values.sizes['huge'][global_values.inarcunc] / 1000000),
                          trunc(global_values.sizes['huge'][global_values.inarccomp] / 1000000))

    summary += "--------------------  --------------   --------------   -------------   -------------   -------------\n"

    summary += global_values.rep + "\n"

    if not critical_only:
        print(summary)
    if f:
        f.write(summary)




def output_recs(critical_only, f):
    # global global_values.messages

    if f:
        f.write(global_values.messages + "\n")

    print(
        "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\nRECOMMENDATIONS:\n")
    if f:
        f.write("\nRECOMMENDATIONS:\n")

    if global_values.recs_msgs_dict['crit']:
        print(global_values.recs_msgs_dict['crit'])
        if f:
            f.write(global_values.recs_msgs_dict['crit'] + "\n")

    if global_values.recs_msgs_dict['imp']:
        if not critical_only:
            if global_values.recs_msgs_dict['crit']:
                print(
                    "-----------------------------------------------------------------------------------------------------")
            print(global_values.recs_msgs_dict['imp'])
        if f:
            if global_values.recs_msgs_dict['crit']:
                f.write(
                    "-----------------------------------------------------------------------------------------------------\n")
            f.write(global_values.recs_msgs_dict['imp'] + "\n")

    if global_values.recs_msgs_dict['info']:
        if not critical_only:
            if global_values.recs_msgs_dict['crit'] or global_values.recs_msgs_dict['imp']:
                print(
                    "-----------------------------------------------------------------------------------------------------")
            print(global_values.recs_msgs_dict['info'])
        if f:
            if global_values.recs_msgs_dict['crit'] or global_values.recs_msgs_dict['imp']:
                f.write(
                    "-----------------------------------------------------------------------------------------------------\n")
            f.write(global_values.recs_msgs_dict['info'] + "\n")

    if not global_values.recs_msgs_dict['crit'] and not global_values.recs_msgs_dict['imp'] and not global_values.recs_msgs_dict['info']:
        print("- None\n")
        if f:
            f.write("None\n")

    if critical_only and not global_values.recs_msgs_dict['crit']:
        print("- No Critical Recommendations\n")


# if len(bdignore_list)> 0 and f:
# 	f.write("\nFOLDERS WHICH COULD BE IGNORED:\n(Multiple .bdignore files must be created in sub-folders - folder names must use /folder/ pattern)\n\n")
# 	for bpath in bdignore_list:
# 		f.write(bpath)

def check_prereqs():
    import subprocess
    import shutil

    # global global_values.messages

    # Check java
    try:
        if shutil.which("java") is None:
            global_values.recs_msgs_dict['crit'] += "- CRITICAL: Java is not installed or on the PATH\n" + \
                                      "    Impact:  Detect program will fail\n" + \
                                      "    Action:  Install OpenJDK 1.8 or 1.11\n\n"
        # 			if global_values.cli_msgs_dict['reqd'].find("detect.java.path") < 0:
        # 				global_values.cli_msgs_dict['reqd'] += ""    --detect.java.path=<PATH_TO_JAVA>\n" + \
        # 				"    (If Java installed, specify path to java executable if not on PATH)\n"
        else:
            try:
                javaoutput = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)
                # javaoutput = 'openjdk version "13.0.1" 2019-10-15'
                # javaoutput = 'java version "1.8.0_181"'
                crit = True
                if javaoutput:
                    line0 = javaoutput.decode("utf-8").splitlines()[0]
                    prog = line0.split(" ")[0].lower()
                    if prog:
                        version_string = line0.split('"')[1]
                        if version_string:
                            major, minor, _ = version_string.split('.')
                            if prog == "openjdk":
                                crit = False
                                if major == "8" or major == "11":
                                    rec = "none"
                                else:
                                    global_values.recs_msgs_dict[
                                        'imp'] += "- IMPORTANT: OpenJDK version {} is not documented as supported by Detect\n".format(
                                        version_string) + \
                                                  "    Impact:  Scan may fail\n" + \
                                                  "    Action:  Check that Detect operates correctly\n\n"
                            elif prog == "java":
                                crit = False
                                if major == "1" and (minor == "8" or minor == "11"):
                                    rec = "none"
                                else:
                                    global_values.recs_msgs_dict[
                                        'imp'] += "- IMPORTANT: Java version {} is not documented as supported by Detect\n".format(
                                        version_string) + \
                                                  "    Impact:  Scan may fail\n" + \
                                                  "    Action:  Check that Detect operates correctly\n\n"
            except:
                crit = True

            if crit:
                global_values.recs_msgs_dict['crit'] += "- CRITICAL: Java program version cannot be determined\n" + \
                                          "    Impact:  Scan may fail\n" + \
                                          "    Action:  Check Java or OpenJDK version 1.8 or 1.11 is installed\n\n"
    # 				if global_values.cli_msgs_dict['reqd'].find("detect.java.path") < 0:
    # 					global_values.cli_msgs_dict['reqd'] += "--detect.java.path=<PATH_TO_JAVA>\n" + \
    # 					"    (If Java installed, specify path to java executable if not on PATH)\n"

    except:
        global_values.recs_msgs_dict['crit'] += "- CRITICAL: Java is not installed or on the PATH\n" + \
                                  "    Impact:  Detect program will fail\n" + \
                                  "    Action:  Install OpenJDK 1.8 or 1.11\n\n"
    # 		if global_values.cli_msgs_dict['reqd'].find("detect.java.path") < 0:
    # 			global_values.cli_msgs_dict['reqd'] += "--detect.java.path=<PATH_TO_JAVA>\n" + \
    # 			"    (If Java installed, specify path to java executable if not on PATH)\n"

    # os_platform = ""
    if platform.system() == "Linux" or platform.system() == "Darwin":
        os_platform = "linux"
        # check for bash and curl
        if shutil.which("bash") is None:
            global_values.recs_msgs_dict['crit'] += "- CRITICAL: Bash is not installed or on the PATH\n" + \
                                      "    Impact:  Detect program will fail\n" + \
                                      "    Action:  Install Bash or add to PATH\n\n"
    else:
        os_platform = "win"

    if shutil.which("curl") is None:
        global_values.recs_msgs_dict['crit'] += "- CRITICAL: Curl is not installed or on the PATH\n" + \
                                  "    Impact:  Detect program will fail\n" + \
                                  "    Action:  Install Curl or add to PATH\n\n"
    else:
        if not check_connection("https://detect.synopsys.com"):
            global_values.recs_msgs_dict['crit'] += "- CRITICAL: No connection to https://detect.synopsys.com\n" + \
                                      "    Impact:  Detect wrapper script cannot be downloaded, Detect cannot be started\n" + \
                                      "    Action:  Either configure proxy (See CLI section) or download Detect manually and run offline (see docs)\n\n"
            global_values.cli_msgs_dict['detect'] = global_values.cli_msgs_dict["detect_" + os_platform + "_proxy"]
        else:
            global_values.cli_msgs_dict['detect'] = global_values.cli_msgs_dict["detect_" + os_platform]
            if not check_connection("https://sig-repo.synopsys.com"):
                global_values.recs_msgs_dict['crit'] += "- CRITICAL: No connection to https://sig-repo.synopsys.com\n" + \
                                          "    Impact:  Detect jar cannot be downloaded; Detect cannot run\n" + \
                                          "    Action:  Either configure proxy (See CLI section) or download Detect manually and run offline (see docs)\n\n"


def check_connection(url):
    import subprocess

    try:
        output = subprocess.check_output(['curl', '-s', '-m', '5', url], stderr=subprocess.STDOUT)
        return True
    except:
        return False


def output_cli(critical_only, report, f):
    output = "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\nDETECT CLI:\n\n"
    if global_values.recs_msgs_dict['crit']:
        output += "Note that scan will probably fail - see CRITICAL recommendations above\n\n"

    output += "    DETECT COMMAND:\n"
    output += re.sub(r"^", "    ", global_values.cli_msgs_dict['detect'], flags=re.MULTILINE)
    output += "\n    MINIMUM REQUIRED OPTIONS:\n"
    output += re.sub(r"^", "    ", global_values.cli_msgs_dict['reqd'], flags=re.MULTILINE)

    print(output)
    # if len(bdignore_list) > 0:
    # 	if report:
    # 		print("        (Note that '.bdignore' exclude file is recommended - see the report file '{}' or use '-b' option\n" + \
    # 		"        to create '.bdignore' files in sub-folders)\n".format(report))
    # 	else:
    # 		print("        (Note that '.bdignore' exclude file is recommended - create a report file using '-r repfile' to\n" + \
    # 		"        see recommended folders to exclude or use '-b' option to create '.bdignore' files in sub-folders)\n")
    if f:
        f.write(output + "\n")

    output = ""
    if global_values.cli_msgs_dict['scan'] != '':
        output += "\nOPTIONS TO IMPROVE SCAN COVERAGE:\n" + global_values.cli_msgs_dict['scan'] + "\n"

    if global_values.cli_msgs_dict['size'] != '':
        output += "\nOPTIONS TO REDUCE SIGNATURE SCAN SIZE:\n" + global_values.cli_msgs_dict['size'] + "\n"

    if global_values.cli_msgs_dict['dep'] != '':
        output += "\nOPTIONS TO OPTIMIZE DEPENDENCY SCAN:\n" + global_values.cli_msgs_dict['dep'] + "\n"

    if global_values.cli_msgs_dict['lic'] != '':
        output += "\nOPTIONS TO IMPROVE LICENSE COMPLIANCE ANALYSIS:\n" + global_values.cli_msgs_dict['lic'] + "\n"

    if global_values.cli_msgs_dict['proj'] != '':
        output += "\nPROJECT OPTIONS:\n" + global_values.cli_msgs_dict['proj'] + "\n"

    if global_values.cli_msgs_dict['rep'] != '':
        output += "\nREPORTING OPTIONS:\n" + global_values.cli_msgs_dict['rep'] + "\n"

    output = re.sub(r"^", "    ", output, flags=re.MULTILINE)

    if not critical_only:
        print(output)
    if f:
        f.write(output + "\n")

    if f:
        print("INFO: Output report file '{}' created".format(report))
    else:
        print("INFO: Use '-r repfile' to produce report file with more information")


def output_config(projdir):
    config_file = os.path.join(projdir, "application-project.yml")
    if not os.path.exists(config_file):
        config = "#\n# EXAMPLE PROJECT CONFIG FILE\n" + \
                 "# Uncomment and update required options\n#\n#\n" + \
                 "# DETECT COMMAND TO RUN:\n#\n" + global_values.cli_msgs_dict['detect'] + "\n" + \
                 "# MINIMUM REQUIRED OPTIONS:\n#\n" + global_values.cli_msgs_dict['reqd'] + "\n" + \
                 "# OPTIONS TO IMPROVE SCAN COVERAGE:\n#\n" + global_values.cli_msgs_dict['scan'] + "\n" + \
                 "# OPTIONS TO REDUCE SIGNATURE SCAN SIZE:\n#\n" + global_values.cli_msgs_dict['size'] + "\n" + \
                 "# OPTIONS TO CONFIGURE DEPENDENCY SCAN:\n#\n" + global_values.cli_msgs_dict['dep'] + "\n" + \
                 "# OPTIONS TO IMPROVE LICENSE COMPLIANCE ANALYSIS:\n#\n" + global_values.cli_msgs_dict['lic'] + "\n" + \
                 "# PROJECT OPTIONS:\n#\n" + global_values.cli_msgs_dict['proj'] + "\n" + \
                 "# REPORTING OPTIONS:\n#\n" + global_values.cli_msgs_dict['rep'] + "\n"

        config = re.sub("=", ": ", config)
        config = re.sub(r"\n ", r"\n#", config, flags=re.S)
        config = re.sub(r"\n--", r"\n#", config, flags=re.S)
        try:
            c = open(config_file, "a")
            c.write(config)
            c.close()
            print(
                "INFO: Config file 'application-project.yml' file written to project folder (Edit to uncomment options)\n" + \
                "      - Use '--spring.profiles.active=project' to specify this configuration")
        except Exception as e:
            print('ERROR: Unable to create project config file ' + str(e))
    else:
        print("INFO: Project config file 'application-project.yml' already exists - not updated")


def main():
    args = config.parser.parse_args()
    config.check_config(args)

    global_values.cli_msgs_dict['reqd'] += "--detect.source.path='{}'\n".format(os.path.abspath(args.scanfolder))

    print(
        "\nDETECT ADVISOR v{} - for use with Synopsys Detect versions up to v{}\n".format(
            global_values.advisor_version, global_values.detect_version))

    print("PROCESSING:")

    if os.path.isabs(args.scanfolder):
        print("Working on project folder '{}'\n".format(args.scanfolder))
    else:
        print("Working on project folder '{}' (Absolute path '{}')\n".format(args.scanfolder,
                                                                             os.path.abspath(args.scanfolder)))

    print("- Reading hierarchy          .....", end="", flush=True)
    process.process_dir(args.scanfolder, 0, False)
    print(" Done")

    if args.report:
        try:
            f = open(args.report, "a")
        except Exception as e:
            print('ERROR: Unable to create output report file \n' + str(e))
            sys.exit(3)
    else:
        f = None

    if not args.signature_only:
        #	if args.full:
        process.detector_process(args.scanfolder, f)
    if args.signature_only:
        global_values.cli_msgs_dict['reqd'] += "--detect.tools=SIGNATURE_SCAN\n"

    if not args.detector_only:
        #	if args.full:
        process.signature_process(args.scanfolder, f)
    if args.detector_only:
        global_values.cli_msgs_dict['reqd'] += "--detect.tools=DETECTOR\n"

    print_summary(args.critical_only, f)

    check_prereqs()

    output_recs(args.critical_only, f)

    output_cli(args.critical_only, args.report, f)

    if args.output_config:
        output_config(args.scanfolder)

    # if args.bdignore:
    # 	create_bdignores()

    print("")
    if f:
        f.write("\n")
        f.close()

main()