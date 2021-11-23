#автомAтизировать headers
from os import write
import requests
# from requests.sessions import BaseAdapter
from bs4 import BeautifulSoup
import json


rs = requests.Session()
lkeys = []
lvals = []
log,pas = 'log', 'pas'
allow_destinations = [
    'Санкт', 'Ленинградская обл',
    'Москов','Москва',
    'Сарат','Самар',
    'уфа',#придумать радиус
    'Свердлов', 'Екатеринбург',
    'Татарстан',
    'Удмурт',
    'Киров' , 'Перм' ,
    'Тюмен' , 'Омск' , 'Новосиб'
]
redCities = {
    'Ижевск':'иж',
    'Санкт-Петербург':'СПб',
    'Московск':'МО',
    'Москва':'МСК',
    'Екатеринбург':'Екб',
    'Новосибирск':'Новосиб',
    'Челябинск':'Челяба',
    'Набережные':'Н.Челны',
    'Пермь':'Пермь',
}
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

def get_token():#Возвращает токен с сайта из куков в формате str
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
        'username' : log,
        'password' : pas
    }
    data = rs.post('https://www.atrucks.su/user/login/',data=data, headers=headers)
    if data.status_code == 200: # доказано что нефакт. Подумать как сделать точнее, либо связать с check_session()
        print('log: Успешная авторизация')
        return data
    else:
        print('log: Авторизация неудалась!')

def check_session():
    # <i class="fa fa-sign-out"></i>
    data = rs.get('https://www.atrucks.su/carrier/') #главная страница в кабинете ( есть вывод имени в странице )
    soup = BeautifulSoup(data.text, 'html.parser')
    res = soup.find('i', {'class':'fa fa-sign-out'})
    if res!=None:
        print('log: Сессия активна!')
        return True
    else:
        print('log: Сессия неактивна, нужна авторизация')       
        get_auth() #неуверен нужно ли..
        
#запускает до авторизации.
# check_session()

#перебор заказчиков в кабинете
#https://www.atrucks.su/carrier/auctions/
def get_ca_and_ids():
    lnc, lic = [], []

    if check_session():
        data = rs.get('https://www.atrucks.su/carrier/auctions/').text
        soup = BeautifulSoup(data,'html.parser')
        resName = soup.findAll('span',{'class':'name'})
        local_step = 0
        #Name
        for item_name in resName:
            if local_step > 1:#2 индекса пропустить :)
                # print(item_name.text) # название конторы
                lnc.append(item_name.text)
            local_step+=1
        #ID
        resIds = soup.findAll('span', {'class':'favorite'})
        for item_idc in resIds:
            item_idc = item_idc.get('data-id')
            lic.append(item_idc)
        return dict(zip(lic, lnc))

check_session()#запускаем

data_comps = get_ca_and_ids()

#посокращать имена городов: Санкт-Петербург - СПБ. Ленинградская обл. - (ЛО), Екатеринбург - Екат ит.д

def check_city_in_RC(city):#сокращение :)
    for x in redCities:   
        if x.lower() in city.lower():
            city=redCities[x]
    return city

def check_city_in_RC_in(city):#сокращение :)
    req = city
    for i, x in redCities.items():
        if city.lower() in x.lower():
            req = i
    return req

def check_city_in_allowCities(city): # city is: Московская обл, г Ногинск, Липецкая обл, г Липецк, etc
    for x in allow_destinations: 
        if x.lower() in city.lower():
            return True
    return False

#перебираем даты
def gen_datas(data_load):
    if len(data_load) == 10:# d1 = 'чч.мм.дддд' #10
        outData = data_load[0:5] #V
    elif len(data_load) == 16:# d2 = 'чч.мм.дддд чч:мм' #16
        outData = data_load[0:5]
    elif len(data_load) == 23:# d3 = 'чч.мм.дддд - чч.мм.дддд' #23
        tmpd = data_load.split('—')
        # print(tmpd)
        outData = tmpd[0][0:5]+'—'+tmpd[1][1:6]
    elif len(data_load) == 35:# d4 = 'чч.мм.дддд ча:ми - чч.мм.дддд ча:ми' #35  
        tmpd = data_load.split('—')
        outData = str(tmpd[0][0:5]+'—'+tmpd[1][1:6])
    return outData #---------------------------------------------------------------дата погрузки

# пробуем обрабатывать
def pars_1(city = 'None', per_page = 300): # None - общая по дефолту, не разбирал строку особо, возможн оможно сделать иначе, хз
    data = rs.get(f'https://www.atrucks.su/carrier/auctions/lots/general/quick/?page=1&per_page={per_page}&sort%5B%5D=load_range&ids=&mds=')
    jat = json.loads(data.text) 
    st, sum_auc = 0, 0
    ret_list = []
    ret_list_link = []
    # перебор лотов
    # ввод сокращенного варианта в аську. Обработка:
    # print('Было:',city)
    city = check_city_in_RC_in(city)
    # print('стало:',city)
    for lot in jat['lots']:
        
        en_pl = ' '.join(lot['destinations']) 
        if check_city_in_allowCities( en_pl ):
            #проверка на встречку
            bvstr = ''
            if("wait_for_bids" in lot):
                bvstr='встречка открыта'
            else:
                bvstr='встречка закрыта'
            #
            comp_name = data_comps[str(lot['company_id'])]
            if 'labels' in lot:
                comment = lot['labels']
                comment = str(comment).split(':')
                comment = comment[-1].split('}')
                comment = comment[0]
            else:
                comment = ''
            id_z = lot['text_id'] #-------------------------------------------------------------ид заказа
            linkId = lot['id']
            # data_load = lot['load_range'] #---------------------------------------------------дата погрузки
            data_load = gen_datas(str(lot['load_range']))
            st_pl = ''.join(lot['origins']) #---------------------------------------------------где грузимся
            st_pl = check_city_in_RC(st_pl)
            en_pl = check_city_in_RC(en_pl)
            st_price = lot['start_price']#------------------------------------------------------стоимость(заказчик)
            st_price /= 1000
            if float(st_price % 1 ) == 0 and st_price != 0:
                st_price = int(st_price)
            if st_price == 0 or st_price == '' or st_price == None:
                st_price = 'Ожидает ставок'
            if st_price != 'Ожидает ставок':
                st_price = str(st_price) + ' тыр' 

            
            curr = lot['currency'] #------------------------------------------------------------валюта
            tr_need = lot['transport']['transport:truck_mode']  #-------------------------------требуемый транспорт
            tr_need_d = lot['transport']['transport:truck_kinds'] #-----------------------------доп к транспорту
            ret_Str = str(data_load) + \
                    ' ' + str(st_pl)+'->'+str(en_pl)+ \
                        ', '+str(st_price)+ ', ' +str(bvstr) + ' ' +\
                            ' ' + str(tr_need) + '/' + str(tr_need_d) + ' [' + comp_name +'] '+id_z
            if city == 'None': # все города погрузки
                sum_auc += 1
                ret_list.append(ret_Str)
                ret_list_link.append(int(linkId))
            elif city.lower() in str(st_pl.lower()):
                sum_auc += 1
                ret_list.append(ret_Str)
                ret_list_link.append(int(linkId))
            
            
    ret_list.append('По запросу итого аукционов: '+str(sum_auc))#вне цикла
    ret_list_link.append(0)
    ret_dict = dict(zip(ret_list, ret_list_link))
    return ret_dict

# print(pars_1(city='елабуг'))