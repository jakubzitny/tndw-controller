#!/usr/local/bin/python3

from logics import Backing

parser = Backing()
retval = parser.parse()

print("Returned: " + str(retval));
