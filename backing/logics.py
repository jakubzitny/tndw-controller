# Logics file providing backing up from DW

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from multiprocessing import Process, Queue, Lock
import requests
import lxml.html
import re, os, sys
import urllib
from time import sleep

class Backing():

	url = "http://distrowatch.com/search.php"
	dbtable = "backing_distros"
	distro_jobs = Queue()
	l = Lock()

	def parse(self):
		#cnt = self.processDistros(self.getList())
		cnt = 0
		return cnt

	def getList(self):
		try:
			root_index = requests.post(self.url, {'status[]': 'All'})
		except Exception:
			print("Not connected.")
			return []

		root_index_html = lxml.html.fromstring(root_index.text)
		regexpNS = "http://exslt.org/regular-expressions"
		distros_raw = root_index_html.xpath('//td[@class="NewsText"]/b/a', namespaces={'re':regexpNS})

		distro_list = []
		for distro in distros_raw:
			link = distro.attrib["href"]
			if (link == "dwres.php?resource=popularity"):
				continue
			distro_list.append(link)

		return distro_list

	def processDistros(self, distro_list):
		processes = []
		pc = 0
		processCount = 12

		# produce
		for distro in distro_list:
			self.distro_jobs.put("http://distrowatch.com/table.php?distribution=" + distro)
			#break # DEBUG
		
		for i in range(processCount):
			p = Process(target=self.processDistroWorker, args=())
			processes.append(p)
			p.start()

		for p in processes:
			p.join()
		return len(distro_list)

	def processDistroWorker(self):
		while(True):
			self.l.acquire()
			if (self.distro_jobs.empty()):
				self.l.release()
				break
			self.processDistro(self.distro_jobs.get_nowait())
			self.l.release()

	def processDistro(self, distro_url):
		distro_index = lxml.html.parse(distro_url)
		
		# TablesTitle div
		title = distro_index.xpath('//td[@class="TablesTitle"]/h1//text()')[0]
		ostype_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[1]//text()')
		ostype = ''.join(ostype_raw[2:])
		basedon_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[2]//text()')
		basedon = re.sub('^ ', '', ''.join(basedon_raw[1:]))
		origin_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[3]//text()')
		origin = re.sub('\n', '', re.sub('^ ', '', ''.join(origin_raw[1:])))
		arch_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[4]//text()')
		arch = re.sub('^ ', '', ''.join(arch_raw[1:]))
		desktop_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[5]//text()')
		desktop = re.sub('^ ', '', ''.join(desktop_raw[1:]))
		category_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[6]//text()')
		category = re.sub('^ ', '', ''.join(category_raw[1:]))
		category_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[6]//text()')
		category = re.sub('^ ', '', ''.join(category_raw[1:]))
		status_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[7]//text()')
		status = re.sub('^ ', '', ''.join(status_raw[1:]))

		# description
		desc_raw = distro_index.xpath('//td[@class="TablesTitle"]//text()')
		pos = 0
		for substr in desc_raw:
			if(substr == 'Popularity (page hits per day)'):
				break
			pos += 1
		desc = desc_raw[pos - 1]


		# summary TODO
		homepage_raw = distro_index.xpath('//table[@class="Info"]/tr[@class="Background"]/td/a')[0]
		homepage = homepage_raw.attrib["href"]
		mailing_raw = distro_index.xpath('//table[@class="Info"]/tr[@class="Background"]/td/a')[1]
		mailing = mailing_raw.attrib["href"]
		forum_raw = distro_index.xpath('//table[@class="Info"]/tr[@class="Background"]/td/a')[2]
		forum = forum_raw.attrib["href"]
		documentation_raw = distro_index.xpath('//table[@class="Info"]/tr[@class="Background"]/td/a')[3]
		documentation = documentation_raw.attrib["href"]
		bt_raw = distro_index.xpath('//table[@class="Info"]/tr[@class="Background"]/td/a')[6]
		bt = bt_raw.attrib["href"]

		#homepage = 

		#print(title)
		#print(ostype)
		#print(basedon)
		#print(origin)
		#print(arch)
		#print(desktop)
		#print(category)
		#print(status)
		#print(desc)
		print("Homepage: " + homepage)
		print("Mailing: " + mailing)
		print("Forum: " + forum)
		print("Doc: " + documentation)
		print("BT: " + bt)
		print()

