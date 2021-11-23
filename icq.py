from bot.bot import Bot
import json
from bot.handler import MessageHandler
from bot.filter import Filter
from bot.handler import MessageHandler
from bot.handler import BotButtonCommandHandler

from main import pars_1

TOKEN = "" #token

statusIn = {'main-menu':True,
            'start-find':False
}

allow_chats = [ #добавлять без @
'760598293', #мой айди
#'676358615', #Василий

]

def change_status(key, val=True):
    for x in statusIn:
        statusIn[x] = False
    statusIn[key] = val
    
def send_allows(bot):
    for chat in allow_chats:
        bot.send_text(chat_id=chat, text='Бот активен! /start -- начать')

def startup(bot, event):  #обработчик чата
    # change_status('main-menu')
    if event.from_chat in allow_chats:
        #сортировка поиска грузов
        if(event.text=='/start'):
            main_menu(bot,event)
        if statusIn['start-find']:
            bot.send_text(chat_id=event.from_chat, text=f'Сортировка по: "{event.text}"')
            go_pars1(bot,event,event.text)
        else:
            if(event.text!='/start'):
                bot.send_text(chat_id=event.from_chat, text=f'Я не знаю этой команды :(')
                main_menu(bot,event)
        # main_menu(bot,event)
    else:
        bot.send_text(chat_id=event.from_chat,
            text=f'Недостаточно прав! Обратитесь к @760598293 \n ваш ID: {event.from_chat}')
            
# bot.answer_callback_query(
#             query_id=event.data['queryId'],
#             text="Была нажата кнопка 1",
#             show_alert=True)

def main_menu(bot,event):#main-menu
    default_markup = [
            [{"text": "Поиск груза!", "callbackData": "start-find","style": "attention"}],
            [{"text": "Интересное", "callbackData": "get-info", "style": "primary"}],
            [{"text": "Atrucks.su", "url": "https://www.atrucks.su/carrier/", "style": "attention"}],

            ]
    bot.send_text(chat_id=event.from_chat,
        text='Выбери действие',
        inline_keyboard_markup=json.dumps(default_markup))         
    
def start_find(bot,event): #заупстить поиск
    change_status('start-find')
    start_find_btns = [ 
            [{"text": "СПб", "callbackData": "go-spb", "style": "primary"},
            {"text": "Ленин.обл", "callbackData": "go-lo", "style": "primary"},
            {"text": "Ижевск", "callbackData": "go-izh", "style": "primary"}],

            [{"text": "Казань", "callbackData": "go-kazan", "style": "primary"},
            {"text": "Омск", "callbackData": "go-omsk", "style": "primary"},
            {"text": "Тюмень", "callbackData": "go-tumen", "style": "primary"}],

            [{"text": "Новосиб", "callbackData": "go-novosib", "style": "primary"},
            {"text": "Уфа", "callbackData": "go-ufa", "style": "primary"},
            {"text": "Самара", "callbackData": "go-samara", "style": "primary"}],

            # [{"text": "Татарстан", "callbackData": "go-tatar", "style": "primary"}],

            [{"text": "Вернуться в главное меню", "callbackData": "go-main-menu", "style": "attention"}],
    ]
    bot.send_text(chat_id=event.from_chat,
            text='напиши в чат необходимую погрузку или выбери ниже:',
            inline_keyboard_markup=json.dumps(start_find_btns))


def get_info_client(bot,event): # получить инфу для внесение в разрешенные, надо сделать как-нибудь подсчет
    go_pars1(bot,event,city='СПб',interes=1)
    go_pars1(bot,event,city='Ленинг',interes=1)
    go_pars1(bot,event,city='МО',interes=1)
    go_pars1(bot,event,city='Иж',interes=1)
    go_pars1(bot,event,city='Каз',interes=1)
    go_pars1(bot,event,city='Омск',interes=1)
    go_pars1(bot,event,city='Тюмень',interes=1)
    go_pars1(bot,event,city='Новосиб',interes=1)
    go_pars1(bot,event,city='уфа',interes=1)
    go_pars1(bot,event,city='самар',interes=1, l=1)
    go_main_menu(bot,event)

def go_pars1(bot,event, city='None', interes=0, l=0):
    # bot.send_text(chat_id=event.from_chat, text=f'По запросу найдено:')
    mylist = pars_1(city=city)
    # print(mylist)
    for x in mylist:
        if interes==0:
            if mylist[x] != 0:
                bot.send_text(chat_id=event.from_chat, text=x, 
                inline_keyboard_markup="{}".format(json.dumps([[
                            {"text": "Перейти к заказу", "url": f"https://www.atrucks.su/a/{mylist[x]}/"},
                        ]])))
            else:
                bot.send_text(chat_id=event.from_chat, text=x)
        else:
            if mylist[x] != 0:
                bot.send_text(chat_id=event.from_chat, text=x, 
                inline_keyboard_markup="{}".format(json.dumps([[
                            {"text": "Перейти к заказу", "url": f"https://www.atrucks.su/a/{mylist[x]}/"},
                        ]])))
    if interes == 0:        
        start_find(bot,event)
    # if l == 1:        
    #     start_find(bot,event)

def go_main_menu(bot,event):
    # bot.send_text(chat_id=event.from_chat,
    #     text = f'возвращаю в главное меню..')
    change_status('main-menu')
    main_menu(bot,event)    
  
def buttons_answer_cb(bot, event): #btns events
    if event.data['callbackData'] == "start-find":
        print('callbackData=',event.data['callbackData'])
        change_status('start-find')
        start_find(bot,event)
    elif event.data['callbackData'] == "get-info":
        print('callbackData=',event.data['callbackData'])
        get_info_client(bot,event)
    elif event.data['callbackData'] == "go-main-menu":
        print('callbackData=',event.data['callbackData'])
        go_main_menu(bot,event)

    elif event.data['callbackData'] == "go-spb":
        go_pars1(bot,event, city='Спб')
    elif event.data['callbackData'] == "go-lo":
        go_pars1(bot,event, city='Ленин')
    elif event.data['callbackData'] == "go-izh":
        go_pars1(bot,event, city='Иж')
    elif event.data['callbackData'] == "go-kazan":
        go_pars1(bot,event, city='Каз')
    elif event.data['callbackData'] == "go-omsk":
        go_pars1(bot,event, city='Омск')
    elif event.data['callbackData'] == "go-tumen":
        go_pars1(bot,event, city='Тюмень')
    elif event.data['callbackData'] == "go-novosib":
        go_pars1(bot,event, city='Новосиб')
    elif event.data['callbackData'] == "go-ufa":
        go_pars1(bot,event, city='уфа')
    elif event.data['callbackData'] == "go-samara":
        go_pars1(bot,event, city='самар')
    # elif event.data['callbackData'] == "go-tatar":
    #     go_pars1(bot,event, city='татар')

    


def main():

    bot = Bot(token=TOKEN)
    send_allows(bot)
    bot.dispatcher.add_handler(MessageHandler(callback=startup))  

    bot.dispatcher.add_handler(BotButtonCommandHandler(
        callback=start_find, filters=Filter.callback_data("start_find")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=buttons_answer_cb))

    bot.start_polling()

if __name__ == '__main__':
    main()