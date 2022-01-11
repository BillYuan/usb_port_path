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
from pyusb_chain.devices.audio_device import AudioDevice
from pyusb_chain.devices.comport_device import COMPortDevice
logger = logging.getLogger("pyusb_path")


class AudioCOMPortDevice(AudioDevice):
    def __init__(self, name, info):
        super(AudioCOMPortDevice, self).__init__(name, info)
        self.comPorts = None

    def parse(self):
        """Parse the XML information, to the get key values, for COM port USB device, will add com ports information.
        :return: None
        """
        super(AudioCOMPortDevice, self).parse()
        self.comPorts = COMPortDevice.get_com_port_list(self)

    def get_com_port(self, index=0):
        """Get the com port name, if there are multi-com ports in the same USB device, need specify the index
        :return: the com port name, like COM16
        """
        if not self.comPorts:
            return None
        return self.comPorts[0]  # only support 1 COM port so far

    def get_key(self, port="speaker"):
        """The key of the USB device, it's port chain with ":Speaker" or ":Microphone" or ":COM"
        :param port: port name to identify the Speaker or Microphone
        :return: the key port chain with ":Speaker" or ":Microphone"
        """
        if "com" in port.lower():
            return "{}:{}".format(self.portChain, self.get_com_port())
        return super(AudioCOMPortDevice, self).get_key(port)

    def get_port(self, chain=None):
        """The port name of the USB device, it's Audio playback name or record name or comport name
        :param chain: the port chain with additional audio type
        :return: the port name
        """
        if "com" in chain.lower():
            return self.get_com_port()
        return super(AudioCOMPortDevice, self).get_port(chain)

    def export_data(self, allInfo=False, jsonFormat=False):
        """Export the USB device information to the data for Json exporting or table print
        :param allInfo: Add all SN and Driver Key info in the list data (jsonFormat is False)
        :param jsonFormat: is dict data for json exporting, default is False
        :return: the data of dict or list
        """
        data = super(AudioCOMPortDevice, self).export_data(allInfo, jsonFormat)
        if jsonFormat:
            data["{}:{}".format(self.portChain, self.get_com_port())] = self._get_data(isDict=True, portName=self.get_com_port())
        else:
            if self.get_com_port():
                data.append(self._get_data(allInfo=allInfo, isDict=False, portName=self.get_com_port()))
        return data

    def _get_data(self, allInfo=False, isDict=False, portName=None):
        d = super(AudioCOMPortDevice, self)._get_data(allInfo, isDict, portName)
        if portName and "com" in portName.lower():
            if isDict:
                if portName:
                    d["Port Name"] = portName
            else:
                d[0] = "{}:{}".format(self.portChain, self.get_com_port())
                d[1] = self.get_com_port()
        return d
