import telebot
from telebot import types
import sqlite3
from datetime import date
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
            cur.execute("INSERT INTO users (fio_adult, fio_kid, is_superuser, phone_number, telegram_nickname) VALUES ('%s', '%s', '%s', '%s', '%s')" % (_adalt_name, _kid_name, "false", _phone_number, message.from_user.username))
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, 'Регистрация прошла успешно\n\nДоступные команды:\n/price - Узнать цены\n/schedule - Узнать расписание\n/signup - Записаться на занятие\n/myinfo - Информация о моих тренировках\n/additional_services - Дополнительные услуги\n/socialnetwork - Добавить свою соц сеть\n/contacts - Контакты')



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
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    info = 'ФИО взрослого;ФИО ребёнка;админские права;номер;телега;тип абонемента;type_of_sport;abonement_count_workout;current_count_workout;day_start_abonement;day_end_abonement;is_have_locker;locker_days_left;frozen_number;vk_ru;inst_ru\n'
    for el in users:
        info += f'{el[1]};{el[2]};{el[3]};{el[4]};{el[5]};{el[6]};{el[7]};{el[8]};{el[9]};{el[10]};{el[11]};{el[12]};{el[13]};{el[14]};{el[15]};{el[16]}\n'
    cur.close()
    conn.close()
    user = pd.DataFrame({info})
    user.to_csv('users.csv', index=False, encoding='utf-8')
    bot.send_document(message.chat.id, open('users.csv', 'rb'))
    bot.send_message(message.chat.id, f'Если в файле криво, то надо поменять кодировку в exel на UTF-8\n\n{info}')



@bot.message_handler(commands=['schedule'])
def find_out_schedule(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Взрослые', callback_data = 'find_out_adult_schedule')
    btn2 = types.InlineKeyboardButton('Дети', callback_data = 'find_out_kid_schedule')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Чьё расписание интересует?', reply_markup=markup)



@bot.message_handler(commands=['change_schedule'])
def change_schedule(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Взрослые', callback_data = 'change_adult_schedule')
    btn2 = types.InlineKeyboardButton('Дети', callback_data = 'change_kid_schedule')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Выберете чьё расписание хотите поменять и введите его', reply_markup=markup)

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
        cur.execute('DELETE FROM price')
        cur.execute("INSERT INTO schedule (adult_schedule, kid_schedule) VALUES ('Взрослые', 'Дети')")
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Данные добавлены')



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
    bot.send_message(message.chat.id, 'Дане')



@bot.message_handler(commands=['add_new_price'])
def add_new_price(message):
    bot.send_message(message.chat.id, 'Напишите тип абонемента:\nГрупповой\nИндивидуальный\nСплит')
    bot.register_next_step_handler(message, add_abonement_type)

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
    bot.send_message(message.chat.id, 'Укажите тип абонемента:\nГрупповой\nИндивидуальный\nСплит')
    bot.register_next_step_handler(message, change_price_abonement_type)

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
    bot.send_message(message.chat.id, f'Укажите вид спорта\n{info}\n\n<em>Скопируйте и вставьте одно из значений\nЕсли написано "None", начните сначала /signup</em>', parse_mode='html')
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
    bot.send_message(message.chat.id, f'Укажите количество занятий\n{info}\n\n<em>Скопируйте и вставьте одно из значений\nЕсли написано "None", начните сначала /signup</em>', parse_mode='html')
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
    bot.send_message(message.chat.id, f'Для оплаты необходимо перевести {info} рублей на сбербанк по номеру 89990009900\nЧтобы оплата прошла, необходимо отправиь чек СРАЗУ после этого сообщения, иначе он не обработается', parse_mode='html')
    bot.register_next_step_handler(message, signup_check)

def signup_check(message):
    conn = sqlite3.connect('tigris_clube.sql')
    cur = conn.cursor()
    cur.execute("UPDATE users SET abonement_type = '%s', type_of_sport = '%s', abonement_count_workout = '%s', day_start_abonement = CURRENT_DATE, day_end_abonement = DATE(CURRENT_DATE, '+1 month') WHERE telegram_nickname = '%s'" % (_abonement_type, _type_of_sport, _abonement_count_workout, message.from_user.username))
    conn.commit()
    cur.execute("SELECT * FROM users WHERE telegram_nickname = '%s'"% (message.from_user.username))
    users = cur.fetchall()
    info = 'ФИО взрослого, ФИО ребёнка, Номер, Телега, Тип абонемента, Группа, Количество занятий\n'
    for el in users:
        info += f'{el[1]}, {el[2]}, {el[4]}, {el[5]}, {el[6]}, {el[7]}, {el[8]}\n'
    cur.close()
    conn.close()
    bot.send_message(-4143866178, info)
    bot.forward_message(-4143866178, message.from_user.id, message.message_id)
    bot.reply_to(message, 'Чек получен и отправлен преподавателю. Спасибо!')



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



@bot.message_handler(commands=['additional_services'])
def find_out_price(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Аренда шкафчика', callback_data = 'look_at_locker')
    btn2 = types.InlineKeyboardButton('Купить книгу', callback_data = 'look_at_book')
    btn3 = types.InlineKeyboardButton('Купить шейкер', callback_data = 'look_at_shaker')
    markup.row(btn1)
    markup.row(btn2, btn3)
    bot.send_message(message.chat.id, 'Что вас интересует?', reply_markup=markup)



@bot.message_handler(commands=['contacts'])
def find_out_chat_id(message):
    bot.send_message(message.chat.id, """<em>Любая информация по тренировкам клуба TIGRIS:</em> +7(985)913-45-16 (@psy_sensei) - Дмитрий\n\n<em>Администратор клуба:</em> +7(901)744-33-28 - ИО\n\n<em>Почта:</em> mma_tigris@bk.ru""", parse_mode='html')



@bot.message_handler(commands=['admin_help'])
def find_out_chat_id(message):
    bot.send_message(message.chat.id, """Команды, доступные админам:\n/users_list - Вывести список пользователей\n/change_schedule - Поменять расписание\n/add_price - Добавить новый вид абонемента\n/change_price - Поменять цену абонемента\n/chat_id - узнать id текущего чата""")



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

bot.infinity_polling()





# @bot.message_handler(content_types=['photo'])
# def get_photo(message):
#     bot.send_message(-4143866178, f'{_kohay_name}')
#     bot.forward_message(-4143866178, message.from_user.id, message.message_id)
#     bot.reply_to(message, 'Чек отправлен преподавателю. Спасибо!')

# @bot.message_handler(commands=['dogovor'])
# def main(message):
#     bot.send_message(message.chat.id, 'Загрузите договор и дождитесь сообщения о загрузке')

# @bot.message_handler(content_types=['document'])
# def get_document(message):
#     bot.reply_to(message, 'Документ получен. Спасибо!')
#     bot.send_message(-4143866178, f'{_kohay_name}')
#     bot.forward_message(-4143866178, message.from_user.id, message.message_id)