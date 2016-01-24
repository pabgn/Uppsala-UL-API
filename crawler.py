#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests,bs4,json, time, io
from BeautifulSoup import BeautifulSoup

class ULCrawler:
	def __init__(self):
		self.stops = {}
		self.lines = {}

	def get_stop_names(self):
		print "### Gathering all bus stops ###"
		r = requests.get('http://www.ul.nu/vemos2_web.dll/hpllista.html').text
		b = BeautifulSoup(r)
		t = b.find('table', {'cellpadding':12})
		s = t.findAll('a', {'name':None})
		s = s[24:]
		for stop in s:
			id = stop['href'].replace("hpl?hplnr=", "")
			name = stop.contents[0]
			name = name[1:]
			self.stops[int(id)]={'name':name}
		print "## COMPLETE! ##\n"
	def lineid_and_direction_exist(self, line_id, line_name, direction):
		if line_id in self.lines:
			return True
		for l in self.lines:
			if line_name==self.lines[l]['name'] and direction==self.lines[l]['direction']:
				return True
		return False
	
	def get_lines(self):
		print "### Lines discovery process started! ###"
		for stop in self.stops:
			id = stop
			r = requests.get('http://www.ul.nu/vemos2_web.dll/hpl?hplnr='+str(id)).text
			b = BeautifulSoup(r, convertEntities=BeautifulSoup.HTML_ENTITIES)
			t = b.find('table', {'cellpadding':5})
			if t!=None:
				trs = t.findAll('tr')
				for tr in trs:
					tds = tr.findAll('td')
					trs = trs[1:]
					if(len(tds[4].contents)>1):
						line_id = tds[4].contents[1]['href'].replace("lt?lti=", "")
						p = line_id.index("&")
						line_id = line_id[:p]
						line_name = tds[0].contents[1].contents[1].contents[0].replace(" ", "")
						direction = tds[1].contents[1].contents[0].replace("  ", "").replace(" ", "")
						if self.lineid_and_direction_exist(line_id, line_name, direction)==False:
							self.lines[line_id]={"name":line_name, "direction":direction, "stops":[]}
							print "-> Line "+line_name+" to "+ direction+" discovered: "+line_id

	def get_lines_stops(self):
		print "@ Gathering stops order for lines @"
		for line in self.lines:
			print "->Getting stops for "+line
			r =  BeautifulSoup(requests.get('http://www.ul.nu/vemos2_web.dll/lt?lti='+line).text, convertEntities=BeautifulSoup.HTML_ENTITIES)
			t = r.find('table', {'cellpadding':5})
			if t!=None:
				trs = t.findAll('tr')
				trs = trs[1:]
				order = 1
				for tr in trs:
					tds = tr.findAll('td')
					if(len(tds[0].contents)>1):
						id = tds[0].contents[1]['href'].replace("hpl?hplnr=", "")
						name = tds[0].contents[1].contents[1].contents[0].replace(" ", "")
						self.lines[line]['stops'].append({"id":id, "name":name, "order":order})
						order+=1

	
	def get_stop_locations(self):
		print "## Gathering location for stops ##\n"
		k=0
		for stop in self.stops:
			k+=1
			print "-> Name: "+self.stops[stop]['name']
			r = json.loads(requests.get('https://api.ul.se/api/v2/stops?query='+self.stops[stop]['name']).text)
			l = None
			for p in r:
				if l ==None:
					if int(p["id"])==stop:
						l = p["coordinate"]
						self.stops[stop]['location']=l
						print "Found!\n"
			if l == None:
				print "No matches :( \n"
			print "Progress: "+str(k)+"/"+str(len(self.stops))
				
			time.sleep(1)
	def save_json(self):
		with io.open('stops.txt', 'w', encoding='utf-8') as f:
			f.write(unicode(json.dumps(self.stops, ensure_ascii=False)))
	def save_json_lines(self):
		with io.open('lines.txt', 'w', encoding='utf-8') as f:
			f.write(unicode(json.dumps(self.lines, ensure_ascii=False)))	
	def load_lines(self):
		with open('lines.txt') as data:  
			self.lines = json.loads(data.read())

	
crawler = ULCrawler()
crawler.get_stop_names()
#crawler.get_lines()
crawler.load_lines()
crawler.get_lines_stops()
crawler.save_json_lines()
#crawler.get_stop_locations()
#crawler.save_json()