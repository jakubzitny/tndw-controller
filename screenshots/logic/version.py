#!/usr/local/bin/python3

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Version(Base):
	__tablename__ = 'versions'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	link = Column(String)
	distro = Column(String)

	def __init__(self, name, link, distro):
		self.name = name
		self.link = link
		self.distro = distro

	def show(self):
		print(self.name)

db = create_engine('postgres://postgres:root@localhost/sdparser')
Base.metadata.drop_all(db)
Base.metadata.create_all(db) 
