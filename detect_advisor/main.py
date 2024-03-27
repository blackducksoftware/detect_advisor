import os
# import tempfile
# import re
import platform
import sys

from . import global_values
from . import config
from . import process
from . import output
from . import messages


def check_prereqs():
    import subprocess
    import shutil

    # global global_values.messages

    # Check java
    try:
        if shutil.which("java") is None:
            messages.message('JAVA1')
        else:
            try:
                subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)

            except subprocess.CalledProcessError:
                messages.message('JAVA2')

    except shutil.Error:
        messages.message('JAVA3')

    if platform.system() == "Linux" or platform.system() == "Darwin":
        os_platform = "linux"
        # check for bash and curl
        if shutil.which("bash") is None:
            messages.message('PLATFORM1')
    else:
        os_platform = "win"

    try:
        if shutil.which("curl") is None:
            messages.message('PLATFORM2')
        else:
            if not check_connection("https://detect.synopsys.com"):
                messages.message('NETWORK1')
                global_values.cli_msgs_dict['detect'] = global_values.cli_msgs_dict["detect_" + os_platform + "_proxy"]
            else:
                global_values.cli_msgs_dict['detect'] = global_values.cli_msgs_dict["detect_" + os_platform]
                if not check_connection("https://sig-repo.synopsys.com"):
                    messages.message('NETWORK2')
    except shutil.Error:
        pass

def check_connection(url):
    import subprocess

    try:
        output = subprocess.check_output(['curl', '-s', '-m', '5', url], stderr=subprocess.STDOUT)
        return True
    except subprocess.SubprocessError:
        return False


def main():
    args = config.parser.parse_args()
    config.check_config(args)

    print(
        "\nDETECT ADVISOR v{} - for use with Synopsys Detect versions up to v{}\n".format(
            global_values.advisor_version, global_values.detect_version))

    print("PROCESSING:")

    check_prereqs()
    global_values.cli_msgs_dict['reqd'] += "--detect.source.path='{}'\n".format(os.path.abspath(args.scanfolder))

    if os.path.isabs(args.scanfolder):
        print("Working on project folder '{}'\n".format(args.scanfolder))
    else:
        print("Working on project folder '{}' (Absolute path '{}')\n".format(args.scanfolder,
                                                                             os.path.abspath(args.scanfolder)))

    print("- Reading Folder Hierarchy     .....", end="", flush=True)
    process.process_dir(args.scanfolder, 0)
    print(" Done")

    if not args.detector_only:
        process.signature_process(args.full)
    if args.detector_only:
        global_values.cli_msgs_dict['reqd'] += "--detect.tools=DETECTOR\n"

    if not args.signature_only:
        process.detector_process(args.full)
    if args.signature_only:
        global_values.cli_msgs_dict['reqd'] += "--detect.tools=SIGNATURE_SCAN\n"

    output.print_summary(args.critical_only, args.report)

    if args.full:
        output.output_full_rep(args.report)

    output.output_recs(args.critical_only, args.report)

    output.output_cli(args.critical_only, args.report)

    if args.output_config:
        output.output_config(args.scanfolder)

    # if args.bdignore:
    # 	create_bdignores()

    print("")


if __name__ == "__main__":
    main()