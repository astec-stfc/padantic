import numpy as np
from munch import Munch

def _rotation_matrix(theta):
    return np.array([[np.cos(theta), 0, np.sin(theta)], [0, 1, 0], [-1*np.sin(theta), 0, np.cos(theta)]])

def read_yaml(fname):
    '''read the contents of a YAML file into a munch
       (a dictionary-type object supporting attribute-style access)
    '''
    contents = Munch()
    with open(fname) as file:
        contents = contents.fromYAML(file)
    return contents
