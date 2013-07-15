#!/usr/bin/env python
#-*- coding: utf-8 -*-

from get import *
from images import replace_images
from markdown import markdown
import os, sys, pipes
import getopt
from getpass import getpass
import random
import datetime

XHTML2HTTP_EXEC = '/usr/bin/xhtml2pdf'
LOGIN_FILE = 'login'

def genhtml(fecha, url, sid, filename = 'out.html', verbose = False):
    """ Genera un fichero HTML con el resumen de los arículos sin leer."""
    if verbose: print 'Cargando template básico'
    template = open('template.html').read().decode('utf-8')
    if verbose: print 'Obteniendo artículos'
    articulos = get(url, sid, verbose)
    articulos = reversed(articulos) # Ordeno del más viejo al más nuevo
    html = ''
    indice = ''

    for art in articulos:
    	md = ""
    	md += '## [%s](%s)\n' % (art['title'], art['link'])
    	md += '#### Link: [%s](%s)\n' % (art['link'], art['link'])
    	md += '#### Feed: %s\n' % art['feed_title']
    	md += '#### Autor: %s\n' % art['author']
    	md = markdown(md)
    	i = art['id']
    	unread = "Para marcar como no leido, subrayar: __UNREAD__%s" % i 
    	html += '<article id="art-%s">%s\n%s\n%s</article><hr />\n' % (i, md,
    			art['content'], unread)

    	indice += '<li>%s: %s (ART%s)</li>' % \
    			(art['feed_title'], art['title'], i)

    # Escribimos en el fichero, teniendo el HTML básico en template.html
    if verbose: print 'Guardando HTML en', filename
    document_code = random.randint(0,99999999) # Identificador único
    write = template % dict(html=html, indice=indice, fecha=fecha, 
    		readall = '__READALL__%s'%document_code)
    arc = open(filename,'w')
    arc.write(write.encode('utf-8'))
    arc.close()

    # Guardamos la lista de artículos del documento
    database = 'db_%s' % document_code
    if verbose: print 'Guardando base de datos en', database
    f = open(database, 'w')
    f.write(','.join([str(art['id']) for art in \
    		articulos])) # IDs separados por coma
    f.close()
    
def genpdf(verbose, filename):
    # Convertimos el HTML a PDF
    filename = pipes.quote(filename) # Evitamos Command Execution
    pdf = pipes.quote(filename + '.pdf')
    if verbose: print 'Guardando PDF en', pdf
    os.system('%s "%s" "%s"' % (XHTML2HTTP_EXEC, filename, pdf))

def uso():
    	print "Uso: python %s [opciones] [out]" % sys.argv[0]
    	print "Si no se especifica out el nombre del fichero será feeds.html"
    	print "Opciones:"
    	print "\t-h | --help \t\t\t Muestra este diálogo"
    	print "\t-v | --verbose \t\t\t Muestra información mientras se ejecuta"
    	print "\t-p | --pdf \t\t\t Genera un fichero resultante en PDF"
    	print "\t-m | --mobi \t\t\t Genera un fichero resultante en un .mobi"
    	print "\t --logout \t\t\t Cerrar la sesión iniciada"
    	exit()

if __name__ == '__main__':
    try:
    	opts, args = getopt.getopt(sys.argv[1:], 'hvmp', \
    			['help', 'verbose', 'kindle-email=', 'only-generate', 'pdf',
    			'logout', 'mobi'])
    except getopt.GetoptError:
    	uso()

    verbose = False
    pdf = False
    mobi = False

    for opt,val in opts:
    	if opt in ('-h','--help'):
    		uso()
    	elif opt in ('-v', '--verbose'):
    		verbose = True
    	elif opt in ('-p', '--pdf'):
    		pdf = True
    	elif opt in ('-m', '--mobi'):
    		mobi = True
    
    if len(args):
    	filename = args[0]
    else:
    	filename = 'feeds.html'

    url, sid = login()

    if ('--logout','') in opts:
    	# Si indicamos la opción logout
    	if logout(url, sid):
    		os.unlink(LOGIN_FILE) # Borramos el fichero
    	else:
    		print "Error cerrando sesión. Saliendo"
    	exit()

    fecha = datetime.datetime.today().ctime()
    genhtml(fecha, url, sid, filename, verbose)
    if mobi:
    	if verbose: print('Descargando imágenes')
    	replace_images(filename, verbose)

    	if verbose: print('Generando el .mobi')
    	print  'kindlegen %s' % pipes.quote(filename)
    	os.system('kindlegen %s' % pipes.quote(filename))

    if pdf: genpdf(verbose, filename)

