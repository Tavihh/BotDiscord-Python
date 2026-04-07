import discord
from discord import app_commands
from discord.ext import commands
from random import randint, choice
from yt_dlp import YoutubeDL
from Clases.ServerConfig import ServerConfig

import os
from dotenv import load_dotenv
load_dotenv()

BOT = os.getenv('BOT')

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Testa a latência do bot")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 Pong! Latência: {round(self.bot.latency * 1000)}ms")

    @app_commands.command(name =f'{BOT}',description=f'Teste se o {BOT.title()} está On')
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Hey {interaction.user.mention}, Estou Funcionando!',delete_after=15)
        
    @app_commands.command(name='fale', description='Falarei oque você quiser no chat')
    @app_commands.describe(oque_dizer = 'Oque eu deveria dizer?')
    async def dig(self, interaction: discord.Interaction,oque_dizer:str):
        #Codigo falando oque o User disse
        await interaction.response.send_message('Mensagem Enviada!',ephemeral=True)
        await interaction.channel.send(f'{oque_dizer}')
        await interaction.delete_original_response()

    @app_commands.command(name='link', description='Entre na minha comunidade do discord!')
    async def link(self, interaction: discord.Interaction):
        channel = await interaction.user.create_dm()
        link_server = os.getenv('LINK_SERVER')
        await channel.send(f'Entre no meu server: {link_server}')
        await interaction.response.send_message('Dm enviada!',delete_after=15)

    @app_commands.command(name='abrace', description='Abraçe algúem')
    @app_commands.describe(quem = 'Quem você quer abraçar??')
    async def abrace(self, interaction: discord.Interaction, quem:discord.Member):
        #Verificando se o bot ta on
        sv = ServerConfig(self.bot, interaction.guild_id)
        if interaction.guild.id in sv.servers_off():
            await interaction.response.send_message('To Off',delete_after=20)
            return
        #Verificando se o usuario deve ser ignorado
        if interaction.user.id in sv.ignore_list():
            await interaction.response.send_message('Você está na minha Ignore List, não posso te responder aqui',delete_after=10)
            return
        #Verificando se é um bot
        if quem.bot == True:
            await interaction.response.send_message('Isso é um Bot',delete_after=10)
            return
        # Pegando o arquivo de midia
        with open(f'midia/abraco-{randint(1,3)}.gif', 'rb') as gif_arquivo:
            gif = discord.File(gif_arquivo)
        async def retribuir_abraco(interact:discord.Interaction):
            if interact.user.id != quem.id:
                await interact.response.send_message('Eii, isso não é para você!',ephemeral=True,delete_after=5)
            else:
                with open(f'midia/abraco-{randint(1,3)}.gif', 'rb') as gif_arquivo:
                    gif = discord.File(gif_arquivo)
                await interact.response.send_message(f'<@{quem.id}> abraçou {interaction.user.mention} Devolta',file=gif,delete_after=18)
        view = discord.ui.View()
        botao_revanche = discord.ui.Button(label='Retribuir',style=discord.ButtonStyle.red)
        view.add_item(botao_revanche)
        botao_revanche.callback = retribuir_abraco
        # await interaction.channel.send(view=view,delete_after=18)
        await interaction.response.send_message(f'{interaction.user.mention} abraçou {quem.mention}',file=gif,view=view,delete_after=18)
    
    @app_commands.command(name='pvp', description='Faça um PVP com alguém')
    @app_commands.describe(quem = 'Contra quem você quer lutar?')
    async def pvp(self, interaction: discord.Interaction, quem:discord.Member):
        #Verificando se o bot ta on
        sv = ServerConfig(self.bot,interaction.guild)
        if interaction.guild.id in sv.servers_off():
            await interaction.response.send_message('To Off',delete_after=20)
            return
        #Verificando se o usuario deve ser ignorado
        if interaction.user.id in sv.ignore_list():
            await interaction.response.send_message('Você está na minha Ignore List, não posso te responder aqui',delete_after=10)
            return
        #Verificando se é um bot
        if quem.bot == True:
            await interaction.response.send_message('Isso é um Bot',delete_after=10)
            return
        # Pegando o arquivo de midia
        with open(f'midia/luta-{randint(1,7)}.gif', 'rb') as gif_arquivo:
            gif = discord.File(gif_arquivo)
        async def revanche_desafiado(interact:discord.Interaction):
            if interact.user.id != quem.id:
                await interact.response.send_message('Eii, isso não é para você!',ephemeral=True,delete_after=5)
            else:
                with open(f'midia/luta-{randint(1,7)}.gif', 'rb') as gif_arquivo:
                    gif = discord.File(gif_arquivo)
                await interact.response.send_message(f'{interaction.user.mention} VS <@{quem.id}>',file=gif,delete_after=18)
                #Sorteia o Ganhador
                jogadores =[interaction.user,quem]
                ganhador = choice(jogadores)
                await interact.channel.send(f'{ganhador.mention} Ganhou!',delete_after=18)
        async def revanche_desafiante(interact:discord.Interaction):
            if interact.user.id != interaction.user.id:
                await interact.response.send_message('Eii, isso não é para você!',ephemeral=True,delete_after=5)
            else:
                with open(f'midia/luta-{randint(1,7)}.gif', 'rb') as gif_arquivo:
                    gif = discord.File(gif_arquivo)
                await interact.response.send_message(f'{interaction.user.mention} VS <@{quem.id}>',file=gif,delete_after=18)
                #Sorteia o Ganhador
                jogadores =[interaction.user,quem]
                ganhador = choice(jogadores)
                await interact.channel.send(f'{ganhador.mention} Ganhou!',delete_after=18)
    
        await interaction.response.send_message(f'{interaction.user.mention} VS {quem.mention}',file=gif,delete_after=18)
        view = discord.ui.View()
        botao_revanche = discord.ui.Button(label='Revanche',style=discord.ButtonStyle.red)
        view.add_item(botao_revanche)
        jogadores =[interaction.user,quem]
        ganhador = choice(jogadores)
        if ganhador == interaction.user:
            botao_revanche.callback = revanche_desafiado
        else:
            botao_revanche.callback = revanche_desafiante
        await interaction.channel.send(f'{ganhador.mention} Ganhou!!',view=view,delete_after=18)

    @app_commands.command(name='beijar', description='Beije algúem')
    @app_commands.describe(quem = 'Quem você quer beijar??')
    async def beijar(self, interaction: discord.Interaction, quem:discord.Member):
        #Verificando se o bot ta on
        sv = ServerConfig(self.bot,interaction.guild)
        if interaction.guild.id in sv.servers_off():
            await interaction.response.send_message('To Off',delete_after=20)
            return
        #Verificando se o usuario deve ser ignorado
        if interaction.user.id in sv.ignore_list():
            await interaction.response.send_message('Você está na minha Ignore List, não posso te responder aqui',delete_after=10)
            return
        #Verificando se é um bot
        if quem.bot == True:
            await interaction.response.send_message('Isso é um Bot',delete_after=10)
            return
        # Pegando o arquivo de midia
        with open(f'midia/beijo{randint(1,3)}.gif', 'rb') as gif_arquivo:
            gif = discord.File(gif_arquivo)
        async def retribuir_beijo(interact:discord.Interaction):
            if interact.user.id != quem.id:
                await interact.response.send_message('Eii, isso não é para você!',ephemeral=True,delete_after=5)
            else:
                with open(f'midia/beijo{randint(1,3)}.gif', 'rb') as gif_arquivo:
                    gif = discord.File(gif_arquivo)
                await interact.response.send_message(f'<@{quem.id}> Beijou {interaction.user.mention} Devolta',file=gif,delete_after=18)
        view = discord.ui.View()
        botao_revanche = discord.ui.Button(label='Retribuir',style=discord.ButtonStyle.red)
        view.add_item(botao_revanche)
        botao_revanche.callback = retribuir_beijo
        # await interaction.channel.send(view=view,delete_after=18)
        await interaction.response.send_message(f'{interaction.user.mention} Beijou {quem.mention}',file=gif,view=view,delete_after=18)

    @app_commands.command(name='avatar', description='Pega o avatar de um membro')
    @app_commands.describe(quem = 'O Avatar de quem que você quer pegar?')
    async def avatar(self, interaction:discord.Interaction,quem:discord.Member):
        #Verificando se o bot ta on
        sv = ServerConfig(self.bot,interaction.guild)
        if interaction.guild.id in sv.servers_off():
            await interaction.response.send_message('To Off',delete_after=20)
            return
        #Verificando se o usuario deve ser ignorado
        if interaction.user.id in sv.ignore_list():
            await interaction.response.send_message('Você está na minha Ignore List, não posso te responder aqui',delete_after=10)
            return

        #Cria o embed e envia
        await interaction.response.send_message(f'Aqui está o avatar de {quem.mention}',delete_after=40)
        embed = discord.Embed(title=f'{quem.global_name}', color=0xFF00FF)
        embed.set_image(url= quem.display_avatar.url)
        await interaction.channel.send(embed=embed,delete_after=40)

    @app_commands.command(name='video-link', description='Baixa um video do youtube e manda aqui')
    @app_commands.describe(link='Cole o Link de um Video do Youtube')
    async def youtube_video(self, interaction: discord.Interaction, link: str):
        # 1. Verificando configurações do servidor
        sv = ServerConfig(self.bot,interaction.guild)
        if interaction.guild.id in sv.servers_off():
            await interaction.response.send_message('To Off', delete_after=20)
            return

        if interaction.user.id in sv.ignore_list():
            await interaction.response.send_message('Você está na minha Ignore List', delete_after=10)
            return

        # 2. DEFER: Essencial para comandos demorados
        await interaction.response.defer(thinking=True)

        folder = "midia/downloads"
        if not os.path.exists(folder):
            os.makedirs(folder)

        ydl_opts = {
            'format': 'best[ext=mp4][filesize<25M]/best',
            'outtmpl': f'{folder}/%(title).50s.%(ext)s',
            'restrictfilenames': True,
            'quiet': True,           # Silencia o console
            'no_warnings': True,        # Silencia avisos
            'noprogress': True,      # Remove barra de progresso no CMD
            'socket_timeout': 30,
            'retries': 5,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)

                if info.get('duration', 0) > 360:
                    await interaction.followup.send("❌ Vídeo muito longo (máximo 6 min).")
                    return

                # Download real
                info_final = ydl.extract_info(link, download=True)
                file_path = ydl.prepare_filename(info_final)

            # 3. Enviar o arquivo
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    # Usamos followup porque já demos o defer no início
                    await interaction.followup.send(content=f"✅ **{info.get('title')}**", file=discord.File(f))

                os.remove(file_path)
            else:
                await interaction.followup.send("❌ Erro ao localizar o arquivo baixado.")

        except Exception as e:
            print(f"ERRO: {e}")
            await interaction.followup.send(f"💥 Ocorreu um erro ao processar o vídeo.")

    @app_commands.command(name='gay', description='Veja o quanto um membro é Gay')
    async def gay(self, interaction:discord.Interaction, quem:discord.Member):
    
        #Verificando se o bot ta on
        sv = ServerConfig(self.bot,interaction.guild)
        if interaction.guild.id in sv.servers_off():
            await interaction.response.send_message('To Off',delete_after=20)
            return
        #Verificando se o usuario deve ser ignorado
        if interaction.user.id in sv.ignore_list():
            await interaction.response.send_message('Você está na minha Ignore List, não posso te responder aqui',delete_after=10)
            return
        #Verificando se é um bot
        if quem.bot == True:
            await interaction.response.send_message('Isso é um Bot',delete_after=10)
            return
        #Verificando se marcou o trevor e enviado o embed
        p = randint(0,100)
        if quem.id == int(os.getenv('DONO')):
            p = 0
        embed = discord.Embed(title=f'O {quem.global_name} é {p}% gay segundo meus cálculos! 🏳️‍🌈', color=0xFF00FF)
        embed.add_field(name='',value=f'📌 use /gay para saber o quanto é o nível gay de uma pessoa! BY:KING', inline=False)
        await interaction.response.send_message(embed=embed,delete_after=40)
        return
        

async def setup(bot):
    await bot.add_cog(Commands(bot))