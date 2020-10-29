import re
from collections import namedtuple
from WizardLogger import WizardLogger


def test_sensitivity(op_val_pair: tuple, sensitivity):
    global args
    cmp_op, val = op_val_pair
    if cmp_op == '>':
        return sensitivity > val
    elif cmp_op == '<':
        return sensitivity < val
    elif cmp_op == '>=':
        return sensitivity >= val
    elif cmp_op == '<=':
        return sensitivity <= val
    elif cmp_op == "=" or cmp_op == "==":
        return sensitivity == val
    elif cmp_op == "!=":
        return sensitivity != val
    else:
        raise ValueError("{} is not a valid value for sensitivity comparison".format(op_val_pair))


def invert_op(op_val_pair: tuple):
    op, val = op_val_pair
    if op == "!=":
        return "==", val
    elif op == "==" or op == "=":
        return "!=", val
    elif op == "<=":
        return ">", val
    elif op == ">=":
        return "<", val
    elif op == ">":
        return "<=", val
    elif op == "<":
        return ">=", val


def format_op_val_pair(op_val_pair: tuple):
    return "sensitivity {} {}".format()


def format_value(val: str):

    if val.lower() == "true":
        return True
    elif val.lower() == "false":
        return False
    elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return str(val[1:len(val)-1])
    elif val.isdecimal():
        return int(val)
    else:
        try:
            return round(float(val), 2)
        except ValueError:
            return val



def parse_cause_actions(cause_action_dict: dict, vars_dict: dict):
    output = {}

    for k, v in cause_action_dict.items():
        split_str = re.split("(?:\\s+(and|or)\\s+)", k)
        intermediate_results = []
        causes_for = []
        causes_against = []
        did_fail = False
        for component in split_str:
            findallret = re.findall("(^[a-z\\_]+) ([<>=]+) ([0-9a-zA-Z\"\'.]+)$", component)
            if len(findallret) > 0:
                # this is an operator
                var, op, val = findallret[0]
                if var not in vars_dict.keys():
                    raise ValueError("Variable {} not found in vars_dict ({})".format(var, vars_dict.keys()))
                else:

                    test_result = test_sensitivity((op, format_value(val)), vars_dict[var])
                    the_result = test_result
                    if the_result:
                        causes_for.append("{} {} {}".format(var, op, val))
                    else:
                        did_fail = True
                        inv = invert_op((op, val))
                        causes_against.append("{} {} {}".format(var, inv[0], inv[1]))

                    if len(intermediate_results) > 0:
                        intermediate_results.append(intermediate_results.pop()(test_result))
                    else:
                        intermediate_results.append(test_result)
                    if did_fail:
                        break
            else:
                if component == "and":
                    intermediate_results.append(lambda x: intermediate_results.pop() and x)
                elif component == "or":
                    intermediate_results.append(lambda x: intermediate_results.pop() or x)
        if did_fail:
            output[v] = (intermediate_results[0], causes_against)
        else:
            output[v] = (intermediate_results[0], causes_for)

    return output


def parse_and_replace_action_vars(action, vars_dict: dict):
    if type(action) == str:
        action_vars = re.findall("\\${([a-zA-Z-0-9_]+)}", action)
        if action_vars is not None:
            for var_name in action_vars:
                result = vars_dict[var_name]
                if callable(result):
                    return result
                action = action.replace("${" + "{}".format(var_name) + "}", str(format_value(str(result))))
    return action


class Actionable(object):
    wl = WizardLogger()
    Output = namedtuple("Output", ["outcome", "causes", "description"])

    def __init__(self, title: str, cause_action_dict, default_description=None):
        self.title = title
        self.cause_action_dict = cause_action_dict
        self.default = default_description

    def test(self, **vars_dict):
        output = parse_cause_actions(self.cause_action_dict, vars_dict)
        true_count = 0
        value_action = None
        failed_test_causes = set()
        for k, v in output.items():
            if v[0]:
                outcome = parse_and_replace_action_vars(k[0], vars_dict)
                desc = parse_and_replace_action_vars(k[1], vars_dict)
                if callable(outcome):
                    result = outcome()
                    if type(result) == list:
                        result = "\n".join(result)
                    desc = desc.replace("${OUT}", str(result))
                value_action = Actionable.Output(outcome=outcome, causes=v[1], description=desc)
                true_count += 1
            else:
                failed_test_causes = failed_test_causes.union(set(v[1]))
        if true_count == 0:
            value_action = Actionable.Output("NO-OP", failed_test_causes, parse_and_replace_action_vars(self.default, vars_dict))
        Actionable.wl.log(topic=self.title, causes=value_action.causes, outcome=value_action.outcome, description=value_action.description)
        return value_action

    def getTable(self, sensitivity_value):
        return Actionable.wl.make_table(sensitivity_value)

    def __str__(self):
        return "[{}]: ({} OR {})".format(self.title, self.cause_action_dict, self.default)


if __name__ == "__main__":
    a = Actionable("sig_scan", {"sensitivity < 2 or json_splitter = true": ("--detect.tools.excluded=SIGNATURE_SCAN", "thing"),
                                  "sensitivity > 5": ("--detect.tools.excluded=WOW", "do iother thing")}, "Default")
    print(a.test(sensitivity=5, json_splitter=False))