sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/ppolicy.ldif
ldapadd -x -W -D "cn=admin,dc=mercadolibre,dc=com,dc=ar" -f oupolicy.ldif
sudo ldapadd -Y EXTERNAL -H ldapi:/// -f ppmodule.ldif

ldapadd -x -W -D "cn=admin,dc=mercadolibre,dc=com,dc=ar" -f passwordpolicy.ldif
