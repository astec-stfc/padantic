from pydantic import BaseModel, model_serializer, ConfigDict, Field, field_validator, ValidationInfo
from typing import TypeVar, Dict, Any

from .baseModels import IgnoreExtra

class ManufacturerElement(IgnoreExtra):
    ''' Manufacturer info model. '''
    manufacturer: str
    serial_number: str
    hardware_type: str
