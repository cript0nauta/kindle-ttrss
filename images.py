#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import re
from md5 import md5
from urllib import urlopen
try:
	from progressbar import ProgressBar
except ImportError:
	ProgressBar = None

def replace_images(filename, verbose):
	""" Reemplaza el origen de las etiquetas IMG contenidas en el
	fichero filename por enlaces a imágenes locales """

	f = open(filename)
	html = f.read()
	f.close()

	re_src = r'\<img.*src="([^"]*)".*\>'
	imagenes = re.findall(re_src, html)

	if verbose and ProgressBar:
		# Para tener una barra de progreso si tenemos el módulo
		imagenes = ProgressBar()(imagenes)

	for img in imagenes:
		# Le ponemos de nombre el hash md5 de la URL original
		destino = 'images/%s.jpg' % md5(img).hexdigest()
		html = html.replace(img, destino) # Reemplazo por un src local

		f = open(destino, 'w')
		content = urlopen(img).read()
		f.write(content)
		f.close()

	f = open(filename, 'w')
	f.write(html)
	f.close()

if __name__ == '__main__':
	replace_images('feeds.html', True)

