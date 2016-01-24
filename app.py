#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, make_response
from flask import request, Response
import os, json
import requests
from BeautifulSoup import BeautifulSoup

app = Flask(__name__)
app.debug=True
@app.route('/stops', methods=['GET'])
def stops():
    if request.method == 'GET':
		with open('stops.txt') as data:  
			k = json.loads(data.read())
			final = []
			for p in k:
				if 'location' in k[p]:
					final.append({"id":p, "name":k[p]['name'], "location":k[p]['location']})
			return json.dumps(final)
@app.route('/lines', methods=['GET'])
def lines():
    if request.method == 'GET':
		with open('lines.txt') as data:  
			final = []
			routes = json.loads(data.read())
			for route in routes:
				find = [idx for idx, f in enumerate(final) if int(f["name"])==int(routes[route]["name"])]
				if len(find)>0:
					final[find[0]]['directions'].append({"name":routes[route]["direction"], "id":route})
				else:
					final.append({"name":int(routes[route]["name"]), "directions":[{"name":routes[route]["direction"], "id":route}]})
			return json.dumps(final)

@app.route('/stops/<line>', methods=['GET'])
def stops_line(line):
	if request.method == 'GET':
		with open('lines.txt') as data:  
			final = []
			lines = json.loads(data.read())
			line = lines[line]
			return json.dumps(line['stops'])
				
					
		return json.dumps(final)

@app.route('/time/<stop>', methods=['GET'])
def times(stop):
    if request.method == 'GET':
		final = []
		r =  BeautifulSoup(requests.get('http://www.ul.nu/vemos2_web.dll/hpl?hplnr='+stop).text, convertEntities=BeautifulSoup.HTML_ENTITIES)
		t = r.find('table', {'cellpadding':5})
		if t!=None:
			trs = t.findAll('tr')
			trs = trs[1:]
			for tr in trs:
				tds = tr.findAll('td')
				line = tds[0].contents[1].contents[1].contents[0].replace(" ", "")
				direction = tds[1].contents[1].contents[0].replace("  ", "").replace(" ", "")
				time = tds[2].contents[1].contents[0].contents[0].replace("\n", "").replace("    ", "").replace("\r", "").replace("  ", "").replace(" om", "")
				cleanTime = time.replace("min", "")
				time = time[:-1]
				hour = ""
				if time[0]==" ":
					time = time[1:]
				if "(" in time:
					i = time.index("(")-1
					hour = time[-i:].replace(")", "")
					time = time[:i].replace("(", "")
				final.append({'line':line, 'direction':direction, 'time':time, 'cleanTime':cleanTime, 'hour':hour, 'stopId':stop})
			
		return json.dumps(final)

if __name__ == '__main__':
    app.run('0.0.0.0', 5000)