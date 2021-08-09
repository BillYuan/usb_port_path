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

import argparse
import logging
import sys
import io
import json
from sys import platform
from tabulate import tabulate
from pyusb_chain.usb_tree_view_tool import UsbTreeViewTool
from pyusb_chain._version import VERSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyusb_path")


class USBDevicesChain(object):
    """Command line interface to list or search all connected USB devices.
    It implements the table print and export json features.
    """
    EXPORT_JSON_NAME = "usb_port_chain_export.json"

    def __init__(self):
        self.args = None
        pass

    def command_process(self):
        """Process command line
        :return: None
        """
        parser = argparse.ArgumentParser(description="Command line for port path of USB devices "
                                                     "(COM ports / Audio Devices)\r\nVersion:{}".format(VERSION))
        if "win32" == platform:
            parser.add_argument("-g", "--gui", action="store_true", default=False, dest="gui",
                help="Launch GUI of USBTreeViewer.exe in Windows system")
        parser.add_argument("-l", "--list", action="store_true", default=False, dest="list",
            help="List all USB devices information for COM ports and USB Audio devices")
        parser.add_argument("-a", "--allinfo", action="store_true", default=False, dest="allinfo",
            help="List all information of USB device, include SN and driver key")
        parser.add_argument("-f", "--filter", action="store", dest="filter",
            help="filter the key words of USB devices information")
        parser.add_argument("-e", "--export", action="store_true", default=False, dest="export",
            help="export the json format with all connected USB devices information")
        parser.add_argument("-v", "--verbose", action="store", dest="verbose",
            help="verbose log mode, 'debug', 'fatal', 'error', 'warning', 'info'")

        self.args = parser.parse_args()
        # enable all info log first if there is -v
        if self.args.verbose:
            v = self.args.verbose.lower()
            if "debug" == v:
                logger.setLevel(logging.DEBUG)
            elif "fatal" == v:
                logger.setLevel(logging.FATAL)
            elif "error" == v:
                logger.setLevel(logging.ERROR)
            elif "warning" == v:
                logger.setLevel(logging.WARNING)
            elif "info" == v:
                logger.setLevel(logging.INFO)

        logger.debug(sys.argv)
        logger.debug(self.args)

        if not self.args.list and not self.args.filter and not self.args.export:
            if "win32" == platform:
                if not self.args.gui:
                    parser.print_help()
            else:
                parser.print_help()

    def process(self):
        """Process the action, start gui or list or export the json with filter options
        :return: None
        """
        tool = UsbTreeViewTool()
        if hasattr(self.args, "gui") and self.args.gui:
            tool.start_gui()
        elif self.args.list or self.args.filter or self.args.export:
            tool.scan()

        if self.args.list or self.args.filter:
            devices = tool.filter(self.args.filter)
            data = []
            headers = ["Port Chain Key", "Port Name", "Device Name"]
            if self.args.allinfo:
                headers.append("SN")
                headers.append("Driver Key")
            for device in devices:
                data = data + device.export_data(self.args.allinfo, jsonFormat=False)
            print("\r\n")
            print(tabulate(data, headers=headers))

        if self.args.export:
            devices = tool.filter(self.args.filter)
            USBDevicesChain.export_json(devices)

    @staticmethod
    def export_json(usbDevices):
        """Export json format file for information of usb devices
        :param usbDevices: the exported usb devices
        :return: None (a json file will be saved in user command line path)
        """
        data = {}
        try:
            for device in usbDevices:
                data.update(device.export_data(jsonFormat=True))
            with io.open(USBDevicesChain.EXPORT_JSON_NAME, 'w', encoding='utf-8') as fobj:
                if sys.version_info[0] <= 2:
                    fobj.write(unicode(json.dumps(data, ensure_ascii=False, indent=4)))
                else:
                    json.dump(data, fobj, indent=4)
            print("\nPlease get '{}' for dumped information!\n".format(USBDevicesChain.EXPORT_JSON_NAME))
        except Exception:
            logger.exception("Fail to save json file ''{}'".format(USBDevicesChain.EXPORT_JSON_NAME))


def main():
    if platform != "win32":
        print("\nSorry, the pyusb-chain has not supported Linux/Mac OS!")
        return

    usbDevicesChain = USBDevicesChain()
    usbDevicesChain.command_process()
    usbDevicesChain.process()


if __name__ == "__main__":
    main()
