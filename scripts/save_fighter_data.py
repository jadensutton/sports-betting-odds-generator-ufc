import csv
import os
import requests
import mysql.connector

import pandas as pd

from bs4 import BeautifulSoup
from datetime import datetime

def remove_non_ints(s: str) -> int:
    if '-' in s:
        return 0

    return int(''.join([str(c) for c in s if c.isdigit()]))

def remove_whitespace(s: str) -> str:
    s = s.replace('\n', '')
    s = ''.join([char for x, char in enumerate(s) if (x != len(s) - 1 and x != 0) and (char != ' ' or (s[x + 1] != ' ' and s[x - 1] != ' '))])

    return s

def get_prior_fight_stats(name: str) -> tuple:
    strikes = 0
    takedowns = 0
    minutes = 0

    r = requests.get(fighter_page_urls[name])
    soup = BeautifulSoup(r.text, 'lxml')
    table = soup.find('table', {'class' : 'b-fight-details__table b-fight-details__table_style_margin-top b-fight-details__table_type_event-details js-fight-table'}).find('tbody').find_all('tr')[:0:-1]
    for n, row in enumerate(table[-5:]):
        if n == 4 and row.find_all('td')[0].find('p').find('a').find('i').find('i').text == 'next':
            row = table[-6]

        cells = row.find_all('td')
        strikes += remove_non_ints(cells[3].find('p').text)
        takedowns += remove_non_ints(cells[4].find('p').text)
        time = remove_whitespace(cells[9].find('p').text)
        minutes += (remove_non_ints(cells[8].find('p').text) - 1) * 5 + int(time.split(':')[0]) + (int(time.split(':')[1]) / 60)

    return strikes / minutes, takedowns / minutes

def get_fighter_attributes(name: str) -> tuple:
    r = requests.get(fighter_page_urls[name])
    soup = BeautifulSoup(r.text, 'lxml')

    attributes = soup.find('div', {'class' : 'b-list__info-box b-list__info-box_style_small-width js-guide'}).find('ul').find_all('li')
    height = str(remove_non_ints(attributes[0].text))
    height_inches = int(height[0]) * 12 + int(height[1:])
    reach = remove_non_ints(attributes[2].text)
    birthday = datetime.strptime(remove_whitespace(attributes[4].text).split(':')[1], '%b %d, %Y')
    age = (datetime.now() - birthday).total_seconds() / 86400 / 365

    return height_inches, reach, age

def get_opponent_prior_wins(event: str, opponent: str) -> tuple:
    wins = 0

    r = requests.get(fighter_page_urls[opponent])
    soup = BeautifulSoup(r.text, 'lxml')
    table = BeautifulSoup(requests.get(fighter_page_urls[opponent]).text, 'lxml').find('table', {'class' : 'b-fight-details__table b-fight-details__table_style_margin-top b-fight-details__table_type_event-details js-fight-table'}).find('tbody').find_all('tr')[:0:-1]
    end_index = [n for n, x in enumerate(table) if x.find_all('td')[0].find('p').find('a').find('i').find('i').text != 'next' and x.find_all('td')[6].find('p').find('a').text == event][0]
    for row in table[:end_index]:
        if row.find('td').find('p').find('a').find('i').find('i').text == 'win':
            wins += 1

    return wins

def get_fighter_data(fighter) -> list:
    r = requests.get(fighter_page_urls[fighter])
    soup = BeautifulSoup(r.text, 'lxml')
    table = soup.find('table', {'class' : 'b-fight-details__table b-fight-details__table_style_margin-top b-fight-details__table_type_event-details js-fight-table'}).find('tbody').find_all('tr')[:0:-1]

    stats = {'Wins': 0, 'Losses': 0, 'Finishes': 0, 'Finished': 0, 'Opponent Prior Wins': 0}
    try:
        if len(table) >= 5:
            for i, fight in enumerate(table[-5:]):
                fight_cells = fight.find_all('td')

                if i < 4:
                    if 'DQ' not in fight_cells[7].find('p').text:
                        if fight_cells[0].find('p').find('a').find('i').find('i').text == 'win':
                            stats['Wins'] += 1

                            if 'KO/TKO' in fight_cells[7].find('p').text or 'SUB' in fight_cells[7].find('p').text:
                                stats['Finishes'] += 1
                        elif fight_cells[0].find('p').find('a').find('i').find('i').text == 'loss':
                            stats['Losses'] += 1

                            if 'KO/TKO' in fight_cells[7].find('p').text or 'SUB' in fight_cells[7].find('p').text:
                                stats['Finished'] += 1

                elif fight_cells[0].find('p').find('a').find('i').find('i').text == 'next':
                    fight_cells = table[-6].find_all('td')

                    if 'DQ' not in fight_cells[7].find('p').text:
                        if fight_cells[0].find('p').find('a').find('i').find('i').text == 'win':
                            stats['Wins'] += 1

                            if 'KO/TKO' in fight_cells[7].find('p').text or 'SUB' in fight_cells[7].find('p').text:
                                stats['Finishes'] += 1
                        elif fight_cells[0].find('p').find('a').find('i').find('i').text == 'loss':
                            stats['Losses'] += 1

                            if 'KO/TKO' in fight_cells[7].find('p').text or 'SUB' in fight_cells[7].find('p').text:
                                stats['Finished'] += 1
                else:
                    fight_cells = table[-1].find_all('td')

                    if 'DQ' not in fight_cells[7].find('p').text:
                        if fight_cells[0].find('p').find('a').find('i').find('i').text == 'win':
                            stats['Wins'] += 1

                            if 'KO/TKO' in fight_cells[7].find('p').text or 'SUB' in fight_cells[7].find('p').text:
                                stats['Finishes'] += 1
                        elif fight_cells[0].find('p').find('a').find('i').find('i').text == 'loss':
                            stats['Losses'] += 1

                            if 'KO/TKO' in fight_cells[7].find('p').text or 'SUB' in fight_cells[7].find('p').text:
                                stats['Finished'] += 1

                curr_opponent = remove_whitespace(fight_cells[1].find_all('p')[1].text)
                stats['Opponent Prior Wins'] += get_opponent_prior_wins(fight_cells[6].find('p').find('a').text, curr_opponent)

            height, reach, age = get_fighter_attributes(fighter)
            strikes_pm, takedowns_pm = get_prior_fight_stats(fighter)

            return reach, stats['Wins'], stats['Losses'], stats['Finishes'], stats['Finished'], stats['Opponent Prior Wins'], strikes_pm, takedowns_pm

    except Exception as e:
        pass

    return None

if __name__ == '__main__':
    fighters = []
    fighter_page_urls = {}
    with open('../data/fighter_ufc_stats_pages.csv', newline='') as f:
        for row in csv.reader(f):
            fighters.append(row[0])
            fighter_page_urls[row[0]] = row[1]

    db = mysql.connector.connect(
        host='us-cdbr-east-05.cleardb.net',
        user=os.environ.get('DB_USER'),
        passwd=os.environ.get('DB_PASS'),
        database='heroku_6b97baa7d0c1585'
    )

    mycursor = db.cursor()

    for fighter in fighters:
        data = get_fighter_data(fighter)
        if data != None:
            sql_string = "INSERT INTO fighterdata (Name, Reach, RecentWins, RecentLosses, RecentFinishes, RecentTimesFinished, RecentOpponentWins, StrikesPerMinute, TakedownsPerMinute) VALUES {}".format((fighter,) + data)
            mycursor.execute(sql_string)

            db.commit()
