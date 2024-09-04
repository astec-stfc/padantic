import numpy as np
from munch import Munch
from collections import OrderedDict


def _rotation_matrix(theta):
    return np.array(
        [
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-1 * np.sin(theta), 0, np.cos(theta)],
        ]
    )


def read_yaml(fname):
    """read the contents of a YAML file into a munch
    (a dictionary-type object supporting attribute-style access)
    """
    contents = Munch()
    with open(fname) as file:
        contents = contents.fromYAML(file)
    return contents


def merge_two_dicts(y, x):
    """Combine to dictionaries: first dictionary overwrites keys in the second dictionary"""
    if not isinstance(x, (dict, OrderedDict)) and not isinstance(
        y, (dict, OrderedDict)
    ):
        return OrderedDict()
    elif not isinstance(x, (dict, OrderedDict)):
        return y
    elif not isinstance(y, (dict, OrderedDict)):
        return x
    else:
        z = x.copy()  # start with x's keys and values
        z.update(y)  # modifies z with y's keys and values & returns None
        return z
