#!/usr/bin/python
import sys
import csv
import ConfigParser
import sha
import base64
from random import choice
import ldap
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import ldap.modlist as modlist
from oauth2client import file, client, tools
from apiclient import discovery
from apiclient import errors
from httplib2 import Http
from bs4 import BeautifulSoup
import dateutil.parser as parser
import mysql.connector
import ConfigParser
from email.MIMEText import MIMEText
import datetime
def variables():
    #Cargando el archivo config.ini
    try:
        config = ConfigParser.ConfigParser()
        config.read("config.ini")
    except Exception, e:
        print e
        print "CRITICAL No pude leer el config.ini revisar que exista"
        sys.exit(1)
    #cargando variables del archivo config.ini recorro con un for las variables que deseo cargar 
    charge_variables("ldap_host ldap_base ldap_ou_person ldap_user_admin ldap_password_admin", "ldap", config)
    charge_variables("file_csv loginShell", "config", config)
    charge_variables("password_valores", "password", config)
    charge_variables("mysql_user mysql_db mysql_pass mysql_host mysql_port mysql_table mysql_table_id mysql_table_fullname mysql_table_email mysql_table_username mysql_table_accion mysql_table_date", "mysql", config)
    charge_variables("credenciales user_id storage_json gmail_from gmail_subject", "gmail", config)
    #Cargo esta variable a mano por que es un int
    globals()['password_logintud'] = int(config.get('password', 'password_logintud'))

def charge_variables(variables, seccion, config):
    for i in variables.split():
        try: 
            globals()['%s' % i] = config.get(seccion, i)
        except Exception, e:
            print e
            print "CRITICAL No pude leer %s revisar el archivo de configuracion" % i 
            sys.exit(1)

def conectar_ldap():
    try:
        con = ldap.initialize(ldap_host)
        con.simple_bind_s(ldap_user_admin, ldap_password_admin)
        con.set_option(ldap.OPT_REFERRALS, 0)
    except Exception, e:
        print e
        print "CRITICAL NO PUDE ME PUDE CONECTAR AL LDAP"
        sys.exit(1)
    return con

def generar_pass():
    password = ""
    password = password.join([choice(password_valores) for i in range(password_logintud)])
    return password

def search_uid_hig(con):
    res = con.search_s(ldap_base, ldap.SCOPE_SUBTREE, 'objectclass=posixaccount', ['uidNumber'])
    uidNum = 0
    for a in res:
        uidNumtemp = a[1].get('uidNumber')[0]
        if uidNumtemp > uidNum:
            uidNum = uidNumtemp
    nextNum = int(uidNum) + 1
    return nextNum

def agregar_usuario_ldap(con,login,apellido,nombre,email):
    #construyo el DN
    dn = "uid=" + login + ","  + ldap_ou_person
    full_name = nombre + " " + apellido
    home = "/home/" + apellido
    #busco el uid mas alto que hay en el ldap y le agrego +1 y le asigno es uid
    uidnumber = str(search_uid_hig(con))
    #Genero la password aleatoria
    password = generar_pass()
    # hasheo la pass
    ctx = sha.new(password) 
    hash = "{SHA}" + base64.b64encode(ctx.digest())
    #genero los atributos si hay algun error en los atributos o se desea agregar mas atributos hay que cambiar esta seccion
    attributes = [
        ('objectClass', ["inetOrgPerson", "posixAccount", "shadowAccount", "simpleSecurityObject"]),
        ("uid", login),
        ("sn", apellido),
        ("givenName", login),
        ("cn", apellido ),
        ('displayName', login),
        ("uidNumber", uidnumber),
        ("gidNumber", uidnumber),
        ("loginShell", loginShell),
        ('userPassword', hash),
        ("homeDirectory", home)
    ]
    try:
        #Agrego usuario 
        result = con.add_s(dn, attributes)
        alta = "alta"
    except Exception, e:
        print attributes
        print dn
        print e
        print "CRITICAL no pude dar de alta el usuario revisar la salida se guarda en la base como problema"
        alta = "problema"
    else:
        # Si funciona Ok mando correo con los datos
        enviar_email(email,login,password,full_name)
    finally:
        #Guardo en la base si la ejecucion termino Ok o CRITICAL
        guardar_mysql(full_name, email, login, alta, datetime.datetime.now())

 
def conectar_gmail():
    #Autenticacion https://developers.google.com/gmail/api/quickstart/python 
    # Creating a storage.JSON file with authentication details
    SCOPES = 'https://www.googleapis.com/auth/gmail.modify' # we are using modify and not readonly, as we will be marking the messages Read
    store = file.Storage(storage_json)
    creds = store.get()
    #si no existe el storage va a crear uno
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(credenciales, SCOPES)
        creds = tools.run_flow(flow, store)
    GMAIL = discovery.build('gmail', 'v1', http=creds.authorize(Http()))
    return GMAIL

def enviar_email(email,login,password,full_name):
    message_text = "Hola buen Dia " + full_name + " se dio de alta tu usuario : " + login + " con las password : " + password + " Cuando ingreses por primera vez se te va a pedir cambiar tu password"
    GMAIL = conectar_gmail()
    message = MIMEText(message_text)
    message['to'] = email
    message['from'] = gmail_from
    message['subject'] = gmail_subject
    message = {'raw': base64.urlsafe_b64encode(message.as_string())}
    try:
        message = (GMAIL.users().messages().send(userId=user_id, body=message).execute())
        print 'Message Id: %s' % message['id']
        return message
    except errors.HttpError, error:
        print 'CRITICAL no pude mandar el email revisar ejecucion: %s' % error
        sys.exit(1)

def guardar_mysql(mysql_fullname, mysql_email, mysql_username, mysql_accion, mysql_date):
    try:
        mymysql = mysql.connector.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,port=mysql_port,database=mysql_db)
    except Exception, e:
        print e
        print "CRITICAL no me pude conectar a la base de datos. verificar la base"
        print 'mysql_host: %s' % mysql_host
        print 'mysql_user: %s' % mysql_user
        print 'mysql_pass: ********'
        print 'mysql_port: %s' % mysql_port
        print 'database: %s' % mysql_db
        sys.exit(1)
    try:
        mycursor = mymysql.cursor()
        sql = "INSERT INTO " + mysql_table + "(" + mysql_table_fullname + "," + mysql_table_email + "," + mysql_table_username +"," + mysql_table_accion + "," + mysql_table_date +") VALUES (%s, %s, %s, %s, %s)"
        val = (mysql_fullname, mysql_email, mysql_username, mysql_accion, mysql_date)
        mycursor.execute(sql, val)
        mymysql.commit()
        print "save data in mysql success"
    except Exception, e:
        print e
        print "CRITICAL NO PUDE INSERTAR EN LA BASE DE DATOS"
        sys.exit(1)

def main():
    variables()
    con = conectar_ldap()
    #Leo el archivo csv y lo recorro
    with open(file_csv) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            #extraigo nombre apellido y email 
            user=""
            nombre = row[0]
            apellido = row[1]
            email = row[2]
            #Genero el usuario con la primera letra de cada nombre + el apellido
            for i in nombre.split():
                user = user + i[0] 
            for i in apellido.split():
                user = user + i
            print (nombre, apellido, email, user.lower())
            agregar_usuario_ldap(con,user.lower(),apellido,nombre,email)
if __name__ == '__main__':
        main()
