import sys
import yaml
from pysdds import read as sddsread

sys.path.append("..")
from PAdantic.PAdantic import PAdantic  # noqa E402

machine = PAdantic(
    layout_file="Machines/CLARA/layouts.yaml",
    section_file="Machines/CLARA/sections.yaml",
    yaml_dir="Machines/CLARA/YAML/",
)

machine.default_layout = "CLARA"

simframe_examples = "../../SimFrame_Examples/FEBE/StandardSetups/Setups/Setup_1_250pC"

with open(
    f"{simframe_examples}/lattice.yaml",
    "r",
) as stream:
    try:
        lattice = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

sdds_twiss = {}
sdds_twiss_file = sddsread(f"{simframe_examples}/FEBE.twi")
for idx, name in enumerate(sdds_twiss_file.col("ElementName").data[0]):
    sdds_twiss[name] = 0.511 * sdds_twiss_file.col("pCentral0").data[0][idx]

current_dictionary = {}
for name, elem in lattice["elements"].items():
    if (
        elem["type"] == "quadrupole"
        and "-FEA-" not in name
        and "-FEH-" not in name
        and "-FED-" not in name
    ):
        linsat = machine.get_element(name).magnetic.linear_saturation_coefficients
        momentum = sdds_twiss[name]
        k1 = elem["k1l"] / elem["length"]
        print(name, k1, momentum, linsat.KToCurrent(k1, momentum))
        current_dictionary[name] = float(linsat.KToCurrent(k1, momentum))

with open("test_currents.yaml", "w") as file:
    yaml.dump(current_dictionary, file)
