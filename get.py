#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import urllib
try:
  import json
except ImportError:
  import simplejson as json

LOGIN_FILE = 'login'

def login():
	""" Se loguea en TTRSS usando la última sesión usada o en una nueva
	si no hay o falla. Si se autentica correctamente devuelve un URL y 
	un SID, de lo contrario muestra un mensaje y cierra el script.
	"""

	try:
		f = open(LOGIN_FILE)
	except IOError:
		# No iniciamos sesión
		url = raw_input('URL: ')
		user = raw_input('User: ')
		password = getpass('Password: ')

		# Nos logueamos usando el api
		j = dict(op='login', user=user, password=password)
		j = json.dumps(j) # Lo convierte a un string en formato JSON
		page = urllib.urlopen(url, j).read()
		j = json.loads(page) # Cargamos el JSON que retornó TTRSS
		if j['status'] == 1:
			# Login fallido
			print "Login fallido"
			exit()
		sid = j['content']['session_id']

		# Creamos un fichero con los datos de la sesión
		f = open(LOGIN_FILE, 'w')
		f.write(';'.join([sid,url]))
		f.close()
	else:
		content = f.read()
		sid, url = content.split(';', 1)
		f.close()
		return url, sid

	j = dict(op='login', user=user, password=password)
	j = json.dumps(j) # Lo convierte a un string en formato JSON
	page = urllib.urlopen(url, j).read()
	j = json.loads(page) # Cargamos el JSON que retornó TTRSS
	if j['status'] == 1:
		# Login fallido
		print "Login fallido"
		logout()
		exit()
	return j['content']['session_id']

def logout():
	""" Cierra la sesión especificada. """
	url, sid = login()
	j = dict(op='logout', sid=sid)
	j = json.dumps(j)
	page = urllib.urlopen(url,j).read()

	# Intenta borrar el fichero de login, pero sigue si no lo logra
	try:
		os.unlink(LOGIN_FILE)
	except OSError:
		pass

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


