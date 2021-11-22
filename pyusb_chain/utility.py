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

import re
import logging
logger = logging.getLogger("pyusb_path")


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
