#!/usr/local/bin/python3

class Screenshot(object):
	""" Screenshot object """

	def __init__(self, filename, link):
		self._filename = filename

	@property
	def filename(self):
		return self._filename

	@filename.setter
	def setFilename(self):
		self._filename = filename

	#filename = property(getFilename, setFilename, delFilename, "screenshot filename")
