import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()
BOT = os.getenv('BOT')
#Coneção com banco de dados
mydb = sqlite3.connect(f"{BOT}_bot.db")
mydb.row_factory = sqlite3.Row
mycursor = mydb.cursor()

class ServerConfig:
        def __init__(self,bot,server):
            self.bot = bot
            self.server = server
        def bot_off(self):
            sql = f"insert into bot values ('0','none','{self.server.id}','{self.server.name}','off')"
            mycursor.execute(sql)
            mydb.commit()
        def bot_on(self):
            sql = f"delete from bot where server_id ='{self.server.id}' and status ='off'"
            mycursor.execute(sql)
            mydb.commit()
        def servers_off(self):
            sql = f"select server_name , server_id from bot where status = 'off' "
            mycursor.execute(sql)
            myresult = mycursor.fetchall()  
            server_list = []
            for x in myresult:
                server_list.append(int(x[1]))
            return server_list
        def ignore_list(self):
            sql = f"select id ,server_id from bot where status ='ignore' and server_id ='{self.server.id}'"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            adm_list = []
            for x in myresult:
                adm_list.append(int(x[0]))
            return adm_list     
        def add_ignore(self,user):
            sql = f"insert into bot values ('{user.id}','{user.global_name}','{self.server.id}','{self.server.name}','ignore')"
            mycursor.execute(sql)
            mydb.commit()
        def remove_ignore(self,user):
            sql = f"delete from bot where id ='{user.id}' and server_id ='{self.server.id}' and status ='ignore'"
            mycursor.execute(sql)
            mydb.commit()
        def adm_list(self):
            sql = f"select id ,server_id from bot where status ='adm' and server_id ='{self.server.id}'"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            adm_list = []
            for x in myresult:
                adm_list.append(int(x[0]))
            return adm_list 
        def add_adm(self,user):
            sql = f"insert into bot values ('{user.id}','{user.global_name}','{self.server.id}','{self.server.name}','adm')"
            mycursor.execute(sql)
            mydb.commit()
        def remove_adm(self,user):
            sql = f"delete from bot where id ='{user.id}' and server_id ='{self.server.id}' and status ='adm'"
            mycursor.execute(sql)
            mydb.commit()
    