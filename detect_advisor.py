import os
# import tempfile
import re
import platform, sys
import global_values
import config
import process
import output

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

    output.print_summary(args.critical_only, f)

    check_prereqs()

    output.output_recs(args.critical_only, f)

    output.output_cli(args.critical_only, args.report, f)

    if args.output_config:
        output.output_config(args.scanfolder)

    # if args.bdignore:
    # 	create_bdignores()

    print("")
    if f:
        f.write("\n")
        f.close()

main()