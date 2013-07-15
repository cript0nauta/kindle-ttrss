#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import urllib
from getpass import getpass
try:
  import json
except ImportError:
  import simplejson as json

try:
    from progressbar import ProgressBar
except ImportError:
    print 'No existe el módulo progressbar'
    ProgressBar = None

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

def unread_count(url, sid):
    """ Devuelve el número de elementos sin leer """
    j = json.dumps(dict(sid=sid,op='getUnread'))
    page = urllib.urlopen(url, j).read()
    j = json.loads(page)
    return int(j['content']['unread'])

def get(url, sid, verbose = False):
    """ Obtiene los elementos sin leer en Tiny Tiny RSS. Si verbose es
    True se muestra una barra de progreso mientras se descargan los
    feeds """
    articles = []
    offset = 0
    unread = unread_count(url, sid)
    if verbose: pbar = ProgressBar(maxval=unread).start()
    while len(articles) < unread:
        j = json.dumps(dict(sid=sid,op='getHeadlines', 
            feed_id=-4, # Todos los artículos
            show_content=True,
            skip = offset,
            limit = 60))
        page = urllib.urlopen(url, j).read()
        j = json.loads(page)
        if j['status'] == 1:
            #Error
            return False
        j = j['content']
        # Añado a articles los artículos no leídos
        articles += [article for article in j if article['unread']]
        offset += 60
        if verbose: pbar.update(len(articles))
    return articles

def update(url, sid, unread, articles):
    """ Marca como leídos o no leídos los items indicados. articles 
    debe ser una lista conteniendo los IDs de cada artículo """
    articles = ','.join([str(a) for a in articles])
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


