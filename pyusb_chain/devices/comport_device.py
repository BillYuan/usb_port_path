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
from pyusb_chain.devices.usb_device import USBDevice
from pyusb_chain.utility import get_values
logger = logging.getLogger("pyusb_path")


class COMPortDevice(USBDevice):
    """COM Port USB device, inherited from USBDevice
    """
    def __init__(self, name, info):
        super(COMPortDevice, self).__init__(name, info)
        #: com ports list
        self.comPorts = None

    def parse(self):
        """Parse the XML information, to the get key values, for COM port USB device, will add com ports information.
        :return: None
        """
        if "win32" == platform:
            super(COMPortDevice, self).parse()
        self.comPorts = self.get_com_port_list(self)

    @staticmethod
    def get_com_port_list(device):
        if "win32" == platform:
            # parse COM ports, note that, for MPU boards, there are more than 1 USB COM port for the same USB port chain
            comPortList = get_values(device.info, r"COM-Port\s*:\s*.*?\(", ["COM-Port", ":", r"\("])
            if comPortList:
                return comPortList
        else:
            device.deviceName = device.info.description
            if device.info.location:
                device.portChain = device.info.location.split(":")[0].replace(".", "-")
            device.locInfo = device.info.hwid
            device.deviceID = "USB/VID_{}&PID_{}".format(device.info.vid, device.info.pid)
            device.sn = device.info.serial_number
            if device.info.device:
                return device.info.device.split(",")
        return None

    def get_com_port(self, index=0):
        """Get the com port name, if there are multi-com ports in the same USB device, need specify the index
        :param index: the index of the com ports
        :return: the com port name, like COM16
        """
        if not self.comPorts:
            return None

        if len(self.comPorts) >= index+1:
            return self.comPorts[index]
        else:
            logger.warning("out of index for com port, index: {}, com port: {}".format(index, self.comPorts))
            return None

    def get_key(self, port=None):
        """The key of the USB device, it's port chain by default, if there are multi-com ports, will append ":index"
        :param port: port name to identify the index
        :return: the key port chain
        """
        if 1 == len(self.comPorts):
            return self.portChain
        else:
            index = 0
            for portItem in self.comPorts:
                if port == portItem:
                    return "{}:{}".format(self.portChain, index)
                index = index + 1
            logger.warning("Multi COM port instance, need specify the port name!")
            return None

    def get_port(self, chain=None):
        """The port name of the USB device, it's COM port name for COMPort USB device
        :param chain: the port chain with additional index
        :return: the port name
        """
        if chain and ":" in chain:
            chainAddition = chain.split(":")[1]
            try:
                chainAddition = int(chainAddition)
            except Exception:
                logger.error("chain key need end with an integer!")
                return None
            return self.get_com_port(chainAddition)
        else:
            if len(self.comPorts) > 1:
                logger.warning("Multi com ports in one chain, need specify the index :0~x")
                return None
            return self.get_com_port()

    def export_data(self, allInfo=False, jsonFormat=False):
        """Export the USB device information to the data for Json exporting or table print
        :param allInfo: Add all SN and Driver Key info in the list data (jsonFormat is False)
        :param jsonFormat: is dict data for json exporting, default is False
        :return: the data of dict or list
        """
        if jsonFormat:
            data = {}
        else:
            data = []
        if len(self.comPorts) > 1:
            index = 0
            for comPort in self.comPorts:
                if jsonFormat:
                    data["{}:{}".format(self.portChain, index)] = self._get_data(isDict=True, comPort=comPort)
                else:
                    data.append(self._get_data(allInfo=allInfo, isDict=False, comPort=comPort, index=index))
                index = index + 1
        else:
            if jsonFormat:
                data["{}".format(self.portChain)] = self._get_data(isDict=True)
            else:
                data.append(self._get_data(allInfo=allInfo, isDict=False))
        return data

    def _get_data(self, allInfo=False, isDict=False, comPort=None, index=None):
        d = super(COMPortDevice, self)._get_data(allInfo=allInfo, isDict=isDict)
        if isDict:
            if comPort:
                d["Port Name"] = comPort
            else:
                d["Port Name"] = self.get_com_port()
        else:
            if index is not None:
                d[0] = "{}:{}".format(self.portChain, index)
            if comPort:
                d[1] = comPort
            else:
                d[1] = self.get_com_port()
        return d
