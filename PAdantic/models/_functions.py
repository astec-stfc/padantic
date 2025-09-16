import numpy as np
from collections import OrderedDict
from pydantic import create_model, BaseModel
from yaml import safe_load


def _rotation_matrix(theta):
    return np.array(
        [
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-1 * np.sin(theta), 0, np.cos(theta)],
        ]
    )


def read_yaml(fname: str) -> BaseModel:
    with open(fname, "r") as f:
        data = safe_load(f)

    # Build fields: field_name: (type, default)
    fields = {key: (type(value), value) for key, value in data.items()}

    # Create and return the dynamic model class
    DynamicModel = create_model(
        "DynamicModel",
        __base__=BaseModel,
        __module__=__name__,
        # model_config=model_config,
        **fields,
    )
    return DynamicModel(**data)


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
