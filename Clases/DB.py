import sqlite3
import datetime
import os
from dotenv import load_dotenv
load_dotenv()
BOT = os.getenv('BOT')
DB_PATH = f"{BOT}_bot.db"

def iniciar_banco():
    # 1. Conecta (Cria o arquivo se não existir)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 2. Tabela Banco (Usamos tipos numéricos para saldo em vez de TEXT)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS banco (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        id_user TEXT NOT NULL UNIQUE,
        saldo_user INTEGER NOT NULL DEFAULT 0,
        saldo_banco INTEGER NOT NULL DEFAULT 0,
        dia_trabalhado TEXT NOT NULL DEFAULT '00/00',
        salario3x INTEGER NOT NULL DEFAULT 0,
        pocao_sorte INTEGER NOT NULL DEFAULT 0
    )
    ''')

    # 3. Tabela Bot
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bot (
        id TEXT PRIMARY KEY,
        nome TEXT,
        server_id TEXT,
        server_name TEXT,
        status TEXT
    )
    ''')

    # 4. Tabela de Convites (Invite Tracker)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS convites (
        user_id TEXT PRIMARY KEY,
        invite_code TEXT UNIQUE,
        usos_atuais INTEGER DEFAULT 0,
        meta_batida INTEGER DEFAULT 0
    )
    ''')

    conn.commit()

    conn.commit()
    conn.close()
    print("✅ Banco de dados pronto para o combate!")

iniciar_banco()

mydb = sqlite3.connect(DB_PATH)
mydb.row_factory = sqlite3.Row
mycursor = mydb.cursor()