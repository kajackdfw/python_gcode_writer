class NCPattern:

    def __init__(self, machine_setup):
        self.summary = 'NCPattern Class initialized.\n'
        self.status = 'initialized'

    def load(self, json_pattern):
        return False

    def get_summary(self):
        return self.summary

    def print_summary(self):
        print(self.summary)
        return True

    def generate_nc_code(self):
        status = 'no_data'
        return status

    def save_nc_data(self, file_path_and_name):
        status = 'nothing_to_save'
        return status