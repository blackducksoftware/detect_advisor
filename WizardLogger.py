from tabulate import tabulate


class WizardLogger(object):
    def __init__(self):
        self._log_dict = dict()

    def log(self, topic, causes, outcome, description):
        if topic not in self._log_dict:
            self._log_dict[topic] = set()
        self._log_dict[topic].add(((causes, ) if type(causes) == str else tuple(causes), outcome, description))

    def make_table(self, sensitivity_value=None):
        data_rows = []
        data_rows_no_op = []
        for topic, cod_list in self._log_dict.items():
            for idx, (cause, outcome, description) in  enumerate(cod_list):
                if outcome == "NO-OP":
                    if idx == 0:
                        data_rows_no_op.append([topic, ', '.join(cause), outcome, description])
                    else:
                        data_rows_no_op.append(["", ', '.join(cause), outcome, description])
                else:
                    if idx == 0:
                        data_rows.append([topic, ', '.join(cause), outcome, description])
                    else:
                        data_rows.append(["", ', '.join(cause), outcome, description])

        table_pos = tabulate(data_rows, headers=("Actionable", "Cause/Condition", "Outcome", "Description"),
                         tablefmt='pretty')
        table_neg = tabulate(data_rows_no_op, headers=("Actionable", "Cause/Condition", "Outcome", "Description"),
                             tablefmt='pretty')

        table_width = max(table_pos.index('\n'), table_neg.index('\n'))
        title = " Sensitivity{} Manifest ".format("({})".format(sensitivity_value) if sensitivity_value is not None else "")
        size = (table_width - len(title)) // 2
        header_str = '-' * size + title + '-' * size
        footer_str = '-' * len(header_str) + "\n"
        return "{}\n{}\n{}{}\n{}".format(header_str, table_pos, footer_str, table_neg, footer_str)


if __name__ == "__main__":
    wl = WizardLogger()
    wl.log("A", ["b", "c"], "af", "asf")

    print(wl.make_table())