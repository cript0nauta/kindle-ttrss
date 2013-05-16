#!/usr/bin/env python
#-*- coding: utf-8 -*-

import urllib
try:
  import json
except ImportError:
  import simplejson as json

def login(user, password, url):
	""" Intenta loguearse en ttss. Retorna un SID si el login es
	efectivo, de lo contrario retorna False """
	j = dict(op='login', user=user, password=password)
	j = json.dumps(j) # Lo convierte a un string en formato JSON
	page = urllib.urlopen(url, j).read()
	j = json.loads(page) # Cargamos el JSON que retornó TTRSS
	if j['status'] == 1:
		# Login fallido
		return False
	return j['content']['session_id']

def logout(url, sid):
	""" Cierra la sesión especificada. Retorna True si no hay error """
	j = dict(op='logout', sid=sid)
	j = json.dumps(j)
	page = urllib.urlopen(url,j).read()
	ret = json.loads(page)
	if not ret['status']:
		return True

def get(url, sid):
	""" Obtiene los elementos sin leer en Tiny Tiny RSS"""
	j = json.dumps(dict(sid=sid,op='getHeadlines', #obtiene artículos
		feed_id=-3, #últimos sin leer
		show_content=True))
	page = urllib.urlopen(url, j).read()
	j = json.loads(page)
	if j['status'] == 1:
		#Error
		return False
	return j['content']

def update(url, sid, unread, articles):
	""" Marca como leídos o no leídos los items indicados. articles 
	debe ser una cadena de texto conteniendo los IDs de cada artículo
	separados por coma"""
	j = json.dumps(dict(op='updateArticle',
		article_ids = articles,
		sid = sid,
		mode = 1 if unread else 0,
		field = 2, #unread
		))
	page = urllib.urlopen(url, j).read()
	j = json.loads(page)
	if j['status'] == 1:
		#Error
		print j
		raise ValueError


