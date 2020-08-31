from django.conf import settings
import mysql.connector

migration_database = mysql.connector.connect(
    #unix_socket='/var/run/mysqld/mysqld.sock',
    host='localhost',
    user=settings.OLD_USN,
    passwd=settings.OLD_PWD,
    database=settings.OLD_DB
)
