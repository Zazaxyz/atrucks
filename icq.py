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

allow_chats = [
"760598293", #мой айди
]

def change_status(key, val=True):
    for x in statusIn:
        statusIn[x] = False
    statusIn[key] = val
    
def send_allows(bot):
    for chat in allow_chats:
        bot.send_text(chat_id=chat, text='Бот активен! /start -- начать')

def check_allow(bot,event):
    for x in allow_chats:
        if event.from_chat == x:
            return True
        else:
            return False

def startup(bot, event):  #обработчик чата
    # change_status('main-menu')
    if check_allow(bot,event):
        #сортировка поиска грузов
        if statusIn['start-find']:
            bot.send_text(chat_id=event.from_chat, text=f'Сортировка по: "{event.text}"')
            go_pars1(bot,event,event.text)
        else:
            if(event.text!='/start'):
                bot.send_text(chat_id=event.from_chat, text=f'Я не знаю этой команды :( {event.text}')
        
        main_menu(bot,event)
    else:
        bot.send_text(chat_id=event.from_chat,
            text='Недостаточно прав! Обратитесь к @760598293')

# bot.answer_callback_query(
#             query_id=event.data['queryId'],
#             text="Была нажата кнопка 1",
#             show_alert=True)

def main_menu(bot,event):#main-menu
    default_markup = [
            [{"text": "Поиск груза!", "callbackData": "start-find","style": "attention"}],
            [{"text": "Получить Id", "callbackData": "get-info", "style": "primary"}],
            
            ]
    bot.send_text(chat_id=event.from_chat,
        text='main menu',
        inline_keyboard_markup=json.dumps(default_markup))

def start_find(bot,event): #заупстить поиск
    change_status('start-find')
    start_find_btns = [ 
            [{"text": "ЛО + СПб", "callbackData": "reg-LO-SPB","style": "attention"}],
            [{"text": "Моск.Обл + Москва", "callbackData": "reg-LO-SPB", "style": "attention"}],
            [{"text": "Вернуться в главное меню", "callbackData": "go-main-menu", "style": "primary"}],
    ]
    bot.send_text(chat_id=event.from_chat,
            text=f'Статус: {statusIn}')
    bot.send_text(chat_id=event.from_chat,
            text='Выбери регион или напиши в чат',
            inline_keyboard_markup=json.dumps(start_find_btns))
    # startup(bot,event)

def get_info_client(bot,event): # получить инфу для внесение в разрешенные
    bot.send_text(chat_id=event.from_chat,
        text = f'твой id: {event.from_chat}')
    go_main_menu(bot,event)

def go_pars1(bot,event, city='None'):

    bot.send_text(chat_id=event.from_chat, text=f'По запросу найдено:')
    mylist = pars_1(city=city)
    print(mylist)
    for x in mylist:
        bot.send_text(chat_id=event.from_chat, text='Вывод:'+x)    
    bot.send_text(chat_id=event.from_chat, text='Вывод:'+mylist)
    go_main_menu(bot,event)

def go_main_menu(bot,event):
    bot.send_text(chat_id=event.from_chat,
        text = f'возвращаю в главное меню..')
    change_status('main-menu')
    main_menu(bot,event)    
  
def buttons_answer_cb(bot, event): #btns events
    if event.data['callbackData'] == "start-find":
        #bot.send_text(chat_id=event.from_chat, text='Вывожу лоты..')
        change_status('start-find')
        start_find(bot,event)
    elif event.data['callbackData'] == "get-info":
        get_info_client(bot,event)
    elif event.data['callbackData'] == "go-main-menu":
        go_main_menu(bot,event)

def main():

    bot = Bot(token=TOKEN)
    send_allows(bot)
    bot.dispatcher.add_handler(MessageHandler(callback=startup))  
    # bot.dispatcher.add_handler(MessageHandler(callback=message_cb))

    bot.dispatcher.add_handler(BotButtonCommandHandler(
        callback=start_find, filters=Filter.callback_data("start_find")))
    # bot.dispatcher.add_handler(BotButtonCommandHandler(
    #     callback=go_main_menu, filters=Filter.callback_data("go-main-menu")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=buttons_answer_cb))

    # bot.dispatcher.add_handler(BotButtonCommandHandler(
    #     callback=buttons_answer_cb, filters=Filter.callback_data("buttons_answer_cb")))

    bot.start_polling()

if __name__ == '__main__':
    main()