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

import os
import uuid
import logging
import re
import subprocess
from sys import platform
if "win32" != platform:
    from serial.tools import list_ports
import xml.etree.ElementTree as ET
from pyusb_chain.usb_device import USBDevice, AudioDevice, COMPortDevice, AlteraUSBBlaster

logger = logging.getLogger("pyusb_path")


class UsbTreeViewTool(object):
    """The USB Tree View Tool object implements the command line interface of free tool
    UsbTreeView.exe in Windows.
    To get the all connected USB devices information, including the USB port chain.
    """
    def __init__(self):
        self.currentPath = os.path.dirname(os.path.abspath(__file__))

        #: Store the scanned all connected USB devices (not including USB hubs)
        self.usbDevices = []

        if "win32" == platform:
            #: The UsbTreeView.exe location
            self.tool = os.path.join(self.currentPath, "UsbTreeView.exe")

    def start_gui(self):
        """Start the UsbTreeView.exe directly
        :return: None
        """
        if "win32" != platform:
            return
        subprocess.Popen("\"{}\"".format(self.tool))

    def export_xml(self):
        """Use UsbTreeView.exe command line to export the XML format of all USB devices information in current PC.
        :return: the exported file name
        """
        if "win32" != platform:
            return
        randomUUID = uuid.uuid4()
        exportFile = "export_{}.xml".format(randomUUID)
        # export xml file
        cmd = "\"{}\" /X={}".format(self.tool, exportFile)
        os.system(cmd)
        return exportFile

    def scan(self):
        """First export the XML file, then parse the all scanned USB devices.
        The information will store in self.usbDevices.
        :return: None
        """
        print("Scanning all USB devices...")
        exportFile = None
        try:
            if "win32" == platform:
                exportFile = self.export_xml()
                self.parse(exportFile)
            else:
                self.parse_linux()
        finally:
            # remove temp export file
            if "win32" == platform:
                if os.path.exists(exportFile):
                    os.remove(exportFile)

    def parse(self, exportFile):
        """Parse the XML file that exported by UsbTreeView.exe
        :param exportFile: the XML file that exported by UsbTreeView.exe
        :return: None
        """
        if "win32" != platform:
            return

        root = ET.parse(exportFile).getroot()
        alteraDevices = []
        for tag in root.iter('node'):
            name = tag.get('text')
            if ":" in name:
                usbHubReg = re.compile(r"Generic .* Hub")
                if usbHubReg.search(name):
                    continue
                info = tag[0].text
                usbSerialDeviceReg = re.compile(r"COM\d")
                usbAudioDeviceReg = re.compile("Audio")
                usbAudioDeviceInfoReg = re.compile("Class\s*:\s*AudioEndpoint")
                usbAlteraUSBBlasterReq = re.compile("Altera USB-Blaster")
                if usbSerialDeviceReg.search(name):
                    usbDevice = COMPortDevice(name, info)
                elif usbAudioDeviceReg.search(name) or usbAudioDeviceInfoReg.search(info):
                    usbDevice = AudioDevice(name, info)
                elif usbAlteraUSBBlasterReq.search(name):
                    usbDevice = AlteraUSBBlaster(name, info)
                    alteraDevices.append(usbDevice)
                else:
                    usbDevice = USBDevice(name, info)
                usbDevice.parse()
                self.usbDevices.append(usbDevice)
        if alteraDevices:
            alteraDevices.sort(key=lambda x: x.driverKey)
            index = 0
            for device in alteraDevices:
                device.USBBlasterName = "USB-Blaster [USB-{}]".format(index)
                index = index + 1

    def parse_linux(self):
        """Parse the USB serial by pyserial, note that it only support VCOM usb devices
            :return: None
        """
        if "win32" == platform:
            return
        ports = list_ports.comports()
        for port in ports:
            if port.pid:
                usbDevice = COMPortDevice(port.description, port)
                usbDevice.parse()
                self.usbDevices.append(usbDevice)

    def get_from_sn(self, sn):
        """Get the usb device by the SN if the devcie has the SN.
        :param sn: the SN of the device to search
        :return: the UsbDevice (None if it's not found)
        """
        if not sn:
            return None

        snKey = sn.split(":")[0]
        for device in self.usbDevices:
            if snKey == device.sn:
                return device
        logger.warning("Cannot get USB device from sn: {}!".format(sn))
        return None

    def get_from_chain(self, chain):
        """Get the usb device by the chain.
        :param chain: the chain to search, like 1-2-3, or 1-5-4:Speaker, 1-5-4:Microphone for audio device,
                      if there are more than 1 com ports associated to the same chain, use index like: 1-3-5:0
        :return: the UsbDevice (None if it's not found)
        """
        if not chain:
            return None

        chainKey = chain.split(":")[0]
        for device in self.usbDevices:
            if chainKey == device.portChain:
                return device
        logger.warning("Cannot get USB device from chain: {}!".format(chain))
        return None

    def get_from_port(self, port):
        """Get the usb device by the port.
        :param port: the port name to search, like "COM17", "Speakers (4- USB Audio Device)"
        :return: the UsbDevice (None if it's not found)
        """
        if not port:
            return None

        for device in self.usbDevices:
            if isinstance(device, AudioDevice):
                if port == device.audioPlaybackName or port == device.audioRecordName:
                    return device
            elif isinstance(device, COMPortDevice):
                if port in device.comPorts:
                    return device
            elif isinstance(device, USBDevice):
                if port == device.deviceID:
                    return device
        logger.warning("Cannot get USB device from port: {}!".format(port))
        return None

    def get_chain_from_port(self, port):
        """Get the chain from the port name.
        :param port: the port name to search, like "COM17", "Speakers (4- USB Audio Device)"
        :return: the chain, like 1-2-3, or 1-5-4:Speaker, 1-5-4:Microphone for audio device,
                 if there are more than 1 com ports associated to the same chain, use index like: 1-3-5:0
        """
        device = self.get_from_port(port)
        if device:
            return device.get_key(port=port)
        return None

    def get_port_from_chain(self, chain=None):
        """Get the port name from the chain
        :param chain: the chain to search, like 1-2-3, or 1-5-4:Speaker, 1-5-4:Microphone for audio device,
                      if there are more than 1 com ports associated to the same chain, use index like: 1-3-5:0
        :return: the port name, like "COM17", "Speakers (4- USB Audio Device)"
        """
        device = self.get_from_chain(chain)
        if device:
            return device.get_port(chain)
        return None

    def filter(self, filters):
        """Filter the usb devices by keywords.
        :param filters: keywords to be search (not case sensitive), use ',' to separate multi-keys.
                        Once there is the key matched in all information of the usb device
                        (port chain, device name, sn, .etc), it will be included in the return list
        :return: the usb devices list
        """
        devices = []
        for device in self.usbDevices:
            dataHash = device.export_data()
            if filters and not UsbTreeViewTool.__include(dataHash, filters):
                continue
            devices.append(device)
        return devices

    @staticmethod
    def __include(data, filters):
        line = ""
        for item in data:
            if item:
                line = line + "{}".format(item)

        filterList = filters.split(",")
        for f in filterList:
            if f.lower() in line.lower():
                return True
        return False
