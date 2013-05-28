#!/usr/bin/env python
#-*- coding: utf-8 -*-

from get import *
import sys, getopt
import re

def uso():
	print "Uso: python %s [opciones] <CLIPPINGS_FILE>" % sys.argv[0]
	print "CLIPPINGS_FILE es el fichero Mis recortes.txt del Kindle"
	print "Opciones:"
	print "\t-v\tMuestra información útil mientras corre"
	exit()

def main(url, sid, filename, verbose = False):
	if verbose: print 'Abriendo fichero de recortes'
	recortes = open(filename).read()
	separator = '\r\n==========\r\n'
	clips = recortes.split(separator)[:-1] # El último elemento está en blanco
	keepunread = [] 
	invalidclips = [] 
	for clip in clips:
		try:
			content = clip.splitlines()[3]
		except IndexError:
			print 'Error de índice en el fichero, ignorando'
			continue
		match= re.match('__(UNREAD|READALL)__([0-9]+)', content)
		if match:
			action, id_ = match.groups()
			if action == 'READALL':
				dbname = 'db_%s' % id_
				if verbose: print 'Abriendo', dbname
				article_ids = open(dbname).read()
				update(url, sid, False, article_ids)
			elif action == 'UNREAD':
				keepunread.append(id_)
		else:
			# Es un subrayado normal que no nos interesa
			# Lo dejamos igual que antes
			invalidclips.append(clip)

	if verbose: print 'Marcando como no leídos:', keepunread
	if keepunread: update(url, sid, True, *keepunread)

	if verbose: print 'Escribiendo en', filename
	f = open(filename, 'w')
	f.write(separator.join(invalidclips) + separator)
	f.close()

if __name__ == '__main__':
	verbose = False
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'v', [])
	except getopt.getoptError:
		uso()

	for opt, val in opts:
		if opt == '-v':
			verbose = True

	if not args:
		uso()

	filename = args[0]
	if verbose: print 'Abriendo', filename
	f = open('login')
	content = f.read()
	sid, url = content.split(';', 1)
	f.close()
	main(url, sid, filename, verbose)

