#!/usr/local/bin/python3

from logic.version import Version

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from multiprocessing import Process, Queue, Lock
import lxml.html
import re, os, sys
import urllib

class SDParser():

	url = "http://www.chrishaney.com/?linux"
	version_jobs = Queue()
	distro_jobs = Queue()
	l = Lock()

	def __init__(self):
		self.db = create_engine('postgres://postgres:root@localhost/sdparser')

	def parse(self):
		return "asd"

	def parses(self):
		root_index = lxml.html.parse(self.url)
		distros_raw = root_index.xpath('//select[@name="distro"]')[0]
		distros = []
		
		print('Found ' + str(len(distros_raw)) + ' distros..')
		for distro in distros_raw:
			distros.append(distro.attrib["value"])
		
		del distros[0]
		self.handleDistros(distros)

	def handleDistros(self, distros):
		directory = 'directory'
		if not os.path.exists(directory):
			os.mkdir(directory)
		os.chdir(directory)
		for distro in distros:
			self.handleDistro(distro)
			#break

	def handleDistro(self, distro):
		root_distro = lxml.html.parse(self.url + '=&distro=' + distro)
		distro_versions_raw = root_distro.xpath('//table/tr/td/a')
		distro_versions = []

		print(distro + ": ")
		cwd = os.getcwd()
		if not os.path.exists(distro):
			os.mkdir(distro)
		os.chdir(distro)

		for distro_version in distro_versions_raw:
			version_raw = distro_version.attrib["href"]
			if(re.search('release', version_raw)):
				version = version_raw[15:]
				distro_versions.append(version)
		self.handleVersions(distro_versions, distro)
		os.chdir('..')

	def handleVersions(self, versions, distro):
		self.handleVersionsSequential(versions, distro)
		#self.handleVersionsParallel(versions, distro)

	def handleVersionsSequential(self, versions, distro):
		for version in versions:
			self.handleVersion([version, distro])

	def handleVersionsParallel(self, versions, distro):
		processes = []
		pc = 0
		prod = Process(target=self.handleVersionsProducent, args=([versions, distro]))
		prod.start()
		processCount = 12
		for i in range(processCount):
			p = Process(target=self.handleVersionWorker, args=())
			processes.append(p)
			p.start()

		for p in processes:
			p.join()
		prod.join()

	def handleVersionsProducent(self, versions, distro):
		for version in versions:
			self.jobs.put([version, distro])

	def handleVersionWorker(self):
		while(True):
			self.l.acquire()
			if (self.jobs.empty()):
				self.l.release()
				break
			self.handleVersion(self.jobs.get_nowait())
			self.l.release()
		

	def handleVersion(self, args):
		#version = re.sub(r' ', '%20', version_raw[15:])
		version,distro = args
		version_str = re.sub(r' ', '%20', version) 
		x = Version(version, self.url + '&release=' + version, distro)

		print("-- " + version)
		version_root = lxml.html.parse(self.url + '&release=' + version)
		version_raw = version_root.xpath('/html/body/div/form/div/div/descendant-or-self::*/img')
		
		screenshots = []
		
		for shot in version_raw:
			screenshots.append('http://www.chrishaney.com/screenshots/scaled/' + version_str + '/' + shot.attrib["src"].split('/')[-1])

		if not os.path.exists(version_str):
			os.mkdir(version_str)
		os.chdir(version_str)
		
		for shot in screenshots:
			if shot.split('/')[-1] not in os.listdir('.'):
				try:
					urllib.request.urlretrieve(shot, shot.split('/')[-1])
				except urllib.URLError:
					pass

		os.chdir('..')

		db = create_engine('postgres://postgres:root@localhost/sdparser')
		Session = sessionmaker(bind=db)
		session = Session()
		session.add(x)
		session.commit()
		session.close()



