# - *- coding: utf- 8 - *-

import config
import telebot
import random
import datetime
import calendar
import pytz
import os, sys
import database
import logger
import time
from database import User

from telebot import types

bot = telebot.TeleBot(config.token) # here you need your personal token
logger = logger.get_logger("bot")
user_dict = {}

def get_time():
	return datetime.datetime.now(pytz.timezone('Europe/Minsk'))

def get_week_number(date = get_time()):
	if date.isocalendar()[1] % 2  == 1:
		return 1;
	return 2;

def shrink_command(input):
	i = input.find('@')
	if i != -1:
		return input[1:i]
	return input[1:]

def get_main_markup():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row('Понедельник', 'Вторник', 'Среда')
	markup.row('Четверг', 'Пятница', 'Суббота')
	markup.row('Сегодня', 'Завтра', 'Сброс')
	return markup

def get_course_markup():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	markup.row('1', '2', '3', '4')
	return markup

def get_group_markup():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	markup.row('1', '2', '3', '4', '5', '6')
	markup.row('7', '8', '9', '10', '11', '12')
	return markup

def get_subgroup_markup():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	markup.row('1', '2')
	return markup

def process_course(message):
	try:
		id = message.chat.id
		user = User(int(id))
		course = message.text
		if not course.isdigit() or int(course) > 4 or int(course) < 1:
			raise Exception("Не верный курс")
		user.course = int(course)		
		user_dict[id] = user
		msg = bot.reply_to(message, 'Выберите группу', reply_markup=get_group_markup())
		bot.register_next_step_handler(msg, process_group_step)
	except Exception as e:
		bot.reply_to(message, 'Что-то пошло не так :/ Попробуйте команду /help')
		logger.error("{0}|{1}|{2}: {3} - ERROR_MSG: {4}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text, e))

def process_group_step(message):
	try:
		id = message.chat.id
		user = user_dict[id]
		group = message.text
		if not group.isdigit() or int(group) > 12 or int(group) < 1:
			raise Exception("Не верная группа")
		user.idgroup = int(group)
		msg = bot.reply_to(message, 'Выберите подгруппу', reply_markup=get_subgroup_markup())
		bot.register_next_step_handler(msg, process_subgroup_step)
	except Exception as e:
		bot.reply_to(message, 'Что-то пошло не так :/ Попробуйте команду /help')
		logger.error("{0}|{1}|{2}: {3} - ERROR_MSG: {4}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text, e))

def process_subgroup_step(message):
	try:
		id = message.chat.id
		user = user_dict[id]
		subgroup = message.text
		if subgroup != '1' and subgroup != '2':
			raise Exception("Не верная подгруппа")
		user.subgroup = int(subgroup)
		user.last_message = get_time()
		user.username = message.chat.username
		user.first_name = message.chat.first_name
		user.last_name = message.chat.last_name
		if database.getuser(id) == None:
			database.adduser(user)
		else:
			database.updateuser(user)
		user_dict.pop(id)
		bot.send_message(id, 'Спасибо, можете выбрать нужный вам день!', reply_markup=get_main_markup())
	except Exception as e:
		bot.reply_to(message, 'Что-то пошло не так :/ Попробуйте команду /help')
		logger.error("{0}|{1}|{2}: {3} - ERROR_MSG: {4}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text, e))

def registration(message):
	msg = bot.reply_to(message, 'Выберите курс', reply_markup=get_course_markup())
	bot.register_next_step_handler(msg, process_course)

def get_user(message):
	user = database.getuser(message.chat.id)
	if user == None:
		user = registrate_user(message)
	else:
		user.last_message = get_time()
		user.username = message.chat.username
		user.first_name = message.chat.first_name
		user.last_name = message.chat.last_name
		database.updateuser(user)
	return user

def registrate_user(message):
	bot.reply_to(message, 'Сначала заполните нужные данные!')
	registration(message)
	return database.getuser(message.chat.id)

@bot.message_handler(commands=['start'])
def welcome(message):
	logger.info("{0}|{1}|{2}: {3}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text))
	try:
		bot.send_message(message.chat.id, "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот созданный для вывода информации о расписании факультета ИТ БГТУ.".format(message.from_user, bot.get_me()), parse_mode='html')
		registration(message)
	except Exception as e:
		bot.reply_to(message, 'Что-то пошло не так :/ Попробуйте команду /help')
		logger.error("{0}|{1}|{2}: {3} - ERROR_MSG: {4}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text, e))


@bot.message_handler(commands=['reset'])
def reset(message):
	logger.info("{0}|{1}|{2}: {3}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text))
	try:
		bot.reply_to(message, 'Сброс настроек!')
		registration(message)
	except Exception as e:
		bot.reply_to(message, 'Что-то пошло не так :/ Попробуйте команду /help')
		logger.error("{0}|{1}|{2}: {3} - ERROR_MSG: {4}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text, e))


@bot.message_handler(commands=['help'])
def help(message):
	logger.info("{0}|{1}|{2}: {3}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text))
	header = "Я - <b>{0.first_name}</b>, бот созданный для вывода информации о расписании факультета ИТ БГТУ.".format(bot.get_me())
	contact = "Если появились вопросы, встретили баг или неточность, писать сюда: @dmtr_den. Ник на github: dim-den ";
	commands = '''<b>Команды бота</b>:
	/help - информация о боте, его командах
	/reset - сброс выбора курса, группы, подгруппы
	/start - инициализация бота
	/today - расписание на сегодня
	/tomorrow - расписание на завтра
	/monday - расписание на понедельник
	/tuesday - расписание на вторник
	/wednesday - расписание на среду
	/thursday- расписание на четверг
	/friday - расписание на пятницу
	/saturday - расписание на субботу
	'''
	post = 'P.S. В групповых чатах работа осуществляется только через команды описаные выше (обычный текст не обрабатывается)'
	bot.send_message(message.chat.id, "{0}\n\n{1}\n\n{2}\n\n{3}".format(header, contact, commands, post), parse_mode='html')

@bot.message_handler(commands=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday' ])
def weekday(message):
	logger.info("{0}|{1}|{2}: {3}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text))
	try:
		user = get_user(message)
		day = database.eng_ru[shrink_command(message.text)]
		bot.send_message(message.chat.id, get_week_day_schedule(day.title(), user), parse_mode='html')
	except Exception as e:
		bot.reply_to(message, 'Что-то пошло не так :/ Попробуйте команду /help')
		logger.error("{0}|{1}|{2}: {3} - ERROR_MSG: {4}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text, e))

 
@bot.message_handler(commands=['today'])
def today(message):
	logger.info("{0}|{1}|{2}: {3}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text))
	try:
		user = get_user(message)
		weekday = get_time().weekday()
		if weekday == 6:
			bot.send_message(message.chat.id, "Сегодня выходной :)\n")
		else:        		
			bot.send_message(message.chat.id, "<b>{0}:</b>\n{1}".format('Сегодня', database.getschedule(user.course, user.idgroup, user.subgroup, weekday, get_week_number())), 
						parse_mode='html')
	except Exception as e:
		bot.reply_to(message, 'Что-то пошло не так :/ Попробуйте команду /help')
		logger.error("{0}|{1}|{2}: {3} - ERROR_MSG: {4}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text, e))


@bot.message_handler(commands=['tomorrow'])
def tomorrow(message):
	logger.info("{0}|{1}|{2}: {3}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text))
	try:
		user = get_user(message)
		tomorrow = get_time() + datetime.timedelta(days=1)
		weekday = tomorrow.weekday()
		if weekday == 6:
			bot.send_message(message.chat.id, "Завтра выходной :)\n")
		else:        		
			bot.send_message(message.chat.id, "<b>{0}:</b>\n{1}".format('Завтра', database.getschedule(user.course, user.idgroup, user.subgroup, weekday, get_week_number(tomorrow))), 
						parse_mode='html')
	except Exception as e:
		bot.reply_to(message, 'Что-то пошло не так :/ Попробуйте команду /help')
		logger.error("{0}|{1}|{2}: {3} - ERROR_MSG: {4}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text, e))

def get_week_day_schedule(week_day, user):
	current_week_day = get_time().weekday()
	week = get_week_number()

	if current_week_day > database.day_number[week_day.lower()]:
		if week == 1:
			week = 2
		else:
			week = 1
		return "<b>{0} на следующей неделе:</b>\n{1}".format(week_day, database.getschedule(user.course, user.idgroup, user.subgroup, database.day_number[week_day.lower()], week))

	return "<b>{0}:</b>\n{1}".format(week_day, database.getschedule(user.course, user.idgroup, user.subgroup, database.day_number[week_day.lower()], week))

@bot.message_handler(content_types=['text'])
def callback(message):
	try:		
		user = get_user(message)
		logger.info("{0}|{1}|{2}: {3}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text))

		if message.text in ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'] :
			bot.send_message(message.chat.id, get_week_day_schedule(message.text, user), parse_mode='html')
		elif message.text == 'Сегодня':
			weekday = get_time().weekday()
			if weekday == 6:
				bot.send_message(message.chat.id, "Сегодня выходной :)\n")
			else:        		
				bot.send_message(message.chat.id, "<b>{0}:</b>\n{1}".format(message.text, database.getschedule(user.course, user.idgroup, user.subgroup, weekday, get_week_number())), 
					parse_mode='html')
		elif message.text == 'Завтра':
			tomorrow = get_time() + datetime.timedelta(days=1)
			weekday = tomorrow.weekday()
			if weekday == 6:
				bot.send_message(message.chat.id, "Завтра выходной :)\n")
			else:        		
				bot.send_message(message.chat.id, "<b>{0}:</b>\n{1}".format(message.text, database.getschedule(user.course, user.idgroup, user.subgroup, weekday, get_week_number(tomorrow))), 
					parse_mode='html')
		elif message.text == 'Сброс':
			bot.reply_to(message, 'Сброс настроек!')
			registration(message)
		elif message.text.lower() == 'anime' or message.text.lower() == 'аниме':
			bot.reply_to(message, 'cила !')
		elif message.chat.type == 'private':
			bot.send_message(message.chat.id, 'Я не знаю что ответить 😢 Попробуйте команду /help')
	except Exception as e:
		bot.reply_to(message, 'Что-то пошло не так :/ Попробуйте команду /help')
		logger.error("{0}|{1}|{2}: {3} - ERROR_MSG: {4}".format(message.chat.username, message.chat.first_name,message.chat.last_name, message.text, e))

def main():
	try:
		bot.infinity_polling(timeout=10, long_polling_timeout=5)
		# bot.polling(none_stop=True)

	except Exception as e:
		logger.error("INTERNAL ERROR - ERROR_MSG: {0}".format(e))
		time.sleep(15)

if __name__ == '__main__':
	main()


