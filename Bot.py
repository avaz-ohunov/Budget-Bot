# Bot.py

from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text, EMPTY_KEYBOARD
from vkbottle import PhotoMessageUploader
from vkbottle import BaseStateGroup
from vkbottle import CtxStorage
from BotToken import bot_token
import importlib
import os
from datetime import datetime
import sqlite3


# Регистрация бота
bot = Bot(token = bot_token)
ctx_name = CtxStorage()


# Состояния принта бюджетов
class ShowBudgets(BaseStateGroup):
	get_budget_num = 1
	get_command = 2
	change_name = 3
	change_summ_plus = 4
	change_summ_minus = 5


# Состояния создания нового бюджета
class CreateBudgets(BaseStateGroup):
	get_name = 1
	get_summ = 2


# Состояния принта общих бюджетов
class ShowOurBudgets(BaseStateGroup):
	get_budget_num = 1
	get_command = 2
	change_name = 3
	change_summ_plus = 4
	change_summ_minus = 5


# Состояния создания нового общего бюджета
class CreateOurBudgets(BaseStateGroup):
	get_name = 1
	get_summ = 2


# Кнопки
kb_budgets = Keyboard()
kb_budgets.add(Text("Мои бюджеты"))
kb_budgets.add(Text("Общие бюджеты"))
kb_budgets.row()
kb_budgets.add(Text("Всего денег"), color = KeyboardButtonColor.PRIMARY)


kb_cancel_create_budgets = Keyboard()
kb_cancel_create_budgets.add(Text("Назад"), color = KeyboardButtonColor.NEGATIVE)
kb_cancel_create_budgets.add(Text("Создать бюджет"), color = KeyboardButtonColor.POSITIVE)


kb_get_command = Keyboard()

kb_get_command.add(Text("Редактировать название"))
kb_get_command.row()

kb_get_command.add(Text("Ввод ➕"), color = KeyboardButtonColor.POSITIVE)
kb_get_command.add(Text("Вывод ➖"), color = KeyboardButtonColor.POSITIVE)
kb_get_command.row()

kb_get_command.add(Text("Удалить бюджет"), color = KeyboardButtonColor.NEGATIVE)
kb_get_command.add(Text("Назад"), color = KeyboardButtonColor.NEGATIVE)


kb_back = Keyboard()
kb_back.add(Text("Назад"), color = KeyboardButtonColor.NEGATIVE)


kb_cancel = Keyboard()
kb_cancel.add(Text("Отмена"), color = KeyboardButtonColor.NEGATIVE)


kb_continue = Keyboard()
kb_continue.add(Text("Пропустить"))


kb_cancel_continue = Keyboard()
kb_cancel_continue.add(Text("Отмена"), color = KeyboardButtonColor.NEGATIVE)
kb_cancel_continue.add(Text("Пропустить"))


# Регистрация юзера
def reg(user_id):
	with sqlite3.connect('База данных.db') as db:
		sql = db.cursor()
		sql.execute(f"CREATE TABLE IF NOT EXISTS t{user_id}(name TEXT, summ TEXT)")


# Метод создания динамической клавиатуры
def create_keyboard(nums):
	global dynamic_kb
	dynamic_kb = Keyboard()
	dynamic_kb.add(Text("Назад"), color = KeyboardButtonColor.NEGATIVE)
	dynamic_kb.add(Text("Создать бюджет"), color = KeyboardButtonColor.POSITIVE)
	dynamic_kb.row()

	for i in range(nums):
		i += 1
		if i % 5 == 0:
			dynamic_kb.row()
			dynamic_kb.add(Text(str(i)))

		else:
			dynamic_kb.add(Text(str(i)))


# Метод показа бюджетов
def show_budgets(user_id):
	global budget_names, budget_amount, db, sql

	budget_names = ""
	budget_amount = 0
	with sqlite3.connect('База данных.db') as db:
		sql = db.cursor()
		for budget in sql.execute(f"SELECT name FROM t{user_id}"):
			budget_amount += 1
			budget_names += f"{budget_amount}) {budget[0]}\n"

	if budget_names == "":
		budget_names = "У вас пока нет бюджетов.\nВы можете их создать, нажав на кнопку «Создать бюджет»👇"


# Метод выбора бюджета
def choose_budget(user_id):
	global dict_names, dict_name
	dict_names = {}
	dict_name = {}
	i = 0

	with sqlite3.connect('База данных.db') as db:
		sql = db.cursor()
		for budget in sql.execute(f"SELECT * FROM t{user_id}"):
			i += 1

			if int(budget[1]) < 0:
				dict_names.update({i: f"{budget[0]}: –₽{'{0:,}'.format(int(budget[1])).replace(',', ' ').replace('-', '')}"})
				dict_name.update({i: budget[0]})
			
			else:
				dict_names.update({i: f"{budget[0]}: ₽{'{0:,}'.format(int(budget[1])).replace(',', ' ')}"})
				dict_name.update({i: budget[0]})


# Метод изменения названия бюджета
def change_name(user_id, budget_new_name):
	name_id = ctx_name.get("name")
	budget_name = dict_name[int(name_id)]
	sql.execute(f"UPDATE t{user_id} SET name = '{budget_new_name}' WHERE name = '{budget_name}'")
	db.commit()


# Метод прибавления суммы к бюджету
def plus_summ(user_id, budget_plus):
	name_id = ctx_name.get("name")
	budget_name = dict_name[int(name_id)]

	for i in sql.execute(f"SELECT summ FROM t{user_id} WHERE name = '{budget_name}'"):
		summ = i[0]
		sql.execute(f"UPDATE t{user_id} SET summ = {int(summ) + int(budget_plus)} WHERE name = '{budget_name}'")
		db.commit()


# Метод убавления суммы с бюджета
def minus_summ(user_id, budget_minus):
	name_id = ctx_name.get("name")
	budget_name = dict_name[int(name_id)]
	
	for i in sql.execute(f"SELECT summ FROM t{user_id} WHERE name = '{budget_name}'"):
		summ = i[0]
		sql.execute(f"UPDATE t{user_id} SET summ = {int(summ) - int(budget_minus)} WHERE name = '{budget_name}'")
		db.commit()


# Метод удаления бюджета
def delete_budget(user_id):
	name_id = ctx_name.get("name")
	budget_name = dict_name[int(name_id)]
	sql.execute(f"DELETE FROM t{user_id} WHERE name = '{budget_name}'")
	db.commit()


# Метод показа обновлённого бюджета
def show_update(user_id, budget_new_name):
	global news
	
	with sqlite3.connect('База данных.db') as db:
		sql = db.cursor()
		for s in sql.execute(f"SELECT summ FROM t{user_id} WHERE name = '{budget_new_name}'"):
			if int(s[0]) < 0:
				news = f"{budget_new_name}: –₽{'{0:,}'.format(int(s[0])).replace(',', ' ').replace('-', '')}"
			
			else:
				news = f"{budget_new_name}: ₽{'{0:,}'.format(int(s[0])).replace(',', ' ')}"


# Метод создания бюджета
def create_budget(user_id, budget_name):
	global msg, sql, db

	with sqlite3.connect('База данных.db') as db:
		sql = db.cursor()
		sql.execute(f"SELECT name FROM t{user_id} WHERE name = '{budget_name}'")
	
		if sql.fetchone() is None:
			sql.execute(f"INSERT INTO t{user_id} VALUES (?, ?)", (budget_name, 0))
			msg = "Введите сумму бюджета"

		else:
			msg = "Такой бюджет уже имеется!"


# Метод создания суммы бюджета
def set_summ(user_id, budget_update_summ, budget_name):
	sql.execute(f"UPDATE t{user_id} SET summ = '{budget_update_summ}' WHERE name = '{budget_name}'")
	db.commit()


# Метод отмены создания бюджета
def cancel_create_budget(user_id, budget_name):
	sql.execute(f"DELETE FROM t{user_id} WHERE name = '{budget_name}'")
	db.commit()


# Метод показа общих бюджетов
def show_our_budgets():
	global budget_names, budget_amount, db, sql

	budget_names = ""
	budget_amount = 0
	with sqlite3.connect('База данных.db') as db:
		sql = db.cursor()
		for budget in sql.execute(f"SELECT name FROM Общие_бюджеты"):
			budget_amount += 1
			budget_names += f"{budget_amount}) {budget[0]}\n"

	if budget_names == "":
		budget_names = "Общих бюджетов пока нет.\nВы можете их создать, нажав на кнопку «Создать бюджет»👇"


# Метод выбора общего бюджета
def choose_our_budget():
	global dict_names, dict_name
	dict_names = {}
	dict_name = {}
	i = 0

	with sqlite3.connect('База данных.db') as db:
		sql = db.cursor()
		for budget in sql.execute(f"SELECT * FROM Общие_бюджеты"):
			i += 1

			if int(budget[1]) < 0:
				dict_names.update({i: f"{budget[0]}: –₽{'{0:,}'.format(int(budget[1])).replace(',', ' ').replace('-', '')}"})
				dict_name.update({i: budget[0]})
			
			else:
				dict_names.update({i: f"{budget[0]}: ₽{'{0:,}'.format(int(budget[1])).replace(',', ' ')}"})
				dict_name.update({i: budget[0]})


# Метод изменения названия общего бюджета
def change_our_name(budget_new_name):
	name_id = ctx_name.get("name")
	budget_name = dict_name[int(name_id)]
	sql.execute(f"UPDATE Общие_бюджеты SET name = '{budget_new_name}' WHERE name = '{budget_name}'")
	db.commit()


# Метод прибавления суммы к общему бюджету
def plus_our_summ(budget_plus):
	name_id = ctx_name.get("name")
	budget_name = dict_name[int(name_id)]

	for i in sql.execute(f"SELECT summ FROM Общие_бюджеты WHERE name = '{budget_name}'"):
		summ = i[0]
		sql.execute(f"UPDATE Общие_бюджеты SET summ = {int(summ) + int(budget_plus)} WHERE name = '{budget_name}'")
		db.commit()


# Метод убавления суммы с общего бюджета
def minus_our_summ(budget_minus):
	name_id = ctx_name.get("name")
	budget_name = dict_name[int(name_id)]
	
	for i in sql.execute(f"SELECT summ FROM Общие_бюджеты WHERE name = '{budget_name}'"):
		summ = i[0]
		sql.execute(f"UPDATE Общие_бюджеты SET summ = {int(summ) - int(budget_minus)} WHERE name = '{budget_name}'")
		db.commit()


# Метод удаления общего бюджета
def delete_our_budget():
	name_id = ctx_name.get("name")
	budget_name = dict_name[int(name_id)]
	sql.execute(f"DELETE FROM Общие_бюджеты WHERE name = '{budget_name}'")
	db.commit()


# Метод показа обновлённого общего бюджета
def show_our_update(budget_new_name):
	global news
	
	with sqlite3.connect('База данных.db') as db:
		sql = db.cursor()
		for s in sql.execute(f"SELECT summ FROM Общие_бюджеты WHERE name = '{budget_new_name}'"):
			if int(s[0]) < 0:
				news = f"{budget_new_name}: –₽{'{0:,}'.format(int(s[0])).replace(',', ' ').replace('-', '')}"
			
			else:
				news = f"{budget_new_name}: ₽{'{0:,}'.format(int(s[0])).replace(',', ' ')}"


# Метод создания общего бюджета
def create_our_budget(budget_name):
	global msg, sql, db

	with sqlite3.connect('База данных.db') as db:
		sql = db.cursor()
		sql.execute(f"SELECT name FROM Общие_бюджеты WHERE name = '{budget_name}'")
	
		if sql.fetchone() is None:
			sql.execute(f"INSERT INTO Общие_бюджеты VALUES (?, ?)", (budget_name, 0))
			msg = "Введите сумму бюджета"

		else:
			msg = "Такой бюджет уже имеется!"


# Метод создания суммы общего бюджета
def set_our_summ(budget_update_summ, budget_name):
	sql.execute(f"UPDATE Общие_бюджеты SET summ = '{budget_update_summ}' WHERE name = '{budget_name}'")
	db.commit()


# Метод отмены создания общего бюджета
def cancel_create_our_budget(budget_name):
	sql.execute(f"DELETE FROM Общие_бюджеты WHERE name = '{budget_name}'")
	db.commit()


# Метод суммы всех бюджетов
def summ_all_budgets(user_id):
	global all_summs
	all_summs = 0

	with sqlite3.connect("База данных.db") as db:
		sql = db.cursor()
		for summ in sql.execute(f"SELECT summ FROM t{user_id}"):
			for i in summ:
				all_summs += int(i)

		for summ in sql.execute(f"SELECT summ FROM Общие_бюджеты"):
			for i in summ:
				all_summs += int(i)


# Состояние принта бюджетов
@bot.on.message(lev = "Мои бюджеты")
async def print_budgets(message: Message):
	global lev
	lev = "my"
	show_budgets(message.peer_id)
	if budget_amount > 0:
		create_keyboard(budget_amount)
		await message.answer(budget_names, keyboard = dynamic_kb)
		await bot.state_dispenser.set(message.peer_id, ShowBudgets.get_budget_num)

	else:
		await message.answer(budget_names, keyboard = kb_cancel_create_budgets)


# Состояние получения номера бюджета
@bot.on.message(state = ShowBudgets.get_budget_num)
async def get_budget_num(message: Message):
	if message.text == "Назад":
		await bot.state_dispenser.delete(message.peer_id)
		
		try:
			ctx_name.delete("name")
		except KeyError:
			pass

		await message.answer("Главное меню", keyboard = kb_budgets)

	elif message.text == "Создать бюджет":
		await bot.state_dispenser.delete(message.peer_id)
		
		try:
			ctx_name.delete("name")
		except KeyError:
			pass

		await message.answer("Введите название бюджета", keyboard = kb_cancel)
		await bot.state_dispenser.set(message.peer_id, CreateBudgets.get_name)
	
	else:
		try:
			choose_budget(message.peer_id)
			ctx_name.set("name", message.text)
			await message.answer(dict_names[int(message.text)], keyboard = kb_get_command)
			await bot.state_dispenser.set(message.peer_id, ShowBudgets.get_command)
		except:
			await message.answer("Бюджет не найден")


# Состояние получения команды
@bot.on.message(state = ShowBudgets.get_command)
async def get_command(message: Message):
	if message.text == "Назад":
		show_budgets(message.peer_id)
		create_keyboard(budget_amount)
		await message.answer(budget_names, keyboard = dynamic_kb)
		await bot.state_dispenser.set(message.peer_id, ShowBudgets.get_budget_num)

	elif message.text == "Редактировать название":
		await message.answer("Введите новое название бюджета", keyboard = kb_back)
		await bot.state_dispenser.set(message.peer_id, ShowBudgets.change_name)

	elif message.text == "Ввод ➕":
		await message.answer("Сколько надо внести в бюджет?", keyboard = kb_back)
		await bot.state_dispenser.set(message.peer_id, ShowBudgets.change_summ_plus)

	elif message.text == "Вывод ➖":
		await message.answer("Сколько надо вывести с бюджета?", keyboard = kb_back)
		await bot.state_dispenser.set(message.peer_id, ShowBudgets.change_summ_minus)

	elif message.text == "Удалить бюджет":
		delete_budget(message.peer_id)
		await message.answer("Бюджет удалён", keyboard = kb_budgets)
		await bot.state_dispenser.delete(message.peer_id)
		ctx_name.delete("name")

	else:
		await message.answer("Команда не найдена")


# Состояние изменения названия
@bot.on.message(state = ShowBudgets.change_name)
async def change_budget_name(message: Message):
	if message.text == "Назад":
		choose_budget(message.peer_id)
		new_message = ctx_name.get("name")
		await message.answer(dict_names[int(new_message)], keyboard = kb_get_command)
		await bot.state_dispenser.set(message.peer_id, ShowBudgets.get_command)

	else:
		change_name(message.peer_id, message.text)
		show_update(message.peer_id, message.text)
		await message.answer("Бюджет обновлён", keyboard = kb_budgets)
		await message.answer(news)
		await bot.state_dispenser.delete(message.peer_id)
		ctx_name.delete("name")


# Состояние прибавления к сумме
@bot.on.message(state = ShowBudgets.change_summ_plus)
async def change_budget_summ(message: Message):
	if message.text == "Назад":
		choose_budget(message.peer_id)
		new_message = ctx_name.get("name")
		await message.answer(dict_names[int(new_message)], keyboard = kb_get_command)
		await bot.state_dispenser.set(message.peer_id, ShowBudgets.get_command)

	else:
		try:
			name_id = ctx_name.get("name")
			budget_name = dict_name[int(name_id)]
			plus_summ(message.peer_id, message.text.replace(" ", ""))
			show_update(message.peer_id, budget_name)

			await message.answer("Бюджет обновлён", keyboard = kb_budgets)
			await message.answer(news)

			await bot.state_dispenser.delete(message.peer_id)
			ctx_name.delete("name")
		except:
			await message.answer("Введите только число!")


# Состояние убавления с суммы бюджета
@bot.on.message(state = ShowBudgets.change_summ_minus)
async def change_budget_minus(message: Message):
	if message.text == "Назад":
		choose_budget(message.peer_id)
		new_message = ctx_name.get("name")
		await message.answer(dict_names[int(new_message)], keyboard = kb_get_command)
		await bot.state_dispenser.set(message.peer_id, ShowBudgets.get_command)

	else:
		try:
			name_id = ctx_name.get("name")
			budget_name = dict_name[int(name_id)]
			minus_summ(message.peer_id, message.text.replace(" ", ""))
			show_update(message.peer_id, budget_name)

			await message.answer("Бюджет обновлён", keyboard = kb_budgets)
			await message.answer(news)

			await bot.state_dispenser.delete(message.peer_id)
			ctx_name.delete("name")
		except:
			await message.answer("Введите только число!")


# Принятие названия бюджета
@bot.on.message(state = CreateBudgets.get_name)
async def get_budget_name(message: Message):
	if message.text == "Отмена":
		await bot.state_dispenser.delete(message.peer_id)
		
		try:
			ctx_name.delete("name")
		except KeyError:
			pass

		await message.answer("Главное меню", keyboard = kb_budgets)

	else:
		create_budget(message.peer_id, message.text)
		if msg == "Введите сумму бюджета":
			await message.answer(msg, keyboard = kb_cancel_continue)
			ctx_name.set("name", message.text)
			await bot.state_dispenser.set(message.peer_id, CreateBudgets.get_summ)

		elif msg == "Такой бюджет уже имеется!":
			await message.answer(msg)


# Принятие суммы бюджета
@bot.on.message(state = CreateBudgets.get_summ)
async def get_budget_summ(message: Message):
	if message.text == "Отмена":
		budget_name = ctx_name.get("name")
		cancel_create_budget(message.peer_id, budget_name)
		await message.answer("Создание бюджета отменено", keyboard = kb_budgets)

		await bot.state_dispenser.delete(message.peer_id)

		try:
			ctx_name.delete("name")
		except KeyError:
			pass

	elif message.text == "Пропустить":
		budget_name = ctx_name.get("name")
		show_update(message.peer_id, budget_name)
		await message.answer("Бюджет создан", keyboard = kb_budgets)
		await message.answer(news)

		await bot.state_dispenser.delete(message.peer_id)
		ctx_name.delete("name")
	
	else:
		try:
			budget_name = ctx_name.get("name")
			set_summ(message.peer_id, message.text.replace(" ", ""), budget_name)
			show_update(message.peer_id, budget_name)
			
			await message.answer("Бюджет создан", keyboard = kb_budgets)
			await message.answer(news)
			
			await bot.state_dispenser.delete(message.peer_id)
			ctx_name.delete("name")
		except:
			await message.answer("Введите только число!")


# Состояние принта общих бюджетов
@bot.on.message(lev = "Общие бюджеты")
async def print_our_budgets(message: Message):
	global lev
	lev = "our"
	show_our_budgets()
	if budget_amount > 0:
		create_keyboard(budget_amount)
		await message.answer(budget_names, keyboard = dynamic_kb)
		await bot.state_dispenser.set(message.peer_id, ShowOurBudgets.get_budget_num)

	else:
		await message.answer(budget_names, keyboard = kb_cancel_create_budgets)


# Состояние получения номера общего бюджета
@bot.on.message(state = ShowOurBudgets.get_budget_num)
async def get_our_budget_num(message: Message):
	if message.text == "Назад":
		await bot.state_dispenser.delete(message.peer_id)
		
		try:
			ctx_name.delete("name")
		except KeyError:
			pass

		await message.answer("Главное меню", keyboard = kb_budgets)

	elif message.text == "Создать бюджет":
		await bot.state_dispenser.delete(message.peer_id)
		
		try:
			ctx_name.delete("name")
		except KeyError:
			pass

		await message.answer("Введите название бюджета", keyboard = kb_cancel)
		await bot.state_dispenser.set(message.peer_id, CreateOurBudgets.get_name)
	
	else:
		try:
			choose_our_budget()
			ctx_name.set("name", message.text)
			await message.answer(dict_names[int(message.text)], keyboard = kb_get_command)
			await bot.state_dispenser.set(message.peer_id, ShowOurBudgets.get_command)
		except:
			await message.answer("Бюджет не найден")


# Состояние получения команды
@bot.on.message(state = ShowOurBudgets.get_command)
async def get_our_command(message: Message):
	if message.text == "Назад":
		show_our_budgets()
		create_keyboard(budget_amount)
		await message.answer(budget_names, keyboard = dynamic_kb)
		await bot.state_dispenser.set(message.peer_id, ShowOurBudgets.get_budget_num)

	elif message.text == "Редактировать название":
		await message.answer("Введите новое название бюджета", keyboard = kb_back)
		await bot.state_dispenser.set(message.peer_id, ShowOurBudgets.change_name)

	elif message.text == "Ввод ➕":
		await message.answer("Сколько надо внести в бюджет?", keyboard = kb_back)
		await bot.state_dispenser.set(message.peer_id, ShowOurBudgets.change_summ_plus)

	elif message.text == "Вывод ➖":
		await message.answer("Сколько надо вывести с бюджета?", keyboard = kb_back)
		await bot.state_dispenser.set(message.peer_id, ShowOurBudgets.change_summ_minus)

	elif message.text == "Удалить бюджет":
		delete_our_budget()
		await message.answer("Общий бюджет удалён", keyboard = kb_budgets)
		await bot.state_dispenser.delete(message.peer_id)
		ctx_name.delete("name")

	else:
		await message.answer("Команда не найдена")


# Состояние изменения названия общего бюджета
@bot.on.message(state = ShowOurBudgets.change_name)
async def change_our_budget_name(message: Message):
	if message.text == "Назад":
		choose_our_budget()
		new_message = ctx_name.get("name")
		await message.answer(dict_names[int(new_message)], keyboard = kb_get_command)
		await bot.state_dispenser.set(message.peer_id, ShowOurBudgets.get_command)

	else:
		change_our_name(message.text)
		show_our_update(message.text)
		await message.answer("Общий бюджет обновлён", keyboard = kb_budgets)
		await message.answer(news)
		await bot.state_dispenser.delete(message.peer_id)
		ctx_name.delete("name")


# Состояние прибавления к сумме общего бюджета
@bot.on.message(state = ShowOurBudgets.change_summ_plus)
async def change_our_budget_summ(message: Message):
	if message.text == "Назад":
		choose_our_budget()
		new_message = ctx_name.get("name")
		await message.answer(dict_names[int(new_message)], keyboard = kb_get_command)
		await bot.state_dispenser.set(message.peer_id, ShowOurBudgets.get_command)

	else:
		try:
			name_id = ctx_name.get("name")
			budget_name = dict_name[int(name_id)]
			plus_our_summ(message.text.replace(" ", ""))
			show_our_update(budget_name)

			await message.answer("Общий бюджет обновлён", keyboard = kb_budgets)
			await message.answer(news)

			await bot.state_dispenser.delete(message.peer_id)
			ctx_name.delete("name")
		except:
			await message.answer("Введите только число!")


# Состояние убавления с суммы общего бюджета
@bot.on.message(state = ShowOurBudgets.change_summ_minus)
async def change_our_budget_minus(message: Message):
	if message.text == "Назад":
		choose_our_budget()
		new_message = ctx_name.get("name")
		await message.answer(dict_names[int(new_message)], keyboard = kb_get_command)
		await bot.state_dispenser.set(message.peer_id, ShowOurBudgets.get_command)

	else:
		try:
			name_id = ctx_name.get("name")
			budget_name = dict_name[int(name_id)]
			minus_our_summ(message.text.replace(" ", ""))
			show_our_update(budget_name)

			await message.answer("Общий бюджет обновлён", keyboard = kb_budgets)
			await message.answer(news)

			await bot.state_dispenser.delete(message.peer_id)
			ctx_name.delete("name")
		except:
			await message.answer("Введите только число!")


# Принятие названия общего бюджета
@bot.on.message(state = CreateOurBudgets.get_name)
async def get_our_budget_name(message: Message):
	if message.text == "Отмена":
		await bot.state_dispenser.delete(message.peer_id)
		
		try:
			ctx_name.delete("name")
		except KeyError:
			pass

		await message.answer("Главное меню", keyboard = kb_budgets)

	else:
		create_our_budget(message.text)
		if msg == "Введите сумму бюджета":
			await message.answer(msg, keyboard = kb_cancel_continue)
			ctx_name.set("name", message.text)
			await bot.state_dispenser.set(message.peer_id, CreateOurBudgets.get_summ)

		elif msg == "Такой бюджет уже имеется!":
			await message.answer(msg)


# Принятие суммы общего бюджета
@bot.on.message(state = CreateOurBudgets.get_summ)
async def get_our_budget_summ(message: Message):
	if message.text == "Отмена":
		budget_name = ctx_name.get("name")
		cancel_create_our_budget(budget_name)
		await message.answer("Создание общего бюджета отменено", keyboard = kb_budgets)

		await bot.state_dispenser.delete(message.peer_id)

		try:
			ctx_name.delete("name")
		except KeyError:
			pass

	elif message.text == "Пропустить":
		budget_name = ctx_name.get("name")
		show_our_update(budget_name)
		await message.answer("Общий бюджет создан", keyboard = kb_budgets)
		await message.answer(news)

		await bot.state_dispenser.delete(message.peer_id)
		ctx_name.delete("name")
	
	else:
		try:
			budget_name = ctx_name.get("name")
			set_our_summ(message.text.replace(" ", ""), budget_name)
			show_our_update(budget_name)
			
			await message.answer("Общий бюджет создан", keyboard = kb_budgets)
			await message.answer(news)
			
			await bot.state_dispenser.delete(message.peer_id)
			ctx_name.delete("name")
		except:
			await message.answer("Введите только число!")


# Создание состояния принятия названия для создания бюджета
@bot.on.message(lev = "Создать бюджет")
async def create_state(message: Message):
	await message.answer("Введите название бюджета", keyboard = kb_cancel)
	
	if lev == "my":
		await bot.state_dispenser.set(message.peer_id, CreateBudgets.get_name)
	elif lev == "our":
		await bot.state_dispenser.set(message.peer_id, CreateOurBudgets.get_name)


# Кнопка "Всего денег"
@bot.on.message(lev = "Всего денег")
async def total_money(message: Message):
	summ_all_budgets(message.peer_id)
	if all_summs < 0:
		await message.answer(f"–₽{'{0:,}'.format(all_summs).replace(',', ' ').replace('-', '')}")

	else:
		await message.answer(f"₽{'{0:,}'.format(all_summs).replace(',', ' ')}")


# Основной режим бота
@bot.on.message()
async def default(message: Message):
	if message.text.lower() == "reg":
		reg(message.peer_id)
		await message.answer("Вы зарегистрированы!", keyboard = kb_budgets)

	elif message.text == "Назад":
		await message.answer("Главное меню", keyboard = kb_budgets)

	else:
		await message.answer("Команда не найдена", keyboard = kb_budgets)


time_now = datetime.today()
print(f"\n[{str(time_now)[:19]}]: Бот успешно запущен")

bot.run_forever()
