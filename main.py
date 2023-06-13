
from fastapi import FastAPI
from starlette.responses import JSONResponse
from fuzzywuzzy import fuzz
import sqlite3 as sq
import datetime

app = FastAPI()



global base, cur
base = sq.connect('main.db')
cur = base.cursor()
if base:
    print('Data base connected OK!')
base.execute(
        'CREATE TABLE IF NOT EXISTS users(id INTEGER,id_user INTEGER,state INTEGER,PRIMARY KEY("id" AUTOINCREMENT))')
base.commit()
base.execute(
        'CREATE TABLE IF NOT EXISTS history(id INTEGER,datatime TEXT,user INTEGER,user_message TEXT,bot_message TEXT,PRIMARY KEY("id" AUTOINCREMENT))')
base.commit()
base.execute(
        'CREATE TABLE IF NOT EXISTS statisticks(id INTEGER,kol_mess INTEGER NOT NULL,kol_users INTEGER NOT NULL,PRIMARY KEY("id" AUTOINCREMENT))')
base.commit()




answer_yes = ['да','конечно','ага','пожалуй']
answer_no = ['нет','нет,конечно','ноуп','найн']

#функция продвинутого сравнения

async def insert_history(id,user_message,bot_message):
    cur.execute(f"INSERT INTO history(datatime,user,user_message,bot_message) VALUES(?,?,?,?)", (datetime.datetime.utcnow(),id,user_message,bot_message))
    base.commit()

async def update_stat_kol_user():
    cur.execute(f"UPDATE statisticks SET kol_users = kol_users + 1")
    base.commit()
async def update_stat_kol_mess():
    cur.execute(f"UPDATE statisticks SET kol_mess = kol_mess + 1")
    base.commit()


async def similarity(message):
    procent = 80
    yes_procent = []
    no_procent = []
    for yes in answer_yes:
        matcher = fuzz.WRatio(message, yes)
        if matcher >= procent:
            yes_procent.append(matcher)
    for no in answer_no:
        matcher = fuzz.WRatio(message, no)
        if matcher >= procent:
            no_procent.append(matcher)
    if len(yes_procent) == 0 and len(no_procent) == 0:
        return "hz"
    elif len(yes_procent) == 0 or len(no_procent) == 0:
        if len(yes_procent) == 0:
            return "no"
        if len(no_procent) == 0:
            return "yes"
    if len(yes_procent) != 0 and len(no_procent) != 0:
        max_yes = 0
        max_no = 0
        if max_yes > max_no:
            return "yes"
        if max_yes < max_no:
            return "no"
        if max_yes == max_no:
            return "hz"
#функция ответов на состоянии старта
async def state0_bot(id : int, message : str):
    if message == "/start":
        id_user = cur.execute(f"SELECT id_user FROM users WHERE id_user = ?",(id,)).fetchone()
        if id_user == None:
            cur.execute(f"INSERT INTO users(id_user,state) VALUES (?,?)",(id,1))
            base.commit()
            return {"BOT": "Привет! Я могу отличить кота от хлеба! Объект перед тобой квадратный?"}
        else:
            cur.execute(f"UPDATE users SET state = 1 WHERE id_user = ?", (id,))
            base.commit()
            return {"BOT": "Привет! Я могу отличить кота от хлеба! Объект перед тобой квадратный?"}
    else:
        return {"BOT": "Сначала меня надо заупустить!Попробуй передать в message - /start"}

#функция ответов на состоянии 1
async def state1_bot(id : int, message : str):

    if message == "/start":
        (id_user,) = cur.execute(f"SELECT id_user FROM users WHERE id_user = ?", (id,)).fetchone()
        cur.execute(f"UPDATE users SET state = 1 WHERE id_user = ?", (id_user,))
        base.commit()
        return {"BOT": "Привет! Я могу отличить кота от хлеба! Объект перед тобой квадратный?"}
    else:
        msg = message.lower()
        res = await similarity(msg)
        if res == "hz":
            return {"BOT": "Я не распознал твой ответ"}
        if res == "yes":
            cur.execute(f"UPDATE users SET state = 2 WHERE id_user = ?", (id,))
            base.commit()
            return {"BOT": "У него есть уши?"}
        if res == "no":
            cur.execute(f"UPDATE users SET state = 1 WHERE id_user = ?", (id,))
            base.commit()
            return {"BOT": "Это кот, а не хлеб! Не ешь его!"}

#функция ответов на состоянии 2
async def state2_bot(id : int, message : str):
    if message == "/start":
        (id_user,) = cur.execute(f"SELECT id_user FROM users WHERE id_user = ?", (id,)).fetchone()
        cur.execute(f"UPDATE users SET state = 1 WHERE id_user = ?", (id_user,))
        base.commit()
        return {"BOT": "Привет! Я могу отличить кота от хлеба! Объект перед тобой квадратный?"}
    else:
        msg = message.lower()
        res = await similarity(msg)
        if res == "hz":
            return {"BOT": "Я не распознал твой ответ"}
        if res == "yes":
            cur.execute(f"UPDATE users SET state = 1 WHERE id_user = ?", (id,))
            base.commit()
            return {"BOT": "Это кот, а не хлеб! Не ешь его!"}
        if res == "no":
            cur.execute(f"UPDATE users SET state = 1 WHERE id_user = ?", (id,))
            base.commit()
            return {"BOT": "Это хлеб, а не кот! Ешь его!"}



@app.get("/bot")
async def start_bot(id : int, message : str):
    id_user = cur.execute(f"SELECT id_user FROM users WHERE id_user = ?", (id,)).fetchone()
    if id_user == None:
        res = await state0_bot(id,message)
        await insert_history(id, message, res['BOT'])
        await update_stat_kol_user()
        await update_stat_kol_mess()
        return res
    else:
        (state_user,) = cur.execute(f"SELECT state FROM users WHERE id_user = ?", (id,)).fetchone()
        if state_user == 1:
            res = await state1_bot(id,message)
            await insert_history(id,message, res['BOT'])
            await update_stat_kol_mess()
            return res
        if state_user == 2:
            res = await state2_bot(id, message)
            await insert_history(id, message, res['BOT'])
            await update_stat_kol_mess()
            return res






