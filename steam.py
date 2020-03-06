import mysql.connector

from clear_table import clearTable
from extract import extract
from analyse import analyse
from password import PASSWORD



def steam():
    mydb = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        passwd = PASSWORD,
        database = 'pythondatabase',
        auth_plugin = 'mysql_native_password'
    )
    my_cursor = mydb.cursor()

    clearTable(my_cursor)
    extract(my_cursor, mydb)
    analyse(my_cursor)



if __name__ == '__main__':
    steam()
