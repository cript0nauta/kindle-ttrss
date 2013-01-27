#!/usr/bin/env python
#-*- coding: utf-8 -*-

from get import get, username, password
from markdown import markdown
import os

def convert(filename = 'out.html'):
	""" Genera un archivo HTML con el resumen de los arículos sin leer """
	template = open('template.html').read().decode('utf-8')
	articulos = get()
	html = ''
	indice = ''

	for i in range(len(articulos)):
		art = articulos[i]
		md = ""
		md += '## [%s](%s) (ART%s)\n' % (art['titulo'], art['link'], i)
		md += '#### Link: [%s](%s)\n' % (art['link'], art['link'])
		md += '#### Feed: %s\n' % art['feed']
		md += '#### Autor: %s\n' % art['autor']

		md = markdown(md)
		html += '<article id="art-%s">%s\n%s</article><hr />\n' % (i, md,
				art['content'])

		indice += '<li>%s: %s (ART%s)</li>' % \
				(art['feed'], art['titulo'], i)

	# Escribimos en el archivo, teniendo el HTML básico en template.html
	write = template % dict(html=html, indice=indice)
	arc = open(filename,'w')
	arc.write(write.encode('utf-8'))
	arc.close()

	os.system('chromium ' + filename)

if __name__ == '__main__':
	convert()

