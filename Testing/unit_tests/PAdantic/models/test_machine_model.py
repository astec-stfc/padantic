from PAdantic.models.baseModels import Aliases
from PAdantic.models.elementList import (
    ElementList,
    MachineLayout,
    MachineModel,
    _baseElement,
)
from PAdantic.models.element import Element
import unittest


class TestMachineModel(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.elements = {
            "elem1": {
                "name": "MAG-01",
                "hardware_class": "Magnet",
                "hardware_type": "Quadrupole",
                "machine_area": "AREA-01",
                "alias": ["elem1"],
            },
            "elem2": {
                "name": "BPM-01",
                "hardware_class": "Monitor",
                "hardware_type": "BPM",
                "machine_area": "AREA-01",
                "alias": ["elem2", "bpm1"],
            },
            "elem3": {
                "name": "CAV-01",
                "hardware_class": "RF",
                "hardware_type": "Cavity",
                "machine_area": "AREA-02",
                "alias": ["elem3", "cav1"],
            },
        }
        return super().setUp()

    def test_empty_machine_model(self):
        with self.assertWarns(Warning):
            mm = MachineModel()
        self.assertEqual(mm.elements, {})
        self.assertEqual(mm.sections, {})
        self.assertEqual(mm.lattices, {})

    def test_add_element_after_init(self):
        with self.assertWarns(Warning):
            mm = MachineModel()
        self.assertEqual(mm.elements, {})
        self.assertEqual(mm.sections, {})
        self.assertEqual(mm.lattices, {})
        mm.append({name: Element(**info) for name, info in self.elements.items()})
        self.assertListEqual(
            sorted(list(mm.sections.keys())),
            ["AREA-01", "AREA-02"],
        )
        for name, info in self.elements.items():
            with self.subTest(name=name):
                self.assertIn(name, mm.elements)
                self.assertIsInstance(mm.elements[name], _baseElement)
                self.assertEqual(
                    mm.elements[name].name,
                    info["name"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_class,
                    info["hardware_class"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_type,
                    info["hardware_type"],
                )
                self.assertEqual(
                    mm.elements[name].machine_area,
                    info["machine_area"],
                )
                self.assertEqual(
                    mm.elements[name].alias,
                    Aliases(aliases=info["alias"]),
                )
        for name, section in mm.sections.items():
            with self.subTest(name=name):
                self.assertIn(name, ["AREA-01", "AREA-02"])
                self.assertIsInstance(section.elements, ElementList)
                if name == "AREA-01":
                    self.assertListEqual(
                        section.names,
                        [
                            "MAG-01",
                            "BPM-01",
                        ],
                    )
                elif name == "AREA-02":
                    self.assertListEqual(section.names, ["CAV-01"])

    def test_machine_model_with_dict_elements_only(self):
        with self.assertWarns(Warning):
            mm = MachineModel(
                elements=self.elements,
            )
        self.assertListEqual(
            sorted(list(mm.sections.keys())),
            ["AREA-01", "AREA-02"],
        )
        for name, info in self.elements.items():
            with self.subTest(name=name):
                self.assertIn(name, mm.elements)
                self.assertIsInstance(mm.elements[name], _baseElement)
                self.assertEqual(
                    mm.elements[name].name,
                    info["name"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_class,
                    info["hardware_class"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_type,
                    info["hardware_type"],
                )
                self.assertEqual(
                    mm.elements[name].machine_area,
                    info["machine_area"],
                )
                self.assertEqual(
                    mm.elements[name].alias,
                    Aliases(aliases=info["alias"]),
                )
        for name, section in mm.sections.items():
            with self.subTest(name=name):
                self.assertIn(name, ["AREA-01", "AREA-02"])
                self.assertIsInstance(section.elements, ElementList)
                if name == "AREA-01":
                    self.assertListEqual(
                        section.names,
                        [
                            "MAG-01",
                            "BPM-01",
                        ],
                    )
                elif name == "AREA-02":
                    self.assertListEqual(section.names, ["CAV-01"])

    def test_machine_model_with_elements_only(self):
        with self.assertWarns(Warning):
            mm = MachineModel(
                elements={
                    name: Element(**info) for name, info in self.elements.items()
                },
            )
        self.assertListEqual(
            sorted(list(mm.sections.keys())),
            ["AREA-01", "AREA-02"],
        )
        for name, info in self.elements.items():
            with self.subTest(name=name):
                self.assertIn(name, mm.elements)
                self.assertIsInstance(mm.elements[name], _baseElement)
                self.assertEqual(
                    mm.elements[name].name,
                    info["name"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_class,
                    info["hardware_class"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_type,
                    info["hardware_type"],
                )
                self.assertEqual(
                    mm.elements[name].machine_area,
                    info["machine_area"],
                )
                self.assertEqual(
                    mm.elements[name].alias,
                    Aliases(aliases=info["alias"]),
                )
        for name, section in mm.sections.items():
            with self.subTest(name=name):
                self.assertIn(name, ["AREA-01", "AREA-02"])
                self.assertIsInstance(section.elements, ElementList)
                if name == "AREA-01":
                    self.assertListEqual(
                        section.names,
                        [
                            "MAG-01",
                            "BPM-01",
                        ],
                    )
                elif name == "AREA-02":
                    self.assertListEqual(section.names, ["CAV-01"])

    def test_machine_model_with_elements_and_areas(self):
        sections = {
            "sections": {
                "AREA-01": ["MAG-01", "BPM-01"],
                "AREA-02": ["CAV-01"],
            }
        }
        with self.assertWarns(Warning):
            mm = MachineModel(
                elements={
                    name: Element(**info) for name, info in self.elements.items()
                },
                section=sections,
            )
        self.assertListEqual(
            list(mm.sections.keys()),
            ["AREA-01", "AREA-02"],
        )
        for name, info in self.elements.items():
            with self.subTest(name=name):
                self.assertIn(name, mm.elements)
                self.assertIsInstance(mm.elements[name], _baseElement)
                self.assertEqual(
                    mm.elements[name].name,
                    info["name"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_class,
                    info["hardware_class"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_type,
                    info["hardware_type"],
                )
                self.assertEqual(
                    mm.elements[name].machine_area,
                    info["machine_area"],
                )
                self.assertEqual(
                    mm.elements[name].alias,
                    Aliases(aliases=info["alias"]),
                )
        for name, section in mm.sections.items():
            with self.subTest(name=name):
                self.assertIn(name, ["AREA-01", "AREA-02"])
                self.assertIsInstance(section.elements, ElementList)
                if name == "AREA-01":
                    self.assertListEqual(
                        section.names,
                        [
                            "MAG-01",
                            "BPM-01",
                        ],
                    )
                elif name == "AREA-02":
                    self.assertListEqual(section.names, ["CAV-01"])
        self.assertDictEqual(mm.lattices, {})

    def test_machine_model_with_elements_areas_and_layout(self):
        sections = {
            "sections": {
                "AREA-01": ["MAG-01", "BPM-01"],
                "AREA-02": ["CAV-01"],
            }
        }
        layout = {
            "layouts": {
                "line1": ["AREA-01", "AREA-02"],
            }
        }
        mm = MachineModel(
            elements={name: Element(**info) for name, info in self.elements.items()},
            section=sections,
            layout=layout,
        )
        self.assertListEqual(
            list(mm.sections.keys()),
            ["AREA-01", "AREA-02"],
        )
        for name, info in self.elements.items():
            with self.subTest(name=name):
                self.assertIn(name, mm.elements)
                self.assertIsInstance(mm.elements[name], _baseElement)
                self.assertEqual(
                    mm.elements[name].name,
                    info["name"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_class,
                    info["hardware_class"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_type,
                    info["hardware_type"],
                )
                self.assertEqual(
                    mm.elements[name].machine_area,
                    info["machine_area"],
                )
                self.assertEqual(
                    mm.elements[name].alias,
                    Aliases(aliases=info["alias"]),
                )
        for name, section in mm.sections.items():
            with self.subTest(name=name):
                self.assertIn(name, ["AREA-01", "AREA-02"])
                self.assertIsInstance(section.elements, ElementList)
                if name == "AREA-01":
                    self.assertListEqual(
                        section.names,
                        [
                            "MAG-01",
                            "BPM-01",
                        ],
                    )
                elif name == "AREA-02":
                    self.assertListEqual(section.names, ["CAV-01"])
        self.assertNotEqual(mm.lattices, {})
        self.assertIsInstance(mm.lattices["line1"], MachineLayout)
        self.assertListEqual(list(mm.lattices.keys()), ["line1"])
        self.assertListEqual(
            mm.lattices["line1"].elements,
            ["MAG-01", "BPM-01", "CAV-01"],
        )
        self.assertListEqual(
            list(mm.lattices["line1"].sections.keys()),
            ["AREA-01", "AREA-02"],
        )
