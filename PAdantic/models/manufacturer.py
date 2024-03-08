from .baseModels import IgnoreExtra

class ManufacturerElement(IgnoreExtra):
    ''' Manufacturer info model. '''
    manufacturer: str
    serial_number: str
    hardware_type: str
