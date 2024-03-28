import os
import argparse
import sys

def check_input_options(prompt, accepted_values):
    value = input(prompt)
    if value == "":
        return 0
    ret = value[0].lower()
    if ret == "q":
        raise Exception("quit")
    ind = 0
    for val in accepted_values:
        if ret == val[0].lower():
            return ind
        ind += 1
    raise Exception("quit")


def check_input_yn(prompt, default):
    if default:
        prompt += " [y]:"
    else:
        prompt += " [n]:"

    value = input(prompt)
    if value == "":
        return default
    ret = value[0].lower()
    if ret == "q":
        raise Exception("quit")
    if ret == "y":
        return True
    elif ret == "n":
        return False
    raise Exception("quit")


def backup_repfile(filename):
    import os

    if os.path.isfile(filename):
        # Determine root filename so the extension doesn't get longer
        n, e = os.path.splitext(filename)

        # Is e an integer?
        try:
            num = int(e)
            root = n
        except ValueError:
            root = filename

        # Find next available file version
        for i in range(1000):
            new_file = "{}.{:03d}".format(root, i)
            if not os.path.isfile(new_file):
                os.rename(filename, new_file)
                print("INFO: Moved old report file '{}' to '{}'\n".format(filename, new_file))
                return new_file
    return ""


def interactive(scanfolder, scantype, critical_only, report, output_config):
    if scanfolder == "" or scanfolder is None:
        scanfolder = os.getcwd()

    try:
        folder = input("Enter project folder to scan (default current folder '{}'):".format(scanfolder))
    except:
        print("Exiting")
        raise "quit"
    # return("", "", False, False, "", False)
    if folder == "":
        folder = scanfolder
    elif not os.path.isdir(folder):
        print("Scan location '{}' does not exist\nExiting".format(folder))
        raise "quit"
    # return("", "", False, False, "", False)
    try:
        if scantype == "d":
            mylist = ['d', 'b', 's']
        elif scantype == "s":
            mylist = ['s', 'd', 'b']
        else:
            mylist = ['b', 'd', 's']
        scantype = check_input_options(
            "Types of scan to check? (b)oth, (d)ependency or (s)ignature] [{}]:".format(scantype), mylist)
        critical_bool = check_input_yn("Critical recommendations only? (y/n)", critical_only)
        if report != "":
            rep_default = True
        else:
            rep_default = False
            report = "report.txt"
        report_bool = check_input_yn("Create output report file? (y/n)", rep_default)
        if report_bool:
            rep = input("Report file name [{}]:".format(report))
            if rep != "":
                report = rep
        config_bool = check_input_yn("Create application-project.yml file? (y/n)", output_config)
    except:
        print("Exiting")
        raise "quit"
    return folder, scantype, critical_bool, report, config_bool


def check_config(args):

    if args.scanfolder == "" or args.interactive:
        # 	try:
        if args.detector_only:
            scantype = "d"
        elif args.signature_only:
            scantype = "s"
        else:
            scantype = "b"
        args.scanfolder, scantype, args.critical_only, args.report, args.output_config = \
            interactive(args.scanfolder, scantype, args.critical_only, args.report,
                               args.output_config)
        if scantype == "d":
            args.detector_only = True
        elif scantype == "s":
            args.signature_only = True
    # 	except:
    # 		sys.exit(1)

    if not os.path.isdir(args.scanfolder):
        print("Scan location '{}' does not exist\nExiting".format(args.scanfolder))
        sys.exit(1)

    if args.report and os.path.exists(args.report):
        backup = backup_repfile(args.report)
        print("Report file '{}' already existed - backed up to {}".format(args.report, backup))


parser = argparse.ArgumentParser(
    description='Check prerequisites for Detect, scan folders, provide recommendations and example CLI options',
    prog='detect-advisor')

parser.add_argument("scanfolder", nargs="?", help="Project folder to analyse", default="")

parser.add_argument("-r", "--report", help="Output report file (must not exist already)")
parser.add_argument("-d", "--detector_only", help="Check for detector files and prerequisites only",
                    action='store_true')
parser.add_argument("-s", "--signature_only", help="Check for files and folders for signature scan only",
                    action='store_true')
parser.add_argument("-c", "--critical_only", help="Only show critical issues which will causes detect to fail",
                    action='store_true')
parser.add_argument("-o", "--output_config", help="Create .yml config file in project folder", action='store_true')
parser.add_argument("-i", "--interactive", help="Use interactive mode to review/set options", action='store_true')
parser.add_argument("-f", "--full", help="Output all information", action='store_true')
