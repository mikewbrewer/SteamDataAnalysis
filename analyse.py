import pandas as pd
import mysql.connector
import gspread

from datetime import datetime, date
from password import PASSWORD
from oauth2client.service_account import ServiceAccountCredentials



def analyse(_cursor):
    # mappings to discount sheet
    code_total_discount_by_day = {
        'Sunday': '4',
        'Monday': '5',
        'Tuesday': '6',
        'Wednesday': '7',
        'Thursday': '8',
        'Friday': '9',
        'Saturday': '10'
    }

    total_days_row_code = '14'
    total_days_col_code = {
        'Sunday': 'C',
        'Monday': 'D',
        'Tuesday': 'E',
        'Wednesday': 'F',
        'Thursday': 'G',
        'Friday': 'H',
        'Saturday': 'I'
    }


    # connect to google sheets
    scope = [ "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("Google_Credentials.json", scope)
    client = gspread.authorize(creds)

    # connect to the individual worksheets within the Spreadsheet
    sh = client.open_by_url('https://docs.google.com/spreadsheets/d/17qZwifMUgG9kqotUgCos8Z0qNhpQQulpNMvl-EaXGL0/edit#gid=0')
    price_wks = sh.get_worksheet(0)
    discount_wks = sh.get_worksheet(1)

    today = str(datetime.now().strftime('%A'))
    # initialize the new rows to be inserted into the worksheets
    new_price_row = [today, str(date.today())]
    new_discount_row = []

    # get subtable of average prices by genre
    _cursor.execute("""
        SELECT genre, AVG(price)
        FROM game_titles
        GROUP BY genre;
    """)
    avg_price_by_genre = _cursor.fetchall()

    # get subtable of number of discounted titles by genre
    _cursor.execute("""
        SELECT genre, COUNT(discount)
        FROM game_titles
        WHERE discount = 'Y'
        GROUP BY genre;
    """)
    num_discount_by_genre = _cursor.fetchall()


    # append each price/discountnum to its respective new row list
    for i in range(0, len(avg_price_by_genre)):
        new_price_row.append(float(round(avg_price_by_genre[i][1], 2)))
        new_discount_row.append(num_discount_by_genre[i][1])

    # write the new rows to the worksheets
    price_wks.append_row(new_price_row, 2)

    totals_cols = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    for i in range(0, len(new_discount_row)):
        temp = int(discount_wks.acell(totals_cols[i] + code_total_discount_by_day[today]).value) + new_discount_row[i]
        discount_wks.update_acell(totals_cols[i] + code_total_discount_by_day[today], temp)

    val = discount_wks.acell(total_days_col_code[today] + total_days_row_code).value
    val = int(val) + 1
    discount_wks.update_acell(total_days_col_code[today] + total_days_row_code, val)




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
    analyse(my_cursor)
