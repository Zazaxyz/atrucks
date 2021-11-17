###СТАРЫЙ ПАРСЕР. РАБОТАЕТ, НО ВОЗМОЖНО Я ЧТО-ТО СЛОМАЛ ))
import requests
from bs4 import BeautifulSoup
import json 


url = 'https://www.atrucks.su/user/login/'
token = 'csrftoken'
rs = requests.Session()
my_login = 'my_login'
my_password = 'my_password'

# print(data.headers)
lkeys = []
lvals = []

token_data = ''


def get_head(url):
    #get token
    data = rs.get(url)
    return data.headers


def get_token(url):
    data = get_head(url=url)
    step = 0
    for x in data:
        lkeys.append(x)
        lvals.append(data[x])
        if 'Set-Cookie' in lkeys[step]:
            token_data = lvals[step]
        step+=1
        #Неправильно сделал, слетело по айди. генерятся по разному, либо лыжи не едут, хз. ПЕРЕДЕЛАТЬ ПО СОВПАДЕНИЮ!!!
    token_data = token_data.split()
    token_data = token_data[8].split('=')
    token_data = token_data[1].split(';')
    token = token_data[0]
    #data 
    #csrfmiddlewaretoken : token 
    #username : login
    #password : pass
    #header = dict(zip(lkeys,lvals))
    data = {
        'csrfmiddlewaretoken' : token, 
        'username' : my_login, #
        'password' : my_password #
    }

    return data

def get_name_and_ids_companys(content):
    list_name_company = []
    list_id_company = []
    content = content
    soup = BeautifulSoup(content, 'html.parser')
    result_name = soup.findAll('span', {'class':'name'})
    local_step = 0
    for item_name in result_name:
        if local_step > 1:
            #print(item_name.text) # название конторы
            list_name_company.append(item_name.text)
        local_step+=1

    result_idc = soup.findAll('span', {'class':'favorite'})
    for item_idc in result_idc:    
        item_idc = item_idc.get('data-id')
        #print(item_idc) # ид конторы( ИЗБРАННОЕ И ОБЩАЯ ПРОПУСКАЕТСЯ !!!! пересчитать списки на всяк случай)
        list_id_company.append(item_idc)

    # print(len(result_name), len(result_idc))
    # склеиваем 
    dict_companys = dict(zip(list_id_company,list_name_company))
    # for x in dict_companys:
    #     print(x,'>>>',dict_companys[x])
    return dict_companys


data = get_name_and_ids_companys('https://www.atrucks.su/carrier/auctions/')


def get_content(url):
    data = get_token(url=url)
    atrucks_data = rs.post(url=url,data=data, headers={
    'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Content-Length': '127',
    'Origin': 'https://www.atrucks.su',
    'Connection': 'keep-alive',
    'Referer': 'https://www.atrucks.su/user/login/'
})
    if atrucks_data.status_code == 200:
        print('Успешно авторизовались')
        #https://www.atrucks.su/carrier/auctions/quick/ ---- общая
        #https://www.atrucks.su/carrier/auctions/lots/general/quick/?page=1&per_page=300&sort%5B%5D=load_range&ids=&mds= ---- запрос json
        auction_at_data = rs.get('https://www.atrucks.su/carrier/auctions/lots/general/quick/?page=1&per_page=300&sort%5B%5D=load_range&ids=&mds=')
        jat = json.loads(auction_at_data.text) 
        st = 0
        # перебор лотов
        for lot in jat['lots']:
            #проверка на встречку
            bvstr = ''
            if("wait_for_bids" in lot):
                bvstr='встречка открыта'
            else:
                bvstr='встречки нету'
            #проверка заказчика
            #надо сделать парсинг https://www.atrucks.su/carrier/auctions/
            #class="col-md-2 col-sm-3 col-xs-6 partners-item"
            # <a href="/carrier/auctions/quick/1266/">
            # <span class="img-thumbnail img-partner" style="background-image: url(/media/0/2/b862-6fba-4c7a-a188-433521799486.jpg)">
            #     <span title="Добавить/убрать из избранных" data-url="/company-info/favorite/1266/add/" data-id="1266" class="favorite js-favorite-change  noactive ">
            #         <i class="fa fa-star" aria-hidden="true"></i>
            #         <i class="fa fa-star-o" aria-hidden="true"></i>
            #     </span>
            #     </span>
            #     <span class="name">Акрон</span>
            # </a>
            #comp name : id 
            get_name_and_ids_companys = get_content('https://www.atrucks.su/carrier/auctions/')
            
            #перебрать заказчиков
            #тут возможно я все сломал, не проверял
            comp_name = str(get_name_and_ids_companys.get(lot['company_id']))
           

            # #lot["company_id"]
            # comp_name = ''
            # if lot["company_id"] == 1266:#1
            #     comp_name = 'Акрон'
            # elif lot["company_id"] == 7755:#2
            #     comp_name = 'Бергауф'
            # elif lot["company_id"] == 2580:#3
            #     comp_name = 'Евраз ЭМИ'
            # elif lot["company_id"] == 425:#4
            #     comp_name = 'ЕК Кемикал'
            # elif lot["company_id"] == 9179:#5
            #     comp_name = 'Завод Стройдеталь'
            # elif lot["company_id"] == 311:#6
            #     comp_name = 'ИжНефтемаш'
            # elif lot["company_id"] == 378:#7
            #     comp_name = 'Картли'
            # elif lot["company_id"] == 4083:#8
            #     comp_name = 'Ника'
            # elif lot["company_id"] == 8662:#9
            #     comp_name = 'Нефикс Косметикс'
            # elif lot["company_id"] == 3580:#10
            #     comp_name = 'Сармол'
            # elif lot["company_id"] == 1258:#11
            #     comp_name = 'Сатурн'
            # elif lot["company_id"] == 2102:#12
            #     comp_name = 'Свет'
            # elif lot["company_id"] == 6734:#13
            #     comp_name = 'Сокол Яр'
            # elif lot["company_id"] == 8677:#14
            #     comp_name = 'ТД ММК'
            # elif lot["company_id"] == 7968:#15
            #     comp_name = 'Уральский Лес'
            # elif lot["company_id"] == 792:#16
            #     comp_name = 'Хаят'
            # elif lot["company_id"] == 8556:#17
            #     comp_name = 'Холдинг Альфа'
            # elif lot["company_id"] == 3137:#18
            #     comp_name = 'ЭмСи Баухеми'
            # else:
            #     comp_name = 'None!'
            # проверка на комм
            if 'labels' in lot:
                comment = lot['labels']
                comment = str(comment).split(':')
                #llist = [{'color'", " '#d16566', 'name'", " 'Особые условия!!!'}]
                comment = comment[-1].split('}')
                comment = comment[0]
                # print(comment[0]) # ---- очищенный комм.
            #comp_name
            id_z = lot['text_id'] #ид заказа
            data_load = lot['load_range'] #дата погрузки
            st_pl = lot['origins'] # где грузимся
            en_pl = lot['destinations'] # выгрузка
            st_price = lot['start_price']
            curr = lot['currency'] #валюта
            tr_need = lot['transport']['transport:truck_mode']  # требуемый транспорт
            tr_need_d = lot['transport']['transport:truck_kinds'] # доп к транспорту
            #bvstr
            #comment
            # comp_name id_z
            # заказчик/ид заказа/дата/откуда/куда/цена/транспорт/комм

            # #вывод
            # if in_city.lower() in str(st_pl).lower():
            #     print(f'{comp_name,id_z}',data_load,'|',st_pl,'-',en_pl,'|',st_price,curr,'|',tr_need,tr_need_d, '|',bvstr,comment)
            #     # print(f'{comp_name,id_z}',data_load,'|',st_pl,'-',en_pl,'|',st_price,curr,'|',tr_need,tr_need_d, '|',bvstr,comment)


        print('Всего аукционов:','>>>',jat['count'])

    else:
        print('Ошибка авторизации')
    rs.close()

#main
get_content(url)