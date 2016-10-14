import os


def read_file():
    file_path = os.path.dirname(os.path.abspath(__file__))
    with open(file_path + "/info_color.txt", "r") as f:
        content = f.readlines()

    return content


def write_file(error, info, warn, debug):
    file_path = os.path.dirname(os.path.abspath(__file__))
    f = open(file_path + "/info_color.txt", "r+")
    f.truncate()
    f.write('ERROR ' + error + '\n')
    f.write('INFO ' + info + '\n')
    f.write('WARN ' + warn + '\n')
    f.write('DEBUG ' + debug + '\n')
    f.close()
