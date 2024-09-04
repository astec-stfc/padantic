from pydantic import Field, field_validator
from typing import List, Type

from .baseModels import IgnoreExtra, T


class LightingElement(IgnoreExtra):
    """Lighting info model."""
