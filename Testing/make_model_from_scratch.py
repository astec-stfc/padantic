import sys

sys.path.append("..")

from pprint import pprint  # noqa E402
from PAdantic.models.magnetic import Quadrupole_Magnet  # noqa E402
from PAdantic.models.physical import PhysicalElement, Position  # noqa E402
from PAdantic.models.element import Quadrupole  # noqa E402
from PAdantic.models.elementList import MachineModel  # noqa E402
from PAdantic.PAdantic import PAdantic  # noqa E402

# We are able to specify layouts even without section definitions
machine = MachineModel(
    layout={
        "layouts": {
            "line1": {
                "FODO": ["QUAD1"],
                "NODO": ["QUAD2"],
            },
        },
    },
)

# Make an element from scratch and add it to the machine
q1 = Quadrupole(
    name="QUAD1",
    machine_area="FODO",
    magnetic=Quadrupole_Magnet(
        length=0.1,
        k1l=1.0,
    ),
    physical=PhysicalElement(
        middle=Position(
            x=0,
            y=0,
            z=0.1,
        ),
        length=0.1,
    ),
)
machine.append({q1.name: q1})
print(f"Machine sections after QUAD-01 addition: {machine.sections}")

# Make another element from scratch and add it to the machine
q2 = Quadrupole(
    name="QUAD2",
    machine_area="NODO",
    magnetic=Quadrupole_Magnet(
        length=0.1,
        k1l=1.0,
    ),
    physical=PhysicalElement(
        middle=Position(
            x=0,
            y=0,
            z=0.5,
        ),
        length=0.1,
    ),
)
machine.append({q2.name: q2})

print("============= Machine Model Creation =============")
# Check the sections and layouts have been built correctly
print(f"Machine sections after QUAD-02 addition: {machine.sections}")
print(f"Machine lattices after QUAD-02 addition: {machine.lattices}")

sections = {
    "sections": {
        "FODO": ["QUAD1"],
        "NODO": ["QUAD2"],
    }
}
layouts = {
    "layouts": {
        "line1": ["FODO", "NODO"],
    }
}

print("============= PADantic Creation =============")
pa_machine = PAdantic(element_list=[q1, q2], layout=layouts, section=sections)
pprint(f"PADantic creation result [elements]: {pa_machine.elements}")
print(f"PADantic creation result [sections]: {pa_machine.sections}")
print(f"PADantic creation result [lattices]: {pa_machine.lattices}")
pa_machine.get_magnets()
