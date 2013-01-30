# kindle-greader
Google Reader en tu Kindle

## Dependencias
[Markdown](http://pypi.python.org/pypi/Markdown)
[Libgreader](https://github.com/askedrelic/libgreader)
[xhtml2pdf](https://github.com/askedrelic/libgreader)

## Configuración
```
# Crear archivo con usuario y contraseña de Google
echo "usuario@gmail.com:micontraseña" > login
```

## Enviar artículos por mail a nuestro Kindle
```
python convert.py
```

## Marcar como leídos los elementos que seleccionamos, según el subrayado
```
# Debemos tener conectado el Kindle
# Suponemos que está montado en /mnt/kindle
python markread.py /mnt/kindle
```
