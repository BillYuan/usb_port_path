# pyusb-chain
Support command line interface to get the port chain of USB devices(serial, audio, .etc) based on UsbDeviceTreeView.exe in windows.


## Installation
The easiest (and best) way to install pyusb-chain is through pip:

```pip install pyusb-chain```

Sources packages are also available at git hub:

https://github.com/BillYuan/usb_port_path

## Quickstart
The API to use pyusb_chain to map between port chain and port name.

```

from pyusb_chain.usb_tree_view_tool import UsbTreeViewTool

tool = UsbTreeViewTool()
tool.scan()  # scan first to get the latest USB devices information

# to get the port chain by COM port
portChain = tool.get_chain_from_port("COM16")  # "1-7-5" or "1-3-1:2" if there are multi-com ports in one USB device 

# to get the port chain by Audio Name
portChain = too.get_chain_from_port("Speakers (4- USB Audio Device)")  # "1-3-7-4:Speaker"
portChain = too.get_chain_from_port("Microphone (4- USB Audio Device)")  # "1-3-7-4:Microphone"


# to get port name by the port chain
portName = tool.get_port_from_chain("1-7-5")  # "COM16"
portName = tool.get_port_from_chain("1-3-1:2")  # "COM11"
portName = tool.get_port_from_chain("1-3-7-4:Speaker")  # "Speakers (4- USB Audio Device)"
portName = tool.get_port_from_chain("1-3-7-4:Microphone")  # "Microphone (4- USB Audio Device)"

```

Support command line standalone usage

```
usage: __main__.py [-h] [-g] [-l] [-a] [-f FILTER] [-e] [-v VERBOSE]

Command line for port path of USB devices (COM ports / Audio Devices)
Version:0.1.3

optional arguments:
  -h, --help            show this help message and exit
  -g, --gui             Launch GUI of USBTreeViewer.exe in Windows system
  -l, --list            List all USB devices information for COM ports and USB
                        Audio devices
  -a, --allinfo         List all information of USB device, include SN and
                        driver key
  -f FILTER, --filter FILTER
                        filter the key words of USB devices information
  -e, --export          export the json format with all connected USB devices
                        information
  -v VERBOSE, --verbose VERBOSE
                        verbose log mode, 'debug', 'fatal', 'error',
                        'warning', 'info'
```

For example,
1. List all devices: ```>pyusb-chain --list --allinfo```
```
Scanning all USB devices...


Port Chain Key    Port Name                       Device Name                                     SN                                                  Driver Key
----------------  ------------------------------  ----------------------------------------------  ------------------------------------------------  ------------
2-1-1                                             Altera USB-Blaster                              8a56TRPS                                                    28
2-1-5:Speaker     Headphones (Realtek USB Audio)  USB Composite Device - Realtek USB Audio        200901010001                                                 8
2-1-6                                             USB Composite Device - 2× Keyboard, 2× HID                                                                   9
2-1-7-3-2         COM16                           Silicon Labs CP210x USB to UART Bridge (COM16)  evkmimxrt1170_1_a                                           14
2-1-7-3-3         COM3                            mbed Composite Device - D:\, COM3, HID          022900001294098900000000000000000000000097969905            17
2-1-7-4-1         COM109                          USB-SERIAL CH340 (COM109)                                                                                   16
2-1-7-4-4                                         USB Input Device - Mouse                                                                                     7
2-1-7-7-1                                         Altera USB-Blaster                              8a56TQ1M                                                    27
2-1-7-7-3         COM11                           USB Composite Device - COM11, E:\               SDAF7507E73                                                 18
2-3-2                                             Realtek USB GbE Family Controller               000002000000                                                 7
3-2                                               Altera USB-Blaster                              8B951BA7                                                    26
3-5                                               USB Composite Device - Camera                                                                                7
3-7                                               Intel(R) Wireless Bluetooth(R) - Media, HID                                                                  0
3-10                                              USB Composite Device                                                                                         6
```

2. Add filter to only list devices you required: ```>pyusb-chain --list Altera --allinfo```
````
Port Chain Key    Port Name    Device Name         SN          Driver Key
----------------  -----------  ------------------  --------  ------------
2-1-1                          Altera USB-Blaster  8a56TRPS            28
2-1-7-7-1                      Altera USB-Blaster  8a56TQ1M            27
3-2                            Altera USB-Blaster  8B951BA7            26
````

3. Export to the json file for all listed devices: ```>pyusb-chain --list Altera --export```

````
Please get 'usb_port_chain_export.json' for dumped information!
````

```` 
{
    "2-1-1": {
        "Port Name": "",
        "Device Name": "Altera USB-Blaster",
        "SN": "8a56TRPS",
        "Location Info": "Port_#0001.Hub_#0004",
        "Device ID": "USB\\VID_09FB&PID_6001\\8A56TRPS",
        "Driver Key": 28
    },
    "2-1-7-7-1": {
        "Port Name": "",
        "Device Name": "Altera USB-Blaster",
        "SN": "8a56TQ1M",
        "Location Info": "Port_#0001.Hub_#0011",
        "Device ID": "USB\\VID_09FB&PID_6001\\8A56TQ1M",
        "Driver Key": 27
    },
    "3-2": {
        "Port Name": "",
        "Device Name": "Altera USB-Blaster",
        "SN": "8B951BA7",
        "Location Info": "Port_#0002.Hub_#0001",
        "Device ID": "USB\\VID_09FB&PID_6001\\8B951BA7",
        "Driver Key": 26
    }
}
````
