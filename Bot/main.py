import telebot
from telebot import types
import sqlite3
from datetime import timedelta, date, datetime
import pandas as pd


bot = telebot.TeleBot('7141651810:AAHdkWKqG-GvzPZ-7qbXWuBiBuXA6PCiVks')
_kid_name = '-'


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users
                (id int auto_increment primary key, 
                fio_adult varchar(100), 
                fio_kid varchar(100), 
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
                inst_ru varchar(50))""")
    
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

    conn.commit()
    cur.close()
    conn.close()
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('/Взрослый')
    btn2 = types.KeyboardButton('/Ребёнок')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Здравствуйте!\nКто будет ходить?\n\n<em>Чтобы начать заполнение заново, нажмите /start до окончания регистрации</em>',  parse_mode='html', reply_markup=markup)



@bot.message_handler(commands=['Взрослый'])
def adult(message):
    bot.send_message(message.chat.id, 'Введите ваше ФИО')
    bot.register_next_step_handler(message, phone_number)
        
def phone_number(message):
        global _adalt_name
        _adalt_name = message.text
        bot.send_message(message.chat.id, 'Введите телефона без "8" для окончания регистрации\n<em>Пример: 9876543210</em>',  parse_mode='html')
        bot.register_next_step_handler(message, register)

def register(message):
        global _phone_number
        _phone_number = message.text
        if (len(_phone_number) != 10):
            bot.send_message(message.chat.id, 'Номер введён некорректно')
            bot.register_next_step_handler(message, register)
        else:
            conn = sqlite3.connect('tigris_clube.sql')
            cur = conn.cursor()
            cur.execute("INSERT INTO users (fio_adult, fio_kid, is_superuser, phone_number, telegram_nickname, current_count_workout) VALUES ('%s', '%s', '%s', '%s', '%s', 0)" % (_adalt_name, _kid_name, "false", _phone_number, message.from_user.username))
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, 'Регистрация прошла успешно\n\nДоступные команды:\n/myinfo - Информация о моих тренировках\n/price - Узнать цены\n/schedule - Узнать расписание\n/signup - Записаться на занятие\n/additionalservices - Дополнительные услуги\n/socialnetwork - Добавить свою соц сеть\n/contacts - Контакты')



@bot.message_handler(commands=['Ребёнок'])
def kid(message):
    bot.send_message(message.chat.id, 'Введите ФИО ребёнка')
    bot.register_next_step_handler(message, adult_with_kid)

def adult_with_kid(message):
    global _kid_name
    _kid_name = message.text
    bot.send_message(message.chat.id, 'Введите ваше ФИО')
    bot.register_next_step_handler(message, phone_number)



@bot.message_handler(commands=['users_list'])
def users_list(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE telegram_nickname = "%s"' % (message.from_user.username))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users')
        users = cur.fetchall()
        info = 'ФИО взрослого;ФИО ребёнка;Админские права;Номер телефона;Ник телеграм;Тип абонемента;Вид Спорта;Количество дней в абонементе;Количество тренировок, которые отходил;Дата начала абонемента;Дата окончания абонемента;Есть ли шкафчик;Дата окончания аренды шкафчика;Количество заморозок;vk_ru;inst_ru\n'
        for el in users:
            info += f'{el[1]};{el[2]};{el[3]};{el[4]};{el[5]};{el[6]};{el[7]};{el[8]};{el[9]};{el[10]};{el[11]};{el[12]};{el[13]};{el[14]};{el[15]};{el[16]}\n'
        cur.close()
        conn.close()
        user = pd.DataFrame({info})
        user.to_csv('users.csv', index=False, encoding='utf-8')
        bot.send_document(message.chat.id, open('users.csv', 'rb'))
        bot.send_message(message.chat.id, f'Если в файле криво, то надо поменять кодировку в exel на UTF-8\n\n{info}')
    else:
        bot.send_message(message.chat_id, 'Вы не админ')



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
    cur.execute('SELECT is_superuser FROM users WHERE telegram_nickname = "%s"' % (message.from_user.username))
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
        bot.send_message(message.chat_id, 'Вы не админ')

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
def change_schedule(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE telegram_nickname = "%s"' % (message.from_user.username))
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
        bot.send_message(message.chat_id, 'Вы не админ')



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
    cur.execute('SELECT is_superuser FROM users WHERE telegram_nickname = "%s"' % (message.from_user.username))
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
                ('Групповой', 'ММА группа №1', '8', '4500'),
                ('Групповой', 'ММА группа №1', '12', '5500'),
                ('Групповой', 'ММА группа №1', 'Безлимит', '8000'),
                ('Групповой', 'ММА группа №2', '1', '800'),
                ('Групповой', 'ММА группа №2', '8', '4500'),
                ('Групповой', 'ММА группа №2', '12', '5500'),
                ('Групповой', 'ММА группа №2', 'Безлимит', '8000'),
                ('Групповой', 'Бокс', '1', '800'),
                ('Групповой', 'Бокс', '8', '4500'),
                ('Групповой', 'Бокс', '12', '5500'),
                ('Групповой', 'Бокс', 'Безлимит', '8000'),
                ('Групповой', 'Тайский бокс (Муай Тай)', '1', '800'),
                ('Групповой', 'Тайский бокс (Муай Тай)', '8', '4500'),
                ('Групповой', 'Тайский бокс (Муай Тай)', '12', '5500'),
                ('Групповой', 'Тайский бокс (Муай Тай)', 'Безлимит', '8000'),
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
        bot.send_message(message.chat_id, 'Вы не админ')



@bot.message_handler(commands=['add_new_price'])
def add_new_price(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE telegram_nickname = "%s"' % (message.from_user.username))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        bot.send_message(message.chat.id, 'Напишите тип абонемента:\nГрупповой\nИндивидуальный\nСплит')
        bot.register_next_step_handler(message, add_abonement_type)
    else: 
        bot.send_message(message.chat_id, 'Вы не админ')

def add_abonement_type(message):
    global _abonement_type
    _abonement_type = message.text
    bot.send_message(message.chat.id, 'Напишите вид спорта')
    bot.register_next_step_handler(message, add_type_of_sport)

def add_type_of_sport(message):
    global _type_of_sport
    _type_of_sport = message.text
    bot.send_message(message.chat.id, 'Напишите количество тренировок')
    bot.register_next_step_handler(message, add_abonement_count_workout)

def add_abonement_count_workout(message):
    global _abonement_count_workout
    _abonement_count_workout = message.text
    bot.send_message(message.chat.id, 'Напишите цену')
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
def add_new_price(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE telegram_nickname = "%s"' % (message.from_user.username))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        bot.send_message(message.chat.id, 'Укажите тип абонемента:\nГрупповой\nИндивидуальный\nСплит')
        bot.register_next_step_handler(message, change_price_abonement_type)
    else:
        bot.send_message(message.chat_id, 'Вы не админ')

def change_price_abonement_type(message):
    global _abonement_type
    _abonement_type = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT type_of_sport FROM price WHERE abonement_type = '%s' GROUP BY type_of_sport"% (_abonement_type))
    price = cur.fetchall()
    info = ''
    for el in price:
        info += f'{el[0]}\n'
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f'Укажите вид спорта\n\n{info}')
    bot.register_next_step_handler(message, change_price_type_of_sport)

def change_price_type_of_sport(message):
    global _type_of_sport
    _type_of_sport = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT abonement_count_workout FROM price WHERE abonement_type = '%s' and type_of_sport = '%s'"% (_abonement_type, _type_of_sport))
    price = cur.fetchall()
    info = ''
    for el in price:
        info += f'{el[0]}\n'
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f'Укажите количество занятий\n\n{info}')
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



@bot.message_handler(commands=['signup'])
def signup(message):
    bot.send_message(message.chat.id, 'Укажите тип абонемента:\nГрупповой\nИндивидуальный\nСплит\n\n<em>Скопируйте и вставьте одно из значений</em>', parse_mode='html')
    bot.register_next_step_handler(message, signup_abonement_type)

def signup_abonement_type(message):
    global _abonement_type
    _abonement_type = message.text.strip()
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT type_of_sport FROM price WHERE abonement_type = '%s' GROUP BY type_of_sport"% (_abonement_type))
    price = cur.fetchall()
    info = ''
    for el in price:
        info += f'{el[0]}\n'
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f'Укажите вид спорта\n{info}\n\n<em>Скопируйте и вставьте одно из значений\nЕсли информации нет, начните сначала /signup</em>', parse_mode='html')
    bot.register_next_step_handler(message, signup_type_of_sport)

def signup_type_of_sport(message):
    global _type_of_sport
    _type_of_sport = message.text.strip()
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT abonement_count_workout FROM price WHERE abonement_type = '%s' and type_of_sport = '%s'"% (_abonement_type, _type_of_sport))
    price = cur.fetchall()
    info = ''
    for el in price:
        info += f'{el[0]}\n'
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f'Укажите количество занятий\n{info}\n\n<em>Скопируйте и вставьте одно из значений\nЕсли информации нет, начните сначала /signup</em>', parse_mode='html')
    bot.register_next_step_handler(message, signup_abonement_count_workout)

def signup_abonement_count_workout(message):
    global _abonement_count_workout
    _abonement_count_workout = message.text.strip()
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT price FROM price WHERE abonement_type = '%s' and type_of_sport = '%s' and abonement_count_workout = '%s'"% (_abonement_type, _type_of_sport, _abonement_count_workout))
    price = cur.fetchall()
    info = ''
    for el in price:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f'Для оплаты необходимо перевести {info} рублей на сбербанк по номеру 89990009900\nЧтобы оплата прошла, необходимо отправиь чек СРАЗУ после этого сообщения, иначе он не обработается\n\n<em>Если сумма не отобразилась, начните сначала /signup</em>', parse_mode='html')
    bot.register_next_step_handler(message, signup_check)

def signup_check(message):
    if (message.content_type == 'photo'):
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("UPDATE users SET abonement_type = '%s', type_of_sport = '%s', abonement_count_workout = '%s', day_start_abonement = CURRENT_DATE, day_end_abonement = DATE(CURRENT_DATE, '+1 month'), current_count_workout = '0', frozen_number = '0'  WHERE telegram_nickname = '%s'" % (_abonement_type, _type_of_sport, _abonement_count_workout, message.from_user.username))
        conn.commit()
        cur.execute("SELECT * FROM users WHERE telegram_nickname = '%s'"% (message.from_user.username))
        users = cur.fetchall()
        info = ''
        for el in users:
            info += f'ЧЕК\n\nФИО взрослого: {el[1]}\nФИО ребёнка: {el[2]}\nНомер: {el[4]}\nТелега: @{el[5]}\nТип абонемента: {el[6]}\nГруппа: {el[7]}\nКоличество занятий: {el[8]}\n'
        cur.close()
        conn.close()
        bot.send_message(-4143866178, info)
        bot.forward_message(-4143866178, message.from_user.id, message.message_id)
        bot.reply_to(message, 'Чек получен и отправлен преподавателю. Спасибо!')
    else:
        bot.reply_to(message, 'Начните сначала /signup')

def cool_signup_check(message):
    if (message.content_type == 'photo'):
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("UPDATE users SET day_start_abonement = CURRENT_DATE, day_end_abonement = DATE(CURRENT_DATE, '+1 month'), current_count_workout = '0', frozen_number = '0' WHERE telegram_nickname = '%s'" % (message.from_user.username))
        conn.commit()
        cur.execute("SELECT * FROM users WHERE telegram_nickname = '%s'"% (message.from_user.username))
        users = cur.fetchall()
        info = ''
        for el in users:
            info += f'ЧЕК\n\nФИО взрослого: {el[1]}\nФИО ребёнка: {el[2]}\nНомер: {el[4]}\nТелега: @{el[5]}\nТип абонемента: {el[6]}\nГруппа: {el[7]}\nКоличество занятий: {el[8]}\n'
        cur.close()
        conn.close()
        bot.send_message(-4143866178, info)
        bot.forward_message(-4143866178, message.from_user.id, message.message_id)
        bot.reply_to(message, 'Чек получен и отправлен преподавателю. Спасибо!')
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
    bot.send_message(message.chat.id, 'Введите ссылку')
    bot.register_next_step_handler(message, add_vk)
    
def add_vk(message):
    _vk = message.text
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('UPDATE users SET vk_ru = "%s" WHERE telegram_nickname = "%s"' % (_vk, message.from_user.username))
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
    cur.execute('UPDATE users SET inst_ru = "%s" WHERE telegram_nickname = "%s"' % (_inst, message.from_user.username))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Соцсеть добавлена')



@bot.message_handler(commands=['additionalservices'])
def find_out_price(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Аренда шкафчика', callback_data = 'look_at_locker')
    btn2 = types.InlineKeyboardButton('Купить книгу', callback_data = 'look_at_book')
    btn3 = types.InlineKeyboardButton('Купить шейкер', callback_data = 'look_at_shaker')
    markup.row(btn1)
    markup.row(btn2, btn3)
    bot.send_message(message.chat.id, 'Что вас интересует?', reply_markup=markup)



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
    cur.execute('SELECT is_superuser FROM users WHERE telegram_nickname = "%s"' % (message.from_user.username))
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'{el[0]}'
    cur.close()
    conn.close()
    if (info == "true"):
        bot.send_message(message.chat.id, "Команды, доступные админам:\n\nРАБОТА С ПОЛЬЗОВАТЕЛЯМИ:\n/users_list - Вывести список пользователей\n/add_admin_user - Сделать пользователя админом\n/delete_user - Удалить неактивного пользователя\n/chat_id - Узнать id текущего чата (доступно всем)\n\nРАБОТА С РАСПИСАНИЕМ:\n/add_schedule_first_time - Самый первый раз добавить расписание (сделать один раз при запуске)\n/change_schedule - Поменять расписание\n\nРАБОТА С ЦЕНАМИ:\n/add_price_first_time - Самый первый раз добавить цены (сделать один раз при запуске)\n/add_new_price - Добавить новый вид абонемента\n/change_price - Поменять цену существующего абонемента\n\nИЗМЕНЕНИЕ ДАТ:\n/change_day_start_abonement - поменять дату начала абонемента определённого пользователя\n/locker_days_left - поменять дату начала пользования шкафчиком у определённого пользователя\n\nДОП ВОЗМОЖНОСТИ:\n/change_contacts - Поменять информацию в графе 'Контакты'\n/all_notification - отправить всем уведомление")
    else:
        bot.send_message(message.chat.id, "Вы не админ")



@bot.message_handler(commands=['delete_user'])
def delete_user(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute('SELECT is_superuser FROM users WHERE telegram_nickname = "%s"' % (message.from_user.username))
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
        info += f'{el[1]}\n'
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да!', callback_data = 'delete_user')
    btn2 = types.InlineKeyboardButton('Нет', callback_data = 'not_find_nick')
    markup.row(btn1)
    markup.row(btn2)
    bot.send_message(message.chat.id, f'Надо удалить {info}?\n\n<em>Если нет, то /delete_user</em>', parse_mode='html', reply_markup=markup)



@bot.message_handler(commands=['add_admin_user'])
def add_admin_user(message):
    bot.send_message(message.chat.id, 'Введите ник нового админа без @')
    bot.register_next_step_handler(message, add_new_admin)

def add_new_admin(message):
    global _telegram_nick
    _telegram_nick =  message.text
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
    markup.row(btn1)
    markup.row(btn2)
    bot.send_message(message.chat.id, f'Надо сделать админом {info}\n\n<em>Если нет, то /add_admin_user</em>', parse_mode='html', reply_markup=markup)



@bot.message_handler(commands=['myinfo'])
def my_info(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("SELECT abonement_type FROM users WHERE telegram_nickname = '%s'"% (message.from_user.username))
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
        cur.execute("SELECT * FROM users WHERE telegram_nickname = '%s'"% (message.from_user.username))
        users = cur.fetchall()
        info = ''
        for el in users:
            info += f'Вид абонемента: {el[6]}\nДата оформления абонемента (ГГГГ-ММ-ДД): {el[10]}\nДата окончиния абонемента (ГГГГ-ММ-ДД): {el[11]}\nИспользовано {el[9]} тренировок из {el[8]}\nШкафчик действует до {el[13]}'
        cur.close()
        conn.close()
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Продлить абонемент', callback_data = 'renew_abonement')
        btn2 = types.InlineKeyboardButton('Оформить заморозку', callback_data = 'freeze_abonement')
        btn3 = types.InlineKeyboardButton('Отметиться на сегодняшней тренировке', callback_data = 'check_in')
        markup.row(btn1)
        markup.row(btn2)
        markup.row(btn3)
        bot.send_message(message.chat.id, info, reply_markup=markup)

def freeze_check(message):
    if (message.content_type == 'photo'):
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("UPDATE users SET frozen_number = '2' WHERE telegram_nickname = '%s'" % (message.from_user.username))
        conn.commit()
        cur.execute("SELECT * FROM users WHERE telegram_nickname = '%s'"% (message.from_user.username))
        users = cur.fetchall()
        info = ''
        for el in users:
            info += f'ВТОРАЯ ЗАМОРОЗКА\n\nФИО взрослого: {el[1]}\nФИО ребёнка: {el[2]}\nНомер: {el[4]}\nТелега: @{el[5]}\nТип абонемента: {el[6]}\nГруппа: {el[7]}\nКоличество занятий: {el[8]}\n'
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Абонемент продлён на 3 дня')
        bot.send_message(-4143866178, info)
        bot.forward_message(-4143866178, message.from_user.id, message.message_id)
    else:
        bot.reply_to(message, 'Это не чек. Попробуте продлить ещё раз')



@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
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
            info += {el[2]}
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, f'{info}\n\n<em>На что хотите поменять?</em>', parse_mode='html')
        bot.register_next_step_handler(callback.message, change_kid_schedule)

    if callback.data == 'find_out_group_price':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM price WHERE abonement_type = "Групповой"')
        schedule = cur.fetchall()
        info = ''
        for el in schedule:
            info += f'{el[2]}: {el[3]} в месяц - {el[4]} рублей\n'
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, f'{info}\n\nЧтобы записать на занятия нажмите /signup')

    if callback.data == 'find_out_splite_price':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM price WHERE abonement_type = "Сплит"')
        schedule = cur.fetchall()
        info = ''
        for el in schedule:
            info += f'{el[2]}: {el[3]} в месяц - {el[4]} рублей\n'
        cur.close()
        conn.close()

        bot.send_message(callback.message.chat.id, f'{info}\n\nЧтобы записать на занятия нажмите /signup')

    if callback.data == 'find_out_individual_price':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM price WHERE abonement_type = "Индивидуальный"')
        schedule = cur.fetchall()
        info = ''
        for el in schedule:
            info += f'{el[2]}: {el[3]} в месяц - {el[4]} рублей\n'
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, f'{info}\n\nЧтобы записать на занятия нажмите /signup')

    if callback.data == 'look_at_locker':
        bot.send_photo(callback.message.chat.id, open('locker.webp', 'rb'), caption='<em>$Цена</em>\n\nЧтобы взять в аренду шкафчик напишите @psy_sensei', parse_mode='html')
    
    if callback.data == 'look_at_book':
        bot.send_photo(callback.message.chat.id, open('book.jpg', 'rb'), caption='<em>$Цена</em>\n\nЧтобы купить книгу напишите @psy_sensei', parse_mode='html')

    if callback.data == 'look_at_shaker':
        bot.send_photo(callback.message.chat.id, open('shacker.jpg', 'rb'), caption='<em>$Цена</em>\n\nЧтобы купить шейкер напишите @psy_sensei', parse_mode='html')

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
                    WHERE abonement_type in (SELECT abonement_type FROM users WHERE telegram_nickname = '%s')
                    and type_of_sport in (SELECT type_of_sport FROM users WHERE telegram_nickname = '%s')
                    and abonement_count_workout in (SELECT abonement_count_workout FROM users WHERE telegram_nickname = '%s')"""% (callback.from_user.username, callback.from_user.username, callback.from_user.username))
        price = cur.fetchall()
        info = ''
        for el in price:
           info += f'{el[0]}'
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, f'Для оплаты необходимо перевести {info} рублей на сбербанк по номеру 89990009900\nЧтобы оплата прошла, необходимо отправиь чек СРАЗУ после этого сообщения, иначе он не обработается', parse_mode='html')
        bot.register_next_step_handler(callback.message, cool_signup_check)

    if callback.data == 'freeze_abonement':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Заморозить', callback_data = 'freeze')
        markup.add(btn1)
        bot.send_message(callback.message.chat.id, 'Если вы не успели отходить 1 тренировку за месяц, то даётся 3 дополнительных дня, чтобы её отходить\n\n<em>Действует только для групп</em>', parse_mode='html', reply_markup=markup)

    if callback.data == 'freeze':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute("SELECT abonement_type, frozen_number, day_end_abonement FROM users WHERE telegram_nickname = '%s'"% (callback.from_user.username))
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
                    cur.execute("UPDATE users SET frozen_number = '1' WHERE telegram_nickname = '%s'" % (callback.from_user.username))
                    conn.commit()
                    cur.close()
                    conn.close()
                    bot.send_message(callback.message.chat.id, 'Абонемент продлён на 3 дня')
            elif (frozen_number == '1' and date_end.strftime('%Y-%m-%d') >= datetime.now().strftime('%Y-%m-%d')):
                bot.send_message(callback.message.chat.id, 'Приложите справку')
                bot.register_next_step_handler(callback.message, freeze_check)
            else:
                bot.send_message(callback.message.chat.id, 'Больше заморозка не доступна')


    if callback.data == 'check_in':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('UPDATE users SET current_count_workout = current_count_workout + 1 WHERE telegram_nickname = "%s"' % (callback.from_user.username))
        conn.commit()
        cur.execute("SELECT * FROM users WHERE telegram_nickname = '%s'"% (callback.from_user.username))
        users = cur.fetchall()
        info = ''
        abonement_count_workout = ''
        current_count_workout = ''
        for el in users:
            info += f'ФИО взрослого: {el[1]}\nФИО ребёнка: {el[2]}\nНомер: {el[4]}\nТелега: @{el[5]}'
            abonement_count_workout += f'{el[8]}'
            current_count_workout += f'{el[9]}'
        cur.close()
        conn.close()
        if (current_count_workout == abonement_count_workout):
            bot.send_message(-4143866178, f'Сегодня будет ПОСЛЕДНЯЯ тренировка у\n\n{info}')
            bot.send_message(callback.message.chat.id, 'Это последняя оплаченная тренировка')
        else:
            bot.send_message(-4143866178, f'Сегодня будет тренировка у\n\n{info}')
            bot.send_message(callback.message.chat.id, 'Вы отметились')

    if callback.data == 'not_find_nick':
        bot.send_message(callback.message.chat.id, 'Начните сначала')

    if callback.data == 'delete_user':
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE telegram_nickname = "%s"' % (_telegram_nick))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, 'Пользователь удалён')

bot.infinity_polling()