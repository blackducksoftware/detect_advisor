import re
from collections import OrderedDict


class Property(object):
    @staticmethod
    def parse(property_str: str, position=None):
        property_str = property_str.strip()
        is_commented = False
        if property_str.startswith('#'):
            property_str = re.sub(r"#\s*", "", property_str)
            is_commented = True
        if (result := re.match(r"--([a-z0-9.]+)\s*=\s*(.+)", property_str)) is None:
            result = re.match(r"([a-z0-9.]+):\s*(.+)", property_str)

        if result is not None:
            return Property(result.groups()[0], result.groups()[1], is_commented=is_commented, position=position)
        else:
            return None

    def __init__(self, property_name, property_value,
                 is_commented=False, position=None):
        self.position = position
        self.property_name = property_name
        self.value = property_value
        self.property_key = "{}:{}".format(self.position, self.property_name)
        self.is_commented = is_commented

    def __str__(self):
        return ("# " if self.is_commented else "") + str(self.property_name) + ": " + str(self.value)

    def __hash__(self):
        return hash(str(self.property_name) + ": " + str(self.value))

    def __repr__(self):
        return "({}): \"{}\"".format(self.position, self.__str__())


class PropertyGroup(object):
    @staticmethod
    def look_for_group_def_title(line_str: str):
        if result := re.match(r'#\s+([A-Z0-9\- ]*):$', line_str):
            return result.group(1)
        return None

    @property
    def num_defined(self):
        return len(self.properties_dict)

    def __init__(self, key, title, defaults=None):
        self.key = key
        self.title = title
        self.line_no_offset = None
        self.defaults = defaults
        self.line_objects = ["#    {}:".format(self.title), "#    "]
        self.properties_dict = OrderedDict()
        if defaults is not None:
            for l_o in defaults.split('\n'):
                if (result := Property.parse(l_o)) is not None:
                    result.is_commented=True
                    self.add_property(result)
                else:
                    self.add_comment_line(l_o)

    def add_property(self, prop: Property, should_update=False):
        if prop.property_name not in self.properties_dict:
            self.properties_dict[prop.property_name] = prop
            self.line_objects.append(prop)
        elif should_update:
            i = self.line_objects.index(self.properties_dict[prop.property_name])
            self.line_objects.pop(i)
            self.line_objects.insert(i, prop)
            self.properties_dict[prop.property_name] = prop

    def add_comment_line(self, comment: str):
        if not comment.startswith("#"):
            comment = "#" + comment
        comment = re.sub(r'#\s*', "#    ", comment)
        comment.replace("\n", "")
        if comment not in self.line_objects and self.title not in comment:
            self.line_objects.append(comment)

    def get_line(self, num, strip_comment=True):
        line = self.line_objects[num+1]
        if strip_comment and '#' in line:
            line = re.sub(r"^\s*#\s*", "", line)
        return line

    def clear(self, with_defaults=True):
        self.line_objects = ["#    {}:".format(self.title), "#    "]
        self.properties_dict = OrderedDict()
        if self.defaults is not None:
            for l_o in self.defaults.split('\n'):
                if (result := Property.parse(l_o)) is not None:
                    result.is_commented=True
                    self.add_property(result)
                else:
                    self.add_comment_line(l_o)

    def __len__(self):
        return len(self.line_objects)

    def __str__(self):
        out_str = ""
        for l_o in self.line_objects:
            out_str += "{}\n".format(str(l_o))

        return out_str


class Configuration(object):

    def __init__(self, filename, config_groups):
        self.filename = filename
        self.file = None
        self.property_groups = OrderedDict()
        self.property_groups_title = OrderedDict()
        for pg in config_groups:
            self.property_groups[pg.key] = pg
            self.property_groups_title[pg.title] = self.property_groups[pg.key]
        try:
            self.file = open(self.filename, 'r')
            current_key = None

            for (i, line) in enumerate(self.file.readlines()):
                line = line[0:len(line)-1]
                potential_prop_grp = PropertyGroup.look_for_group_def_title(line)
                # See if we've switched property groups (by title)
                if potential_prop_grp in self.property_groups_title:
                    current_key = self.property_groups_title[potential_prop_grp].key
                    self.property_groups[current_key].line_no_offset = i # set the offset in the original config to where we are now

                if current_key is not None:
                    if (result := Property.parse(line)) is not None:
                        # Add legit property
                        self.property_groups[current_key].add_property(result, should_update=True)
                    else:
                        # add a comment line
                        self.property_groups[current_key].add_comment_line(line)

        except FileNotFoundError:
            self.file = open(self.filename, 'w')

    def str_add(self, property_class, property_str, is_commented=False, should_update=False):
        property = Property.parse(property_str)
        if property is None:
            self.property_groups[property_class].add_comment_line(property_str)
        else:
            property.is_commented = is_commented
            self.property_groups[property_class].add_property(property, should_update=should_update)

    def add(self, property_class, property: Property):
        property.position = len(self.property_groups[property_class])
        self.property_groups[property_class].add_property(property)

    def has_prop(self, property_name):
        for v in self.property_groups.values():
            for p in v.properties_dict.values():
                if p.property_name is not None and p.property_name == property_name:
                    return True
        return False

    def get_prop(self, property_name):
        for v in self.property_groups.values():
            for p in v.properties_dict.values():
                if p.property_name is not None and p.property_name == property_name:
                    return p
        return None

    def get_props_like(self, property_name_expr):
        prop_list = []
        for v in self.property_groups.values():
            for p in v.properties_dict.values():
                if p.property_name is not None and property_name_expr in p.property_name:
                    prop_list.append(p)
        return prop_list

    def uncomment_property(self, property_name, assert_value=None):
        if result := self.get_prop(property_name) is not None:
            if assert_value is not None and result.value != assert_value:
                return False
            else:
                result.is_commented=False
                return True
        return False

    def uncomment_like(self, property_name_expr):
        result = self.get_props_like(property_name_expr)
        for p in result:
            p.is_commented=False
        return len(result)

    def clear_group(self, group_key):
        if group_key in self.property_groups:
            self.property_groups[group_key].clear()

    def get_lines(self):
        lines = []
        for pg in self.property_groups.values():
            for l_o in pg.line_objects:
                lines.append("{}\n".format(l_o))
        return lines

    def __contains__(self, item):
        return self.has_prop(item)

    def __getitem__(self, item):
        if item in self.property_groups:
            return self.property_groups[item]
        return self.get_prop(item)

    def __repr__(self):
        outstr = ""
        for key, i in self.property_groups.items():
            outstr += "({}) -> {}\n".format(key, str(i))
        return outstr

    def __str__(self):
        outstr = ""
        for _, pg in self.property_groups.items():
            #if pg.num_defined > 0:
            outstr += "{}\n".format(str(pg))
        return outstr


if __name__ == "__main__":
    c = Configuration('application-project_good.yml', [PropertyGroup('detect', 'DETECT COMMAND TO RUN'),
                                                  PropertyGroup('reqd', 'MINIMUM REQUIRED OPTIONS'),
                                                  PropertyGroup('scan', 'OPTIONS TO IMPROVE SCAN COVERAGE'),
                                                  PropertyGroup('size', 'OPTIONS TO REDUCE SIGNATURE SCAN SIZE'),
                                                  PropertyGroup('dep', 'OPTIONS TO CONFIGURE DEPENDENCY SCAN'),
                                                  PropertyGroup('lic', 'OPTIONS TO IMPROVE LICENSE COMPLIANCE ANALYSIS'),
                                                  PropertyGroup('proj', 'PROJECT OPTIONS'),
                                                  PropertyGroup('docker', 'DOCKER SCANNING')])
    print(c)