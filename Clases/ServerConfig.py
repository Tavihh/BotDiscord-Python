import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
BOT = os.getenv('BOT')

# Conexão com banco de dados
mydb = sqlite3.connect(f"{BOT}_bot.db")
mydb.row_factory = sqlite3.Row
mycursor = mydb.cursor()

class ServerConfig:
    def __init__(self, bot, server):
        self.bot = bot
        self.server = server # Agora recebe o objeto Guild completo

    def _executar(self, sql, params=()):
        """Método auxiliar para evitar repetição de código"""
        mycursor.execute(sql, params)
        mydb.commit()

    def bot_off(self):
        sql = "INSERT INTO bot VALUES (?, ?, ?, ?, ?)"
        params = ('0', 'none', str(self.server.id), self.server.name, 'off')
        self._executar(sql, params)

    def bot_on(self):
        sql = "DELETE FROM bot WHERE server_id = ? AND status = 'off'"
        self._executar(sql, (str(self.server.id),))

    def servers_off(self):
        sql = "SELECT server_id FROM bot WHERE status = 'off'"
        mycursor.execute(sql)
        # Usando o nome da coluna para ser mais prático
        return [int(row['server_id']) for row in mycursor.fetchall()]

    def ignore_list(self):
        sql = "SELECT id FROM bot WHERE status = 'ignore' AND server_id = ?"
        mycursor.execute(sql, (str(self.server.id),))
        return [int(row['id']) for row in mycursor.fetchall()]

    def add_ignore(self, user):
        nome = user.global_name or user.name
        sql = "INSERT INTO bot VALUES (?, ?, ?, ?, ?)"
        params = (str(user.id), nome, str(self.server.id), self.server.name, 'ignore')
        self._executar(sql, params)

    def remove_ignore(self, user):
        sql = "DELETE FROM bot WHERE id = ? AND server_id = ? AND status = 'ignore'"
        self._executar(sql, (str(user.id), str(self.server.id)))

    def adm_list(self):
        sql = "SELECT id FROM bot WHERE status = 'adm' AND server_id = ?"
        mycursor.execute(sql, (str(self.server.id),))
        return [int(row['id']) for row in mycursor.fetchall()]

    def add_adm(self, user):
        nome = user.global_name or user.name
        sql = "INSERT INTO bot VALUES (?, ?, ?, ?, ?)"
        params = (str(user.id), nome, str(self.server.id), self.server.name, 'adm')
        self._executar(sql, params)

    def remove_adm(self, user):
        sql = "DELETE FROM bot WHERE id = ? AND server_id = ? AND status = 'adm'"
        self._executar(sql, (str(user.id), str(self.server.id)))