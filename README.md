# CHALLENGE-MERCADOLIBRE-2

El Challenge esta Testeado en un Debian 9

## Objetivo

Dado un archivo CSV conteniendo nombre, apellido y correo electrónico de
usuarios, desarrollar un sistema que lo lea y cree cuentas y password en
OpenLDAP. La password deben ser del tipo random y debe ser enviada, junto con
el nombre de usuario, por correo electrónico.
Al ingresar el usuario, se le debe solicitar cambio de contraseña.
El estado de todo los usuarios debe ser guardado en una base de datos MySQL o
MongoDB junto con su password almacenada en forma segura.
Esto debe ser desarrollado en Python, Ruby o Java.



## CONFIGURACION

En el archivo config.ini esta toda la configuracion

[mysql] | Justification
------- |  -------------
mysql_user| Nombre de usuario con previligios para crear una database
mysql_db | Nombre de la base de datos
mysql_pass | password del usuario con previlegios para crear la base
mysql_host | host donde esta hosteado el mysql o mariadb
mysql_port | puerto del mysql o mariadb
mysql_table | nombre de la tabla
mysql_table_id | nombre de la columna id
mysql_table_fullname | nombre de la columna donde se almacena el nombre completo
mysql_table_email | nombre de la columna donde se almacena el email
mysql_table_username | nombre de la columna donde se almacena el usuario
mysql_table_accion | nombre de la columna donde se almacena la accion (Alta = usuario se dio de alta correctamente | problema = hubo algun problema)
mysql_table_date | nombre de la tabla donde se almacena la fecha

[gmail] | Justification
------- |  -------------
credenciales | archivo generado siguiendo estas instrucciones https://developers.google.com/gmail/api/quickstart/python
user_id | user id por lo genera es "me"
storage_json | nombre del archivo donde se va a guardar la authorizacion
gmail_from | From de gmail
gmail_subject |  texto del asunto

[ldap] | Justification
------- |  -------------
ldap_host | string de conexion del ldap ejemplo : ldap://192.168.1.204:389
ldap_base | base del ldap ejemplo :  dc=mercadolibre,dc=com,dc=ar
ldap_ou_person | ou donde van a colgar los usuarios ejemplo :  ou=People,dc=mercadolibre,dc=com,dc=ar
ldap_user_admin | usuario admin ejemplo :  cn=admin,dc=mercadolibre,dc=com,dc=ar
ldap_password_admin | password del usuario admin 

[config] | Justification
------- |  -------------
file_csv | file de etrada tiene que ser csv y debe contener nombre, apellido y correo electrónico 
loginShell | definir que shell que van a tener los usuarios ejemplo : /bin/bash

[password] | Justification
------- |  -------------
password_logintud | longitud de la password
password_valores | valores que va a tomar la password ejemplo :  0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ

## GMAIL
Generar las credenciales (client_secret.json) para utilizar las apis de gmail ver siguiente enlace

  https://developers.google.com/gmail/api/quickstart/python

Si no existe el archivo storage_json. va a requerir darle permisos en forma manual siguiendo las instrucciones que arroje por pantalla
Mas info https://developers.google.com/gmail/api/quickstart/python


## Test script from Docker 

### pre requisitos

  Verificar el archivo config.ini ahi vive la configuracion. 
  el archivo storage.json tiene que estar configurado.
  Mariadb y el openldap va a escuchar en la ip del host cambiar la configuracion por la ip

### Build docker

```bash
  docker build -t challenge2-mariadb -f Dockerfile-mariadb .
  docker build -t challenge2-openldap -f Dockerfile-openldap .
  docker build -t challenge2 -f Dockerfile .
```
### Exec Openldap
  setear las variables segun corresponda mas info en <https://github.com/osixia/docker-openldap>
```bash
  docker run --name challenge2-openldap -e LDAP_ORGANISATION="mercadolibre" -e LDAP_DOMAIN="mercadolibre.com.ar" -e LDAP_ADMIN_PASSWORD="mercadolibre" -p 389:389 -p 636:636  -d challenge2-openldap:latest --copy-service
```

### Exec mariadb
  
  para ver todas las variables del mariadb revisar la configuracion <https://hub.docker.com/_/mariadb>

```bash

  docker run --name challenge2-mariadb -e MYSQL_ROOT_PASSWORD="mercadolibre" -e MYSQL_DATABASE="mercadolibre_ldap" -e MYSQL_USER="mercadolibre" -e MYSQL_PASSWORD="mercadolibre" -p 3306:3306 -d challenge2-mariadb:latest

```

### exec challenge Docker

```bash
  docker run --name challenge2  -v $(pwd)/config.ini:/ChallengeMercadoLibre2/config.ini -v $(pwd)/storage.json:/ChallengeMercadoLibre2/storage.json  -v $(pwd)/client_secret.json:/ChallengeMercadoLibre2/client_secret.json -v $(pwd)/users.csv:/ChallengeMercadoLibre2/users.csv -d challenge2:latest

```

cada ves que se necesite ejecutar utilizar el siguiente comando 

```bash

  docker start challenge2

```

Ver los logs 

```bash

  docker logs challenge2

```

## Test script from Debian
### Sistema Operativo
Debian 9 netinstall

###Base de datos
Tener instalado mariadb server
```bash
	$ sudo apt install mariadb-server
	$ sudo mysql_secure_installation
```

Crear usuario y password 

```mysql
	GRANT ALL ON *.* TO 'mercadolibre'@'localhost' IDENTIFIED BY 'mercadolibre' WITH GRANT OPTION;
	FLUSH PRIVILEGES;
``` 
Crear la base de datos

```mysql
	create database mercadolibre_ldap ;
``` 

crear tablas hay 2 maneras restaurando el dump 

```mysql
	$ mysql -u mercadolibre -pmercadolibre mercadolibre_ldap < mysql/dump_mercadolibre_ldap.sql 
``` 

o ejecutando el siguiente script 

```bash
	$ python mysql/init_mysql.py
``` 

#Ldap

instalar openldap
```bash
	$ sudo apt-get install slapd ldap-utils
``` 
Configurar openldap

```bash
dpkg-reconfigure -plow slapd
```
configuracion 

dominio = mercadolibre.com.ar
ou = mercadolibre
pass = mercadolibre

Generar ou

```bash
	$ ldapadd -x -D cn=admin,dc=mercadolibre,dc=com,dc=ar -W -f u_org.ldif
``` 

### Python Config

Verificar tener instalado cliente pip

```bash
	$ sudo apt install python-pip
	$ sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
```

Instalar todas las dependencias

```
$ pip install -r requirements.txt 
```

### EJECUCION

```bash
  $ python challenge3.py
```

