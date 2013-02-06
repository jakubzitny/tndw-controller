#!/usr/local/bin/python3

from screenshot import *
from SDParser import *
import signal, os, sys, traceback


if __name__ == "__main__":
	parser=SDParser()
	try:
		print(parser.parse())
	except KeyboardInterrupt:
		print("Shutdown requested...exiting")
	except Exception:
		traceback.print_exc(file=sys.stdout)
		sys.exit(1)
