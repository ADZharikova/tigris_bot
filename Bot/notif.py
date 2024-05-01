from datetime import datetime, timedelta
import sqlite3
import telebot
import time

bot = telebot.TeleBot('7069056617:AAHnd4Y6PE2TpKuJLdxg2GdHuo1IeICrS20')

class Notif:

    def notification(self, _chat: str):
        time.sleep(2332800)
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('SELECT day_start_abonement FROM users WHERE chat_id = "%s" and is_active = "true"' % (_chat))
        users = cur.fetchall()
        day_start_abonement = ''
        for el in users:
            day_start_abonement += f'{el[0]}'
        cur.close()
        conn.close()

        dt = datetime.strptime(day_start_abonement, '%Y-%m-%d')
        _target_date = dt + timedelta(days=26)

        if (_target_date < datetime.now()):
            bot.send_message(_chat, '❗️ Скоро истекает ваш абонемент. Проверить дату окончания можно в /myinfo', parse_mode='html')


        time.sleep(259200)
        conn = sqlite3.connect('tigris_clube.sql')
        cur = conn.cursor()
        cur.execute('SELECT day_start_abonement FROM users WHERE chat_id = "%s" and is_active = "true"' % (_chat))
        users = cur.fetchall()
        day_start_abonement = ''
        for el in users:
            day_start_abonement += f'{el[0]}'
        cur.close()
        conn.close()

        dt = datetime.strptime(day_start_abonement, '%Y-%m-%d')
        _target_date = dt + timedelta(days=29)

        if (_target_date < datetime.now()):
            bot.send_message(_chat, '❗️ Не забудьте продлить абонемент. Дату окончания абонемента можно проверить в /myinfo', parse_mode='html')