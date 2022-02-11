import config
import telebot
import random
import datetime
import calendar
import pytz
import os, sys
import database
import logger
import sqlite3
from database import User

from telebot import types

bot = telebot.TeleBot(config.token) # here you need your personal token

if __name__ == "__main__":
    users = database.getusers()

    count = 0
    for user in users:
        if user[0] > 0:
            if count > 8:
                bot.send_message(user[0],
                             "Было обновлено расписание бота для нового семестра! Попробуй! \n/reset - если не работает расписание на день")
                print('Notified:', user)
            count += 1

    print('Users notified: ', count)



