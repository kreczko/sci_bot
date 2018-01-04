import json
from glob import glob
from os.path import dirname, join


def tidy_file(file_name):
    with open(file_name) as f:
        content = json.load(f)
    with open(file_name, 'w') as f:
        json.dump(content, f, indent=4)

path = join(dirname(__file__), '*.json')
files = glob(path)
for f in files:
    print('Tidying up file "{}"'.format(f))
    tidy_file(f)
