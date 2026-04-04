import discord
from discord import app_commands
from discord.ext import commands
from time import sleep
import os
from dotenv import load_dotenv
from Clases.DB import iniciar_banco

load_dotenv()

TOKEN = os.getenv('TOKEN')
BOT = os.getenv('BOT')


class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True  # <--- ESSA LINHA É O COLÍRIO DO BOT
        intents.message_content = True  # <--- ESSA LINHA É O SEGREDO
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Percorre os arquivos na pasta 'cogs'
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✅ Sucesso ao carregar: {filename}')
                except Exception as e:
                    print(f'❌ Erro ao carregar {filename}: {e}')
        await self.tree.sync()
        total_comandos = len(self.tree.get_commands())
        iniciar_banco()
        print(f"{total_comandos} Comandos sincronizados para {self.user}")

bot = MyBot()
bot.run(TOKEN)