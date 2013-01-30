#!/usr/bin/env python
#-*- coding: utf-8 -*-

import get
import sys, getopt
import re
import json

JSON_DATABASE = 'db.json'
CLIPPINGS = 'documents/Mis recortes.txt'

def uso():
	print "Uso: python %s [opciones] <KINDLE_DIR>" % sys.argv[0]
	print "Opciones:"
	print "\t-v\tMuestra información útil mientras corre"
	exit()

def main(kindledir, verbose = False):
	""" A partir del archivo de recortes del Kindle, le informa a Google
	Reader que los posts fueron leídos """

	arc = open(CLIPPINGS).read()
	re_filename = r'(?P<filename>[0-9]{4}\-[0-9]{2}\-[0-9]{2}.html)'
	re_artxx = r'(?P<artid>ART[0-9]+)'
	re_underscore = r'__(?P<action>[^_]+)__%s?' % re_artxx
	re_entry = r'%s .+\n.+\n\r\n%s \r\n=+' % (re_filename, re_underscore)

	j = json.load(open(JSON_DATABASE))
	tomark = [] # Lista de tags para marcar como leídos
	stillunread = [] # Tags de posts que seguirán no leídos
	find = re.findall(re_entry, arc)

	for filename, action, artid in find:
		articulos = j.get(filename, {}) # No hay nada si no existe la clave
		if action == 'READALL':
			# Añadimos todos los posts del fichero a tomark
			tomark += articulos.values()

			# Borramos la clava para marcar como leído una sola vez
			try:
				del(j[filename])
			except KeyError:
				if verbose: print 'No se encuentra', filename, 'en el JSON, ignorando'
		elif articulos:
			# Si artículos no está vacío (ya se procesó ants)
			tag = articulos[artid]
			stillunread.append(tag)

	# Borramos de tomark los elementos de stillunread
	for tag in stillunread:
		try:
			find = tomark.index(tag)
		except IndexError:
			if verbose: print tag, 'no aparece en la lista tomark'
		else:
			# Si se encuentra lo borro
			del(tomark[find])

	# Marcamos los tags que quedaron como leídos en Google Reader
	for tag in tomark:
		if verbose: print 'Marcando como leído', tag
		get.markRead(tag)
	json.dump(j, open(JSON_DATABASE, 'w'))

if __name__ == '__main__':
	verbose = False
	try:
		opt, args = getopt.getopt(sys.argv[1:], 'v', [])
	except getopt.getoptError:
		uso()

	for opt, val in opts:
		if opt == '-v':
			verbose = True

	if not args:
		uso()
	main(args[0], verbose)

