import builtins
from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
    model_serializer,
    ConfigDict,
)
from typing import Dict, Type


class ControlVariable(BaseModel):
    identifier: str
    """Unique identifier for the control variable."""
    dtype: type
    """Data type of the control variable (e.g., int, float, str)."""
    protocol: str
    """Protocol or method used to interact with the control variable."""
    units: str = "Arb. Units"
    """Units of measurement for the control variable."""
    description: str = "Default Description"
    """Description of the control variable."""
    read_only: bool = True
    """Indicates if the variable is read-only."""
    model_config = ConfigDict(
        arbitrary_types_allowed=False,
        extra="allow",
        frozen=True,
    )

    def __init__(self, **data):
        super().__init__(**data)

    @field_validator("dtype", mode="before")
    def validate_dtype(cls, v) -> Type:
        """Convert from string to type if necessary."""
        if isinstance(v, str):
            try:
                return getattr(builtins, v)
            except AttributeError:
                raise ValueError(f"Unknown dtype string: {v}")
        if isinstance(v, type):
            return v
        raise TypeError(f"dtype must be a type or string, got {type(v)}")

    @model_serializer
    def serialize(self):
        data = self.__dict__.copy()
        if isinstance(self.dtype, type):
            data["dtype"] = self.dtype.__name__
        elif isinstance(self.dtype, str):
            data["dtype"] = self.dtype
        return data


class ControlsInformation(BaseModel):
    variables: Dict[str, ControlVariable]
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
        frozen=True,
    )

    @field_validator("variables", mode="before")
    def validate_variables(cls, v) -> Dict[str, ControlVariable]:
        """Ensure all values are ControlVariable instances."""
        if isinstance(v, dict):
            validated_dict = {}
            for key, value in v.items():
                if isinstance(value, ControlVariable):
                    validated_dict[key] = value
                elif isinstance(value, dict):
                    try:
                        validated_dict[key] = ControlVariable(**value)
                    except ValidationError as e:
                        raise ValueError(
                            (
                                "Invalid ControlVariable definition for key "
                                + f"'{key}': "
                                + f"{e}"
                            )
                        ) from e
                else:
                    raise TypeError(
                        (
                            f"Value for key '{key}'"
                            + "must be a ControlVariable or dict, "
                            + f"got {type(value)}"
                        )
                    )
            return validated_dict
        raise TypeError(f"variables must be a dict, got {type(v)}")
