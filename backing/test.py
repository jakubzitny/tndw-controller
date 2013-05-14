#!/usr/local/bin/python3

from models import Test

class Test():

	def parse(self):
		t = Test(name="aaaaaaaasd", type="yxc")
		t.save()
		return t.name
