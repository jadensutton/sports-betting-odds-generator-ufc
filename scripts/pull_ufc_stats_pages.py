import csv

import pandas as pd

from googlesearch import search
from time import sleep

def get_fighter_page(name: str):
    success = False
    while success is False:
        try:
            query = 'site:ufcstats.com ' + name

            url = None
            for j in search(query, tld='co.in', num=10, stop=1, pause=2):
                url = j

            success = True

        except Exception as e:
            print(e)
            print('Trying again in 10m...')
            sleep(600)

    return url

if __name__ == '__main__':
    pages = {}

    fighters = []
    with open('../data/fighters.csv', newline='') as f:
        for row in csv.reader(f):
            fighters.append(row[0])

    for n, fighter in enumerate(fighters):
        print('{}% finished'.format(100 * round(n / len(fighters), 2)))
        pages[fighter] = get_fighter_page(fighter)

    pd.DataFrame.from_dict(data=pages, orient='index').to_csv('../data/fighter_ufc_stats_pages.csv', header=False)
