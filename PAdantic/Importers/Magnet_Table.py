import os
from math import ceil
import pandas

magnet_table_filename = os.path.join(
    os.path.dirname(__file__), "CLARA Magnet Table v6.xlsx"
)
magnet_table = pandas.read_excel(
    magnet_table_filename,
    sheet_name="Table",
    skiprows=2,
    index_col=(2, 3, 5, 6),
    dtype={"serial number": "str"},
).fillna(0)


def create_degauss_values(maxI):
    if maxI < 10.0:
        maxI = 10.0
    return [
        round(ceil(maxI) / 10.0 * v, 2)
        for v in [9.98, -9.98, 6.0, -6.0, 4.0, -4.0, 2.0, -2.0, 1.0, -1.0, 0.0]
    ]


def add_magnet_table_parameters(n, e, magnetPV):
    try:
        magPVsplit = magnetPV.split("-")
        magnet = (
            magPVsplit[0].replace("EBT", "CLA"),
            magPVsplit[1].replace("HRG1", "GUN"),
            magPVsplit[3],
            int(magPVsplit[4]),
        )
        table = magnet_table.loc[
            magnet,
            [
                "slope [units/A]",
                "max current [A]",
                "f [units/A³]",
                "a [units/A²]",
                "I0 [A]",
                "d [units]",
                "magnetic length [mm]",
                "current [A]",
                "magnet type",
                "serial number",
            ],
        ]
        m, I_max, f, a, I0, d, L, I_degauss, manufacturer, serial_number = table
        e.magnetic.linear_saturation_coefficients.update_from_string(
            ",".join(list(map(str, [m, I_max, f, a, I0, d, L])))
        )
        e.degauss.values = create_degauss_values(float(I_degauss))
        e.manufacturer.manufacturer = manufacturer
        e.manufacturer.serial_number = serial_number
        e.electrical.maxI = ceil(I_degauss)
        e.electrical.minI = -1.0 * ceil(I_degauss)
    except Exception:
        print("Magnet missing from magnet table!", magnet)
    return e
