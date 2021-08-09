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
import re

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
        self.driveKey = 0

    def parse(self):
        """Parse the XML information, to the get key values.
        :return: None
        """
        self.portChain = self.name.split(":")[0].replace("[", "").replace("]", "").strip()
        self.deviceName = self.name.replace("[{}] :".format(self.portChain), "").strip()

        # parse location information
        locInfoList = self.get_values(self.info, r"\r\nLocation Info\s*:\s*.*?\r\n", ["Location Info", ":"])
        if locInfoList:
            self.locInfo = locInfoList[0]

        # parse device ID
        deviceIDList = self.get_values(self.info, r"\r\nDevice ID\s*:\s*.*?\r\n", ["Device ID", ":"])
        if deviceIDList:
            self.deviceID = deviceIDList[0]

        # parse sn
        snList = self.get_values(self.info, r"\r\niSerialNumber.*?\r\n Language 0x0409\s*:\s*.*?\r\n",
                                 ["iSerialNumber.*?\r\n", "Language 0x0409", ":", "\""])
        if snList:
            self.sn = snList[0]

        # parse driver key, conver to index
        # which is used to get the index priority for Altera blaster list
        driverKeyList = self.get_values(self.info, r"\r\nDriver KeyName\s*:\s*.*?\(",
                                 ["Driver KeyName", ":", r"\(", r"\{.*\}", r"\\"])
        if driverKeyList:
            driverKey = driverKeyList[0]
            try:
                self.driveKey = int(driverKey)
            except Exception:
                logger.exception("Fail to parse to get driver key index: {}".format(driverKey))

    @staticmethod
    def get_values(text, reg, excludeWrappers=None):
        """Use regular expression and exclude wrappers to get the final required string
        :param text: the full original string
        :param reg:  regular expression to search
        :param excludeWrappers: to be excluded after getting from the reg search, use ',' to separate multi-wrappers.
        :return: all matched values list
        """
        values = []
        if not text:
            return values

        try:
            pattern = re.compile(reg)
            matched = pattern.findall(text)
            if matched and len(matched) > 0:
                for v in matched:
                    if excludeWrappers:
                        s = v
                        for wrapper in excludeWrappers:
                            s = re.sub(wrapper, "", s)
                        values.append(s.strip())
                    else:
                        values.append(v.strip())
        except Exception:
            logger.exception("invalid parse to get value: {}".format(reg))
        return values

    def get_key(self, port=None):
        """The key of the USB device, it's port chain by default
        :param port: interface to be used in child classes
        :return: the key port chain
        """
        return self.portChain

    def get_port(self, chain=None):
        """The port name of the USB device, it's deviceID by default
        :param chain: interface to be used in child classes
        :return: the port name
        """
        return self.deviceID

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
            d["Driver Key"] = self.driveKey
        else:
            d = []
            d.append(self.portChain)
            d.append("")
            d.append(self.deviceName)
            if allInfo:
                d.append(self.sn)
                d.append(self.driveKey)
        return d


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
        super(COMPortDevice, self).parse()
        # parse COM ports, note that, for MPU boards, there are more than 1 USB COM port for the same USB port chain
        comPortList = self.get_values(self.info, r"COM-Port\s*:\s*.*?\(", ["COM-Port", ":", r"\("])
        if comPortList:
            self.comPorts = comPortList

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
        audioList = self.get_values(self.info, r"Child Device \d\s*:.*\s*Device ID.*?\s*Class\s*:\s*AudioEndpoint\s*")
        if audioList:
            for audioInfo in audioList:
                audioInfoList = self.get_values(audioInfo, r"Child Device \d\s*:\s*.*?\r\n\s*Device ID",
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
