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
from pyusb_chain.devices.usb_device import USBDevice
from pyusb_chain.utility import get_values
logger = logging.getLogger("pyusb_path")


class AudioDevice(USBDevice):
    def __init__(self, name, info):
        super(AudioDevice, self).__init__(name, info)
        self.audioPlaybackName = None
        self.audioRecordName = None

    def parse(self):
        """Parse the XML information, to the get key values.
        :return: None
        """
        super(AudioDevice, self).parse()
        # parse audio playback
        # search Child Device ... with Class : AudioEndpoint
        # then parser the Audio Port name from Child Device, note that '(Audio Endpoint)' should be excluded.
        audioList = get_values(self.info, r"Child Device \d\s*:.*\s*Device ID.*?\s*Class\s*:\s*AudioEndpoint\s*")
        if audioList:
            for audioInfo in audioList:
                audioInfoList = get_values(audioInfo, r"Child Device \d\s*:\s*.*?\r\n\s*Device ID",
                                                [r"Child Device \d", ":", r"\(Audio Endpoint\)", "Device ID"])
                self.__parse_audio_port_name(audioInfoList)

    def __parse_audio_port_name(self, audioInfoList):
        if not audioInfoList:
            return
        for audio in audioInfoList:
            if "sp" in audio.lower() or "headphone" in audio.lower():
                if not self.audioPlaybackName:
                    self.audioPlaybackName = audio
            elif "mic" in audio.lower() or "rec" in audio.lower() or "linein" in audio.lower():
                if not self.audioRecordName:
                    self.audioRecordName = audio

    def get_key(self, port="speaker"):
        """The key of the USB device, it's port chain with ":Speaker" or ":Microphone"
        :param port: port name to identify the Speaker or Microphone
        :return: the key port chain with ":Speaker" or ":Microphone"
        """
        if "mic" in port.lower():
            return "{}:Microphone".format(self.portChain)
        elif "sp" in port.lower():
            return "{}:Speaker".format(self.portChain)
        return None

    def get_port(self, chain=None):
        """The port name of the USB device, it's Audio playback name or record name
        :param chain: the port chain with additional audio type
        :return: the port name
        """
        if chain and "mic" in chain.lower():
            return self.audioRecordName
        elif chain and "sp" in chain.lower():
            return self.audioPlaybackName
        logger.warning("chain for audio device need end with :Microphone or :Speaker")
        return None

    def export_data(self, allInfo=False, jsonFormat=False):
        """Export the USB device information to the data for Json exporting or table print
        :param allInfo: Add all SN and Driver Key info in the list data (jsonFormat is False)
        :param jsonFormat: is dict data for json exporting, default is False
        :return: the data of dict or list
        """
        if jsonFormat:
            data = {}
            data["{}:{}".format(self.portChain, "Speaker")]= self._get_data(isDict=True, portName=self.audioPlaybackName)
            if self.audioRecordName:
                data["{}:{}".format(self.portChain, "Microphone")] = self._get_data(isDict=True, portName=self.audioRecordName)
        else:
            data = []
            data.append(self._get_data(allInfo=allInfo, isDict=False, portName=self.audioPlaybackName))
            if self.audioRecordName:
                data.append(self._get_data(allInfo=allInfo, isDict=False, portName=self.audioRecordName))
        return data

    def _get_data(self, allInfo=False, isDict=False, portName=None):
        d = super(AudioDevice, self)._get_data(allInfo=allInfo, isDict=isDict)
        if isDict:
            if portName:
                d["Port Name"] = portName
            else:
                d["Port Name"] = self.audioPlaybackName
        else:
            if portName == self.audioRecordName:
                d[0] = "{}:{}".format(self.portChain, "Microphone")
                d[1] = self.audioRecordName
            else:
                d[0] = "{}:{}".format(self.portChain, "Speaker")
                d[1] = self.audioPlaybackName
        return d
