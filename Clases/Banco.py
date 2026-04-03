import sqlite3
import datetime
import os
from dotenv import load_dotenv
load_dotenv()
BOT = os.getenv('BOT')
#Coneção com banco de dados
mydb = sqlite3.connect(f"{BOT}_bot.db")
mydb.row_factory = sqlite3.Row
mycursor = mydb.cursor()

# Dica: Mantenha a conexão dentro da classe ou passe como argumento para evitar locks
class Banco:
    def __init__(self, bot, user):
        self.bot = bot
        self.user = user
        
        self.abrir_conta()

        # 2. Busca segura usando '?' para evitar SQL Injection
        sql = "SELECT nome, saldo_user, saldo_banco, dia_trabalhado, salario3x, pocao_sorte FROM banco WHERE id_user = ?"
        mycursor.execute(sql, (str(self.user.id),)) # Sempre passe como tupla
        x = mycursor.fetchone() # fetchone() é mais rápido que fetchall() para um usuário só

        if x:
            self.nome = x[0]
            self.saldo_user = int(x[1])
            self.saldo_banco = int(x[2])
            self.dia_trabalhado = x[3]
            self.salario3x = int(x[4])
            self.pocao_sorte = int(x[5])

    def abrir_conta(self):
        # 3. 'OR IGNORE' impede que o bot crashe se a conta já existir
        sql = "INSERT OR IGNORE INTO banco (nome, id_user) VALUES (?, ?)"
        mycursor.execute(sql, (self.user.display_name, str(self.user.id)))
        mydb.commit()

    def trocar_saldo_user(self, novo_saldo: int):
        sql = "UPDATE banco SET saldo_user = ? WHERE id_user = ?"
        mycursor.execute(sql, (novo_saldo, str(self.user.id)))
        mydb.commit()

    def trocar_saldo_banco(self, novo_saldo: int):
        sql = "UPDATE banco SET saldo_banco = ? WHERE id_user = ?"
        mycursor.execute(sql, (novo_saldo, str(self.user.id)))
        mydb.commit()

    def trabalhou(self):
        agora = datetime.datetime.now()
        data_str = f"{agora.day}/{agora.month}"
        sql = "UPDATE banco SET dia_trabalhado = ? WHERE id_user = ?"
        mycursor.execute(sql, (data_str, str(self.user.id)))
        mydb.commit()
            
    def trocar_itens(self, item: str, nova_quantidade: int):
        # Atenção: nomes de colunas não aceitam '?', então validamos antes
        colunas_validas = ['salario3x', 'pocao_sorte']
        if item in colunas_validas:
            sql = f"UPDATE banco SET {item} = ? WHERE id_user = ?"
            mycursor.execute(sql, (nova_quantidade, str(self.user.id)))
            mydb.commit()

    def membros_saldo(self, guild):
            # 1. Buscamos ID, Nome e Saldo (Ordenado do maior para o menor)
            sql = "SELECT id_user, nome, saldo_banco FROM banco ORDER BY saldo_banco DESC"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()

            ranking_local = []
            for x in myresult:
                user_id = int(x[0]) # ID do usuário no banco
                nome_user = x[1]    # Nome salvo no banco
                saldo = int(x[2])   # Saldo do banco

                if guild.get_member(int(user_id)):
                    ranking_local.append((user_id, nome_user, saldo))

                # 3. PRAGMATISMO: Se já achamos os 10 primeiros do server, paramos de procurar
                if len(ranking_local) >= 10:
                    break
                    
            return ranking_local
            