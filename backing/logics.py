# Logics file providing backing up from DW

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from multiprocessing import Process, Queue, Lock
import requests
import lxml.html
import re, os, sys
import urllib
from time import sleep
import pprint
from inspect import getmembers
from backing.models import *
from screenshots_fetch.models import *

class Backing():

	url = "http://distrowatch.com/search.php"
	dbtable = "backing_distros"
	distro_jobs = Queue()
	l = Lock()

	def parse_test(self):
		t = Thing(name="aaasd")
		t.type = "qwesdyc"
		t.numbers = [1,2,3,4]
		t.save()
		cnt = t.numbers
		return cnt

	def parse(self):
		cnt = self.processDistros(self.getList())
		#cnt = 0
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
		distro_data = Distribution()
		
		# TablesTitle div
		name = distro_index.xpath('//td[@class="TablesTitle"]/h1//text()')[0]
		distro_data.name = name
		distro_data.shortname = name.lower().replace(" ", "").replace("/", "")

		# screenshots
		name_possible = distro_data.shortname.replace("linux", "").replace("gnu", "")
		if (name_possible == "opensuse"):
			name_possible = "suse"
		elif (name_possible == "pcos"):
			name_possible = "os4"
		elif (name_possible == "zorinos"):
			name_possible = "zorin"
		elif (name_possible == "solusos"):
			name_possible = "Solusos"
		elif (name_possible == "redhatenterprise"):
			name_possible = "redhat"
		elif (name_possible == "elementaryos"):
			name_possible = "elementary"
		elif (name_possible == "pc-bsd"):
			name_possible = "pcbsd"
		elif (name_possible == "peppermintos"):
			name_possible = "peppermint"
		elif (name_possible == "tails"):
			name_possible = "incognito"
		elif (name_possible == "luninuxos"):
			name_possible = "luninux"
		elif (name_possible == "descent|os"):
			name_possible = "descent"
		elif (name_possible == "pinguyos"):
			name_possible = "pinguy"
		elif (name_possible == "salixos"):
			name_possible = "salix"
		elif (name_possible == "systemrescuecd"):
			name_possible = "systemrescue"
		elif (name_possible == "jolios"):
			name_possible = "jolicloud"
		elif (name_possible == "kororaproject"):
			name_possible = "korora"
		elif (name_possible == "commodoreosvision"):
			name_possible = "commodore"
		elif (name_possible == "galponminino"):
			name_possible = "minino"
		elif (name_possible == "bio-"):
			name_possible = "biolinux"
		elif (name_possible == "emmabuntüs"):
			name_possible = "emmabuntus"
		elif (name_possible == "turbo"):
			name_possible = "turbolinux"
		elif (name_possible == "av"):
			name_possible = "avlinux"
		elif (name_possible == "salineos"):
			name_possible = "saline"
		elif (name_possible == "fromscratch"):
			name_possible = "lfs"
		elif (name_possible == "redobackup&recovery"):
			name_possible = "redobackup"
		elif (name_possible == "liberté"):
			name_possible = "liberte"
		elif (name_possible == "skole"):
			name_possible = "skolelinux"
		elif (name_possible == "voyagerlive"):
			name_possible = "voyager"
		elif (name_possible == "m0n0wall"):
			name_possible = "monowall"
		elif (name_possible == "blackpantheros"):
			name_possible = "blackpanther"
		elif (name_possible == "big"):
			name_possible = "biglinux"
		elif (name_possible == "dyne:bolic"):
			name_possible = "dynebolic"
		elif (name_possible == "nexentaos"):
			name_possible = "nexenta"
		elif (name_possible == "tangostudio"):
			name_possible = "tango"
		elif (name_possible == "blagand"):
			name_possible = "blag"
		elif (name_possible == "plddistribution"):
			name_possible = "pld"
		elif (name_possible == "ubuntuprivacyremix"):
			name_possible = "ubuntupr"
		elif (name_possible == "dream"):
			name_possible = "dreamstudio"
		elif (name_possible == "qimo4kids"):
			name_possible = "qimo"
		elif (name_possible == "privatixlive-system"):
			name_possible = "privatix"
		elif (name_possible == "olpcos"):
			name_possible = "olpc"
		elif (name_possible == "phinxdesktop"):
			name_possible = "phinx"
		elif (name_possible == "syllableserver"):
			name_possible = "syllable"
		elif (name_possible == "ulteoapplicationsystem"):
			name_possible = "ulteo"
		elif (name_possible == "resu"):
			name_possible = "resulinux"
		elif (name_possible == "xandrosdesktopos"):
			name_possible = "xandros"
		#print(name_possible)
		try:
			sd_screenshot_distro = SdDistribution.objects.get(name=name_possible)
			distro_data.sdscreenshot_id = sd_screenshot_distro.id
		except SdDistribution.MultipleObjectsReturned:
			print("fail-multiple")
			distro_data.sdscreenshot_id = 1
		except SdDistribution.DoesNotExist:
			print("fail-none")
			distro_data.sdscreenshot_id = 1


		# OsType
		ostype_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[1]//text()')
		os_type_string = ''.join(ostype_raw[2:])
		try:
			os_type = OsType.objects.get(name__iexact=os_type_string)
		except OsType.DoesNotExist:
			os_type = OsType(name=os_type_string)
			os_type.save()
		distro_data.os_type = os_type

		# basedon
		basedon_type_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[2]//text()')
		if ''.join(basedon_type_raw).find("forked") != -1:
			basedon_type = "forked"
		elif ''.join(basedon_type_raw).find("Independent") != -1:
			basedon_type = "independent"
		else:
			basedon_type = "based"

		basedons = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[2]/a/text()')
		based_ons = []
		for basedon_string in basedons:
			try:
				basedon = BasedOnDistro.objects.get(name__iexact=basedon_string, type__iexact=basedon_type)
			except BasedOnDistro.DoesNotExist:
				shortname = basedon_string.lower().replace("(stable)", "").replace("(testing)", "").replace(" ", "").replace("/", "");
				if (shortname == "debian"):
					shortname = "debiangnulinux"
				if (shortname == "redhat"):
					shortname = "redhatenterpriselinux"
				basedon = BasedOnDistro(name=basedon_string, shortname=shortname, type=basedon_type)
				basedon.save()
			based_ons.append(basedon)

		# Origin
		origin_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[3]//text()')
		distro_data.origin = re.sub('\n', '', re.sub('^ ', '', ''.join(origin_raw[1:])))
		# Architectures
		arch_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[4]//text()')
		arch_list = re.sub(' ', '', ''.join(arch_raw[1:])).split(',')
		architectures = []
		for arch_string in arch_list:
			try:
				architecture = Architecture.objects.get(name__iexact=arch_string)
			except Architecture.DoesNotExist:
				architecture = Architecture(name=arch_string)
				architecture.save()
			architectures.append(architecture)
		# Desktops
		desktop_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[5]//text()')
		desktops_list = re.sub('^ ', '', ''.join(desktop_raw[1:])).split(',')
		desktops = []
		for desktop_string in desktops_list:
			try:
				desktop = Desktop.objects.get(name__iexact=desktop_string)
			except Desktop.DoesNotExist:
				desktop = Desktop(name=desktop_string)
				desktop.save()
			desktops.append(desktop)
		# Categories
		category_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[6]//text()')
		categories_list = re.sub('^ ', '', ''.join(category_raw[1:])).split(',')
		categories = []
		for category_string in categories_list:
			try:
				category = Category.objects.get(name__iexact=category_string)
			except Category.DoesNotExist:
				category = Category(name=category_string)
				category.save()
			categories.append(category)
		# Status
		status_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[7]//text()')
		distro_data.status = re.sub('^ ', '', ''.join(status_raw[1:]))
		# Popularity
		popularity_raw = distro_index.xpath('//td[@class="TablesTitle"]/ul/li[8]//text()')
		# TODO
		try:
			distro_data.popularity = (int) (popularity_raw[2][0])
		except Exception:
			distro_data.popularity = -1
		# description
		desc_raw = distro_index.xpath('//td[@class="TablesTitle"]//text()')
		try:
			desc = desc_raw[desc_raw.index('Popularity (hits per day)') - 1]
		except Exception:
			desc = "N/A"
		distro_data.description = desc

		#print(distro_data.shortname)

		# Summary
		summary_raw = distro_index.xpath('//table[@class="Info"]')[0]
		for row in summary_raw.xpath('//tr[@class="Background"]'):
			td = row.getchildren()
			if(td[0].text_content().find("Buy") != -1): break
			if(td[0].text_content().find("Distribution") != -1 or len(td) <= 1): continue
			#print(td[0].text_content())
			links = []
			for link_raw in td[1].findall('a'):
				try:
					attrib = ("!!!" if link_raw.attrib['href'] is None else link_raw.attrib['href'])
				except:
					continue
				#print("-- " + link_raw.text + "("+ attrib + ")")
				link = Link(name = link_raw.text, href = attrib)
				link.save()
				links.append(link.id)
			if(td[0].text_content().find("Home Page") != -1):
				distro_data.homepage = links
			elif(td[0].text_content().find("Mailing Lists") != -1):
				distro_data.mailing_lists = links
			elif(td[0].text_content().find("User Forums") != -1):
				distro_data.user_forums = links
			elif(td[0].text_content().find("Documentation") != -1):
				distro_data.documentations = links
			elif(td[0].text_content().find("Screenshots") != -1):
				distro_data.screenshots = links
			elif(td[0].text_content().find("Download Mirrors") != -1):
				distro_data.download_mirrors = links
			elif(td[0].text_content().find("Bug Tracker") != -1):
				distro_data.bug_trackers = links
			elif(td[0].text_content().find("Related Websites") != -1):
				distro_data.related_websites = links
			elif(td[0].text_content().find("Reviews") != -1):
				distro_data.reviews = links
			else:
				print("wtf")

		distro_data.save()
		for architecture in architectures:
			distro_data.architectures.add(architecture)
		for desktop in desktops:
			distro_data.desktops.add(desktop)
		for category in categories:
			distro_data.categories.add(category)
		for basedon in based_ons:
			distro_data.based_ons.add(basedon)
		distro_data.save()
		print(distro_data.shortname + "done")
