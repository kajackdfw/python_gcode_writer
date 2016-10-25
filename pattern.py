import sys, getopt


class NCPattern:

    def __init__(self, argv):

        self.nc_file = 'nc/test.nc'
        self.pattern_file = ''
        self.machine = ''
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
                self.machine = arg
            elif opt in ("-n", "--nc_file"):
                self.nc_file = arg
            elif opt in ("-p", "--pattern_file"):
                self.pattern_file = arg

        if self.machine == '':
            print('Error: You must specify a cnc machine!')
            sys.exit(2)

        self.summary = '  NCPattern Class initialized for ' + self.machine + '\n'
        self.status = 'initialized'

    def load(self):
        if self.pattern_file == '':
            print('Error: You must specify a json pattern file!')
            sys.exit(2)
        self.summary += '  Load ' + self.pattern_file + ' \n'
        return False

    def get_summary(self):
        return self.summary

    def print_summary(self):
        print(self.summary)
        return True

    def generate_nc_code(self):
        status = 'no_data'
        return status

    def save_nc_data(self):
        self.summary += '  Save NC data to ' + self.nc_file + ' \n'
        status = 'nothing_to_save'
        return status
