import discord
from discord import app_commands
from discord.ext import commands
from random import choice, randint
import datetime
from Clases.BancoConfig import BancoConfig
from Clases.ServerConfig import ServerConfig
from Clases.Loja import LojaView

import os
from dotenv import load_dotenv
load_dotenv()

BOT = os.getenv('BOT')

class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='banco-saldo', description=f'Veja tudo que você ou outra pessoa tem no {BOT.title()} Bank')
    @app_commands.describe(quem = 'De quem você ver os Dados?')
    async def banco_saldo(self, interaction:discord.Interaction,quem:discord.Member):
        #Verificando se o bot ta on
        sv = ServerConfig(self.bot,interaction.guild)
        if interaction.guild.id in sv.servers_off():
            await interaction.response.send_message('To Off',delete_after=20)
            return
        #Verificando se o usuario deve ser ignorado
        if interaction.user.id in sv.ignore_list():
            await interaction.response.send_message('Você está na minha Ignore List, não posso te responder aqui',delete_after=10)
            return
        #Verificando se não é um bot
        if quem.bot == True:
            await interaction.response.send_message('Isso é um Bot',ephemeral=True,delete_after=10)
            return

        user = BancoConfig(self.bot, quem)
        try:
            #Cria o Embed e Envia
            embed = discord.Embed(title=f"{BOT.title()} Bank", color=0x00ff00)
            embed.add_field(name="Usuario",value=f"{quem.mention}", inline=False)
            embed.add_field(name="Saldo Banco", value=f"{user.saldo_banco} {BOT}s", inline=False)
            embed.add_field(name="Saldo em Mãos", value=f"{user.saldo_user} {BOT}s", inline=False)
            embed.add_field(name='Ultimo dia Trabalhado', value=f'{user.dia_trabalhado}',inline=False)
            embed.add_field(name='Salario3x',value=f'{user.salario3x}',inline=False)
            embed.add_field(name='Pocao da Sorte',value=f'{user.pocao_sorte}',inline=False)
            embed.set_thumbnail(url= quem.display_avatar.url)
            await interaction.response.send_message(embed=embed,delete_after=30)
        except:
            user.abrir_conta()
            user = BancoConfig(self.bot, quem.id)
            #Cria o Embed e Envia
            embed = discord.Embed(title=f"{BOT.title()} Bank", color=0x00ff00)
            embed.add_field(name="Usuario",value=f"{quem.mention}", inline=False)
            embed.add_field(name="Saldo-Banco", value=f"{user.saldo_banco} {BOT}s", inline=False)
            embed.add_field(name="Saldo", value=f"{user.saldo_user} {BOT}s", inline=False)
            embed.add_field(name='Ultimo dia Trabalhado', value=f'{user.dia_trabalhado}',inline=False)
            embed.add_field(name='Salario3x',value=f'{user.salario3x}',inline=False)
            embed.add_field(name='Pocao da Sorte',value=f'{user.pocao_sorte}',inline=False)
            embed.set_thumbnail(url= quem.display_avatar.url)
            await interaction.response.send_message(embed=embed,delete_after=30)

    @app_commands.command(name='banco-transferir', description='Transfira moedas para alguém')
    async def realizar_transferencia(self, interaction: discord.Interaction, quem: discord.Member, valor: int):
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
        # Verificando se é um valor válido
        if valor <= 0:
            return await interaction.response.send_message('Valor inválido.', ephemeral=True)

        user = BancoConfig(self.bot, interaction.user)
        alvo = BancoConfig(self.bot, quem) # Passando o objeto QUEM

        if user.saldo_banco < valor:
            return await interaction.response.send_message('Você não tem saldo no banco para essa transferência.', ephemeral=True)

        # Se o alvo não tiver conta, abrimos na hora
        if alvo.saldo_banco == 0:
            alvo.abrir_conta()

        user.trocar_saldo_banco(user.saldo_banco - valor)
        alvo.trocar_saldo_banco(alvo.saldo_banco + valor)
        
        await interaction.response.send_message(f'✅ Transferência de {valor} {BOT}s enviada para {quem.mention}!')
    
    @app_commands.command(name='banco-depositar', description=f'Deposite seus {BOT}s')
    @app_commands.describe(quantia='Quanto quer guardar?')
    async def realizar_deposito(self, interaction: discord.Interaction, quantia: int): # Nome único!
        sv = ServerConfig(self.bot, interaction.guild) # Verifique se sua classe aceita o objeto guild
        
        if interaction.guild.id in sv.servers_off() or interaction.user.id in sv.ignore_list():
            return await interaction.response.send_message('Bot desativado ou você está na Ignore List.', ephemeral=True)

        if quantia <= 0:
            return await interaction.response.send_message('Não é possível depositar valores negativos ou zero.', ephemeral=True)

        user = BancoConfig(self.bot, interaction.user) # Passando o objeto USER

        # Se o saldo for 0 (usuário novo), tentamos abrir a conta automaticamente
        if user.saldo_user == 0 and quantia > 0:
             user.abrir_conta()

        if quantia > user.saldo_user:
            quantia = user.saldo_user
            user.trocar_saldo_user(user.saldo_user - quantia)
            user.trocar_saldo_banco(user.saldo_banco + quantia)
            await interaction.response.send_message(f'Depósito de todos os {quantia} {BOT}s realizado com sucesso!.', ephemeral=True)
            return

        user.trocar_saldo_user(user.saldo_user - quantia)
        user.trocar_saldo_banco(user.saldo_banco + quantia)
        await interaction.response.send_message(f'💰 Depósito de {quantia} {BOT}s realizado com sucesso!')

    @app_commands.command(name='banco-sacar', description=f'Saque seus {BOT}s')
    @app_commands.describe(quantia='Quanto quer tirar?')
    async def realizar_saque(self, interaction: discord.Interaction, quantia: int): # Nome único!
        sv = ServerConfig(self.bot, interaction.guild)
        
        if quantia <= 0:
            return await interaction.response.send_message('Valor de saque inválido.', ephemeral=True)

        user = BancoConfig(self.bot, interaction.user)

        if quantia > user.saldo_banco:
            await interaction.response.send_message(f'Sacando todos os {user.saldo_banco} disponíveis.', ephemeral=True)
            quantia = user.saldo_banco
            user.trocar_saldo_banco(user.saldo_banco - quantia)
            user.trocar_saldo_user(user.saldo_user + quantia)
            return

        user.trocar_saldo_banco(user.saldo_banco - quantia)
        user.trocar_saldo_user(user.saldo_user + quantia)
        await interaction.response.send_message(f'💸 Saque de {quantia} {BOT}s realizado!')

    @app_commands.command(name='banco-trabalhar', description=f'Trabalhe por {BOT}s')
    async def trabalhar(self, interaction: discord.Interaction):
        #Verificando se o bot ta on
        sv = ServerConfig(self.bot,interaction.guild)
        if interaction.guild.id in sv.servers_off():
            await interaction.response.send_message('To Off',delete_after=20)
            return
        #Verificando se o usuario deve ser ignorado
        if interaction.user.id in sv.ignore_list():
            await interaction.response.send_message('Você está na minha Ignore List, não posso te responder aqui',delete_after=10)
            return

        dia = datetime.datetime.today().day
        mes = datetime.datetime.today().month
        #Escolhendo a profissão e executando o programa
        profissao =['garcom','prefeito','mineiro','entregador','presidente','lixeiro','chefe de cozinha','Chapeleiro','Policial','Traficante','Segurança','Motorista de Onibus','Piloto de avião','Navegante de Barcos','Cantor']
        salario = randint(1,300)+300
        user = BancoConfig(self.bot, interaction.user)
        try:
            #Verificando se já trabalhou hoje
            if user.dia_trabalhado == f'{dia}/{mes}':
                await interaction.response.send_message('você ja trabalhou hoje, Volte amanhã!',delete_after=15)
                return
            #Verificando se tem o item salario3x
            if user.salario3x >=1:
                user.trocar_itens('salario3x',user.salario3x - 1)
                await interaction.channel.send('Usado Salario 3X, seu salário foi multiplicado por 3!',delete_after=15)
                salario = salario*3
            #Depositando o salario
            user.trocar_saldo_user(int(salario + user.saldo_user))
            await interaction.response.send_message(f'você trabalhou como {choice(profissao)} e recebeu {salario} {BOT}s', delete_after=15)
            #Cria o Embed e Envia
            user.trabalhou()
        except:
            user.abrir_conta()
            user = BancoConfig(self.bot, interaction.user.id)
            #Verificando se já trabalhou hoje
            if user.dia_trabalhado == f'{dia}/{mes}':
                await interaction.response.send_message('você ja trabalhou hoje, Volte amanhã!',delete_after=15)
                return
            #Verificando se tem o item salario3x
            if user.salario3x >=1:
                user.trocar_itens('salario3x',user.salario3x - 1)
                await interaction.channel.send('Usado Salario 3X, seu salário foi multiplicado por 3!',delete_after=15)
                salario = salario*3
            #Depositando o salario
            user.trocar_saldo_user(salario + user.saldo_user)
            await interaction.response.send_message(f'você trabalhou como {choice(profissao)} e recebeu {salario} {BOT}s', delete_after=15)
            #Cria o Embed e Envia
            user.trabalhou()

    @app_commands.command(name='banco-roubar', description=f'Tente roubar {BOT}s de alguém')
    @app_commands.describe(quem=f'Quem você quer tentar roubar?')
    async def roubar(self, interaction: discord.Interaction, quem:discord.Member):
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
        #Verificando se está tentando se roubar
        if interaction.user.id == quem.id:
            await interaction.response.send_message(f'Hey {interaction.user.mention} você não pode roubar a si mesmo🤨',delete_after=10)
            return

        user = BancoConfig(self.bot, interaction.user)
        alvo = BancoConfig(self.bot, quem)
        if alvo.saldo_user < 25:
            #Cria o Embed e Envia
            embed = discord.Embed(title=f"{BOT.title()} Bank", color=0x00ff00)
            embed.add_field(name="Usuario",value=f"{quem.mention}", inline=False)
            embed.add_field(name="Saldo", value=f"{alvo.saldo_user} {BOT}s", inline=False)
            embed.set_thumbnail(url= quem.display_avatar.url)
            await interaction.response.send_message(content='Vai roubar oque?, ele não tem nada ksks' ,embed=embed, delete_after=10)
        else:
            #Pegando o Saldo dos 2 e decidindo a quantia do roubo
            saldo_roubado = randint(alvo.saldo_user//10,alvo.saldo_user//4)     
            #Repondo os novos valores
            alvo.trocar_saldo_user(alvo.saldo_user - saldo_roubado)
            user.trocar_saldo_user(user.saldo_user + saldo_roubado)
            await interaction.response.send_message(f'🤑Você roubou {saldo_roubado} {BOT}s de {quem.mention}',delete_after=18)

    @app_commands.command(name='banco-apostar', description=f'Aposte 1000 {BOT}s e tente ganhar 10.000')
    async def casino(self, interaction:discord.Interaction):
        #Verificando se o bot ta on
        sv = ServerConfig(self.bot,interaction.guild)
        if interaction.guild.id in sv.servers_off():
            await interaction.response.send_message('To Off',delete_after=20)
            return
        #Verificando se o usuario deve ser ignorado
        if interaction.user.id in sv.ignore_list():
            await interaction.response.send_message('Você está na minha Ignore List, não posso te responder aqui',delete_after=10)
            return
        try:
            user = BancoConfig(self.bot, interaction.user)
            #Verificando se tem Saldo Suficiente
            if user.saldo_user < 1000:
                #Cria o Embed e Envia
                embed = discord.Embed(title=f"{BOT.title()} Bank", color=0x00ff00)
                embed.add_field(name="Usuario",value=f"{interaction.user.mention}", inline=False)
                embed.add_field(name="Saldo", value=f"{user.saldo_user} {BOT}s", inline=False)
                embed.set_thumbnail(url= interaction.user.display_avatar.url)
                await interaction.response.send_message(content=f'Saldo Insuficiente. são Necessarios 1000 {BOT}s, Saque seus  {BOT}s',embed=embed,delete_after=10)
                return
            else:
                #Verificando se tem poção da sorte
                if user.pocao_sorte >=1:
                    chance = randint(1,8)
                    #Gastando uma poção
                    user.trocar_itens('pocao_sorte',user.pocao_sorte - 1)
                    await interaction.channel.send('Usou 1x Poção da Sorte Haha..',delete_after=10)

                else:
                    chance = randint(1,100)
                if chance <=8:
                    #Depositando os novos valores
                    user.trocar_saldo_user(user.saldo_user - 1000)
                    user.trocar_saldo_banco(user.saldo_banco + 10000)
                    #Cria o Embed e Envia
                    embed = discord.Embed(title=f"{BOT.title()} Bank", color=0x00ff00)
                    embed.add_field(name="Usuario",value=f"{interaction.user.mention}", inline=False)
                    embed.add_field(name="Saldo Banco", value=f"{user.saldo_banco + 10000} {BOT}s", inline=False)
                    embed.set_thumbnail(url= interaction.user.display_avatar.url)
                    await interaction.response.send_message(content=f'🤑Parabens {interaction.user.mention}!! você ganhou o Premio!💸💸',embed=embed,delete_after=60)
                    return
                else:
                    repostas = ['tente denovo','Quem sabe na proxima','Tente denovo amanhã','você está com azar emm']
                    await interaction.response.send_message(f'Infelizmente não foi dessa vez {interaction.user.mention}... {choice(repostas)}',delete_after=10)
                    user.trocar_saldo_user(user.saldo_user - 1000)
                    return
        except:
            user.abrir_conta()
            user = BancoConfig(self.bot, interaction.user.id)
            #Verificando se tem Saldo Suficiente
            if user.saldo_user < 1000:
                await interaction.response.send_message(f'{BOT}s Insuficientes. são Necessarios 1000 {BOT}s, Saque seus Oopas',delete_after=10)
                #Cria o Embed e Envia
                embed = discord.Embed(title=f"{BOT.title()} Bank", color=0x00ff00)
                embed.add_field(name="Usuario",value=f"{interaction.user.mention}", inline=False)
                embed.add_field(name="Saldo", value=f"{user.saldo_user} {BOT}s", inline=False)
                embed.set_thumbnail(url= interaction.user.display_avatar.url)
                await interaction.channel.send(embed=embed,delete_after=10)
                return

    @app_commands.command(name='banco-top-local', description=f'Veja o Rank-Local de {BOT}s')
    async def top_local(self, interaction: discord.Interaction):
        sv = ServerConfig(self.bot, interaction.guild)
        if interaction.guild.id in sv.servers_off():
            return await interaction.response.send_message('To Off', delete_after=20)

        # 1. Pega a lista já filtrada e ordenada (Top 10 ou Top 6 como você preferir)
        lista_membros = BancoConfig(self.bot, interaction.user).membros_saldo(interaction.guild)
        if not lista_membros:
            return await interaction.response.send_message("Ninguém neste servidor tem conta no banco ainda!", ephemeral=True)
        embed = discord.Embed(title=f"🏆 Rank Local - {BOT.title()} Bank", color=0x00ff00)
    
        # 2. Monta o embed com os dados da lista
        for i, usuario in enumerate(lista_membros):
            nome_user = usuario[1]
            saldo = usuario[2]
            embed.add_field(
                name=f"{i+1}º {nome_user} — {saldo} {BOT}s", 
                value="━━━━━━━━━━━━━━━━━━━━━━━━", 
                inline=False
            )

        embed.add_field(name='', value=f'📌 Use `/banco-depositar` para aparecer no rank! 🤑', inline=False)
        try: embed.set_thumbnail(url=interaction.guild.icon.url)
        except: pass
        await interaction.response.send_message(embed=embed, delete_after=30)

    @app_commands.command(name='loja', description='Abre a loja de itens')
    async def loja(self, interaction: discord.Interaction):
        sv = ServerConfig(self.bot, interaction.guild)
        if interaction.guild.id in sv.servers_off():
            return await interaction.response.send_message('Bot desativado neste servidor.', ephemeral=True)

        embed = discord.Embed(title=f"🏪 {BOT.title()} Store", color=0x00FF00)
        embed.add_field(name="🍀 Poção da Sorte (500)", value="Aumenta chances no cassino.", inline=False)
        embed.add_field(name="💰 3x+ Salário (500)", value="Triplica o próximo /trabalhar.", inline=False)
        
        view = LojaView(self.bot, interaction.user, BancoConfig)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Bank(bot))