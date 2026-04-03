import discord
from discord.ext import commands
from random import randint, choice
import asyncio
import google.generativeai as genai
import os
from yt_dlp import YoutubeDL
from Clases.Server import ServerConfig

# Configura a API (Pegue sua chave em: https://aistudio.google.com/)
genai.configure(api_key=os.getenv("GEMINI_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL")) # Versão rápida e leve

# --- CONFIGURAÇÃO DE RESPOSTAS (Fora da classe para não poluir) ---
RESPOSTAS_ESTATICAS = {
    ("bom dia","dia") : ["Bom dia! ☀️", "Diaa", "Buenos Dias", 'Good Dayy'],
    ("boa tarde","tarde") : ["Boa tarde! 🌞", "Tarde", "Buenas Tardes", 'Good Afternoon'],
    ('boa noite', 'vou dor', 'ja vou dor', 'fui dorm', 'partiu sono', 'gnight', 'indo de berço') : ["Boa noite!", "Noite", "Buenas Noches", 'Good Night', 'Dorme bem manin'],
    ("da adm","me da adm") : ['Nop', 'Pede pro ADM', 'Adm pra que?', 'Ta achando que aqui é bagunça?'],
    ('eae', 'oi', 'salve', 'slv', 'eai', 'opa', 'aoba', 'fala tu', 'coé') : ['Eae Manin','Chegou mais um pra festa','Salveee', 'Eae'],
    ('server ruim', 'server lixo', 'server chato', 'sv ruim', 'sv bosta', 'que sv lixo') : ['Faz melhor então','falou o bonzão','duvido falar isso na cara do ADM skks','Problema teu?','Quem te perguntou?','Falou o mestre da diversão... sqn.','A porta da rua é a serventia da casa, amigão.','Se tá ruim pra você, imagina pra quem tem que te aguentar.','Duvido falar isso na cara do ADM.'],
    ('server par', 'sv par', 'server mor', 'sv mor', 'chat par', 'chat mor', 'parou tudo') : ['Pshh, poderia ter mais membros aqui..', 'convida teus amigos pra caa deixa de ser bobo', 'realmente ta meio parado..', 'relaxa, daqui a pouco o chat volta a ativa'],
    ('alguém on', 'alguem on', 'algm on', 'alguém vivo', 'alguem vivo', 'tem alguem', 'vivo?') : ['so você e deus amigo', 'acho que ta todo mundo off', 'devem estar ocupados', 'tenta outra hora', 'Tenta gritar "PIX GRÁTIS" que aparece alguém.' ],
    ('fodase', 'foda-se', 'fds', 'foda se') : ['Desfoda-se'],
    ("duvi"): [ "Meu pau no seu ouvido.", "Duvidou? No meu pirulito você rodou."],
    ("que","quê"): ["Queijo!"],
    "mario" : ["Aquele que te pegou atrás do armário?", "Conheço, é primo daquele que te comeu no vestiário."],
    "cinco" : ["Meu pau no seu brinco."],
    "seis" : ["Meu pau que te fez."],
    "sete" : ["Meu pau que te derrete."],
    "oito" : ["Meu pau no seu biscoito."],
    "dez" : ["Meu pau nos seus pés."],
}

class Interacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bn = os.getenv('BOT', 'Oopa').lower()

    # 1. Função de Sorteio (Membro da Classe)
    def sorteio(self, chance=3):
        return randint(1, chance) == 1

    # 2. O Decorador Correto para Cogs
    @commands.Cog.listener()
    async def on_message(self, message):
        # Filtros Iniciais
        if message.author.bot or not message.guild:
            return

        sv = ServerConfig(self.bot, message.guild)
        if message.guild.id in sv.servers_off() or message.author.id in sv.ignore_list():
            return

        texto = message.content.lower()
        
        # --- LÓGICA DE RESPOSTAS RÁPIDAS (Dicionário) ---
        for gatilho, resposta in RESPOSTAS_ESTATICAS.items():
            if texto.startswith(gatilho):
                async with message.channel.typing():
                    await asyncio.sleep(1.5)
                    final_msg = choice(resposta) if isinstance(resposta, list) else resposta
                    await message.channel.send(final_msg)
                return
        
        gatilhos_mata = (f'{self.bn} mate a', f'{self.bn} mate o', f'{self.bn} mata o', f'{self.bn} mata a', f'{self.bn} executa')
        if any(g in texto for g in gatilhos_mata):
            # Pega o último nome da frase de forma segura
            partes = message.content.split()
            if len(partes) < 3: return # Comando incompleto
            alvo = partes[-1] 

            # 3. Sistema de Imunidade (Admins e Criador)
            # Verifica se o alvo citado é um admin ou o criador (usando ID ou nome)
            if alvo.lower() in ['sans', 'san', 'trev', 'otavio'] or any(adm in alvo for adm in sv.adm_list()):
                await message.channel.send(choice(['Não quero.', 'Mata você, eu hein.', 'Esse aí é parça, mexe com quem tá quieto.']))
                return

            # 4. Sequência de Execução
            async with message.channel.typing():
                await asyncio.sleep(1.5)
                await message.channel.send('🚨 **MODO EXTERMINADOR ATIVADO!** 🤖')
                
                await asyncio.sleep(1.5)
                await message.channel.send(f'🎯 Localizando alvo: **{alvo}**...')

            # 5. Sorteio do Resultado (80% Sucesso / 20% Falha)
            sucesso = randint(1, 5) > 1

            async with message.channel.typing():
                await asyncio.sleep(2)
                
                if sucesso:
                    if os.path.exists('midia/tiros.gif'):
                        with open('midia/tiros.gif', 'rb') as f:
                            await message.channel.send(file=discord.File(f))
                    await message.channel.send(f'💥 **RATATATATA!** {alvo} foi pro saco! 💀')
                else:
                    if os.path.exists('midia/explosao.gif'):
                        with open('midia/explosao.gif', 'rb') as f:
                            await message.channel.send(file=discord.File(f))
                    await message.channel.send('⚠️ **ERRO NO SISTEMA!** A arma explodiu na minha mão! 💥🔥')
            
            return

        membro = [m.display_name[:4].lower() for m in message.guild.members if not m.bot]
        if texto[:4] in membro:
            respostas = [
                'Esse é o mais sigma do server 🗿🍷',
                'Ihh, esse aí? É o capitão do time do arco-íris 🌈',
                'Gente fina, mas se ficar sozinho com a sua conta, ela some 💸',
                'Esse nunca foi preso atoa... sempre teve um motivo muito bom 🚔',
                'Esse é turista: aparece, solta uma pérola e some por 3 meses ✈️',
                'Esse daí gosta de dar o bumbum, mas diz que é "experimental" 🍑',
                'Não sei o que aparece primeiro: a volta de Jesus ou esse cara no chat ☁️',
                'Lenda viva! Ou melhor, lenda, porque vivo ele quase não tá 💀',
                'Diz a lenda que se você olhar pro espelho e falar o nome dele 3 vezes, sua carteira some 🕵️',
                'O shape dele é de dar inveja... em um Grilo 🦗',
                'Se inteligência fosse dinheiro, ele estaria devendo pro banco do Bot 📉',
                'É o braço direito do ADM, mas o ADM não sabe disso ainda 🤡',
                'Entrou no servidor só pra pegar o link de outros e nunca mais falar nada 🚶',
                'Esse é o tipo de cara que pede PIX de 1 real pra inteirar o corote 🍺',
                'O maior inimigo do ban... por enquanto 🔨',
                'Gente boa, mas se a polícia bater na porta, ele pula a janela 👮',
                'A última vez que ele trabalhou no /banco-trabalhar, o servidor caiu de susto 👷',
                'Se beleza fosse crime, ele seria a pessoa mais honesta do mundo 🙊',
                'O verdadeiro significado de "tanto faz": se sair do servidor, ninguém percebe 🤐',
                'Dizem que ele é o criador do bot, mas a única coisa que ele criou foi dívida 🧠',
                'O mais sigma do server 🗿🍷',
                'Capitão do time do arco-íris 🌈',
                'Gente boa, mas deve pro banco 💸',
                'Preso? Sempre por um bom motivo 🚔',
                'Aparece a cada eclipse 🌑',
                'Gosta de dar o bumbum em off 🍑',
                'Jesus volta antes desse cara ☁️',
                'Lenda viva (mais pra lenda) 💀',
                'Carteira some perto dele 🕵️',
                'Shape de grilo 🦗',
                'QI de temperatura de geladeira 📉',
                'Puxa-saco oficial do ADM 🤡',
                'Turista profissional 🚶',
                'Pede PIX de 1 real pro corote 🍺',
                'Inimigo n° 1 do Ban 🔨',
                'Pula a janela se a polícia bater 👮',
                'Trabalhar no bot? Ele tem alergia 👷',
                'Bonito? Só de longe e no escuro 🙊',
                'Se sair, ninguém percebe 🤐',
                'Só cria dívida no server 🧠'
            ]
            #Simula que está digitando
            async with message.channel.typing():
                await asyncio.sleep( 1.5 )
            await message.channel.send(choice(respostas))

        # --- INTERAÇÃO COM NOME DO BOT (IA ou Gatilhos) ---
        if self.bn in texto or self.bot.user.mentioned_in(message):
            await self.handle_ia_or_triggers(message, texto)

        # --- DOWNLOADER DE VÍDEO (Separado para organização) ---
        if texto.startswith('https://'):
            await self.handle_video_download(message)

    async def handle_ia_or_triggers(self, message, texto):
        async with message.channel.typing():
            # 1. Identificação e Relação
            user_id = message.author.id
            guild_id = message.guild.id
            criador_id = os.getenv('DONO')
            guild_dono = os.getenv('GUILD_DONO')    
            relacao = "seu criador" if user_id == criador_id else "membro comum"
            relacao_guilda = 'Seu Servidor' if guild_id == guild_dono else 'Servidor comum que você apenas é um bot'

            # 2. Prompt Zeca Urubu
            # Pegamos o conteúdo da mensagem removendo o nome do bot para a IA focar na pergunta
            pergunta_limpa = texto.replace(self.bn, "").replace(f'<@{self.bot.user.id}>', "").strip()
            if not pergunta_limpa:
                pergunta_limpa = "me deu oi ou apenas me chamou"
            
            # 1. Busca as últimas 10 mensagens (incluindo a que acabou de ser enviada)
            mensagens = []
            async for msg in message.channel.history(limit=20):
                # Formatamos como "Nome: Mensagem" para a IA entender o contexto
                mensagens.append(f"{msg.author.display_name}: {msg.content}")

            # 2. O Discord entrega da mais NOVA para a mais ANTIGA. 
            # Para a IA entender a conversa, precisamos inverter a ordem.
            mensagens.reverse()

            # 3. Junta tudo em um bloco de texto (Contexto)
            contexto_chat = "\n".join(mensagens)

            prompt = (
                f"Diretrizes de Personalidade: {os.getenv('BOT_PERSONALITY')}\n\n"
                f"Atualmente, você está falando com um membro, que é {relacao}.\n\n"
                f"Atualmente, você está no Servidor: {message.guild.name}, que é {relacao_guilda}.\n\n"
                f"Contexto: {contexto_chat}\n\n"
                f"Interação do {message.author.id}: {pergunta_limpa}"
            )



            try:
                # 3. Gera a resposta e envia
                response = model.generate_content(prompt)
                # Adicionamos um pequeno delay para simular o tempo de leitura do corvo
                await message.channel.send(response.text)
                return
                
            except Exception as e:
                await asyncio.sleep(1)
                await message.channel.send(f'To cansado de conversar, Pra ver meus comandos, use /')
                print(f"❌ ERRO NO GEMINI (on_message): {e}")
                return 

    async def handle_video_download(self, message):
        video_link = message.content
        folder = "midia/downloads"

        if not os.path.exists(folder):
            os.makedirs(folder)

        ydl_opts = {
            'format': 'best[ext=mp4][filesize<25M]/best',
            'outtmpl': f'{folder}/%(title).50s.%(ext)s',
            'restrictfilenames': True,
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
            'retries': 5,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                # 1. Extrai info e baixa de uma vez só (mais rápido)
                info = ydl.extract_info(video_link, download=True)
                
                if info.get('duration', 0) > 360:
                    print("⚠️ Vídeo muito longo, ignorando.")
                    return

                file_path = ydl.prepare_filename(info)

            # --- AQUI ESTAVA O ERRO: BUSCA SEGURA DO CANAL ---
            id_env = os.getenv('CANAL_DOWNLOADS')
            if not id_env:
                print("❌ ERRO: CANAL_DOWNLOADS não configurado no .env")
                return

            canal_id = int(id_env) # Converte para número!
            
            # Tenta pegar do cache, se não achar, busca no servidor do Discord
            canal = self.bot.get_channel(canal_id) or await self.bot.fetch_channel(canal_id)

            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    await canal.send(content=f"🎥 Enviado por: {message.author.mention}", file=discord.File(f))
                
                os.remove(file_path) # Limpa o lixo do disco

        except Exception as e:
            print(f"❌ ERRO ao processar vídeo: {e}")

async def setup(bot):
    await bot.add_cog(Interacao(bot))