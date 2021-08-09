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
from setuptools import setup, find_packages

version = '0.2.0'

install_requires = [
    'tabulate'
]

version_file = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'pyusb_chain/_version.py')

try:
    with open(version_file, 'w') as f:
        f.write("VERSION='%s'" % version)
except Exception as e:
    print(e)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pyusb-chain",
    version=version,
    url='https://github.com/BillYuan/usb_port_path',
    description="Tool to map usb device port chain and port name",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Bill Yuan",
    author_email="bill.yuan@qq.com",
    license="MIT License",
    install_requires=install_requires,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pyusb-chain = pyusb_chain.__main__:main',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9"
    ],
)
