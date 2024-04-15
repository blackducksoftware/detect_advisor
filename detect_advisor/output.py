from math import trunc
import os
import re

from . import global_values


def print_summary(critical_only, reportfile):
    if critical_only:
        return

    summary = "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n" + \
              "SUMMARY INFO:\nTotal Scan Size = {:,d} MB\n\n".format(
                  trunc((global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][
                      global_values.notinarc]) / 1000000)) + \
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

    summary += row.format(
        "ALL FILES (Scan size)",
        global_values.counts['file'][global_values.notinarc] + global_values.counts['arc'][global_values.notinarc],
        trunc((global_values.sizes['file'][global_values.notinarc] + global_values.sizes['arc'][
            global_values.notinarc]) / 1000000),
        global_values.counts['file'][global_values.inarc] + global_values.counts['arc'][global_values.inarc],
        trunc((global_values.sizes['file'][global_values.inarcunc] + global_values.sizes['arc'][
            global_values.inarcunc]) / 1000000),
        trunc((global_values.sizes['file'][global_values.inarccomp] + global_values.sizes['arc'][
            global_values.inarccomp]) / 1000000))

    summary += "====================  ==============   ==============   =============   =============   =============\n"

    summary += "{:25} {:>10,d}              N/A      {:>10,d}             N/A             N/A   \n".format(
        "Folders", global_values.counts['dir'][global_values.notinarc],
        global_values.counts['dir'][global_values.inarc])

    summary += row.format(
        "Ignored Folders",
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

    print(summary)
    if reportfile is not None:
        with open(reportfile, "a") as repfile:
            repfile.write(summary)


def output_full_rep(reportfile):

    rep = "\n\n" + global_values.full_rep + "\n\n"

    desc = {
        'large': "LARGE FILES (> {}MB):".format(trunc(global_values.largesize / 1000000)),
        'huge': "HUGE FILES (> {}MB):".format(trunc(global_values.hugesize / 1000000)),
        'js_single': 'SINGLETON JS FILES:',
        'arcs_pm': 'ARCHIVES CONTAINING PACKAGE MANAGER CONFIGS:',
        'bin': 'BINARY FILES:'
    }
    for ftype in desc.keys():
        rep += desc[ftype] + '\n' + "\n".join(global_values.file_list[ftype]) + '\n\n'

    print(rep)

    if reportfile is not None:
        with open(reportfile, "a") as repfile:
            repfile.write(rep)


def output_recs(critical_only, reportfile):
    # global global_values.messages

    text = global_values.messages
    text += \
        "\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\nRECOMMENDATIONS:\n\n"

    if global_values.recs_msgs_dict['crit']:
        text += (global_values.recs_msgs_dict['crit'])

    if global_values.recs_msgs_dict['imp']:
        if not critical_only:
            if global_values.recs_msgs_dict['crit']:
                text += (
                    "-----------------------------------------------------------------------------------------------------\n\n")
            text += (global_values.recs_msgs_dict['imp'])

    if global_values.recs_msgs_dict['info']:
        if not critical_only:
            if global_values.recs_msgs_dict['crit'] or global_values.recs_msgs_dict['imp']:
                text += (
                    "-----------------------------------------------------------------------------------------------------\n\n")
            text += (global_values.recs_msgs_dict['info'])

    if not global_values.recs_msgs_dict['crit'] and not global_values.recs_msgs_dict['imp'] and not global_values.recs_msgs_dict['info']:
        text += ("- None\n")

    if critical_only and not global_values.recs_msgs_dict['crit']:
        text += ("- No Critical Recommendations\n")

    print(text)

    if reportfile is not None:
        with open(reportfile, "a") as repfile:
            repfile.write(text)


def output_cli(critical_only, reportfile):
    output = "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\nDETECT CLI:\n\n"
    if global_values.recs_msgs_dict['crit']:
        output += "Note that scan will probably fail - see CRITICAL recommendations above\n\n"

    output += "    DETECT COMMAND:\n"
    output += re.sub(r"^", "    ", global_values.cli_msgs_dict['detect'], flags=re.MULTILINE)
    output += "\n    MINIMUM REQUIRED OPTIONS:\n"
    output += re.sub(r"^", "    ", global_values.cli_msgs_dict['reqd'], flags=re.MULTILINE)

    # if len(bdignore_list) > 0:
    # 	if report:
    # 		print("        (Note that '.bdignore' exclude file is recommended - see the report file '{}' or use '-b' option\n" + \
    # 		"        to create '.bdignore' files in sub-folders)\n".format(report))
    # 	else:
    # 		print("        (Note that '.bdignore' exclude file is recommended - create a report file using '-r repfile' to\n" + \
    # 		"        see recommended folders to exclude or use '-b' option to create '.bdignore' files in sub-folders)\n")

    if not critical_only:
        output += '\n'
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

    print(output)

    if reportfile is not None:
        output = re.sub(r"^", "    ", output, flags=re.MULTILINE)
        with open(reportfile, "a") as repfile:
            repfile.write(output)


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
