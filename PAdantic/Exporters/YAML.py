import yaml
from pydantic import BaseModel
import numpy as np


def export_as_yaml(filename: str, ele: BaseModel) -> None:
    with open(filename,"w") as yaml_file:
            yaml.default_flow_style=True
            yaml.dump(ele.yaml_dump(), yaml_file)
