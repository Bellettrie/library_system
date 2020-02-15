import mysql.connector

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="oldsystem"
        )
        mycursor = mydb.cursor(dictionary=True)
        print(mydb)
        mycursor.execute("SHOW TABLES")

        for x in mycursor:
            print(x)
        mycursor.execute("SELECT * FROM publicatie where titel=''")
        for x in mycursor:
            print(x)
