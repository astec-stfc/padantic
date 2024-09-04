import os
import sys

sys.path.append(r"C:\Users\jkj62\Documents\GitHub\SimFrame")
sys.path.append(os.path.abspath("../../"))
from PAdantic.PAdantic import PAdantic
from SimulationFramework import Framework as fw

import argparse

parser = argparse.ArgumentParser(description="Track the FEBE lattice.")
parser.add_argument(
    "setting", default="1", type=str, help="Settings directory to load settings from"
)
parser.add_argument("charge", default=250, type=int, help="Starting charge in pC")
parser.add_argument(
    "--sample",
    default=2,
    type=int,
    help="Sub-sample the input distribution by factor 2**(3 * sample)",
)
parser.add_argument("--code", default="elegant", type=str, help="Tracking code to use")


class test:

    def __init__(
        self,
        args,
        start_lattice="S02",
        startcharge=250,
        code="elegant",
        clean=False,
        prefix=None,
    ):
        super().__init__()
        self.args = args
        self.framework = fw.Framework(".", clean=False, overwrite=False, verbose=False)
        self.start_lattice = start_lattice
        self.startcharge = startcharge
        self.code = code
        self.prefix = prefix
        self.scaling = 6
        self.sample_interval = 2 ** (3 * self.args.sample)

    def before_tracking(self):
        if self.prefix is None:
            self.framework[self.start_lattice].prefix = (
                "../../Basefiles/Base_" + str(self.args.charge) + "pC/"
            )
        self.framework[self.start_lattice].sample_interval = 2 ** (3 * self.args.sample)

    def track(self, *args, **kwargs):
        self.before_tracking()
        self.framework.track(*args, **kwargs)


if __name__ == "__main__":
    args = parser.parse_args()

    opt = test(
        args,
        start_lattice="FEBE",
        prefix=None,
        startcharge=args.charge,
        code=args.code,
        clean=False,
    )
    opt.framework.loadSettings("./FEBE_2_Bunches.def")
    opt.framework.clean = False
    opt.framework.setSubDirectory(
        "Output/Setup_" + str(args.setting) + "_" + str(opt.startcharge) + "pC/"
    )

    quad_settings_files = [
        "./Settings/"
        + str(args.charge)
        + "pC/"
        + args.setting
        + "/transverse_best_changes_upto_S07_Simple.yaml",
        "./Settings/"
        + str(args.charge)
        + "pC/"
        + args.setting
        + "/S07_transverse_best_changes_Simple.yaml",
        "./Settings/"
        + str(args.charge)
        + "pC/"
        + args.setting
        + "/FEBE_transverse_best_changes.yaml",
        "./Settings/"
        + str(args.charge)
        + "pC/"
        + args.setting
        + "/nelder_mead_best_changes_Simple.yaml",
    ]
    changes_files = []
    print(opt.framework["bunch_compressor"])
    for c in quad_settings_files:
        opt.framework.load_changes_file(c)

    for c in changes_files:
        opt.framework.load_changes_file(c)
    print(opt.framework["bunch_compressor"])
    # print(opt.framework['FEBE'])
    # opt.track(startfile=opt.start_lattice, endfile='FEBE', preprocess=True, track=True, postprocess=False, save_summary=False)
