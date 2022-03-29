import pandas as pd
import requests

from bs4 import BeautifulSoup

def remove_non_ints(s: str) -> int:
    return int(''.join([int(c) for c in s.split() if c.isdigit()]))

def pull_fighters():
    fighters = []

    pages = [char for char in 'abcdefghijklmnopqrstuvwxyz']
    for page in pages:
        r = requests.get('http://ufcstats.com/statistics/fighters?char={}&page=all'.format(page))
        soup = BeautifulSoup(r.text, 'lxml')
        table = soup.find('table', {'class' : 'b-statistics__table'}).find('tbody').find_all('tr')[1:]
        for row in table:
            cells = row.find_all('td')
            if '-' not in cells[3].text and '-' not in cells[5].text and remove_non_ints(cells[7].text) + remove_non_ints(cells[8].text) + remove_non_ints(cells[9].text) >= 5:
                name = '{first} {last}'.format(first=cells[0].find('a').text, last=cells[1].find('a').text)
                fighters.append(name)

    return fighters

if __name__ == '__main__':
    fighters = pull_fighters()
    df = pd.DataFrame(fighters, columns=['name'])
    df.to_csv('../data/fighters.csv', index=False)
