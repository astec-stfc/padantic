import unittest
from PAdantic.models.element import Element, ElectricalElement, ManufacturerElement


class TestElement(unittest.TestCase):

    def test_element_creation_with_no_controls(self):
        elem = Element(
            machine_area="AREA-01",
            hardware_type="Magnet",
            hardware_class="Quadrupole",
            name="CLA-A1-QUAD-01",
        )
        self.assertEqual(elem.machine_area, "AREA-01")
        self.assertEqual(elem.hardware_type, "Magnet")
        self.assertEqual(elem.name, "CLA-A1-QUAD-01")
        self.assertIsInstance(elem, Element)
        self.assertIsInstance(elem.electrical, ElectricalElement)
        self.assertIsInstance(elem.manufacturer, ManufacturerElement)
        self.assertIsNone(elem.controls, None)
        self.assertIsNone(elem.alias)

    def test_element_with_aliases(self):
        elem = Element(
            machine_area="AREA-01",
            hardware_type="Magnet",
            hardware_class="Quadrupole",
            name="CLA-A1-QUAD-01",
            alias=["CLA-QUAD01", "CLA-QUAD1"],
        )
        self.assertEqual(elem.alias.aliases, ["CLA-QUAD01", "CLA-QUAD1"])

    def test_to_CATAP(self):
        elem = Element(
            machine_area="AREA-01",
            hardware_type="Magnet",
            hardware_class="Quadrupole",
            name="CLA-A1-QUAD-01",
            alias=["CLA-QUAD01", "CLA-QUAD1"],
        )
        catap_dict = elem.to_CATAP()
        self.assertEqual(catap_dict["machine_area"], "AREA-01")
        self.assertEqual(catap_dict["hardware_type"], "Magnet")
        self.assertEqual(catap_dict["name"], "CLA-A1-QUAD-01")
        self.assertEqual(catap_dict["name_alias"], ["CLA-QUAD01", "CLA-QUAD1"])
        self.assertEqual(catap_dict["manufacturer"], "")
        self.assertNotIn("controls", catap_dict)
        self.assertNotIn("electrical", catap_dict)

    def test_element_creation_with_controls(self):
        controls_info = {
            "variables": {
                "var1": {
                    "identifier": "var1",
                    "dtype": "float",
                    "protocol": "CA",
                    "units": "V",
                    "description": "A float variable for voltage",
                }
            }
        }
        elem = Element(
            machine_area="AREA-01",
            hardware_type="Magnet",
            hardware_class="Quadrupole",
            name="CLA-A1-QUAD-01",
            controls=controls_info,
        )
        self.assertIsNotNone(elem.controls)
        self.assertIn("var1", elem.controls.variables)
        self.assertEqual(elem.controls.variables["var1"].identifier, "var1")
        self.assertEqual(elem.controls.variables["var1"].dtype, float)
        self.assertEqual(elem.controls.variables["var1"].protocol, "CA")
        self.assertEqual(elem.controls.variables["var1"].units, "V")
        self.assertEqual(
            elem.controls.variables["var1"].description, "A float variable for voltage"
        )

    def test_element_serialisation(self):
        controls_info = {
            "variables": {
                "var1": {
                    "identifier": "var1",
                    "dtype": "float",
                    "protocol": "CA",
                    "units": "V",
                    "description": "A float variable for voltage",
                }
            }
        }
        elem = Element(
            machine_area="AREA-01",
            hardware_type="Magnet",
            hardware_class="Quadrupole",
            name="CLA-A1-QUAD-01",
            controls=controls_info,
        )
        serialized = elem.model_dump()
        self.assertIn("machine_area", serialized)
        self.assertIn("hardware_type", serialized)
        self.assertIn("hardware_class", serialized)
        self.assertIn("name", serialized)
        self.assertIn("manufacturer", serialized)
        self.assertIn("electrical", serialized)
        self.assertIn("alias", serialized)
        self.assertIn("physical", serialized)
        self.assertIn("controls", serialized)
        self.assertIn("variables", serialized["controls"])
        self.assertIn("var1", serialized["controls"]["variables"])
        self.assertEqual(
            serialized["controls"]["variables"]["var1"]["identifier"], "var1"
        )
        self.assertEqual(serialized["controls"]["variables"]["var1"]["dtype"], "float")
        self.assertEqual(serialized["controls"]["variables"]["var1"]["protocol"], "CA")
        self.assertEqual(serialized["controls"]["variables"]["var1"]["units"], "V")
        self.assertEqual(
            serialized["controls"]["variables"]["var1"]["description"],
            "A float variable for voltage",
        )


if __name__ == "__main__":
    unittest.main()
