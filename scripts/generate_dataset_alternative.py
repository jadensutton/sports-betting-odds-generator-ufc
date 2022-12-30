import csv
import requests

import pandas as pd

from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep

def remove_non_ints(s: str) -> int:
    if '-' in s:
        return 0

    return int(''.join([str(c) for c in s if c.isdigit()]))

def remove_whitespace(s: str) -> str:
    s = s.replace('\n', '')
    s = ''.join([char for x, char in enumerate(s) if (x != len(s) - 1 and x != 0) and (char != ' ' or (s[x + 1] != ' ' and s[x - 1] != ' '))])

    return s

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

def get_prior_fight_stats(name: str, event: str) -> tuple:
    strikes = 0
    takedowns = 0
    minutes = 0

    r = requests.get(fighter_page_urls[name])
    soup = BeautifulSoup(r.text, 'lxml')
    table = soup.find('table', {'class' : 'b-fight-details__table b-fight-details__table_style_margin-top b-fight-details__table_type_event-details js-fight-table'}).find('tbody').find_all('tr')[:0:-1]
    end_index = [n for n, x in enumerate(table) if x.find_all('td')[0].find('p').find('a').find('i').find('i').text != 'next' and x.find_all('td')[6].find('p').find('a').text == event][0]
    for row in table[end_index - 3:end_index]:
        cells = row.find_all('td')
        strikes += remove_non_ints(cells[3].find('p').text)
        takedowns += remove_non_ints(cells[4].find('p').text)
        time = remove_whitespace(cells[9].find('p').text)
        minutes += (remove_non_ints(cells[8].find('p').text) - 1) * 5 + int(time.split(':')[0]) + (int(time.split(':')[1]) / 60)

    return strikes / minutes, takedowns / minutes

def get_opponent_prior_wins(event: str, opponent: str) -> tuple:
    wins = 0

    r = requests.get(fighter_page_urls[opponent])
    soup = BeautifulSoup(r.text, 'lxml')
    table = soup.find('table', {'class' : 'b-fight-details__table b-fight-details__table_style_margin-top b-fight-details__table_type_event-details js-fight-table'}).find('tbody').find_all('tr')[:0:-1]
    end_index = [n for n, x in enumerate(table) if x.find_all('td')[0].find('p').find('a').find('i').find('i').text != 'next' and x.find_all('td')[6].find('p').find('a').text == event][0]
    for row in table[:end_index]:
        if row.find('td').find('p').find('a').find('i').find('i').text == 'win':
            wins += 1

    return wins

def generate_dataset(fighters: list):
    fight_data = []
    fights = []

    for p, fighter in enumerate(fighters):
        try:
            r = requests.get(fighter_page_urls[fighter])
            soup = BeautifulSoup(r.text, 'lxml')
            table = soup.find('table', {'class' : 'b-fight-details__table b-fight-details__table_style_margin-top b-fight-details__table_type_event-details js-fight-table'}).find('tbody').find_all('tr')[:0:-1]
            for n, row in enumerate(table):
                if n < len(table) - 5 and table[n + 5].find_all('td')[0].find('p').find('a').find('i').find('i').text != 'next':
                    cells = table[n + 5].find_all('td')
                    opponent = remove_whitespace(cells[1].find_all('p')[1].text)
                    if opponent in fighters and {fighter, opponent} not in fights:
                        a_stats = {'Wins': 0, 'Finishes': 0, 'Finished': 0, 'Opponent Prior Wins': 0}
                        b_stats = {'Wins': 0, 'Finishes': 0, 'Finished': 0, 'Opponent Prior Wins': 0}
                        fight_sequence_valid = True
                        for i, fight in enumerate(table[n:n + 5]):
                            fight_cells = fight.find_all('td')

                            if 'DQ' not in fight_cells[7].find('p').text:
                                if fight_cells[0].find('p').find('a').find('i').find('i').text == 'win':
                                    a_stats['Wins'] += 1

                                    if 'KO/TKO' in fight_cells[7].find('p').text or 'SUB' in fight_cells[7].find('p').text:
                                        a_stats['Finishes'] += 1
                                elif 'KO/TKO' in fight_cells[7].find('p').text or 'SUB' in fight_cells[7].find('p').text:
                                        a_stats['Finished'] += 1

                                curr_opponent = remove_whitespace(fight_cells[1].find_all('p')[1].text)
                                if curr_opponent in fighters:
                                    a_stats['Opponent Prior Wins'] += get_opponent_prior_wins(fight_cells[6].find('p').find('a').text, curr_opponent)

                        table_b = BeautifulSoup(requests.get(fighter_page_urls[opponent]).text, 'lxml').find('table', {'class' : 'b-fight-details__table b-fight-details__table_style_margin-top b-fight-details__table_type_event-details js-fight-table'}).find('tbody').find_all('tr')[:0:-1]
                        curr_fight_index = [i for i, x in enumerate(table_b) if remove_whitespace(x.find_all('td')[1].find_all('p')[1].find('a').text) == fighter][0]
                        if curr_fight_index < 5:
                            fight_sequence_valid = False

                        else:
                            for i, fight in enumerate(table_b[curr_fight_index - 5:curr_fight_index]):
                                fight_cells = fight.find_all('td')

                                if 'DQ' not in fight_cells[7].find('p').text:
                                    if fight_cells[0].find('p').find('a').find('i').find('i').text == 'win':
                                        b_stats['Wins'] += 1

                                        if 'KO/TKO' in fight_cells[7].find('p').text or 'SUB' in fight_cells[7].find('p').text:
                                            b_stats['Finishes'] += 1
                                    elif 'KO/TKO' in fight_cells[7].find('p').text or 'SUB' in fight_cells[7].find('p').text:
                                            b_stats['Finished'] += 1

                                b_stats['Opponent Prior Wins'] += get_opponent_prior_wins(fight_cells[6].find('p').find('a').text, remove_whitespace(fight_cells[1].find_all('p')[1].text))

                        if fight_sequence_valid is True:
                            fights.append({fighter, opponent})

                            event = cells[6].find('p').find('a').text

                            fighter_elo = float(historical_fighter_elos[fighter][n + 5])
                            opponent_elo = float(historical_fighter_elos[opponent][curr_fight_index])

                            height_a, reach_a, age_a = get_fighter_attributes(fighter)
                            height_b, reach_b, age_b = get_fighter_attributes(opponent)
                            strikes_pm_a, takedowns_pm_a = get_prior_fight_stats(fighter, event)
                            strikes_pm_b, takedowns_pm_b = get_prior_fight_stats(opponent, event)

                            if len(cells[0].find_all('p')) == 1:
                                result = 1  if cells[0].find('p').find('a').find('i').find('i').text == 'win' else 0
                                fight_data.append([fighter_elo - opponent_elo, age_a - age_b, reach_a - reach_b, a_stats['Wins'] - b_stats['Wins'], a_stats['Finishes'] - b_stats['Finishes'], a_stats['Finished'] - b_stats['Finished'], a_stats['Opponent Prior Wins'] - b_stats['Opponent Prior Wins'], strikes_pm_a - strikes_pm_b, takedowns_pm_a - takedowns_pm_b, result])

        except Exception as e:
            print(e)

    return fight_data

if __name__ == '__main__':
    fighters = []
    fighter_page_urls = {}
    with open('data/fighter_ufc_stats_pages.csv', newline='') as f:
        for row in csv.reader(f):
            fighters.append(row[0])
            fighter_page_urls[row[0]] = row[1]

    historical_fighter_elos = {}
    with open('data/fighter_historical_elos.csv', newline='') as f:
        for row in csv.reader(f):
            historical_fighter_elos[row[0]] = row[1:]

    dataset = generate_dataset(fighters)
    df = pd.DataFrame(dataset, columns=['elo_diff', 'age_diff', 'reach_diff','5f_win_diff','5f_finish_diff','5f_finished_diff','5f_opp_win_diff','strpm_diff','tdpm_diff','result'])
    df.to_csv('data/train_v3.csv', index=False)
 