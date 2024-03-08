from pydantic import Field, NonNegativeFloat, NonNegativeInt

from .baseModels import IgnoreExtra

class DiagnosticElement(IgnoreExtra): ...


class BPM_Diagnostic(DiagnosticElement):
    ''' BPM Diagnostic model. '''
    type: str = Field(alias='bpm_type')
    settle_time: NonNegativeFloat = Field(alias='bpm_set_max_wait_time', default=0.5)
    attenuation1_calibration: NonNegativeInt = Field(alias='att1cal')
    attenuation2_calibration: NonNegativeInt = Field(alias='att2cal')
    voltage1_calibration: NonNegativeFloat = Field(alias='v1cal')
    voltage2_calibration: NonNegativeFloat = Field(alias='v2cal')
    charge_calibration: NonNegativeFloat = Field(alias='qcal')
    mn: float
    xn: float
    yn: float

class Camera_Diagnostic(DiagnosticElement):
    ''' Camera Diagnostic model. '''
    type: str = Field(alias='CAM_TYPE')
