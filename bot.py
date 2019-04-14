import telebot
import config
import dbworker
from telebot import types
from SQLighter import SQLighter
import urllib.request
import utils
import sqlite3
import cherrypy

bot = telebot.TeleBot(config.token)

class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

WEBHOOK_HOST = '104.248.40.112'
WEBHOOK_PORT = 443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '104.248.40.112'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % config.token

user_final_data = ""
# Начало диалога
@bot.message_handler(commands=["start"])
def cmd_start(message):
    global user_final_data
    user_final_data = ""
    start_menu = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    goods_btn = types.KeyboardButton("Товары")
    contacts_btn = types.KeyboardButton("Контакты")
    start_menu.add(goods_btn, contacts_btn)
    bot.send_message(message.chat.id, "Добро пожаловать в наш телеграм магазин, выберите интересующее вас в меню ниже", reply_markup=start_menu)
    dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)

# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    global user_final_data
    user_final_data = ""
    start_menu = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    goods_btn = types.KeyboardButton("Товары")
    contacts_btn = types.KeyboardButton("Контакты")
    start_menu.add(goods_btn, contacts_btn)
    bot.send_message(message.chat.id, "Что ж, начнём по-новой", reply_markup=start_menu)
    dbworker.set_state(message.chat.id, config.States.S_START.value)


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NAME.value)
def user_entering_name(message):
    global user_final_data
    user_final_data = ""
    if message.text == "Товары":
        goods_menu = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        shoes_btn = types.KeyboardButton("Обувь")
        # dress_btn = types.KeyboardButton("Одежда")
        # accesories_btn = types.KeyboardButton("Аксессуары")
        goods_menu.add(shoes_btn)
        bot.send_message(message.chat.id, "Какие товары вас интересуют?", reply_markup=goods_menu)
        # В случае с именем не будем ничего проверять, пусть хоть "25671", хоть Евкакий
        dbworker.set_state(message.chat.id, config.States.S_ENTER_AGE.value)
    elif message.text == "Контакты":
        start_menu = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        goods_btn = types.KeyboardButton("Товары")
        contacts_btn = types.KeyboardButton("Контакты")
        bot.send_message(message.chat.id, "Телефон для связи 8808080808")
        start_menu.add(goods_btn, contacts_btn)
        bot.send_message(message.chat.id, "Готовы перейти к товарам?", reply_markup=start_menu)
    else:
        start_menu = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        goods_btn = types.KeyboardButton("Товары")
        contacts_btn = types.KeyboardButton("Контакты")
        start_menu.add(goods_btn, contacts_btn)
        bot.send_message(message.chat.id, "Добро пожаловать в наш телеграм магазин, выберите интересующее вас в меню ниже", reply_markup=start_menu)
        dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)



@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_AGE.value)
def user_entering_age(message):
    global user_final_data
    user_final_data = ""
    # А вот тут сделаем проверку
    if message.text == "Обувь":
        # Подключаемся к БД
        sql_db_worker = SQLighter(config.database_name)
        # Получаем случайную строку из БД
        all = sql_db_worker.select_all()
        goods_menu = types.ReplyKeyboardMarkup()
        for a in all:
            btn = types.KeyboardButton(a[1] + " Размеры: " + a[3])
            goods_menu.add(btn)
        bot.send_message(message.chat.id, "Выберите интерсующий товар из меню", reply_markup=goods_menu)
        sql_db_worker.close()
        dbworker.set_state(message.chat.id, config.States.S_PICK_SHOES.value)
    # На данном этапе мы уверены, что message.text можно преобразовать в число, поэтому ничем не рискуем


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_PICK_SHOES.value)
def user_entering_age1(message):
    global user_final_data
    sql_db_worker = SQLighter(config.database_name)
    order_menu = types.InlineKeyboardMarkup(row_width=1)
    make_order_btn = types.InlineKeyboardButton(text="Сделать заказ", callback_data="order")
    back_to_start_btn = types.InlineKeyboardButton(text="В начало", callback_data="reset_to_start")
    order_menu.add(make_order_btn, back_to_start_btn)

    all = sql_db_worker.select_all()
    for a in all:
        if a[1] in message.text and a[3] in message.text:
            msg = "Товар: " + a[1] + "\nЦена: " + a[2] + "\nРазмеры в наличии: " + a[3]
            bot.send_message(message.chat.id, msg)
            resource = urllib.request.urlopen(a[-1])
            output = open("file01.jpg", "wb")
            output.write(resource.read())
            output.close()
            photo = open('file01.jpg', 'rb')
            bot.send_photo(message.chat.id, photo, reply_markup=order_menu)
            user_final_data = user_final_data +  "Сделан заказ: \n" + msg
    sql_db_worker.close()

@bot.callback_query_handler(func=lambda call: True and dbworker.get_current_state(call.message.chat.id) == config.States.S_PICK_SHOES.value)
def callback_inline(call):
    if call.message:
        if call.data == "order":
            keyboard_hider = types.ReplyKeyboardRemove()
            dbworker.set_state(call.message.chat.id, config.States.S_MAKE_ORDER_NAME.value)
            bot.send_message(call.message.chat.id, "Введите ваше имя", reply_markup=keyboard_hider)
        elif call.data == "reset_to_start":
            dbworker.set_state(call.message.chat.id, config.States.S_START.value)
            user_final_data = ""
            start_menu = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            goods_btn = types.KeyboardButton("Товары")
            contacts_btn = types.KeyboardButton("Контакты")
            start_menu.add(goods_btn, contacts_btn)
            bot.send_message(call.message.chat.id, "Добро пожаловать в наш телеграм магазин, выберите интересующее вас в меню ниже", reply_markup=start_menu)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_MAKE_ORDER_NAME.value)
def user_entering_name(message):
    bot.send_message(message.chat.id, "Ваш номер телефона")
    global user_final_data
    user_final_data = user_final_data + "\nИмя:" + message.text
    dbworker.set_state(message.chat.id, config.States.S_MAKE_ORDER_ADDR.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_MAKE_ORDER_ADDR.value)
def user_entering_name(message):
    bot.send_message(message.chat.id, "Введите ваш адрес")
    global user_final_data
    user_final_data = user_final_data + "\nТелефон:" + message.text
    dbworker.set_state(message.chat.id, config.States.S_ORDER_DETAILS.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ORDER_DETAILS.value)
def user_entering_name(message):
    bot.send_message(message.chat.id, "Спасибо за заказ, наш оператор свяжется с вами в ближайшее время")
    global user_final_data
    user_final_data = user_final_data + "\nАдрес:" + message.text
    dbworker.set_state(message.chat.id, config.States.S_START.value)
    bot.send_message("466167801", user_final_data)
    bot.send_message("496413777", user_final_data)
    user_final_data = ""


@bot.message_handler(func=lambda m: True)
def cmd_start(message):
    global user_final_data
    user_final_data = ""
    start_menu = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    goods_btn = types.KeyboardButton("Товары")
    contacts_btn = types.KeyboardButton("Контакты")
    start_menu.add(goods_btn, contacts_btn)
    bot.send_message(message.chat.id, "Добро пожаловать в наш телеграм магазин, выберите интересующее вас в меню ниже", reply_markup=start_menu)
    dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)





bot.remove_webhook()

# Ставим заново вебхук
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Указываем настройки сервера CherryPy
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

# Собственно, запуск!
cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
