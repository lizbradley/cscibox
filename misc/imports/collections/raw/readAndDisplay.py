import csv

from pprint import pprint

def read_and_display(name):
    input_file = file(name + ".csv", "U")
    r          = csv.DictReader(input_file)
    for row in r:
        pprint(row)

if __name__ == '__main__':
    read_and_display('constants')
    read_and_display('paleomag')
    read_and_display('polepositions')
    read_and_display('fairbanks')
    read_and_display('elements')
    read_and_display('sunspots')
