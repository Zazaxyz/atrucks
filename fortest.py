from os import write
import requests
# from requests.sessions import BaseAdapter
from bs4 import BeautifulSoup

rs = requests.Session()
lkeys = []
lvals = []
headers = {
    'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Content-Length': '127',
    'Origin': 'https://www.atrucks.su',
    'Connection': 'keep-alive',
    'Referer': 'https://www.atrucks.su/user/login/'
    }
current_headers = {}


def get_token():
#Возвращает токен с сайта из куков в формате str
    data = rs.get('https://www.atrucks.su/user/login/')
    for x in data.headers:
        if 'Set-Cookie' in x:
            token_data = data.headers[x]
            token_data = token_data.split()
            for x in token_data:
                if 'csrftoken' in x:
                    x = x.split('=')
                    result = x[1].split(';')
                    result = result[0]
                    return result
                    break # result прерывает цикл???
            break

def get_auth():
    token = get_token()
    data = {
        'csrfmiddlewaretoken' : token, 
        'username' : 'my_login',
        'password' : 'my_password'
    }
    data = rs.post('https://www.atrucks.su/user/login/',data=data, headers=headers)
    if data.status_code == 200:
        print('log: Успешная авторизация')
        return data
    else:
        print('log: Авторизация неудалась!')

def check_session():
    # <i class="fa fa-sign-out"></i>
    data = rs.get('https://www.atrucks.su/carrier/')
    soup = BeautifulSoup(data.text, 'html.parser')
    res = soup.find('i', {'class':'fa fa-sign-out'})
    if res!=None:
        print('log: Сессия активна!')
    else:
        print('log: Сессия неактивна, нужна авторизация')
        get_auth()

check_session()

def check_comps_and_ids():
    pass

def get_auctions(city='None'):
    pass
    