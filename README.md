# kindle-ttrss
Tiny Tiny RSS en tu Kindle

Basado en [kindle-greader](https://github.com/sh4r3m4n/kindle-greader)

## Configurar TTRSS
* Asegurarse de habilitar el API en las preferencias de tt-rss
* La URL será http://mihost/path-a-tt-rss/api/

## Dependencias
* [python-markdown](http://pypi.python.org/pypi/Markdown)
* [xhtml2pdf](https://github.com/askedrelic/libgreader) (opcional, para convertir a PDF)
* [kindlegen](http://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211) (opcional, para convertir a mobi)

## Convertir los feeds a HTML y MOBI
```
$ git clone git@github.com:sh4r3m4n/kindle-ttrss.git
$ cd kindle-ttrss
$ ./convert.py -m # Se genera un feeds.html y un feeds.mobi
```

## Marcar como leídos los elementos
```
$ # Se deben subrayar las palabras clave __UNREAD__XXX y __READALL__XXX en el kindle
$ # Se supone que el Kindle está conectado y montado en /mnt/kindle
$ ./markread.py "/mnt/kindle/documents/Mis recortes.txt" # Le paso como argumento el fichero con los subrayados
```
