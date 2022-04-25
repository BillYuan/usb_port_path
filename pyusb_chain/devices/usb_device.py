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
from pyusb_chain.utility import get_values
logger = logging.getLogger("pyusb_path")


class USBDevice(object):
    """USBDevice object uses to store the information of USB device
    (device name, port chain, location, device id, SN and driver key)
    """
    def __init__(self, name, info):
        self.name = name
        self.info = info

        #: deviceName is the friendly name to describe the usb device
        self.deviceName = None

        #: portChain is the key for the usb device, like "1-3-7-4"
        #: for audio device, the portChain will append ":Speaker" or ":Microphone" to identify the playback or record
        #:      device, although they are associated to the same USB device
        #: for USB COM port, if there are more than 1 com ports associated to the same USB device, like I.MX8 series,
        #:      the portChain will append the index ":0" or ":1"
        self.portChain = None

        #: locInfo is to the original location information, like "Port_#0001.Hub_#0002"
        self.locInfo = None

        #: deviceID is the assigned ID by the system, like "USB\VID_0403&PID_6011\6&2ED78AA8&0&1"
        self.deviceID = None

        #: sn is the SN information for the device, not all USB device has SN
        self.sn = None

        #: driverKey is the driver key name, there is a index at the end, which will be used to Altera Blaster
        #: (CPLD downloader) which one is the first #0, or secondary #1, .etc.
        self.driverKey = 0

    def parse(self):
        """Parse the XML information, to the get key values.
        :return: None
        """
        self.portChain = self.name.split(":")[0].replace("[", "").replace("]", "").strip()
        self.deviceName = self.name.replace("[{}] :".format(self.portChain), "").strip()

        # parse location information
        locInfoList = get_values(self.info, r"\r\nLocation Info\s*:\s*.*?\r\n", ["Location Info", ":"])
        if locInfoList:
            self.locInfo = locInfoList[0]

        # parse device ID
        deviceIDList = get_values(self.info, r"\r\nDevice ID\s*:\s*.*?\r\n", ["Device ID", ":"])
        if deviceIDList:
            self.deviceID = deviceIDList[0]

        # parse sn
        snList = get_values(self.info, r"\r\niSerialNumber.*?\r\n Language 0x0409\s*:\s*.*?\r\n",
                                 ["iSerialNumber.*?\r\n", "Language 0x0409", ":", "\""])
        if snList:
            self.sn = snList[0]

        # parse driver key, conver to index
        # which is used to get the index priority for Altera blaster list
        driverKeyList = get_values(self.info, r"\r\nDriver KeyName\s*:\s*.*?\(",
                                 ["Driver KeyName", ":", r"\(", r"\{.*\}", r"\\"])
        if driverKeyList:
            driverKey = driverKeyList[0]
            try:
                self.driverKey = int(driverKey)
            except Exception:
                logger.exception("Fail to parse to get driver key index: {}".format(driverKey))

    def get_key(self, port=None):
        """The key of the USB device, it's port chain by default
        :param port: interface to be used in child classes
        :return: the key port chain
        """
        return self.portChain

    def get_port(self, chain=None):
        """The port name of the USB device, it's None by default
        :param chain: interface to be used in child classes
        :return: the port name
        """
        return None

    def export_data(self, allInfo=False, jsonFormat=False):
        """Export the USB device information to the data for Json exporting or table print
        :param allInfo: Add all SN and Driver Key info in the list data (jsonFormat is False)
        :param jsonFormat: is dict data for json exporting, default is False
        :return: the data of dict or list
        """
        if jsonFormat:
            d = {}
            d["{}".format(self.portChain)] = self._get_data(isDict=True)
            return d
        else:
            return [self._get_data(allInfo=allInfo)]

    def _get_data(self, allInfo=False, isDict=False):
        if isDict:
            d = {}
            d["Port Name"] = ""
            d["Device Name"] = self.deviceName
            d["SN"] = self.sn
            d["Location Info"] = self.locInfo
            d["Device ID"] = self.deviceID
            d["Driver Key"] = self.driverKey
        else:
            d = []
            d.append(self.portChain)
            d.append("")
            d.append(self.deviceName)
            if allInfo:
                d.append(self.sn)
                d.append(self.driverKey)
        return d
