import sys
import ConfigParser
import mysql.connector


def variables():
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    """seccion = "mysql"
    for i in "mysql_user mysql_db mysql_pass mysql_host mysql_port mysql_table mysql_table_id mysql_table_fullname mysql_table_email mysql_table_username mysql_table_accion mysql_table_date".split():
        globals()['%s' % i] = config.get(seccion, i)"""

    charge_variables("mysql_user mysql_db mysql_pass mysql_host mysql_port mysql_table mysql_table_id mysql_table_fullname mysql_table_email mysql_table_username mysql_table_accion mysql_table_date", "mysql", config)
    #Cargo esta variable a mano por que es un int
    #globals()['password_logintud'] = int(config.get('password', 'password_logintud'))

def charge_variables(variables, seccion, config):
    """ config = ConfigParser.ConfigParser()
    config.read("config.ini") """
    for i in variables.split():
        globals()['%s' % i] = config.get(seccion, i)

def main():
    variables()
    try:
        mymysql = mysql.connector.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,port=mysql_port)
    except Exception, e:
        print e
        print "CRITICAL NO PUDE CONECTAR A LA BASE DE DATOS REVISAR QUE LA BASE ESTE ARRIBA O QUE EL HOST USER Y PASS SEAN CORRECTOS"
        sys.exit(1)
    mycursor = mymysql.cursor()
    mycursor.execute("SHOW DATABASES")
    flag = 0
    for i in mycursor:
        if mysql_db in i:
            flag = 1
    if flag == 1:
        try:
            mymysql.close()
            mymysql = mysql.connector.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,port=mysql_port,database=mysql_db)
        except Exception, e:
            print e
            print "CRITICAL NO ME PUDE CONECTAR A LA BASE DE DATOS REVISAR SI EL USUARIO TIENE PERMISOS"
    else:
        try:
            print "CREANDO DATABASE"
            mycursor.execute("CREATE DATABASE " + mysql_db)
            mymysql.close()
            mymysql = mysql.connector.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,port=mysql_port,database=mysql_db)
        except Exception, e:
            print e
            print "CRITICAL NO PUDE CREAR LA BASE DE DATOS REVISAR SI EL USUARIO TIENE PERMISOS"
    mycursor = mymysql.cursor()
    mycursor.execute("SHOW TABLES")
    flag = 0
    for i in mycursor:
        if mysql_table in i:
            flag = 1
    if flag == 0:
        print "CREANDO TABLE"
        mycursor.execute("create table " + mysql_table + " ( " + mysql_table_id + " INT NOT NULL AUTO_INCREMENT, " + mysql_table_fullname + " TEXT NOT NULL, " + mysql_table_email + " TEXT NOT NULL, " + mysql_table_username + " TEXT NOT NULL, " + mysql_table_accion + " TEXT NOT NULL, " + mysql_table_date + " DATE, PRIMARY KEY ( " + mysql_table_id + " ));")
    mymysql.close()
    mymysql = mysql.connector.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,port=mysql_port,database=mysql_db)
    return mymysql





if __name__ == '__main__':
    main()

