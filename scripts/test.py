import mysql.connector

if __name__ == '__main__':
        db = mysql.connector.connect(
            host='us-cdbr-east-05.cleardb.net',
            user='bfa36e4204c168',
            passwd='7a0e5271',
            database='heroku_6b97baa7d0c1585'
        )

        mycursor = db.cursor()

        sql_string = "DELETE FROM fighterdata WHERE Name IN {} LIMIT 10".format(('Shamil Abdurakhimov', 'Israel Adesanya'))
        mycursor.execute(sql_string)

        db.commit()
