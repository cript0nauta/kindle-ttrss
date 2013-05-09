#!/usr/bin/env python
#-*- coding: utf-8 -*-

from get import get
from markdown import markdown
import os, sys, pipes
import getopt
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import json

XHTML2HTTP_EXEC = '/usr/bin/xhtml2pdf'
JSON_DATABASE = 'db.json'

def convert(fecha, filename = 'out.html', verbose = False):
	""" Genera un fichero HTML con el resumen de los arículos sin leer."""
	if verbose: print 'Cargando template básico'
	template = open('template.html').read().decode('utf-8')
	if verbose: print 'Obteniendo artículos'
	articulos = get()
	html = ''
	indice = ''

	# Abrimos o creamos el JSON que almacane el tag original de cada idart
	try:
		arc = open(JSON_DATABASE)
	except IOError:
		# Creamos la base de datos si no existe
		if verbose: print 'El JSON no exite, creando'
		json.dump({}, open(JSON_DATABASE, 'w'))
		j = {}
	else:
		if verbose: print 'Json cargado correctamente'
		j = json.load(arc)
	key = dict()

	for i in range(len(articulos)):
		art = articulos[i]
		key['ART%s'%i] = art['tag']
		md = ""
		md += '## [%s](%s) (ART%s)\n' % (art['titulo'], art['link'], i)
		md += '#### Link: [%s](%s)\n' % (art['link'], art['link'])
		md += '#### Feed: %s\n' % art['feed']
		md += '#### Autor: %s\n' % art['autor']
		md = markdown(md)
		unread = "Para marcar como no leido, subrayar: __UNREAD__ART%s" % i
		html += '<article id="art-%s">%s\n%s\n%s</article><hr />\n' % (i, md,
				art['content'], unread)

		indice += '<li>%s: %s (ART%s)</li>' % \
				(art['feed'], art['titulo'], i)

	# Escribimos en la base de datos
	j[filename] = key
	if verbose: print 'Escribiendo en JSON'
	json.dump(j, open(JSON_DATABASE, 'w'))

	# Escribimos en el fichero, teniendo el HTML básico en template.html
	if verbose: print 'Guardando HTML en', filename
	write = template % dict(html=html, indice=indice, fecha=fecha)
	arc = open(filename,'w')
	arc.write(write.encode('utf-8'))
	arc.close()
	
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
		print "\t-k <mail>| --kindle-email=mail \t El e-mail del Kindle" 
		print "\t-g | --only-generate \t\t Solo genera el PDF, no lo envía"
		exit()

if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hvk:m:g', \
				['help', 'verbose', 'kindle-email=', 'only-generate'])
	except getopt.GetoptError:
		uso()

	verbose = True
	kindlemail = None
	enviar = True

	for opt,val in opts:
		if opt in ('-h','--help'):
			uso()
		elif opt in ('-v', '--verbose'):
			verbose = True
		elif opt in ('-k', '--kindle-email'):
			kindlemail = val
		elif opt in ('-g', '--only-generate'):
			enviar = False
	
	if kindlemail is None:
		""" Si mi gmail es pepe@gmail.com el del kindle es pepe@kindle.com """
		kindlemail = username.split('@')[0]
		kindlemail += '@kindle.com'

	fecha = os.popen('date "+%F-%R"').read()[:-1]
	if len(args):
		filename = args[0]
	else:
		filename = fecha + '.html'

	convert(fecha, filename, verbose)
	if enviar: send(filename+'.pdf', verbose, kindlemail)

