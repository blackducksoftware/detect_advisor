import global_values

def process_pmdata():
    pm_allfiles = {}
    pm_allexts = {}

    for pm in global_values.pm_dict.keys():
        if len(global_values.pm_dict[pm]['files']) > 0:
            for ffile in global_values.pm_dict[pm]['files']:
                if ffile not in pm_allfiles.keys():
                    pm_allfiles[ffile] = [pm]
                else:
                    pm_allfiles[ffile].append(pm)

        if len(global_values.pm_dict[pm]['exts']) > 0:
            for fext in global_values.pm_dict[pm]['exts']:
                if fext not in pm_allexts.keys():
                    pm_allexts[fext] = [pm]
                else:
                    pm_allexts[fext].append(pm)

    return