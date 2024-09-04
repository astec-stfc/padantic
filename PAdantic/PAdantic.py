import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
from copy import copy
import glob

from yaml.constructor import Constructor

def add_bool(self, node):
    return self.construct_scalar(node)

Constructor.add_constructor(u'tag:yaml.org,2002:bool', add_bool)

from typing import get_origin, Any, Dict
from pydantic import BaseModel, field_validator
from .models.elementList import MachineModel
from .Importers.YAML_Loader import read_YAML_File

class PAdantic(MachineModel):
    yaml_dir: str

    @field_validator('yaml_dir', mode='before')
    @classmethod
    def validate_yaml_dir(cls, v: str) -> str:
        if os.path.isdir(v):
            return v
        elif os.path.isdir(os.path.abspath(os.path.dirname(__file__) + '/' + v)):
            return os.path.abspath(os.path.dirname(__file__) + '/' + v)
        else:
            raise ValueError(f'Directory {v} does not exist')

    def model_post_init(self, __context):
        super().model_post_init(__context)
        YAML_files = glob.glob(os.path.abspath(self.yaml_dir+'/**/*.yaml'), recursive=True)
        yaml_elems = [read_YAML_File(y) for y in YAML_files]
        self.update({y.name: y for y in yaml_elems})
