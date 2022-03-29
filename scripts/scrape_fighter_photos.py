import requests
from bs4 import BeautifulSoup

def get_photo_url(fighter):
    r = requests.get('https://www.ufc.com/athlete/{}'.format(fighter.replace(' ', '-')))
    soup = BeautifulSoup(r.text, 'lxml')

    try:
        image_url = soup.find('div', {'class' : 'c-bio__image'}).find('img').get('src')

        return image_url

    except Exception as e:
        return 'https://i.ibb.co/vYB53Kw/Untitled-1.png'

if __name__ == '__main__':
    print(get_photo_url('Conor McGregor'))
