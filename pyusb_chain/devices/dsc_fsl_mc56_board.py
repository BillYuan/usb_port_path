# MIT License
#
# Copyright (c) 2021 Bill.Yuan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
from sys import platform
from pyusb_chain.devices.comport_device import COMPortDevice
from pyusb_chain.utility import get_values
logger = logging.getLogger("pyusb_path")


class DSCFSLMC56Board(COMPortDevice):
    def __init__(self, name, info):
        super(DSCFSLMC56Board, self).__init__(name, info)
        self.downloadSN = None

    def parse(self):
        super(DSCFSLMC56Board, self).parse()
        self.deviceName = "{}, {}".format("DSC FSL", self.deviceName)

        # update driver key from emulation order
        if "win32" == platform:
            # parse COM ports, note that, for MPU boards, there are more than 1 USB COM port for the same USB port chain
            comPortInfoList = get_values(self.info, r"COM-Port\s*:\s*.*?\(.*\)", [r".*\\Device\\USBSER", r"\)"])
            if comPortInfoList:
                try:
                    self.driverKey = int(comPortInfoList[0])
                except Exception:
                    logger.exception("Fail to parse to get DSC index: {}".format(comPortInfoList[0]))
