import mysql.connector
from password import PASSWORD


# These scripts are run about every day or so, this function is run before
# all the others and checks to see if there is already a game_titles table
# in the database and deletes it if there is.
def clearTable(_cursor):
    try:
        _cursor.execute("""
            DROP TABLE game_titles;
        """)
    except:
        print ("- - NON EXISTANT TABLE CANNOT BE DROPPED - -")


if __name__ == '__main__':
    # if run on it's own, this connects the script to the database
    mydb = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        passwd = PASSWORD,
        database = 'pythondatabase',
        auth_plugin = 'mysql_native_password'
    )
    my_cursor = mydb.cursor()
    clearTable(my_cursor)
