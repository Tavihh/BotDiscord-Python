import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
BOT = os.getenv('BOT', 'Oopa')
mydb = sqlite3.connect(f"{BOT}_bot.db")
mydb.row_factory = sqlite3.Row
mycursor = mydb.cursor()

class InviteConfig:
    def __init__(self, bot, server):
        self.bot = bot
        self.server = server

    def buscar_convite(self, user_id):
        """Retorna o código do convite se o usuário já tiver um."""
        sql = "SELECT invite_code FROM convites WHERE user_id = ?"
        mycursor.execute(sql, (str(user_id),))
        result = mycursor.fetchone()
        return result[0] if result else None

    def registrar_convite(self, user_id, code):
        """Salva um novo convite no banco."""
        sql = "INSERT INTO convites (user_id, invite_code, usos_atuais, meta_batida) VALUES (?, ?, 0, 0)"
        mycursor.execute(sql, (str(user_id), code))
        mydb.commit()

    def adicionar_uso(self, code):
        """Soma +1 ao contador do convite e retorna o total atual."""
        sql = "UPDATE convites SET usos_atuais = usos_atuais + 1 WHERE invite_code = ?"
        mycursor.execute(sql, (code,))
        mydb.commit()
        
        # Busca o novo total e o status da meta
        sql_check = "SELECT user_id, usos_atuais, meta_batida FROM convites WHERE invite_code = ?"
        mycursor.execute(sql_check, (code,))
        return mycursor.fetchone()

    def set_meta_batida(self, user_id):
        """Marca que o usuário já recebeu o cargo pela meta."""
        sql = "UPDATE convites SET meta_batida = 1 WHERE user_id = ?"
        mycursor.execute(sql, (str(user_id),))
        mydb.commit()

    def buscar_dono_do_convite(self, code):
        """Retorna os dados do dono do convite baseado no código."""
        sql = "SELECT user_id, usos_atuais, meta_batida FROM convites WHERE invite_code = ?"
        mycursor.execute(sql, (code,))
        return mycursor.fetchone()