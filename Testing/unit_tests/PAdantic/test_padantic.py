import unittest
from PAdantic.PAdantic import PAdantic
from PAdantic.models.element import Quadrupole
from PAdantic.models.magnetic import Quadrupole_Magnet
from PAdantic.models.physical import PhysicalElement, Position


class TestPAdantic(unittest.TestCase):
    def setUp(self):
        self.q1 = Quadrupole(
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
        self.q2 = Quadrupole(
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
        self.sections = {
            "sections": {
                "FODO": ["QUAD1"],
                "NODO": ["QUAD2"],
            }
        }
        self.layouts = {
            "layouts": {
                "line1": ["FODO", "NODO"],
            }
        }

        self.machine = PAdantic(
            layout=self.layouts,
            section=self.sections,
            element_list=[self.q1, self.q2],
        )

    def test_get_elements_s_pos(self):
        elements_s_pos = self.machine.get_elements_s_pos()
        self.assertIsInstance(elements_s_pos, dict)
        self.assertGreater(len(elements_s_pos), 0)

    def test_get_dipoles(self):
        dipoles = self.machine.get_dipoles()
        self.assertIsInstance(dipoles, list)
        self.assertEqual(len(dipoles), 0)

    def test_get_quadrupoles(self):
        quadrupoles = self.machine.get_quadrupoles()
        self.assertIsInstance(quadrupoles, list)
        self.assertGreater(len(quadrupoles), 0)

    def test_get_element_with_two_paths_fails_when_path_is_not_provided(self):
        layouts = {
            "layouts": {
                "line1": ["FODO", "NODO"],
                "line2": ["NODO", "FODO"],
            }
        }
        machine = PAdantic(
            layout=layouts,
            section=self.sections,
            element_list=[self.q1, self.q2],
        )
        with self.assertRaises(Exception) as context:
            _ = machine.get_quadrupoles()
            self.assertEqual(context.msg, '"default_layout" = None is not defined')

    def test_get_element_with_two_paths_and_path_defined(self):
        layouts = {
            "layouts": {
                "line1": ["FODO", "NODO"],
                "line2": ["NODO", "XODO"],
            }
        }
        q3 = Quadrupole(
                    name="QUAD3",
                    machine_area="XODO",
                    magnetic=Quadrupole_Magnet(
                        length=0.1,
                        k1l=1.0,
                    ),
                    physical=PhysicalElement(
                        middle=Position(
                            x=0,
                            y=0,
                            z=0.6,
                        ),
                        length=0.1,
                    ),
                )
        sections = {
                    "sections": {
                        "FODO": ["QUAD1"],
                        "NODO": ["QUAD2"],
                        "XODO": ["QUAD3"],
                    }
                }
        machine = PAdantic(
            layout=layouts,
            section=sections,
            element_list=[self.q1, self.q2, q3],
        )
        quadrupoles = machine.get_quadrupoles(path="line1")
        self.assertIsInstance(quadrupoles, list)
        self.assertGreater(len(quadrupoles), 0)
        quadrupoles = machine.get_quadrupoles(path="line2")
        self.assertIsInstance(quadrupoles, list)
        self.assertGreater(len(quadrupoles), 0)
