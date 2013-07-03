#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import re
from md5 import md5
from urllib import urlopen
try:
    from progressbar import ProgressBar
except ImportError:
    print 'No existe el módulo progressbar'
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

        try:
            f = open(destino)
        except IOError:
            # No se descargó anteriormente
            f = open(destino, 'w')
            try:
                content = urlopen(img).read()
            except IOError:
                # No se puede abrir la imagen
                print 'No se puede abrir', img, ', saltando'
                continue
            f.write(content)
    	html = html.replace(img, destino) # Reemplazo por un src local
        f.close()

    f = open(filename, 'w')
    f.write(html)
    f.close()

if __name__ == '__main__':
    replace_images('feeds.html', True)

