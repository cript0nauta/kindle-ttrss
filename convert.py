#!/usr/bin/env python
#-*- coding: utf-8 -*-

from get import *
from markdown import markdown
import os, sys, pipes
import getopt
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import json
from getpass import getpass

XHTML2HTTP_EXEC = '/usr/bin/xhtml2pdf'
JSON_DATABASE = 'db.json'

def genhtml(fecha, url, sid, filename = 'out.html', verbose = False):
	""" Genera un fichero HTML con el resumen de los arículos sin leer."""
	if verbose: print 'Cargando template básico'
	template = open('template.html').read().decode('utf-8')
	if verbose: print 'Obteniendo artículos'
	articulos = get(url, sid)
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
	write = template % dict(html=html, indice=indice, fecha=fecha)
	arc = open(filename,'w')
	arc.write(write.encode('utf-8'))
	arc.close()
	
def genpdf(verbose, filename):
	# Convertimos el HTML a PDF
	filename = pipes.quote(filename) # Evitamos Command Execution
	pdf = pipes.quote(filename + '.pdf')
	if verbose: print 'Guardando PDF en', pdf
	os.system('%s "%s" "%s"' % (XHTML2HTTP_EXEC, filename, pdf))

def mail(to, subject, text, attach):
   msg = MIMEMultipart()

   msg['From'] = username
   msg['To'] = to
   msg['Subject'] = subject

   msg.attach(MIMEText(text))

   part = MIMEBase('application', 'octet-stream')
   part.set_payload(open(attach, 'rb').read())
   Encoders.encode_base64(part)
   part.add_header('Content-Disposition',
           'attachment; filename="%s"' % os.path.basename(attach))
   msg.attach(part)

   mailServer = smtplib.SMTP("smtp.gmail.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(username, password)
   mailServer.sendmail(username, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()

def send(filename, verbose, kindlemail):
	""" Enviamos el PDF a nuestro Kindle desde nuestro gmail """
	if verbose: print 'Enviando a',kindlemail,'...',
	mail(kindlemail, 'Convertir', '', filename)
	if verbose: print 'Enviado'

def uso():
		print "Uso: python %s [opciones] [out]" % sys.argv[0]
		print "Si no se especifica out el nombre del fichero será (fecha).html"
		print "Opciones:"
		print "\t-h | --help \t\t\t Muestra este diálogo"
		print "\t-v | --verbose \t\t\t Muestra información mientras se ejecuta"
		print "\t-m <mail>| --kindle-email=mail \t Se envía al e-mail del Kindle" 
		print "\t-p | --pdf \t\t\t Genera un fichero resultante en PDF"
		exit()

if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hvm:p', \
				['help', 'verbose', 'kindle-email=', 'only-generate', 'pdf'])
	except getopt.GetoptError:
		uso()

	verbose = True
	kindlemail = None
	enviar = False
	pdf = False

	for opt,val in opts:
		if opt in ('-h','--help'):
			uso()
		elif opt in ('-v', '--verbose'):
			verbose = True
		elif opt in ('-m', '--kindle-email'):
			enviar = True
			kindlemail = val
		elif opt in ('-p', '--pdf'):
			pdf = True
	
	if kindlemail is None and enviar:
		""" Si mi gmail es pepe@gmail.com el del kindle es pepe@kindle.com """
		kindlemail = username.split('@')[0]
		kindlemail += '@kindle.com'

	fecha = os.popen('date "+%F-%R"').read()[:-1]
	if len(args):
		filename = args[0]
	else:
		filename = fecha + '.html'

	url = "http://localhost/tt-rss/api/" #raw_input('URL: ')
	user = raw_input('User: ')
	password = getpass('Password: ')
	sid = login(user, password, url)
	if not sid:
		print 'Login fallido'
		exit()
	genhtml(fecha, url, sid, filename, verbose)
	if pdf: genpdf(verbose, filename)
	if enviar: send(filename+'.pdf', verbose, kindlemail)

