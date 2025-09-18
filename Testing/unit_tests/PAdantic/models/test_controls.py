import unittest
from PAdantic.models.control import ControlVariable, ControlsInformation


class TestControlVariable(unittest.TestCase):
    def test_control_variable_creation(self):
        cv = ControlVariable(
            identifier="var1",
            dtype="float",
            protocol="CA",
            units="V",
            description="A float variable for voltage",
        )
        self.assertEqual(cv.identifier, "var1")
        self.assertEqual(cv.dtype, float)
        self.assertEqual(cv.protocol, "CA")
        self.assertEqual(cv.units, "V")
        self.assertEqual(cv.description, "A float variable for voltage")

    def test_dtype_as_type(self):
        cv = ControlVariable(
            identifier="var1",
            dtype=float,
            protocol="CA",
        )
        self.assertEqual(cv.dtype, float)

    def test_validation_for_missing_dtype(self):
        with self.assertRaises(ValueError):
            ControlVariable(
                identifier="var1",
                protocol="CA",
            )

    def test_validation_for_missing_identifier(self):
        with self.assertRaises(ValueError):
            ControlVariable(
                dtype="float",
                protocol="CA",
            )

    def test_validation_for_missing_protocol(self):
        with self.assertRaises(ValueError):
            ControlVariable(
                identifier="var1",
                dtype="float",
            )

    def test_invalid_dtype(self):
        with self.assertRaises(ValueError):
            ControlVariable(
                identifier="var2",
                dtype="unknown_type",
                protocol="PVA",
            )


class TestControlsInformation(unittest.TestCase):
    def test_controls_information_creation(self):
        controls_info = ControlsInformation(
            variables={
                "var1": ControlVariable(
                    identifier="var1",
                    dtype="float",
                    protocol="CA",
                    units="V",
                    description="A float variable for voltage",
                ),
                "var2": ControlVariable(
                    identifier="var2",
                    dtype="int",
                    protocol="PVA",
                ),
            }
        )
        self.assertIn("var1", controls_info.variables)
        self.assertIn("var2", controls_info.variables)
        self.assertEqual(controls_info.variables["var1"].dtype, float)
        self.assertEqual(controls_info.variables["var2"].dtype, int)

    def test_controls_information_with_dicts(self):
        controls_info = ControlsInformation(
            variables={
                "var1": {
                    "identifier": "var1",
                    "dtype": "float",
                    "protocol": "CA",
                    "units": "V",
                    "description": "A float variable for voltage",
                },
                "var2": {
                    "identifier": "var2",
                    "dtype": "int",
                    "protocol": "PVA",
                },
            }
        )
        self.assertIn("var1", controls_info.variables)
        self.assertIn("var2", controls_info.variables)
        self.assertEqual(controls_info.variables["var1"].dtype, float)
        self.assertEqual(controls_info.variables["var2"].dtype, int)

    def test_controls_information_with_mixed_types(self):
        controls_info = ControlsInformation(
            variables={
                "var1": ControlVariable(
                    identifier="var1",
                    dtype="float",
                    protocol="CA",
                    units="V",
                    description="A float variable for voltage",
                ),
                "var2": {
                    "identifier": "var2",
                    "dtype": "int",
                    "protocol": "PVA",
                },
            }
        )
        self.assertIn("var1", controls_info.variables)
        self.assertIn("var2", controls_info.variables)
        self.assertEqual(controls_info.variables["var1"].dtype, float)
        self.assertEqual(controls_info.variables["var2"].dtype, int)

    def test_controls_information_with_invalid_dict(self):
        with self.assertRaises(ValueError):
            ControlsInformation(
                variables={
                    "var1": {
                        "identifier": "var1",
                        "dtype": "float",
                        # Missing protocol
                    },
                }
            )

    def test_controls_information_with_invalid_type(self):
        with self.assertRaises(TypeError):
            ControlsInformation(variables=["not", "a", "dict"])

    def test_controls_information_model_dump_serialises_dtypes(self):
        controls_info = ControlsInformation(
            variables={
                "var1": ControlVariable(
                    identifier="var1",
                    dtype=float,
                    protocol="CA",
                    units="V",
                    description="A float variable for voltage",
                ),
                "var2": ControlVariable(
                    identifier="var2",
                    dtype=int,
                    protocol="PVA",
                ),
            }
        )
        dumped = controls_info.model_dump()
        self.assertEqual(dumped["variables"]["var1"]["dtype"], "float")
        self.assertEqual(dumped["variables"]["var2"]["dtype"], "int")
