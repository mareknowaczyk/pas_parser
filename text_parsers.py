""" Line parsers

Classes and functions that improves text file processing.
The purpose of that parsers was to process text file like, sed, awk tools,
basing on regular expressions.

"""

import re


def lines_iterator(file_content):
    """File lines iterator

    :file_content: file contents

    """
    retval = ''
    line_idx = 0
    for char in file_content:
        retval += char if not char == '\n' else ''
        if char == '\n':
            yield (line_idx, retval)
            retval = ''
            line_idx+=1
    if retval:
        yield retval
    pass


class LineParser(object):

    """Single line parser"""

    def __init__(self, searchall_regex):
        """Initialization

        :searchall_regex: regular expression to search (re.searchall)

        """
        self._searchall_regex = searchall_regex
        self._regex = re.compile(self._searchall_regex)

    def _call_callback(self, callback, returned_value):
        if returned_value and callback:
            callback(returned_value)

    def parse(self, line, callback=None):
        """single line parsing

        :line: single pascal file line to parse
        :returns: tuple with searched groups
        :callback: callback function called with returned tupple as argument

        """
        res = self._regex.findall(line)
        self._call_callback(callback, res)
        return res          

class LineToStringParser(LineParser):
    """Parse line with single group regex, and output matched group as 'parse' result
    as string"""

    def __init__(self, searchall_regex):
        LineParser.__init__(self, searchall_regex)

    def parse(self, line, callback=None):
        res = super(LineToStringParser, self).parse(line)
        res = "" if not res else res[0]
        self._call_callback(callback, res)
        return res
       



