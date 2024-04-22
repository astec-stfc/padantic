from pydantic import Field, NonNegativeFloat, NonNegativeInt, field_validator
from typing import List, Type
from .baseModels import IgnoreExtra, T, Aliases, DeviceList

class DiagnosticElement(IgnoreExtra): ...

class BPM_Diagnostic(DiagnosticElement):
    ''' BPM Diagnostic model. '''
    type: str = Field(alias='bpm_type', default='Stripline')
    settle_time: NonNegativeFloat = Field(alias='bpm_set_max_wait_time', default=0.5)
    attenuation1_calibration: NonNegativeInt | None = Field(alias='att1cal', default=12)
    attenuation2_calibration: NonNegativeInt | None = Field(alias='att2cal', default=12)
    voltage1_calibration: NonNegativeFloat | None = Field(alias='v1cal', default=1)
    voltage2_calibration: NonNegativeFloat | None = Field(alias='v2cal', default=1)
    charge_calibration: NonNegativeFloat | None = Field(alias='qcal', default=70)
    mn: float | None = 15
    xn: float | None = 0
    yn: float | None = 0

class Camera_Pixel_Results_Indices(IgnoreExtra):
    x: int = Field(default=0, alias='X_POS')
    y: int = Field(default=1, alias='Y_POS')
    x_sigma: int = Field(default=2, alias='X_SIGMA_POS')
    y_sigma: int = Field(default=3, alias='Y_SIGMA_POS')
    covariance: int = Field(default=4, alias='COV_POS')

class Camera_Pixel_Results_Names(IgnoreExtra):
    x: str = Field(default='X', alias='X_NAME')
    y: str = Field(default='Y', alias='Y_NAME')
    x_sigma: str = Field(default='X_SIGMA', alias='X_SIGMA_NAME')
    y_sigma: str = Field(default='Y_SIGMA', alias='Y_SIGMA_NAME')
    covariance: str = Field(default='COV', alias='COV_NAME')

class Camera_Mask(IgnoreExtra):
    middle:  List[float|int] = [1280, 1080] # X_MASK_DEF, Y_MASK_DEF
    radius:  List[float|int] = [1240, 1040] # X_MASK_RAD_DEF, Y_MASK_RAD_DEF
    maximum: List[float|int] = [300, 300] # X_MASK_RAD_MAX, Y_MASK_RAD_MAX
    use_maximum_values: bool = Field(default=True, alias='USE_MASK_RAD_LIMITS')

    @classmethod
    def from_CATAP(cls: Type[T], fields: dict) -> T:
        cls._create_field(cls, fields, 'middle', ['X_MASK_DEF', 'Y_MASK_DEF'])
        cls._create_field(cls, fields, 'radius', ['X_MASK_RAD_DEF', 'Y_MASK_RAD_DEF'])
        cls._create_field(cls, fields, 'maximum', ['X_MASK_RAD_MAX', 'Y_MASK_RAD_MAX'])
        return super().from_CATAP(fields)

class Camera_Sensor(IgnoreExtra):
    x_pixels: int = Field(alias='BINARY_NUM_PIX_X', default=2160)
    y_pixels: int = Field(alias='BINARY_NUM_PIX_Y', default=2560)
    x_scale_factor: int = Field(alias='X_PIX_SCALE_FACTOR', default=2)
    y_scale_factor: int = Field(alias='Y_PIX_SCALE_FACTOR', default=2)
    beam_pixel_average: float = Field(alias='AVG_PIXEL_VALUE_FOR_BEAM', default=97.2)
    middle:  List[float|int] = [0,0] # X_CENTER_DEF, Y_CENTER_DEF
    pixels_to_mm: List[float] = [0.0134, 0.0134] # ARRAY_DATA_X_PIX_2_MM, ARRAY_DATA_Y_PIX_2_MM
    minimum: List[float|int] = [150, 150] # MIN_X_PIXEL_POS, MIN_Y_PIXEL_POS
    maximum: List[float|int] = [2400, 2000] # MAX_X_PIXEL_POS, MAX_Y_PIXEL_POS
    bit_depth: int = 16
    operating_middle:  List[float|int] = [1000,1000] # OPERATING_CENTER_X, OPERATING_CENTER_Y
    mechanical_middle:  List[float|int] = [1000,1000] # MECHANICAL_CENTER_X, MECHANICAL_CENTER_Y

    @classmethod
    def from_CATAP(cls: Type[T], fields: dict) -> T:
        cls._create_field(cls, fields, 'middle', ['X_CENTER_DEF', 'Y_CENTER_DEF'])
        cls._create_field(cls, fields, 'pixels_to_mm', ['ARRAY_DATA_X_PIX_2_MM', 'ARRAY_DATA_Y_PIX_2_MM'])
        cls._create_field(cls, fields, 'minimum', ['MIN_X_PIXEL_POS', 'MIN_Y_PIXEL_POS'])
        cls._create_field(cls, fields, 'maximum', ['MAX_X_PIXEL_POS', 'MAX_Y_PIXEL_POS'])
        cls._create_field(cls, fields, 'operating_middle', ['OPERATING_CENTER_X', 'OPERATING_CENTER_Y'])
        cls._create_field(cls, fields, 'mechanical_middle', ['MECHANICAL_CENTER_X', 'MECHANICAL_CENTER_Y'])
        return super().from_CATAP(fields)

class Camera_Diagnostic(DiagnosticElement):
    ''' Camera Diagnostic model. '''
    type: str = Field(alias='CAM_TYPE')
    pixel_results_indices: Camera_Pixel_Results_Indices# = Camera_Pixel_Results_Indices()
    pixel_results_names: Camera_Pixel_Results_Names# = Camera_Pixel_Results_Names()
    mask: Camera_Mask# = Camera_Mask()
    sensor: Camera_Sensor# = Camera_Sensor()
    epics_x_pixels: int = Field(alias='ARRAY_DATA_NUM_PIX_X', default=1080)
    epics_y_pixels: int = Field(alias='ARRAY_DATA_NUM_PIX_Y', default=1280)
    rotation: int|float = 0
    flipped_horizontally: bool = Field(alias='IMAGE_FLIP_LR', default=True)
    flipped_vertically: bool = Field(alias='IMAGE_FLIP_UD', default=False)

    @classmethod
    def from_CATAP(cls: Type[T], fields: dict) -> T:
        cls._create_field_class(cls, fields, 'pixel_results_indices', Camera_Pixel_Results_Indices)
        cls._create_field_class(cls, fields, 'pixel_results_names', Camera_Pixel_Results_Names)
        cls._create_field_class(cls, fields, 'mask', Camera_Mask)
        cls._create_field_class(cls, fields, 'sensor', Camera_Sensor)
        return super().from_CATAP(fields)

class Screen_Diagnostic(DiagnosticElement):
    ''' Camera Diagnostic model. '''
    type: str = Field(alias='screen_type', default='CLARA_HV_MOVER')
    has_camera: bool = True
    camera_name: str = ''
    devices: str|list|DeviceList = DeviceList()

    @field_validator('devices', mode='before')
    @classmethod
    def validate_devices(cls, v: str|List) -> DeviceList:
        if isinstance(v, str):
            return DeviceList(devices=list(map(str.strip, v.split(','))))
        elif isinstance(v, (list, tuple)):
            return DeviceList(devices=list(v))
        elif isinstance(v, (DeviceList)):
            return v
        else:
            raise ValueError('devices should be a string or a list of strings')

class Charge_Diagnostic(DiagnosticElement):
    type: str = Field(alias='charge_type')
