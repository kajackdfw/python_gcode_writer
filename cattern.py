import sys, getopt, json


class Cattern:

    def __init__(self, argv):

        self.nc_file = 'nc/test.nc'
        self.pattern_file = ''
        self.machine_file = ''

        self.groups = []
        self.group_count = 0

        self.pattern_perimeter = {}
        self.pattern_dic = {}

        self.nc_data = ''
        self.entity_list = []


        try:
            opts, args = getopt.getopt(argv, "", ["machine=", "pattern_file=", "nc_file="])
        except getopt.GetoptError:
            print('python nc.py -m <cnc_machine> -p <json_pattern_file>')
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print('test.py --machine=wazer.json --pattern_file=bird_house.json --nc_file=bird_house.nc')
                sys.exit()
            elif opt in ("-m", "--machine"):
                self.machine_file = arg
            elif opt in ("-n", "--nc_file"):
                self.nc_file = arg
            elif opt in ("-p", "--pattern_file"):
                self.pattern_file = arg

        if self.machine_file == '':
            print('Error: You must specify a cnc machine!')
            sys.exit(2)

        # Load the machine file if present
        try:
            machine_fh = open("machines/" + self.machine_file + ".json", "r")
            json_array_string = str(machine_fh.read())
            self.machine = json.loads(json_array_string)
            self.summary = '  Machine config for ' + self.machine['description'] + ' loaded\n'
        except IOError:
            print("  Error : No machine file found for " + self.machine_file + '\n')
            sys.exit()

        self.summary += '  NCPattern Class initialized \n'
        self.status = 'initialized'

    def load(self):
        if self.pattern_file == '':
            print('Error: You must specify a json pattern file!')
            sys.exit(2)

        # Load the pattern file if present
        try:
            pattern_fh = open(self.pattern_file, "r")
            json_array_string = str(pattern_fh.read())
            self.pattern_dic = json.loads(json_array_string)
            for cut_number, cut_values in self.pattern_dic['groups'].items():
                self.groups.insert(int(cut_number), cut_values)
        except IOError:
            print("  Error : No pattern file found for " + self.pattern_file + '\n')
            sys.exit()
        # set some statistics for use with code logic
        self.group_count_setter()
        return True

    def validator(self):
        group_num = 0
        for group in self.groups:
            group_errors = 0
            self.summary += '    Validate group ' + str(group_num) + ' \n'
            if 'shape' not in group:
                self.summary += '      Error: group ' + str(group_num) + ' is missing shape attribute. \n'
                group_errors += 1
            else:
                self.summary += '      Shape = ' + group['shape'] + ' \n'

            if 'x' not in group:
                self.summary += '      Error: group ' + str(group_num) + ' is missing x attribute. \n'
            if 'y' not in group:
                self.summary += '      Error: group ' + str(group_num) + ' is missing y attribute. \n'
            group_num += 1
        return True

    # Group methods *******************************************************************************

    def group_count_setter(self):
        self.group_count = 0
        for x in self.groups:
            self.group_count += 1
        self.summary += '  ' + str(self.group_count) + ' groups found.\n'

    # NC Code methods *****************************************************************************

    def nc_code_generate(self):
        status = 'no_data'
        return status

    def nc_code_save(self):
        if len(self.nc_data) > 0:
            nc_fh = open(self.nc_file, "w")
            nc_fh.write(self.nc_data)
            self.summary += '  NC data saved in ' + self.nc_file + ' \n'
            nc_fh.close()
            return True
        else:
            self.summary += '  No NC data to save! \n'
        return False

    def nc_code_get(self):
        return self.nc_data

    # Summary methods *****************************************************************************

    def summary_get(self):
        return self.summary

    def summary_print(self):
        print(self.summary)
        return True

