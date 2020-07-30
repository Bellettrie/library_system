from bellettrie_library_system.settings import OLD_USN, OLD_PWD, OLD_DB
import mysql.connector

migration_database = mysql.connector.connect(
    unix_socket='/var/run/mysqld/mysqld.sock',
    user=OLD_USN,
    passwd=OLD_PWD,
    database=OLD_DB
)
