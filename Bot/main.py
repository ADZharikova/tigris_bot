import telebot
from telebot import types
import sqlite3
from datetime import timedelta, datetime
import calendar
from gog import Gog
from notif import Notif
import threading
import os
import xlsxwriter


bot = telebot.TeleBot('7069056617:AAHnd4Y6PE2TpKuJLdxg2GdHuo1IeICrS20')
_kid_name = '-'
_gog = Gog()
_notif = Notif()

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users
                (id int auto_increment primary key,
                fio_adult varchar(100),
                fio_kid varchar(100),
                is_agree bool,
                is_superuser bool,
                phone_number integer,
                telegram_nickname varchar(50),
                abonement_type varchar(50),
                type_of_sport varchar(50),
                abonement_count_workout integer,
                current_count_workout integer,
                day_start_abonement date,
                day_end_abonement date,
                is_have_locker bool,
                locker_days_left date,
                frozen_number integer,
                vk_ru varchar(50),
                inst_ru varchar(50),
                chat_id varchar(50),
                is_active bool)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS schedule
                (id int auto_increment primary key,
                adult_schedule varchar(1000),
                kid_schedule varchar(1000))""")

    cur.execute("""CREATE TABLE IF NOT EXISTS price
                (id int auto_increment primary key,
                abonement_type varchar(50),
                type_of_sport varchar(50),
                abonement_count_workout varchar(50),
                price integer)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS club_contacts
                (id int auto_increment primary key,
                contacts varchar(1000))""")

    cur.execute("""CREATE TABLE IF NOT EXISTS additionalservices
                (id int auto_increment primary key,
                type varchar(1000),
                description varchar(1000),
                photo varchar(1000),
                price varchar(50))""")

    conn.commit()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Ознакомлен', callback_data = 'agree')
    markup.row(btn1)
    bot.send_message(message.chat.id, 'Здравствуйте!\nДля начала регистрации просьба ознакомиться с <a href="https://tigrisfight.ru/dogovor-publichnoi-oferty/">договором публичной оферты</a>.\nНажимая "Ознакомлен" вы подтверждаете, что соглашаетесь с ним', parse_mode='html', reply_markup = markup)

def phone_number(message):
        global _adult_name
        _adult_name = message.text
        if (_adult_name == '/start'):
            bot.register_next_step_handler(message, start)
        else:
            bot.send_message(message.chat.id, 'Введите телефона без "8" для окончания регистрации\n<em>Пример: 9876543210</em>',  parse_mode='html')
            bot.register_next_step_handler(message, register)

def register(message):
        global _phone_number
        _phone_number = message.text
        if (_phone_number == '/start'):
            bot.register_next_step_handler(message, start)
        elif (len(_phone_number) != 10):
            bot.send_message(message.chat.id, 'Номер введён некорректно')
            bot.register_next_step_handler(message, register)

        else:
            conn = sqlite3.connect('tigris_clube.sql')
            cur = conn.cursor()
            cur.execute('DELETE FROM users WHERE telegram_nickname = "%s"' % (message.from_user.username))
            cur.execute("INSERT INTO users (fio_adult, fio_kid, is_agree, is_superuser, phone_number, telegram_nickname, current_count_workout, chat_id, is_active) VALUES ('%s', '%s', 'true', 'false', '%s', '%s', 0, '%s', 'true')" % (_adult_name, _kid_name, _phone_number, message.from_user.username, message.chat.id))
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, 'Регистрация прошла успешно\n\n<em>Доступные команды можно посмотреть в меню слева от клавиатуры.</em>', parse_mode='html')

def adult_with_kid(message):
    global _kid_name
    _kid_name = message.text
    if (_kid_name == '/start'):
        bot.register_next_step_handler(message, start)
    else:
        bot.send_message(message.chat.id, 'Введите ваше ФИО')
        bot.register_next_step_handler(message, phone_number)



@bot.message_handler(commands=['users_list'])
def users_list(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE chat_id = "%s"' % (message.chat.id))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        workbook = xlsxwriter.Workbook('users.xlsx')
        worksheet = workbook.add_worksheet()
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users')
        users = cur.fetchall()
        worksheet.write(0, 0, 'ФИО взрослого')
        worksheet.write(0, 1, 'ФИО ребёнка')
        worksheet.write(0, 2, 'Ознакомлен с договором')
        worksheet.write(0, 3, 'Админ')
        worksheet.write(0, 4, 'Номер телефона')
        worksheet.write(0, 5, 'Ник телеграм')
        worksheet.write(0, 6, 'Тип абонемента')
        worksheet.write(0, 7, 'Направление')
        worksheet.write(0, 8, 'Количество дней в абонементе')
        worksheet.write(0, 9, 'Количество тренировок, которые отходил')
        worksheet.write(0, 10, 'Дата начала абонемента')
        worksheet.write(0, 11, 'Дата окончания абонемента')
        worksheet.write(0, 12, 'Есть ли шкафчик')
        worksheet.write(0, 13, 'Дата окончания аренды шкафчика')
        worksheet.write(0, 14, 'Количество заморозок')
        worksheet.write(0, 15, 'vk_ru')
        worksheet.write(0, 16, 'inst_ru')
        worksheet.write(0, 17, 'ID чата')
        worksheet.write(0, 18, 'Активен ли')
        row = 1
        for el in users:
            for i in range(0, 19):
                worksheet.write(row, i, str(el[i+1]))
            row += row
        cur.close()
        conn.close()
        workbook.close()
        bot.send_document(message.chat.id, open('users.xlsx', 'rb'))
    else:
        bot.send_message(message.chat.id, 'Вы не админ')



@bot.message_handler(commands=['schedule'])
def find_out_schedule(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Взрослые', callback_data = 'find_out_adult_schedule')
    btn2 = types.InlineKeyboardButton('Дети', callback_data = 'find_out_kid_schedule')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Чьё расписание интересует?', reply_markup=markup)



@bot.message_handler(commands=['change_schedule'])
def change_schedule(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE chat_id = "%s"' % (message.chat.id))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Взрослые', callback_data = 'change_adult_schedule')
        btn2 = types.InlineKeyboardButton('Дети', callback_data = 'change_kid_schedule')
        markup.row(btn1, btn2)
        bot.send_message(message.chat.id, 'Выберете чьё расписание хотите поменять и введите его', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Вы не админ')

def change_adult_schedule(message):
    _adult_schedule_new = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('UPDATE schedule SET adult_schedule = "%s"' % (_adult_schedule_new))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Расписание для взрослых изменено')

def change_kid_schedule(message):
    _kid_schedule = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('UPDATE schedule SET kid_schedule = "%s"' % (_kid_schedule))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Расписание для детей изменено')



@bot.message_handler(commands=['add_schedule_first_time'])
def add_schedule_first_time(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE chat_id = "%s"' % (message.chat.id))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('DELETE FROM schedule')
        cur.execute("INSERT INTO schedule (adult_schedule, kid_schedule) VALUES ('Взрослые', 'Дети')")
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Расписание добавлено')
    else:
        bot.send_message(message.chat.id, 'Вы не админ')



@bot.message_handler(commands=['price'])
def find_out_price(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Групповые', callback_data = 'find_out_group_price')
    btn2 = types.InlineKeyboardButton('Сплит', callback_data = 'find_out_splite_price')
    btn3 = types.InlineKeyboardButton('Индивидуальные', callback_data = 'find_out_individual_price')
    markup.row(btn1, btn2)
    markup.row(btn3)
    bot.send_message(message.chat.id, 'Выберите тип занятий', reply_markup=markup)



@bot.message_handler(commands=['add_price_first_time'])
def add_price_first_time(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE chat_id = "%s"' % (message.chat.id))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('DELETE FROM price')
        cur.execute("""INSERT INTO price (abonement_type, type_of_sport, abonement_count_workout, price)
                VALUES ('Групповой', 'ММА группа №1', '1', '800'),
                ('Групповой', 'ММА группа №1', '8','4500'),
                ('Групповой', 'ММА группа №1', '12','5500'),
                ('Групповой', 'ММА группа №1', 'Безлимит', '8000'),
                ('Групповой', 'ММА группа №2', '1', '800'),
                ('Групповой', 'ММА группа №2', '8', '4500'),
                ('Групповой', 'ММА группа №2', '12','5500'),
                ('Групповой', 'ММА группа №2', 'Безлимит', '8000'),
                ('Групповой', 'Бокс', '1', '800'),
                ('Групповой', 'Бокс', '8','4500'),
                ('Групповой', 'Бокс', '12','5500'),
                ('Групповой', 'Бокс', 'Безлимит','8000'),
                ('Групповой', 'Тайский бокс (Муай Тай)', '1','800'),
                ('Групповой', 'Тайский бокс (Муай Тай)', '8','4500'),
                ('Групповой', 'Тайский бокс (Муай Тай)', '12','5500'),
                ('Групповой', 'Тайский бокс (Муай Тай)', 'Безлимит','8000'),
                ('Групповой', 'Кикбоксинг', '1', '800'),
                ('Групповой', 'Кикбоксинг', '8', '4500'),
                ('Групповой', 'Кикбоксинг', '12', '5500'),
                ('Групповой', 'Кикбоксинг', 'Безлимит', '8000'),
                ('Индивидуальный', '90 мин', '1', '3500'),
                ('Индивидуальный', '90 мин', '4', '13000'),
                ('Индивидуальный', '90 мин', '8', '26000'),
                ('Индивидуальный', '90 мин', '12', '38000'),
                ('Индивидуальный', '60 мин', '1', '3000'),
                ('Индивидуальный', '60 мин', '4', '11000'),
                ('Индивидуальный', '60 мин', '8', '22000'),
                ('Индивидуальный', '60 мин', '12', '32000'),
                ('Сплит', '90 мин', '1', '5000'),
                ('Сплит', '90 мин', '4', '18500'),
                ('Сплит', '90 мин', '8', '37000'),
                ('Сплит', '90 мин', '12', '55000'),
                ('Сплит', '60 мин', '1', '4300'),
                ('Сплит', '60 мин', '4', '16300'),
                ('Сплит', '60 мин', '8', '32500'),
                ('Сплит', '60 мин', '12', '47000')""")
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Цены добавлены')
    else:
        bot.send_message(message.chat.id, 'Вы не админ')



@bot.message_handler(commands=['add_new_price'])
def add_new_price(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE chat_id = "%s"' % (message.chat.id))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        bot.send_message(message.chat.id, 'Напишите тип абонемента:\nГрупповой\nИндивидуальный\nСплит\n\n<em>Для отмены записи нажмите /cancel</em>', parse_mode='html')
        bot.register_next_step_handler(message, add_abonement_type)
    else:
        bot.send_message(message.chat.id, 'Вы не админ')

def add_abonement_type(message):
    global _abonement_type
    _abonement_type = message.text
    if (_abonement_type == "/cancel"):
        bot.send_message(message.chat.id, '<em>Доступные команды можно посмотреть в меню слева от клавиатуры.</em>', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Напишите направление.\n\n<em>Для отмены записи нажмите /cancel</em>', parse_mode='html')
        bot.register_next_step_handler(message, add_type_of_sport)

def add_type_of_sport(message):
    global _type_of_sport
    _type_of_sport = message.text
    if (_type_of_sport == "/cancel"):
        bot.send_message(message.chat.id, '<em>Доступные команды можно посмотреть в меню слева от клавиатуры.</em>', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Напишите количество тренировок.\n\n<em>Для отмены записи нажмите /cancel</em>', parse_mode='html')
        bot.register_next_step_handler(message, add_abonement_count_workout)

def add_abonement_count_workout(message):
    global _abonement_count_workout
    _abonement_count_workout = message.text
    if (_abonement_count_workout == "/cancel"):
        bot.send_message(message.chat.id, '<em>Доступные команды можно посмотреть в меню слева от клавиатуры.</em>', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Напишите цену.\n\n<em>Для отмены записи нажмите /cancel</em>', parse_mode='html')
        bot.register_next_step_handler(message, add_price_new)

def add_price_new(message):
    global _price
    _price = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("INSERT INTO price (abonement_type, type_of_sport, abonement_count_workout, price) VALUES ('%s', '%s', '%s', '%s')"% (_abonement_type, _type_of_sport, _abonement_count_workout, _price))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Готово. Для проверки вызовите /price')



@bot.message_handler(commands=['change_price'])
def change_price(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE chat_id = "%s"' % (message.chat.id))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("SELECT abonement_type FROM price GROUP BY abonement_type")
        price = cur.fetchall()
        info = list()
        for abonement_type in price:
            info.append(abonement_type)
        cur.close()
        conn.close()
        for el in info:
            btn = types.KeyboardButton(str(el)[2:-3])
            markup.add(btn)
        bot.send_message(message.chat.id, 'Укажите тип абонемента', reply_markup=markup)
        bot.register_next_step_handler(message, change_price_abonement_type)
    else:
        bot.send_message(message.chat.id, "Вы не админ")

def change_price_abonement_type(message):
    global _abonement_type
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    _abonement_type = message.text.strip()
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT type_of_sport FROM price WHERE abonement_type = '%s' GROUP BY type_of_sport"% (_abonement_type))
    price = cur.fetchall()
    info = list()
    for type_of_sport in price:
            info.append(type_of_sport)
    cur.close()
    conn.close()
    for el in info:
        btn = types.KeyboardButton(str(el)[2:-3])
        markup.add(btn)
    bot.send_message(message.chat.id, 'Укажите направление', reply_markup=markup)
    bot.register_next_step_handler(message, change_price_type_of_sport)

def change_price_type_of_sport(message):
    global _type_of_sport
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    _type_of_sport = message.text.strip()
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT abonement_count_workout FROM price WHERE abonement_type = '%s' and type_of_sport = '%s'"% (_abonement_type, _type_of_sport))
    price = cur.fetchall()
    info = list()
    for abonement_count_workout in price:
        info.append(abonement_count_workout)
    cur.close()
    conn.close()
    for el in info:
        btn = types.KeyboardButton(str(el)[2:-3])
        markup.add(btn)
    bot.send_message(message.chat.id, 'Укажите количество занятий', reply_markup=markup)
    bot.register_next_step_handler(message, change_price_abonement_count_workout)

def change_price_abonement_count_workout(message):
    global _abonement_count_workout
    _abonement_count_workout = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM price WHERE abonement_type = '%s' and type_of_sport = '%s' and abonement_count_workout = '%s'"% (_abonement_type, _type_of_sport, _abonement_count_workout))
    price = cur.fetchall()
    info = ''
    for el in price:
        info += f'Тип абонимента: {el[1]}\nТип спорта: {el[2]}\nКоличество тренировок: {el[3]} в месяц\nАктуальная цена: {el[4]} рублей\n'
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f'Напишите новую цену\n\nСейчас\n<em>{info}</em>', parse_mode='html')
    bot.register_next_step_handler(message, change_price)

def change_price(message):
    global _price
    _price = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("UPDATE price SET price = '%s' WHERE abonement_type = '%s' and type_of_sport = '%s' and abonement_count_workout = '%s'" % (_price, _abonement_type, _type_of_sport, _abonement_count_workout))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Готово. Для проверки вызовите /price')



@bot.message_handler(commands=['delete_abonement'])
def delete_abonement(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE chat_id = "%s"' % (message.chat.id))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("SELECT abonement_type FROM price GROUP BY abonement_type")
        price = cur.fetchall()
        info = list()
        for abonement_type in price:
            info.append(abonement_type)
        cur.close()
        conn.close()
        for el in info:
            btn = types.KeyboardButton(str(el)[2:-3])
            markup.add(btn)
        bot.send_message(message.chat.id, 'Укажите тип абонемента', reply_markup=markup)
        bot.register_next_step_handler(message, delete_abonement_type)
    else:
        bot.send_message(message.chat.id, "Вы не админ")

def delete_abonement_type(message):
    global _abonement_type
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    _abonement_type = message.text.strip()
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT type_of_sport FROM price WHERE abonement_type = '%s' GROUP BY type_of_sport"% (_abonement_type))
    price = cur.fetchall()
    info = list()
    for type_of_sport in price:
            info.append(type_of_sport)
    cur.close()
    conn.close()
    for el in info:
        btn = types.KeyboardButton(str(el)[2:-3])
        markup.add(btn)
    bot.send_message(message.chat.id, 'Укажите направление', reply_markup=markup)
    bot.register_next_step_handler(message, delete_type_of_sport)

def delete_type_of_sport(message):
    global _type_of_sport
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    _type_of_sport = message.text.strip()
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT abonement_count_workout FROM price WHERE abonement_type = '%s' and type_of_sport = '%s'"% (_abonement_type, _type_of_sport))
    price = cur.fetchall()
    info = list()
    for abonement_count_workout in price:
        info.append(abonement_count_workout)
    cur.close()
    conn.close()
    for el in info:
        btn = types.KeyboardButton(str(el)[2:-3])
        markup.add(btn)
    bot.send_message(message.chat.id, 'Укажите количество занятий', reply_markup=markup)
    bot.register_next_step_handler(message, delete_abonement_count_workout)

def delete_abonement_count_workout(message):
    global _abonement_count_workout
    _abonement_count_workout = message.text.strip()
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM price WHERE abonement_type = '%s' and type_of_sport = '%s' and abonement_count_workout = '%s'"% (_abonement_type, _type_of_sport, _abonement_count_workout))
    price = cur.fetchall()
    info = ''
    for el in price:
        info += f'Тип абонемента: {el[1]}\nГруппа: {el[2]}\nКоличество занятий: {el[3]}\nЦена: {el[4]}'
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да!', callback_data = 'delete_abonement')
    btn2 = types.InlineKeyboardButton('Нет', callback_data = 'not_find_nick')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f'Хотите удалить\n\n{info}', parse_mode='html', reply_markup=markup)



@bot.message_handler(commands=['signup'])
def signup(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT abonement_type FROM price GROUP BY abonement_type")
    price = cur.fetchall()
    info = list()
    for abonement_type in price:
        info.append(abonement_type)
    cur.close()
    conn.close()
    for el in info:
        btn = types.KeyboardButton(str(el)[2:-3])
        markup.add(btn)
    bot.send_message(message.chat.id, 'Укажите тип абонемента\n\n<em>Для отмены записи нажмите /cancel</em>', parse_mode='html', reply_markup=markup)
    bot.register_next_step_handler(message, signup_abonement_type)

def signup_abonement_type(message):
    global _abonement_type
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    _abonement_type = message.text.strip()
    if (_abonement_type == "/cancel"):
        bot.send_message(message.chat.id, '<em>Доступные команды можно посмотреть в меню слева от клавиатуры.</em>', parse_mode='html')
    else:
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("SELECT type_of_sport FROM price WHERE abonement_type = '%s' GROUP BY type_of_sport"% (_abonement_type))
        price = cur.fetchall()
        info = list()
        for type_of_sport in price:
                info.append(type_of_sport)
        cur.close()
        conn.close()
        for el in info:
            btn = types.KeyboardButton(str(el)[2:-3])
            markup.add(btn)
        bot.send_message(message.chat.id, 'Укажите направление\n\n<em>Для отмены записи нажмите /cancel</em>', parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, signup_type_of_sport)

def signup_type_of_sport(message):
    global _type_of_sport
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    _type_of_sport = message.text.strip()
    if (_type_of_sport == "/cancel"):
        bot.send_message(message.chat.id, '<em>Доступные команды можно посмотреть в меню слева от клавиатуры.</em>', parse_mode='html')
    else:
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("SELECT abonement_count_workout FROM price WHERE abonement_type = '%s' and type_of_sport = '%s'"% (_abonement_type, _type_of_sport))
        price = cur.fetchall()
        info = list()
        for abonement_count_workout in price:
            info.append(abonement_count_workout)
        cur.close()
        conn.close()
        for el in info:
            btn = types.KeyboardButton(str(el)[2:-3])
            markup.add(btn)
        bot.send_message(message.chat.id, 'Укажите количество занятий\n\n<em>Для отмены записи нажмите /cancel</em>', parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, signup_abonement_count_workout)

def signup_abonement_count_workout(message):
    global _abonement_count_workout
    _abonement_count_workout = message.text.strip()
    if (_abonement_count_workout == "/cancel"):
        bot.send_message(message.chat.id, '<em>Доступные команды можно посмотреть в меню слева от клавиатуры.</em>', parse_mode='html')
    else:
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("SELECT price FROM price WHERE abonement_type = '%s' and type_of_sport = '%s' and abonement_count_workout = '%s'"% (_abonement_type, _type_of_sport, _abonement_count_workout))
        price = cur.fetchall()
        info = ''
        for el in price:
            info += f'{el[0]}'
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, f'Для оплаты необходимо перевести <b>{info}</b> рублей\nна Cбербанк\nпо номеру <b>8(985)913-45-16</b>\nна имя Дмитрия Юрьевича М.\n\nЧтобы оплата прошла, необходимо прикрепить сюда СКРИНШОТ чека СРАЗУ после этого сообщения. Для проверки успешности оплаты зайдите в /myinfo\n⚠️ <em>Если абонемент не отобразился, свяжитесь с администратором @psy_sensei</em>', parse_mode='html')
        bot.register_next_step_handler(message, signup_check)

def signup_check(message):
    if (message.content_type == 'photo'):
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("UPDATE users SET abonement_type = '%s', type_of_sport = '%s', abonement_count_workout = '%s', day_start_abonement = CURRENT_DATE, day_end_abonement = DATE(CURRENT_DATE, '+1 month'), current_count_workout = '0', frozen_number = '0', telegram_nickname = '%s' WHERE chat_id = '%s'" % (_abonement_type, _type_of_sport, _abonement_count_workout, message.from_user.username, message.chat.id))
        conn.commit()
        cur.execute("SELECT price FROM price WHERE abonement_type in (SELECT abonement_type FROM users WHERE chat_id = '%s') and type_of_sport in (SELECT type_of_sport FROM users WHERE chat_id = '%s') and abonement_count_workout in (SELECT abonement_count_workout FROM users WHERE chat_id = '%s')"% (message.chat.id, message.chat.id, message.chat.id))
        price = cur.fetchall()
        _price = ''
        for el in price:
            _price += f'{el[0]}'
        cur.execute("SELECT * FROM users WHERE chat_id = '%s'"% (message.chat.id))
        users = cur.fetchall()
        info = ''
        for el in users:
            _fio_adult = f'{el[1]}'
            _fio_kid = f'{el[2]}'
            _abonement = f'{el[7]}'
            _sport = f'{el[8]}'
            count_workout = f'{el[9]}'
            info += f'ЧЕК\n\nДата оплаты: {el[11]}\nФИО взрослого: {el[1]}\nФИО ребёнка: {el[2]}\nНомер: {el[5]}\nТелега: @{el[6]}\nТип абонемента: {el[7]}\nГруппа: {el[8]}\nКоличество занятий: {el[9]}\n'
        cur.close()
        conn.close()
        bot.send_message(-4143866178, info)
        bot.forward_message(-4143866178, message.from_user.id, message.message_id)
        _gog.add_payment(_fio_adult, _fio_kid, str(datetime.now().date()), _abonement, _sport, count_workout, _price)
        bot.reply_to(message, 'Чек получен и отправлен преподавателю. Спасибо!')
        threading.Timer(0, _notif.notification(message.chat.id))
    else:
        bot.reply_to(message, 'Чек не защитан, начните сначала /signup')

def cool_signup_check(message):
    if (message.content_type == 'photo'):
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("UPDATE users SET day_start_abonement = CURRENT_DATE, day_end_abonement = DATE(CURRENT_DATE, '+1 month'), current_count_workout = '0', frozen_number = '0', telegram_nickname = '%s' WHERE chat_id = '%s'" % (message.from_user.username, message.chat.id))
        conn.commit()
        cur.execute("SELECT price FROM price WHERE abonement_type in (SELECT abonement_type FROM users WHERE chat_id = '%s') and type_of_sport in (SELECT type_of_sport FROM users WHERE chat_id = '%s') and abonement_count_workout in (SELECT abonement_count_workout FROM users WHERE chat_id = '%s')"% (message.chat.id, message.chat.id, message.chat.id))
        price = cur.fetchall()
        _price = ''
        for el in price:
            _price += f'{el[0]}'
        cur.execute("SELECT * FROM users WHERE chat_id = '%s'"% (message.chat.id))
        users = cur.fetchall()
        info = ''
        for el in users:
            _fio_adult = f'{el[1]}'
            _fio_kid = f'{el[2]}'
            _abonement = f'{el[7]}'
            _sport = f'{el[8]}'
            count_workout = f'{el[9]}'
            info += f'ЧЕК\n\nДата оплаты: {el[11]}\nФИО взрослого: {el[1]}\nФИО ребёнка: {el[2]}\nНомер: {el[5]}\nТелега: @{el[6]}\nТип абонемента: {el[7]}\nГруппа: {el[8]}\nКоличество занятий: {el[9]}\n'
        cur.close()
        conn.close()
        bot.send_message(-4143866178, info)
        bot.forward_message(-4143866178, message.from_user.id, message.message_id)
        _gog.add_payment(_fio_adult, _fio_kid, str(datetime.now().date()), _abonement, _sport, count_workout, _price)
        bot.reply_to(message, 'Чек получен и отправлен преподавателю. Спасибо!')
        threading.Timer(0, _notif.notification(message.chat.id))
    else:
        bot.reply_to(message, 'Это не чек. Попробуте продлить ещё раз')



@bot.message_handler(commands=['chat_id'])
def find_out_chat_id(message):
    bot.send_message(message.chat.id, message.chat.id)



@bot.message_handler(commands=['socialnetwork'])
def add_socialnetwork(message):
    bot.send_message(message.chat.id, 'Какую соцсеть хотите добавить?\n/VK\n/Instagram\n\n<em>Нажмите на нужную соц. сеть</em>', parse_mode='html')



@bot.message_handler(commands=['VK'])
def add_socialnetwork(message):
    bot.send_message(message.chat.id, 'Введите юзернейм (@user) или ссылку')
    bot.register_next_step_handler(message, add_vk)

def add_vk(message):
    _vk = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('UPDATE users SET vk_ru = "%s" WHERE chat_id = "%s"' % (_vk, message.chat.id))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Соцсеть добавлена')



@bot.message_handler(commands=['Instagram'])
def add_socialnetwork(message):
    bot.send_message(message.chat.id, 'Введите свой ник')
    bot.register_next_step_handler(message, add_inst)

def add_inst(message):
    _inst = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('UPDATE users SET inst_ru = "%s" WHERE chat_id = "%s"' % (_inst, message.chat.id))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Соцсеть добавлена')



@bot.message_handler(commands=['additionalservices'])
def find_out_add_type(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT type FROM additionalservices")
    additionalservices = cur.fetchall()
    info = list()
    for type in additionalservices:
        info.append(type)
    cur.close()
    conn.close()
    for el in info:
        btn = types.KeyboardButton(str(el)[2:-3])
        markup.add(btn)
    bot.send_message(message.chat.id, 'Что вас интересует?', reply_markup=markup)
    bot.register_next_step_handler(message, show_additionalservices)

def show_additionalservices(message):
    _show_type_add = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM additionalservices WHERE type = '%s'"% (_show_type_add))
    additionalservices = cur.fetchall()
    for el in additionalservices:
        bot.send_photo(message.chat.id, open(str(el[3]), 'rb'), caption=f'{el[1]}: {el[4]} рублей\n\n{el[2]}', parse_mode='html')
    cur.close()
    conn.close()


def change_date_end_rent_locker(message):
    if (message.content_type == 'photo'):
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("UPDATE users SET locker_days_left = DATE(CURRENT_DATE, '+1 month') WHERE chat_id = '%s'" % (message.chat.id))
        conn.commit()
        cur.execute("SELECT price FROM additionalservices WHERE type = 'Аренда шкафчика'")
        additionalservices = cur.fetchall()
        _price_rent = ''
        for el in additionalservices:
            _price_rent += f'{el[0]}'
        cur.execute("SELECT * FROM users WHERE chat_id = '%s'"% (message.chat.id))
        users = cur.fetchall()
        info = ''
        for el in users:
            fio_adult = {el[1]}
            fio_kid = {el[2]}
            info += f'АРЕНДА ШКАФЧИКА\n\nФИО взрослого: {el[1]}\nФИО ребёнка: {el[2]}\nНомер: {el[5]}\nТелега: @{el[6]}\nТип абонемента: {el[7]}\nГруппа: {el[8]}\nКоличество занятий: {el[9]}\nДата покупки: {datetime.now().date()}'
        cur.close()
        conn.close()
        _gog.add_payment(str(fio_adult)[2:-2], str(fio_kid)[2:-2], str(datetime.now().date()), "Аренда шкафчика", "-", "-", str(_price_rent))
        bot.send_message(-4143866178, info)
        bot.forward_message(-4143866178, message.from_user.id, message.message_id)
        bot.send_message(message.chat.id, 'Оплата прошла')
    else:
        bot.reply_to(message, 'Это не чек. Попробуте арендовать ещё раз')



@bot.message_handler(commands=['add_additional_services_first_time'])
def add_additional_services_first_time(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE chat_id = "%s"' % (message.chat.id))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("""INSERT INTO additionalservices (type, description, photo, price)
                    VALUES ('Аренда шкафчика', 'Можно арендовать шкафчик на месяц', 'locker.webp', '5000'),
                    ('Купить книгу', 'Ссылка на книгу. Очень хорошая, берите', 'book.jpg', '190000'),
                    ('Шейкер клуба', 'Не проливается и очень крутой. Только сейчас по скидке', 'shacker.jpg', '99999999')""")
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Доп услуги добавлены')
    else:
        bot.send_message(message.chat.id, 'Вы не админ')



@bot.message_handler(commands=['add_additional_service'])
def add_additional_service_type(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE chat_id = "%s"' % (message.chat.id))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        bot.send_message(message.chat.id, 'Напишите название')
        bot.register_next_step_handler(message, add_additional_service_description)
    else:
        bot.send_message(message.chat.id, 'Вы не админ')

def add_additional_service_description(message):
    global _additional_type
    _additional_type = message.text
    bot.send_message(message.chat.id, 'Напишите описание')
    bot.register_next_step_handler(message, add_additional_service_price)

def add_additional_service_price(message):
    global _additional_description
    _additional_description = message.text
    bot.send_message(message.chat.id, 'Напишите цену')
    bot.register_next_step_handler(message, add_additional_service_photo)

def add_additional_service_photo(message):
    global _additional_price
    _additional_price = message.text
    bot.send_message(message.chat.id, 'Отправьте фото документом')
    bot.register_next_step_handler(message, add_new_additional_service)

def add_new_additional_service(message):
    global _additional_type
    global _additional_price
    global _additional_description
    file_info = bot.get_file(message.document.file_id)
    _additional_photo = bot.download_file(file_info.file_path)
    save_path = message.document.file_name
    with open(save_path, 'wb') as new_file:
        new_file.write(_additional_photo)
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("INSERT INTO additionalservices (type, description, photo, price) VALUES ('%s', '%s', '%s', '%s')" % (_additional_type, _additional_description, save_path, _additional_price))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Доп услуга добавлена')



@bot.message_handler(commands=['delete_additional_service'])
def delete_additional_service(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE chat_id = "%s"' % (message.chat.id))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("SELECT type FROM additionalservices")
        price = cur.fetchall()
        info = list()
        for abonement_type in price:
            info.append(abonement_type)
        cur.close()
        conn.close()
        for el in info:
            btn = types.KeyboardButton(str(el)[2:-3])
            markup.add(btn)
        bot.send_message(message.chat.id, 'Укажите какую услугу хотите удалить', reply_markup=markup)
        bot.register_next_step_handler(message, delete_add)
    else:
        bot.send_message(message.chat.id, "Вы не админ")

def delete_add(message):
    global _type_addit
    _type_addit =  message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM additionalservices WHERE type = '%s'"% (_type_addit))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[1]}'
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да!', callback_data = 'delete_add')
    btn2 = types.InlineKeyboardButton('Нет', callback_data = 'not_find_nick')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f'Надо удалить {info}?', parse_mode='html', reply_markup=markup)



@bot.message_handler(commands=['change_price_additional_service'])
def change_price_additional_service(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE chat_id = "%s"' % (message.chat.id))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("SELECT type FROM additionalservices")
        price = cur.fetchall()
        info = list()
        for abonement_type in price:
            info.append(abonement_type)
        cur.close()
        conn.close()
        for el in info:
            btn = types.KeyboardButton(str(el)[2:-3])
            markup.add(btn)
        bot.send_message(message.chat.id, 'Укажите на какую услугу хотите поменять цену', reply_markup=markup)
        bot.register_next_step_handler(message, new_price_additional_service)
    else:
        bot.send_message(message.chat.id, "Вы не админ")

def new_price_additional_service(message):
    global _add_type
    _add_type = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT price FROM additionalservices WHERE type = '%s'"% (_add_type))
    price = cur.fetchall()
    info = ''
    for el in price:
        info += f'Актуальная цена: {el[0]} рублей'
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f'Напишите новую цену\n\nСейчас\n<em>{info}</em>', parse_mode='html')
    bot.register_next_step_handler(message, update_price_additional_service)


def update_price_additional_service(message):
    global _add_type
    _new_price = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("UPDATE additionalservices SET price = '%s' WHERE type = '%s'" % (_new_price, _add_type))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Готово. Для проверки вызовите /additionalservices')



@bot.message_handler(commands=['contacts'])
def find_out_contacts(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM club_contacts')
    club_contacts = cur.fetchall()
    info = ''
    for el in club_contacts:
        info += f'{el[1]}'
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f'{info}')



@bot.message_handler(commands=['change_contacts'])
def add_contacts(message):
    bot.send_message(message.chat.id, 'Введите новый текст')
    bot.register_next_step_handler(message, change_contacts)

def change_contacts(message):
    _contacts = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("DELETE FROM club_contacts")
    cur.execute("INSERT INTO club_contacts (contacts) VALUES ('%s')"% (_contacts))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Контакты изменены')



@bot.message_handler(commands=['admin_help'])
def admin_help(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE chat_id = "%s"' % (message.chat.id))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        bot.send_message(message.chat.id, "Команды, доступные админам:\n\nРАБОТА С ПОЛЬЗОВАТЕЛЯМИ:\n/users_list - Вывести список пользователей\n/inactive_user - Сделать пользователя неактивным, чтобы он перестал получать уведомления\n/delete_user - Удалить пользователя\n/chat_id - Узнать id текущего чата (доступно всем)\n\nРАБОТА С РАСПИСАНИЕМ:\n/add_schedule_first_time - Самый первый раз добавить расписание (сделать один раз при запуске)\n/change_schedule - Поменять расписание\n\nРАБОТА С ЦЕНАМИ:\n/add_price_first_time - Самый первый раз добавить цены (сделать один раз при запуске)\n/add_new_price - Добавить новый вид абонемента\n/change_price - Поменять цену существующего абонемента\n/delete_abonement - Удалить вид абонемента\n\nИЗМЕНЕНИЕ ДАТ:\n/change_day_start_abonement - поменять дату начала абонемента определённого пользователя\n/change_day_end_abonement - поменять дату окончания абонемента определённого пользователя\n/change_day_end_abonement_all - поменять дату окончания абонемента ВСЕХ пользователей\n/locker_days_left - поменять дату окончания аренды шкафчика определённого пользователя\n\nДОП УСЛУГИ:\n/add_additional_service - добавить новую доп услугу\n/change_price_additional_service - изменить цену существующей доп услуги\n/delete_additional_service - удалить существующую услугу\n\nДОП ВОЗМОЖНОСТИ:\n/change_contacts - Поменять информацию в графе 'Контакты клуба'\n/all_notification - отправить всем уведомление")
    else:
        bot.send_message(message.chat.id, "Вы не админ")



@bot.message_handler(commands=['inactive_user'])
def inactive_user(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE chat_id = "%s"' % (message.chat.id))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        bot.send_message(message.chat.id, 'Введите ник пользователя, которого хотите сделать неактивным')
        bot.register_next_step_handler(message, inactive_user_check)
    else:
        bot.send_message(message.chat.id, "Вы не админ")

def inactive_user_check(message):
    global _telegram_nick
    _telegram_nick =  message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE telegram_nickname = '%s'"% (_telegram_nick))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[1]}'
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да!', callback_data = 'inactive_user')
    btn2 = types.InlineKeyboardButton('Нет', callback_data = 'not_find_nick')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f'Надо сделать неактивным {info}?', parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['delete_user'])
def delete_user(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE chat_id = "%s"' % (message.chat.id))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        bot.send_message(message.chat.id, 'Введите ник пользователя, которого хотите удалить')
        bot.register_next_step_handler(message, delete_user_check)
    else:
        bot.send_message(message.chat.id, "Вы не админ")

def delete_user_check(message):
    global _telegram_nick
    _telegram_nick =  message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE telegram_nickname = '%s'"% (_telegram_nick))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[1]}'
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да!', callback_data = 'delete_user')
    btn2 = types.InlineKeyboardButton('Нет', callback_data = 'not_find_nick')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f'Надо удалить {info}?', parse_mode='html', reply_markup=markup)



@bot.message_handler(commands=['add_boss_user'])
def add_admin_user(message):
    bot.send_message(message.chat.id, 'Введите ник нового админа без @')
    bot.register_next_step_handler(message, add_new_admin)

def add_new_admin(message):
    global _telegram_nick
    _telegram_nick = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE telegram_nickname = '%s'"% (_telegram_nick))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[1]}\n'
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да!', callback_data = 'add_new_admin')
    btn2 = types.InlineKeyboardButton('Нет', callback_data = 'not_find_nick')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f'Надо сделать админом {info}', reply_markup=markup)



@bot.message_handler(commands=['locker_days_left'])
def locker_days_left(message):
    bot.send_message(message.chat.id, 'Введите ник пользователя без @')
    bot.register_next_step_handler(message, change_locker_days_left)

def change_locker_days_left(message):
    global _telegram_nick
    _telegram_nick =  message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE telegram_nickname = '%s'"% (_telegram_nick))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[1]}'
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да!', callback_data = 'change_locker_days_left')
    btn2 = types.InlineKeyboardButton('Нет', callback_data = 'not_find_nick')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f'Надо поменять дату шкафчика у {info}?', reply_markup=markup)

def update_locker_days_left(message):
    global _telegram_nick
    _new_day = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('UPDATE users SET locker_days_left = "%s" WHERE telegram_nickname = "%s"' % (_new_day, _telegram_nick))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Дата установлена')



@bot.message_handler(commands=['change_day_start_abonement'])
def change_day_start_abonement(message):
    bot.send_message(message.chat.id, 'Введите ник пользователя без @')
    bot.register_next_step_handler(message, add_new_day_start_abonement)

def add_new_day_start_abonement(message):
    _telegram_nick =  message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE telegram_nickname = '%s'"% (_telegram_nick))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[1]}'
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да!', callback_data = 'change_day_start_abonement')
    btn2 = types.InlineKeyboardButton('Нет', callback_data = 'not_find_nick')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f'Надо поменять дату начала абонемента у {info}?', reply_markup=markup)

def update_day_start_abonement(message):
    _new_day = message.text
    _date_start = datetime.strptime(_new_day, '%Y-%m-%d')
    _days = calendar.monthrange(_date_start.year, _date_start.month)[1]
    _date_end = _date_start + timedelta(days=_days)
    _date_start = _date_start.date()
    _date_end = _date_end.date()
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('UPDATE users SET day_start_abonement = "%s", day_end_abonement = "%s" WHERE chat_id = "%s"' % (_date_start, _date_end, message.chat.id))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Дата изменена')



@bot.message_handler(commands=['change_day_end_abonement'])
def change_day_end_abonement(message):
    bot.send_message(message.chat.id, 'Введите ник пользователя без @')
    bot.register_next_step_handler(message, add_new_day_end_abonement)

def add_new_day_end_abonement(message):
    _telegram_nick =  message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE telegram_nickname = '%s'"% (_telegram_nick))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[1]}'
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да!', callback_data = 'change_day_end_abonement')
    btn2 = types.InlineKeyboardButton('Нет', callback_data = 'not_find_nick')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f'Надо поменять дату окончания абонемента у {info}?', reply_markup=markup)

def update_day_end_abonement(message):
    _new_day =  message.text
    _date_end = datetime.strptime(_new_day, '%Y-%m-%d').date()
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('UPDATE users SET day_end_abonement = "%s" WHERE chat_id = "%s"' % (_date_end, message.chat.id))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Дата изменена')



@bot.message_handler(commands=['change_day_end_abonement_all'])
def change_day_end_abonement_all(message):
    bot.send_message(message.chat.id, 'ВСЕ!\nВведите количество дней, на которые надо сдвинуть абонемент')
    bot.register_next_step_handler(message, add_new_day_end_abonement_all)

def add_new_day_end_abonement_all(message):
    global _new_days_end_all
    _new_days_end_all =  message.text
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да!', callback_data = 'change_day_end_abonement_all')
    btn2 = types.InlineKeyboardButton('Нет', callback_data = 'not_find_nick')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f'Надо ВСЕМ сдвинуть дату окончания абонемента на {_new_days_end_all} дней?', reply_markup=markup)



@bot.message_handler(commands=['myinfo'])
def my_info(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT abonement_type FROM users WHERE chat_id = '%s'"% (message.chat.id))
    users = cur.fetchall()
    check_chekin = ''
    for el in users:
        check_chekin += f'{el[0]}'
    cur.close()
    conn.close()
    if (check_chekin == 'None'):
        bot.send_message(message.chat.id, 'Вы ни на что не записаны. Для записи нажмите /signup')
    else:
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE chat_id = '%s'"% (message.chat.id))
        users = cur.fetchall()
        info = ''
        for el in users:
            info += f'<b>Вид абонемента:</b> {el[7]}\n<b>Дата оформления абонемента:</b> {el[11]}\n<b>Дата окончиния абонемента:</b> {el[12]}\n<b>Использовано</b> {el[13]} тренировок из {el[9]}\n<b>Аренда шкафчика до</b>: {el[14]}\n\n<em>Даты отображаются в фотмате ГГГГ-ММ-ДД</em>'
        conn.close()
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Продлить абонемент', callback_data = 'renew_abonement')
        btn2 = types.InlineKeyboardButton('Оформить заморозку', callback_data = 'freeze_abonement')
        btn3 = types.InlineKeyboardButton('Отметиться на сегодняшней тренировке', callback_data = 'check_in')
        btn4 = types.InlineKeyboardButton('Арендовать шкафчик', callback_data = 'rent_locker')
        markup.row(btn1)
        markup.row(btn2, btn4)
        markup.row(btn3)
        bot.send_message(message.chat.id, info, parse_mode='html', reply_markup=markup)

def freeze_check(message):
    if (message.content_type == 'photo'):
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("UPDATE users SET frozen_number = '2', day_end_abonement = DATE(day_end_abonement, '+3 days') WHERE chat_id = '%s'" % (message.chat.id))
        conn.commit()
        cur.execute("SELECT * FROM users WHERE chat_id = '%s'"% (message.chat.id))
        users = cur.fetchall()
        info = ''
        for el in users:
            info += f'ВТОРАЯ ЗАМОРОЗКА\n\nФИО взрослого: {el[1]}\nФИО ребёнка: {el[2]}\nНомер: {el[5]}\nТелега: @{el[6]}\nТип абонемента: {el[7]}\nГруппа: {el[8]}\nКоличество занятий: {el[9]}\nДата продления: {datetime.now().date()}'
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Абонемент продлён на 3 дня')
        bot.send_message(-4143866178, info)
        bot.forward_message(-4143866178, message.from_user.id, message.message_id)
    else:
        bot.reply_to(message, 'Это не справка. Попробуте продлить ещё раз')



@bot.message_handler(commands=['all_notification'])
def all_notification(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    btn = types.KeyboardButton('!Всем!')
    markup.add(btn)
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT abonement_type FROM price GROUP BY abonement_type")
    price = cur.fetchall()
    info = list()
    for abonement_type in price:
        info.append(abonement_type)
    cur.close()
    conn.close()
    for el in info:
        btn = types.KeyboardButton(str(el)[2:-3])
        markup.add(btn)
    bot.send_message(message.chat.id, 'Выберете, кому хотите отправить уведомления.\n\n<em>Для отмены записи нажмите /cancel</em>', parse_mode='html', reply_markup=markup)
    bot.register_next_step_handler(message, all_notification)

def all_notification(message):
    global _type_of_abonement_notification
    _type_of_abonement_notification = message.text
    if (_type_of_abonement_notification == "/cancel"):
        bot.send_message(message.chat.id, '<em>Доступные команды можно посмотреть в меню слева от клавиатуры.</em>', parse_mode='html')
    else:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Текст', callback_data = 'all_text')
        btn2 = types.InlineKeyboardButton('Фото', callback_data = 'all_photo')
        btn3 = types.InlineKeyboardButton('Текст и фото', callback_data = 'all_text_and_photo')
        markup.row(btn1, btn2, btn3)
        bot.send_message(message.chat.id, 'Выберете вид уведомления', reply_markup=markup)

def all_notification_text(message):
    global _notification
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да!', callback_data = 'all_notification_text')
    btn2 = types.InlineKeyboardButton('Нет', callback_data = 'not_find_nick')
    markup.row(btn1, btn2)
    _notification = message.text
    bot.send_message(message.chat.id, f'Нужно отправить:\n{_notification}', parse_mode='html', reply_markup=markup)

def all_notification_photo(message):
    global _notification_photo
    file_info = bot.get_file(message.document.file_id)
    _photo = bot.download_file(file_info.file_path)
    _notification_photo = message.document.file_name
    with open(_notification_photo, 'wb') as new_file:
        new_file.write(_photo)
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да!', callback_data = 'all_notification_photo')
    btn2 = types.InlineKeyboardButton('Нет', callback_data = 'not_find_nick')
    markup.row(btn1, btn2)
    bot.send_photo(message.chat.id, open(_notification_photo, 'rb'), caption=f'Нужно отправить только это фото?', parse_mode='html', reply_markup=markup)

def all_notification_text_and_photo(message):
    global _notification
    _notification = message.text
    bot.send_message(message.chat.id, 'Приложите фото документом, которое хотите отправить')
    bot.register_next_step_handler(message, all_notification_photo_and_text)

def all_notification_photo_and_text(message):
    global _notification_photo
    global _notification
    file_info = bot.get_file(message.document.file_id)
    _photo = bot.download_file(file_info.file_path)
    _notification_photo = message.document.file_name
    with open(_notification_photo, 'wb') as new_file:
        new_file.write(_photo)
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да!', callback_data = 'all_notification_text_and_photo')
    btn2 = types.InlineKeyboardButton('Нет', callback_data = 'not_find_nick')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Отправить так?')
    bot.send_photo(message.chat.id, open(_notification_photo, 'rb'), caption=f'{_notification}', parse_mode='html', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'start_adult':
        bot.send_message(callback.message.chat.id, 'Введите ваше ФИО')
        bot.register_next_step_handler(callback.message, phone_number)

    if callback.data == 'start_kid':
        bot.send_message(callback.message.chat.id, 'Введите ФИО ребёнка')
        bot.register_next_step_handler(callback.message, adult_with_kid)

    if callback.data == 'find_out_adult_schedule':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM schedule')
        schedule = cur.fetchall()
        info = ''
        for el in schedule:
            info += f'Взрослые:\n{el[1]}'
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, info)

    if callback.data == 'find_out_kid_schedule':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM schedule')
        schedule = cur.fetchall()
        info = ''
        for el in schedule:
            info += f'Дети:\n{el[2]}'
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, info)

    if callback.data == 'change_adult_schedule':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM schedule')
        schedule = cur.fetchall()
        info = ''
        for el in schedule:
            info += el[1]
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, f'{info}\n\n<em>На что хотите поменять?</em>', parse_mode='html')
        bot.register_next_step_handler(callback.message, change_adult_schedule)

    if callback.data == 'change_kid_schedule':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM schedule')
        schedule = cur.fetchall()
        info = ''
        for el in schedule:
            info += el[2]
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, f'{info}\n\n<em>На что хотите поменять?</em>', parse_mode='html')
        bot.register_next_step_handler(callback.message, change_kid_schedule)

    if callback.data == 'find_out_group_price':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('SELECT type_of_sport FROM price WHERE abonement_type = "Групповой" GROUP BY type_of_sport')
        schedule = cur.fetchall()
        info = '<em>Групповые в месяц</em>'
        for el in schedule:
            info += f'\n<b>{str(el)[2:-3]}:</b>\n'
            cur.execute('SELECT * FROM price WHERE abonement_type = "Групповой" and type_of_sport = "%s"'% (el))
            price = cur.fetchall()
            for pr in price:
                info += f'{pr[3]} шт - {pr[4]} рублей\n'
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, f'{info}\n\nЧтобы записаться на занятия нажмите /signup', parse_mode='html')

    if callback.data == 'find_out_splite_price':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('SELECT type_of_sport FROM price WHERE abonement_type = "Сплит" GROUP BY type_of_sport')
        schedule = cur.fetchall()
        info = '<em>Сплит</em>'
        for el in schedule:
            info += f'\n<b>{str(el)[2:-3]}:</b>\n'
            cur.execute('SELECT * FROM price WHERE abonement_type = "Сплит" and type_of_sport = "%s"'% (el))
            price = cur.fetchall()
            for pr in price:
                info += f'{pr[3]} шт - {pr[4]} рублей\n'
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, f'{info}\n\nЧтобы записать на занятия нажмите /signup', parse_mode='html')

    if callback.data == 'find_out_individual_price':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('SELECT type_of_sport FROM price WHERE abonement_type = "Индивидуальный" GROUP BY type_of_sport')
        schedule = cur.fetchall()
        info = '<em>Индивидуальные</em>'
        for el in schedule:
            info += f'\n<b>{str(el)[2:-3]}:</b>\n'
            cur.execute('SELECT * FROM price WHERE abonement_type = "Индивидуальный" and type_of_sport = "%s"'% (el))
            price = cur.fetchall()
            for pr in price:
                info += f'{pr[3]} шт - {pr[4]} рублей\n'
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, f'{info}\n\nЧтобы записать на занятия нажмите /signup', parse_mode='html')

    if callback.data == 'add_new_admin':
        global _telegram_nick
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('UPDATE users SET is_superuser = "true" WHERE telegram_nickname = "%s"' % (_telegram_nick))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, 'Админ создан')

    if callback.data == 'renew_abonement':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("""SELECT price
                    FROM price
                    WHERE abonement_type in (SELECT abonement_type FROM users WHERE chat_id = '%s')
                    and type_of_sport in (SELECT type_of_sport FROM users WHERE chat_id = '%s')
                    and abonement_count_workout in (SELECT abonement_count_workout FROM users WHERE chat_id = '%s')"""% (callback.message.chat.id, callback.message.chat.id, callback.message.chat.id))
        price = cur.fetchall()
        info = ''
        for el in price:
           info += f'{el[0]}'
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, f'Для оплаты необходимо перевести <b>{info}</b> рублей\nна Cбербанк\nпо номеру <b>8(985)913-45-16</b>\nна имя Дмитрия Юрьевича М.\n\nЧтобы оплата прошла, необходимо прикрепить сюда СКРИНШОТ чека СРАЗУ после этого сообщения. Для проверки успешности оплаты зайдите в /myinfo\n⚠️ <em>Если абонемент не отобразился, свяжитесь с администратором @psy_sensei</em>', parse_mode='html')
        bot.register_next_step_handler(callback.message, cool_signup_check)

    if callback.data == 'freeze_abonement':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Заморозить', callback_data = 'freeze')
        markup.add(btn1)
        bot.send_message(callback.message.chat.id, 'Если после завершения оплаченного месяца, у вас осталась одна не использованная тренировка, то можно сдвинуть дату окончания абонемента на 3 дня, чтобы её использовать.\n\n<em>Действует только для групп</em>', parse_mode='html', reply_markup=markup)

    if callback.data == 'freeze':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("SELECT abonement_type, frozen_number, day_end_abonement FROM users WHERE chat_id = '%s'"% (callback.message.chat.id))
        user = cur.fetchall()
        abonement_type = ''
        frozen_number = ''
        day_end_abonement = ''
        for el in user:
            abonement_type += f'{el[0]}'
            frozen_number += f'{el[1]}'
            day_end_abonement += f'{el[2]}'
        cur.close()
        conn.close()
        dt = datetime.strptime(day_end_abonement, '%Y-%m-%d')
        date_end = dt + timedelta(days=3)
        if (abonement_type != 'Групповой'):
            bot.send_message(callback.message.chat.id, 'Эта функция доступна только по групповому абонементу')
        else:
            if (frozen_number == '0' and date_end.strftime('%Y-%m-%d') >= datetime.now().strftime('%Y-%m-%d')):
                conn = sqlite3.connect('tigris_clube.sql')
                cur = conn.cursor()
                cur.execute("UPDATE users SET frozen_number = '1', day_end_abonement = DATE(day_end_abonement, '+3 days')   WHERE chat_id = '%s'" % (callback.message.chat.id))
                conn.commit()
                cur.execute("SELECT * FROM users WHERE chat_id = '%s'"% (callback.message.chat.id))
                users = cur.fetchall()
                info = ''
                for el in users:
                    info += f'ЗАМОРОЗКА\n\nФИО взрослого: {el[1]}\nФИО ребёнка: {el[2]}\nНомер: {el[5]}\nТелега: @{el[6]}\nТип абонемента: {el[7]}\nГруппа: {el[8]}\nКоличество занятий: {el[9]}\nДата продления: {datetime.now().date()}'
                cur.close()
                conn.close()
                bot.send_message(callback.message.chat.id, 'Абонемент продлён на 3 дня')
                bot.send_message(-4143866178, info)
            elif (frozen_number == '1' and date_end.strftime('%Y-%m-%d') >= datetime.now().strftime('%Y-%m-%d')):
                bot.send_message(callback.message.chat.id, 'Приложите справку')
                bot.register_next_step_handler(callback.message, freeze_check)
            else:
                bot.send_message(callback.message.chat.id, 'Больше заморозка не доступна')


    if callback.data == 'check_in':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('UPDATE users SET current_count_workout = current_count_workout + 1 WHERE chat_id = "%s"' % (callback.message.chat.id))
        conn.commit()
        cur.execute("SELECT * FROM users WHERE chat_id = '%s'"% (callback.message.chat.id))
        users = cur.fetchall()
        info = ''
        abonement_count_workout = ''
        current_count_workout = ''
        for el in users:
            info += f'Тип абонемента: {el[7]}\nФИО взрослого: {el[1]}\nФИО ребёнка: {el[2]}\nНомер: {el[5]}\nТелега: @{el[6]}'
            abonement_count_workout += f'{el[8]}'
            current_count_workout += f'{el[9]}'
        cur.close()
        conn.close()
        if (current_count_workout == abonement_count_workout):
            bot.send_message(-4143866178, f'{datetime.now().date()} будет ПОСЛЕДНЯЯ тренировка у\n\n{info}')
            bot.send_message(callback.message.chat.id, 'Это последняя оплаченная тренировка')
        else:
            bot.send_message(-4143866178, f'{datetime.now().date()} будет тренировка у\n\n{info}')
            bot.send_message(callback.message.chat.id, 'Вы отметились')

    if callback.data == 'not_find_nick':
        bot.send_message(callback.message.chat.id, 'Операция отменена')

    if callback.data == 'delete_user':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE telegram_nickname = "%s"' % (_telegram_nick))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, 'Пользователь удалён')


    if callback.data == 'inactive_user':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('UPDATE users SET is_active = "false" WHERE telegram_nickname = "%s"' % (_telegram_nick))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, 'Пользователь не будет получать нотификации')

    if callback.data == 'change_locker_days_left':
        bot.send_message(callback.message.chat.id, 'Напишите дату окончиния аренды шкафчика в формате ГГГГ-ММ-ДД')
        bot.register_next_step_handler(callback.message, update_locker_days_left)

    if callback.data == 'change_day_start_abonement':
        bot.send_message(callback.message.chat.id, 'Напишите дату начала использования абонемента в формате ГГГГ-ММ-ДД')
        bot.register_next_step_handler(callback.message, update_day_start_abonement)

    if callback.data == 'change_day_end_abonement':
        bot.send_message(callback.message.chat.id, 'Напишите дату окончания использования абонемента в формате ГГГГ-ММ-ДД')
        bot.register_next_step_handler(callback.message, update_day_end_abonement)

    if callback.data == 'change_day_end_abonement_all':
        global _new_days_end_all
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('UPDATE users SET day_end_abonement = DATE(day_end_abonement, "+%s days")' % (_new_days_end_all))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, 'Дата изменена')

    if callback.data == 'delete_abonement':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('DELETE FROM price WHERE abonement_type = "%s" and type_of_sport = "%s" and abonement_count_workout = "%s"'% (_abonement_type, _type_of_sport, _abonement_count_workout))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, 'Абонемент удалён')

    if callback.data == 'delete_add':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("SELECT photo FROM additionalservices WHERE type = '%s'"% (_type_addit))
        additionalservices = cur.fetchall()
        info = ''
        for el in additionalservices:
            info += f'{el[0]}'
        os.remove(f"{info}")
        cur.execute('DELETE FROM additionalservices WHERE type = "%s"'% (_type_addit))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, 'Услуга удалена')

    if callback.data == 'rent_locker':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Арендовать', callback_data = 'change_date_end_rent_locker')
        btn2 = types.InlineKeyboardButton('Что-то не хочется', callback_data = 'not_find_nick')
        markup.add(btn1, btn2)
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("SELECT description, price FROM additionalservices WHERE type = 'Аренда шкафчика'")
        additionalservices = cur.fetchall()
        info = ''
        for el in additionalservices:
            info += f'{el[0]} за {el[1]} рублей'
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, f'{info}', parse_mode='html', reply_markup=markup)

    if callback.data == 'change_date_end_rent_locker':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("SELECT price FROM additionalservices WHERE type = 'Аренда шкафчика'")
        additionalservices = cur.fetchall()
        info = ''
        for el in additionalservices:
            info += f'{el[0]}'
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, f'Для того, чтобы взять шкафчик в аренду, оплатите <b>{info}</b> рублей на Сбербанк\nпо номеру <b>8(985)913-45-16</b>\nна имя Дмитрия Юрьевича М. И пришлите СКРИНШОТ чека СРАЗУ после этого сообщения.', parse_mode='html')
        bot.register_next_step_handler(callback.message, change_date_end_rent_locker)

    if callback.data == 'all_notification_text':
        global _notification
        if (_type_of_abonement_notification == "!Всем!"):
            conn = sqlite3.connect('tigris_clube.sql')
            cur = conn.cursor()
            cur.execute("SELECT chat_id FROM users where is_active = 'true'")
            users = cur.fetchall()
            info = ''
            for el in users:
                bot.send_message(el[0], _notification, parse_mode='html')
            cur.close()
            conn.close()
        else:
            conn = sqlite3.connect('tigris_clube.sql')
            cur = conn.cursor()
            cur.execute("SELECT chat_id FROM users where is_active = 'true' and abonement_type = '%s'"%(_type_of_abonement_notification))
            users = cur.fetchall()
            info = ''
            for el in users:
                bot.send_message(el[0], _notification, parse_mode='html')
            cur.close()
            conn.close()
        bot.send_message(callback.message.chat.id, 'Готово')

    if callback.data == 'all_notification_photo':
        if (_type_of_abonement_notification == "!Всем!"):
            conn = sqlite3.connect('tigris_clube.sql')
            cur = conn.cursor()
            cur.execute("SELECT chat_id FROM users where is_active = 'true'")
            users = cur.fetchall()
            for el in users:
                bot.send_photo(el[0], open(_notification_photo, 'rb'))
            cur.close()
            conn.close()
        else:
            conn = sqlite3.connect('tigris_clube.sql')
            cur = conn.cursor()
            cur.execute("SELECT chat_id FROM users where is_active = 'true' and abonement_type = '%s'"%(_type_of_abonement_notification))
            users = cur.fetchall()
            for el in users:
                bot.send_photo(el[0], open(_notification_photo, 'rb'))
            cur.close()
            conn.close()
        os.remove(f"{_notification_photo}")
        bot.send_message(callback.message.chat.id, 'Готово')

    if callback.data == 'all_notification_text_and_photo':
        if (_type_of_abonement_notification == "!Всем!"):
            conn = sqlite3.connect('tigris_clube.sql')
            cur = conn.cursor()
            cur.execute("SELECT chat_id FROM users where is_active = 'true'")
            users = cur.fetchall()
            for el in users:
                bot.send_photo(el[0], open(_notification_photo, 'rb'), caption=f'{_notification}')
            cur.close()
            conn.close()
        else:
            conn = sqlite3.connect('tigris_clube.sql')
            cur = conn.cursor()
            cur.execute("SELECT chat_id FROM users where is_active = 'true' and abonement_type = '%s'"%(_type_of_abonement_notification))
            users = cur.fetchall()
            for el in users:
                bot.send_photo(el[0], open(_notification_photo, 'rb'), caption=f'{_notification}')
            cur.close()
            conn.close()
        os.remove(f"{_notification_photo}")
        bot.send_message(callback.message.chat.id, 'Готово')

    if callback.data == 'agree':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Взрослый', callback_data = 'start_adult')
        btn2 = types.InlineKeyboardButton('Ребёнок', callback_data = 'start_kid')
        markup.row(btn1, btn2)
        bot.send_message(callback.message.chat.id, 'Для кого хотели бы приобрести абонемент\n\n<em>Чтобы начать заполнение заново, нажмите 2 раза /start до окончания регистрации</em>',  parse_mode='html', reply_markup=markup)

    if callback.data == 'all_text':
        bot.send_message(callback.message.chat.id, 'Напишите текст, который хотите отправить')
        bot.register_next_step_handler(callback.message, all_notification_text)

    if callback.data == 'all_photo':
        bot.send_message(callback.message.chat.id, 'Приложите фото документом, которое хотите отправить')
        bot.register_next_step_handler(callback.message, all_notification_photo)

    if callback.data == 'all_text_and_photo':
        bot.send_message(callback.message.chat.id, 'Напишите текст, который хотите прикрепить к фото')
        bot.register_next_step_handler(callback.message, all_notification_text_and_photo)



bot.infinity_polling()