import discord
from discord.ext import commands
from random import randint, choice
from Clases.Server import ServerConfig
import os

BOT_NAME = os.getenv('BOT', 'Oopa').lower()

class Emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.MAPA_REACOES = {
            ('dinhei', 'dinheiro', 'rico', 'grana', 'pagar'): ['💸','🤑','💵','💰','🪙'],
            ('bw', 'mine', 'mush', 'jogar', 'lol', 'cs', 'valorant'): ['⚒️','⛏️','🗿', '🎮', '🕹️'],
            ('comida', 'comer', 'fome', 'lanche', 'pizza'): ['🍔','🍕','🍟','🌭','🍿', '😋'],
            ('dormir', 'sono', 'cama', 'fui', 'noite'): ['💤', '😴', '🛌', '🌙'],
            ('pc', 'computador', 'programar', 'codigo', 'erro', 'bug'): ['💻', '⌨️', '🖱️', '⚙️', '🤖', '🐛'],
            ('musica', 'tocar', 'ensaio', 'banda', 'som'): ['🎷', '🎺', '🎶', '🎼', '🎸', '🎹'],
            ('treinar', 'academia', 'correr', 'calistenia', 'shape'): ['🦾', '🏋️', '🏃', '👟', '🥗', '🔥'],
            ('xadrez', 'xeque', 'jogar', 'estudar'): ['♟️', '🏰', '🐴', '👑', '🏁', '🧠'],
            ('lixo', 'ruim', 'bosta', 'noob', 'odeio'): ['💩', '🤡', '🗑️', '👎', '😡', '🤮'],
            ('top', 'massa', 'legal', 'boa', 'venci', 'ganhei'): ['🔥', '✨', '✅', '🤙', '💎', '🎉'],
            ('exercito', 'quartel', 'soldado', 'serviço', 'marcha', 'militar'): ['🪖', '🫡', '🎖️', '⛺', '💂'],
        }

    def deve_reagir(self, gatilhos, texto):
        if any(g in texto for g in gatilhos):
            return randint(1, 1) == 1 # Ajustei para 1 em 4 (25% de chance) para não poluir muito
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        # Filtros de segurança básicos
        if message.author.bot or not message.guild:
            return

        # (Aqui você mantém as suas verificações de ServerConfig/Ignore List)

        texto = message.content.lower()

        # O Loop deve ficar aqui, no corpo do on_message
        for gatilhos, emojis in self.MAPA_REACOES.items():
            if self.deve_reagir(gatilhos, texto): 
                emoji_escolhido = choice(emojis)
                try:
                    await message.add_reaction(emoji_escolhido)
                except discord.Forbidden:
                    print(f"⚠️ Sem permissão para reagir no canal {message.channel.name}")
                except discord.HTTPException as e:
                    print(f"❌ Erro ao reagir: {e}")
  

        # Reação Especial (Quando citam o nome dele)
        if BOT_NAME in texto:
            if randint(1, 2) == 1: # 50% de chance de mandar o óculos escuros
                await message.add_reaction('😎')

async def setup(bot):
    await bot.add_cog(Emoji(bot))