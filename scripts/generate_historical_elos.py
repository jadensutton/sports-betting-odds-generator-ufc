import requests

import pandas as pd

from bs4 import BeautifulSoup

def remove_whitespace(s: str) -> str:
    s = s.replace('\n', '')
    s = ''.join([char for x, char in enumerate(s) if (x != len(s) - 1 and x != 0) and (char != ' ' or (s[x + 1] != ' ' and s[x - 1] != ' '))])

    return s

def generate_historical_elos():
    elos = {}

    #Get all events in UFC history in ascending order then iterate through them
    r = requests.get('http://www.ufcstats.com/statistics/events/completed?page=all')
    soup = BeautifulSoup(r.text, 'lxml')

    events = soup.find('table', {'class': 'b-statistics__table-events'}).find('tbody').find_all('tr')
    event_urls = [event.find('td').find('i').find('a').get('href') for event in reversed(events[2:])]
    for url in event_urls:
        #Get table of fights in each event then iterate through them
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        
        fights = soup.find('table', {'class': 'b-fight-details__table b-fight-details__table_style_margin-top b-fight-details__table_type_event-details js-fight-table'}).find('tbody').find_all('tr')
        for fight in reversed(fights):
            #Check if fight was a DQ or ended in a draw/no-contest (No ELO adjustment)
            if len(fight.find_all('td')[0].find_all('p')) == 1 and 'DQ' not in fight.find_all('td')[7].find('p').text:
                #Find the winner and loser and adjust their ELOS
                winner = remove_whitespace(fight.find_all('td')[1].find_all('p')[0].find('a').text)
                loser = remove_whitespace(fight.find_all('td')[1].find_all('p')[1].find('a').text)

                if winner not in elos:
                    elos[winner] = [1500]
                if loser not in elos:
                    elos[loser] = [1500]

                e_w = 1 / (1 + 10 ** ((elos[loser][-1] - elos[winner][-1]) / 400))
                e_l = 1 - e_w

                elos[winner].append(elos[winner][-1] + 32 * (1 - e_w))
                elos[loser].append(elos[loser][-1] - 32 * (e_l))

    return elos

if __name__ == '__main__':
    elos = generate_historical_elos()
    pd.DataFrame.from_dict(data=elos, orient='index').to_csv('data/fighter_historical_elos.csv', header=False)