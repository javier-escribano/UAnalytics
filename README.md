# UAnalytics

Este proyecto consiste en la implementación de una aplicación web utilizando herramientas para el uso y tratado de datos con **Python**. Para ello hemos basado nuestra práctica en una aplicación de búsqueda de información de usuarios en determinadas redes sociales, haciendo uso de distinas **APIs** para cumplir tal propósito. A su vez, mostraría los datos más relevantes y específicos a la búsqueda mostrando, en la medida de lo posible, la información hallada en forma de diferentes estructuras y bloques de datos.

## Integrantes del Grupo:

- Javier Escribano Salgado // javier.escribano@udc.es
- Alejandro Álvarez Corujo // a.corujo@udc.es
- Brais Vázquez Villa // brais.vazques.villa@udc.es

## Cómo ejecutar el contenedor Docker en Linux:
Es necesario tener instalado docker-compose para poder ejecutar correctamente el proyecto Django, para ello se pueden descargar los ejecutables para Windows y Mac aquí https://docs.docker.com/compose/install/ . Además es necesario tener instalado el propio docker para poder ejecutar los comandos que actúan sobre la imagen, para ello se pude hacer uso de las instrucciones para distintas plataformas denro de la propia web de Docker.

Para linux será necesario ejecutar este comando como administrador para tener la última versión estable del docker-compose:

```console
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
Y darle permisos de ejecución:

```console
chmod +x /usr/local/bin/docker-compose
```

Una vez instalado el docker-compose y tener el propio docker presente en la máquina, como es lógico, se tendrá que ejecutar un script que automatizará todo el proceso de obtención de la imagen del repositorio y su propia ejecución:

````console
./script.sh
````

