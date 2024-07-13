#импорты библиотек
from configs.cfg import gst, base
from configs.forParse import days,titles,days_cells
from configs.dictionaries import groupsToTables,tablesToKeys
from configs.groups import groupList1v
from configs.databaseTables import tableList1v
groupList = groupList1v
tableList = tableList1v
import sqlite3
import gspread
from time import sleep
import os
from week import cur_week
import numpy as np

#настройка основных библиотек
weekNumber = f'{cur_week()} неделя'
googleSheets = gspread.service_account(filename = gst)
db = sqlite3.connect(base,check_same_thread = False)
cur = db.cursor()

#чистка бд
def clearDatabase():
	for table in tableList:
		cur.execute(f'DROP TABLE IF EXISTS {table};')
		db.commit()
		print(f'Deleted table: {table}')

#создание таблиц БД
def createTables():
	for table in tableList:
		cur.execute(f'CREATE TABLE IF NOT EXISTS {table}('
					'day TEXT NOT NULL,'
					'schedule TEXT'
					')')
		db.commit();
		print(f'Created table: {table}')

#сохранение таблицы 
def saveTable(group,day,schedule):
	if group in groupList:
		table = groupsToTables.get(group)
		print(table)
		cur.execute(f"SELECT schedule FROM {table} WHERE day = '{day}'")
		cur.execute(f'INSERT INTO {table} VALUES(?,?);',(day,schedule))
		db.commit()
		print(f'Saved schedule for group: {group}\nDay: {day}');
	else:
		print('Group not exists.')

#получаем ячейки
def getCells(day):
	cells = days_cells.get(day);
	return cells;

#парсим расписание
def parseSchedule():
	for group in groupList:
		print(group)
		table = groupsToTables.get(group)
		print(table)
		key = tablesToKeys.get(table)
		googleTable = googleSheets.open_by_key(key)
		worksheet = googleTable.worksheet(f'{weekNumber}')
		for day in days:
			cur.execute(f"SELECT schedule FROM {table} WHERE day = '{day}'")
			rawData = cur.fetchone()
			if rawData is None:
				cells = getCells(day)
				schedule = np.array(worksheet.get(cells))
				schedule[schedule == '!'] = 'Окно'
				s = [''] * 6;
				for i in range(len(s)):
					if schedule[i][0] == schedule[i][1]:
						if schedule[i][0] == 'Окно':
							s[i] = ''
						else:
							s[i] = f'{titles[i]}\n{schedule[i][0]}\n'
					else:
						s[i] = f'{titles[i]}\n{schedule[i][0]} | {schedule[i][1]}\n'
				scheduleString = '\n'.join(s);
				if scheduleString.strip() == '':
					scheduleString = 'Пар нет.'
				saveTable(group,day,scheduleString)
				sleep(5)

def main():
	clearDatabase()
	createTables()
	parseSchedule()
if __name__ == '__main__':
	main();