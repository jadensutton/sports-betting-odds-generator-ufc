import flask
import os
import sys
import pickle
import mysql.connector
import requests

from bs4 import BeautifulSoup
from flask import request
from flask.helpers import send_from_directory
from flask_cors import CORS, cross_origin

app = flask.Flask(__name__, static_folder='client/build', static_url_path='')
cors = CORS(app)
app.config['CORS_HEADER'] = 'Content-Type'

pickle_in = open('models/model_v3.pickle', 'rb')
model = pickle.load(pickle_in)

def generate_x(fighter_stats, opponent_stats) -> list:
    return [fighter_stats[n] - opponent_stats[n] for n in range(len(fighter_stats))]

def get_fighter_photo(fighter) -> str:
    r = requests.get('https://www.ufc.com/athlete/{}'.format(fighter.replace('-','').replace(' ', '-')))
    soup = BeautifulSoup(r.text, 'lxml')

    try:
        image_url = soup.find('div', {'class' : 'hero-profile__image-wrap'}).find('img').get('src')

        return image_url

    except Exception as e:
        print(e)
        return 'https://i.ibb.co/vYB53Kw/Untitled-1.png'

@app.route('/get_fighters', methods=['GET'])
@cross_origin()
def get_fighters() -> list:
    db = mysql.connector.connect(
        host='us-cdbr-east-05.cleardb.net',
        user=os.environ.get('DB_USER'),
        passwd=os.environ.get('DB_PASS'),
        database='heroku_6b97baa7d0c1585'
    )

    mycursor = db.cursor()

    sql_string = "SELECT Name FROM fighterdata"
    mycursor.execute(sql_string)
    data = mycursor.fetchall()

    return {'status': 'success', 'result': '---'.join([x[0] for x in data])}

@app.route('/generate_odds', methods=['GET'])
@cross_origin()
def generate_odds() -> dict:
    try:
        r = request.args
        fighter_a = r['fighter_a']
        fighter_b = r['fighter_b']

        db = mysql.connector.connect(
            host='us-cdbr-east-05.cleardb.net',
            user=os.environ.get('DB_USER'),
            passwd=os.environ.get('DB_PASS'),
            database='heroku_6b97baa7d0c1585'
        )

        mycursor = db.cursor()

        sql_string = "SELECT * FROM fighterdata WHERE Name IN {}".format((fighter_a, fighter_b))
        mycursor.execute(sql_string)
        data = mycursor.fetchall()

        if len(data) == 2:
            fighter_a_data = [x for x in data if x[0] == fighter_a][0][1:]
            fighter_b_data = [x for x in data if x[0] == fighter_b][0][1:]

            x1, x2 = generate_x(fighter_a_data, fighter_b_data), generate_x(fighter_b_data, fighter_a_data)

            proba_1 = model.predict_proba([x1])[0]
            proba_2 = model.predict_proba([x2])[0]

            fighter_a_proba = round(100 * (proba_1[1] + proba_2[0]) / 2, 1)
            fighter_b_proba = round(100 * (proba_1[0] + proba_2[1]) / 2, 1)

            odds = (fighter_a_proba, fighter_b_proba)

            fighter_a_moneyline = '{sign}{amount}'.format(sign=('+' if fighter_a_proba < fighter_b_proba else '-'), amount=round(100 * max(odds) / min(odds)))
            fighter_b_moneyline = '{sign}{amount}'.format(sign=('+' if fighter_a_proba > fighter_b_proba else '-'), amount=round(100 * max(odds) / min(odds)))

            return {'status': 'success', 'result': [fighter_a_proba, fighter_a_moneyline, fighter_b_proba, fighter_b_moneyline, get_fighter_photo(fighter_a), get_fighter_photo(fighter_b)]}

        else:
            return {'status': 'failure', 'result': '{} not found in database. Either the fighter name is incorrect or this fighter does not have enough data available to make a prediction.'.format(({fighter_a, fighter_b} - {data[0][0],}).pop())}

    except Exception as e:
        print(e)
        sys.stdout.flush()
        return {'status': 'failure', 'result': 'Unknown error, please try again later.'}

@app.route('/')
@cross_origin()
def serve():
    return send_from_directory(app.static_folder, 'index.html')
