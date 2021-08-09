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

import json

import pytest
import sys
import os
import io
from sys import platform
import xml.etree.ElementTree as ET

sys.path.append("..")
from pyusb_chain.__main__ import USBDevicesChain
from pyusb_chain.usb_tree_view_tool import UsbTreeViewTool
from pyusb_chain.usb_device import USBDevice

CUR_PATH = os.path.dirname(os.path.abspath(__file__))


def test_commandline():
    sys.argv = ['.\\__main__.py', '-g', '-l', '-f', 'COM12', '-e', '-v debug']
    usbDevicesChain = USBDevicesChain()
    usbDevicesChain.command_process()
    if "win32" == platform:
        assert usbDevicesChain.args.gui
    assert usbDevicesChain.args.list
    assert usbDevicesChain.args.filter == 'COM12'
    assert usbDevicesChain.args.export


def test_export_xml():
    tool = UsbTreeViewTool()
    exportedFile = tool.export_xml()
    assert os.path.exists(exportedFile) == True
    with io.open(exportedFile, 'r', encoding='utf8') as f:
        lines = f.readlines()
        assert len(lines) > 0
    os.remove(exportedFile)


def test_usb_tree_parse():
    exportXMLFile = os.path.join(CUR_PATH, "export_test.xml")
    tool = UsbTreeViewTool()
    tool.parse(exportXMLFile)
    assert len(tool.usbDevices) == 12


def test_filter_data():
    exportXMLFile = os.path.join(CUR_PATH, "export_test.xml")
    tool = UsbTreeViewTool()
    tool.parse(exportXMLFile)
    devices = tool.filter("COM16")
    assert len(devices) == 1

    devices = tool.filter("Audio")
    assert len(devices) == 3

    devices = tool.filter("CP2102")
    assert len(devices) == 2


def test_export_json():
    exportXMLFile = os.path.join(CUR_PATH, "export_test.xml")
    tool = UsbTreeViewTool()
    tool.parse(exportXMLFile)
    USBDevicesChain.export_json(tool.usbDevices)
    jsonData = None
    with io.open(USBDevicesChain.EXPORT_JSON_NAME, 'r', encoding='utf8') as f:
        jsonData = json.loads(f.read())
    os.remove(USBDevicesChain.EXPORT_JSON_NAME)
    assert len(jsonData) == 20


def test_usb_device_get_values_location_info():
    # base USB device
    values = USBDevice.get_values(
        "\r\nService : silabser\r\nEnumerator : USB\r\nLocation Info : Port_#0002.Hub_#0008\r\nLocation IDs: PCIROOT\r\n",
        r"\r\nLocation Info\s*:\s*.*?\r\n", ["Location Info", ":"])
    assert len(values) == 1
    assert values[0] == "Port_#0002.Hub_#0008"


def test_usb_device_get_values_device_id():
    values = USBDevice.get_values(
        "\r\nKernel Name: \\Device\\USBPDO-24\r\nDevice ID  : USB\\VID_10C4&PID_EA60\\EVKMIMXRT1170_1_A\r\nHardware IDs : USB\\VID_10C4&PID_EA60&REV_0100 USB\\VID_10C4&PID_EA60",
        r"\r\nDevice ID\s*:\s*.*?\r\n", ["Device ID", ":"])
    assert len(values) == 1
    assert values[0] == "USB\\VID_10C4&PID_EA60\\EVKMIMXRT1170_1_A"


def test_usb_device_get_values_sn():
    # base USB device SN
    values = USBDevice.get_values(
        'iProduct: 0x02 (String Descriptor 2)\r\n Language 0x0409 : "CP2102 USB to UART Bridge"\r\niSerialNumber: 0x03 (String Descriptor 3)\r\n Language 0x0409         : "evkmimxrt1170_1_a"\r\nbNumConfigurations       : 0x01 (1 Configuration)"',
        r"\r\niSerialNumber.*?\r\n Language 0x0409\s*:\s*.*?\r\n",
        ["iSerialNumber.*?\r\n", "Language 0x0409", ":", "\""])
    assert len(values) == 1
    assert values[0] == "evkmimxrt1170_1_a"


def test_usb_device_get_values_comport():
    # Com port
    values = USBDevice.get_values(
        'Power State : D0 (supported: D0, D2, D3, wake from D0, wake from D2)\r\nCOM-Port : COM16 (\\Device\\Silabser0)\r\n',
        r"COM-Port\s*:\s*.*?\(", ["COM-Port", ":", r"\("])
    assert len(values) == 1
    assert values[0] == "COM16"


def test_usb_device_get_values_multi_comports():
    # multi com ports
    values = USBDevice.get_values(
        'Power State : D0 (supported: D0, D2, D3, wake from D0, wake from D2)\r\nCOM-Port : COM16 (\\Device\\Silabser0)\r\nService : FTSER2K\r\n  COM-Port: COM10 (\\Device\\VCP1)',
        r"COM-Port\s*:\s*.*?\(", ["COM-Port", ":", r"\("])
    assert len(values) == 2
    assert values[0] == "COM16"
    assert values[1] == "COM10"


def test_usb_device_get_values_audio():
    # audio playback
    values = USBDevice.get_values(
        ' Child Device 1        : Speakers (USB Audio Device) (Audio Endpoint)\r\n  Device ID \r\n',
        r"Child Device \d\s*:\s*.*?\(Audio Endpoint\)", [r"Child Device \d", ":", r"\(Audio Endpoint\)"])
    assert len(values) == 1
    assert values[0] == "Speakers (USB Audio Device)"

    values = USBDevice.get_values(
        ' Child Device 4        : Speakers (USB Audio Device) (Audio Endpoint)\r\n  Device ID \r\n',
        r"Child Device \d\s*:\s*.*?\(Audio Endpoint\)", [r"Child Device \d", ":", r"\(Audio Endpoint\)"])
    assert len(values) == 1
    assert values[0] == "Speakers (USB Audio Device)"

    # audio record
    values = USBDevice.get_values(
        ' Child Device 2        : Microphone (USB Audio Device) (Audio Endpoint)\r\n  Device ID \r\n',
        r"Child Device \d\s*:\s*.*?\(Audio Endpoint\)", [r"Child Device \d", ":", r"\(Audio Endpoint\)"])
    assert len(values) == 1
    assert values[0] == "Microphone (USB Audio Device)"

    # search class: Audio Endpoint, then get the Chide Device
    values = USBDevice.get_values(
        '\r\n Child Device 1 : Speakers_rt1050_b2b_hs0 (3- USB Audio Device)\r\n  Device ID \r\n Class : AudioEndpoint\r\nDriver KeyName\r\n\
        \r\n  Child Device 2        : Microphone (USB Audio Device) (Audio Endpoint)\r\n  Device ID \r\n Class : AudioEndpoint\r\n',
        r"\r\n\s+Child Device \d\s*:.*\s*Device ID.*?\s*Class\s*:\s*AudioEndpoint\s*")
    assert len(values) == 2
    valueSubs = USBDevice.get_values(values[0], r"Child Device \d\s*:\s*.*?\r\n\s*Device ID",
                                     [r"Child Device \d", ":", r"\(Audio Endpoint\)", "Device ID"])
    assert len(valueSubs) == 1
    assert valueSubs[0] == "Speakers_rt1050_b2b_hs0 (3- USB Audio Device)"

    valueSubs = USBDevice.get_values(values[1], r"Child Device \d\s*:\s*.*?\r\n\s*Device ID",
                                     [r"Child Device \d", ":", r"\(Audio Endpoint\)", "Device ID"])
    assert len(valueSubs) == 1
    assert valueSubs[0] == "Microphone (USB Audio Device)"


def test_usb_device_get_values_driver_key():
    # driver key
    values = USBDevice.get_values(
        'PID_6001\r\nDriver KeyName: {36fc9e60-c465-11cf-8056-444553540000}\\0027 (GUID_DEVCLASS_USB)\r\nDriver',
        r"\r\nDriver KeyName\s*:\s*.*?\(", ["Driver KeyName", ":", r"\(", r"\{.*\}", r"\\"])
    assert len(values) == 1
    assert values[0] == "0027"
    assert int(values[0]) == 27


def test_usb_device_parse():
    exportXMLFile = os.path.join(CUR_PATH, "export_test.xml")
    tool = UsbTreeViewTool()
    tool.parse(exportXMLFile)

    # serial port CP2102
    usbPortDevice = tool.usbDevices[8]
    assert usbPortDevice.deviceName == "Silicon Labs CP2102 USB to UART Bridge Controller - COM16"
    assert usbPortDevice.portChain == "1-7-5"
    assert usbPortDevice.locInfo == "Port_#0005.Hub_#0004"
    assert usbPortDevice.deviceID == "USB\\VID_10C4&PID_EA60\\0001"
    assert usbPortDevice.sn is None
    assert usbPortDevice.get_com_port() == "COM16"

    # CMSIS-DAP serial port
    usbPortDevice = tool.usbDevices[9]
    assert usbPortDevice.deviceName == "ARM mbed Composite Device - F:\\, COM18, HID"
    assert usbPortDevice.portChain == "1-7-6"
    assert usbPortDevice.locInfo == "Port_#0006.Hub_#0004"
    assert usbPortDevice.deviceID == "USB\\VID_0D28&PID_0204\\0205000047784E4500349004D917002AE561000097969900"
    assert usbPortDevice.sn == "0205000047784e4500349004d917002ae561000097969900"
    assert usbPortDevice.get_com_port() == "COM18"

    # multi serial ports IMX8
    usbPortDevice = tool.usbDevices[0]
    assert usbPortDevice.deviceName == "Future Devices International FTDI Quad RS232-HS - COM9, COM10, COM11, COM12"
    assert usbPortDevice.portChain == "1-3-1"
    assert usbPortDevice.locInfo == "Port_#0001.Hub_#0002"
    assert usbPortDevice.deviceID == "USB\\VID_0403&PID_6011\\6&2ED78AA8&0&1"
    assert usbPortDevice.sn is None
    assert usbPortDevice.get_com_port() == "COM9"
    assert usbPortDevice.get_com_port(1) == "COM10"
    assert usbPortDevice.get_com_port(2) == "COM11"
    assert usbPortDevice.get_com_port(3) == "COM12"

    # USB audio
    usbPortDevice = tool.usbDevices[4]
    assert usbPortDevice.deviceName == "C-Media USB Audio Device - Audio, HID"
    assert usbPortDevice.portChain == "1-3-7-3"
    assert usbPortDevice.locInfo == "Port_#0003.Hub_#0003"
    assert usbPortDevice.deviceID == "USB\\VID_0D8C&PID_0014\\7&B60E087&0&3"
    assert usbPortDevice.sn is None
    assert usbPortDevice.audioPlaybackName == "Speakers (USB Audio Device)"
    assert usbPortDevice.audioRecordName == "Microphone (USB Audio Device)"

    usbPortDevice = tool.usbDevices[5]
    assert usbPortDevice.deviceName == "C-Media USB Audio Device - Audio, HID"
    assert usbPortDevice.portChain == "1-3-7-4"
    assert usbPortDevice.locInfo == "Port_#0004.Hub_#0003"
    assert usbPortDevice.deviceID == "USB\\VID_0D8C&PID_0014\\7&B60E087&0&4"
    assert usbPortDevice.sn is None
    assert usbPortDevice.audioPlaybackName == "Speakers (4- USB Audio Device)"
    assert usbPortDevice.audioRecordName == "Microphone (4- USB Audio Device)"


def test_usb_tree_view_tool_get_device():
    exportXMLFile = os.path.join(CUR_PATH, "export_test.xml")
    tool = UsbTreeViewTool()
    tool.parse(exportXMLFile)

    # test get from sn
    device = tool.get_from_sn("123456789")
    assert device is None
    device = tool.get_from_sn(None)
    assert device is None

    device = tool.get_from_sn("0205000047784e4500349004d917002ae561000097969900")
    assert device.sn == "0205000047784e4500349004d917002ae561000097969900"
    assert device.portChain == "1-7-6"

    # test get from chain
    device = tool.get_from_chain("1-3-4")
    assert device is None
    device = tool.get_from_chain(None)
    assert device is None

    device = tool.get_from_chain("1-7-6")
    assert device.portChain == "1-7-6"
    assert device.sn == "0205000047784e4500349004d917002ae561000097969900"

    device = tool.get_from_chain("1-3-1:0")
    assert device.portChain == "1-3-1"
    assert device.get_com_port(0) == "COM9"
    assert device.get_key("COM9") == "1-3-1:0"

    device = tool.get_from_chain("1-3-1:3")
    assert device.portChain == "1-3-1"
    assert device.get_com_port(3) == "COM12"
    assert device.get_key("COM12") == "1-3-1:3"

    device = tool.get_from_chain("1-3-7-4:Speaker")
    assert device.portChain == "1-3-7-4"
    assert device.get_key("Speakers (4- USB Audio Device)") == "1-3-7-4:Speaker"
    assert device.audioPlaybackName == "Speakers (4- USB Audio Device)"
    assert device.audioRecordName == "Microphone (4- USB Audio Device)"

    device = tool.get_from_chain("1-3-7-4:Microphone")
    assert device.portChain == "1-3-7-4"
    assert device.get_key("Microphone (4- USB Audio Device)") == "1-3-7-4:Microphone"
    assert device.audioPlaybackName == "Speakers (4- USB Audio Device)"
    assert device.audioRecordName == "Microphone (4- USB Audio Device)"

    # test get from port
    device = tool.get_from_port("COM121")
    assert device is None
    device = tool.get_from_port(None)
    assert device is None

    device = tool.get_from_port("COM12")
    assert device.portChain == "1-3-1"
    assert device.get_key("COM12") == "1-3-1:3"

    device = tool.get_from_port("Speakers (4- USB Audio Device)")
    assert device.portChain == "1-3-7-4"
    assert device.get_key("Speakers (4- USB Audio Device)") == "1-3-7-4:Speaker"
    assert device.audioPlaybackName == "Speakers (4- USB Audio Device)"
    assert device.audioRecordName == "Microphone (4- USB Audio Device)"


def test_usb_tree_view_tool_covert():
    exportXMLFile = os.path.join(CUR_PATH, "export_test.xml")
    tool = UsbTreeViewTool()
    tool.parse(exportXMLFile)

    assert tool.get_chain_from_port("COM16") == "1-7-5"
    assert tool.get_port_from_chain("1-7-5") == "COM16"
    assert tool.get_chain_from_port("COM18") == "1-7-6"
    assert tool.get_port_from_chain("1-7-6") == "COM18"
    assert tool.get_chain_from_port("COM9") == "1-3-1:0"
    assert tool.get_port_from_chain("1-3-1:0") == "COM9"
    assert tool.get_chain_from_port("COM9") == "1-3-1:0"
    assert tool.get_chain_from_port("COM12") == "1-3-1:3"
    assert tool.get_port_from_chain("1-3-1:3") == "COM12"
    assert tool.get_chain_from_port("Speakers (4- USB Audio Device)") == "1-3-7-4:Speaker"
    assert tool.get_port_from_chain("1-3-7-4:Speaker") == "Speakers (4- USB Audio Device)"
    assert tool.get_chain_from_port("Microphone (4- USB Audio Device)") == "1-3-7-4:Microphone"
    assert tool.get_port_from_chain("1-3-7-4:Microphone") == "Microphone (4- USB Audio Device)"
