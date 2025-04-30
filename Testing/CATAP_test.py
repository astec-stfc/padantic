import os
import sys

sys.path.append(
    r"C:\Users\jkj62.CLRC\Documents\GitHub\CATAP\Nightly\CATAP_Nightly_15_04_2024\python310"
)
from CATAP.HardwareFactory import HardwareFactory, STATE  # noqa E402


class Test:

    def __init__(self):
        self.HFHF = HardwareFactory
        self.CATAP_state = STATE.VIRTUAL  # STATE.OFFLINE
        self.HardwareFactory = self.HFHF(
            self.CATAP_state, os.path.abspath("./to_CATAP/MasterLattice")
        )
        self.HardwareFactory.messagesOff()
        # self.HardwareFactory.debugMessagesOff()
        # self.HardwareFactory.makeSilent()
        self.magnetFactory = self.HardwareFactory.getMagnetFactory()


if __name__ == "__main__":
    test = Test()
