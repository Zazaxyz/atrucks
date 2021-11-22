#автомAтизировать headers
from os import write
import requests
# from requests.sessions import BaseAdapter
from bs4 import BeautifulSoup
import json


rs = requests.Session()
lkeys = []
lvals = []
log,pas = 'log', 'pass'
#хэдер, без него не работает. надо придумать как вытащить из куков  /  вставлять из data.header запроса get
#возможно не работало из-за типов данных. тут в словаре все строка. из хедера сессии возможно тип другой, проверить опосля...

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
check_session()

#перебор заказчиков в кабинете
#https://www.atrucks.su/carrier/auctions/
def check_comps_and_ids():
    list_name_company = []
    list_id_company = []
    content = rs.get('https://www.atrucks.su/carrier/auctions/',headers=headers).text
    soup = BeautifulSoup(content, 'html.parser')
    result_name = soup.findAll('span', {'class':'name'})
    local_step = 0
    for item_name in result_name:
        if local_step > 1:#2 индекса пропустить :)
            #print(item_name.text) # название конторы
            list_name_company.append(item_name.text)
        local_step+=1

    result_idc = soup.findAll('span', {'class':'favorite'})
    for item_idc in result_idc:    
        item_idc = item_idc.get('data-id')
        #print(item_idc) # ид конторы( ИЗБРАННОЕ И ОБЩАЯ ПРОПУСКАЕТСЯ !!!! пересчитать списки на всяк случай)
        list_id_company.append(item_idc)

    # print(len(result_name), len(result_idc)) #на 2 больше, учитывать!
    # склеиваем 
    dict_companys = dict(zip(list_id_company,list_name_company)) #ключ сделать айди. Поскольку в парсе значение приходит именно айдишником заказчика
    # for x in dict_companys:
    #     print(x,'>>>',dict_companys[x])
    return dict_companys

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
            #print(item_idc) # ид конторы( ИЗБРАННОЕ И ОБЩАЯ ПРОПУСКАЕТСЯ !!!! пересчитать списки на всяк случай)
            lic.append(item_idc)
        return dict(zip(lic, lnc))


check_session()

data_comps = get_ca_and_ids()


def send_out(comp_name,id_z, data_load, st_pl, en_pl, st_price, curr, tr_need, tr_need_d, bvstr, comment):
    print(f'{comp_name,id_z}',data_load,'|',st_pl,'-',en_pl,'|',st_price,curr,'|',tr_need,tr_need_d, '|',bvstr,comment)\
    #посокращать имена городов: Санкт-Петербург - СПБ. Ленинградская обл. - (ЛО), Екатеринбург - Екат ит.д



# пробуем обрабатывать
def pars_1(city = 'None', per_page = 300): # None - общая по дефолту, не разбирал строку особо, возможн оможно сделать иначе, хз
    data = rs.get(f'https://www.atrucks.su/carrier/auctions/lots/general/quick/?page=1&per_page={per_page}&sort%5B%5D=load_range&ids=&mds=')
    jat = json.loads(data.text) 
    st, sum_auc = 0, 0
    ret_list = []
    # перебор лотов
    for lot in jat['lots']:
    #проверка на встречку
        bvstr = ''
        if("wait_for_bids" in lot):
            bvstr='встречка открыта'
        else:
            bvstr='встречки нету'
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
        data_load = lot['load_range'] #-----------------------------------------------------дата погрузки
        st_pl = ''.join(lot['origins']) #---------------------------------------------------где грузимся
        en_pl = lot['destinations'] #-------------------------------------------------------выгрузка
        st_price = lot['start_price']#------------------------------------------------------стоимость(заказчик)
        curr = lot['currency'] #------------------------------------------------------------валюта
        tr_need = lot['transport']['transport:truck_mode']  #-------------------------------требуемый транспорт
        tr_need_d = lot['transport']['transport:truck_kinds'] #-----------------------------доп к транспорту
        # print(st_pl, type(st_pl))
        
        if city == 'None': # все города погрузки
            sum_auc += 1
            ret_list.append(str(comp_name) +' > ' + str(id_z) + \
                ' > ' + str(data_load) + ' > ' + str(st_pl) + \
                ' > ' + str(en_pl) +' > ' + str(st_price) + \
                ' > ' + str(curr) +' > ' + str(tr_need) + \
                ' > ' + str(tr_need_d) +' > ' + str(bvstr) +' > ' + str(comment))
            # print(ret_list)
            # send_out(comp_name,id_z, data_load, st_pl, en_pl, st_price, curr, tr_need, tr_need_d, bvstr, comment)
        elif city.lower() in str(st_pl.lower()):
            sum_auc += 1
            ret_list.append(str(comp_name) +' > ' + str(id_z) + \
                ' > ' + str(data_load) + ' > ' + str(st_pl) + \
                ' > ' + str(en_pl) +' > ' + str(st_price) + \
                ' > ' + str(curr) +' > ' + str(tr_need) + \
                ' > ' + str(tr_need_d) +' > ' + str(bvstr) +' > ' + str(comment))
            # print(ret_list)
            # send_out(comp_name,id_z, data_load, st_pl, en_pl, st_price, curr, tr_need, tr_need_d, bvstr, comment)
    print("По запросу итого аукционов: ",'>>>',sum_auc)
    return ret_list

#предполагаю высокую нагрузку из-за вызова функции вывода.
# то что спарсили, в словарь, и передовать на вывод словарь. Так вызовем только 1 раз функцию. сделать потом
# фильтрация выгрузок.....

# print(pars_1(city='москва')) # оно работает :))

