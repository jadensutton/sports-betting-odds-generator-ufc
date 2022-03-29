import mysql.connector
import os

if __name__ == '__main__':
        db = mysql.connector.connect(
            host='us-cdbr-east-05.cleardb.net',
            user=os.environ.get('DB_USER'),
            passwd=os.environ.get('DB_PASS'),
            database='heroku_6b97baa7d0c1585'
        )

        mycursor = db.cursor()

        sql_string = "DELETE FROM fighterdata WHERE Name IN {} LIMIT 10".format(('Shamil Abdurakhimov', 'Israel Adesanya'))
        mycursor.execute(sql_string)

        db.commit()
