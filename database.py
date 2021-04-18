import sqlite3
import os

lesson_time = ['08.00-9.35', '09.50-11.25', '11.40-13.15', '13.50-15.25', '15.40-17.15', '17.30-19.05', '19.20-20.55']
day_number = {'понедельник' : 0, 'вторник' : 1, 'среда' : 2, 'четверг' : 3, 'пятница' : 4, 'суббота' : 5  }
eng_ru = {'monday' : 'понедельник', 'tuesday' : 'вторник', 'wednesday' : 'среда', 'thursday' : 'четверг', 'friday' : 'пятница', 'saturday' : 'суббота' }

class User:
	def __init__(self, id):
		self.id = id
		self.course = None
		self.idgroup = None
		self.subgroup = None
		self.last_message = None
		self.username = None
		self.first_name = None
		self.last_name = None

def getfile(filename):
	script_directory = os.path.dirname(os.path.abspath(__file__))
	return os.path.join(script_directory, filename)


def getschedule(course, idgroup, subgroup, week_day, week):
	conn = sqlite3.connect(getfile('schedule.db'))
	cursor = conn.cursor()

	sqlselect = '''SELECT * FROM TIMETABLE WHERE course = ? AND idgroup = ? AND subgroup = ? 
											AND week_day = ?  AND week = ?'''

	cursor.execute(sqlselect, (course, idgroup, subgroup, week_day, week))

	res = ""
	for line in cursor.fetchall():
		time = lesson_time[int(line[5])]
		audotorium = line[8]
		lesson_type = line[6]
		subject = line[7]
		if audotorium != None and lesson_type != None :
			res += "{0} ({1}): {2}. {3}\n".format(time, audotorium, lesson_type, subject)
		elif audotorium != None:
			res += "{0} ({1}): {2}\n".format(time, audotorium, subject)
		elif lesson_type != None:
			res += "{0}: {1}. {2}\n".format(time, lesson_type, subject)
		else:
			res += "{0}: {1}\n".format(time, subject)

	if res == "":
		res = "Упс, информации об расписании на этот день нет :("
	return res

def getuser(id):
	sqlselect = 'SELECT * FROM user WHERE ID = ?'
	conn = sqlite3.connect(getfile('users.db'))
	cursor = conn.cursor()
	cursor.execute(sqlselect, (id, ))
	res = cursor.fetchone()
	if res == None:
		return None
	user = User(id)
	user.course = res[1]
	user.idgroup = res[2]
	user.subgroup = res[3]
	user.last_message = res[4]
	user.username = res[5]
	user.first_name = res[6]
	user.last_name = res[7]
	return user

def adduser(user):
	sqlinsert = '''INSERT INTO USER(id,course,idgroup,subgroup,last_message,username,first_name,last_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?);'''
	conn = sqlite3.connect(getfile('users.db'))
	cursor = conn.cursor()
	cursor.execute(sqlinsert, (user.id,user.course,user.idgroup,user.subgroup, user.last_message, user.username, user.first_name, user.last_name))
	conn.commit()

def updateuser(user):
	sqlinsert = '''UPDATE USER SET course = ?, idgroup = ?, subgroup = ?, last_message = ?, username = ?, first_name = ?, last_name = ?  WHERE id = ?;'''
	conn = sqlite3.connect(getfile('users.db'))
	cursor = conn.cursor()
	cursor.execute(sqlinsert, (user.course,user.idgroup,user.subgroup, user.last_message, user.username, user.first_name, user.last_name, user.id))
	conn.commit()
