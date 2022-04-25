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

sys.path.append("..")
from pyusb_chain.__main__ import USBDevicesChain
from pyusb_chain.usb_tree_view_tool import UsbTreeViewTool
from pyusb_chain.utility import get_values

CUR_PATH = os.path.dirname(os.path.abspath(__file__))


def test_commandline():
    if "win32" == platform:
        sys.argv = ['.\\__main__.py', '-g', '-l', '-f', 'COM12', '-e', '-v debug']
    else:
        sys.argv = ['.\\__main__.py', '-l', '-f', 'COM12', '-e', '-v debug']
    usbDevicesChain = USBDevicesChain()
    usbDevicesChain.command_process()
    if "win32" == platform:
        assert usbDevicesChain.args.gui
    assert usbDevicesChain.args.list
    assert usbDevicesChain.args.filter == 'COM12'
    assert usbDevicesChain.args.export


@pytest.mark.skipif('win32' != platform, reason="requires the windows os")
def test_export_xml():
    tool = UsbTreeViewTool()
    exportedFile = tool.export_xml()
    assert os.path.exists(exportedFile) == True
    with io.open(exportedFile, 'r', encoding='utf8') as f:
        lines = f.readlines()
        assert len(lines) > 0
    os.remove(exportedFile)


@pytest.mark.skipif('win32' != platform, reason="requires the windows os")
def test_usb_tree_parse():
    exportXMLFile = os.path.join(CUR_PATH, "export_test.xml")
    tool = UsbTreeViewTool()
    tool.parse(exportXMLFile)
    assert len(tool.usbDevices) == 15


def test_filter_data():
    tool = UsbTreeViewTool()
    if "win32" == platform:
        exportXMLFile = os.path.join(CUR_PATH, "export_test.xml")
        tool.parse(exportXMLFile)
        devices = tool.filter("COM16")
        assert len(devices) == 1

        devices = tool.filter("Audio")
        assert len(devices) == 4

        devices = tool.filter("CP2102")
        assert len(devices) == 2
    else:
        tool.parse_linux()
        devices = tool.filter("tty")
        assert len(devices) > 1
        # for linux, so far, only support VCOM
        devices = tool.filter("Audio")
        assert len(devices) == 0


def test_export_json():
    exportXMLFile = os.path.join(CUR_PATH, "export_test.xml")
    tool = UsbTreeViewTool()
    if "win32" == platform:
        tool.parse(exportXMLFile)
    else:
        tool.parse_linux()
    USBDevicesChain.export_json(tool.usbDevices)
    jsonData = None
    with io.open(USBDevicesChain.EXPORT_JSON_NAME, 'r', encoding='utf8') as f:
        jsonData = json.loads(f.read())
    os.remove(USBDevicesChain.EXPORT_JSON_NAME)
    if "win32" == platform:
        assert len(jsonData) == 25
    else:
        assert len(jsonData) > 1


def test_export_printtable():
    exportXMLFile = os.path.join(CUR_PATH, "export_test.xml")
    tool = UsbTreeViewTool()
    if "win32" == platform:
        tool.parse(exportXMLFile)
    else:
        tool.parse_linux()
    devices = tool.filter(None)
    if "win32" == platform:
        assert len(devices) == 15
    else:
        assert len(devices) > 1

    # COMPortDevice
    data = devices[0].export_data(True, jsonFormat=False)
    assert data[0][0] == '1-3-1:0'
    assert data[0][1] == 'COM9'
    assert data[0][2] == 'Future Devices International FTDI Quad RS232-HS - COM9, COM10, COM11, COM12'
    assert data[0][4] == 13
    assert data[3][0] == '1-3-1:3'
    assert data[3][1] == 'COM12'
    assert data[1][2] == 'Future Devices International FTDI Quad RS232-HS - COM9, COM10, COM11, COM12'
    assert data[3][4] == 13

    data = devices[3].export_data(True, jsonFormat=False)
    assert data[0][0] == '1-3-7-2'
    assert data[0][1] == 'COM17'
    assert data[0][2] == 'ARM mbed Composite Device - E:\\, COM17, HID'
    assert data[0][3] == '0229000012979c5b00000000000000000000000097969905'
    assert data[0][4] == 5

    # AudioDevice
    data = devices[4].export_data(True, jsonFormat=False)
    assert data[0][0] == '1-3-7-3:Speaker'
    assert data[0][1] == 'Speakers (USB Audio Device)'
    assert data[0][2] == 'C-Media USB Audio Device - Audio, HID'
    assert data[0][4] == 34
    assert data[1][0] == '1-3-7-3:Microphone'
    assert data[1][1] == 'Microphone (USB Audio Device)'
    assert data[1][2] == 'C-Media USB Audio Device - Audio, HID'
    assert data[1][4] == 34

    # AudioCOMPortDevice
    data = devices[12].export_data(True, jsonFormat=False)
    assert data[0][0] == '1-24-1:Speaker'
    assert data[0][1] == 'Speakers (4- USB AUDIO+CDC DEMO)'
    assert data[0][2] == 'USB Composite Device - COM23'
    assert data[0][4] == 62
    assert data[1][0] == '1-24-1:Microphone'
    assert data[1][1] == 'Microphone (4- USB AUDIO+CDC DEMO)'
    assert data[1][2] == 'USB Composite Device - COM23'
    assert data[1][4] == 62
    assert data[2][0] == '1-24-1:COM23'
    assert data[2][1] == 'COM23'
    assert data[2][2] == 'USB Composite Device - COM23'
    assert data[2][4] == 62

    # USBDevice
    data = devices[6].export_data(True, jsonFormat=False)
    assert data[0][0] == '1-4'
    assert data[0][1] == ''
    assert data[0][2] == 'ASIX Elec AX88772C'
    assert data[0][4] == 11


@pytest.mark.skipif('win32' != platform, reason="requires the windows os")
def test_usb_device_get_values_location_info():
    # base USB device
    values = get_values(
        "\r\nService : silabser\r\nEnumerator : USB\r\nLocation Info : Port_#0002.Hub_#0008\r\nLocation IDs: PCIROOT\r\n",
        r"\r\nLocation Info\s*:\s*.*?\r\n", ["Location Info", ":"])
    assert len(values) == 1
    assert values[0] == "Port_#0002.Hub_#0008"


@pytest.mark.skipif('win32' != platform, reason="requires the windows os")
def test_usb_device_get_values_device_id():
    values = get_values(
        "\r\nKernel Name: \\Device\\USBPDO-24\r\nDevice ID  : USB\\VID_10C4&PID_EA60\\EVKMIMXRT1170_1_A\r\nHardware IDs : USB\\VID_10C4&PID_EA60&REV_0100 USB\\VID_10C4&PID_EA60",
        r"\r\nDevice ID\s*:\s*.*?\r\n", ["Device ID", ":"])
    assert len(values) == 1
    assert values[0] == "USB\\VID_10C4&PID_EA60\\EVKMIMXRT1170_1_A"


@pytest.mark.skipif('win32' != platform, reason="requires the windows os")
def test_usb_device_get_values_sn():
    # base USB device SN
    values = get_values(
        'iProduct: 0x02 (String Descriptor 2)\r\n Language 0x0409 : "CP2102 USB to UART Bridge"\r\niSerialNumber: 0x03 (String Descriptor 3)\r\n Language 0x0409         : "evkmimxrt1170_1_a"\r\nbNumConfigurations       : 0x01 (1 Configuration)"',
        r"\r\niSerialNumber.*?\r\n Language 0x0409\s*:\s*.*?\r\n",
        ["iSerialNumber.*?\r\n", "Language 0x0409", ":", "\""])
    assert len(values) == 1
    assert values[0] == "evkmimxrt1170_1_a"


@pytest.mark.skipif('win32' != platform, reason="requires the windows os")
def test_usb_device_get_values_comport():
    # Com port
    values = get_values(
        'Power State : D0 (supported: D0, D2, D3, wake from D0, wake from D2)\r\nCOM-Port : COM16 (\\Device\\Silabser0)\r\n',
        r"COM-Port\s*:\s*.*?\(", ["COM-Port", ":", r"\("])
    assert len(values) == 1
    assert values[0] == "COM16"


@pytest.mark.skipif('win32' != platform, reason="requires the windows os")
def test_usb_device_get_values_multi_comports():
    # multi com ports
    values = get_values(
        'Power State : D0 (supported: D0, D2, D3, wake from D0, wake from D2)\r\nCOM-Port : COM16 (\\Device\\Silabser0)\r\nService : FTSER2K\r\n  COM-Port: COM10 (\\Device\\VCP1)',
        r"COM-Port\s*:\s*.*?\(", ["COM-Port", ":", r"\("])
    assert len(values) == 2
    assert values[0] == "COM16"
    assert values[1] == "COM10"


@pytest.mark.skipif('win32' != platform, reason="requires the windows os")
def test_usb_device_get_values_audio():
    # audio playback
    values = get_values(
        ' Child Device 1        : Speakers (USB Audio Device) (Audio Endpoint)\r\n  Device ID \r\n',
        r"Child Device \d\s*:\s*.*?\(Audio Endpoint\)", [r"Child Device \d", ":", r"\(Audio Endpoint\)"])
    assert len(values) == 1
    assert values[0] == "Speakers (USB Audio Device)"

    values = get_values(
        ' Child Device 4        : Speakers (USB Audio Device) (Audio Endpoint)\r\n  Device ID \r\n',
        r"Child Device \d\s*:\s*.*?\(Audio Endpoint\)", [r"Child Device \d", ":", r"\(Audio Endpoint\)"])
    assert len(values) == 1
    assert values[0] == "Speakers (USB Audio Device)"

    # audio record
    values = get_values(
        ' Child Device 2        : Microphone (USB Audio Device) (Audio Endpoint)\r\n  Device ID \r\n',
        r"Child Device \d\s*:\s*.*?\(Audio Endpoint\)", [r"Child Device \d", ":", r"\(Audio Endpoint\)"])
    assert len(values) == 1
    assert values[0] == "Microphone (USB Audio Device)"

    # search class: Audio Endpoint, then get the Chide Device
    values = get_values(
        '\r\n Child Device 1 : Speakers_rt1050_b2b_hs0 (3- USB Audio Device)\r\n  Device ID \r\n Class : AudioEndpoint\r\nDriver KeyName\r\n\
        \r\n  Child Device 2        : Microphone (USB Audio Device) (Audio Endpoint)\r\n  Device ID \r\n Class : AudioEndpoint\r\n',
        r"\r\n\s+Child Device \d\s*:.*\s*Device ID.*?\s*Class\s*:\s*AudioEndpoint\s*")
    assert len(values) == 2
    valueSubs = get_values(values[0], r"Child Device \d\s*:\s*.*?\r\n\s*Device ID",
                                     [r"Child Device \d", ":", r"\(Audio Endpoint\)", "Device ID"])
    assert len(valueSubs) == 1
    assert valueSubs[0] == "Speakers_rt1050_b2b_hs0 (3- USB Audio Device)"

    valueSubs = get_values(values[1], r"Child Device \d\s*:\s*.*?\r\n\s*Device ID",
                                     [r"Child Device \d", ":", r"\(Audio Endpoint\)", "Device ID"])
    assert len(valueSubs) == 1
    assert valueSubs[0] == "Microphone (USB Audio Device)"


@pytest.mark.skipif('win32' != platform, reason="requires the windows os")
def test_usb_device_get_values_driver_key():
    # driver key
    values = get_values(
        'PID_6001\r\nDriver KeyName: {36fc9e60-c465-11cf-8056-444553540000}\\0027 (GUID_DEVCLASS_USB)\r\nDriver',
        r"\r\nDriver KeyName\s*:\s*.*?\(", ["Driver KeyName", ":", r"\(", r"\{.*\}", r"\\"])
    assert len(values) == 1
    assert values[0] == "0027"
    assert int(values[0]) == 27


@pytest.mark.skipif('win32' != platform, reason="requires the windows os")
def test_usb_tree_get_vid_pid():
    exportXMLFile = os.path.join(CUR_PATH, "export_test.xml")
    tool = UsbTreeViewTool()
    tool.load(exportXMLFile)

    info = tool.root[0][1][1][26][0].text
    vid, pid = UsbTreeViewTool.get_vid_pid(info)
    assert vid == UsbTreeViewTool.VID_DSC_FSL_MC56
    assert pid == UsbTreeViewTool.PID_DSC_FSL_MC56


def test_usb_device_parse():
    if "win32" == platform:
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

        usbPortDevice = tool.usbDevices[12]
        assert usbPortDevice.deviceName == "USB Composite Device - COM23"
        assert usbPortDevice.portChain == "1-24-1"
        assert usbPortDevice.locInfo == "Port_#0001.Hub_#0008"
        assert usbPortDevice.deviceID == "USB\\VID_1FC9&PID_00A6\\6&4180336&0&1"
        assert usbPortDevice.sn is None
        assert usbPortDevice.audioPlaybackName == "Speakers (4- USB AUDIO+CDC DEMO)"
        assert usbPortDevice.audioRecordName == "Microphone (4- USB AUDIO+CDC DEMO)"
        assert usbPortDevice.get_com_port() == "COM23"

        usbPortDevice = tool.usbDevices[13]
        assert "[USB1]" in usbPortDevice.deviceName

        usbPortDevice = tool.usbDevices[14]
        assert "[USB2]" in usbPortDevice.deviceName
    else:
        tool = UsbTreeViewTool()
        tool.parse_linux()
        assert len(tool.usbDevices) > 1
        usbPortDevice = tool.usbDevices[0]
        assert len(usbPortDevice.deviceName) > 1
        assert len(usbPortDevice.portChain) > 1
        assert len(usbPortDevice.locInfo) > 1
        assert len(usbPortDevice.deviceID) > 1
        assert "tty" in usbPortDevice.get_com_port()


@pytest.mark.skipif('win32' != platform, reason="requires the windows os")
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

    device = tool.get_from_port("Speakers (4- USB AUDIO+CDC DEMO)")
    assert device.portChain == "1-24-1"
    assert device.audioPlaybackName == "Speakers (4- USB AUDIO+CDC DEMO)"
    assert device.audioRecordName == "Microphone (4- USB AUDIO+CDC DEMO)"
    assert device.get_com_port() == "COM23"
    assert device.get_key("COM23") == "1-24-1:COM23"
    assert device.get_key("Speaker") == "1-24-1:Speaker"
    assert device.get_key("Microphone") == "1-24-1:Microphone"
    assert tool.get_from_port("COM23") == device


@pytest.mark.skipif('win32' != platform, reason="requires the windows os")
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
    assert tool.get_chain_from_port("COM23") == "1-24-1:COM23"
    assert tool.get_port_from_chain("1-24-1:COM") == "COM23"
    assert tool.get_chain_from_port("Speakers (4- USB AUDIO+CDC DEMO)") == "1-24-1:Speaker"
    assert tool.get_port_from_chain("1-24-1:Speaker") == "Speakers (4- USB AUDIO+CDC DEMO)"
    assert tool.get_chain_from_port("Microphone (4- USB AUDIO+CDC DEMO)") == "1-24-1:Microphone"
    assert tool.get_port_from_chain("1-24-1:Microphone") == "Microphone (4- USB AUDIO+CDC DEMO)"
